from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import EmailForm, TokenForm
from .validators import login_user
from .models import Album, Photo, Archive, Link
import requests
import os

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
                if not login_user(request, auth_token):
                    request.session['_message'] = "We couldn't log you in." + message
                    return redirect('/validate')
                return redirect('/')
            else:
                request.session['_message'] = ' '.join(auth_token) + message
                return redirect('/validate')
        else:
            request.session['_message'] = 'Something went wrong.' + message
            return redirect('/validate')
    return render(request, 'validate.html', {'form': form, 'message': message})


@login_required
def upload(request):
    return render(request, 'upload.html')

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

def photos(request):
    """
    Creates album, photos, archive, and link
    """
    try:
        Album.objects.get(owner_id=request.user, title=request.POST.get('title', ''))
        return render(request, 'upload.html', {'message': 'You already have another album with this title. Please try again with another title.'})
    except Album.DoesNotExist:
        album = Album.objects.create(owner_id=request.user, title=request.POST.get('title', ''))
        for image in request.FILES.getlist('album'):
            Photo.objects.create(filename=image, albums=album)
        archive = Archive.objects.create(album_id=album)
        album.add_archive(archive)
        link = Link.objects.create(archive=archive)
        thumbnails = Photo.objects.filter(albums=album)
        # Serve up page with link ready to be copied and pasted
        return redirect('/gallery/{}/{}'.format(album.id, archive.id))

def download(request, id, uuid):
    """
    Renders a page with a zip file available for download
    """
    archive = Archive.objects.get(pk=id)
    filename = os.path.relpath(archive.filename, settings.MEDIA_ROOT)[9:]
    album = Album.objects.get(archive_id=archive)
    return render(request, 'download.html', {'archive_id': archive.id, 'filename': filename, 'album': album})

def download_zip(request):
    """
    Downloads the zip file served as a resource
    """
    # "Fake" route that just serves the file to the user
    file_path = Archive.objects.get(id=request.POST.get('archive_id')).filename
    with open(file_path, 'rb') as zipfile:
        response = HttpResponse(zipfile.read(), content_type='application/zip')
        response['Content-Disposition'] = 'inline; filename=' + file_path
    return response

@login_required
def albums(request):
    """
    Displays a list of albums associated with logged in user.
    """
    albums = Album.objects.filter(owner_id=request.user)
    return render(request, 'albums.html', {'albums': albums})

@login_required
def gallery(request, album_id, archive_id):
    """
    Displays a grid of pictures in a specific album
    """
    thumbnails = Photo.objects.filter(albums=album_id)
    link = Link.objects.get(archive_id=archive_id)
    album_title = Album.objects.get(pk=album_id).title
    return render(request, 'gallery.html', {'images': thumbnails, 'link': link, 'album_title': album_title})
