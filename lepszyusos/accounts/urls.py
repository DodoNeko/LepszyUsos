from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.LogowanieView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('rejestracja/', views.rejestracja, name='rejestracja'),
    path('profil/', views.profil, name='profil'),
]
