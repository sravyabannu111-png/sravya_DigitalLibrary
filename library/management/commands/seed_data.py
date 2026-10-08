from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from library.models import Author, Book, Member, CirculationRecord


class Command(BaseCommand):
    help = 'Populates the library database with sample authors, books, members, and circulation records.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding library data...")

        # Clear existing records to ensure fresh demo data if requested or populate cleanly
        CirculationRecord.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()
        Member.objects.all().delete()

        # 1. Create Authors
        authors_data = [
            ("Robert C. Martin", "Acclaimed software engineer, speaker, and author known as 'Uncle Bob', pioneer of Agile and Clean Architecture."),
            ("George Orwell", "English novelist, essayist, journalist and critic whose work is marked by lucid prose and social criticism."),
            ("Frank Herbert", "American science fiction author best known for the masterpiece novel Dune and its sequels."),
            ("Yuval Noah Harari", "Israeli public intellectual, historian and professor known for his worldwide bestsellers exploring human history."),
            ("Mary Shelley", "English novelist best known for her Gothic masterpiece Frankenstein; or, The Modern Prometheus."),
            ("Arthur Conan Doyle", "British writer and physician who created the legendary detective character Sherlock Holmes."),
            ("Carl Sagan", "American astronomer, planetary scientist, and science communicator known for his television series Cosmos."),
            ("Sun Tzu", "Ancient Chinese military general, strategist, and philosopher credited as the author of The Art of War."),
        ]

        authors = {}
        for name, bio in authors_data:
            author, _ = Author.objects.get_or_create(name=name, defaults={'biography': bio})
            authors[name] = author

        self.stdout.write(f"Created {len(authors)} authors.")

        # 2. Create Books with high quality reliable cover images
        books_data = [
            {
                "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
                "author": authors["Robert C. Martin"],
                "isbn": "978-0132350884",
                "genre": "Science & Tech",
                "total_copies": 5,
                "available_copies": 3,
                "cover_url": "https://images.unsplash.com/photo-1532012164546-f432f2e3777a?auto=format&fit=crop&w=600&q=80",
                "description": "Even bad code can function. But if code isn't clean, it can bring a development organization to its knees. Every year, countless hours and significant resources are lost because of poorly written code."
            },
            {
                "title": "1984: Nineteen Eighty-Four",
                "author": authors["George Orwell"],
                "isbn": "978-0451524935",
                "genre": "Fiction",
                "total_copies": 6,
                "available_copies": 4,
                "cover_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80",
                "description": "A startling and haunting novel that paints a terrifying picture of a world governed by total surveillance, censorship, and omnipresent state authority."
            },
            {
                "title": "Dune",
                "author": authors["Frank Herbert"],
                "isbn": "978-0441013593",
                "genre": "Fantasy & Sci-Fi",
                "total_copies": 4,
                "available_copies": 2,
                "cover_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80",
                "description": "Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides, heir to a noble family in a grand intergalactic saga of politics, ecology, and destiny."
            },
            {
                "title": "Sapiens: A Brief History of Humankind",
                "author": authors["Yuval Noah Harari"],
                "isbn": "978-0062316097",
                "genre": "History",
                "total_copies": 5,
                "available_copies": 3,
                "cover_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=600&q=80",
                "description": "From a renowned historian comes a groundbreaking narrative of humanity’s creation and evolution, exploring how biology and history have defined us."
            },
            {
                "title": "Frankenstein: Or, The Modern Prometheus",
                "author": authors["Mary Shelley"],
                "isbn": "978-0141439471",
                "genre": "Fiction",
                "total_copies": 3,
                "available_copies": 3,
                "cover_url": "https://images.unsplash.com/photo-1476275466078-4007374efbbe?auto=format&fit=crop&w=600&q=80",
                "description": "Mary Shelley's chilling Gothic thriller about a young scientist who drives himself to the brink of sanity in his quest to conquer death."
            },
            {
                "title": "The Hound of the Baskervilles",
                "author": authors["Arthur Conan Doyle"],
                "isbn": "978-0140437867",
                "genre": "Mystery & Thriller",
                "total_copies": 4,
                "available_copies": 2,
                "cover_url": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=600&q=80",
                "description": "Sherlock Holmes and Dr. Watson investigate the curse of the Baskerville family on the desolate Devonshire moors."
            },
            {
                "title": "Cosmos: A Personal Voyage",
                "author": authors["Carl Sagan"],
                "isbn": "978-0345331359",
                "genre": "Science & Tech",
                "total_copies": 3,
                "available_copies": 1,
                "cover_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80",
                "description": "Cosmos traces the origin of knowledge and the scientific method, blending science and philosophy to contemplate our position in the universe."
            },
            {
                "title": "The Art of War",
                "author": authors["Sun Tzu"],
                "isbn": "978-1590302255",
                "genre": "Philosophy",
                "total_copies": 3,
                "available_copies": 2,
                "cover_url": "https://images.unsplash.com/photo-1463320726281-696a485928c7?auto=format&fit=crop&w=600&q=80",
                "description": "An ancient Chinese military treatise dating from the Late Spring and Autumn Period, influential in tactical and modern strategic philosophy."
            },
            {
                "title": "The Clean Coder: A Code of Conduct for Professional Programmers",
                "author": authors["Robert C. Martin"],
                "isbn": "978-0137081073",
                "genre": "Education",
                "total_copies": 2,
                "available_copies": 0,  # Zero copies to test out-of-stock validation!
                "cover_url": "https://images.unsplash.com/photo-1516259762381-22954d7d3ad2?auto=format&fit=crop&w=600&q=80",
                "description": "Uncle Bob introduces the disciplines, techniques, tools, and practices of true software craftsmanship."
            }
        ]

        books = {}
        for b in books_data:
            book = Book.objects.create(**b)
            books[book.isbn] = book

        self.stdout.write(f"Created {len(books)} books.")

        # 3. Create Members
        members_data = [
            ("Eleanor Vance", "MEM-101", "eleanor.vance@university.edu", "+1 (555) 234-5678", date.today() - timedelta(days=120)),
            ("Liam Gallagher", "MEM-102", "liam.g@university.edu", "+1 (555) 345-6789", date.today() - timedelta(days=90)),
            ("Sophia Rodriguez", "MEM-103", "sophia.r@university.edu", "+1 (555) 456-7890", date.today() - timedelta(days=60)),
            ("Marcus Chen", "MEM-104", "marcus.c@university.edu", "+1 (555) 567-8901", date.today() - timedelta(days=45)),
            ("Aisha Patel", "MEM-105", "aisha.p@university.edu", "+1 (555) 678-9012", date.today() - timedelta(days=30)),
        ]

        members = []
        for name, m_id, email, phone, joined in members_data:
            member = Member.objects.create(
                name=name,
                member_id=m_id,
                email=email,
                phone=phone,
                joined_date=joined
            )
            members.append(member)

        self.stdout.write(f"Created {len(members)} members.")

        # 4. Create Circulation Records (Active on-time, Active overdue, Returned on-time, Returned with fine)
        today = date.today()

        # Eleanor has:
        # - 1 active on-time loan (Clean Code)
        # - 1 active OVERDUE loan (Dune) -> Due 4 days ago ($4 fine pending)
        CirculationRecord.objects.create(
            book=books["978-0132350884"],  # Clean Code
            member=members[0],
            issue_date=today - timedelta(days=5),
            due_date=today + timedelta(days=9),
            returned=False,
            fine_amount=Decimal('0.00')
        )
        CirculationRecord.objects.create(
            book=books["978-0441013593"],  # Dune
            member=members[0],
            issue_date=today - timedelta(days=18),
            due_date=today - timedelta(days=4),  # Overdue by 4 days!
            returned=False,
            fine_amount=Decimal('0.00')
        )

        # Liam has:
        # - 1 active OVERDUE loan (1984) -> Due 8 days ago ($8 fine pending)
        # - 1 past returned loan on time
        CirculationRecord.objects.create(
            book=books["978-0451524935"],  # 1984
            member=members[1],
            issue_date=today - timedelta(days=22),
            due_date=today - timedelta(days=8),
            returned=False,
            fine_amount=Decimal('0.00')
        )
        CirculationRecord.objects.create(
            book=books["978-0141439471"],  # Frankenstein
            member=members[1],
            issue_date=today - timedelta(days=30),
            due_date=today - timedelta(days=16),
            return_date=today - timedelta(days=17),
            returned=True,
            fine_amount=Decimal('0.00')
        )

        # Sophia has:
        # - 1 active on-time loan (Cosmos)
        # - 1 past returned loan that was overdue by 3 days with $3.00 fine paid
        CirculationRecord.objects.create(
            book=books["978-0345331359"],  # Cosmos
            member=members[2],
            issue_date=today - timedelta(days=3),
            due_date=today + timedelta(days=11),
            returned=False,
            fine_amount=Decimal('0.00')
        )
        CirculationRecord.objects.create(
            book=books["978-0140437867"],  # Baskervilles
            member=members[2],
            issue_date=today - timedelta(days=35),
            due_date=today - timedelta(days=21),
            return_date=today - timedelta(days=18),  # Returned 3 days late
            returned=True,
            fine_amount=Decimal('3.00')
        )

        # Marcus has:
        # - 1 active on-time loan (Sapiens)
        # - 1 active loan (The Clean Coder - 0 available)
        CirculationRecord.objects.create(
            book=books["978-0062316097"],  # Sapiens
            member=members[3],
            issue_date=today - timedelta(days=6),
            due_date=today + timedelta(days=8),
            returned=False,
            fine_amount=Decimal('0.00')
        )
        CirculationRecord.objects.create(
            book=books["978-0137081073"],  # The Clean Coder
            member=members[3],
            issue_date=today - timedelta(days=2),
            due_date=today + timedelta(days=12),
            returned=False,
            fine_amount=Decimal('0.00')
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded comprehensive digital library data!"))
