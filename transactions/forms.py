from django import forms
from .models import IncomeSource, ExpenseCategory, Transaction

class IncomeSourceForm(forms.ModelForm):
    class Meta:
        model = IncomeSource
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description', 'monthly_budget']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'monthly_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'date', 'description', 'transaction_type', 'income_source', 'expense_category', 'receipt']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'transaction_type': forms.Select(attrs={'class': 'form-control', 'id': 'transaction_type'}),
            'income_source': forms.Select(attrs={'class': 'form-control', 'id': 'income_source_field'}),
            'expense_category': forms.Select(attrs={'class': 'form-control', 'id': 'expense_category_field'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['income_source'].queryset = IncomeSource.objects.filter(user=user)
            self.fields['expense_category'].queryset = ExpenseCategory.objects.filter(user=user)
    
    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        income_source = cleaned_data.get('income_source')
        expense_category = cleaned_data.get('expense_category')
        
        if transaction_type == Transaction.INCOME:
            if expense_category:
                self.add_error('expense_category', 'Income transactions cannot have an expense category.')
            if not income_source:
                self.add_error('income_source', 'Income transactions must have an income source.')
        
        if transaction_type == Transaction.EXPENSE:
            if income_source:
                self.add_error('income_source', 'Expense transactions cannot have an income source.')
            if not expense_category:
                self.add_error('expense_category', 'Expense transactions must have an expense category.')
        
        return cleaned_data 