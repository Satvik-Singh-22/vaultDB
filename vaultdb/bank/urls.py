from django.urls import path
from .views import home, login_view, dashboard, apply_loan

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('apply-loan/', apply_loan, name='apply_loan'),
]
