from django.test import TestCase
from wypozyczalnia.models.osoby import Klient, Pracownik
from wypozyczalnia.models.sprzedaze import Sklep
from wypozyczalnia.models.operacje import Transakcja, Reklamacja, Koszyk, PozycjaKoszyka
from wypozyczalnia.models.sprzedaze import ZakupSprzetu, Akcesoria, StanMagazynowyAkcesoriow
from wypozyczalnia.models.wypozyczenia import Wypozyczenie, Rower
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth import get_user_model

from django.db.models import ProtectedError
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class DB_Tests(TestCase):
    @classmethod
    def setUp(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="testuser")
        cls.sklep = Sklep.objects.create(miasto="Warszawa")
        cls.klient = Klient.objects.create(imie="Jan",nazwisko="Testowy")
        cls.pracownik = Pracownik.objects.create(imie="Adam", nazwisko="Nowak")

    def test_StworzTransakcje(self):
        t = Transakcja.objects.create(
            sklep=self.sklep, 
            klient=self.klient, 
            pracownik=self.pracownik
        )
        self.assertEqual(Transakcja.objects.count(), 1)
        self.assertEqual(str(t), f"TR-{t.id:04d}")
    
    def test_ZwrotKosztWynajmu(self):
        t = Transakcja.objects.create(sklep=self.sklep, klient=self.klient, pracownik=self.pracownik)
        
        akcesoria = Akcesoria.objects.create(nazwa="Kask", cena=50, rabat=0)
        StanMagazynowyAkcesoriow.objects.create(sklep=self.sklep, akcesorium=akcesoria, ilosc=10) # Dodaj to!
        ZakupSprzetu.objects.create(transakcja=t, akcesoria=akcesoria, ilosc=1)
            
        rower = Rower.objects.create(marka="Rower Testowy", cena_za_godzine=30, sklep=self.sklep)

        czas_wypozyczenia = timezone.now()
        czas_zwrotu = czas_wypozyczenia + timedelta(hours=1) 

        Wypozyczenie.objects.create(    
            transakcja=t, 
            rower=rower, 
            data_wypozyczenia=czas_wypozyczenia,
            termin_zwrotu=czas_zwrotu
        )
        self.assertEqual(t.utarg_sprzedaze.amount, 50)
        self.assertEqual(t.utarg_wynajmy.amount, 30)
        self.assertEqual(t.utarg_calkowity.amount, 80) # Koszt wynajmu uwzględnia czasowy koszt + koszt zakupu akcesoriów.
    
    def test_KosztWynajmu(self):
        rower = Rower.objects.create(marka="Rower Testowy", cena_za_godzine=30, sklep=self.sklep)
        t = Transakcja.objects.create(sklep=self.sklep, klient=self.klient, pracownik=self.pracownik)
        wypozyczenie = Wypozyczenie.objects.create(transakcja=t, rower=rower, data_wypozyczenia=timezone.now())
    
        self.assertEqual(wypozyczenie.koszt_wynajmu().amount, 0) # Koszt zwrotu jest zerowy, jeśli rower nie został zwrócony.

    def test_UsunPracownika(self): # Sprawdzamy, czy zwrócony zostanie błąd że nie możemy usunąć pracownika od tak.
        t = Transakcja.objects.create(sklep=self.sklep, klient=self.klient, pracownik=self.pracownik)
        with self.assertRaises(ProtectedError):
            self.pracownik.delete()
    
    def test_Reklamacja(self):
        t = Transakcja.objects.create(sklep=self.sklep, klient=self.klient, pracownik=self.pracownik)
        r = Reklamacja.objects.create(transakcja=t, status="1", opis_problemu="Usterka testowa")
        self.assertEqual(r.get_status_display(), "Nowa")
        self.assertEqual(t.reklamacje.count(), 1) # Czy reklamacja sie dodala?

    def test_Rabat(self):
        akcesoria = Akcesoria.objects.create(nazwa="Kask", cena=100, rabat=20) # Nakładamy 20% rabat.
        self.assertEqual(akcesoria.cena_po_rabacie().amount, 80) # Uwaga do formatu MONEY wymagany jest .amount inaczej porównujemy zły typ danych

    def test_Koszyk(self):
        koszyk = Koszyk.objects.create(uzytkownik=self.user)
        przedmiot = Akcesoria.objects.create(nazwa="Kask", cena=100)
        pozycja = PozycjaKoszyka.objects.create(
            koszyk=koszyk, 
            produkt=przedmiot, 
            ilosc=2
        )
    
        self.assertEqual(pozycja.produkt, przedmiot)
        self.assertEqual(pozycja.koszt_calkowity.amount, 200) # Sprawdzamy, czy dwa kaski w koszyku kosztują tyle ile powinny czyli 200 zł.

    def test_Unique(self):
        t1 = Transakcja.objects.create(id=13, sklep=self.sklep, klient=self.klient, pracownik=self.pracownik)
        with self.assertRaises(IntegrityError):
            Transakcja.objects.create(id=13, sklep=self.sklep, klient=self.klient, pracownik=self.pracownik)
            # Sprawdzamy, czy da się dwie takie same transakcje zrobić. Jak nie to mamy Assert IntegrityError.

    def test_WypozyczenieNiedostepnego(self):
        rower = Rower.objects.create(marka="Rower Niedostepny", cena_za_godzine=30, dostepnosc=False, sklep=self.sklep)
        t = Transakcja.objects.create(sklep=self.sklep, klient=self.klient, pracownik=self.pracownik)
        
        wypozyczenie = Wypozyczenie(transakcja=t, rower=rower)
        with self.assertRaises(ValidationError):
            wypozyczenie.full_clean()
    
    def test_ZmianaStatusuWypozyczenia(self):
        rower = Rower.objects.create(
            nr_seryjny="SN-007", marka="Test", typ_roweru="MTB", 
            kolor="Czarny", kraj="Polska", cena_za_godzine=30, 
            dostepnosc=True,
            sklep=self.sklep
        )
        t = Transakcja.objects.create(sklep=self.sklep, klient=self.klient, pracownik=self.pracownik)
        Wypozyczenie.objects.create(transakcja=t, rower=rower)
        
        rower.refresh_from_db()
        self.assertFalse(rower.dostepnosc, "Bike should become unavailable after rental.")

    def test_ZmianaStatusuPoZwrocie(self):
        rower = Rower.objects.create(
            nr_seryjny="SN-008", marka="Test", typ_roweru="MTB", 
            kolor="Biały", kraj="Polska", cena_za_godzine=30, 
            dostepnosc=True,
            sklep=self.sklep
        )
        t = Transakcja.objects.create(sklep=self.sklep, klient=self.klient, pracownik=self.pracownik)
        wypozyczenie = Wypozyczenie.objects.create(transakcja=t, rower=rower)

        wypozyczenie.termin_zwrotu = wypozyczenie.data_wypozyczenia + timedelta(hours=2)
        rachunek = wypozyczenie.zakoncz_wypozyczenie() # Termin zwrotu na teraz, oddajemy go i placimy za wypozyczenie.
        
        rower.refresh_from_db()
        self.assertTrue(rower.dostepnosc, "Bike should become available after rental.")
        self.assertEqual(rachunek.amount, 60)
        self.assertEqual(str(rachunek.currency), 'PLN')
    
    def test_koszt_zakonczenia_z_kara(self):
        rower = Rower.objects.create(
            nr_seryjny="SN-009", marka="Test", typ_roweru="MTB", 
            kolor="Biały", kraj="Polska", cena_za_godzine=30, 
            dostepnosc=True,
            sklep=self.sklep
        )
        t = Transakcja.objects.create(sklep=self.sklep, klient=self.klient, pracownik=self.pracownik)
        wypozyczenie = Wypozyczenie.objects.create(transakcja=t, rower=rower)
        
        # Termin zwrotu 2h po czasie
        wypozyczenie.planowany_termin_zwrotu = wypozyczenie.data_wypozyczenia + timedelta(hours=1)
        wypozyczenie.termin_zwrotu = wypozyczenie.data_wypozyczenia + timedelta(hours=3)
        
        rachunek = wypozyczenie.zakoncz_wypozyczenie()
        
        # Koszt kary za spóźnienie: calkowity koszt to 90 PLN za calkowite 3h wykorzystania roweru 
        # Kara w tej sytuacji ma mnoznik [2] wiec mamy 2h spoznienia x 2.0 x 30 PLN => 120 kary + 90 kosztu = 210 PLN. 
        self.assertEqual(rachunek.amount, 210)