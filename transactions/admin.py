from django.contrib import admin
from .models import IncomeSource, ExpenseCategory, Transaction

@admin.register(IncomeSource)
class IncomeSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'description')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'monthly_budget')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'transaction_type', 'date', 'user')
    list_filter = ('transaction_type', 'date', 'user')
    search_fields = ('description', 'user__username')
    date_hierarchy = 'date'
