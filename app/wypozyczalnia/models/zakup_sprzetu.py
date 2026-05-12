from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator

class ZakupSprzetu(models.Model):
    transakcja = models.ForeignKey(
        'Transakcja',
        on_delete=models.CASCADE, # Jeżeli nie było transakcji (usunięto) to nie było również i zakupu.
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
        default_currency='PLN'
    )
    class Meta:
        unique_together = ('transakcja', 'akcesoria') # unique_together dla pól.
        verbose_name = "Zakup"
        verbose_name_plural = "Zakupy"

    def save(self, *args, **kwargs):
        if not self.cena_sprzedazy or self.cena_sprzedazy.amount == 0:
            self.cena_sprzedazy = self.FK_Akcesoria.cena_po_rabacie()
        super().save(*args, **kwargs)

    def utarg(self): # Ilosc sprzedanych rzeczy x po jakiej cenie.
        return self.cena_sprzedazy * self.ilosc
        
