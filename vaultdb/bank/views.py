from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *

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
    serializer_class = CustomerSupportSerializer  # ✅ Correct

    
class BankTransactionViewSet(viewsets.ModelViewSet):
    queryset= BankTransaction.objects.all()
    serializer_class= BankTransactionSerializer
    
def frontend(request):
    return render(request, "index.html")