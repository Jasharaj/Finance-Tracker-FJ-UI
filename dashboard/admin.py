from django.contrib import admin
from .models import BudgetGoal, SavingsGoal

@admin.register(BudgetGoal)
class BudgetGoalAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'period', 'user', 'start_date', 'end_date')
    list_filter = ('period', 'user', 'start_date')
    search_fields = ('category__name', 'user__username')
    date_hierarchy = 'start_date'

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_amount', 'current_amount', 'target_date', 'user')
    list_filter = ('target_date', 'user')
    search_fields = ('name', 'user__username')
