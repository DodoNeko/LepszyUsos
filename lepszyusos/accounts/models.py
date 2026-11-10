from django.contrib.auth.models import AbstractUser
from django.db import models


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
