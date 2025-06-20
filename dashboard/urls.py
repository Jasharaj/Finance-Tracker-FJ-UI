from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Budget Goals
    path('budget-goals/', views.budget_goal_list, name='budget_goal_list'),
    path('budget-goals/create/', views.budget_goal_create, name='budget_goal_create'),
    path('budget-goals/<int:pk>/edit/', views.budget_goal_edit, name='budget_goal_edit'),
    path('budget-goals/<int:pk>/delete/', views.budget_goal_delete, name='budget_goal_delete'),
    
    # Savings Goals
    path('savings-goals/', views.savings_goal_list, name='savings_goal_list'),
    path('savings-goals/create/', views.savings_goal_create, name='savings_goal_create'),
    path('savings-goals/<int:pk>/edit/', views.savings_goal_edit, name='savings_goal_edit'),
    path('savings-goals/<int:pk>/delete/', views.savings_goal_delete, name='savings_goal_delete'),
    
    # Reports
    path('reports/', views.generate_report, name='generate_report'),
] 