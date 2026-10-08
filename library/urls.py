from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_catalog, name='book_catalog'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/issue/', views.issue_book, name='issue_book_for_book'),
    path('books/add/', views.add_book, name='add_book'),
    path('circulation/issue/', views.issue_book, name='issue_book'),
    path('circulation/return/<int:record_id>/', views.return_book, name='return_book'),
    path('members/', views.member_dashboard, name='members'),
    path('members/<int:pk>/', views.member_dashboard, name='member_dashboard'),
    path('members/directory/', views.member_list, name='member_list'),
    path('members/add/', views.add_member, name='add_member'),
    path('authors/add/', views.add_author, name='add_author'),
    path('calculator/', views.due_date_calculator, name='calculator'),
    path('api/calculate-fine/', views.api_calculate_fine, name='api_calculate_fine'),
]
