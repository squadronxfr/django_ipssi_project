from django.urls import path
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth import views as auth_views

from . import views
from .decorators import admin_required, recruteur_required, candidat_required


def home(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return redirect('login')


@admin_required
def admin_only_view(request):
    return HttpResponse("admin ok")


@recruteur_required
def recruiter_or_admin_view(request):
    return HttpResponse("recruiter ok")


@candidat_required
def candidate_only_view(request):
    return HttpResponse("candidate ok")


urlpatterns = [
    path('', home, name='home'),
    path('login/', views.RoleBasedLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.CandidateSignUpView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('password-change/', views.PasswordChangeViewCBV.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('only-admin/', admin_only_view, name='only_admin'),
    path('recruiter-or-admin/', recruiter_or_admin_view, name='recruiter_or_admin'),
    path('only-candidate/', candidate_only_view, name='only_candidate'),
]