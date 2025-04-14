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

class RegisterView(APIView):
    
    def post(self, request):
        email= request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({"detail": "Email and password required"},status=status.HTTP_400_BAD_REQUEST)
        if Customer.objects.filter(username=email).exists():
            return Response({"detail": "Customer with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        customer = Customer.objects.create(
            username=email,
            password=make_password(password)
        )    
        return Response({
            "detail": "Customer created successfully"},
            status= status.HTTP_201_CREATED)
    
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("email")
        password = request.data.get("password")
        print("Login attempt:")
        print("Email:", username)
        print("Password:", password)
        try:
            user = Customer.objects.get(username=username)
            role = "customer"
            user_id= user.customer_id
        except Customer.DoesNotExist:
            try:
                user = Employee.objects.get(username=username)
                role = "employee"
                user_id= user.employee_id
            except Employee.DoesNotExist:
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        if not check_password(password, user.password):
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = {
            "id": user_id,
            "username": user.username,
            "role": role,
        }

        refresh = RefreshToken.for_user(user)
        refresh["role"]= role 
        for key, value in payload.items():
            refresh[key] = value

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": role
        }, status=status.HTTP_200_OK)
    
    
def frontend(request):
    return render(request, "index.html")

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def whoami(request):
    user= request.user

    is_employee = Employee.objects.filter(username=user.username).exists()
    is_manager = is_employee and BranchManager.objects.filter(manager_id_username=user.username).exists()
    is_customer = Customer.objects.filter(email=user.username).exists()

    return Response({
        'username': user.username,
        'is_employee': is_employee,
        'is_manager': is_manager,
        'is_customer': is_customer
    })

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
    accounts = Account.objects.filter(customer=customer)
    transactions = BankTransaction.objects.filter(account__in=accounts).order_by('-timestamp')
    loans = Loan.objects.filter(customer=customer)
    cards = Card.objects.filter(account__in=accounts)

    dashboard_data = {
        "accounts": AccountSerializer(accounts, many=True).data,
        "transactions": BankTransactionSerializer(transactions, many=True).data,
        "loans": LoanSerializer(loans, many=True).data,
        "cards": CardSerializer(cards, many=True).data,
    }

    return Response(dashboard_data)
