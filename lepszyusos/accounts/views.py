from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import LogowanieForm, RejestracjaForm


class LogowanieView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LogowanieForm
    redirect_authenticated_user = True


def rejestracja(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RejestracjaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        if user.czeka_na_zatwierdzenie:
            messages.info(request, 'Konto utworzone. Funkcje prowadzącego będą dostępne po zatwierdzeniu przez administratora.')
        else:
            messages.success(request, 'Konto utworzone, witaj!')
        return redirect('profil')
    return render(request, 'accounts/rejestracja.html', {'form': form})


@login_required
def profil(request):
    return render(request, 'accounts/profil.html')
