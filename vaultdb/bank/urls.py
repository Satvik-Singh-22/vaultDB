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
print(f"Registering employee dashboard URL: employee/dashboard/ -> {employee_dashboard_view.__name__}")

urlpatterns = [
    # API routes
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('empboard/', employee_dashboard_view, name='employee_dashboard'),
    path('whoami/', whoami),
    path('token/', LoginView.as_view(), name='custom_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('test-loan/', test_loan_flow),
    path('test-loan/', views.test_loan, name='test-loan'),
    path('customers/me/', customer_profile, name="customer_profile"),
    path('accounts/<int:account_id>/', get_account_detail, name= "account-details"),
    path('accounts/<int:account_id>/transactions/', get_account_transactions, name= "view-account-transactions"),
    path('customers/<int:customer_id>/', views.get_customer_detail),
    path('branches/<int:branch_id>/', views.get_branch_detail),
    path('transactions/', views.get_user_transactions, name='account-transactions'),
    path('account-types/', get_account_types, name='get_account_types'),
    path('branches/', get_branches, name='get_branches'),
    path('accounts/', AccountViewAPI.as_view(), name='create_account'),
    path('transactions/transfer/', transfer_funds, name='transfer_funds'),
    path('cards/', CardListAPIView.as_view(), name='card-list'),
    path('cards/request/', RequestNewCardAPIView.as_view(), name='request-card'),
    path('cards/<int:card_id>/block/', BlockCardAPIView.as_view(), name='block-card'),
    path('api/cards/<int:card_id>/statement/', views.card_statement_view),


]
