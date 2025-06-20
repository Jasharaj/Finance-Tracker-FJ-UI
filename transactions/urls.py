from django.urls import path
from . import views

urlpatterns = [
    # Income Sources
    path('income-sources/', views.income_source_list, name='income_source_list'),
    path('income-sources/create/', views.income_source_create, name='income_source_create'),
    path('income-sources/<int:pk>/edit/', views.income_source_edit, name='income_source_edit'),
    path('income-sources/<int:pk>/delete/', views.income_source_delete, name='income_source_delete'),
    
    # Expense Categories
    path('expense-categories/', views.expense_category_list, name='expense_category_list'),
    path('expense-categories/create/', views.expense_category_create, name='expense_category_create'),
    path('expense-categories/<int:pk>/edit/', views.expense_category_edit, name='expense_category_edit'),
    path('expense-categories/<int:pk>/delete/', views.expense_category_delete, name='expense_category_delete'),
    
    # Transactions
    path('', views.transaction_list, name='transaction_list'),
    path('create/', views.transaction_create, name='transaction_create'),
    path('<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    
    # API
    path('api/categories/', views.get_transaction_categories, name='get_transaction_categories'),
] 