from django.db import models
from django.core.validators import RegexValidator
from decimal import Decimal 
from djmoney.models.fields import MoneyField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import transaction
from django.core.exceptions import ValidationError

class Sklep(models.Model):
    # Zakładamy odgórnie, że nazwa sklepu jest znana - to jedna sieć.
    MIASTA = [
        ('Waw', 'Warszawa'),
        ('Cze', 'Częstochowa'),
        ('Poz', 'Poznań'),
        ('Lub', 'Lublin'),
        ('Gda', 'Gdańsk'),
        ('Kra', 'Kraków'),
        ('Kat', 'Katowice'),
        ('Sie', 'Siedlce'),
        ('Słu', 'Słupsk'),
        ('Tor', 'Toruń'),
        ('Byd', 'Bydgoszcz'),
        ('Elb', 'Elbląg'),
    ]

    miasto = models.CharField(max_length=150, null=False, choices=MIASTA)
    adres = models.CharField(max_length=150)
    kod_pocztowy = models.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{2}-\d{3}$', 'Kod pocztowy musi być w formacie: 00-000')] # Walidator dla kodu pocztowego.
    )

    class Meta:
        verbose_name = "Sklep"
        verbose_name_plural = "Sklepy"

    def __str__(self):
        return f"{self.adres} ({self.get_miasto_display()})"

class ZakupSprzetu(models.Model):
    transakcja = models.ForeignKey(
        'Transakcja', 
        on_delete=models.CASCADE,
        related_name='sprzedaze'
    )
    akcesoria = models.ForeignKey(
        'Akcesoria',
        on_delete=models.PROTECT # Zapobiegamy usunięciu historii sprzedaży przy próbie usunięcia produktu.
    )
    ilosc = models.PositiveIntegerField( # Ilość to po prostu ile sztuk danego produktu sprzedano w jednej operacji.
        default=1,
        validators=[MinValueValidator(1)]
    )
    cena_sprzedazy = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='PLN',
        editable=False
    )
    class Meta:
        verbose_name = "Sprzedaż"
        verbose_name_plural = "Sprzedaże"

    # def save(self, *args, **kwargs):
    #     self.cena_sprzedazy = self.akcesoria.cena_po_rabacie() * self.ilosc
    #     super().save(*args, **kwargs)
    def save(self, *args, **kwargs):
        if not self.pk:
            with transaction.atomic():
                try:
                    stan = StanMagazynowyAkcesoriow.objects.select_for_update().get(
                        sklep=self.transakcja.sklep,
                        akcesorium=self.akcesoria
                    )
                except StanMagazynowyAkcesoriow.DoesNotExist:
                    raise ValidationError(f"Produkt {self.akcesoria.nazwa} nie jest dostępny w sklepie {self.transakcja.sklep}.")

                if stan.ilosc < self.ilosc:
                    raise ValidationError(f"Brak wystarczającej ilości towaru. Dostępne: {stan.ilosc}")
                
                stan.ilosc -= self.ilosc
                stan.save()

        self.cena_sprzedazy = self.akcesoria.cena_po_rabacie() * self.ilosc
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"SP-{self.id:04d}"
    
# Tutaj proponuję przyjąć np. taką kategoryzację:
        # A1 - AN (Sprzęt stricte pod kątem roweru)
        # B1 - BN (Sprzęt ochronny, kaski itd)
        # C1 - CN (Narzędzia, gadżety)
class Akcesoria(models.Model):
    KATEGORIE = [
        ("A1", "Oświetlenie"),
        ("A2", "Błotniki"),
        ("A3", "Hamulce"),
        ("A4", "Dzwonki"),
        ("A5", "Uchwyty"),
        ("A6", "Siodełka"),
        ("A7", "Opony"),
        ("A8", "Bagażniki"),
        ("A9", "Przyczepki"),
        ("A10", "Lusterka"),    # Konieczność rozwinięcia maksymalnej dopuszczalnej liczby znaków tutaj.

        ("B1", "Kaski"),
        ("B2", "Zapięcia"),
        ("B3", "Kamizelki"),
        ("B4", "Ochraniacze"),

        ("C1", "Pompki"),
        ("C2", "Dętki"),
        ("C3", "Liczniki"),
        ("C4", "Koszyki")
    ]

    nazwa = models.CharField(max_length=200)
    kategoria = models.CharField(max_length=3, choices=KATEGORIE)
    cena = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='PLN',
        max_digits=10,
        help_text='Cena jednostkowa produktu.'
    )
    rabat = models.PositiveIntegerField( # Rabat liczymy tylko w dodatnich %.
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Rabat w procentach (0-100%)'
    )
    kolor = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Akcesoria"
        verbose_name_plural = "Akcesoria"

    def cena_po_rabacie(self):
        if self.rabat and self.rabat > 0:
            return self.cena * Decimal(100 - self.rabat) / Decimal('100') # Zapobiegamy konwersji na floata
        return self.cena

    def __str__(self):
        return f"{self.nazwa} ({self.get_kategoria_display()})" # Zwracamy podgląd dla kategorii a nie jego kodu. Metoda generowana przez Django.

class StanMagazynowyAkcesoriow(models.Model):
    sklep = models.ForeignKey('Sklep', on_delete=models.CASCADE, related_name='stany_magazynowe')
    akcesorium = models.ForeignKey('Akcesoria', on_delete=models.CASCADE, related_name='stany_magazynowe')
    ilosc = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('sklep', 'akcesorium') 
        verbose_name = "Stan magazynowy"
        verbose_name_plural = "Stany magazynowe"

    def __str__(self):
        return f"{self.akcesorium.nazwa} - {self.sklep.miasto}: {self.ilosc} szt."