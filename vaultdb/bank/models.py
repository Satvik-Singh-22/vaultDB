from django.db import models
import uuid
# Create your models here.
class Branch( models.Model):
    branch_id = models.AutoField(primary_key= True)
    name = models.CharField(max_length= 100)
    location = models.TextField()

    def __str__(self):
        return f"ID: {self.branch_id}\t Name: {self.name}"

class Employee ( models.Model):
    employee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length= 100)
    branch_id= models.ForeignKey('Branch', on_delete= models.PROTECT)
    role = models.CharField(max_length=50)
    username= models.CharField(max_length=50, null=False, unique=True)
    password= models.CharField(max_length=25, null = False)

    def __str__(self):
        return f"ID: {self.employee_id}\t Name: {self.name}"
    
class BranchManager(models.Model):
    manager_id = models.OneToOneField(
        'Employee',
        on_delete=models.CASCADE,
        primary_key=True
        )
    branch = models.OneToOneField('Branch', on_delete=models.CASCADE,
                                  unique=True)
    

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    address = models.TextField()
    phone_number = models.CharField(max_length=25)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class AccountType(models.Model):
    type_id= models.AutoField(primary_key= True)
    type_name =models.CharField(max_length=20, unique=True, null= False)
    interest_rate = models.DecimalField(decimal_places=2, max_digits=7, null=False)

class Account(models.Model):
    accountID= models.AutoField(primary_key=True)
    type_id= models.ForeignKey('AccountType',on_delete=models.PROTECT)
    balance= models.DecimalField(max_digits=17, decimal_places=2, default=0.00)
    customer_id= models.ForeignKey('Customer', on_delete=models.CASCADE)
    branch_id= models.ForeignKey('Branch', on_delete=models.CASCADE)

class LoanType(models.Model):
    loan_code= models.AutoField(primary_key=True)
    name= models.CharField(max_length=50, unique= True, null= False)
    interest_rate= models.DecimalField(
        max_digits=7, decimal_places= 2,
        null= False
    )

class Loan(models.Model):
    loan_id = models.AutoField(primary_key= True)
    loan_code= models.ForeignKey('Loan', on_delete=models.DO_NOTHING)
    amount= models.DecimalField(
        max_digits= 7, decimal_places= 2, 
        null= False
    )
    start_date = models.DateField( auto_now_add=True )
    tenure = models.PositiveIntegerField()
    customer_id= models.ForeignKey('Customer', on_delete= models.CASCADE)
    employee_id= models.ForeignKey('Employee', on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('Approved', 'APPROVED'),
        ('Pending', 'PENDING'),
        ('Repaid', 'REPAID'),
        ('Overdue', 'OVERDUE'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')  # CHECK (Status IN (...))

class Repayment( models.Model):
    repayment_id = models.AutoField(primary_key= True)
    loan_id = models.ForeignKey('Loan', on_delete=models.CASCADE)
    customer_id= models.ForeignKey('Customer', on_delete= models.CASCADE)
    due_date= models.DateField(null=False)
    amount= models.DecimalField(decimal_places= 2, 
                                max_digits=7, null= False)
    STATUS_CHOICES =[
        ('Pending', 'PENDING'),
        ('Paid', 'PAID'),
        ('Overdue', 'OVERDUE')
    ]

    status= models.CharField(max_length=20, choices= STATUS_CHOICES, default= 'Pending')
    payment_date= models.DateField()


class Card(models.Model):
    CARD_TYPE_CHOICES = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),
    ]

    card_id = models.AutoField(primary_key=True)
    card_number = models.UUIDField(default=uuid.uuid4, unique=True)
    expiry_date = models.DateField()
    card_type = models.CharField(max_length=10, choices=CARD_TYPE_CHOICES)
    account = models.ForeignKey('Account', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.card_type} Card ({self.card_number})"

class CustomerSupport(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    support_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    issue_description = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Support {self.support_id} - {self.status}"
    
class BankTransaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)

    TRANSACTION_CHOICES = [
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
        ('Transfer', 'Transfer')
    ]
    transactionType = models.CharField(max_length=20, choices=TRANSACTION_CHOICES)

    amount = models.DecimalField(max_digits=17, decimal_places=2, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    account_id = models.ForeignKey('Account', on_delete=models.SET_NULL, null=True)
    receiver_account_id = models.ForeignKey(
        'Account', on_delete=models.SET_NULL, null=True, related_name='receiver_transactions'
    )
    employee_id = models.ForeignKey('Employee', on_delete=models.DO_NOTHING, null=True)

    STATUS_CHOICES = [
        ('Failed', 'Failed'),
        ('Successful', 'Successful'),
        ('Pending', 'Pending')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
