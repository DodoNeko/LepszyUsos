from django.contrib.auth.models import AbstractUser
from django.db import models


class Grupa(models.Model):
    nazwa = models.CharField('nazwa grupy', max_length=50, unique=True)
    opis = models.CharField('opis', max_length=150, blank=True)

    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'
        ordering = ['nazwa']

    def __str__(self):
        return self.nazwa

class User(AbstractUser):
    """Użytkownik systemu.

    Administrator to superuser Django (is_superuser / is_staff), loguje się do /admin/
    i zarządza kursami. Pozostali użytkownicy mają rolę student albo prowadzący.
    Konto prowadzącego wymaga zatwierdzenia przez administratora (is_approved).
    """

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        PROWADZACY = 'prowadzacy', 'Prowadzący'

    role = models.CharField('rola', max_length=20, choices=Role.choices, default=Role.STUDENT)
    nr_albumu = models.CharField('numer albumu', max_length=10, blank=True)
    grupa = models.ForeignKey(
        Grupa,
        verbose_name='grupa',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='studenci',
    )
    is_approved = models.BooleanField(
        'zatwierdzony',
        default=True,
        help_text='Konto prowadzącego działa dopiero po zatwierdzeniu przez administratora.',
    )

    class Meta:
        verbose_name = 'użytkownik'
        verbose_name_plural = 'użytkownicy'

    def __str__(self):
        full_name = self.get_full_name()
        return full_name or self.username

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_prowadzacy(self):
        """Prowadzący z zatwierdzonym kontem."""
        return self.role == self.Role.PROWADZACY and self.is_approved

    @property
    def czeka_na_zatwierdzenie(self):
        return self.role == self.Role.PROWADZACY and not self.is_approved

class Zajecia(models.Model):
    class Dzien(models.IntegerChoices):
        PONIEDZIALEK = 1, 'Poniedziałek'
        WTOREK = 2, 'Wtorek'
        SRODA = 3, 'Środa'
        CZWARTEK = 4, 'Czwartek'
        PIATEK = 5, 'Piątek'

    class TypZajec(models.TextChoices):
        WYKLAD = 'wyklad', 'Wykład'
        CWICZENIA = 'cwiczenia', 'Ćwiczenia'
        LABORATORIUM = 'laboratorium', 'Laboratorium'
        PROJEKT = 'projekt', 'Projekt'

    grupa = models.ForeignKey(
        Grupa,
        verbose_name='grupa',
        on_delete=models.CASCADE,
        related_name='zajecia',
    )
    przedmiot = models.CharField('przedmiot', max_length=120)
    typ = models.CharField('typ zajęć', max_length=20, choices=TypZajec.choices, default=TypZajec.CWICZENIA)
    dzien = models.IntegerField('dzień tygodnia', choices=Dzien.choices)
    godzina_od = models.TimeField('od godziny')
    godzina_do = models.TimeField('do godziny')
    sala = models.CharField('sala', max_length=30, blank=True)
    prowadzacy = models.CharField('prowadzący', max_length=120, blank=True)

    class Meta:
        verbose_name = 'zajęcia'
        verbose_name_plural = 'zajęcia'
        ordering = ['dzien', 'godzina_od']

    def __str__(self):
        return f'{self.przedmiot} ({self.get_dzien_display()} {self.godzina_od:%H:%M}-{self.godzina_do:%H:%M})'
