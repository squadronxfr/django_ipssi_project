from django.contrib import admin, messages
from django.db.models import QuerySet, Count
from django.http import HttpRequest
from django.utils.html import format_html

from accounts.models import UserProfile
from .models import Poste, Candidature, Score, Notification


class BaseRecruitmentAdmin(admin.ModelAdmin):
    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'profile'):
            return request.user.profile.role in [UserProfile.Roles.ADMIN, UserProfile.Roles.RECRUITER]
        return False

    def has_module_permission(self, request: HttpRequest) -> bool:
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'profile'):
            return request.user.profile.role in [UserProfile.Roles.ADMIN, UserProfile.Roles.RECRUITER]
        return False

    has_add_permission = has_view_permission
    has_change_permission = has_view_permission
    has_delete_permission = has_view_permission


@admin.register(Poste)
class PosteAdmin(BaseRecruitmentAdmin):
    list_display = ('titre', 'actif', 'date_creation', 'nombre_candidatures')
    list_filter = ('actif',)
    search_fields = ('titre', 'description', 'competences_requises')
    ordering = ('-date_creation',)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.annotate(candidatures_count=Count('candidatures'))

    @admin.display(description="Nb. Candidatures", ordering='candidatures_count')
    def nombre_candidatures(self, obj: Poste) -> int:
        return obj.candidatures_count


class ScoreInline(admin.StackedInline):
    model = Score
    extra = 0
    readonly_fields = ('score_ia', 'recommandation_ia', 'date_analyse')
    can_delete = False

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(Candidature)
class CandidatureAdmin(BaseRecruitmentAdmin):
    list_display = ('candidat', 'poste', 'statut', 'date_soumission', 'apercu_cv')
    list_filter = ('statut', 'poste__titre')
    search_fields = ('candidat__username', 'candidat__email', 'poste__titre')
    readonly_fields = ('candidat', 'poste', 'date_soumission')
    ordering = ('-date_soumission',)
    actions = ['marquer_en_revue', 'marquer_acceptee', 'marquer_refusee']
    inlines = [ScoreInline]

    @admin.display(description="CV")
    def apercu_cv(self, obj: Candidature) -> str:
        if obj.cv_file:
            return format_html('<a href="{url}" target="_blank">Voir CV</a>', url=obj.cv_file.url)
        return "N/A"

    @admin.action(description="Marquer comme 'En revue'")
    def marquer_en_revue(self, request: HttpRequest, queryset: QuerySet):
        updated = queryset.update(statut=Candidature.Statuts.EN_REVUE)
        self.message_user(request, f"{updated} candidatures mises à jour.", messages.SUCCESS)

    @admin.action(description="Marquer comme 'Acceptée'")
    def marquer_acceptee(self, request: HttpRequest, queryset: QuerySet):
        updated = queryset.update(statut=Candidature.Statuts.ACCEPTEE)
        self.message_user(request, f"{updated} candidatures acceptées.", messages.SUCCESS)

    @admin.action(description="Marquer comme 'Refusée'")
    def marquer_refusee(self, request: HttpRequest, queryset: QuerySet):
        updated = queryset.update(statut=Candidature.Statuts.REFUSEE)
        self.message_user(request, f"{updated} candidatures refusées.", messages.SUCCESS)


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('candidature', 'score_ia', 'date_analyse')
    readonly_fields = [f.name for f in Score._meta.fields]
    search_fields = ('candidature__candidat__username', 'candidature__poste__titre')

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'notification_type', 'user__username')
    search_fields = ('user__username', 'message')
    actions = ['marquer_comme_lu']

    @admin.action(description="Marquer les notifications sélectionnées comme lues")
    def marquer_comme_lu(self, request: HttpRequest, queryset: QuerySet):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notifications marquées comme lues.", messages.SUCCESS)

    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        return request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == UserProfile.Roles.ADMIN)

    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == UserProfile.Roles.ADMIN)

    has_add_permission = has_view_permission
    has_change_permission = has_view_permission
    has_delete_permission = has_view_permission