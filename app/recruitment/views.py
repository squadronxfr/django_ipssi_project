from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView, View
from accounts.decorators import AdminRequiredMixin, RecruiterRequiredMixin

from accounts.models import UserProfile
from .forms import CandidatureForm
from .models import Candidature, Poste


class PosteListView(ListView):
    model = Poste
    context_object_name = "postes"

    def get_template_names(self):
        return ["recruitment/poste_list.html" if self._is_recruiter() else "recruitment/poste_list.html"]

    def get_queryset(self):
        return Poste.objects.all() if self._is_recruiter() else Poste.objects.filter(actif=True)

    def _is_recruiter(self):
        return (hasattr(self.request.user, 'profile') and 
                self.request.user.profile.role == UserProfile.Roles.RECRUITER)


class PosteDetailView(DetailView):
    model = Poste
    template_name = "recruitment/poste_detail.html"
    context_object_name = "poste"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CandidatureForm()
        
        if self.request.user.is_authenticated:
            context["existing_candidature"] = Candidature.objects.filter(
                poste=self.object, candidat=self.request.user
            ).first()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        form = CandidatureForm(request.POST, request.FILES)
        if form.is_valid():
            candidature = form.save(commit=False)
            candidature.candidat = request.user
            candidature.poste = self.object
            candidature.save()
            return redirect(self.request.path)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class RecruiterDashboardView(ListView):
    model = Candidature
    template_name = "recruitment/dashboard_recruteur.html"
    context_object_name = "candidatures"

    def get_queryset(self):
        return Candidature.objects.select_related("candidat", "poste", "score").all()


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "recruitment/dashboard_admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        candidature_stats = Candidature.objects.values('statut').annotate(count=Count('statut'))
        
        context.update({
            'total_postes': Poste.objects.count(),
            'total_candidatures': Candidature.objects.count(),
            'postes_actifs': Poste.objects.filter(actif=True).count(),
            'candidatures_par_statut': list(candidature_stats)
        })
        return context


class DownloadCVView(LoginRequiredMixin, View):
    def get(self, request, candidature_id):
        candidature = get_object_or_404(Candidature, pk=candidature_id)
        user = request.user

        is_admin = hasattr(user, "profile") and user.profile.role == UserProfile.Roles.ADMIN
        is_recruiter = hasattr(user, "profile") and user.profile.role == UserProfile.Roles.RECRUITER
        is_owner = candidature.candidat == user

        if not (is_admin or is_recruiter or is_owner):
            return HttpResponseForbidden("Vous n'avez pas la permission de voir ce fichier.")

        if not candidature.cv_file:
            raise Http404("Fichier CV non trouvé.")

        try:
            return FileResponse(candidature.cv_file.open("rb"), as_attachment=True)
        except FileNotFoundError:
            raise Http404("Fichier non trouvé sur le disque.")