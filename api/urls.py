from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ─────────────────────────────────────────────────────────────────
    path('auth/register', views.RegisterView.as_view(), name='register'),
    path('auth/login',    views.LoginView.as_view(),    name='login'),
    path('auth/logout',   views.LogoutView.as_view(),   name='logout'),

    # ── Dashboard ─────────────────────────────────────────────────────────────
    path('dashboard', views.DashboardView.as_view(), name='dashboard'),

    # ── Families – specific paths BEFORE parameterised ─────────────────────
    path('families/mine',                          views.FamilyMineView.as_view(),         name='families-mine'),
    path('families/members',                       views.FamilyMembersView.as_view(),      name='families-members'),
    path('families/invite',                        views.FamilyInviteView.as_view(),       name='families-invite'),
    path('families/members/<int:user_id>',         views.FamilyRemoveMemberView.as_view(), name='families-remove-member'),
    path('families',                               views.FamilyCreateView.as_view(),       name='families-create'),

    # ── Accounts ──────────────────────────────────────────────────────────────
    path('accounts/<int:pk>/summary', views.AccountSummaryView.as_view(),    name='accounts-summary'),
    path('accounts/<int:pk>',         views.AccountDetailView.as_view(),     name='accounts-detail'),
    path('accounts',                  views.AccountListCreateView.as_view(), name='accounts-list'),

    # ── Spending – summary BEFORE list ────────────────────────────────────────
    path('spending/summary',   views.SpendingSummaryView.as_view(),    name='spending-summary'),
    path('spending/<int:pk>',  views.SpendingDetailView.as_view(),     name='spending-detail'),
    path('spending',           views.SpendingListCreateView.as_view(), name='spending-list'),

    # ── Expenses – calendar BEFORE list ───────────────────────────────────────
    path('expenses/calendar',        views.ExpenseCalendarView.as_view(),    name='expenses-calendar'),
    path('expenses/<int:pk>/pay',    views.ExpensePayView.as_view(),         name='expenses-pay'),
    path('expenses/<int:pk>',        views.ExpenseDetailView.as_view(),      name='expenses-detail'),
    path('expenses',                 views.ExpenseListCreateView.as_view(),  name='expenses-list'),

    # ── Debts – summary BEFORE list ───────────────────────────────────────────
    path('debts/summary',            views.DebtSummaryView.as_view(),        name='debts-summary'),
    path('debts/<int:pk>/payment',   views.DebtPaymentCreateView.as_view(),  name='debts-payment'),
    path('debts/<int:pk>',           views.DebtDetailView.as_view(),         name='debts-detail'),
    path('debts',                    views.DebtListCreateView.as_view(),     name='debts-list'),

    # ── Banks ─────────────────────────────────────────────────────────────────
    path('banks/<int:pk>', views.BankDetailView.as_view(), name='banks-detail'),
    path('banks',          views.BankListView.as_view(),   name='banks-list'),

    # ── Categories ────────────────────────────────────────────────────────────
    path('categories/<int:pk>', views.CategoryDetailView.as_view(),     name='categories-detail'),
    path('categories',          views.CategoryListCreateView.as_view(), name='categories-list'),

    # ── Users (admin) ─────────────────────────────────────────────────────────
    path('users/<int:pk>', views.UserDetailView.as_view(),     name='users-detail'),
    path('users',          views.UserListCreateView.as_view(), name='users-list'),

    # ── Incomes ───────────────────────────────────────────────────────────────
    path('incomes/<int:pk>', views.IncomeDetailView.as_view(),     name='incomes-detail'),
    path('incomes',          views.IncomeListCreateView.as_view(), name='incomes-list'),

    # ── Report ────────────────────────────────────────────────────────────────
    path('report', views.ReportView.as_view(), name='report'),

    # ── Transfers ─────────────────────────────────────────────────────────────
    path('transfers/<int:pk>', views.TransferDetailView.as_view(),     name='transfers-detail'),
    path('transfers',          views.TransferListCreateView.as_view(), name='transfers-list'),
]
