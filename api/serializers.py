from rest_framework import serializers
from .models import (
    User, Role, Family, FamilyMember, Bank, Account,
    Category, Spending, Expense, ExpenseLog, Debt, DebtPayment,
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('name', 'username', 'email', 'phone', 'password', 'password_confirmation')

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirmation'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'phone', 'role_id', 'is_staff', 'created_at')
        read_only_fields = ('id', 'is_staff', 'created_at')


class UserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'phone', 'role_id', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class FamilySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Family
        fields = ('id', 'name', 'owner', 'created_at')
        read_only_fields = ('id', 'owner', 'created_at')


class FamilyMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = FamilyMember
        fields = ('id', 'user', 'role', 'joined_at')
        read_only_fields = ('id', 'user', 'joined_at')


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ('id', 'name', 'created_at')
        read_only_fields = ('id', 'created_at')


class AccountSerializer(serializers.ModelSerializer):
    bank = BankSerializer(read_only=True)
    bank_id = serializers.PrimaryKeyRelatedField(
        queryset=Bank.objects.all(),
        source='bank',
    )

    class Meta:
        model = Account
        fields = ('id', 'account_number', 'balance', 'bank_id', 'bank', 'family_id', 'created_at')
        read_only_fields = ('id', 'family_id', 'created_at')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'icon', 'color', 'created_at')
        read_only_fields = ('id', 'created_at')


class SpendingSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Spending
        fields = (
            'id', 'amount', 'description', 'spent_at',
            'account_id', 'category_id', 'category', 'user_id', 'created_at',
        )
        read_only_fields = ('id', 'user_id', 'category', 'created_at')


class ExpenseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseLog
        fields = ('id', 'expense_id', 'amount_paid', 'paid_at', 'account_id', 'notes', 'created_at')
        read_only_fields = ('id', 'created_at')


class ExpenseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    logs = ExpenseLogSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = (
            'id', 'name', 'amount', 'day_of_month', 'frequency',
            'category_id', 'category', 'account_id', 'active', 'logs', 'created_at',
        )
        read_only_fields = ('id', 'category', 'logs', 'created_at')


class DebtPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtPayment
        fields = ('id', 'debt_id', 'amount', 'paid_at', 'account_id', 'notes', 'created_at')
        read_only_fields = ('id', 'created_at')


class DebtSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()
    payments = DebtPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Debt
        fields = (
            'id', 'creditor', 'description', 'original_amount', 'current_balance',
            'monthly_payment', 'interest_rate', 'start_date', 'due_date', 'status',
            'account_id', 'user_id', 'progress_percentage', 'payments', 'created_at',
        )
        read_only_fields = ('id', 'user_id', 'progress_percentage', 'payments', 'created_at')
