from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator

class SerwisRoweru(models.Model):
    rower = models.ForeignKey(
        'Rower', 
        on_delete=models.CASCADE, 
        related_name='serwisy'
    )
    data_rozpoczecia = models.DateField(default=date.today)
    data_zakonczenia = models.DateField(null=True, blank=True)
    opis_usterki = models.TextField()
    koszt_naprawy = MoneyField(
        max_digits=10, 
        decimal_places=2, 
        default_currency='PLN', 
        default=0
    )
    class Meta:
        verbose_name = "Serwis"
        verbose_name_plural = "Serwisy"

    def __str__(self):
        return f"Serwis {self.rower.nr_seryjny} - {self.data_rozpoczecia}"