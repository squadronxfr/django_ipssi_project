# Documentation de l'API de Recrutement

Ce document décrit les endpoints de l'API REST pour le module de recrutement.

**Préfixe de l'API**: `/recruitment/api/`

---

## Ressource : Postes (`/postes/`)

Endpoints pour gérer les offres d'emploi.

- **`GET /recruitment/api/postes/`**
  - **Description**: Récupère la liste de tous les postes.
  - **Permissions**: Tout utilisateur authentifié.
  - **Filtres**: `search` (sur titre, description, compétences), `ordering` (sur `date_creation`, `titre`).

- **`POST /recruitment/api/postes/`**
  - **Description**: Crée un nouveau poste.
  - **Permissions**: Recruteur ou Admin.
  - **Corps de la requête**: Objet JSON avec les détails du poste (`titre`, `description`, etc.).

- **`GET /recruitment/api/postes/{id}/`**
  - **Description**: Récupère les détails d'un poste spécifique.
  - **Permissions**: Tout utilisateur authentifié.

- **`PUT /recruitment/api/postes/{id}/`**
  - **Description**: Met à jour complètement un poste.
  - **Permissions**: Recruteur ou Admin.

- **`PATCH /recruitment/api/postes/{id}/`**
  - **Description**: Met à jour partiellement un poste.
  - **Permissions**: Recruteur ou Admin.

- **`DELETE /recruitment/api/postes/{id}/`**
  - **Description**: Supprime un poste.
  - **Permissions**: Recruteur ou Admin.

---

## Ressource : Candidatures (`/candidatures/`)

Endpoints pour gérer les candidatures aux postes.

- **`GET /recruitment/api/candidatures/`**
  - **Description**: Récupère la liste des candidatures. Les candidats ne voient que leurs propres candidatures. Les recruteurs et admins voient tout.
  - **Permissions**: Tout utilisateur authentifié.
  - **Filtres**: `ordering` (sur `date_soumission`, `statut`).

- **`POST /recruitment/api/candidatures/`**
  - **Description**: Crée une nouvelle candidature (postuler à une offre).
  - **Permissions**: Candidat uniquement.
  - **Corps de la requête**: `multipart/form-data` avec les champs du formulaire (`motivation`, `cv_file`, etc.) et l'ID du poste.

- **`GET /recruitment/api/candidatures/{id}/`**
  - **Description**: Récupère les détails d'une candidature spécifique.
  - **Permissions**: Propriétaire de la candidature, Recruteur ou Admin.

- **`PUT /recruitment/api/candidatures/{id}/`**
  - **Description**: Met à jour une candidature.
  - **Permissions**: Propriétaire de la candidature, Recruteur ou Admin.

- **`PATCH /recruitment/api/candidatures/{id}/`**
  - **Description**: Met à jour partiellement une candidature (ex: changer le statut).
  - **Permissions**: Propriétaire de la candidature, Recruteur ou Admin.

- **`DELETE /recruitment/api/candidatures/{id}/`**
  - **Description**: Supprime une candidature.
  - **Permissions**: Propriétaire de la candidature, Recruteur ou Admin.

---

## Ressource : Scores (`/scores/`)

Endpoints pour consulter les scores des candidatures.

- **`GET /recruitment/api/scores/`**
  - **Description**: Récupère la liste des scores. Les candidats ne voient que les scores de leurs candidatures.
  - **Permissions**: Tout utilisateur authentifié.

- **`GET /recruitment/api/scores/{id}/`**
  - **Description**: Récupère un score spécifique.
  - **Permissions**: Propriétaire de la candidature associée, Recruteur ou Admin.
