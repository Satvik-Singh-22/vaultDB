from rest_framework import serializers
from .models import *

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model= Branch
        fields= '__all__' 

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__' 

class BranchManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model= BranchManager
        fields= '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model= Customer
        fields= '__all__'

class AccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= AccountType
        fields= '__all__'

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model= Account
        fields= '__all__'

class LoanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= LoanType
        fields= '__all__'

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model= Loan
        fields= '__all__'

class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model= Repayment
        fields= '__all__'

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model= Card
        fields= '__all__'

class CustomerSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model= CustomerSupport
        fields= '__all__'

class BankTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model= BankTransaction
        fields= '__all__'
