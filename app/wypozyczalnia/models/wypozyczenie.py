from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from datetime import date
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

class Wypozyczenie(models.Model):
    transakcja = models.ForeignKey(
        'Transakcja',
        on_delete=models.CASCADE,
        related_name='wynajmy'
    )

    rower = models.ForeignKey(
        'Rower',
        on_delete=models.CASCADE,
        related_name='historia_wynajmow'
    )
    data_wypozyczenia = models.DateTimeField(auto_now_add=True)
    termin_zwrotu = models.DateTimeField(null=True, blank=True)
    cena_za_godzine = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN')

    class Meta:
        verbose_name = "Wypożyczenie"
        verbose_name_plural = "Wypożyczenia"

    def save(self, *args, **kwargs):
        if not self.cena_za_godzine:
            self.cena_za_godzine = self.rower.stawka_godzinowa # UPDATE, jeśli jest null to bierzemy stawkę z rowera.
        super().save(*args, **kwargs)

    def koszt_wynajmu(self):
        if not self.termin_zwrotu:
            return Decimal('0.00')
        
        czas = self.termin_zwrotu - self.data_wypozyczenia
        godziny = Decimal(czas.total_seconds() / 3600) # Zamieniamy na godziny aby obliczyć cenę wynajmu rowera.
        return self.cena_za_godzine * godziny
