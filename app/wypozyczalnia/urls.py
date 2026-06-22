from django.urls import path, include
from . import views

# Namespace for the app
app_name = 'wypozyczalnia'

urlpatterns = [
    path('', views.strona_glowna, name='strona_glowna'),
    path('koszyk/', views.koszyk_widok, name='koszyk'),
    path('koszyk/dodaj/<str:typ_produktu>/<int:produkt_id>/', views.dodaj_do_koszyka, name='dodaj_do_koszyka'),
    path('koszyk/usun/<int:pozycja_id>/', views.usun_z_koszyka, name='usun_z_koszyka'),
    path('kasa/', views.kasa, name='kasa'),
    path('zamowienia/', views.moje_zamowienia, name='zamowienia'),
    path('zamowienia/zwroc/<int:wynajem_id>/', views.zwroc_rower, name='zwroc_rower'),
    path('profil/', views.profil, name='profil'),
    path('reklamacje/', views.moje_reklamacje, name='reklamacje'),
    path('reklamacje/dodaj/<int:transakcja_id>/', views.dodaj_reklamacje, name='dodaj_reklamacje'),
    path('o-nas/', views.o_nas, name='o_nas'),
]