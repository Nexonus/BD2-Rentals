from django.urls import path, include
from . import views

# Namespace for the app
app_name = 'wypozyczalnia'

urlpatterns = [
    path('', views.strona_glowna, name='strona_glowna'),
    path('accounts/register', views.rejestracja, name='rejestracja'),
    path('accounts/', include('django.contrib.auth.urls')),
]