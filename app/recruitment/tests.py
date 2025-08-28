import os
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import UserProfile
from .models import Poste, Candidature, Notification, Score
from .validators import validate_document_file, MAX_FILE_SIZE_BYTES

# --- Fixtures & Helpers ---

def create_user(username, role, is_staff=False):
    """Crée un utilisateur avec un profil et un rôle spécifiques."""
    user = User.objects.create_user(username=username, password='password123', email=f'{username}@test.com', is_staff=is_staff)
    UserProfile.objects.create(user=user, role=role)
    return user

# --- Test Suites ---

class ModelTests(TestCase):
    """Tests pour les modèles de l'application recruitment."""

    @classmethod
    def setUpTestData(cls):
        cls.candidat = create_user('testcandidat', UserProfile.Roles.CANDIDATE)
        cls.poste = Poste.objects.create(titre="Développeur Python", description="Un super poste.")

    def test_poste_creation(self):
        self.assertEqual(str(self.poste), "Développeur Python")
        self.assertTrue(self.poste.actif)

    def test_candidature_creation(self):
        candidature = Candidature.objects.create(candidat=self.candidat, poste=self.poste)
        self.assertEqual(str(candidature), f"testcandidat -> Développeur Python (Soumise)")
        self.assertEqual(candidature.statut, Candidature.Statuts.SOUMISE)

    def test_unique_candidature_constraint(self):
        """Vérifie qu'un candidat ne peut pas postuler deux fois au même poste."""
        Candidature.objects.create(candidat=self.candidat, poste=self.poste)
        from django.db.utils import IntegrityError
        with self.assertRaises(IntegrityError):
            Candidature.objects.create(candidat=self.candidat, poste=self.poste)

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.candidat,
            notification_type=Notification.NotificationType.NOUVEAU_POSTE,
            message="Test notification"
        )
        self.assertEqual(str(notification), f"Notification pour testcandidat (Nouveau poste créé)")


class FileUploadTests(TestCase):
    """Tests pour la validation des fichiers uploadés."""

    def test_valid_pdf_upload(self):
        """Vérifie qu'un PDF valide passe la validation."""
        # %PDF est la signature magique d'un fichier PDF
        valid_pdf = SimpleUploadedFile("cv.pdf", b"%PDF-test content", content_type="application/pdf")
        self.assertIsNone(validate_document_file(valid_pdf)) # Ne doit lever aucune exception

    def test_invalid_extension(self):
        invalid_file = SimpleUploadedFile("cv.txt", b"some text", content_type="text/plain")
        from django.core.exceptions import ValidationError
        with self.assertRaisesMessage(ValidationError, "Extension de fichier non autorisée."):
            validate_document_file(invalid_file)

    def test_file_too_large(self):
        large_content = b'a' * (MAX_FILE_SIZE_BYTES + 1)
        large_file = SimpleUploadedFile("cv.pdf", large_content, content_type="application/pdf")
        from django.core.exceptions import ValidationError
        with self.assertRaisesMessage(ValidationError, "Fichier trop volumineux"):
            validate_document_file(large_file)

    def test_malicious_file_signature(self):
        """Teste qu'un fichier avec une signature d'exécutable (MZ) est bloqué."""
        exe_file = SimpleUploadedFile("cv.docx", b"MZ... rest of file", content_type="application/octet-stream")
        from django.core.exceptions import ValidationError
        with self.assertRaisesMessage(ValidationError, "Type de fichier non autorisé"):
            validate_document_file(exe_file)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NotificationSignalTests(TestCase):
    """Teste l'envoi de notifications et d'emails via les signaux Django."""

    @classmethod
    def setUpTestData(cls):
        cls.candidat = create_user('candidat_email', UserProfile.Roles.CANDIDATE)
        cls.recruteur = create_user('recruteur_email', UserProfile.Roles.RECRUITER)
        cls.admin = create_user('admin_email', UserProfile.Roles.ADMIN, is_staff=True)

    def test_new_candidature_notification(self):
        """Vérifie qu'un email et une notif sont envoyés au recruteur lors d'une nouvelle candidature."""
        poste = Poste.objects.create(titre="Poste pour notif")
        Candidature.objects.create(candidat=self.candidat, poste=poste)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn(self.recruteur.email, email.to)
        self.assertEqual(email.subject, "Nouvelle candidature reçue")

        self.assertTrue(Notification.objects.filter(
            user=self.recruteur,
            notification_type=Notification.NotificationType.NOUVELLE_CANDIDATURE
        ).exists())

    def test_status_update_notification(self):
        """Vérifie qu'un email et une notif sont envoyés au candidat lors d'un changement de statut."""
        poste = Poste.objects.create(titre="Poste pour statut")
        candidature = Candidature.objects.create(candidat=self.candidat, poste=poste)
        mail.outbox.clear() # Vider la boîte mail de la création

        candidature.statut = Candidature.Statuts.EN_REVUE
        candidature.save()

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn(self.candidat.email, email.to)
        self.assertEqual(email.subject, "Mise à jour de votre candidature")
        self.assertIn("En revue", email.body)

        self.assertTrue(Notification.objects.filter(
            user=self.candidat,
            notification_type=Notification.NotificationType.STATUT_CANDIDATURE
        ).exists())

    def test_new_poste_notification(self):
        """Vérifie qu'un email et une notif sont envoyés à l'admin lors de la création d'un poste."""
        Poste.objects.create(titre="Nouveau poste admin")
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn(self.admin.email, email.to)
        self.assertEqual(email.subject, "Nouveau poste créé")


class WebAccessTests(TestCase):
    """Teste les permissions d'accès pour les vues web."""

    @classmethod
    def setUpTestData(cls):
        cls.candidat = create_user('web_candidat', UserProfile.Roles.CANDIDATE)
        cls.recruteur = create_user('web_recruteur', UserProfile.Roles.RECRUITER)
        cls.admin = create_user('web_admin', UserProfile.Roles.ADMIN)
        cls.poste = Poste.objects.create(titre="Poste Web")
        cls.candidature = Candidature.objects.create(
            candidat=cls.candidat, 
            poste=cls.poste,
            cv_file=SimpleUploadedFile("cv.pdf", b"%PDF-test")
        )

    def test_dashboard_access(self):
        """Teste l'accès aux dashboards admin et recruteur."""
        self.client.login(username='web_candidat', password='password123')
        response = self.client.get(reverse('recruitment:dashboard_admin'))
        self.assertEqual(response.status_code, 302) # Redirect
        response = self.client.get(reverse('recruitment:dashboard_recruteur'))
        self.assertEqual(response.status_code, 302) # Redirect

        self.client.login(username='web_recruteur', password='password123')
        response = self.client.get(reverse('recruitment:dashboard_recruteur'))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='web_admin', password='password123')
        response = self.client.get(reverse('recruitment:dashboard_admin'))
        self.assertEqual(response.status_code, 200)

    def test_cv_download_security(self):
        """Teste que seul le propriétaire, un recruteur ou un admin peut télécharger un CV."""
        # Propriétaire
        self.client.login(username='web_candidat', password='password123')
        response = self.client.get(reverse('recruitment:download_cv', args=[self.candidature.id]))
        self.assertEqual(response.status_code, 200)

        # Recruteur
        self.client.login(username='web_recruteur', password='password123')
        response = self.client.get(reverse('recruitment:download_cv', args=[self.candidature.id]))
        self.assertEqual(response.status_code, 200)

        # Autre candidat (non autorisé)
        other_candidat = create_user('other_user', UserProfile.Roles.CANDIDATE)
        self.client.login(username='other_user', password='password123')
        response = self.client.get(reverse('recruitment:download_cv', args=[self.candidature.id]))
        self.assertEqual(response.status_code, 403) # Forbidden


class APITests(APITestCase):
    """Suite de tests complète pour l'API REST de recrutement."""

    @classmethod
    def setUpTestData(cls):
        cls.candidat = create_user('api_candidat', UserProfile.Roles.CANDIDATE)
        cls.recruteur = create_user('api_recruteur', UserProfile.Roles.RECRUITER)
        cls.admin = create_user('api_admin', UserProfile.Roles.ADMIN)
        cls.poste = Poste.objects.create(titre="Poste API", description="Desc API")

    def test_poste_api_permissions(self):
        """Teste les permissions sur le PosteViewSet."""
        url = reverse('recruitment:poste-list')
        data = {'titre': 'Nouveau Poste API', 'description': 'Test'}

        # Anonyme ne peut rien faire
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Candidat peut lire mais pas créer
        self.client.force_authenticate(user=self.candidat)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Recruteur peut lire et créer
        self.client.force_authenticate(user=self.recruteur)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_candidature_api_permissions_and_crud(self):
        """Teste le CRUD et les permissions sur le CandidatureViewSet."""
        url = reverse('recruitment:candidature-list')
        cv_file = SimpleUploadedFile("cv.pdf", b"%PDF-test")
        data = {'poste': self.poste.id, 'cv_file': cv_file}

        # Recruteur ne peut pas créer de candidature
        self.client.force_authenticate(user=self.recruteur)
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Candidat peut créer une candidature
        self.client.force_authenticate(user=self.candidat)
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        candidature_id = response.data['id']

        # Le candidat peut voir sa propre candidature
        detail_url = reverse('recruitment:candidature-detail', args=[candidature_id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Le recruteur peut changer le statut de la candidature
        self.client.force_authenticate(user=self.recruteur)
        patch_data = {'statut': Candidature.Statuts.EN_REVUE}
        response = self.client.patch(detail_url, patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['statut'], Candidature.Statuts.EN_REVUE)


class PerformanceTests(TestCase):
    """Tests de performance pour éviter les régressions (ex: N+1 queries)."""

    @classmethod
    def setUpTestData(cls):
        cls.recruteur = create_user('perf_recruteur', UserProfile.Roles.RECRUITER)
        for i in range(15):
            Poste.objects.create(titre=f'Poste Perf {i}')

    def test_poste_list_query_count(self):
        """Vérifie que la liste des postes ne fait pas un nombre excessif de requêtes."""
        self.client.login(username='perf_recruteur', password='password123')
        with self.assertNumQueries(4): # 1 user, 1 profile, 1 session, 1 postes
            self.client.get(reverse('recruitment:poste_list'))

    def test_recruiter_dashboard_query_count(self):
        """Vérifie que le dashboard recruteur est optimisé (utilise select_related)."""
        candidat = create_user('perf_candidat', UserProfile.Roles.CANDIDATE)
        postes = Poste.objects.all()
        for i in range(10):
            Candidature.objects.create(candidat=candidat, poste=postes[i])
        
        self.client.login(username='perf_recruteur', password='password123')
        # Le nombre de requêtes doit être constant, peu importe le nombre de candidatures
        # 1 user, 1 profile, 1 session, 1 candidatures (avec select_related)
        with self.assertNumQueries(4):
            self.client.get(reverse('recruitment:dashboard_recruteur'))