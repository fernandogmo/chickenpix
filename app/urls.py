from django.urls import path, include
# from django.views.generic.base import RedirectView
# from django.conf import settings
from . import views

urlpatterns = [
        path('', views.home, name='home'),
        path('accounts/', include('django.contrib.auth.urls')),
        path('', include('drfpasswordless.urls')),
        path('validate/', views.validate, name='validate'),
        path('photos/', views.photos, name='photos'),
        path('upload/', views.upload, name='upload'),
        # path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),
]
