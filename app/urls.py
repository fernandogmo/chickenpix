from django.urls import path, include
# from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
        path('', views.home, name='home'),
        path('accounts/', include('django.contrib.auth.urls')),
        path('', include('drfpasswordless.urls')),
        path('validate/', views.validate, name='validate'),
        path('photos/', views.photos, name='photos'),
        path('upload/', views.upload, name='upload'),
        # Link for people to go to to click a button to download zip file
        path('download/<int:id>/<uuid:uuid>/', views.download, name='download'),
        # "Hidden" view that doesn't send user to any HTML page - just serves the zip file for download
        path('download/', views.download_zip, name='download_zip'),
        # path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),
        path('albums/', views.albums, name='albums'),
        path('gallery/<int:album_id>/<int:archive_id>', views.gallery, name='gallery'),
        path('photo/<int:photo_id>', views.photo, name='photo'),
        path('tag_users/', views.tag_users, name='tag_users'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
