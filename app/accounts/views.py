from typing import Optional

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from .forms import CandidateSignUpForm, ProfileForm
from .models import UserProfile


class RoleBasedLoginView(LoginView):
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True
    template_name = "accounts/login.html"

    def get_success_url(self):
        user = self.request.user

        if user.is_superuser or user.is_staff or user.groups.filter(name='admin_group').exists():
            return reverse('admin:index')

        if user.groups.filter(name='recruteur_group').exists():
            return reverse('recruitment:dashboard_recruteur')

        return reverse('profile')

    def _safe_reverse(self, name: str, fallback: str = "/") -> str:
        try:
            return reverse(name)
        except Exception:
            return fallback


class CandidateSignUpView(FormView):
    form_class = CandidateSignUpForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("login")

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "Vous êtes déjà connecté.")
            return redirect(self._safe_reverse("profile", fallback="/"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: CandidateSignUpForm):
        user: User = form.save(commit=False)
        user.email = form.cleaned_data.get("email", "").strip()
        user.first_name = form.cleaned_data.get("first_name", "").strip()
        user.last_name = form.cleaned_data.get("last_name", "").strip()
        user.save()

        UserProfile.objects.create(user=user, role=UserProfile.Roles.CANDIDATE)
        messages.success(self.request, "Votre compte a été créé. Vous pouvez maintenant vous connecter.")
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


def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect("login")


@method_decorator(login_required, name="dispatch")
class PasswordChangeViewCBV(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("password_change_done")