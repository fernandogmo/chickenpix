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
        message = request.session['_message']
    else:
        form = TokenForm(request.POST)
        if form.is_valid():
            response = requests.post('http://localhost:8000/callback/auth/', data={'token': request.POST.get("token", "")})
            if response.status_code == 200:
                token = response.json().get('token')
                user_token = Token.objects.get(key=token)
                user = User.objects.get(id=user_token.user_id)
                login(request, user)
                return redirect('/')
            else:
                request.session['_message'] = response.json().get('token', "NO DETAIL!")[0] + " Please re-enter your token."
                return redirect('/success')
        else:
            request.session['_message'] = "Something went wrong. Please re-enter your token."
            return redirect('/success')
    return render(request, 'success.html', {'form': form, 'message': message})


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
                request.session['_message'] = response.json().get('detail', "NO DETAIL!")

                return redirect('/success')
            else:
                return render('/', {'message': response.json().get('detail')})
    return render(request, 'home.html', {'form': form, 'message': 'You are not logged in. Please enter your email address to receive a login token. No signup is required!'})
