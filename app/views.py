from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import EmailForm, TokenForm
import requests
import datetime
from rest_framework.authtoken.models import Token

User = get_user_model()

# Create your views here.
def index(request):
    return HttpResponse("Hello, world! PREPARE TO BE PIXELATED")

def success(request):
    if request.method == 'GET':
        form = TokenForm()
        message = request.GET.get("message", "")
    else:
        form = TokenForm(request.POST)
        if form.is_valid():
            response = requests.post('http://0.0.0.0:8000/callback/auth/', data={'token': request.POST.get("token", "")})
            if response.status_code == 200:
                token = response.json().get('token')
                user_token = Token.objects.get(key=token)
                user = User.objects.get(id=user_token.user_id)
                login(request, user)
                return redirect('/')
            else:
                return redirect('/')
        else:
            return render(request, 'failure.html')
    return render(request, 'success.html', {'form': form, 'message': message})
"""
def failure(request):
    return render(request, 'failure.html')
"""
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
                return redirect('/success', message=response.json().get('detail'))
            else:
                return render('/', {'message': response.json().get('detail')})
    return render(request, 'home.html', {'form': form, 'message': 'You are not logged in. Please enter your email address to receive a login token. No signup is required!'})
