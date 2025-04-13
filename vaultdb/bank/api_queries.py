from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from .serializers import *

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def whoami(request):
    user= request.user

    is_employee = Employee.objects.filter(username=user.username).exists()
    is_manager = BranchManager.objects.filter(managerid__username=user.username).exists()
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
