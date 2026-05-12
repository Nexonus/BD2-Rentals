from django.contrib import admin
from .models.sklep import Sklep
from .models.akcesoria import Akcesoria
from .models.transakcja import Transakcja
from .models.zakup_sprzetu import ZakupSprzetu
from .models.wypozyczenie import Wypozyczenie
from .models.rower import Rower
from .models.klient import Klient
from .models.pracownik import Pracownik

admin.site.register(Sklep)
admin.site.register(Akcesoria)
admin.site.register(Transakcja)
admin.site.register(ZakupSprzetu)
admin.site.register(Wypozyczenie)
admin.site.register(Rower)
admin.site.register(Klient)
admin.site.register(Pracownik)