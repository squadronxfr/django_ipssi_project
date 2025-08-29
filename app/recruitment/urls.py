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
    path('', views.PosteListView.as_view(), name='poste_list'),
    path('postes/<int:pk>/', views.PosteDetailView.as_view(), name='poste_detail'),

    # Vue pour postuler (utilise la même vue que le détail)
    path('postes/<int:pk>/apply/', views.PosteDetailView.as_view(), name='candidature_create'),

    # Dashboards
    path('dashboard/admin/', views.AdminDashboardView.as_view(), name='dashboard_admin'),
    path('dashboard/recruteur/', views.RecruiterDashboardView.as_view(), name='dashboard_recruteur'),

    # URL sécurisée pour le téléchargement de CV
    path('candidatures/cv/<int:candidature_id>/', views.DownloadCVView.as_view(), name='download_cv'),

    # URLs de l'API
    path('api/', include(router.urls)),
]
