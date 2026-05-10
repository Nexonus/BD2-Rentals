from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator

class Pracownik(models.Model):
    STANOWISKA = [
        ("SP", "Sprzedawca"),
        ("KI", "Kierownik"),
        ("SE", "Serwisant"),
    ]
    imie = models.CharField(max_length=30)
    nazwisko = models.CharField(max_length=40)
    stanowisko = models.CharField(max_length=2, choices=STANOWISKA)
    telefon = PhoneNumberField(null=True, blank=True, unique=True, default=None)
    data_zatrudnienia = models.DateField(null=False, default=date.today)

    def __str__(self):
        return f"{self.stanowisko} {self.imie} {self.nazwisko}"


