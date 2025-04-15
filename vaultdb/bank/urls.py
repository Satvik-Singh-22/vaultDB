# bank/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *
from django.urls import path
from .views import test_loan_flow
from bank.views import test_loan  # or wherever the test_loan view is defined
from django.urls import path
from . import views  # Import the views module


router = DefaultRouter()
router.register(r'employee', EmployeeViewSet)
router.register(r'branch', BranchViewSet)
router.register(r'branchmanager', BranchManagerViewSet)
router.register(r'customer', CustomerViewSet)
router.register(r'accounttype', AccountTypeViewSet)
router.register(r'account', AccountViewSet)
router.register(r'loantype', LoanTypeViewSet)
router.register(r'loan', LoanViewSet)
router.register(r'repayment', RepaymentViewSet)
router.register(r'customersupport', CustomerSupportViewSet)
router.register(r'banktransaction', BankTransactionViewSet)

urlpatterns = [
    # API rapioutes
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('api/dashboard/', dashboard_view, name = 'dashboard'),
    path('employee/dashboard/', employee_dashboard_view, name='employee_dashboard'),
    path('whoami/', whoami),
    path('token/',  LoginView.as_view(), name='custom_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('test-loan/', test_loan_flow),
    path('test-loan/', views.test_loan, name='test-loan'),


]
