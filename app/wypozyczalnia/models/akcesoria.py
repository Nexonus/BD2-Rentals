from django.db import models
from djmoney.models.fields import MoneyField
from decimal import Decimal
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

    nazwa = models.CharField(max_length=150)
    kategoria = models.CharField(max_length=2, choices=KATEGORIE)
    cena = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='PLN',
        max_digits=10,
    )
    rabat = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Rabat w procentach (0-100)'
    )
    kolor = models.CharField(max_length=2, choices=KOLORY, blank=True)

    class Meta:
        verbose_name = "Akcesoria"
        verbose_name_plural = "Akcesoria"

    def cena_po_rabacie(self):
        if self.rabat and self.rabat > 0:
            return self.cena * Decimal(100 - self.rabat) / Decimal('100') # Zapobiegamy konwersji na floata
        return self.cena

    def __str__(self):
        return f"{self.nazwa} ({self.get_kategoria_display()})" # Zwracamy podgląd dla kategorii a nie jego kodu. Metoda generowana przez Django.

