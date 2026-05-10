from django.contrib import admin
from .models import Klient, Pracownik, Akcesoria, Reklamacja

admin.site.register(Klient)
admin.site.register(Pracownik)
admin.site.register(Akcesoria)
admin.site.register(Reklamacja)