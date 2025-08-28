from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, FormView, ListView, TemplateView, View

from accounts.decorators import admin_required, recruteur_required
from accounts.models import UserProfile

from .forms import CandidatureForm
from .models import Candidature, Poste


class PosteListView(ListView):
    """Affiche la liste des postes. Différente pour les candidats et les recruteurs."""

    model = Poste
    context_object_name = "postes"

    def get_template_names(self):
        """Utilise un template différent si l'utilisateur est un recruteur."""
        if hasattr(self.request.user, "profile") and self.request.user.profile.role == UserProfile.Roles.RECRUITER:
            return ["recruitment/poste_list_recruteur.html"]
        return ["recruitment/poste_list.html"]

    def get_queryset(self):
        """Les candidats ne voient que les postes actifs."""
        if hasattr(self.request.user, "profile") and self.request.user.profile.role == UserProfile.Roles.RECRUITER:
            return Poste.objects.all()  # Les recruteurs voient tout
        return Poste.objects.filter(actif=True)


class PosteDetailView(DetailView, FormView):
    """Affiche les détails d'un poste et le formulaire de candidature."""

    model = Poste
    template_name = "recruitment/poste_detail.html"
    context_object_name = "poste"
    form_class = CandidatureForm

    def get_success_url(self):
        return reverse_lazy("recruitment:poste-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["existing_candidature"] = Candidature.objects.filter(
                poste=self.object, candidat=self.request.user
            ).first()
        return context

    def form_valid(self, form):
        """Crée une candidature si le formulaire est valide."""
        if not self.request.user.is_authenticated:
            return redirect("accounts:login")

        poste = self.get_object()
        candidature = form.save(commit=False)
        candidature.candidat = self.request.user
        candidature.poste = poste
        candidature.save()
        # Rediriger avec un message de succès (peut être géré avec le framework de messages)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        """Gère la soumission du formulaire."""
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


@method_decorator(recruteur_required, name="dispatch")
class RecruiterDashboardView(ListView):
    """Dashboard pour les recruteurs, liste les candidatures."""

    model = Candidature
    template_name = "recruitment/recruiter_dashboard.html"
    context_object_name = "candidatures"

    def get_queryset(self):
        """Affiche les candidatures avec les scores."""
        return Candidature.objects.select_related("candidat", "poste", "score").all()


@method_decorator(admin_required, name="dispatch")
class AdminDashboardView(TemplateView):
    """Dashboard pour les administrateurs."""

    template_name = "recruitment/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_postes"] = Poste.objects.count()
        context["total_candidatures"] = Candidature.objects.count()
        context["postes_actifs"] = Poste.objects.filter(actif=True).count()
        context["candidatures_par_statut"] = (
            Candidature.objects.values("statut").annotate(count=Count("statut")).order_by()
        )
        return context


class DownloadCVView(LoginRequiredMixin, View):
    """Vue sécurisée pour le téléchargement des CV."""

    def get(self, request, candidature_id):
        candidature = get_object_or_404(Candidature, pk=candidature_id)
        user = request.user

        # Seuls l'admin, le recruteur ou le candidat lui-même peuvent voir le CV
        is_admin = hasattr(user, "profile") and user.profile.role == UserProfile.Roles.ADMIN
        is_recruiter = hasattr(user, "profile") and user.profile.role == UserProfile.Roles.RECRUITER
        is_owner = candidature.candidat == user

        if not (is_admin or is_recruiter or is_owner):
            return HttpResponseForbidden("Vous n'avez pas la permission de voir ce fichier.")

        if not candidature.cv_file:
            raise Http404("Fichier CV non trouvé.")

        # Utiliser FileResponse pour servir le fichier
        try:
            return FileResponse(candidature.cv_file.open("rb"), as_attachment=True)
        except FileNotFoundError:
            raise Http404("Fichier non trouvé sur le disque.")