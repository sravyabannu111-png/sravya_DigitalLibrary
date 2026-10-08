from datetime import date, timedelta
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Author(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    GENRE_CHOICES = [
        ('Fiction', 'Fiction'),
        ('Non-Fiction', 'Non-Fiction'),
        ('Science & Tech', 'Science & Tech'),
        ('History', 'History'),
        ('Fantasy & Sci-Fi', 'Fantasy & Sci-Fi'),
        ('Mystery & Thriller', 'Mystery & Thriller'),
        ('Biography', 'Biography'),
        ('Philosophy', 'Philosophy'),
        ('Education', 'Education'),
    ]

    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    isbn = models.CharField('ISBN', max_length=20, unique=True)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES, default='Fiction')
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_url = models.URLField('Cover Image URL', blank=True, max_length=500)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['title']

    def clean(self):
        if self.available_copies > self.total_copies:
            raise ValidationError({'available_copies': "Available copies cannot exceed total copies."})

    @property
    def is_available(self):
        return self.available_copies > 0

    @property
    def issued_copies(self):
        return max(0, self.total_copies - self.available_copies)

    def __str__(self):
        return f"{self.title} ({self.isbn})"


class Member(models.Model):
    name = models.CharField(max_length=200)
    member_id = models.CharField('Member ID', max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    joined_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} [{self.member_id}]"

    @property
    def active_borrowed_count(self):
        return self.circulation_records.filter(returned=False).count()

    @property
    def overdue_borrowed_count(self):
        today = date.today()
        return self.circulation_records.filter(returned=False, due_date__lt=today).count()


class CirculationRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='circulation_records')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='circulation_records')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True)
    return_date = models.DateField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    returned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-issue_date']

    def save(self, *args, **kwargs):
        # Default due date to 14 days after issue date if not provided
        if not self.due_date and self.issue_date:
            self.due_date = self.issue_date + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.returned:
            return False
        return self.due_date < date.today()

    @property
    def days_overdue(self):
        ref_date = self.return_date if self.returned else date.today()
        if ref_date and self.due_date and ref_date > self.due_date:
            return (ref_date - self.due_date).days
        return 0

    @property
    def days_remaining(self):
        if self.returned:
            return 0
        diff = (self.due_date - date.today()).days
        return max(0, diff)

    def calculate_projected_fine(self, target_date=None, rate=Decimal('1.00')):
        check_date = target_date or (self.return_date if self.returned else date.today())
        if check_date and self.due_date and check_date > self.due_date:
            overdue_days = (check_date - self.due_date).days
            return Decimal(overdue_days) * rate
        return Decimal('0.00')

    def __str__(self):
        status = "Returned" if self.returned else "Active"
        return f"{self.book.title} -> {self.member.name} ({status})"
