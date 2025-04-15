from datetime import date, timedelta, timezone
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status
from .models import *
from .serializers import *
from .api_queries import *
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, mixins


class BranchViewSet(viewsets.ModelViewSet):
    queryset= Branch.objects.all()
    serializer_class= BranchSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset= Employee.objects.all()
    serializer_class= EmployeeSerializer

class BranchManagerViewSet(viewsets.ModelViewSet):
    queryset= BranchManager.objects.all()
    serializer_class= BranchManagerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset= Customer.objects.all()
    serializer_class= CustomerSerializer

class AccountTypeViewSet(viewsets.ModelViewSet):
    queryset= AccountType.objects.all()
    serializer_class= AccountTypeSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset= Account.objects.all()
    serializer_class= AccountSerializer

class LoanViewSet(viewsets.ModelViewSet):
    queryset= Loan.objects.all()
    serializer_class= LoanSerializer

class LoanTypeViewSet(viewsets.ModelViewSet):
    queryset= LoanType.objects.all()
    serializer_class= LoanTypeSerializer

class RepaymentViewSet(viewsets.ModelViewSet):
    queryset= Repayment.objects.all()
    serializer_class= RepaymentSerializer

class CardViewSet(viewsets.ModelViewSet):
    queryset= Card.objects.all()
    serializer_class= CardSerializer

class CustomerSupportViewSet(viewsets.ModelViewSet):
    queryset= CustomerSupport.objects.all()
    serializer_class= LoanSerializer
    
class BankTransactionViewSet(viewsets.ModelViewSet):
    queryset= BankTransaction.objects.all()
    serializer_class= BankTransactionSerializer

from django.http import JsonResponse

def test_loan(request):
    return JsonResponse({"status": "Loan applied and approved"})


# bank/views.py
from django.http import JsonResponse
from .api_queries import apply_and_approve_loan

def test_loan_flow(request):
    try:
        apply_and_approve_loan('Mitchel Johnson', 'Employee_8')
        return JsonResponse({'status': 'Loan applied and approved'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"detail": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        if Customer.objects.filter(username=email).exists() or User.objects.filter(username=email).exists():
            return Response({"detail": "Customer with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a Customer
        customer = Customer.objects.create(
            username=email,
            password=make_password(password)
        )

        # Create a corresponding Django User for JWT
        User.objects.create_user(
            username=email,
            password=password
        )

        return Response({"detail": "Customer created successfully"}, status=status.HTTP_201_CREATED)
class LoginView(APIView):
    permission_classes = [AllowAny]  
    def post(self, request):
        username = request.data.get("email")
        password = request.data.get("password")
        print("Login attempt:")
        print("Email:", username)
        print("Password:", password)
        
        # First try to find the Django User model instance
        try:
            # This assumes you have a User model with matching username
            auth_user = User.objects.get(username=username)
            
            # Now determine if they're a customer or employee
            try:
                user = Customer.objects.get(username=username)
                role = "customer"
                user_id = user.customer_id
            except Customer.DoesNotExist:
                try:
                    user = Employee.objects.get(username=username)
                    role = "employee"
                    user_id = user.employee_id
                except Employee.DoesNotExist:
                    return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
                
            # Check password (you might want to use Django's auth system here)
            if not check_password(password, user.password):
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate token for the Django User
            refresh = RefreshToken.for_user(auth_user)
            
            # Add custom claims
            refresh["role"] = role
            refresh["id"] = user_id
            refresh["username"] = username
            
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": role
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)    
    
def frontend(request):
    return render(request, "index.html")

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def whoami(request):
    user = request.user
    
    # Add debugging
    print("User in request:", user.username)
    print("User ID:", user.id)
    print("Request auth:", request.auth)  # This shows the token being used
    
    # Check if this username exists in Employee model
    employee_exists = Employee.objects.filter(username=user.username).exists()
    print("Username exists in Employee model:", employee_exists)
    
    # Original code continues...
    is_employee = Employee.objects.filter(username=user.username).exists()
    is_manager = is_employee and BranchManager.objects.filter(manager_id__username=user.username).exists()
    is_customer = Customer.objects.filter(username=user.username).exists()
    
    r = {
        'username': user.username,
        'is_employee': is_employee,
        'is_manager': is_manager,
        'is_customer': is_customer
    }
    print("whoami view:", r)
    return Response(r)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_accounts(request):
    # Get the authenticated user
    user = request.user
    
    # Fetch accounts related to this user
    accounts = Account.objects.filter(customer=user.customer)
    
    # Serialize accounts
    serializer = AccountSerializer(accounts, many=True)
    
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    user = request.user

    try:
        customer = Customer.objects.get(email=user.username)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found."}, status=404)

    # Fetch data
    accounts = Account.objects.filter(customer_id=customer)
    transactions = BankTransaction.objects.filter(account_id__in=accounts).order_by('-timestamp')[:5]
    loans = Loan.objects.filter(customer_id=customer)
    cards = Card.objects.filter(account__in=accounts)

    dashboard_data = {
        "username": customer.name,
        "accounts": AccountSerializer(accounts, many=True).data,
        "transactions": BankTransactionSerializer(transactions, many=True).data,
        "loans": LoanSerializer(loans, many=True).data,
        "cards": CardSerializer(cards, many=True).data,
    }
    print(dashboard_data)
    return Response(dashboard_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_dashboard_view(request):
    """
    View for employee dashboard data
    """
    try:
        # Get the employee based on the authenticated user
        employee = Employee.objects.get(user=request.user)

        
        # Get the branch the employee works at
        branch = employee.branch
        
        # Check if the employee is a manager
        is_manager = BranchManager.objects.filter(manager_id=employee.employee_id).exists()
        
        # Count customers, loans, and customer support cases in this branch
        customer_count = Customer.objects.filter(branch=branch).count()
        loan_count = Loan.objects.filter(customer__branch=branch, status='ACTIVE').count()
        complaint_count = CustomerSupport.objects.filter(branch=branch, status='OPEN').count()
        
        # Serialize the employee and branch data
        employee_data = EmployeeSerializer(employee).data
        branch_data = BranchSerializer(branch).data
        
        # Return all the relevant data
        return Response({
            'employee': employee_data,
            'branch': branch_data,
            'customer_count': customer_count,
            'loan_count': loan_count,
            'complaint_count': complaint_count,
            'is_manager': is_manager
        }, status=status.HTTP_200_OK)
        
    except Employee.DoesNotExist:
        return Response({
            'detail': 'Employee data not found for this user.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def customer_profile(request):
    user= request.user
    try:
        customer = Customer.objects.get(email=user.username)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found."}, status=404)
    serializer = CustomerProfileSerializer(customer)
    print(serializer.data)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def AccountListView(request):
    user = request.user
    try:
        
        customer = Customer.objects.get(email=user.username)
        accounts = Account.objects.filter(customer_id=customer)
        serializer = AccountDataSerializer(accounts, many=True)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=404)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_account_detail(request, account_id):
    try:
        account = Account.objects.get(accountID=account_id)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)

    # Restrict customer access to their own account
    if hasattr(request.user, 'customer'):
        if account.customer != request.user.customer:
            return Response({'error': 'Unauthorized'}, status=403)

    # If the user is an employee or admin, let it pass
    serializer = AccountDataSerializer(account)
    print(serializer.data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_account_transactions(request, account_id):
    try:
        account = Account.objects.get(accountID=account_id, customer=request.user.customer)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)

    transactions = BankTransaction.objects.filter(
        Q(account_id=account) | Q(receiver_account_id=account)
    ).order_by('-timestamp')

    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_detail(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_branch_detail(request, branch_id):
    try:
        branch = Branch.objects.get(branch_id=branch_id)
        serializer = BranchSerializer(branch)
        return Response(serializer.data)
    except Branch.DoesNotExist:
        return Response({'error': 'Branch not found'}, status=404)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_transactions(request):
    try:
        user = request.user
        
        # For customers: filter only their transactions
        if hasattr(user, 'customer'):
            customer_accounts = Account.objects.filter(customer_id=user.customer)
            transactions = BankTransaction.objects.filter(account_id__in=customer_accounts)
        else:
            # Employees/Admins see all transactions (or you can restrict as needed)
            transactions = BankTransaction.objects.all()
    except Exception as e:
        return Response({"error": f"Transaction unable to be fetched: {str(e)}"}, status=404)
    serializer = TransactionSerializer(transactions.order_by('-timestamp'), many=True)
    print(serializer.data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_account_types(request):
    types = AccountType.objects.all()
    serializer = AccountTypeSerializer(types, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_branches(request):
    branches = Branch.objects.all()
    serializer = BranchSerializer(branches, many=True)
    return Response(serializer.data)


class AccountViewAPI(generics.GenericAPIView, 
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AccountCreateSerializer
        return AccountDataSerializer
    
    def get_queryset(self):
        user = self.request.user
        try:
            customer = Customer.objects.get(email=user.username)
            return Account.objects.filter(customer_id=customer)
        except Customer.DoesNotExist:
            return Account.objects.none()
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

# views.py
from decimal import Decimal
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_funds(request):
    account_id = request.data.get('account_id')
    receiver_account_id = request.data.get('receiver_account_id')
    amount = request.data.get('amount')
    description = request.data.get('description')
    
    try:
        amount = Decimal(amount)  # ✅ Safe and precise
    except:
        return Response({'detail': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate inputs
    if not all([account_id, receiver_account_id, amount]):
        return Response({'detail': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get accounts
        from_account = Account.objects.get(accountID=account_id)
        to_account = Account.objects.get(accountID=receiver_account_id)
        
        # Verify account ownership - using customer_id relationship
        if from_account.customer_id.username != request.user.username:
            return Response({'detail': 'Not authorized to transfer from this account'},
                          status=status.HTTP_403_FORBIDDEN)
        
        # Check sufficient funds
        if from_account.balance < (amount):
            return Response({'detail': 'Insufficient funds'},
                          status=status.HTTP_400_BAD_REQUEST)
            
        # Create transaction in a transaction
        from django.db import transaction
        with transaction.atomic():
            # Deduct from source account
            from_account.balance -= (amount)
            from_account.save()
            
            # Add to target account
            to_account.balance += (amount)
            to_account.save()
            
            # Create transaction record
            transaction_record = BankTransaction.objects.create(
                account_id=from_account,
                receiver_account_id=to_account,
                amount=amount,
                transactionType='Transfer',
                status='COMPLETED'
            )
        
        return Response({
            'detail': 'Transfer successful',
            'transaction_id': transaction_record.transaction_id
        }, status=status.HTTP_200_OK)
        
    except Account.DoesNotExist:
        return Response({'detail': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class CardListAPIView(generics.ListAPIView):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = self.request.user.customer
        return Card.objects.filter(account__customer_id=customer)

# Request a new card
class RequestNewCardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        customer = request.user.customer
        account_id = request.data.get("account_id")
        card_type = request.data.get("card_type")

        if not account_id or not card_type:
            return Response({"error": "account_id and card_type are required."}, status=400)

        account = get_object_or_404(Account, pk=account_id, customer_id=customer)

        new_card = Card.objects.create(
            card_number=uuid.uuid4(),
            expiry_date=date.today() + timedelta(days=365 * 4),
            card_type=card_type,
            account=account
        )

        serializer = CardSerializer(new_card)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Block a card (for now, just deletes it)
class BlockCardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, card_id):
        customer = request.user.customer
        card = get_object_or_404(Card, pk=card_id, account__customer_id=customer)

        card.delete()  # Optional: replace with `card.is_blocked = True` if you add such a field
        return Response({"message": "Card blocked successfully."}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def card_statement_view(request, card_id):
    one_month_ago = timezone.now() - timedelta(days=30)
    transactions = BankTransaction.objects.filter(
        card_id=card_id,
        timestamp__gte=one_month_ago
    ).order_by('-timestamp')
    
    serializer = BankTransactionSerializer(transactions, many=True)
    return Response(serializer.data)