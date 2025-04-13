# bank/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

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
    path('/', include(router.urls)),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('whoami/', whoami),
    path('token/',  LoginView.as_view(), name='custom_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
