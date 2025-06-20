from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import IncomeSource, ExpenseCategory, Transaction
from .forms import IncomeSourceForm, ExpenseCategoryForm, TransactionForm
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

@login_required
def income_source_list(request):
    income_sources = IncomeSource.objects.filter(user=request.user)
    return render(request, 'transactions/income_source_list.html', {'income_sources': income_sources})

@login_required
def income_source_create(request):
    if request.method == 'POST':
        form = IncomeSourceForm(request.POST)
        if form.is_valid():
            income_source = form.save(commit=False)
            income_source.user = request.user
            income_source.save()
            messages.success(request, 'Income source created successfully!')
            return redirect('income_source_list')
    else:
        form = IncomeSourceForm()
    
    return render(request, 'transactions/income_source_form.html', {'form': form})

@login_required
def income_source_edit(request, pk):
    income_source = get_object_or_404(IncomeSource, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = IncomeSourceForm(request.POST, instance=income_source)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income source updated successfully!')
            return redirect('income_source_list')
    else:
        form = IncomeSourceForm(instance=income_source)
    
    return render(request, 'transactions/income_source_form.html', {'form': form, 'income_source': income_source})

@login_required
def income_source_delete(request, pk):
    income_source = get_object_or_404(IncomeSource, pk=pk, user=request.user)
    
    if request.method == 'POST':
        income_source.delete()
        messages.success(request, 'Income source deleted successfully!')
        return redirect('income_source_list')
    
    return render(request, 'transactions/income_source_confirm_delete.html', {'income_source': income_source})

@login_required
def expense_category_list(request):
    expense_categories = ExpenseCategory.objects.filter(user=request.user)
    
    # Calculate current month's expenses for each category
    today = timezone.now()
    
    for category in expense_categories:
        category.current_month_expenses = category.get_monthly_expenses(today.year, today.month)
        category.budget_status = category.get_budget_status(today.year, today.month)
    
    return render(request, 'transactions/expense_category_list.html', {'expense_categories': expense_categories})

@login_required
def expense_category_create(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            expense_category = form.save(commit=False)
            expense_category.user = request.user
            expense_category.save()
            messages.success(request, 'Expense category created successfully!')
            return redirect('expense_category_list')
    else:
        form = ExpenseCategoryForm()
    
    return render(request, 'transactions/expense_category_form.html', {'form': form})

@login_required
def expense_category_edit(request, pk):
    expense_category = get_object_or_404(ExpenseCategory, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST, instance=expense_category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense category updated successfully!')
            return redirect('expense_category_list')
    else:
        form = ExpenseCategoryForm(instance=expense_category)
    
    return render(request, 'transactions/expense_category_form.html', {'form': form, 'expense_category': expense_category})

@login_required
def expense_category_delete(request, pk):
    expense_category = get_object_or_404(ExpenseCategory, pk=pk, user=request.user)
    
    if request.method == 'POST':
        expense_category.delete()
        messages.success(request, 'Expense category deleted successfully!')
        return redirect('expense_category_list')
    
    return render(request, 'transactions/expense_category_confirm_delete.html', {'expense_category': expense_category})

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    # Filter by date
    date_filter = request.GET.get('date_filter', 'month')
    today = timezone.now().date()
    
    if date_filter == 'week':
        start_date = today - timedelta(days=today.weekday())
        transactions = transactions.filter(date__gte=start_date)
    elif date_filter == 'month':
        start_date = today.replace(day=1)
        transactions = transactions.filter(date__gte=start_date)
    elif date_filter == 'year':
        start_date = today.replace(month=1, day=1)
        transactions = transactions.filter(date__gte=start_date)
    
    # Filter by type
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        if transaction_type == Transaction.INCOME:
            transactions = transactions.filter(income_source_id=category_id)
        else:
            transactions = transactions.filter(expense_category_id=category_id)
    
    # Calculate totals
    income_total = transactions.filter(transaction_type=Transaction.INCOME).aggregate(total=Sum('amount'))['total'] or 0
    expense_total = transactions.filter(transaction_type=Transaction.EXPENSE).aggregate(total=Sum('amount'))['total'] or 0
    balance = income_total - expense_total
    
    # Get categories for filters
    income_sources = IncomeSource.objects.filter(user=request.user)
    expense_categories = ExpenseCategory.objects.filter(user=request.user)
    
    return render(request, 'transactions/transaction_list.html', {
        'transactions': transactions,
        'income_total': income_total,
        'expense_total': expense_total,
        'balance': balance,
        'date_filter': date_filter,
        'transaction_type': transaction_type,
        'category_id': category_id,
        'income_sources': income_sources,
        'expense_categories': expense_categories,
    })

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction created successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user)
    
    return render(request, 'transactions/transaction_form.html', {'form': form})

@login_required
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
    return render(request, 'transactions/transaction_form.html', {'form': form, 'transaction': transaction})

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transaction_list')
    
    return render(request, 'transactions/transaction_confirm_delete.html', {'transaction': transaction})

@login_required
def get_transaction_categories(request):
    transaction_type = request.GET.get('type')
    
    if transaction_type == Transaction.INCOME:
        categories = IncomeSource.objects.filter(user=request.user).values('id', 'name')
        field_name = 'income_source'
    else:
        categories = ExpenseCategory.objects.filter(user=request.user).values('id', 'name')
        field_name = 'expense_category'
    
    return JsonResponse({
        'categories': list(categories),
        'field_name': field_name
    })
