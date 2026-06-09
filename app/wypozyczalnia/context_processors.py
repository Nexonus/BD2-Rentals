from .models.operacje import Koszyk

def cart_processor(request):
    cart_items_count = 0
    if request.user.is_authenticated:
        try:
            koszyk = Koszyk.objects.get(uzytkownik=request.user)
            cart_items_count = sum(pozycja.ilosc for pozycja in koszyk.pozycje.all() if pozycja.produkt is not None)
        except Koszyk.DoesNotExist:
            cart_items_count = 0
    return {'cart_items_count': cart_items_count}
