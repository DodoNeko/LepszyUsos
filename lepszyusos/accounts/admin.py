from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Rola w systemie', {'fields': ('role', 'nr_albumu', 'is_approved')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rola w systemie', {'fields': ('role', 'nr_albumu', 'is_approved')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_approved', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'nr_albumu')
    actions = ['zatwierdz_konta']

    @admin.action(description='Zatwierdź zaznaczone konta')
    def zatwierdz_konta(self, request, queryset):
        liczba = queryset.update(is_approved=True)
        self.message_user(request, f'Zatwierdzono kont: {liczba}.', messages.SUCCESS)
