from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator


class Akcesoria(models.Model):
    KATEGORIE = [
        ("LA", "Lampki"),
        ("KA", "Kaski"),
        ("UC", "Uchwyty"),
        ("LI", "Liczniki"),
        ("IN", "Inne"),
    ]

    KOLORY = [
        ("1", "Zielony"),
        ("2", "Niebieski"),
        ("3", "Różowy"),
        ("4", "Czerwony"),
        ("5", "Biały"),
        ("6", "Czarny"),
        ("7", "Żółty"),
        ("8", "Fioletowy"),
        ("9", "Inny"),
    ]

    nazwa = models.CharField(max_length=30)
    kategoria = models.CharField(max_length=2, choices=KATEGORIE)
    cena = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='PLN',
        max_digits=6,
    )
    rabat = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Rabat w procentach (0-100)'
    )
    kolor = models.CharField(max_length=1, choices=KOLORY, blank=True)

    def cena_po_rabacie(self):
        if self.rabat:
            return self.cena * (100 - self.rabat) / 100
        return self.cena

    def __str__(self):
        return f"{self.nazwa} - {self.cena} PLN"
