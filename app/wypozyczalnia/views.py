from django.shortcuts import render
from .models.wypozyczenia import Rower

def strona_glowna(request):
    lista_rowerow = Rower.objects.all()
    context = {
        'rowery': lista_rowerow
    }
    return render(request, 'wypozyczalnia/index.html', context)