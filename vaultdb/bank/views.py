from django.shortcuts import render


def home(request):
    return render(request, 'bank/home.html')

def login_view(request):
    return render(request, 'bank/login.html')

def dashboard(request):
    return render(request, 'bank/dashboard.html')

def apply_loan(request):
    return render(request, 'bank/loan_application.html')
