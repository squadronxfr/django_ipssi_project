# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Poste, Candidature, Score


class PosteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poste
        fields = [
            'id', 'titre', 'description', 'competences_requises', 'date_creation', 'actif'
        ]
        read_only_fields = ['id', 'date_creation']


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['id', 'score_ia', 'recommandation_ia', 'date_analyse', 'candidature']
        read_only_fields = ['id', 'score_ia', 'recommandation_ia', 'date_analyse', 'candidature']


class CandidatureSerializer(serializers.ModelSerializer):
    # Inclure un rendu en lecture seule du score
    score = ScoreSerializer(read_only=True)
    # Afficher des infos basiques sur le poste
    poste_titre = serializers.CharField(source='poste.titre', read_only=True)

    class Meta:
        model = Candidature
        fields = [
            'id', 'candidat', 'poste', 'poste_titre',
            'cv_file', 'lettre_motivation_file',
            'date_soumission', 'statut', 'score'
        ]
        read_only_fields = ['id', 'date_soumission', 'candidat', 'score']

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            user = request.user
            # Création: seul le candidat (role candidate) peut créer sa candidature
            if self.instance is None and request.method in ("POST",):
                role = getattr(getattr(user, 'profile', None), 'role', None)
                if not (user.is_staff or user.is_superuser) and role != 'candidate':
                    raise serializers.ValidationError("Seuls les candidats peuvent soumettre une candidature.")
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Candidature:
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['candidat'] = request.user
        return super().create(validated_data)

    def update(self, instance: Candidature, validated_data: dict[str, Any]) -> Candidature:
        # Les candidats ne peuvent mettre à jour que leurs propres fichiers (cv/lettre)
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            user = request.user
            role = getattr(getattr(user, 'profile', None), 'role', None)
            if user == instance.candidat and role == 'candidate':
                # Restreindre les champs modifiables par le candidat
                allowed = {'cv_file', 'lettre_motivation_file'}
                for key in list(validated_data.keys()):
                    if key not in allowed:
                        validated_data.pop(key)
        return super().update(instance, validated_data)