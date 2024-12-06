from django.urls import path
from . import views
from .views import IncomeView
from .views import ExpenseView
from .views import BudgetView
from .views import BudgetListView, BudgetUpdateView, BudgetDeleteView
from .views import ExpenseListView
from .views import ExpenseUpdateView
from .views import ExpenseDeleteView
from .views import IncomeListView
from .views import IncomeUpdateView
from .views import IncomeDeleteView
from .views import AuditLogView
from .views import MonthlyIncomeView
from .views import MonthlyExpenseView


urlpatterns = [
    path('activity/', views.fetch_activity, name='fetch_activity'),
     path("api/income/", IncomeView.as_view(), name="add_income"),
      path('api/expense/', ExpenseView.as_view(), name='expense-api'),
      path('api/budget/', BudgetView.as_view(), name='budget'),


    path('api/budget-list/', BudgetListView.as_view(), name='budget-list'),
    path('api/budget-update/<str:budget_id>/', BudgetUpdateView.as_view(), name='budget-update'),
    path('api/budget-delete/<str:budget_id>/', BudgetDeleteView.as_view(), name='budget-delete'),

    path('api/expenses/', ExpenseListView.as_view(), name='expense-list'),
    path('api/expense-update/<str:expense_id>/', ExpenseUpdateView.as_view(), name='expense-update'),
    path('api/expense-delete/<str:expense_id>/', ExpenseDeleteView.as_view(), name='expense-delete'),
    path('api/incomes/', IncomeListView.as_view(), name='income-list'),
    path('api/income-update/<str:income_id>/', IncomeUpdateView.as_view(), name='income-update'),
    path('api/income-delete/<str:income_id>/', IncomeDeleteView.as_view(), name='income-delete'),
    path('api/audit-logs/', AuditLogView.as_view(), name='audit-logs'),
    path('api/monthly-income/', MonthlyIncomeView.as_view(), name='monthly-income'),
    path('api/monthly-expense/', MonthlyExpenseView.as_view(), name='monthly-expense'),
]



