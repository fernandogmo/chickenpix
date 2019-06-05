from django.urls import path, include
from . import views

urlpatterns = [
        path('', views.home, name='home'),
        path('accounts/', include('django.contrib.auth.urls')),
        path('', include('drfpasswordless.urls')),
        path('validate/', views.validate, name='validate'),
        path('photos/', views.photos, name='photos'),
        path('upload/', views.upload, name='upload'),
]
