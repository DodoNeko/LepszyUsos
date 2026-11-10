"""Dekoratory do sprawdzania ról w widokach.

Przykład:
    from accounts.decorators import tylko_prowadzacy

    @tylko_prowadzacy
    def edytuj_kurs(request, pk):
        kurs = get_object_or_404(Kurs, pk=pk, prowadzacy=request.user)
        ...

Sama rola nie wystarcza: prowadzący może zarządzać tylko swoim kursem,
dlatego w widoku zawsze filtrujcie obiekty po request.user.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def _wymagaj(warunek):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not warunek(request.user):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


tylko_student = _wymagaj(lambda u: u.is_student)
tylko_prowadzacy = _wymagaj(lambda u: u.is_prowadzacy)
tylko_admin = _wymagaj(lambda u: u.is_superuser)
