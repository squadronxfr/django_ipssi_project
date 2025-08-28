# -*- coding: utf-8 -*-
from django.urls import path
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth import views as auth_views

from .views import (
    RoleBasedLoginView,
    CandidateSignUpView,
    ProfileView,
    LogoutViewCBV,
    PasswordChangeViewCBV,
)
from .decorators import admin_required, recruteur_required, candidat_required

def home(request):
    """Redirige vers profil si connecté, sinon vers login."""
    if request.user.is_authenticated:
        return redirect('profile')
    return redirect('login')


@admin_required
def admin_only_view(request):
    return HttpResponse("admin ok")


@recruteur_required
def recruiter_or_admin_view(request):
    return HttpResponse("recruiter ok")


@candidat_required
def candidate_only_view(request):
    return HttpResponse("candidate ok")


urlpatterns = [
    path('', home, name='home'),
    # Auth
    path('login/', RoleBasedLoginView.as_view(), name='login'),
    path('logout/', LogoutViewCBV.as_view(), name='logout'),
    path('register/', CandidateSignUpView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-change/', PasswordChangeViewCBV.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # Endpoints de test pour les décorateurs
    path('only-admin/', admin_only_view, name='only_admin'),
    path('recruiter-or-admin/', recruiter_or_admin_view, name='recruiter_or_admin'),
    path('only-candidate/', candidate_only_view, name='only_candidate'),
]
