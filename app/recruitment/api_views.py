from __future__ import annotations
from django.db.models import QuerySet
from rest_framework import viewsets, permissions, parsers, filters
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions
from accounts.models import UserProfile
from .models import Poste, Candidature, Score
from .serializers import PosteSerializer, CandidatureSerializer, ScoreSerializer


# ---------------------
# Permissions DRF custom
# ---------------------
class IsAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True
        role = getattr(getattr(user, 'profile', None), 'role', None)
        return role == UserProfile.Roles.ADMIN


class IsRecruiterOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or
            request.user.groups.filter(name__in=['admin_group', 'recruteur_group']).exists()
        )

class IsCandidate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='candidat_group').exists()

class IsOwnerOrRecruiterAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.candidat == request.user or
            request.user.is_staff or
            request.user.groups.filter(name__in=['admin_group', 'recruteur_group']).exists()
        )



# -------------
# ViewSets API
# -------------
class PosteViewSet(viewsets.ModelViewSet):
    queryset = Poste.objects.all()
    serializer_class = PosteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titre', 'description', 'competences_requises']
    ordering_fields = ['date_creation', 'titre']

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [IsRecruiterOrAdmin()]


class CandidatureViewSet(viewsets.ModelViewSet):
    serializer_class = CandidatureSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date_soumission', 'statut']

    def get_queryset(self):
        user = self.request.user
        qs = Candidature.objects.select_related('poste', 'candidat').all()

        if not user.is_authenticated:
            return qs.none()

        if user.is_staff or user.groups.filter(name__in=['admin_group', 'recruteur_group']).exists():
            return qs

        return qs.filter(candidat=user)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        if self.request.method == 'POST':
            # Seuls les candidats peuvent créer leur candidature
            return [IsCandidate()]
        # PATCH/PUT/DELETE: propriétaire ou recruteur/admin
        return [IsOwnerOrRecruiterAdmin()]


class ScoreViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScoreSerializer

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        qs = Score.objects.select_related('candidature', 'candidature__candidat', 'candidature__poste').all()
        if not user.is_authenticated:
            return qs.none()
        if user.is_superuser or user.is_staff:
            return qs
        role = getattr(getattr(user, 'profile', None), 'role', None)
        if role in (UserProfile.Roles.RECRUITER, UserProfile.Roles.ADMIN):
            return qs
        # Candidate: ne voir que le score de ses candidatures
        return qs.filter(candidature__candidat_id=user.id)