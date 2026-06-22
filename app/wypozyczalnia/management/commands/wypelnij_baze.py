from django.core.management.base import BaseCommand
from wypozyczalnia.models.osoby import Klient, Pracownik
from wypozyczalnia.models.sprzedaze import Sklep, Akcesoria, ZakupSprzetu, StanMagazynowyAkcesoriow
from wypozyczalnia.models.wypozyczenia import Rower, Wypozyczenie
from wypozyczalnia.models.operacje import Transakcja, Koszyk, PozycjaKoszyka
from datetime import date, timedelta
from django.utils import timezone
from decimal import Decimal

class Command(BaseCommand):
    help = 'Wypełnia bazę danych przykładowymi danymi wypożyczalni'

    def handle(self, *args, **kwargs):
        self.stdout.write("Czyszczenie bazy danych...")
        # Kasujemy w odpowiedniej kolejności (najpierw zależne)
        PozycjaKoszyka.objects.all().delete()
        Koszyk.objects.all().delete()
        Wypozyczenie.objects.all().delete()
        ZakupSprzetu.objects.all().delete()
        StanMagazynowyAkcesoriow.objects.all().delete()
        Transakcja.objects.all().delete()
        Klient.objects.all().delete()
        Pracownik.objects.all().delete()
        Rower.objects.all().delete()
        Sklep.objects.all().delete()
        Akcesoria.objects.all().delete()

        self.stdout.write("Dodawanie sklepów...")
        sklep1 = Sklep.objects.create(miasto='Waw', adres='ul. Prosta 12', kod_pocztowy='00-012')
        sklep2 = Sklep.objects.create(miasto='Kra', adres='ul. Krzywa 34', kod_pocztowy='30-034')

        self.stdout.write("Dodawanie pracowników...")
        prac1 = Pracownik.objects.create(imie='Jan', nazwisko='Kowalski', stanowisko='KI', telefon='+48111222333', data_zatrudnienia=date(2022, 1, 10))
        prac2 = Pracownik.objects.create(imie='Anna', nazwisko='Nowak', stanowisko='SP', telefon='+48222333444', data_zatrudnienia=date(2023, 5, 20))
        prac3 = Pracownik.objects.create(imie='Piotr', nazwisko='Zieliński', stanowisko='SE', telefon='+48333444555', data_zatrudnienia=date(2023, 6, 1))

        self.stdout.write("Dodawanie klientów...")
        klient1 = Klient.objects.create(imie='Adam', nazwisko='Mickiewicz', kraj='PL', telefon='+48555666777', pesel='90010112345')
        klient2 = Klient.objects.create(imie='Juliusz', nazwisko='Słowacki', kraj='PL', telefon='+48666777888', pesel='92020223456')

        self.stdout.write("Dodawanie akcesoriów...")
        kask1 = Akcesoria.objects.create(nazwa='Kask L', kategoria='B1', cena=Decimal('120.00'), kolor='Czarny')
        kask2 = Akcesoria.objects.create(nazwa='Kask M', kategoria='B1', cena=Decimal('120.00'), kolor='Biały')
        zapiecie = Akcesoria.objects.create(nazwa='Zapięcie U-Lock', kategoria='B2', cena=Decimal('85.50'))
        lampki = Akcesoria.objects.create(nazwa='Zestaw lampek LED', kategoria='A1', cena=Decimal('45.00'))

        self.stdout.write("Dodawanie stanów magazynowych...")
        for akcesorium in [kask1, kask2, zapiecie, lampki]:
            StanMagazynowyAkcesoriow.objects.create(sklep=sklep1, akcesorium=akcesorium, ilosc=20)
            StanMagazynowyAkcesoriow.objects.create(sklep=sklep2, akcesorium=akcesorium, ilosc=20)

        self.stdout.write("Dodawanie rowerów...")
        rower1 = Rower.objects.create(nr_seryjny='R-MTB-001', typ_roweru='MTB', marka='Trek', kolor='Czarny', kraj='USA', dostepnosc=True, cena_za_godzine=Decimal('15.00'), sklep=sklep1)
        rower2 = Rower.objects.create(nr_seryjny='R-CITY-001', typ_roweru='CITY', marka='Romet', kolor='Niebieski', kraj='Polska', dostepnosc=True, cena_za_godzine=Decimal('12.00'), sklep=sklep1)
        rower3 = Rower.objects.create(nr_seryjny='R-ROAD-001', typ_roweru='ROAD', marka='Giant', kolor='Czerwony', kraj='Tajwan', dostepnosc=True, cena_za_godzine=Decimal('20.00'), sklep=sklep2)
        rower4 = Rower.objects.create(nr_seryjny='R-MTB-002', typ_roweru='MTB', marka='Merida', kolor='Zielony', kraj='Tajwan', dostepnosc=True, cena_za_godzine=Decimal('18.00'), sklep=sklep2)
        rower5 = Rower.objects.create(nr_seryjny='R-CITY-002', typ_roweru='CITY', marka='Kross', kolor='Biały', kraj='Polska', dostepnosc=True, cena_za_godzine=Decimal('10.00'), sklep=sklep2)

        self.stdout.write("Dodawanie przykładowych transakcji...")
        # Transakcja 1: Wypożyczenie MTB + kask
        t1 = Transakcja.objects.create(
            sklep=sklep1, 
            klient=klient1, 
            pracownik=prac2, 
            kaucja_pobrana=Decimal('100.00')
        )
        Wypozyczenie.objects.create(
            transakcja=t1,
            rower=rower1,
            planowany_termin_zwrotu=timezone.now() + timedelta(hours=3)
        )
        rower1.dostepnosc = False
        rower1.save()

        ZakupSprzetu.objects.create(
            transakcja=t1,
            akcesoria=kask1,
            ilosc=1
        )

        # Transakcja 2: Wypożyczenie CITY na 1h
        t2 = Transakcja.objects.create(
            sklep=sklep1, 
            klient=klient2, 
            pracownik=prac2, 
            kaucja_pobrana=Decimal('50.00')
        )
        Wypozyczenie.objects.create(
            transakcja=t2,
            rower=rower2,
            planowany_termin_zwrotu=timezone.now() + timedelta(hours=1)
        )
        rower2.dostepnosc = False
        rower2.save()
        
        # Transakcja 3: Tylko zakup akcesoriów (bez wypożyczenia)
        t3 = Transakcja.objects.create(
            sklep=sklep2, 
            klient=klient1, 
            pracownik=prac1, 
            kaucja_pobrana=Decimal('0.00')
        )
        ZakupSprzetu.objects.create(
            transakcja=t3,
            akcesoria=lampki,
            ilosc=2
        )

        self.stdout.write(self.style.SUCCESS("Baza danych została pomyślnie zasilona przykładowymi danymi!"))
