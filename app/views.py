from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

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
