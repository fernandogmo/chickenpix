from django.urls import path, include
from . import views

urlpatterns = [
        path('', views.home, name='home'),
        path('accounts/', include('django.contrib.auth.urls')),
        path('', include('drfpasswordless.urls')),
        path('success/', views.success, name='success'),
        # path('failure/', views.failure, name='failure'),
        path('photos/', views.photos, name='photos'),
]
