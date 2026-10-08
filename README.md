# Digital Library & E-Book Circulation Portal

A modern Django full-stack web application designed for digital library catalog browsing, instant search, book circulation tracking (14-day duration), dynamic overdue fine calculations, and member dashboards.

Built for **Capstone Project 3: Digital Library & E-Book Circulation Portal** and configured for **Render** deployment.

---

## Features
- **Book Catalog**: Responsive Bootstrap 5 catalog with availability badges (`In Stock` / `Out of Stock`), metric cards, and genre filtering.
- **Instant Search**: Client-side JavaScript search by Title, Author, ISBN, or Genre with instant feedback (keyboard shortcut `/`).
- **Book Issue Workflow**: Automated validation ensuring copies are in stock, atomical inventory reduction, and automatic 14-day due date calculation.
- **Book Return Workflow & Fine Engine**: Interactive return workflow with live overdue fine calculation ($\$1.00$/day) and automated stock restock.
- **Member Dashboard**: Real-time loan tracking, due date alerts, overdue danger warnings, and borrowing history.
- **Interactive Calculator**: Standalone due-date and overdue fine simulator with preset testing buttons.
- **Django Admin**: Complete administration dashboard at `/admin/` for Books, Authors, Members, and Circulation Records.
- **Seed Data**: Built-in management command (`python manage.py seed_data`) to generate sample data for testing.

---

## Technology Stack
- **Backend**: Python 3.11+, Django 6.1 (Django ORM, SQLite `db.sqlite3`)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Bootstrap Icons, Google Fonts (`Outfit`, `Plus Jakarta Sans`)
- **Server & Deployment**: WhiteNoise, Gunicorn, Render Blueprint (`render.yaml`)

---

## Project Structure
```text
.
├── manage.py                   # Django root management CLI
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render Blueprint configuration
├── create_superuser.py         # Automated admin account initialization
├── .gitignore                  # Git ignore rules
│
├── digital_library/            # Django project settings & configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── library/                    # Digital library application
    ├── migrations/             # Database schema migrations
    ├── management/commands/    # Seed data command (seed_data.py)
    ├── templates/library/      # Responsive HTML5 templates
    ├── static/                 # Custom CSS & JavaScript
    ├── admin.py                # Admin site registration
    ├── forms.py                # Django ModelForms & validations
    ├── models.py               # Database models (Author, Book, Member, CirculationRecord)
    ├── tests.py                # 9 unit & integration tests
    ├── urls.py                 # App URL routing
    └── views.py                # View controllers & business logic
```

---

## Local Setup & Development

1. **Activate virtual environment**:
   ```bash
   # Windows
   .\venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Populate demo data**:
   ```bash
   python manage.py seed_data
   ```

5. **Run test suite**:
   ```bash
   python manage.py test
   ```

6. **Start local development server**:
   ```bash
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
   Access Django Admin at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) (Default credentials: `admin` / `admin123`).

---

## Deploying to Render

1. Sign in to [Render](https://render.com).
2. Click **New +** → **Blueprint**.
3. Connect this GitHub repository (`sravyabannu111-png/sravya_DigitalLibrary`).
4. Render automatically reads `render.yaml`, sets up Python 3.11, installs dependencies, runs static collection, executes migrations, initializes the superuser, and launches Gunicorn.
5. Once deployment completes, access your live digital library URL!
