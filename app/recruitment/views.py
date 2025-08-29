from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView, View, CreateView, UpdateView, DeleteView
from accounts.decorators import AdminRequiredMixin, RecruiterRequiredMixin, CandidateRequiredMixin

from accounts.models import UserProfile
from .forms import CandidatureForm, PosteForm, CandidatureStatusForm
from .models import Candidature, Poste, Notification


class PosteListView(ListView):
    model = Poste
    context_object_name = "postes"

    def get_template_names(self):
        return ["recruitment/poste_list.html"]

    def get_queryset(self):
        return Poste.objects.filter(actif=True)


class UserCandidaturesListView(CandidateRequiredMixin, ListView):
    model = Candidature
    template_name = 'recruitment/user_candidatures.html'
    context_object_name = 'candidatures'

    def get_queryset(self):
        return Candidature.objects.filter(candidat=self.request.user).select_related('poste')


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

            # Create notifications for recruiters and admins
            admins_and_recruiters = User.objects.filter(
                profile__role__in=[UserProfile.Roles.ADMIN, UserProfile.Roles.RECRUITER]
            ).distinct()
            for user in admins_and_recruiters:
                Notification.objects.create(
                    user=user,
                    notification_type=Notification.NotificationType.NOUVELLE_CANDIDATURE,
                    message=f"Nouvelle candidature de {candidature.candidat.get_full_name()} pour le poste {candidature.poste.titre}."
                )

            return redirect(self.request.path)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class PosteCreateView(AdminRequiredMixin, CreateView):
    model = Poste
    form_class = PosteForm
    template_name = 'recruitment/poste_form.html'
    success_url = reverse_lazy('recruitment:dashboard_admin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Créer un nouveau poste"
        return context


class PosteUpdateView(AdminRequiredMixin, UpdateView):
    model = Poste
    form_class = PosteForm
    template_name = 'recruitment/poste_form.html'
    success_url = reverse_lazy('recruitment:dashboard_admin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Modifier le poste : {self.object.titre}"
        return context


class PosteDeleteView(AdminRequiredMixin, DeleteView):
    model = Poste
    template_name = 'recruitment/poste_confirm_delete.html'
    success_url = reverse_lazy('recruitment:dashboard_admin')


class CandidatureDetailView(RecruiterRequiredMixin, DetailView):
    model = Candidature
    template_name = 'recruitment/candidature_detail.html'
    context_object_name = 'candidature'


class CandidatureUpdateStatusView(RecruiterRequiredMixin, UpdateView):
    model = Candidature
    form_class = CandidatureStatusForm
    template_name = 'recruitment/candidature_status_form.html'
    
    def get_success_url(self):
        return reverse_lazy('recruitment:candidature_detail', kwargs={'pk': self.object.pk})


class PosteCandidaturesListView(AdminRequiredMixin, ListView):
    model = Candidature
    template_name = 'recruitment/poste_candidatures.html'
    context_object_name = 'candidatures'

    def get_queryset(self):
        self.poste = get_object_or_404(Poste, pk=self.kwargs['poste_id'])
        return Candidature.objects.filter(poste=self.poste)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poste'] = self.poste
        return context


class RecruiterDashboardView(RecruiterRequiredMixin, ListView):
    model = Candidature
    template_name = "recruitment/dashboard_recruteur.html"
    context_object_name = "candidatures"

    def get_queryset(self):
        return Candidature.objects.select_related("candidat", "poste", "score").all()


class AdminDashboardView(AdminRequiredMixin, ListView):
    model = Poste
    template_name = "recruitment/dashboard_admin.html"
    context_object_name = "postes"


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
