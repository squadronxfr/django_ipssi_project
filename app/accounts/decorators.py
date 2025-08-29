from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or
        user.is_staff or
        user.groups.filter(name='admin_group').exists()
    )

def is_recruiter(user):
    return user.is_authenticated and (
        is_admin(user) or
        user.groups.filter(name='recruteur_group').exists()
    )

def is_candidate(user):
    return user.is_authenticated and user.groups.filter(name='candidat_group').exists()

admin_required = user_passes_test(is_admin, login_url='/login/')
recruteur_required = user_passes_test(is_recruiter, login_url='/login/')
candidat_required = user_passes_test(is_candidate, login_url='/login/')

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)

class RecruiterRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_recruiter(self.request.user)

class CandidateRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_candidate(self.request.user)