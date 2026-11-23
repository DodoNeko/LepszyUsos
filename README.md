# LepszyUSOS

Projekt zaliczeniowy z przedmiotu *Szkielety tworzenia aplikacji* (PCz). Lepsza wersja USOS web: kursy, terminy i zakres zaliczeń, oceny.

Technologie: Django 5.2, SQLite, Bootstrap 5.3 (CDN).

## Uruchomienie (Windows, PowerShell)

W folderze repozytorium:

```
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cd lepszyusos
python manage.py migrate
python manage.py konta_testowe
python manage.py runserver
```

Aplikacja działa pod adresem http://127.0.0.1:8000/.

Testy: `python manage.py test accounts`

> Po zmianie modelu użytkownika (gałąź `authPart`) trzeba usunąć stary plik `db.sqlite3`, a potem znów uruchomić `migrate` i `konta_testowe`.

## Konta testowe

Tworzy je komenda `python manage.py konta_testowe`. Można ją uruchamiać wiele razy: konta się nie dublują, a hasła wracają do wartości z tabeli.

| Login | Hasło | Rola | Uwagi |
|---|---|---|---|
| `admin` | `admin123` | Administrator | superuser, ma dostęp do `/admin/` |
| `student` | `student123` | Student | Jan Kowalski, nr albumu 100001 |
| `prowadzacy` | `prowadzacy123` | Prowadzący | Anna Nowak, konto zatwierdzone |
| `prowadzacy2` | `prowadzacy123` | Prowadzący | Piotr Wiśniewski, konto **niezatwierdzone** (do pokazania zatwierdzania w panelu admina) |

Hasła są tylko do testów lokalnych.

## Role

| Rola | Jak powstaje | Co może |
|---|---|---|
| Administrator | tylko komendą `createsuperuser`, `konta_testowe` albo przez innego admina w `/admin/`. **Nie da się go założyć przez rejestrację.** | panel `/admin/`: zarządza użytkownikami, zatwierdza konta prowadzących (akcja „Zatwierdź zaznaczone konta”), tworzy kursy |
| Prowadzący | rejestracja na stronie z wyborem „Prowadzący” | może się zalogować od razu, ale funkcje prowadzącego działają dopiero po zatwierdzeniu przez admina (`is_approved`) |
| Student | rejestracja na stronie z wyborem „Student” (wymagany numer albumu, 5-6 cyfr, unikalny) | konto działa od razu |

Formularz rejestracji przyjmuje tylko pola: login, imię, nazwisko, e-mail, rola (student/prowadzący), numer albumu i hasło. Dopisanie do żądania `is_staff` albo `is_superuser` nic nie da, co sprawdza test.

## Obsługa aplikacji

Opis dotyczy tego, co działa teraz: konta, logowanie, profil i panel admina. Kursy, zaliczenia i oceny dojdą w kolejnych częściach projektu.

### Jako administrator

1. Zaloguj się na stronie (`/konto/login/`) jako `admin` / `admin123`. W menu pojawi się czerwona plakietka „admin” i link **Panel admina**. Możesz też wejść od razu na `/admin/`.
2. **Zatwierdzanie konta prowadzącego, sposób 1 (kilka kont naraz):**
   - w panelu kliknij **Użytkownicy**;
   - w filtrze po prawej „Według: zatwierdzony” wybierz **Nie**, żeby zostały tylko konta czekające na zatwierdzenie;
   - zaznacz konta, w polu **Akcja** wybierz „Zatwierdź zaznaczone konta” i kliknij **Wykonaj**.
3. **Zatwierdzanie konta prowadzącego, sposób 2 (jedno konto):** kliknij login użytkownika, w sekcji „Rola w systemie” zaznacz **Zatwierdzony** i kliknij **Zapisz**.
4. **Wyszukiwanie użytkowników:** pole wyszukiwania nad listą szuka po loginie, imieniu, nazwisku, e-mailu i numerze albumu. Filtry po prawej zawężają listę po roli, zatwierdzeniu, statusie obsługi i aktywności.
5. **Dodanie użytkownika ręcznie:** Użytkownicy, potem **Dodaj**. Podajesz login i hasło, a w sekcji „Rola w systemie” rolę, numer albumu i zatwierdzenie.
6. **Nadanie komuś uprawnień administratora:** w edycji użytkownika zaznacz **W zespole** (`is_staff`) i **Status administratora** (`is_superuser`). Tylko w ten sposób albo komendą `createsuperuser` powstaje nowy admin.
7. **Zablokowanie konta:** odznacz **Aktywny**. Użytkownik nie będzie mógł się zalogować, a jego dane zostają w bazie.
8. Sekcja **Grupy** w panelu jest wbudowana w Django. Projekt jej nie używa, bo role trzymamy w polu `role`.

### Jako prowadzący

1. **Rejestracja:** kliknij **Załóż konto**, wypełnij login, imię, nazwisko, e-mail i hasło, a w polu „Rejestruję się jako” wybierz **Prowadzący**. Numeru albumu nie trzeba podawać.
2. Po rejestracji od razu jesteś zalogowany, ale na profilu widać żółty komunikat, że konto czeka na zatwierdzenie. Do tego czasu funkcje prowadzącego są zablokowane (błąd 403).
3. Kiedy admin zatwierdzi konto, komunikat znika, a w menu pojawia się plakietka „prowadzący”.
4. Do testów: `prowadzacy` / `prowadzacy123` (zatwierdzony) oraz `prowadzacy2` / `prowadzacy123` (czeka na zatwierdzenie).
5. **Profil** (kliknij swoje imię w menu): login, imię i nazwisko, e-mail, rola, data założenia konta.
6. **Wylogowanie:** przycisk **Wyloguj** w menu.

### Jako student

1. **Rejestracja:** kliknij **Załóż konto**, wypełnij dane, wybierz **Student** i podaj numer albumu (5-6 cyfr, nie może być zajęty). Konto działa od razu i jesteś zalogowany.
2. Jeśli coś jest źle wpisane (na przykład numer albumu `12ab`, zajęty e-mail albo różne hasła), błędne pole podświetla się na czerwono z opisem błędu.
3. Do testów: `student` / `student123`.
4. **Profil** (kliknij swoje imię w menu): dane konta razem z numerem albumu. W menu jest plakietka „student”.
5. Student nie ma dostępu do panelu admina. Wejście na `/admin/` kończy się ekranem logowania do panelu.
6. **Wylogowanie:** przycisk **Wyloguj** w menu.

## Ścieżki

| Adres | Do czego służy | Logowanie | Kto ma dostęp |
|---|---|---|---|
| `/` | strona główna | nie | wszyscy |
| `/konto/login/` | logowanie | nie | niezalogowani (zalogowany trafia na stronę główną) |
| `/konto/rejestracja/` | zakładanie konta studenta lub prowadzącego | nie | niezalogowani (zalogowany trafia na stronę główną) |
| `/konto/logout/` | wylogowanie, tylko metodą POST (przycisk „Wyloguj” w menu) | tak | każdy zalogowany |
| `/konto/profil/` | dane zalogowanego użytkownika, informacja o oczekiwaniu na zatwierdzenie | tak | każdy zalogowany; niezalogowany jest przekierowany na logowanie |
| `/admin/` | panel administratora Django | tak | tylko administrator (`is_staff`); inni są przekierowani na logowanie panelu |

## Zabezpieczenia dla kolejnych widoków

W `accounts/decorators.py` są dekoratory do widoków:

| Dekorator | Przepuszcza | Niezalogowany | Zalogowany z inną rolą |
|---|---|---|---|
| `@tylko_student` | studenta | przekierowanie na logowanie | błąd 403 |
| `@tylko_prowadzacy` | **zatwierdzonego** prowadzącego | przekierowanie na logowanie | błąd 403 (także niezatwierdzony prowadzący) |
| `@tylko_admin` | administratora | przekierowanie na logowanie | błąd 403 |

Sama rola nie wystarcza: prowadzący może zmieniać tylko swoje kursy, więc w widoku zawsze filtrujemy po zalogowanym użytkowniku:

```python
from accounts.decorators import tylko_prowadzacy

@tylko_prowadzacy
def edytuj_kurs(request, pk):
    kurs = get_object_or_404(Kurs, pk=pk, prowadzacy=request.user)
    ...
```

## Zasady w zespole

- W modelach odwołujemy się do użytkownika przez `settings.AUTH_USER_MODEL`, nigdy przez `django.contrib.auth.models.User`.
- Szablony rozszerzają `base.html` (`{% extends 'base.html' %}`, blok `content`, opcjonalnie `nav_links`).
- Formularze mogą dziedziczyć `BootstrapMixin` z `accounts/forms.py`, a pola renderujemy przez `{% include '_form_field.html' %}`.
- Każdy commituje ze swojego konta, pracujemy na osobnych gałęziach i robimy PR do `main`.
