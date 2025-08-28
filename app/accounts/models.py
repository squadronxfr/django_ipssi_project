from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        RECRUITER = 'recruiter', 'Recruteur'
        CANDIDATE = 'candidate', 'Candidat'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CANDIDATE)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
