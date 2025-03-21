from django.contrib import admin

from .models import *
# Register your models here.

my_models= [Branch, Employee, BranchManager,
            Customer, AccountType, Account,
            LoanType, Loan, Repayment,
            Card, CustomerSupport, BankTransaction]
for m in my_models:
    admin.site.register(m)
