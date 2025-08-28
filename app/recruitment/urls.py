from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

app_name = 'recruitment'

# Configuration du routeur pour les vues de l'API DRF
router = DefaultRouter()
router.register(r'postes', api_views.PosteViewSet, basename='poste')
router.register(r'candidatures', api_views.CandidatureViewSet, basename='candidature')
router.register(r'scores', api_views.ScoreViewSet, basename='score')

# URLs pour les vues web traditionnelles
urlpatterns = [
    # Vues pour les postes
    path('', views.poste_list_view, name='poste_list'),
    path('postes/<int:pk>/', views.poste_detail_view, name='poste_detail'),

    # Vue pour postuler
    path('postes/<int:pk>/apply/', views.CandidatureCreateView.as_view(), name='candidature_create'),

    # Dashboards
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/recruteur/', views.dashboard_recruteur, name='dashboard_recruteur'),

    # URL sécurisée pour le téléchargement de CV
    path('candidatures/cv/<int:candidature_id>/', views.download_cv, name='download_cv'),

    # URLs de l'API
    path('api/', include(router.urls)),
]
