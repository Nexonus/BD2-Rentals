from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator

class Reklamacja(models.Model):
    STATUSY ={
        "1": "Nowa",
        "2" : "W toku",
        "3": "Rozpatrzono"
    }

    DECYZJE ={
        "P": "Przyjęto",
        "N": "Nie przyjęto"
    }

    status = models.CharField(max_length=1, choices=STATUSY)
    data_zgloszenia = models.DateField(auto_now=True)
    decyzja = models.CharField(max_length=1, choices=DECYZJE, blank=True)
    opis_problemu = models.CharField(max_length=1000)

    def __str__(self):
        return f"Reklamacja {self.id} - {self.transakcja} - {self.status}"