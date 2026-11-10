from django.test import TestCase
from django.urls import reverse

from .models import User


class RejestracjaTests(TestCase):
    def dane(self, **kwargs):
        d = {
            'username': 'jkowalski', 'first_name': 'Jan', 'last_name': 'Kowalski',
            'email': 'jan@example.com', 'role': 'student', 'nr_albumu': '123456',
            'password1': 'TajneHaslo123!', 'password2': 'TajneHaslo123!',
        }
        d.update(kwargs)
        return d

    def test_student_rejestruje_sie_i_jest_zalogowany(self):
        r = self.client.post(reverse('rejestracja'), self.dane())
        self.assertRedirects(r, reverse('profil'))
        u = User.objects.get(username='jkowalski')
        self.assertTrue(u.is_student)
        self.assertTrue(u.is_approved)

    def test_prowadzacy_czeka_na_zatwierdzenie(self):
        self.client.post(reverse('rejestracja'), self.dane(role='prowadzacy', nr_albumu=''))
        u = User.objects.get(username='jkowalski')
        self.assertFalse(u.is_prowadzacy)
        self.assertTrue(u.czeka_na_zatwierdzenie)

    def test_student_bez_numeru_albumu(self):
        r = self.client.post(reverse('rejestracja'), self.dane(nr_albumu=''))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.exists())

    def test_zly_numer_albumu(self):
        self.client.post(reverse('rejestracja'), self.dane(nr_albumu='12ab'))
        self.assertFalse(User.objects.exists())

    def test_duplikat_emaila(self):
        User.objects.create_user('inny', email='jan@example.com', password='x')
        self.client.post(reverse('rejestracja'), self.dane())
        self.assertFalse(User.objects.filter(username='jkowalski').exists())


class LogowanieTests(TestCase):
    def test_logowanie_i_profil(self):
        User.objects.create_user('ania', password='TajneHaslo123!')
        r = self.client.post(reverse('login'), {'username': 'ania', 'password': 'TajneHaslo123!'})
        self.assertRedirects(r, reverse('home'))
        self.assertEqual(self.client.get(reverse('profil')).status_code, 200)

    def test_profil_wymaga_logowania(self):
        r = self.client.get(reverse('profil'))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse('login'), r.url)

    def test_wylogowanie_post(self):
        User.objects.create_user('ania', password='TajneHaslo123!')
        self.client.login(username='ania', password='TajneHaslo123!')
        self.client.post(reverse('logout'))
        self.assertEqual(self.client.get(reverse('profil')).status_code, 302)
