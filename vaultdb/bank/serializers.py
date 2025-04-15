from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User

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

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user with this email")

        credentials = {
            'username': user.username,
            'password': password
        }

        user = authenticate(**credentials)

        if not user:
            raise serializers.ValidationError("Incorrect credentials")

        data = super().validate(credentials)
        data["email"] = user.email
        data["username"] = user.username
        return data
    

class CustomerProfileSerializer(serializers.ModelSerializer):
    accounts = serializers.SerializerMethodField()
    cards = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'customer_id', 'name', 'email', 'phone_number', 'address',
            'date_of_birth', 'accounts', 'cards'
        ]

    def get_accounts(self, obj):
        accounts = Account.objects.filter(customer_id=obj)
        return AccountSerializer(accounts, many=True).data
    def get_cards(self, obj):
        cards = Card.objects.filter(account__customer_id=obj)
        return CardSerializer(cards, many=True).data

class AccountDataSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type_id.type_name')

    class Meta:
        model = Account
        fields = ['accountID', 'balance', 'type_name']

