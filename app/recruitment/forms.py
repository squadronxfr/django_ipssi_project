from django import forms
from .models import Candidature


class CandidatureForm(forms.ModelForm):
    """Formulaire pour la création d'une candidature."""

    class Meta:
        model = Candidature
        fields = ["cv_file", "lettre_motivation_file"]
        widgets = {
            "cv_file": forms.FileInput(attrs={"class": "form-control"}),
            "lettre_motivation_file": forms.FileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "cv_file": "Votre CV (PDF, DOC, DOCX)",
            "lettre_motivation_file": "Lettre de motivation (optionnel)",
        }