from django.urls import path, include
from . import views

urlpatterns = [
        path('', views.home, name='home'),
        path('accounts/', include('django.contrib.auth.urls')),
        path('', include('drfpasswordless.urls')),
        path('success/', views.email_auth_success, name='email_auth_success'),
        path('failure/', views.email_auth_failure, name='email_auth_failure'),
        path('photos/', views.photos, name='photos'),
]
