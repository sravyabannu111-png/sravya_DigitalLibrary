from datetime import date, timedelta
from decimal import Decimal
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.conf import settings

from .models import Author, Book, Member, CirculationRecord
from .forms import BookIssueForm, BookReturnForm, BookForm, MemberForm, AuthorForm


def book_catalog(request):
    """Catalog view displaying books with search and filter capabilities."""
    query = request.GET.get('q', '').strip()
    genre_filter = request.GET.get('genre', '').strip()
    availability_filter = request.GET.get('availability', '').strip()

    books = Book.objects.select_related('author').all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(isbn__icontains=query) |
            Q(genre__icontains=query)
        )

    if genre_filter:
        books = books.filter(genre__iexact=genre_filter)

    if availability_filter == 'available':
        books = books.filter(available_copies__gt=0)
    elif availability_filter == 'unavailable':
        books = books.filter(available_copies=0)

    # Aggregated Stats
    total_books_count = Book.objects.count()
    total_copies_sum = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
    active_loans_count = CirculationRecord.objects.filter(returned=False).count()
    today = date.today()
    overdue_loans_count = CirculationRecord.objects.filter(returned=False, due_date__lt=today).count()
    genres_list = [g[0] for g in Book.GENRE_CHOICES]

    # Serialization for instant JavaScript client-side search & filtering
    books_data = []
    for b in Book.objects.select_related('author').all():
        books_data.append({
            'id': b.id,
            'title': b.title,
            'author': b.author.name,
            'author_id': b.author.id,
            'isbn': b.isbn,
            'genre': b.genre,
            'total_copies': b.total_copies,
            'available_copies': b.available_copies,
            'is_available': b.is_available,
            'cover_url': b.cover_url or '',
            'description': b.description or '',
            'issue_url': f"/circulation/issue/?book={b.id}",
            'detail_url': f"/books/{b.id}/"
        })

    context = {
        'books': books,
        'query': query,
        'genre_filter': genre_filter,
        'availability_filter': availability_filter,
        'genres_list': genres_list,
        'total_books_count': total_books_count,
        'total_copies_sum': total_copies_sum,
        'active_loans_count': active_loans_count,
        'overdue_loans_count': overdue_loans_count,
        'books_json': json.dumps(books_data),
        'daily_fine_rate': getattr(settings, 'DAILY_FINE_RATE', 1.00),
    }
    return render(request, 'library/catalog.html', context)


def book_detail(request, pk):
    """Detailed book view with circulation history and stock stats."""
    book = get_object_or_404(Book.objects.select_related('author'), pk=pk)
    active_loans = CirculationRecord.objects.filter(book=book, returned=False).select_related('member')
    past_loans = CirculationRecord.objects.filter(book=book, returned=True).select_related('member')[:10]

    context = {
        'book': book,
        'active_loans': active_loans,
        'past_loans': past_loans,
    }
    return render(request, 'library/book_detail.html', context)


def issue_book(request, book_id=None):
    """Book issue workflow enforcing stock verification and updating inventory."""
    initial_book = None
    if book_id:
        initial_book = get_object_or_404(Book, pk=book_id)
    elif request.GET.get('book'):
        try:
            initial_book = Book.objects.get(pk=request.GET.get('book'))
        except (Book.DoesNotExist, ValueError):
            pass

    initial_member = None
    if request.GET.get('member'):
        try:
            initial_member = Member.objects.get(pk=request.GET.get('member'))
        except (Member.DoesNotExist, ValueError):
            pass

    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['book']
            member = form.cleaned_data['member']
            issue_date = form.cleaned_data['issue_date']
            due_date = form.cleaned_data.get('due_date') or (issue_date + timedelta(days=getattr(settings, 'DEFAULT_LOAN_DAYS', 14)))

            # Atomic transaction to guarantee stock safety
            with transaction.atomic():
                # Refresh book from db with lock
                locked_book = Book.objects.select_for_update().get(pk=book.pk)
                if locked_book.available_copies <= 0:
                    messages.error(
                        request,
                        f"Cannot issue '{locked_book.title}': No available copies left in inventory!"
                    )
                    return render(request, 'library/issue_book.html', {'form': form, 'book': locked_book})

                # Reduce available copies
                locked_book.available_copies -= 1
                locked_book.save(update_fields=['available_copies'])

                # Create circulation record
                record = CirculationRecord.objects.create(
                    book=locked_book,
                    member=member,
                    issue_date=issue_date,
                    due_date=due_date,
                    returned=False,
                    fine_amount=Decimal('0.00')
                )

            messages.success(
                request,
                f"Success! '{locked_book.title}' issued to {member.name}. Due on {due_date.strftime('%b %d, %Y')}."
            )
            return redirect('member_dashboard', pk=member.pk)
    else:
        form = BookIssueForm(initial_book=initial_book, initial_member=initial_member)

    # Books with stock for helper guidance
    available_books = Book.objects.filter(available_copies__gt=0).select_related('author')
    members = Member.objects.all()

    context = {
        'form': form,
        'selected_book': initial_book,
        'available_books': available_books,
        'members': members,
        'default_loan_days': getattr(settings, 'DEFAULT_LOAN_DAYS', 14),
    }
    return render(request, 'library/issue_book.html', context)


def return_book(request, record_id):
    """Book return workflow with dynamic and server-enforced fine calculation."""
    record = get_object_or_404(
        CirculationRecord.objects.select_related('book', 'member'),
        pk=record_id
    )

    if record.returned:
        messages.info(request, f"This book was already returned on {record.return_date}.")
        return redirect('member_dashboard', pk=record.member.pk)

    fine_rate = Decimal(str(getattr(settings, 'DAILY_FINE_RATE', 1.00)))
    today = date.today()
    days_overdue = max(0, (today - record.due_date).days)
    projected_fine = Decimal(days_overdue) * fine_rate

    if request.method == 'POST':
        form = BookReturnForm(request.POST)
        if form.is_valid():
            actual_return_date = form.cleaned_data['return_date']
            
            # Recalculate fine based on the submitted return date
            if actual_return_date > record.due_date:
                calc_days_overdue = (actual_return_date - record.due_date).days
                final_fine = Decimal(calc_days_overdue) * fine_rate
            else:
                calc_days_overdue = 0
                final_fine = Decimal('0.00')

            with transaction.atomic():
                locked_book = Book.objects.select_for_update().get(pk=record.book.pk)
                # Increase available copies
                locked_book.available_copies = min(locked_book.total_copies, locked_book.available_copies + 1)
                locked_book.save(update_fields=['available_copies'])

                # Update record
                record.return_date = actual_return_date
                record.fine_amount = final_fine
                record.returned = True
                record.save(update_fields=['return_date', 'fine_amount', 'returned'])

            if final_fine > Decimal('0.00'):
                messages.warning(
                    request,
                    f"'{record.book.title}' returned successfully. Overdue by {calc_days_overdue} days. Fine calculated: ${final_fine:.2f}."
                )
            else:
                messages.success(
                    request,
                    f"'{record.book.title}' returned on time! No overdue fine charged."
                )

            return redirect('member_dashboard', pk=record.member.pk)
    else:
        form = BookReturnForm(initial={'return_date': today})

    context = {
        'record': record,
        'form': form,
        'days_overdue': days_overdue,
        'projected_fine': projected_fine,
        'fine_rate': fine_rate,
        'today': today,
    }
    return render(request, 'library/return_book.html', context)


def member_dashboard(request, pk=None):
    """Member dashboard displaying active loans, overdue alerts, and borrowing history."""
    members = Member.objects.annotate(
        active_count=Count('circulation_records', filter=Q(circulation_records__returned=False))
    ).order_by('name')

    if not members.exists():
        messages.info(request, "No members found in system. Please add a member or seed sample data.")
        return redirect('add_member')

    if pk:
        current_member = get_object_or_404(Member, pk=pk)
    else:
        # Default to first member
        current_member = members.first()

    today = date.today()
    active_loans = CirculationRecord.objects.filter(
        member=current_member,
        returned=False
    ).select_related('book', 'book__author').order_by('due_date')

    past_loans = CirculationRecord.objects.filter(
        member=current_member,
        returned=True
    ).select_related('book', 'book__author').order_by('-return_date')

    total_fines_paid = past_loans.aggregate(total=Sum('fine_amount'))['total'] or Decimal('0.00')

    # Calculate pending fines for active overdue books
    fine_rate = Decimal(str(getattr(settings, 'DAILY_FINE_RATE', 1.00)))
    pending_fines = Decimal('0.00')
    overdue_count = 0

    loan_details = []
    for loan in active_loans:
        is_over = loan.due_date < today
        days_late = (today - loan.due_date).days if is_over else 0
        fine = Decimal(days_late) * fine_rate
        if is_over:
            pending_fines += fine
            overdue_count += 1
        
        loan_details.append({
            'record': loan,
            'is_overdue': is_over,
            'days_overdue': days_late,
            'days_remaining': max(0, (loan.due_date - today).days) if not is_over else 0,
            'pending_fine': fine,
        })

    context = {
        'members': members,
        'member': current_member,
        'loan_details': loan_details,
        'past_loans': past_loans,
        'total_fines_paid': total_fines_paid,
        'pending_fines': pending_fines,
        'overdue_count': overdue_count,
        'today': today,
        'fine_rate': fine_rate,
    }
    return render(request, 'library/member_dashboard.html', context)


def member_list(request):
    """View to list all library members with summary stats."""
    query = request.GET.get('q', '').strip()
    members = Member.objects.annotate(
        active_loans_count=Count('circulation_records', filter=Q(circulation_records__returned=False)),
        total_loans_count=Count('circulation_records'),
    )
    if query:
        members = members.filter(
            Q(name__icontains=query) |
            Q(member_id__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    context = {
        'members': members,
        'query': query,
    }
    return render(request, 'library/member_list.html', context)


def due_date_calculator(request):
    """Standalone interactive due-date and fine calculator page."""
    daily_rate = getattr(settings, 'DAILY_FINE_RATE', 1.00)
    loan_days = getattr(settings, 'DEFAULT_LOAN_DAYS', 14)

    context = {
        'daily_rate': daily_rate,
        'loan_days': loan_days,
        'today': date.today(),
    }
    return render(request, 'library/calculator.html', context)


def add_book(request):
    """Add new book to library catalog."""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f"Book '{book.title}' added successfully!")
            return redirect('book_catalog')
    else:
        form = BookForm()
    return render(request, 'library/forms/generic_form.html', {
        'form': form,
        'title': 'Add New Book to Catalog',
        'subtitle': 'Register a new title, specify available copies and author.',
        'btn_text': 'Add Book',
        'icon': 'bi-journal-plus'
    })


def add_member(request):
    """Register new library member."""
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"Member '{member.name}' ({member.member_id}) registered successfully!")
            return redirect('member_dashboard', pk=member.pk)
    else:
        form = MemberForm()
    return render(request, 'library/forms/generic_form.html', {
        'form': form,
        'title': 'Register New Member',
        'subtitle': 'Enroll a student or faculty member into circulation records.',
        'btn_text': 'Register Member',
        'icon': 'bi-person-plus'
    })


def add_author(request):
    """Add a new author."""
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(request, f"Author '{author.name}' created successfully!")
            return redirect('add_book')
    else:
        form = AuthorForm()
    return render(request, 'library/forms/generic_form.html', {
        'form': form,
        'title': 'Add New Author',
        'subtitle': 'Create an author profile to link with books.',
        'btn_text': 'Save Author',
        'icon': 'bi-feather'
    })


def api_calculate_fine(request):
    """JSON API for client-side fine calculation validation."""
    try:
        due_date_str = request.GET.get('due_date')
        return_date_str = request.GET.get('return_date') or str(date.today())
        
        if not due_date_str:
            return JsonResponse({'error': 'due_date parameter is required'}, status=400)
            
        due_d = date.fromisoformat(due_date_str)
        ret_d = date.fromisoformat(return_date_str)
        
        days_over = max(0, (ret_d - due_d).days)
        rate = Decimal(str(getattr(settings, 'DAILY_FINE_RATE', 1.00)))
        fine = Decimal(days_over) * rate
        
        return JsonResponse({
            'due_date': str(due_d),
            'return_date': str(ret_d),
            'days_overdue': days_over,
            'rate_per_day': float(rate),
            'fine_amount': float(fine),
            'is_overdue': days_over > 0
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
