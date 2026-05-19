from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from datetime import date
from django_countries.fields import CountryField

class Klient(models.Model):
    imie = models.CharField(max_length=100)
    nazwisko = models.CharField(max_length=100)
    kraj = CountryField(blank=True)
    telefon = PhoneNumberField(
        null=False, 
        blank=False, 
        unique=True, 
        max_length=12)
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

    class Meta:
        verbose_name = "Klient"
        verbose_name_plural = "Klienci"
    
    def get_full_name(self):
        if self.imie and self.nazwisko:
            return self.imie + " " + self.nazwisko

    def get_fragment_peselu(self):
        if self.pesel:
            return f"***{self.pesel[-4:]}"
        return "Brak"

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"
    
class Pracownik(models.Model):
    STANOWISKA = [
        ("SP", "Sprzedawca"),
        ("KI", "Kierownik"),
        ("SE", "Serwisant"),
    ]
    
    imie = models.CharField(max_length=50)
    nazwisko = models.CharField(max_length=50)
    stanowisko = models.CharField(max_length=2, choices=STANOWISKA)
    telefon = PhoneNumberField(null=True, blank=True, unique=True, default=None)
    data_zatrudnienia = models.DateField(null=False, default=date.today)

    def get_full_name(self):
        if self.imie and self.nazwisko:
            return self.imie + " " + self.nazwisko
        
    class Meta:
        verbose_name = "Pracownik"
        verbose_name_plural = "Pracownicy"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_stanowisko_display()})"


