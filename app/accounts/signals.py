from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import UserProfile

@receiver(post_save, sender=UserProfile)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        group_mapping = {
            UserProfile.Roles.ADMIN: 'admin_group',
            UserProfile.Roles.RECRUITER: 'recruteur_group',
            UserProfile.Roles.CANDIDATE: 'candidat_group',
        }
        group_name = group_mapping.get(instance.role, 'candidat_group')
        group, _ = Group.objects.get_or_create(name=group_name)
        instance.user.groups.clear()
        instance.user.groups.add(group)