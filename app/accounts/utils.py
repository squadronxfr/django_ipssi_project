import logging
from typing import Iterable, Iterable as _Iterable, List, Optional, Union, Sequence, Mapping

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist

from .models import UserProfile
from . import permissions as perms


@transaction.atomic
def create_default_groups() -> None:
    """
    Crée (ou met à jour) les groupes par défaut et leur assigne les permissions
    définies dans accounts.permissions et UserProfile.Meta.permissions.
    """
    # S'assurer que les Permission concernés existent
    ct = ContentType.objects.get_for_model(UserProfile)

    required_codenames = set()
    for codes in perms.GROUP_PERMISSIONS.values():
        required_codenames.update(codes)

    # Vérifier l'existence des Permission objets
    existing_perms = Permission.objects.filter(content_type=ct, codename__in=required_codenames)
    existing_by_code = {p.codename: p for p in existing_perms}

    missing = required_codenames - set(existing_by_code.keys())
    if missing:
        pass

    # Créer/mettre à jour les groupes et assigner les permissions
    for group_name, codename_set in perms.GROUP_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        perm_objs: Iterable[Permission] = Permission.objects.filter(
            content_type=ct, codename__in=list(codename_set)
        )
        group.permissions.set(list(perm_objs))
        group.save()



logger = logging.getLogger(__name__)


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
        logger.debug("Permissions manquantes (peut-être migrations non appliquées): %s", ", ".join(sorted(missing)))

    # Créer/mettre à jour les groupes et assigner les permissions
    for group_name, codename_set in perms.GROUP_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        perm_objs: _Iterable[Permission] = Permission.objects.filter(
            content_type=ct, codename__in=list(codename_set)
        )
        group.permissions.set(list(perm_objs))
        group.save()


def send_templated_email(
    subject: str,
    to_emails: Union[str, Sequence[str]],
    template_txt: str,
    context: Optional[Mapping] = None,
    html_template: Optional[str] = None,
    from_email: Optional[str] = None,
) -> bool:
    """
    Envoie un email basé sur un template.

    - subject: Sujet de l'email (le préfixe EMAIL_SUBJECT_PREFIX sera ajouté automatiquement par certaines configurations).
    - to_emails: destinataire unique (str) ou liste de destinataires.
    - template_txt: chemin du template texte (ex: 'accounts/emails/welcome_email.txt').
    - context: dictionnaire de variables pour le rendu du template.
    - html_template: optionnel, template HTML à joindre en multipart.
    - from_email: expéditeur (DEFAULT_FROM_EMAIL sinon).

    Retourne True si l'envoi réussit, False sinon. Log les erreurs.
    """
    context = context or {}
    recipients: List[str] = [to_emails] if isinstance(to_emails, str) else list(to_emails)
    try:
        body_text = render_to_string(template_txt, context)
    except Exception as e:
        logger.error("Echec rendu template texte '%s': %s", template_txt, e, exc_info=True)
        return False

    try:
        message = EmailMultiAlternatives(subject=subject, body=body_text, to=recipients, from_email=from_email)

        if html_template:
            try:
                body_html = render_to_string(html_template, context)
                # Ajouter alternative HTML
                message.attach_alternative(body_html, "text/html")
            except TemplateDoesNotExist:
                # On ne bloque pas si le template HTML est absent
                logger.info("Template HTML '%s' introuvable, envoi en texte brut uniquement.", html_template)
            except Exception as e:
                logger.error("Echec rendu template HTML '%s': %s", html_template, e, exc_info=True)

        message.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error("Echec envoi email vers %s: %s", ", ".join(recipients), e, exc_info=True)
        return False


def send_welcome_email(user, extra_context: Optional[Mapping] = None) -> bool:
    """
    Envoie un email de bienvenue à un nouvel utilisateur.

    Utilise les templates:
      - accounts/emails/welcome_email.txt (obligatoire)
      - accounts/emails/welcome_email.html (optionnel)
    """
    full_name = (user.get_full_name() or user.username).strip()
    context = {
        "user": user,
        "first_name": user.first_name or user.username,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email,
        "site_name": "RH System",
        "login_url": "/login/",
    }
    if extra_context:
        context.update(extra_context)

    subject = "Bienvenue sur RH System"
    return send_templated_email(
        subject=subject,
        to_emails=user.email or [],
        template_txt="accounts/emails/welcome_email.txt",
        context=context,
        html_template="accounts/emails/welcome_email.html",
    )
