from django import forms
from .models import Candidature, Poste


class CandidatureForm(forms.ModelForm):
    """Formulaire pour la création d'une candidature."""

    class Meta:
        model = Candidature
        fields = ["cv_file", "lettre_motivation_file"]
        widgets = {
            "cv_file": forms.ClearableFileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-indigo-700'}),
            "lettre_motivation_file": forms.ClearableFileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-indigo-700'}),
        }
        labels = {
            "cv_file": "Votre CV (PDF, DOC, DOCX)",
            "lettre_motivation_file": "Lettre de motivation (optionnel)",
        }


class PosteForm(forms.ModelForm):
    """Formulaire pour la création et la modification d'un poste."""

    class Meta:
        model = Poste
        fields = ['titre', 'description', 'competences_requises', 'type_contrat', 'actif']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm'}),
            'description': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm', 'rows': 5}),
            'competences_requises': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm', 'rows': 3}),
            'type_contrat': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm'}),
            'actif': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary'}),
        }
        labels = {
            'titre': 'Titre du poste',
            'description': 'Description complète',
            'competences_requises': 'Compétences requises',
            'type_contrat': 'Type de contrat',
            'actif': 'Poste actif / ouvert',
        }


class CandidatureStatusForm(forms.ModelForm):
    """Formulaire pour la modification du statut d'une candidature."""

    class Meta:
        model = Candidature
        fields = ['statut']
        widgets = {
            'statut': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm'}),
        }
        labels = {
            'statut': 'Nouveau statut de la candidature',
        }