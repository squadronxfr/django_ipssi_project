from django.db import models
from django.contrib.auth.models import User
from .validators import validate_document_file
from .utils import upload_to_cv, upload_to_lettre


class Poste(models.Model):
    class TypeContrat(models.TextChoices):
        CDI = "CDI", "CDI"
        CDD = "CDD", "CDD"
        ALTERNANCE = "Alternance", "Alternance"

    titre = models.CharField(max_length=200)
    description = models.TextField()
    competences_requises = models.TextField(blank=True)
    type_contrat = models.CharField(max_length=20, choices=TypeContrat.choices, default=TypeContrat.CDI)
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date_creation"]
        indexes = [
            models.Index(fields=["actif", "date_creation"]),
        ]

    def __str__(self) -> str:
        return self.titre


class Candidature(models.Model):
    class Statuts(models.TextChoices):
        SOUMISE = "submitted", "Soumise"
        EN_REVUE = "in_review", "En revue"
        ENTRETIEN = "interview", "Entretien"
        ACCEPTEE = "accepted", "Acceptée"
        REFUSEE = "rejected", "Refusée"

    candidat = models.ForeignKey(User, on_delete=models.CASCADE, related_name="candidatures")
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE, related_name="candidatures")
    cv_file = models.FileField(
        upload_to=upload_to_cv,
        validators=[validate_document_file],
        blank=True,
        null=True,
    )
    lettre_motivation_file = models.FileField(
        upload_to=upload_to_lettre,
        validators=[validate_document_file],
        blank=True,
        null=True,
    )
    date_soumission = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=Statuts.choices, default=Statuts.SOUMISE)

    class Meta:
        ordering = ["-date_soumission"]
        indexes = [
            models.Index(fields=["statut", "date_soumission"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["candidat", "poste"], name="unique_candidature_par_poste"),
        ]

    def __str__(self) -> str:
        return f"{self.candidat.username} -> {self.poste.titre} ({self.get_statut_display()})"

    def get_statut_class(self) -> str:
        if self.statut == self.Statuts.SOUMISE:
            return "bg-gray-100 text-gray-800"
        elif self.statut == self.Statuts.EN_REVUE:
            return "bg-yellow-100 text-yellow-800"
        elif self.statut == self.Statuts.ENTRETIEN:
            return "bg-blue-100 text-blue-800"
        elif self.statut == self.Statuts.ACCEPTEE:
            return "bg-green-100 text-green-800"
        elif self.statut == self.Statuts.REFUSEE:
            return "bg-red-100 text-red-800"
        return "bg-gray-100 text-gray-800"


class Score(models.Model):
    candidature = models.OneToOneField(Candidature, on_delete=models.CASCADE, related_name="score")
    score_ia = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recommandation_ia = models.TextField(blank=True)
    date_analyse = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_analyse"]

    def __str__(self) -> str:
        return f"Score {self.score_ia if self.score_ia is not None else '-'} pour {self.candidature}"


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        NOUVELLE_CANDIDATURE = "new_candidature", "Nouvelle candidature"
        STATUT_CANDIDATURE = "status_update", "Changement de statut"
        NOUVEAU_POSTE = "new_post", "Nouveau poste créé"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
        ]

    def __str__(self) -> str:
        return f"Notification pour {self.user.username} ({self.get_notification_type_display()})"