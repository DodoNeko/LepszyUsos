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


class BezpieczenstwoRejestracjiTests(TestCase):
    def test_nie_da_sie_zarejestrowac_admina(self):
        """Dopisane do formularza pola is_staff/is_superuser są ignorowane."""
        self.client.post(reverse('rejestracja'), {
            'username': 'haker', 'first_name': 'H', 'last_name': 'K',
            'email': 'h@example.com', 'role': 'student', 'nr_albumu': '654321',
            'password1': 'TajneHaslo123!', 'password2': 'TajneHaslo123!',
            'is_staff': 'on', 'is_superuser': 'on',
        })
        u = User.objects.get(username='haker')
        self.assertFalse(u.is_staff)
        self.assertFalse(u.is_superuser)

    def test_nieznana_rola_odrzucona(self):
        self.client.post(reverse('rejestracja'), {
            'username': 'haker', 'first_name': 'H', 'last_name': 'K',
            'email': 'h@example.com', 'role': 'admin', 'nr_albumu': '654321',
            'password1': 'TajneHaslo123!', 'password2': 'TajneHaslo123!',
        })
        self.assertFalse(User.objects.filter(username='haker').exists())

    def test_panel_admina_tylko_dla_staff(self):
        User.objects.create_user('ania', password='TajneHaslo123!')
        self.client.login(username='ania', password='TajneHaslo123!')
        r = self.client.get('/admin/')
        self.assertEqual(r.status_code, 302)
        self.assertIn('/admin/login/', r.url)


class DekoratoryTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import AnonymousUser
        from django.test import RequestFactory
        from .decorators import tylko_admin, tylko_prowadzacy, tylko_student
        from django.http import HttpResponse

        self.rf = RequestFactory()
        self.anon = AnonymousUser()
        widok = lambda request: HttpResponse('ok')
        self.widoki = {
            'student': tylko_student(widok),
            'prowadzacy': tylko_prowadzacy(widok),
            'admin': tylko_admin(widok),
        }
        self.student = User.objects.create_user('s', password='x', role='student', nr_albumu='111111')
        self.prow = User.objects.create_user('p', password='x', role='prowadzacy', is_approved=True)
        self.prow_nz = User.objects.create_user('pn', password='x', role='prowadzacy', is_approved=False)
        self.admin = User.objects.create_superuser('a', password='x')

    def wywolaj(self, rodzaj, user):
        from django.core.exceptions import PermissionDenied
        req = self.rf.get('/x/')
        req.user = user
        try:
            return self.widoki[rodzaj](req).status_code
        except PermissionDenied:
            return 403

    def test_dostepy(self):
        oczekiwane = {
            # (widok, użytkownik): kod odpowiedzi
            ('student', 'student'): 200, ('student', 'prow'): 403, ('student', 'admin'): 403,
            ('prowadzacy', 'prow'): 200, ('prowadzacy', 'prow_nz'): 403, ('prowadzacy', 'student'): 403,
            ('admin', 'admin'): 200, ('admin', 'student'): 403, ('admin', 'prow'): 403,
        }
        for (widok, kto), kod in oczekiwane.items():
            with self.subTest(widok=widok, kto=kto):
                self.assertEqual(self.wywolaj(widok, getattr(self, kto)), kod)

    def test_anonim_przekierowany_na_login(self):
        for widok in self.widoki:
            with self.subTest(widok=widok):
                self.assertEqual(self.wywolaj(widok, self.anon), 302)


class KontaTestoweTests(TestCase):
    def test_komenda_tworzy_konta_bez_duplikatow(self):
        from django.core.management import call_command
        from io import StringIO
        call_command('konta_testowe', stdout=StringIO())
        call_command('konta_testowe', stdout=StringIO())
        self.assertEqual(User.objects.count(), 4)
        admin = User.objects.get(username='admin')
        self.assertTrue(admin.is_superuser and admin.is_staff)
        self.assertFalse(admin.is_student)
        self.assertTrue(User.objects.get(username='student').is_student)
        self.assertTrue(User.objects.get(username='prowadzacy').is_prowadzacy)
        self.assertTrue(User.objects.get(username='prowadzacy2').czeka_na_zatwierdzenie)
        self.assertTrue(self.client.login(username='student', password='student123'))
