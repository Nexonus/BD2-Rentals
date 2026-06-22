from django import forms
from .models.osoby import Klient
from .models.operacje import Reklamacja
from django_countries.widgets import CountrySelectWidget

class KlientForm(forms.ModelForm):
    class Meta:
        model = Klient
        fields = ['imie', 'nazwisko', 'kraj', 'telefon', 'pesel']
        widgets = {
            'imie': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary'}),
            'nazwisko': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary'}),
            'kraj': CountrySelectWidget(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': '+48123456789'}),
            'pesel': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': '11 cyfr'}),
        }
        labels = {
            'imie': 'Imię',
            'nazwisko': 'Nazwisko',
            'kraj': 'Kraj',
            'telefon': 'Numer telefonu',
            'pesel': 'PESEL',
        }

class ReklamacjaForm(forms.ModelForm):
    class Meta:
        model = Reklamacja
        fields = ['opis_problemu']
        widgets = {
            'opis_problemu': forms.Textarea(attrs={'class': 'form-control bg-dark text-light border-secondary', 'rows': 4, 'placeholder': 'Opisz problem z transakcją lub produktem...'}),
        }
        labels = {
            'opis_problemu': 'Opis usterki / problemu',
        }
