from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator

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
        return f"Transakcja nr {self.id} - Sklep: {self.sklep.miasto}"
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