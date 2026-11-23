from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from .models import Grupa, User, Zajecia


@admin.register(Grupa)
class GrupaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'opis')
    search_fields = ('nazwa', 'opis')


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Rola w systemie', {'fields': ('role', 'nr_albumu', 'grupa', 'is_approved')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rola w systemie', {'fields': ('role', 'nr_albumu', 'grupa', 'is_approved')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'grupa', 'is_approved', 'is_staff')
    list_filter = ('role', 'grupa', 'is_approved', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'nr_albumu', 'grupa__nazwa')
    actions = ['zatwierdz_konta']

    @admin.action(description='Zatwierdź zaznaczone konta')
    def zatwierdz_konta(self, request, queryset):
        liczba = queryset.update(is_approved=True)
        self.message_user(request, f'Zatwierdzono kont: {liczba}.', messages.SUCCESS)


@admin.register(Zajecia)
class ZajeciaAdmin(admin.ModelAdmin):
    list_display = ('przedmiot', 'grupa', 'typ', 'dzien', 'godzina_od', 'godzina_do', 'sala', 'prowadzacy')
    list_filter = ('grupa', 'dzien', 'typ')
    search_fields = ('przedmiot', 'prowadzacy', 'sala', 'grupa__nazwa')