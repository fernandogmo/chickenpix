from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import EmailForm
import requests

# Create your views here.
def index(request):
    return HttpResponse("Hello, world! PREPARE TO BE PIXELATED")

def email_auth_success(request):
    request.POST.get("email", "")
    return render(request, 'success.html')

def email_auth_failure(request):
    return render(request, 'failure.html')

@login_required
def photos(request):
    return render(request, 'photos.html')

def home(request):
    if request.method == 'GET':
        form = EmailForm()
    else:
        form = EmailForm(request.POST)
        if form.is_valid():
            response = requests.post('http://localhost:8000/auth/email/', data={'email': request.POST.get("email", "")})
            if response.status_code == 200:
                return render(request, 'success.html')
            else:
                return render(request, 'failure.html')
    return render(request, 'home.html', {'form': form})
