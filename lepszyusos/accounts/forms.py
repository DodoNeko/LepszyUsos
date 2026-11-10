import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class BootstrapMixin:
    """Dodaje klasy Bootstrapa do wszystkich pól formularza."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.setdefault('class', css)

    def full_clean(self):
        super().full_clean()
        # podświetlenie błędnych pól na czerwono
        for name in self.errors:
            if name in self.fields:
                widget = self.fields[name].widget
                widget.attrs['class'] = widget.attrs.get('class', '') + ' is-invalid'


class LogowanieForm(BootstrapMixin, AuthenticationForm):
    pass


class RejestracjaForm(BootstrapMixin, UserCreationForm):
    role = forms.ChoiceField(
        label='Rejestruję się jako',
        choices=User.Role.choices,
        initial=User.Role.STUDENT,
        help_text='Konto prowadzącego musi zostać zatwierdzone przez administratora.',
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'nr_albumu')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('first_name', 'last_name', 'email'):
            self.fields[name].required = True
        self.fields['nr_albumu'].help_text = 'Wymagany dla studentów (5-6 cyfr).'

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Konto z tym adresem e-mail już istnieje.')
        return email

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        nr = (cleaned.get('nr_albumu') or '').strip()
        if role == User.Role.STUDENT:
            if not nr:
                self.add_error('nr_albumu', 'Student musi podać numer albumu.')
            elif not re.fullmatch(r'\d{5,6}', nr):
                self.add_error('nr_albumu', 'Numer albumu to 5-6 cyfr.')
            elif User.objects.filter(nr_albumu=nr).exists():
                self.add_error('nr_albumu', 'Ten numer albumu jest już zarejestrowany.')
        else:
            cleaned['nr_albumu'] = ''
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        user.nr_albumu = self.cleaned_data.get('nr_albumu', '')
        # prowadzący czeka na zatwierdzenie przez administratora
        user.is_approved = user.role == User.Role.STUDENT
        if commit:
            user.save()
        return user
