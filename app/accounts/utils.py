# -*- coding: utf-8 -*-
from typing import Iterable

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from .models import UserProfile
from . import permissions as perms


@transaction.atomic
def create_default_groups() -> None:
    """
    Crée (ou met à jour) les groupes par défaut et leur assigne les permissions
    définies dans accounts.permissions et UserProfile.Meta.permissions.

    Idempotent: peut être appelé plusieurs fois sans effets indésirables.
    """
    # S'assurer que les Permission concernés existent (après migrations)
    ct = ContentType.objects.get_for_model(UserProfile)

    # Construire l'ensemble des codenames nécessaires
    required_codenames = set()
    for codes in perms.GROUP_PERMISSIONS.values():
        required_codenames.update(codes)

    # Vérifier l'existence des Permission objets
    existing_perms = Permission.objects.filter(content_type=ct, codename__in=required_codenames)
    existing_by_code = {p.codename: p for p in existing_perms}

    missing = required_codenames - set(existing_by_code.keys())
    if missing:
        # Les built-ins (add/change/delete/view) existent toujours après migrations
        # Si des customs manquent, c'est probablement que les migrations n'ont pas été appliquées.
        # On ne lève pas d'erreur bloquante, mais on continue avec celles disponibles.
        pass

    # Créer/mettre à jour les groupes et assigner les permissions
    for group_name, codename_set in perms.GROUP_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        perm_objs: Iterable[Permission] = Permission.objects.filter(
            content_type=ct, codename__in=list(codename_set)
        )
        group.permissions.set(list(perm_objs))
        group.save()
