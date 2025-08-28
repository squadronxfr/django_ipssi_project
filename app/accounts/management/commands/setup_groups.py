# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from accounts.utils import create_default_groups


class Command(BaseCommand):
    help = (
        "Crée/Met à jour les groupes par défaut (admin_group, recruteur_group, "
        "candidat_group) et assigne leurs permissions."
    )

    def handle(self, *args, **options):
        create_default_groups()
        self.stdout.write(self.style.SUCCESS("Groupes et permissions configurés."))
