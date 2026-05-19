from django.contrib import admin
from .models.osoby import Pracownik, Klient
from .models.operacje import Transakcja, Reklamacja
from .models.sprzedaze import Sklep, Akcesoria, ZakupSprzetu
from .models.wypozyczenia import Wypozyczenie, Rower, SerwisRoweru
# Zmiana podziału na pliki, aby łatwiej zaimportować je do projektu.

# py manage.py makemigrations [Po zmianie w bazie!]
# py manage.py migrate

# py manage.py createsuperuser
# py manage.py runserver 

admin.site.site_header = "BD2 Rentals Management"
admin.site.site_title = "BD2 Rentals Admin"

@admin.register(ZakupSprzetu)
class ZakupSprzetuAdmin(admin.ModelAdmin):
    readonly_fields = ('wyswietl_cene',)
    fields = ('transakcja', 'akcesoria', 'ilosc', 'wyswietl_cene')

    def wyswietl_cene(self, obj):
        if obj.pk:
            return obj.cena_sprzedazy
        return "Zostanie wyliczona automatycznie"
    
    wyswietl_cene.short_description = "Cena sprzedaży"

@admin.register(Wypozyczenie)
class WypozyczenieAdmin(admin.ModelAdmin):
    readonly_fields = ('cena_za_godzine', 'pokaz_podsumowanie')
    
    fieldsets = (
        ('Dane wypożyczenia', {
            'fields': ('transakcja', 'rower', 'planowany_termin_zwrotu', 'termin_zwrotu')
        }),
        ('Rozliczenie', {
            'fields': ('cena_za_godzine', 'pokaz_podsumowanie'),
        }),
    )

    def pokaz_podsumowanie(self, obj):
        if not obj.termin_zwrotu:
            return "Rower jest wypożyczony"
            
        return (
            f"Koszt podstawowy: {obj.koszt_wynajmu()} PLN | "
            f"KARA: {obj.kara_za_spoznienie()} PLN | "
            f"ŁĄCZNIE: {obj.koszt_calkowity()} PLN"
        )
    
    pokaz_podsumowanie.short_description = "Podsumowanie finansowe"

@admin.register(Rower)
class RowerAdmin(admin.ModelAdmin):
    list_display = ('nr_seryjny', 'marka', 'typ_roweru', 'cena_za_godzine', 'dostepnosc')
    search_fields = ('nr_seryjny', 'marka')
    list_filter = ('typ_roweru', 'dostepnosc')
    list_editable = ('dostepnosc',) # Admin can quickly change availability directly from the list

@admin.register(SerwisRoweru)
class SerwisRoweruAdmin(admin.ModelAdmin):
    list_display = ('rower', 'data_rozpoczecia', 'data_zakonczenia', 'koszt_naprawy')
    list_filter = ('data_rozpoczecia', 'data_zakonczenia')
    search_fields = ('opis_usterki',)

@admin.register(Klient)
class KlientAdmin(admin.ModelAdmin):
    # Shows their basic contact info directly in the table
    list_display = ('id', 'imie', 'nazwisko', 'telefon', 'pesel')
    # Allows staff to instantly search for a customer by last name, phone, or PESEL
    search_fields = ('nazwisko', 'telefon', 'pesel')
    list_filter = ('kraj',)

@admin.register(Pracownik)
class PracownikAdmin(admin.ModelAdmin):
    list_display = ('id', 'imie', 'nazwisko', 'stanowisko', 'data_zatrudnienia')
    search_fields = ('nazwisko', 'stanowisko')
    # Easily filter to see only Mechanics or only Cashiers
    list_filter = ('stanowisko',)

@admin.register(Akcesoria)
class AkcesoriaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'kategoria', 'cena', 'rabat', 'kolor')
    search_fields = ('nazwa', 'kategoria')
    list_filter = ('kategoria', 'kolor')
    # Allows the admin to quickly change the discount (rabat) without opening the item
    list_editable = ('rabat',)

@admin.register(Sklep)
class SklepAdmin(admin.ModelAdmin):
    list_display = ('id', 'miasto', 'adres', 'kod_pocztowy')
    search_fields = ('miasto', 'adres')

admin.site.register(Transakcja)
admin.site.register(Reklamacja)