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

admin.site.register(Sklep)
admin.site.register(Akcesoria)
admin.site.register(Transakcja)
admin.site.register(Klient)
admin.site.register(Pracownik)
admin.site.register(Reklamacja)