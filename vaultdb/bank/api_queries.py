from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from .serializers import *

# bank/api_queries.py
from django.db import connection

def apply_and_approve_loan(customer_name, employee_name='Employee_8'):
    with connection.cursor() as cursor:
        # Step 1: Create Loan
        cursor.execute("""
        WITH new_loan AS (
            INSERT INTO Loan (Type, LoanAmount, StartDate, Tenure, CustomerID, EmployeeID, Status)
            VALUES (
                (SELECT Code FROM LoanType WHERE Name = 'Home Loan'),
                500000.00,
                CURRENT_DATE,
                10,
                (SELECT CustomerID FROM Customer WHERE Name = %s),
                NULL,
                'Pending'
            )
            RETURNING LoanID, CustomerID
        )

        -- Step 2: Create corresponding Loan Account
        INSERT INTO Account (TypeID, Balance, CustomerID, BranchID)
        SELECT 
            (SELECT TypeID FROM AccountType WHERE TypeName = 'Loan Account'),
            500000.00,
            nl.CustomerID,
            (SELECT BranchID FROM Customer WHERE CustomerID = nl.CustomerID)
        FROM new_loan nl;
        """, [customer_name])

        # Step 3: Approve Loan
        cursor.execute("""
        UPDATE Loan
        SET 
            Status = 'Approved',
            EmployeeID = (SELECT EmployeeID FROM Employee WHERE Name = %s)
        WHERE 
            CustomerID = (SELECT CustomerID FROM Customer WHERE Name = %s)
            AND Status = 'Pending';
        """, [employee_name, customer_name])
