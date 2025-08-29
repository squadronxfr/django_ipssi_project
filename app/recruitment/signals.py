from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.models import UserProfile
from accounts.utils import send_templated_email
from .models import Candidature, Poste, Notification


@receiver(post_save, sender=Candidature)
def notify_on_candidature_change(sender, instance, created, **kwargs):
    """Notifie les recruteurs d'une nouvelle candidature ou le candidat d'un changement de statut."""
    if created:
        # 1. Notifier les recruteurs d'une nouvelle candidature
        recruteurs = User.objects.filter(profile__role=UserProfile.Roles.RECRUITER)
        if not recruteurs.exists():
            return

        poste_url = reverse("recruitment:poste-detail", kwargs={"pk": instance.poste.pk})
        context = {
            "candidat_name": instance.candidat.get_full_name() or instance.candidat.username,
            "poste_titre": instance.poste.titre,
            "poste_url": poste_url,
        }

        for recruteur in recruteurs:
            Notification.objects.create(
                user=recruteur,
                notification_type=Notification.NotificationType.NOUVELLE_CANDIDATURE,
                message=f"Nouvelle candidature de {context['candidat_name']} pour le poste: {context['poste_titre']}."
            )
            send_templated_email(
                subject="Nouvelle candidature reçue",
                to_emails=recruteur.email,
                template_txt="recruitment/emails/new_candidature.txt",
                html_template="recruitment/emails/new_candidature.html",
                context=context,
            )
    else:
        # 2. Notifier le candidat d'un changement de statut
        try:
            original_instance = Candidature.objects.get(pk=instance.pk)
            if original_instance.statut != instance.statut:
                context = {
                    "poste_titre": instance.poste.titre,
                    "nouveau_statut": instance.get_statut_display(),
                }
                Notification.objects.create(
                    user=instance.candidat,
                    notification_type=Notification.NotificationType.STATUT_CANDIDATURE,
                    message=f"Le statut de votre candidature pour le poste \"{context['poste_titre']}\" est maintenant : {context['nouveau_statut']}."
                )
                send_templated_email(
                    subject="Mise à jour de votre candidature",
                    to_emails=instance.candidat.email,
                    template_txt="recruitment/emails/status_update.txt",
                    html_template="recruitment/emails/status_update.html",
                    context=context,
                )
        except Candidature.DoesNotExist:
            pass  # Ne rien faire si l'instance originale n'existe pas


@receiver(post_save, sender=Poste)
def notify_admin_on_new_poste(sender, instance, created, **kwargs):
    """Notifie les administrateurs de la création d'un nouveau poste."""
    if created:
        admins = User.objects.filter(Q(profile__role=UserProfile.Roles.ADMIN) | Q(is_staff=True))
        if not admins.exists():
            return

        context = {
            "poste_titre": instance.titre,
            "poste_description": instance.description,
        }

        for admin in admins:
            Notification.objects.create(
                user=admin,
                notification_type=Notification.NotificationType.NOUVEAU_POSTE,
                message=f"Un nouveau poste a été créé : {instance.titre}"
            )
            send_templated_email(
                subject="Nouveau poste créé",
                to_emails=admin.email,
                template_txt="recruitment/emails/new_poste.txt",
                html_template="recruitment/emails/new_poste.html",
                context=context,
            )
