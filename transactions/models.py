from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class IncomeSource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='income_sources')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class ExpenseCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.name
    
    def get_monthly_expenses(self, year, month):
        return self.expenses.filter(
            date__year=year,
            date__month=month
        ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    def get_budget_status(self, year, month):
        spent = self.get_monthly_expenses(year, month)
        return {
            'spent': spent,
            'budget': self.monthly_budget,
            'remaining': self.monthly_budget - spent,
            'percentage': (spent / self.monthly_budget * 100) if self.monthly_budget > 0 else 0
        }

class Transaction(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'
    
    TRANSACTION_TYPES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    income_source = models.ForeignKey(IncomeSource, on_delete=models.SET_NULL, null=True, blank=True, related_name='incomes')
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} on {self.date}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.transaction_type == self.INCOME and self.expense_category:
            raise ValidationError("Income transactions cannot have an expense category.")
        
        if self.transaction_type == self.EXPENSE and self.income_source:
            raise ValidationError("Expense transactions cannot have an income source.")
        
        if self.transaction_type == self.INCOME and not self.income_source:
            raise ValidationError("Income transactions must have an income source.")
        
        if self.transaction_type == self.EXPENSE and not self.expense_category:
            raise ValidationError("Expense transactions must have an expense category.")
