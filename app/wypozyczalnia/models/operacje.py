from django.db import models
from djmoney.models.fields import MoneyField

class Transakcja(models.Model):
    #--- FK ---
    sklep = models.ForeignKey(
        'Sklep',
        on_delete=models.CASCADE, # Nie ma sklepu, nie ma transakcji.
        related_name='wszystkie_transakcje'
    )
    klient = models.ForeignKey(
        'Klient',
        on_delete=models.PROTECT,
        related_name='klient_transakcje'
    )
    pracownik = models.ForeignKey(
        'Pracownik',
        on_delete=models.PROTECT,
        related_name='zrealizowane_transakcje'
    )
    data_transakcji = models.DateTimeField(auto_now_add=True) #auto_now_add zapisuje czas transakcji tylko dla operacji INSERT.
    #--- Kaucje ---
    kaucja_pobrana = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='PLN',
        default=0
    )
    kaucja_zwrocona = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='PLN',
        default=0
    )
    class Meta:
        unique_together = ('id', 'sklep')
        verbose_name = "Transakcja"
        verbose_name_plural = "Transakcje"

    def __str__(self):
        return f"TR-{self.id:04d}"
    @property
    def utarg_sprzedaze(self):
        suma_akcesoria = sum(pozycja.utarg() for pozycja in self.sprzedaze.all()) # Całkowita suma pieniężna ze sprzedaży.
        return suma_akcesoria
    @property
    def utarg_wynajmy(self):
        return sum(w.koszt_wynajmu() for w in self.wynajmy.all())
    @property
    def utarg_calkowity(self):
        return self.utarg_sprzedaze + self.utarg_wynajmy

class Reklamacja(models.Model):
    transakcja = models.ForeignKey(
        'Transakcja',
        on_delete=models.CASCADE,
        related_name='reklamacje'
    )
    STATUSY ={
        "1": "Nowa",
        "2" : "W toku",
        "3": "Rozpatrzono",
        "4": "Odłożono"
    }

    DECYZJE ={
        "P": "Przyjęto",
        "N": "Nie przyjęto",
        "": "Oczekuje"
    }

    status = models.CharField(max_length=1, choices=STATUSY)
    data_zgloszenia = models.DateField(auto_now_add=True)
    decyzja = models.CharField(max_length=1, choices=DECYZJE, blank=True)
    opis_problemu = models.TextField(max_length=500, verbose_name="Opis usterki")

    class Meta:
        verbose_name = "Reklamacja"
        verbose_name_plural = "Reklamacje"

    def __str__(self):
        return f"RE-{self.id:04d} ({self.transakcja}) - {self.get_status_display()}"