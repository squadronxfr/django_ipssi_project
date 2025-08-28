# -*- coding: utf-8 -*-
from typing import Any

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CandidateSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requis. Une adresse email valide.")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def clean_email(self) -> str:
        email = self.cleaned_data.get("email", "").strip()
        if not email:
            raise forms.ValidationError("L'email est requis.")
        # Optionnel: garantir unicité d'email si souhaité (non imposé par défaut par Django)
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte utilise déjà cet email.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def clean_email(self) -> str:
        email = self.cleaned_data.get("email", "").strip()
        if not email:
            raise forms.ValidationError("L'email est requis.")
        # L'email doit être unique pour les autres utilisateurs
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre compte.")
        return email
