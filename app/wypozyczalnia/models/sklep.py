from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator

class Sklep(models.Model):
    miasto = models.CharField(max_length=150)
    adres = models.CharField(max_length=150)
    
    kod_pocztowy = models.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{2}-\d{3}$', 'Kod pocztowy musi być w formacie: 00-000')] # Walidator dla kodu pocztowego.
    )

    class Meta:
        verbose_name = "Sklep"
        verbose_name_plural = "Sklepy"

    def __str__(self):
        return f"Sklep {self.miasto} - {self.adres}"