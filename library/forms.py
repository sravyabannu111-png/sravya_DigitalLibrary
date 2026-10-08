from datetime import date, timedelta
from decimal import Decimal
from django import forms
from django.conf import settings
from .models import Author, Book, Member, CirculationRecord


class BookIssueForm(forms.ModelForm):
    class Meta:
        model = CirculationRecord
        fields = ['member', 'book', 'issue_date', 'due_date']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-select', 'id': 'issueMemberSelect'}),
            'book': forms.Select(attrs={'class': 'form-select', 'id': 'issueBookSelect'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'issueDateInput'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'dueDateInput'}),
        }

    def __init__(self, *args, **kwargs):
        initial_book = kwargs.pop('initial_book', None)
        initial_member = kwargs.pop('initial_member', None)
        super().__init__(*args, **kwargs)
        
        today = date.today()
        default_due = today + timedelta(days=getattr(settings, 'DEFAULT_LOAN_DAYS', 14))
        
        if not self.initial.get('issue_date'):
            self.initial['issue_date'] = today
        if not self.initial.get('due_date'):
            self.initial['due_date'] = default_due

        # Filter books with available copies > 0 for new issues, but keep selected book if editing
        if initial_book:
            self.fields['book'].initial = initial_book
        if initial_member:
            self.fields['member'].initial = initial_member

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        issue_date = cleaned_data.get('issue_date')
        due_date = cleaned_data.get('due_date')

        if book and book.available_copies <= 0:
            raise forms.ValidationError(
                f"Cannot issue '{book.title}': No available copies left in stock (0 available)."
            )

        if issue_date and due_date and due_date < issue_date:
            raise forms.ValidationError("Due date cannot be earlier than issue date.")

        return cleaned_data


class BookReturnForm(forms.Form):
    return_date = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'returnDateInput'}),
        label="Actual Return Date"
    )
    confirm_fine = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'confirmFineCheckbox'}),
        label="Acknowledge fine calculation"
    )


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'genre', 'total_copies', 'available_copies', 'cover_url', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Clean Code'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 978-0132350884'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cover_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://images.unsplash.com/...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Synopsis or summary'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get('total_copies') or 0
        available = cleaned_data.get('available_copies') or 0
        if available > total:
            raise forms.ValidationError("Available copies cannot exceed total copies.")
        return cleaned_data


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'member_id', 'email', 'phone', 'joined_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'member_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MEM-1001'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'member@library.org'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 019-2834'}),
            'joined_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('joined_date'):
            self.initial['joined_date'] = date.today()


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'biography']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author name'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Author biography'}),
        }
