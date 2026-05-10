from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from datetime import date
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator, MaxValueValidator

class Klient(models.Model):
    imie = models.CharField(max_length=30)
    nazwisko = models.CharField(max_length=40)
    kraj = CountryField(blank=True)
    telefon = PhoneNumberField(null=False, blank=False, unique=True)
    pesel = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='PESEL musi składać się z 11 cyfr'
            )
        ],
        help_text='11 cyfr'
    )

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"

    def get_fragment_peselu(self):
        if self.pesel:
            return f"***{self.pesel[-4:]}"
        return "BRAK"

