from django.db import models
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from datetime import date
from decimal import Decimal, ROUND_UP

from django.utils import timezone

from django.core.exceptions import ValidationError

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
    planowany_termin_zwrotu = models.DateTimeField(null=True, blank=True)

    cena_za_godzine = MoneyField(
        max_digits=10, 
        decimal_places=2, 
        default_currency='PLN',
        editable=False
        )

    class Meta:
        verbose_name = "Wypożyczenie"
        verbose_name_plural = "Wypożyczenia"

    def koszt_wynajmu(self):
        if not self.termin_zwrotu:
            return self.cena_za_godzine * Decimal('0.0')
        
        czas = self.termin_zwrotu - self.data_wypozyczenia
        godziny = Decimal(czas.total_seconds() / 3600).quantize(Decimal('0.01')) # Zamieniamy na godziny aby obliczyć cenę wynajmu rowera.
        return self.cena_za_godzine * godziny
    # Mała korekta zaokrąglenie do dwóch miejsc po przecinku ze względu na floating point.

    def oblicz_spoznienie(self): # Not Null Terminy 
        if self.termin_zwrotu and self.planowany_termin_zwrotu and self.termin_zwrotu > self.planowany_termin_zwrotu:
            roznica = self.termin_zwrotu - self.planowany_termin_zwrotu
            return Decimal(roznica.total_seconds() / 3600).quantize(Decimal('0.01')) 
        return Decimal('0.00')

    def kara_za_spoznienie(self):
        mnoznik_kary = Decimal('2.0') 
        kara_amount = (self.oblicz_spoznienie() * self.cena_za_godzine.amount * mnoznik_kary).quantize(Decimal('0.01'))
        return Money(kara_amount, self.cena_za_godzine.currency)

    def koszt_calkowity(self):
        wynajem_podstawowy = self.koszt_wynajmu() 
        total = wynajem_podstawowy + self.kara_za_spoznienie()
        total_amount = total.amount.quantize(Decimal('0.01'), rounding=ROUND_UP)
        return Money(total_amount, total.currency)
    
    def zakoncz_wypozyczenie(self):
        if not self.termin_zwrotu:
            self.termin_zwrotu = timezone.now()
            self.save()

        self.rower.status(True) # Odblokowanie roweru
        return self.koszt_calkowity()
    
    def clean(self):
        if not self.pk and self.rower and not self.rower.dostepnosc:
            raise ValidationError({'rower': "This bike is unavailable for rental."})

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.pk: 
            self.cena_za_godzine = self.rower.cena_za_godzine
            self.rower.status(False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"WY-{self.id:04d}"

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
    
    cena_za_godzine = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN')

    def status(self, dostepnosc: bool): # Zmiana statusu roweru
        self.dostepnosc = dostepnosc 
        self.save(update_fields=['dostepnosc'])

    class Meta:
        verbose_name = "Rower"
        verbose_name_plural = "Rowery"

    def __str__(self):
        return f"{self.marka} {self.get_typ_roweru_display()} ({self.nr_seryjny})"

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