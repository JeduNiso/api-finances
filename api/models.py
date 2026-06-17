from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class Role(models.Model):
    role = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.role


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL, related_name='users')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


class Family(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='owned_families')
    members = models.ManyToManyField(User, through='FamilyMember', related_name='families')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'families'

    def __str__(self):
        return self.name


class FamilyMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='family_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='family_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'family_members'
        unique_together = ('family', 'user')

    def __str__(self):
        return f"{self.user.email} in {self.family.name}"


class Bank(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'banks'

    def __str__(self):
        return self.name


class Account(models.Model):
    CURRENCY_CHOICES = [('BOB', 'Boliviano'), ('USD', 'US Dollar')]
    account_number = models.CharField(max_length=50, unique=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='BOB')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    bank = models.ForeignKey(Bank, on_delete=models.RESTRICT, related_name='accounts')
    family = models.ForeignKey(Family, on_delete=models.RESTRICT, related_name='accounts')
    users = models.ManyToManyField(User, through='UserAccount', related_name='accounts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts'

    def __str__(self):
        return self.account_number


class UserAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_accounts')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users_accounts'
        unique_together = ('user', 'account')

    def __str__(self):
        return f"{self.user.email} - {self.account.account_number}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name


class Spending(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255, null=True, blank=True)
    spent_at = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.RESTRICT, related_name='spendings')
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_name='spendings')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='spendings')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'spending'

    def __str__(self):
        return f"{self.amount} on {self.spent_at}"


class Expense(models.Model):
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('bimonthly', 'Bimonthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    day_of_month = models.SmallIntegerField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_name='expenses')
    account = models.ForeignKey(Account, on_delete=models.RESTRICT, related_name='expenses')
    debt = models.ForeignKey('Debt', null=True, blank=True, on_delete=models.SET_NULL, related_name='linked_expenses')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expenses'

    def __str__(self):
        return self.name


class ExpenseLog(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='logs')
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    paid_at = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.RESTRICT, related_name='expense_logs')
    notes = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'expenses_log'

    def __str__(self):
        return f"Log {self.id} for {self.expense.name}"


class Debt(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paid', 'Paid'),
        ('paused', 'Paused'),
    ]
    creditor = models.CharField(max_length=150)
    description = models.CharField(max_length=255, null=True, blank=True)
    original_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='debts')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='debts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def progress_percentage(self):
        if self.original_amount == 0:
            return 100.0
        paid = float(self.original_amount) - float(self.current_balance)
        return round((paid / float(self.original_amount)) * 100, 2)

    class Meta:
        db_table = 'debts'

    def __str__(self):
        return f"{self.creditor} - {self.current_balance}"


class DebtPayment(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_at = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.RESTRICT, related_name='debt_payments')
    notes = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'debts_payments'

    def __str__(self):
        return f"Payment {self.id} for {self.debt.creditor}"


class Income(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255)
    received_at = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.RESTRICT, related_name='incomes')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='incomes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'incomes'

    def __str__(self):
        return f"{self.description} – {self.amount}"


class Transfer(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255, null=True, blank=True)
    transferred_at = models.DateField()
    origin_account = models.ForeignKey(Account, on_delete=models.RESTRICT, related_name='transfers_out')
    destination_account = models.ForeignKey(Account, on_delete=models.RESTRICT, related_name='transfers_in')
    spending = models.OneToOneField(
        'Spending', null=True, blank=True, on_delete=models.SET_NULL, related_name='transfer'
    )
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='transfers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transfers'

    def __str__(self):
        return f"Transfer {self.amount} from {self.origin_account} to {self.destination_account}"
