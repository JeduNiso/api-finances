from django.contrib import admin
from .models import (
    Role, User, Family, FamilyMember, Bank, Account, UserAccount,
    Category, Spending, Expense, ExpenseLog, Debt, DebtPayment,
)

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Family)
admin.site.register(FamilyMember)
admin.site.register(Bank)
admin.site.register(Account)
admin.site.register(UserAccount)
admin.site.register(Category)
admin.site.register(Spending)
admin.site.register(Expense)
admin.site.register(ExpenseLog)
admin.site.register(Debt)
admin.site.register(DebtPayment)
