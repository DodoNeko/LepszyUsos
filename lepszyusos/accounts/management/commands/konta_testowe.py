"""Tworzy (albo przywraca) konta testowe: admina, studenta i prowadzących.

Użycie:  python manage.py konta_testowe

Można uruchamiać wielokrotnie: istniejące konta nie są dublowane,
tylko ich dane i hasła wracają do wartości z listy poniżej.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User

KONTA = [
    {
        'username': 'admin', 'password': 'admin123',
        'first_name': 'Adam', 'last_name': 'Administrator', 'email': 'admin@lepszyusos.pl',
        'role': User.Role.STUDENT, 'nr_albumu': '', 'is_approved': True,
        'is_staff': True, 'is_superuser': True,
    },
    {
        'username': 'student', 'password': 'student123',
        'first_name': 'Jan', 'last_name': 'Kowalski', 'email': 'student@lepszyusos.pl',
        'role': User.Role.STUDENT, 'nr_albumu': '100001', 'is_approved': True,
        'is_staff': False, 'is_superuser': False,
    },
    {
        'username': 'prowadzacy', 'password': 'prowadzacy123',
        'first_name': 'Anna', 'last_name': 'Nowak', 'email': 'prowadzacy@lepszyusos.pl',
        'role': User.Role.PROWADZACY, 'nr_albumu': '', 'is_approved': True,
        'is_staff': False, 'is_superuser': False,
    },
    {
        'username': 'prowadzacy2', 'password': 'prowadzacy123',
        'first_name': 'Piotr', 'last_name': 'Wiśniewski', 'email': 'prowadzacy2@lepszyusos.pl',
        'role': User.Role.PROWADZACY, 'nr_albumu': '', 'is_approved': False,
        'is_staff': False, 'is_superuser': False,
    },
]


class Command(BaseCommand):
    help = 'Tworzy konta testowe (admin, student, prowadzący zatwierdzony i niezatwierdzony).'

    @transaction.atomic
    def handle(self, *args, **options):
        for dane in KONTA:
            dane = dict(dane)
            haslo = dane.pop('password')
            user, utworzone = User.objects.get_or_create(username=dane['username'])
            for pole, wartosc in dane.items():
                setattr(user, pole, wartosc)
            user.is_active = True
            user.set_password(haslo)
            user.save()
            stan = 'utworzono' if utworzone else 'zaktualizowano'
            self.stdout.write(f'{stan}: {user.username} / {haslo}')
        self.stdout.write(self.style.SUCCESS('Konta testowe gotowe.'))
