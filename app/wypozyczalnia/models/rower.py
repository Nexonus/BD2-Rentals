from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator

class Rower(models.Model):
    MODEL_CHOICES = [
        ('MTB', 'Górski'), 
        ('ROAD', 'Szosowy'), 
        ('CITY', 'Miejski')
        ]
    
    nr_seryjny = models.CharField(max_length=50, unique=True)
    typ_roweru = models.CharField(max_length=4, choices=MODEL_CHOICES)
    marka = models.CharField(max_length=50)
    kolor = models.CharField(max_length=30)
    kraj = models.CharField(max_length=100)
    dostepnosc = models.BooleanField(default=True)
    
    stawka_godzinowa = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN')

    class Meta:
        verbose_name = "Rower"
        verbose_name_plural = "Rowery"

    def __str__(self):
        return f"{self.marka} {self.get_typ_roweru_display()} ({self.nr_seryjny})"