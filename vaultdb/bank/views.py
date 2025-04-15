from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status
from .models import *
from .serializers import *
from .api_queries import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes


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

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
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
        employee = Employee.objects.get(username=request.user.username)
        
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