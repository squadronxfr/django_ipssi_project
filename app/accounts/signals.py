from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

from .models import UserProfile
from . import permissions as perms
from .utils import create_default_groups

ROLE_TO_GROUP = {
    UserProfile.Roles.ADMIN: perms.ADMIN_GROUP,
    UserProfile.Roles.RECRUITER: perms.RECRUITER_GROUP,
    UserProfile.Roles.CANDIDATE: perms.CANDIDATE_GROUP,
}


def _ensure_groups_exist():
    try:
        create_default_groups()
    except Exception:
        pass


def _assign_user_to_group(profile: UserProfile) -> None:
    group_name = ROLE_TO_GROUP.get(profile.role)
    if not group_name:
        return

    _ensure_groups_exist()

    user = profile.user
    groups_to_consider = [perms.ADMIN_GROUP, perms.RECRUITER_GROUP, perms.CANDIDATE_GROUP]
    user.groups.remove(*Group.objects.filter(name__in=groups_to_consider))

    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)


@receiver(post_save, sender=UserProfile)
def userprofile_post_save(sender, instance: UserProfile, created, **kwargs):
    _assign_user_to_group(instance)