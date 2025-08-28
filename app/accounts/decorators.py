# -*- coding: utf-8 -*-
"""
Décorateurs pour protéger les vues selon les rôles utilisateurs.

Rôles disponibles (valeurs):
- "admin"
- "recruiter"
- "candidate"

Chaque décorateur renvoie une page 403 en cas d'accès refusé.
Si le template templates/403.html n'existe pas, on renvoie une HttpResponseForbidden simple.

Exemples d'utilisation:

    from django.urls import path
    from accounts.decorators import admin_required, recruteur_required, candidat_required, role_required

    @admin_required
    def admin_dashboard(request):
        ...

    @recruteur_required
    def recruteur_page(request):
        ...

    @candidat_required
    def candidate_portal(request):
        ...

    @role_required(roles=["admin", "recruiter"])  # accès aux admins et recruteurs
    def mixed_view(request):
        ...

"""
from functools import wraps
from typing import Callable, Iterable, Optional

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.core.exceptions import PermissionDenied

from .models import UserProfile


FORBIDDEN_TEMPLATE = "accounts/403.html"


def _render_403(request: HttpRequest) -> HttpResponse:
    """Tente d'afficher un template 403, sinon renvoie HttpResponseForbidden."""
    try:
        return render(request, FORBIDDEN_TEMPLATE, status=403)
    except Exception:
        # Si le template n'existe pas, on renvoie une réponse 403 simple
        return HttpResponseForbidden("403 Forbidden")


def _user_has_role(request: HttpRequest, allowed: Iterable[str]) -> bool:
    """
    Vérifie si l'utilisateur de la requête possède l'un des rôles autorisés.
    - superuser et staff sont traités comme admin.
    - gère l'absence éventuelle de profil utilisateur.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return False

    # Les superusers (et staff) sont considérés comme admin par défaut
    if user.is_superuser or user.is_staff:
        return "admin" in allowed or UserProfile.Roles.ADMIN in allowed

    # Récupérer le rôle depuis le profil si existant
    role: Optional[str] = None
    try:
        # related_name='profile' sur UserProfile
        if hasattr(user, "profile") and user.profile:
            role = user.profile.role
    except Exception:
        role = None

    if role is None:
        return False

    # Autorisé si le rôle est dans la liste autorisée (valeurs exactes)
    return role in set(str(r) for r in allowed)


def role_required(roles: Iterable[str]) -> Callable:
    """
    Décorateur générique restreignant l'accès aux utilisateurs ayant l'un des rôles fournis.

    Paramètres:
        roles: Iterable[str] des valeurs de rôle autorisées ("admin", "recruiter", "candidate").

    Comportement:
        - Si l'utilisateur n'est pas autorisé, renvoie une page 403.
        - Si autorisé, exécute la vue normalement.
    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(request: HttpRequest, *args, **kwargs):
            if _user_has_role(request, roles):
                return view_func(request, *args, **kwargs)
            return _render_403(request)

        return _wrapped_view

    return decorator


def admin_required(view_func: Callable) -> Callable:
    """Autorise uniquement les utilisateurs avec rôle admin (ou superuser/staff)."""
    return role_required([UserProfile.Roles.ADMIN])(view_func)


def recruteur_required(view_func: Callable) -> Callable:
    """
    Autorise les recruteurs et les admins.
    """
    return role_required([UserProfile.Roles.RECRUITER, UserProfile.Roles.ADMIN])(view_func)


def candidat_required(view_func: Callable) -> Callable:
    """Autorise uniquement les candidats."""
    return role_required([UserProfile.Roles.CANDIDATE])(view_func)
