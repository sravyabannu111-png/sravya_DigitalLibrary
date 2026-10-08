from django.contrib import admin
from .models import Author, Book, Member, CirculationRecord


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'biography_snippet', 'book_count')
    search_fields = ('name',)

    def biography_snippet(self, obj):
        return (obj.biography[:75] + '...') if len(obj.biography) > 75 else obj.biography
    biography_snippet.short_description = 'Biography'

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = 'Books in Catalog'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'isbn', 'total_copies', 'available_copies', 'status_badge')
    list_filter = ('genre',)
    search_fields = ('title', 'author__name', 'isbn')
    ordering = ('title',)

    def status_badge(self, obj):
        return f"{obj.available_copies}/{obj.total_copies} Available"
    status_badge.short_description = 'Availability'


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'member_id', 'email', 'phone', 'joined_date', 'active_loans')
    search_fields = ('name', 'member_id', 'email', 'phone')
    ordering = ('name',)

    def active_loans(self, obj):
        return obj.active_borrowed_count
    active_loans.short_description = 'Active Loans'


@admin.register(CirculationRecord)
class CirculationRecordAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'issue_date', 'due_date', 'return_date', 'fine_amount', 'returned', 'status_label')
    list_filter = ('returned', 'issue_date', 'due_date')
    search_fields = ('book__title', 'member__name', 'member__member_id')
    ordering = ('-issue_date',)

    def status_label(self, obj):
        if obj.returned:
            return "Returned"
        if obj.is_overdue:
            return f"OVERDUE ({obj.days_overdue} days)"
        return f"Active ({obj.days_remaining} days left)"
    status_label.short_description = 'Circulation Status'
