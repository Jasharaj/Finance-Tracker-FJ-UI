from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from transactions.models import ExpenseCategory
import datetime

class BudgetGoal(models.Model):
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    
    PERIOD_CHOICES = [
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budget_goals')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='budget_goals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default=MONTHLY)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.category.name} - {self.amount} ({self.get_period_display()})"
    
    def get_progress(self):
        from transactions.models import Transaction
        
        # Determine date range based on period
        today = timezone.now().date()
        if self.period == self.WEEKLY:
            # Get the start of the current week (Monday)
            start_of_period = today - datetime.timedelta(days=today.weekday())
            end_of_period = start_of_period + datetime.timedelta(days=6)
        elif self.period == self.MONTHLY:
            # Get the start of the current month
            start_of_period = today.replace(day=1)
            # Get the end of the current month
            if today.month == 12:
                end_of_period = today.replace(day=31)
            else:
                next_month = today.replace(month=today.month + 1, day=1)
                end_of_period = next_month - datetime.timedelta(days=1)
        else:  # YEARLY
            start_of_period = today.replace(month=1, day=1)
            end_of_period = today.replace(month=12, day=31)
        
        # Calculate expenses for the period
        expenses = Transaction.objects.filter(
            user=self.user,
            expense_category=self.category,
            transaction_type='expense',
            date__gte=start_of_period,
            date__lte=end_of_period
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        return {
            'spent': expenses,
            'budget': self.amount,
            'remaining': self.amount - expenses,
            'percentage': (expenses / self.amount * 100) if self.amount > 0 else 0,
            'period_start': start_of_period,
            'period_end': end_of_period
        }

class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_progress_percentage(self):
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0
    
    def days_remaining(self):
        if self.target_date:
            today = timezone.now().date()
            if today > self.target_date:
                return 0
            return (self.target_date - today).days
        return None
