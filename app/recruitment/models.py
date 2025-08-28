from django.db import models
from django.contrib.auth.models import User


class Poste(models.Model):
    """Modèle représentant un poste à pourvoir."""

    titre = models.CharField(max_length=200)
    description = models.TextField()
    competences_requises = models.TextField(blank=True)
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
    """Candidature d'un utilisateur (candidat) à un poste."""

    class Statuts(models.TextChoices):
        SOUMISE = "submitted", "Soumise"
        EN_REVUE = "in_review", "En revue"
        ACCEPTEE = "accepted", "Acceptée"
        REFUSEE = "rejected", "Refusée"

    candidat = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="candidatures",
    )
    poste = models.ForeignKey(
        Poste,
        on_delete=models.CASCADE,
        related_name="candidatures",
    )
    cv_file = models.FileField(upload_to="cvs/", blank=True, null=True)
    lettre_motivation_file = models.FileField(upload_to="lettres/", blank=True, null=True)
    date_soumission = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=Statuts.choices, default=Statuts.SOUMISE)

    class Meta:
        ordering = ["-date_soumission"]
        indexes = [
            models.Index(fields=["statut", "date_soumission"]),
        ]
        constraints = [
            # Un candidat ne peut soumettre qu'une candidature par poste simultanément (optionnel)
            models.UniqueConstraint(fields=["candidat", "poste"], name="unique_candidature_par_poste"),
        ]

    def __str__(self) -> str:
        return f"{self.candidat.username} -> {self.poste.titre} ({self.get_statut_display()})"


class Score(models.Model):
    """Score d'analyse IA associé à une candidature."""

    candidature = models.OneToOneField(
        Candidature,
        on_delete=models.CASCADE,
        related_name="score",
    )
    score_ia = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recommandation_ia = models.TextField(blank=True)
    date_analyse = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_analyse"]

    def __str__(self) -> str:
        return f"Score {self.score_ia if self.score_ia is not None else '-'} pour {self.candidature}"
