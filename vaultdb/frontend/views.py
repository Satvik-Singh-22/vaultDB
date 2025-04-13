# frontend/views.py
from django.shortcuts import render

def frontend(request):
    return render(request, 'index.html')  # Or wherever your React app's entry point is located
