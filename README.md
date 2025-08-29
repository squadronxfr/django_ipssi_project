# 🚀 Gestion Intelligente des Ressources Humaines (Django)

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-4.2-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.14-orange.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

Plateforme RH permettant la publication d'offres (*postes*), la gestion des **candidatures** (CV & lettres), des **rôles** (admin / recruteur / candidat), des **tableaux de bord**, et une **API REST**.
Objectifs : simplicité d'usage, sécurité, architecture claire **MVT**, et base prête à accueillir un module **IA** de scoring de CV.

---

## 📋 Sommaire
- [🎯 Aperçu](#-aperçu)
- [🏗️ Architecture (MVT)](#️-architecture-mvt)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🚀 Installation & Lancement](#-installation--lancement)
- [⚙️ Configuration (ENV)](#️-configuration-env)
- [📁 Structure du dépôt](#-structure-du-dépôt)
- [🔧 Modèles & Vues (explications)](#-modèles--vues-explications)
- [📡 API REST (DRF)](#-api-rest-drf)
- [🔒 Sécurité & Bonnes pratiques](#-sécurité--bonnes-pratiques)
- [📊 Tableaux de bord](#-tableaux-de-bord)
- [🤖 IA (intégration prévue)](#-ia-intégration-prévue)
- [💻 Exemples de code](#-exemples-de-code)
- [👥 Répartition des tâches](#-répartition-des-tâches)
- [🔄 Workflow Git & Conventions](#-workflow-git--conventions)
- [📄 Licence](#-licence)

---

## 🎯 Aperçu
- **Apps** : `accounts` (auth / rôles / profil), `recruitment` (postes, candidatures, dashboards, API).
- **Rôles** : `admin`, `recruiter`, `candidate` – contrôles d'accès par décorateurs et vues.
- **Fichiers** : upload sécurisé (PDF/DOC/DOCX), chemins horodatés.
- **API** : endpoints DRF pour `postes`, `candidatures`, `scores`.
- **Dashboards** : recruteur (liste des candidatures), admin (KPIs agrégés).
- **Base IA** : modèle `Score` et endpoints prévus pour brancher un pipeline NLP (HuggingFace).

---

## 🏗️ Architecture (MVT)
- **Model** : persistance des entités (ex. `Poste`, `Candidature`, `Score`, `UserProfile`).
- **View** : logique (listes, détail, création de candidature, dashboards).
- **Template** : rendu HTML (hérite de `base.html`, cohérence UI).
Cette séparation facilite lisibilité, testabilité et réutilisation.

---

## ✨ Fonctionnalités
- 👤 Gestion des **utilisateurs & rôles** (admin/recruteur/candidat).
- 📝 Gestion des **postes** et **candidatures** (CV & lettre).
- 📧 **Notifications e-mail** (base de config prête).
- 📊 **Tableaux de bord** (admin & recruteur).
- 🔌 **API REST** pour intégrations externes.
- 🧠 Préparation à l'**IA** : extraction de compétences, scoring, résumé (pipeline à connecter).

---

## 🚀 Installation & Lancement

### 📋 1) Pré-requis
- Python 3.11+, pip
- (Option) Docker & docker-compose

### 📦 2) Clonage
```bash
git clone <URL_DU_DEPOT>
cd django_ipssi_project
```

### 🐳 3) Démarrage rapide (Docker)
```bash
docker-compose up --build
# Application: http://localhost:8000
```
> Le `docker-compose.yml` expose `8000` et monte `./app` dans le conteneur pour un dev fluide.

### 🐍 4) Démarrage local (venv)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cd app
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## ⚙️ Configuration (ENV)
Ajoutez un fichier `.env` (ou variables d'environnement) pour la messagerie :
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=...
```

---

## 📁 Structure du dépôt
```
app/
├── 📁 accounts/
│   ├── 📄 models.py        # UserProfile (rôle)
│   ├── 📄 decorators.py    # admin/recruteur/candidat_required
│   ├── 📄 views.py         # login/register/profile/password change
│   ├── 📄 urls.py
│   └── 📁 templates/
│       ├── 📄 base.html
│       ├── 📁 accounts/     # login, register, profile
│       └── 📁 registration/ # password_change_form, password_change_done
│
├── 📁 recruitment/
│   ├── 📄 models.py        # Poste, Candidature, Score, Notification
│   ├── 📄 views.py         # PosteListView, PosteDetailView, dashboards
│   ├── 📄 api_views.py     # ViewSets DRF (postes, candidatures, scores)
│   ├── 📄 serializers.py   # DRF
│   ├── 📄 validators.py    # DocumentUploadValidator (PDF/DOC/DOCX)
│   ├── 📄 utils.py         # upload path builder (horodatage)
│   ├── 📄 urls.py          # web + router DRF
│   └── 📁 templates/recruitment/
│       ├── 📄 poste_list.html, poste_detail.html
│       ├── 📄 recruiter_dashboard.html
│       └── 📄 admin_dashboard.html
│
├── 🐳 Dockerfile
├── 🐳 docker-compose.yml
├── 🔧 Makefile
├── 📦 requirements.txt
└── 📖 README.md
```

---

## 🔧 Modèles & Vues (explications)

### 👤 `accounts`
- **Model** `UserProfile(role)` : rattache un rôle à l'utilisateur.
- **Decorators** : `admin_required`, `recruteur_required`, `candidate_required`.
- **Views** : `login`, `logout`, `register` (inscription candidat), `ProfileView`, `PasswordChangeView`.
- **Templates** : `base.html` + pages d'auth & profil (héritent de la base).

### 📝 `recruitment`
- **Models**
  - `Poste(titre, description, competences_requises, date_creation, actif)`
  - `Candidature(candidat, poste, cv_file, lettre_motivation_file, statut, date_soumission)`
  - `Score(application=OneToOne(Candidature), ai_score, ai_recommendation, analyzed_at)`
- **Views (web)**
  - `PosteListView` (liste publique si `actif=True`, sinon tous pour recruteur)
  - `PosteDetailView` + **formulaire de candidature**
  - `RecruiterDashboardView` (liste des candidatures)
  - `AdminDashboardView` (KPIs agrégés)
  - `DownloadCVView` (contrôle d'accès strict)
- **Templates** : liste, détail, dashboards (héritent de `base.html`).

---

## 📡 API REST (DRF)
Base router : `/recruitment/api/`

| Endpoint | Méthodes | Description |
|----------|----------|-------------|
| `/recruitment/api/postes/` | GET, POST | Liste et création des postes |
| `/recruitment/api/postes/{id}/` | GET, PUT, PATCH, DELETE | CRUD d'un poste |
| `/recruitment/api/candidatures/` | GET, POST | Liste et création des candidatures |
| `/recruitment/api/candidatures/{id}/` | GET, PUT, PATCH, DELETE | CRUD d'une candidature |
| `/recruitment/api/scores/` | GET, POST | Liste et création des scores IA |
| `/recruitment/api/scores/{id}/` | GET, PUT, PATCH, DELETE | CRUD d'un score |

### 🔐 Sécurité API
- **Candidat** : accès limité à ses candidatures (IsOwner).
- **Recruteur/Admin** : accès global aux ressources (IsRecruiterOrAdmin).

---

## 🔒 Sécurité & Bonnes pratiques
- ✅ **CSRF** activé, sessions sécurisées (cookies), vues protégées par **login_required** et **décorateurs de rôle**.
- ✅ **Contrôle d'accès fichiers** : seul le propriétaire, un recruteur ou un admin peut télécharger un CV.
- ✅ **Validation des fichiers** (extensions & taille max) côté serveur.
- ⚡ Performances : utiliser `select_related()` / `prefetch_related()` sur les listes volumineuses.

---

## 📊 Tableaux de bord
- **👨‍💼 Recruteur** : liste des candidatures (candidat, poste, statut, date, lien CV).
- **🔧 Admin** : total postes, total candidatures, postes actifs, répartition par statut.
- **📈 Évolution possible** : graphiques (Chart.js/Recharts) pour **statistiques dynamiques**.

---

## 🤖 IA (intégration prévue)
- 📊 Dataset possible : corpus de CVs (Kaggle ou interne anonymisé).
- 🔄 Pipeline type : **prétraitement** (extraction compétences/formation/expériences), **modèle** (BERT/DistilBERT), **métriques** (F1, précision, rappel), **exposition API** (endpoint interne).
- ⚡ Option asynchrone via **Celery** si scoring lourd.

---

## 💻 Exemples de code

### 🏗️ **1. Modèles & Relations**
*Fichier : `app/recruitment/models.py`*

```python
class Poste(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    competences_requises = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    
    def __str__(self):
        return self.titre

class Candidature(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    ]
    
    candidat = models.ForeignKey(User, on_delete=models.CASCADE)
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE)
    cv_file = models.FileField(upload_to=upload_to_cv, validators=[DocumentUploadValidator()])
    lettre_motivation_file = models.FileField(upload_to=upload_to_lettre, validators=[DocumentUploadValidator()])
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_soumission = models.DateTimeField(auto_now_add=True)

class Score(models.Model):
    application = models.OneToOneField(Candidature, on_delete=models.CASCADE)
    ai_score = models.FloatField()
    ai_recommendation = models.TextField()
    analyzed_at = models.DateTimeField(auto_now_add=True)
```

### 🔐 **2. Décorateurs de Rôles**
*Fichier : `app/accounts/decorators.py`*

```python
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès interdit : droits administrateur requis.")
        return redirect('accounts:login')
    return _wrapped_view

def recruteur_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role in ['admin', 'recruiter']:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès interdit : droits recruteur requis.")
        return redirect('accounts:login')
    return _wrapped_view
```

### 🎯 **3. Vues MVT avec Contrôle d'Accès**
*Fichier : `app/recruitment/views.py`*

```python
class PosteDetailView(DetailView):
    model = Poste
    template_name = 'recruitment/poste_detail.html'
    context_object_name = 'poste'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['candidature_form'] = CandidatureForm()
        return context
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Vous devez être connecté pour postuler.")
            return redirect('accounts:login')
        
        # ...existing code for form handling...

@recruteur_required
def download_cv(request, candidature_id):
    candidature = get_object_or_404(Candidature, id=candidature_id)
    
    # Vérification des permissions
    if not (request.user.userprofile.role in ['admin', 'recruiter'] or 
            candidature.candidat == request.user):
        raise Http404("Fichier non trouvé")
    
    file_path = candidature.cv_file.path
    if os.path.exists(file_path):
        # ...existing code for file serving...
```

### 📊 **4. Dashboard avec KPIs**
*Fichier : `app/recruitment/views.py`*

```python
@admin_required
def admin_dashboard(request):
    total_postes = Poste.objects.count()
    total_candidatures = Candidature.objects.count()
    postes_actifs = Poste.objects.filter(actif=True).count()
    
    # Répartition des candidatures par statut
    candidatures_par_statut = Candidature.objects.values('statut').annotate(
        count=Count('statut')
    ).order_by('statut')
    
    context = {
        'total_postes': total_postes,
        'total_candidatures': total_candidatures,
        'postes_actifs': postes_actifs,
        'candidatures_par_statut': candidatures_par_statut,
    }
    return render(request, 'recruitment/admin_dashboard.html', context)
```

### 🔌 **5. API ViewSets avec Permissions**
*Fichier : `app/recruitment/api_views.py`*

```python
class CandidatureViewSet(viewsets.ModelViewSet):
    serializer_class = CandidatureSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'recruiter']:
            return Candidature.objects.select_related('candidat', 'poste').all()
        return Candidature.objects.filter(candidat=user).select_related('poste')
    
    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsAuthenticated, IsCandidateOrAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerRecruiterOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
```

### 🛡️ **6. Validation de Fichiers**
*Fichier : `app/recruitment/validators.py`*

```python
class DocumentUploadValidator:
    allowed_extensions = ['.pdf', '.doc', '.docx']
    max_file_size = 5 * 1024 * 1024  # 5MB
    
    def __call__(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f'Type de fichier non autorisé. Extensions acceptées : {", ".join(self.allowed_extensions)}'
            )
        
        if value.size > self.max_file_size:
            raise ValidationError(
                f'Fichier trop volumineux. Taille maximale : {self.max_file_size // (1024*1024)}MB'
            )
```

### 🔄 **7. Chemins d'Upload Horodatés**
*Fichier : `app/recruitment/utils.py`*

```python
from datetime import datetime
import os

def upload_to_cv(instance, filename):
    timestamp = datetime.now().strftime('%Y/%m/%d')
    username = instance.candidat.username
    return f'cvs/{timestamp}/{username}_{filename}'

def upload_to_lettre(instance, filename):
    timestamp = datetime.now().strftime('%Y/%m/%d')
    username = instance.candidat.username
    return f'lettres/{timestamp}/{username}_{filename}'
```

### 🌐 **8. URLs et Routage**
*Fichier : `app/recruitment/urls.py`*

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

# Router DRF
router = DefaultRouter()
router.register(r'postes', api_views.PosteViewSet, basename='poste')
router.register(r'candidatures', api_views.CandidatureViewSet, basename='candidature')
router.register(r'scores', api_views.ScoreViewSet, basename='score')

app_name = 'recruitment'

urlpatterns = [
    # Web URLs
    path('', views.PosteListView.as_view(), name='poste_list'),
    path('poste/<int:pk>/', views.PosteDetailView.as_view(), name='poste_detail'),
    path('dashboard/recruteur/', views.recruiter_dashboard, name='dashboard_recruteur'),
    path('dashboard/admin/', views.admin_dashboard, name='dashboard_admin'),
    path('download-cv/<int:candidature_id>/', views.download_cv, name='download_cv'),
    
    # API URLs
    path('api/', include(router.urls)),
]
```

---

## 👥 Répartition des tâches
- **🔧🎨 Back-end / Front-end** : Eddy TEROSIER, Samuel TOMEN NANA
- **🧠 IA / Data / Sécurité** : Moussa BAKAYOKO, Carolle TIGNOKPA
- **📋 Gestion de projet** : Trello / GitHub (branches par rôle, PRs, merges).

---

## 🔄 Workflow Git & Conventions
- **🌿 Branches** : `main` (stable), `feature/<nom>`, `fix/<nom>`.
- **💬 Commits** : clairs et réguliers (éviter "update/test"), ex. `feat(recruitment): add ApplicationViewSet`.
- **🔀 PR** : revue par un pair, squash & merge, suppression branche après merge.
- **📝 Issues** : une tâche = une issue, liée à une PR.


<div align="center">

*Made with ❤️ by IPSSI Students*

</div>
