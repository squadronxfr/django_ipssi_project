# -*- coding: utf-8 -*-
from typing import Optional

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView, TemplateView

from .decorators import candidat_required
from .forms import CandidateSignUpForm, ProfileForm
from .models import UserProfile


class RoleBasedLoginView(LoginView):
    """
    Vue de connexion personnalisée avec redirection selon le rôle.

    Redirections (si les URLs existent), sinon fallback:
      - admin -> 'admin:index' (admin Django) si accessible, sinon profil
      - recruiter -> 'profile' (fallback générique)
      - candidate -> 'profile'
    """

    authentication_form = AuthenticationForm
    redirect_authenticated_user = True
    template_name = "accounts/login.html"  # correspond au template de l'app

    def get_success_url(self):
        user = self.request.user
        # Fallback par défaut
        default_url = self._safe_reverse("profile", fallback="/")

        # Superuser/staff -> admin
        if user.is_superuser or user.is_staff:
            return self._safe_reverse("admin:index", fallback=default_url)

        role: Optional[str] = None
        try:
            if hasattr(user, "profile") and user.profile:
                role = user.profile.role
        except Exception:
            role = None

        if role == UserProfile.Roles.ADMIN:
            return self._safe_reverse("admin:index", fallback=default_url)
        elif role == UserProfile.Roles.RECRUITER:
            return self._safe_reverse("profile", fallback=default_url)
        elif role == UserProfile.Roles.CANDIDATE:
            return self._safe_reverse("profile", fallback=default_url)
        return default_url

    def _safe_reverse(self, name: str, fallback: str = "/") -> str:
        try:
            return reverse(name)
        except Exception:
            return fallback


class CandidateSignUpView(FormView):
    """
    Vue d'inscription pour les candidats uniquement (les autres rôles sont créés par l'admin).

    - Accessible uniquement aux utilisateurs non authentifiés.
    - Crée un User + UserProfile avec rôle "candidate".
    - Redirige vers la page de connexion (ou page de profil si login auto choisi).
    """

    form_class = CandidateSignUpForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("login")  # par convention si la route existe

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            # Empêcher un utilisateur connecté de s'inscrire à nouveau
            messages.info(request, "Vous êtes déjà connecté.")
            return redirect(self._safe_reverse("profile", fallback="/"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: CandidateSignUpForm):
        # Création de l'utilisateur
        user: User = form.save(commit=False)
        user.email = form.cleaned_data.get("email", "").strip()
        user.first_name = form.cleaned_data.get("first_name", "").strip()
        user.last_name = form.cleaned_data.get("last_name", "").strip()
        user.save()

        # Créer le profil candidat
        UserProfile.objects.create(user=user, role=UserProfile.Roles.CANDIDATE)

        messages.success(self.request, "Votre compte a été créé. Vous pouvez maintenant vous connecter.")

        # Option: connecter automatiquement l'utilisateur
        # login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Veuillez corriger les erreurs du formulaire.")
        return super().form_invalid(form)

    def _safe_reverse(self, name: str, fallback: str = "/") -> str:
        try:
            return reverse(name)
        except Exception:
            return fallback


class ProfileView(LoginRequiredMixin, FormView):
    """
    Vue de profil utilisateur (consultation et modification).

    - Affiche et permet de modifier les champs basiques du User: prénom, nom, email.
    - Tous les rôles authentifiés peuvent y accéder.
    """

    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form: ProfileForm):
        form.save()
        messages.success(self.request, "Profil mis à jour avec succès.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Veuillez corriger les erreurs.")
        return super().form_invalid(form)


from django.contrib.auth import logout
from django.contrib import messages


def logout_view(request):
    """Déconnecte l'utilisateur, affiche un message et redirige vers le login."""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect("login")


@method_decorator(login_required, name="dispatch")
class PasswordChangeViewCBV(PasswordChangeView):
    """Vue de changement de mot de passe."""

    form_class = PasswordChangeForm
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("password_change_done")
