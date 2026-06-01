from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models.wypozyczenia import Rower

def strona_glowna(request):
    lista_rowerow = Rower.objects.all()
    context = {
        'rowery': lista_rowerow
    }
    return render(request, 'wypozyczalnia/index.html', context)

def rejestracja(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('wypozyczalnia:login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
