from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import EmailForm, TokenForm
from .validators import login_user
import requests

def validate(request):
    """
    Validates the 6-digit callback token sent to user
    and entered into TokenForm.

    If the callback token is valid, the callback endpoint
    will return an authentication token and the user will
    be logged in and redirected to the homepage.

    Otherwise, the user is sent back to the 6-digit token
    form.
    """
    if request.method == 'GET':
        # Render page with empty form
        form = TokenForm()
        message = request.session['_message']
    elif request.method == 'POST':
        # Initialize TokenForm instance with POSTed 6-digit token
        form = TokenForm(request.POST)
        message = ' Please re-enter your token.'
        if form.is_valid():
            # If token is 6 digits, authenticate it and receive authentication token
            response = requests.post('http://localhost:8000/callback/auth/',
                                     data={'token': request.POST.get("token", "")})
            # Save authentication token or error message
            auth_token = response.json().get('token', 'NO DETAIL!')
            if response.status_code == 200:
                # Make sure auth token is associated with a user
                login_user(request, auth_token)
                return redirect('/')
            else:
                request.session['_message'] = ' '.join(auth_token) + message
                return redirect('/validate')
        else:
            request.session['_message'] = 'Something went wrong.' + message
            return redirect('/validate')
    return render(request, 'validate.html', {'form': form, 'message': message})


@login_required
def photos(request):
    return render(request, 'photos.html')

def home(request):
    """
    Handles homepage view.

    Renders a page with a email address form &
    sends an email containing a 6-digit login token
    """
    if request.method == 'GET':
        form = EmailForm()
    else:
        form = EmailForm(request.POST)
        if form.is_valid():
            response = requests.post('http://localhost:8000/auth/email/',
                                     data={'email': request.POST.get("email", "")})
            detail = response.json().get('detail', 'NO DETAIL!')
            if response.status_code == 200:
                request.session['_message'] = detail
                return redirect('/validate')
            else:
                return render(request, 'home.html', {'form': form, 'message': detail})
    return render(request, 'home.html', {'form': form,
                                         'message': 'You are not logged in. \
                                         Please enter your email address to \
                                         receive a login token. No signup is required!'})
