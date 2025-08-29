from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Crée les groupes par défaut"

    def handle(self, *args, **options):
        groups = ['admin_group', 'recruteur_group', 'candidat_group']
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)
        self.stdout.write(self.style.SUCCESS("Groupes créés."))
