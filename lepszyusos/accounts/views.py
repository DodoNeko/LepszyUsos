from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from datetime import time
from types import SimpleNamespace
from .forms import LogowanieForm, RejestracjaForm
from .models import Zajecia, Grupa

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


PRZYKLADOWE_ZAJECIA = [
    SimpleNamespace(
        przedmiot='Szkielety tworzenia aplikacji',
        typ='laboratorium',
        get_typ_display=lambda: 'Laboratorium',
        dzien=1,
        godzina_od=time(8, 0),
        godzina_do=time(9, 30),
        sala='L-102',
        prowadzacy='dr inż. Jan Kowalski',
    ),
    SimpleNamespace(
        przedmiot='Bazy danych',
        typ='wyklad',
        get_typ_display=lambda: 'Wykład',
        dzien=1,
        godzina_od=time(10, 0),
        godzina_do=time(11, 30),
        sala='A-1',
        prowadzacy='dr hab. Anna Nowak',
    ),
    SimpleNamespace(
        przedmiot='Algorytmy i struktury danych',
        typ='cwiczenia',
        get_typ_display=lambda: 'Ćwiczenia',
        dzien=2,
        godzina_od=time(12, 0),
        godzina_do=time(13, 30),
        sala='B-204',
        prowadzacy='mgr Piotr Zieliński',
    ),
    SimpleNamespace(
        przedmiot='Inżynieria oprogramowania',
        typ='projekt',
        get_typ_display=lambda: 'Projekt',
        dzien=4,
        godzina_od=time(14, 0),
        godzina_do=time(15, 30),
        sala='L-205',
        prowadzacy='dr Katarzyna Wiśniewska',
    ),
]


@login_required
def mapa_zajec(request):
    grupa = getattr(request.user, 'grupa', None)
    uzywa_przykładowych = False

    if grupa is not None:
        qs = Zajecia.objects.filter(grupa=grupa).order_by('dzien', 'godzina_od')
        if qs.exists():
            lista_zajec = list(qs)
        else:
            lista_zajec = PRZYKLADOWE_ZAJECIA
            uzywa_przykładowych = True
    else:
        lista_zajec = PRZYKLADOWE_ZAJECIA
        uzywa_przykładowych = True

    dni = [
        {'nr': 1, 'nazwa': 'Poniedziałek', 'zajecia': []},
        {'nr': 2, 'nazwa': 'Wtorek', 'zajecia': []},
        {'nr': 3, 'nazwa': 'Środa', 'zajecia': []},
        {'nr': 4, 'nazwa': 'Czwartek', 'zajecia': []},
        {'nr': 5, 'nazwa': 'Piątek', 'zajecia': []},
    ]
    dni_map = {d['nr']: d for d in dni}
    for z in lista_zajec:
        if z.dzien in dni_map:
            dni_map[z.dzien]['zajecia'].append(z)

    return render(
        request,
        'accounts/mapa_zajec.html',
        {
            'grupa': grupa,
            'dni': dni,
            'uzywa_przykładowych': uzywa_przykładowych,
        },
    )
    