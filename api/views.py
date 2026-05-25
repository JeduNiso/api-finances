from decimal import Decimal

from django.contrib.auth import authenticate
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    User, Family, FamilyMember, Bank, Account, UserAccount,
    Category, Spending, Expense, ExpenseLog, Debt, DebtPayment,
)
from .serializers import (
    RegisterSerializer, UserSerializer, UserWriteSerializer,
    FamilySerializer, FamilyMemberSerializer, BankSerializer,
    AccountSerializer, CategorySerializer, SpendingSerializer,
    ExpenseSerializer, ExpenseLogSerializer, DebtSerializer, DebtPaymentSerializer,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _family_context(user):
    """Return (family, member_ids) for the user's family, or (None, [user.id])."""
    family = Family.objects.filter(members=user).first()
    if family:
        return family, list(family.members.values_list('id', flat=True))
    return None, [user.id]


# ─── Auth ─────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response(
                {'message': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {'message': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': str(refresh.access_token),
            'refresh': str(refresh),
        })


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                RefreshToken(refresh_token).blacklist()
        except Exception:
            pass
        return Response({'message': 'Logged out successfully.'})


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        family, member_ids = _family_context(user)
        accounts = Account.objects.filter(family=family) if family else Account.objects.filter(users=user)

        total_balance = accounts.aggregate(t=Sum('balance'))['t'] or Decimal('0')
        monthly_spending = (
            Spending.objects.filter(
                user__in=member_ids,
                spent_at__year=today.year,
                spent_at__month=today.month,
            ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        )
        active_debts_count = Debt.objects.filter(user__in=member_ids, status='active').count()

        upcoming_days = list(range(today.day, min(today.day + 7, 32)))
        upcoming_qs = (
            Expense.objects.filter(account__in=accounts, active=True, day_of_month__in=upcoming_days)
            .select_related('category', 'account')
        )
        return Response({
            'total_balance': total_balance,
            'monthly_spending': monthly_spending,
            'active_debts_count': active_debts_count,
            'upcoming_expenses_count': upcoming_qs.count(),
            'upcoming_expenses': ExpenseSerializer(upcoming_qs, many=True).data,
        })


# ─── Families ─────────────────────────────────────────────────────────────────

class FamilyCreateView(APIView):
    def post(self, request):
        name = request.data.get('name')
        if not name:
            return Response({'message': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        family = Family.objects.create(name=name, owner=request.user)
        FamilyMember.objects.create(family=family, user=request.user, role='owner')
        return Response(FamilySerializer(family).data, status=status.HTTP_201_CREATED)


class FamilyMineView(APIView):
    def get(self, request):
        family = Family.objects.filter(members=request.user).first()
        if not family:
            return Response(None)
        return Response(FamilySerializer(family).data)


class FamilyMembersView(APIView):
    def get(self, request):
        family = Family.objects.filter(members=request.user).first()
        if not family:
            return Response([])
        members = FamilyMember.objects.filter(family=family).select_related('user')
        return Response(FamilyMemberSerializer(members, many=True).data)


class FamilyInviteView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'message': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        family = Family.objects.filter(owner=request.user).first()
        if not family:
            return Response({'message': 'You do not own a family.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        FamilyMember.objects.get_or_create(family=family, user=user, defaults={'role': 'member'})
        return Response({'message': 'Member invited successfully.'})


class FamilyRemoveMemberView(APIView):
    def delete(self, request, user_id):
        family = Family.objects.filter(owner=request.user).first()
        if not family:
            return Response({'message': 'You do not own a family.'}, status=status.HTTP_403_FORBIDDEN)
        deleted, _ = FamilyMember.objects.filter(family=family, user_id=user_id).delete()
        if not deleted:
            return Response({'message': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Accounts ─────────────────────────────────────────────────────────────────

class AccountListCreateView(APIView):
    def get(self, request):
        family, _ = _family_context(request.user)
        if family:
            accounts = Account.objects.filter(family=family).select_related('bank').prefetch_related('users')
        else:
            accounts = Account.objects.filter(users=request.user).select_related('bank').prefetch_related('users')
        return Response(AccountSerializer(accounts, many=True).data)

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        family = Family.objects.filter(members=request.user).first()
        if not family:
            return Response(
                {'message': 'You must belong to a family to create an account.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        owner_id = request.data.get('owner_id')
        if owner_id:
            if not family.members.filter(id=owner_id).exists():
                return Response({'message': 'Owner must be a family member.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                owner = User.objects.get(id=owner_id)
            except User.DoesNotExist:
                return Response({'message': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            owner = request.user
        account = serializer.save(family=family)
        UserAccount.objects.create(user=owner, account=account)
        return Response(AccountSerializer(account).data, status=status.HTTP_201_CREATED)


class AccountDetailView(APIView):
    def _get_account(self, request, pk):
        family, _ = _family_context(request.user)
        qs = Account.objects.select_related('bank').prefetch_related('users')
        try:
            if family:
                return qs.filter(family=family).get(pk=pk)
            return qs.filter(users=request.user).get(pk=pk)
        except Account.DoesNotExist:
            return None

    def put(self, request, pk):
        account = self._get_account(request, pk)
        if not account:
            return Response({'message': 'Account not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AccountSerializer(account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        account = self._get_account(request, pk)
        if not account:
            return Response({'message': 'Account not found.'}, status=status.HTTP_404_NOT_FOUND)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountSummaryView(APIView):
    def get(self, request, pk):
        family, _ = _family_context(request.user)
        qs = Account.objects.select_related('bank')
        try:
            account = qs.filter(family=family).get(pk=pk) if family else qs.filter(users=request.user).get(pk=pk)
        except Account.DoesNotExist:
            return Response({'message': 'Account not found.'}, status=status.HTTP_404_NOT_FOUND)
        today = timezone.now().date()
        monthly_spending = (
            Spending.objects.filter(
                account=account,
                spent_at__year=today.year,
                spent_at__month=today.month,
            ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        )
        active_debts = (
            Debt.objects.filter(account=account, status='active')
            .aggregate(t=Sum('current_balance'))['t'] or Decimal('0')
        )
        return Response({
            'account': AccountSerializer(account).data,
            'monthly_spending': monthly_spending,
            'active_debts': active_debts,
        })


# ─── Spending ─────────────────────────────────────────────────────────────────

class SpendingListCreateView(APIView):
    def get(self, request):
        _, member_ids = _family_context(request.user)
        qs = (
            Spending.objects.filter(user__in=member_ids)
            .select_related('category', 'account', 'account__bank', 'user')
            .order_by('-spent_at')
        )
        return Response(SpendingSerializer(qs, many=True).data)

    def post(self, request):
        serializer = SpendingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SpendingDetailView(APIView):
    def _get(self, request, pk):
        try:
            return Spending.objects.filter(user=request.user).get(pk=pk)
        except Spending.DoesNotExist:
            return None

    def put(self, request, pk):
        obj = self._get(request, pk)
        if not obj:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SpendingSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        obj = self._get(request, pk)
        if not obj:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SpendingSummaryView(APIView):
    def get(self, request):
        today = timezone.now().date()
        _, member_ids = _family_context(request.user)
        qs = Spending.objects.filter(
            user__in=member_ids,
            spent_at__year=today.year,
            spent_at__month=today.month,
        )
        total = qs.aggregate(t=Sum('amount'))['t'] or Decimal('0')
        by_category = list(
            qs.values('category__name', 'category__icon', 'category__color')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        return Response({'total': total, 'by_category': by_category})


# ─── Expenses ─────────────────────────────────────────────────────────────────

class ExpenseListCreateView(APIView):
    def _user_accounts(self, request):
        family, _ = _family_context(request.user)
        if family:
            return Account.objects.filter(family=family)
        return Account.objects.filter(users=request.user)

    def get(self, request):
        qs = (
            Expense.objects.filter(account__in=self._user_accounts(request))
            .select_related('category')
            .prefetch_related('logs')
        )
        return Response(ExpenseSerializer(qs, many=True).data)

    def post(self, request):
        serializer = ExpenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExpenseDetailView(APIView):
    def _get(self, request, pk):
        family, _ = _family_context(request.user)
        accounts = Account.objects.filter(family=family) if family else Account.objects.filter(users=request.user)
        try:
            return Expense.objects.filter(account__in=accounts).get(pk=pk)
        except Expense.DoesNotExist:
            return None

    def put(self, request, pk):
        obj = self._get(request, pk)
        if not obj:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ExpenseSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        obj = self._get(request, pk)
        if not obj:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseCalendarView(APIView):
    def get(self, request):
        family, _ = _family_context(request.user)
        accounts = Account.objects.filter(family=family) if family else Account.objects.filter(users=request.user)
        today = timezone.now().date()
        expenses = (
            Expense.objects.filter(account__in=accounts, active=True)
            .select_related('category', 'account')
            .prefetch_related('logs')
        )
        result = []
        for expense in expenses:
            log = expense.logs.filter(
                paid_at__year=today.year,
                paid_at__month=today.month,
            ).first()
            data = ExpenseSerializer(expense).data
            data['log'] = ExpenseLogSerializer(log).data if log else None
            result.append(data)
        return Response(result)


class ExpensePayView(APIView):
    def post(self, request, pk):
        family, _ = _family_context(request.user)
        accounts = Account.objects.filter(family=family) if family else Account.objects.filter(users=request.user)
        try:
            expense = Expense.objects.filter(account__in=accounts).get(pk=pk)
        except Expense.DoesNotExist:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        today = timezone.now().date()
        log = ExpenseLog.objects.create(
            expense=expense,
            account=expense.account,
            amount_paid=request.data.get('amount_paid', expense.amount),
            paid_at=request.data.get('paid_at', today.isoformat()),
            notes=request.data.get('notes', ''),
        )
        return Response(ExpenseLogSerializer(log).data, status=status.HTTP_201_CREATED)


# ─── Debts ────────────────────────────────────────────────────────────────────

class DebtListCreateView(APIView):
    def get(self, request):
        _, member_ids = _family_context(request.user)
        qs = (
            Debt.objects.filter(user__in=member_ids)
            .select_related('user', 'account', 'account__bank')
            .prefetch_related('payments')
        )
        return Response(DebtSerializer(qs, many=True).data)

    def post(self, request):
        serializer = DebtSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DebtDetailView(APIView):
    def _get(self, request, pk):
        try:
            return (
                Debt.objects.filter(user=request.user)
                .prefetch_related('payments')
                .get(pk=pk)
            )
        except Debt.DoesNotExist:
            return None

    def put(self, request, pk):
        obj = self._get(request, pk)
        if not obj:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DebtSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        obj = self._get(request, pk)
        if not obj:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


USD_TO_BOB = Decimal('9.97')


class DebtSummaryView(APIView):
    def get(self, request):
        _, member_ids = _family_context(request.user)
        all_qs = Debt.objects.filter(user__in=member_ids).select_related('account')
        active_count = all_qs.filter(status='active').count()

        def _agg(qs):
            r = qs.aggregate(orig=Sum('original_amount'), curr=Sum('current_balance'))
            orig = r['orig'] or Decimal('0')
            curr = r['curr'] or Decimal('0')
            return curr, orig - curr  # owed, paid

        bob_qs = all_qs.filter(Q(account__currency='BOB') | Q(account__isnull=True))
        usd_qs = all_qs.filter(account__currency='USD')

        bob_owed, bob_paid = _agg(bob_qs)
        usd_owed, usd_paid = _agg(usd_qs)

        return Response({
            'bob': {'owed': bob_owed, 'paid': bob_paid},
            'usd': {'owed': usd_owed, 'paid': usd_paid},
            'total_owed_bob': bob_owed + usd_owed * USD_TO_BOB,
            'total_paid_bob': bob_paid + usd_paid * USD_TO_BOB,
            'active_count': active_count,
        })


class DebtPaymentCreateView(APIView):
    def post(self, request, pk):
        try:
            debt = Debt.objects.filter(user=request.user).get(pk=pk)
        except Debt.DoesNotExist:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        amount = request.data.get('amount')
        if not amount:
            return Response({'message': 'Amount is required.'}, status=status.HTTP_400_BAD_REQUEST)

        account_id = request.data.get('account_id')
        if not account_id:
            return Response({'message': 'account_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.now().date()
        payment = DebtPayment.objects.create(
            debt=debt,
            account_id=account_id,
            amount=amount,
            paid_at=request.data.get('paid_at', today.isoformat()),
            notes=request.data.get('notes', ''),
        )

        amount_dec = Decimal(str(amount))
        debt.current_balance = max(Decimal('0'), debt.current_balance - amount_dec)
        if debt.current_balance == Decimal('0'):
            debt.status = 'paid'
        debt.save()

        return Response(DebtPaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


# ─── Banks ────────────────────────────────────────────────────────────────────

class BankListView(APIView):
    def get(self, request):
        return Response(BankSerializer(Bank.objects.all(), many=True).data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'message': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = BankSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BankDetailView(APIView):
    def _get(self, pk):
        try:
            return Bank.objects.get(pk=pk)
        except Bank.DoesNotExist:
            return None

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({'message': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        obj = self._get(pk)
        if not obj:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BankSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'message': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        obj = self._get(pk)
        if not obj:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Categories ───────────────────────────────────────────────────────────────

class CategoryListCreateView(APIView):
    def get(self, request):
        return Response(CategorySerializer(Category.objects.all(), many=True).data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetailView(APIView):
    def _get(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def put(self, request, pk):
        obj = self._get(pk)
        if not obj:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        obj = self._get(pk)
        if not obj:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Users (admin) ────────────────────────────────────────────────────────────

class UserListCreateView(APIView):
    def get(self, request):
        return Response(UserSerializer(User.objects.all(), many=True).data)

    def post(self, request):
        serializer = UserWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    def _get(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self._get(pk)
        if not user:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)

    def put(self, request, pk):
        user = self._get(pk)
        if not user:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserWriteSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user).data)

    def delete(self, request, pk):
        user = self._get(pk)
        if not user:
            return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
