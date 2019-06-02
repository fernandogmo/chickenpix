from django.urls import path

from . import views

urlpatterns = [
        path('', TemplateView.as_view(template_name='home.html'), name='home'),
        path('accounts/', include('django.contrib.auth.urls')),
        path('', include('drfpasswordless.urls')),
        path('success/', views.email_auth_success, name='email_auth_success'),
        path('failure/', views.email_auth_failure, name='email_auth_failure'),
        path('photos/', views.photos, name='photos'),
]
