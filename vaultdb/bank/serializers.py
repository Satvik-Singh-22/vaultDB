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
    card_number = serializers.UUIDField(read_only=True)

    class Meta:
        model = Card
        fields = ['card_id', 'card_number', 'expiry_date', 'card_type', 'account']


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
    customer_id = serializers.SerializerMethodField()
    branch_id = serializers.SerializerMethodField()
    interest_rate = serializers.DecimalField(source='type_id.interest_rate', max_digits=5, decimal_places=2)

    class Meta:
        model = Account
        fields = ['accountID', 'balance', 'type_name', 'customer_id', 'branch_id', 'interest_rate']

    def get_customer_id(self, obj):
        return {'customer_id': obj.customer_id.customer_id} if obj.customer_id else None

    def get_branch_id(self, obj):
        return {'branch_id': obj.branch_id.branch_id} if obj.branch_id else None

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransaction
        fields = [
            'transaction_id',
            'account_id',
            'amount',
            'transactionType',
            'timestamp',
            'status',
            'receiver_account_id',
            'employee_id'  # if applicable
        ]

class AccountCreateSerializer(serializers.ModelSerializer):
    initial_deposit = serializers.DecimalField(max_digits=17, decimal_places=2, write_only=True)
    
    class Meta:
        model = Account
        fields = ['type_id', 'branch_id', 'initial_deposit']
        
    def create(self, validated_data):
        request = self.context['request']
        
        # Get the customer related to this user by username
        try:
            customer = Customer.objects.get(username=request.user.username)
        except Customer.DoesNotExist:
            raise serializers.ValidationError("No customer account found for this user")
            
        initial_deposit = validated_data.pop('initial_deposit')
        
        account = Account.objects.create(
            customer_id=customer,
            balance=initial_deposit,
            **validated_data
        )
        
        # Optionally create a transaction record for the initial deposit
        BankTransaction.objects.create(
            account_id=account,
            transaction_type='DEPOSIT',
            amount=initial_deposit,
            status='COMPLETED'
        )
        
        return account
    
class ChangePinSerializer(serializers.Serializer):
    new_pin = serializers.CharField(min_length=4, max_length=4)

class CardLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['limit_daily', 'limit_monthly', 'international_usage']

class CardTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransaction
        fields = ['transaction_id', 'transactionType', 'amount', 'timestamp', 'status']
