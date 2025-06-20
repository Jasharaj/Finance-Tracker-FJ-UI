from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, Q
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange
from django.http import JsonResponse
import json

from transactions.models import Transaction, IncomeSource, ExpenseCategory
from .models import BudgetGoal, SavingsGoal
from .forms import BudgetGoalForm, SavingsGoalForm

@login_required
def dashboard(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    _, last_day = monthrange(today.year, today.month)
    end_of_month = today.replace(day=last_day)
    
    # Monthly overview
    income_transactions = Transaction.objects.filter(
        user=request.user,
        transaction_type=Transaction.INCOME,
        date__gte=start_of_month,
        date__lte=end_of_month
    )
    
    expense_transactions = Transaction.objects.filter(
        user=request.user,
        transaction_type=Transaction.EXPENSE,
        date__gte=start_of_month,
        date__lte=end_of_month
    )
    
    monthly_income = income_transactions.aggregate(total=Sum('amount'))['total'] or 0
    monthly_expenses = expense_transactions.aggregate(total=Sum('amount'))['total'] or 0
    monthly_savings = monthly_income - monthly_expenses
    
    # Income breakdown by source
    income_by_source = list(income_transactions.values('income_source__name').annotate(
        total=Sum('amount'),
        name=F('income_source__name')
    ).order_by('-total'))
    
    # Expense breakdown by category
    expense_by_category = list(expense_transactions.values('expense_category__name').annotate(
        total=Sum('amount'),
        name=F('expense_category__name')
    ).order_by('-total'))
    
    # Budget status
    budget_statuses = []
    expense_categories = ExpenseCategory.objects.filter(user=request.user)
    
    for category in expense_categories:
        budget_status = category.get_budget_status(today.year, today.month)
        budget_status['category'] = category.name
        budget_statuses.append(budget_status)
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Savings goals
    savings_goals = SavingsGoal.objects.filter(user=request.user)
    
    # Prepare data for charts
    current_month_dates = [start_of_month + timedelta(days=x) for x in range((end_of_month - start_of_month).days + 1)]
    
    daily_expense_data = []
    for date in current_month_dates:
        daily_total = expense_transactions.filter(date=date).aggregate(total=Sum('amount'))['total'] or 0
        daily_expense_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'amount': float(daily_total)
        })
    
    category_data = [{'name': item['name'], 'value': float(item['total'])} for item in expense_by_category]
    income_data = [{'name': item['name'], 'value': float(item['total'])} for item in income_by_source]
    
    context = {
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_savings': monthly_savings,
        'income_by_source': income_by_source,
        'expense_by_category': expense_by_category,
        'budget_statuses': budget_statuses,
        'recent_transactions': recent_transactions,
        'savings_goals': savings_goals,
        'charts_data': {
            'daily_expenses': json.dumps(daily_expense_data),
            'category_expenses': json.dumps(category_data),
            'income_sources': json.dumps(income_data)
        }
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def budget_goal_list(request):
    budget_goals = BudgetGoal.objects.filter(user=request.user)
    
    for goal in budget_goals:
        goal.progress = goal.get_progress()
    
    return render(request, 'dashboard/budget_goal_list.html', {'budget_goals': budget_goals})

@login_required
def budget_goal_create(request):
    if request.method == 'POST':
        form = BudgetGoalForm(request.POST, user=request.user)
        if form.is_valid():
            budget_goal = form.save(commit=False)
            budget_goal.user = request.user
            budget_goal.save()
            messages.success(request, 'Budget goal created successfully!')
            return redirect('budget_goal_list')
    else:
        form = BudgetGoalForm(user=request.user)
    
    return render(request, 'dashboard/budget_goal_form.html', {'form': form})

@login_required
def budget_goal_edit(request, pk):
    budget_goal = get_object_or_404(BudgetGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BudgetGoalForm(request.POST, instance=budget_goal, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget goal updated successfully!')
            return redirect('budget_goal_list')
    else:
        form = BudgetGoalForm(instance=budget_goal, user=request.user)
    
    return render(request, 'dashboard/budget_goal_form.html', {'form': form, 'budget_goal': budget_goal})

@login_required
def budget_goal_delete(request, pk):
    budget_goal = get_object_or_404(BudgetGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        budget_goal.delete()
        messages.success(request, 'Budget goal deleted successfully!')
        return redirect('budget_goal_list')
    
    return render(request, 'dashboard/budget_goal_confirm_delete.html', {'budget_goal': budget_goal})

@login_required
def savings_goal_list(request):
    savings_goals = SavingsGoal.objects.filter(user=request.user)
    return render(request, 'dashboard/savings_goal_list.html', {'savings_goals': savings_goals})

@login_required
def savings_goal_create(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            savings_goal = form.save(commit=False)
            savings_goal.user = request.user
            savings_goal.save()
            messages.success(request, 'Savings goal created successfully!')
            return redirect('savings_goal_list')
    else:
        form = SavingsGoalForm()
    
    return render(request, 'dashboard/savings_goal_form.html', {'form': form})

@login_required
def savings_goal_edit(request, pk):
    savings_goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=savings_goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Savings goal updated successfully!')
            return redirect('savings_goal_list')
    else:
        form = SavingsGoalForm(instance=savings_goal)
    
    return render(request, 'dashboard/savings_goal_form.html', {'form': form, 'savings_goal': savings_goal})

@login_required
def savings_goal_delete(request, pk):
    savings_goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        savings_goal.delete()
        messages.success(request, 'Savings goal deleted successfully!')
        return redirect('savings_goal_list')
    
    return render(request, 'dashboard/savings_goal_confirm_delete.html', {'savings_goal': savings_goal})

@login_required
def generate_report(request):
    report_type = request.GET.get('type', 'monthly')
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    # Determine date range based on report type
    if report_type == 'monthly':
        start_date = datetime(year, month, 1).date()
        _, last_day = monthrange(year, month)
        end_date = datetime(year, month, last_day).date()
        title = f"Monthly Report - {start_date.strftime('%B %Y')}"
    elif report_type == 'yearly':
        start_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
        title = f"Yearly Report - {year}"
    else:  # custom
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        title = f"Custom Report - {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
    
    # Get transactions for the period
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    )
    
    income_transactions = transactions.filter(transaction_type=Transaction.INCOME)
    expense_transactions = transactions.filter(transaction_type=Transaction.EXPENSE)
    
    # Calculate summary
    total_income = income_transactions.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = expense_transactions.aggregate(total=Sum('amount'))['total'] or 0
    net_savings = total_income - total_expenses
    
    # Income breakdown by source
    income_by_source = list(income_transactions.values('income_source__name').annotate(
        total=Sum('amount'),
        name=F('income_source__name')
    ).order_by('-total'))
    
    # Expense breakdown by category
    expense_by_category = list(expense_transactions.values('expense_category__name').annotate(
        total=Sum('amount'),
        name=F('expense_category__name')
    ).order_by('-total'))
    
    # Prepare chart data
    income_data = [{'name': item['name'], 'value': float(item['total'])} for item in income_by_source]
    expense_data = [{'name': item['name'], 'value': float(item['total'])} for item in expense_by_category]
    
    # Generate monthly data for the comparison chart
    monthly_data = []
    current_year = timezone.now().year
    
    # Only generate monthly data if viewing yearly report or if in current year
    if report_type == 'yearly' or (start_date.year == current_year):
        # Get data for each month
        for m in range(1, 13):
            month_start = datetime(year, m, 1).date()
            _, month_days = monthrange(year, m)
            month_end = datetime(year, m, month_days).date()
            
            # Skip future months
            if month_start > timezone.now().date():
                monthly_data.append({
                    'month': month_start.strftime('%b'),
                    'income': 0,
                    'expenses': 0
                })
                continue
            
            # Get monthly income
            month_income = Transaction.objects.filter(
                user=request.user,
                transaction_type=Transaction.INCOME,
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Get monthly expenses
            month_expenses = Transaction.objects.filter(
                user=request.user,
                transaction_type=Transaction.EXPENSE,
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_data.append({
                'month': month_start.strftime('%b'),
                'income': float(month_income),
                'expenses': float(month_expenses)
            })
    
    context = {
        'title': title,
        'start_date': start_date,
        'end_date': end_date,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': net_savings,
        'income_by_source': income_by_source,
        'expense_by_category': expense_by_category,
        'monthly_data': monthly_data,
        'charts_data': {
            'income': json.dumps(income_data),
            'expenses': json.dumps(expense_data)
        }
    }
    
    return render(request, 'dashboard/report.html', context)
