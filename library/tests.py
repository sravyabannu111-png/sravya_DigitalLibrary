from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from library.models import Author, Book, Member, CirculationRecord


class DigitalLibraryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(
            name="Robert C. Martin",
            biography="Author of Clean Code."
        )
        self.book_available = Book.objects.create(
            title="Clean Code",
            author=self.author,
            isbn="978-0132350884",
            genre="Science & Tech",
            total_copies=3,
            available_copies=2,
            cover_url="https://images.unsplash.com/photo-1532012164546-f432f2e3777a"
        )
        self.book_out_of_stock = Book.objects.create(
            title="The Clean Coder",
            author=self.author,
            isbn="978-0137081073",
            genre="Education",
            total_copies=1,
            available_copies=0,
            cover_url=""
        )
        self.member = Member.objects.create(
            name="Eleanor Vance",
            member_id="MEM-101",
            email="eleanor@university.edu",
            phone="+1 555-0192",
            joined_date=date.today() - timedelta(days=30)
        )

    def test_catalog_view(self):
        """Verify catalog view loads and renders books."""
        response = self.client.get(reverse('book_catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clean Code")
        self.assertContains(response, "The Clean Coder")

    def test_catalog_search(self):
        """Verify catalog filter by query."""
        response = self.client.get(reverse('book_catalog'), {'q': 'Clean Code'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clean Code")

    def test_issue_book_successful(self):
        """Verify issuing an available book reduces available_copies and sets 14-day due date."""
        initial_available = self.book_available.available_copies
        issue_date = date.today()
        expected_due = issue_date + timedelta(days=14)

        response = self.client.post(reverse('issue_book'), {
            'book': self.book_available.id,
            'member': self.member.id,
            'issue_date': issue_date.isoformat(),
            'due_date': expected_due.isoformat(),
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.book_available.refresh_from_db()
        self.assertEqual(self.book_available.available_copies, initial_available - 1)

        # Check circulation record
        record = CirculationRecord.objects.filter(book=self.book_available, member=self.member, returned=False).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.due_date, expected_due)
        self.assertEqual(record.fine_amount, Decimal('0.00'))

    def test_prevent_issue_when_out_of_stock(self):
        """Verify business rule: do not issue a book when available copies are zero."""
        response = self.client.post(reverse('issue_book'), {
            'book': self.book_out_of_stock.id,
            'member': self.member.id,
            'issue_date': date.today().isoformat(),
            'due_date': (date.today() + timedelta(days=14)).isoformat(),
        })

        # Form should be invalid with an error
        self.assertEqual(response.status_code, 200)
        self.book_out_of_stock.refresh_from_db()
        self.assertEqual(self.book_out_of_stock.available_copies, 0)
        # Ensure no record was created
        record_exists = CirculationRecord.objects.filter(book=self.book_out_of_stock).exists()
        self.assertFalse(record_exists)

    def test_return_book_on_time_increases_stock_zero_fine(self):
        """Verify returning an on-time book increments stock and charges $0 fine."""
        # Create an active loan due in future
        record = CirculationRecord.objects.create(
            book=self.book_available,
            member=self.member,
            issue_date=date.today() - timedelta(days=5),
            due_date=date.today() + timedelta(days=9),
            returned=False
        )
        # Manually emulate that available copies was decremented
        self.book_available.available_copies = 1
        self.book_available.save()

        response = self.client.post(reverse('return_book', args=[record.id]), {
            'return_date': date.today().isoformat(),
            'confirm_fine': True
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        record.refresh_from_db()
        self.assertTrue(record.returned)
        self.assertEqual(record.return_date, date.today())
        self.assertEqual(record.fine_amount, Decimal('0.00'))

        self.book_available.refresh_from_db()
        self.assertEqual(self.book_available.available_copies, 2)

    def test_return_book_overdue_calculates_fine(self):
        """Verify returning an overdue book calculates fine at $1.00/day overdue."""
        due_date = date.today() - timedelta(days=5)  # 5 days overdue
        record = CirculationRecord.objects.create(
            book=self.book_available,
            member=self.member,
            issue_date=date.today() - timedelta(days=19),
            due_date=due_date,
            returned=False
        )

        response = self.client.post(reverse('return_book', args=[record.id]), {
            'return_date': date.today().isoformat(),
            'confirm_fine': True
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        record.refresh_from_db()
        self.assertTrue(record.returned)
        self.assertEqual(record.return_date, date.today())
        self.assertEqual(record.fine_amount, Decimal('5.00'))

    def test_member_dashboard(self):
        """Verify member dashboard loads with loan history."""
        response = self.client.get(reverse('member_dashboard', args=[self.member.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.member.name)
        self.assertContains(response, self.member.member_id)

    def test_calculator_view(self):
        """Verify interactive calculator tool loads."""
        response = self.client.get(reverse('calculator'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Due-Date & Overdue Fine Calculator")

    def test_api_calculate_fine(self):
        """Verify API returns expected fine calculation."""
        due = (date.today() - timedelta(days=4)).isoformat()
        ret = date.today().isoformat()
        response = self.client.get(reverse('api_calculate_fine'), {
            'due_date': due,
            'return_date': ret
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['days_overdue'], 4)
        self.assertEqual(data['fine_amount'], 4.0)
