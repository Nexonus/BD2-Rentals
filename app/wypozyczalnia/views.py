from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from .models.wypozyczenia import Rower, Wypozyczenie
from .models.sprzedaze import Akcesoria, ZakupSprzetu, Sklep
from .models.operacje import Koszyk, PozycjaKoszyka, Transakcja
from .models.osoby import Klient, Pracownik
from django.utils import timezone
from decimal import Decimal

from django.db import transaction
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError
from django.db import IntegrityError

def strona_glowna(request):
    q = request.GET.get('q', '')
    kategoria = request.GET.get('kategoria', 'wszystko')

    lista_rowerow = Rower.objects.all()
    lista_akcesoriow = Akcesoria.objects.all()

    if q:
        lista_rowerow = lista_rowerow.filter(marka__icontains=q)
        lista_akcesoriow = lista_akcesoriow.filter(nazwa__icontains=q)

    if kategoria == 'rowery':
        lista_akcesoriow = lista_akcesoriow.none()
    elif kategoria == 'akcesoria':
        lista_rowerow = lista_rowerow.none()
    elif kategoria.startswith('rower_'):
        typ = kategoria.replace('rower_', '')
        lista_rowerow = lista_rowerow.filter(typ_roweru=typ)
        lista_akcesoriow = lista_akcesoriow.none()
    elif kategoria.startswith('akc_'):
        typ = kategoria.replace('akc_', '')
        lista_akcesoriow = lista_akcesoriow.filter(kategoria=typ)
        lista_rowerow = lista_rowerow.none()

    context = {
        'rowery': lista_rowerow,
        'akcesoria': lista_akcesoriow,
        'q': q,
        'kategoria': kategoria,
        'kategorie_rowerow': Rower.MODEL_CHOICES,
        'kategorie_akcesoriow': Akcesoria.KATEGORIE
    }
    return render(request, 'wypozyczalnia/index.html', context)

@login_required
def dodaj_do_koszyka(request, typ_produktu, produkt_id):
    koszyk, _ = Koszyk.objects.get_or_create(uzytkownik=request.user)
    
    if typ_produktu == 'rower':
        produkt = get_object_or_404(Rower, id=produkt_id)
        if not produkt.dostepnosc:
            messages.error(request, "Ten rower jest aktualnie niedostępny.")
            return redirect('wypozyczalnia:strona_glowna')
    elif typ_produktu == 'akcesoria':
        produkt = get_object_or_404(Akcesoria, id=produkt_id)
    else:
        return redirect('wypozyczalnia:strona_glowna')
        
    content_type = ContentType.objects.get_for_model(produkt)
    pozycja, created = PozycjaKoszyka.objects.get_or_create(
        koszyk=koszyk,
        content_type=content_type,
        object_id=produkt.id,
    )
    
    if not created and typ_produktu == 'akcesoria':
        pozycja.ilosc += 1
        pozycja.save()
        messages.success(request, f"Zwiększono ilość {produkt} w koszyku.")
    elif not created and typ_produktu == 'rower':
        messages.info(request, "Ten rower jest już w koszyku.")
    else:
        messages.success(request, f"Dodano {produkt} do koszyka.")
        
    return redirect('wypozyczalnia:strona_glowna')

@login_required
def usun_z_koszyka(request, pozycja_id):
    pozycja = get_object_or_404(PozycjaKoszyka, id=pozycja_id, koszyk__uzytkownik=request.user)
    pozycja.delete()
    messages.success(request, "Usunięto pozycję z koszyka.")
    return redirect('wypozyczalnia:koszyk')

@login_required
def koszyk_widok(request):
    koszyk, _ = Koszyk.objects.get_or_create(uzytkownik=request.user)
    pozycje = koszyk.pozycje.all()
    
    koszt_akcesoriow = Decimal('0.00')
    koszt_godzinowy_rowerow = Decimal('0.00')
    rowery_w_koszyku = []
    akcesoria_w_koszyku = []
    
    for pozycja in pozycje:
        if pozycja.produkt is None:
            pozycja.delete()
            continue
            
        if isinstance(pozycja.produkt, Akcesoria):
            koszt_akcesoriow += pozycja.produkt.cena_po_rabacie().amount * pozycja.ilosc
            akcesoria_w_koszyku.append(pozycja)
        elif isinstance(pozycja.produkt, Rower):
            koszt_godzinowy_rowerow += pozycja.produkt.cena_za_godzine.amount
            rowery_w_koszyku.append(pozycja)
            
    context = {
        'koszyk': koszyk,
        'pozycje': pozycje,
        'rowery_w_koszyku': rowery_w_koszyku,
        'akcesoria_w_koszyku': akcesoria_w_koszyku,
        'koszt_akcesoriow': koszt_akcesoriow,
        'koszt_godzinowy_rowerow': koszt_godzinowy_rowerow,
    }
    return render(request, 'wypozyczalnia/koszyk.html', context)

from .forms import KlientForm

@login_required
def kasa(request):
    if request.method == 'POST':
        koszyk = get_object_or_404(Koszyk, uzytkownik=request.user)
        pozycje = koszyk.pozycje.all()
        
        if not pozycje.exists():
            messages.warning(request, "Twój koszyk jest pusty.")
            return redirect('wypozyczalnia:koszyk')
            
        sklep = Sklep.objects.first()
        pracownik = Pracownik.objects.first()
        
        # Wymagaj uzupełnionego profilu
        if not hasattr(request.user, 'klient_profil'):
            messages.warning(request, "Zanim przejdziesz do kasy, musisz uzupełnić swój profil.")
            return redirect('wypozyczalnia:profil')
            
        klient = request.user.klient_profil
            
        if not (sklep and pracownik and klient):
            messages.error(request, "Błąd systemu: Brak wymaganych danych w bazie (sklep/pracownik/klient).")
            return redirect('wypozyczalnia:koszyk')
        try:
            with transaction.atomic():
                transakcja = Transakcja.objects.create(
                    sklep=sklep,
                    klient=klient,
                    pracownik=pracownik
                )
                
                for pozycja in pozycje:
                    if pozycja.produkt is None:
                        continue
                        
                    if isinstance(pozycja.produkt, Rower):
                        rower = pozycja.produkt
                        #rower.dostepnosc = False   # Mała korekta, bo teraz model się tym zajmuje 
                        #rower.save()
                        
                        Wypozyczenie.objects.create(
                            transakcja=transakcja,
                            rower=rower
                        )
                    elif isinstance(pozycja.produkt, Akcesoria):
                        ZakupSprzetu.objects.create(
                            transakcja=transakcja,
                            akcesoria=pozycja.produkt,
                            ilosc=pozycja.ilosc
                        )
                        
                pozycje.delete()
                
                messages.success(request, "Dziękujemy! Twoja rezerwacja i zakupy zostały pomyślnie zapisane.")
                return redirect('wypozyczalnia:strona_glowna')
                
            return redirect('wypozyczalnia:koszyk')
        
        except ValidationError as e:
            messages.error(request, f"Błąd: {e.message_dict}")
            return redirect('wypozyczalnia:koszyk')

@login_required
def moje_zamowienia(request):
    if not hasattr(request.user, 'klient_profil'):
        messages.warning(request, "Aby zobaczyć swoje zamówienia, uzupełnij najpierw swój profil.")
        return redirect('wypozyczalnia:profil')
        
    klient = request.user.klient_profil
    transakcje = Transakcja.objects.filter(klient=klient).order_by('-data_transakcji')
    
    context = {
        'klient': klient,
        'transakcje': transakcje,
    }
    return render(request, 'wypozyczalnia/zamowienia.html', context)

@login_required
def profil(request):
    klient = getattr(request.user, 'klient_profil', None)
    
    if request.method == 'POST':
        form = KlientForm(request.POST, instance=klient)
        if form.is_valid():
            nowy_klient = form.save(commit=False)
            nowy_klient.user = request.user
            nowy_klient.save()
            messages.success(request, "Twój profil został zaktualizowany!")
            return redirect('wypozyczalnia:strona_glowna')
    else:
        form = KlientForm(instance=klient)
        
    return render(request, 'wypozyczalnia/profil.html', {'form': form})

@login_required
def zwroc_rower(request, wynajem_id):
    if request.method == 'POST':
        wynajem = get_object_or_404(Wypozyczenie, id=wynajem_id)
        
        # Oznacz jako zwrócony
        #wynajem.termin_zwrotu = timezone.now()
        #wynajem.save()
        
        # Przywróć dostępność roweru
        #rower.dostepnosc = True
        #rower.save()
        rower = wynajem.rower
        wynajem.zakoncz_wypozyczenie() # Zrobiłem to jako funkcja w modelu jak by co! ^^

        messages.success(request, f"Rower {rower.marka} został pomyślnie zwrócony!")
    return redirect('wypozyczalnia:zamowienia')
