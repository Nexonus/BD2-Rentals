from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def rejestracja(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('wypozyczalnia:strona_glowna')
    else:
        form = UserCreationForm()

    return render(request, 'users/register.html', {'form': form})
