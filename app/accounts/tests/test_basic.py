# -*- coding: utf-8 -*-
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group

from accounts.models import UserProfile
from accounts import permissions as perms


class TestAccountsBasic(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name=perms.ADMIN_GROUP)
        Group.objects.get_or_create(name=perms.RECRUITER_GROUP)
        Group.objects.get_or_create(name=perms.CANDIDATE_GROUP)

        self.admin = User.objects.create_user(username="adminu", password="Adm1nPassw0rd!")
        self.admin.is_staff = True
        self.admin.save()
        UserProfile.objects.create(user=self.admin, role=UserProfile.Roles.ADMIN)

        self.recruiter = User.objects.create_user(username="recu", password="RecPassw0rd!")
        UserProfile.objects.create(user=self.recruiter, role=UserProfile.Roles.RECRUITER)

        self.candidate = User.objects.create_user(username="canu", password="CandPassw0rd!")
        UserProfile.objects.create(user=self.candidate, role=UserProfile.Roles.CANDIDATE)

    def test_user_roles_and_groups_assigned(self):
        self.assertTrue(self.admin.groups.filter(name=perms.ADMIN_GROUP).exists())
        self.assertTrue(self.recruiter.groups.filter(name=perms.RECRUITER_GROUP).exists())
        self.assertTrue(self.candidate.groups.filter(name=perms.CANDIDATE_GROUP).exists())

    def test_decorators_access(self):
        admin_url = reverse('only_admin')
        rec_url = reverse('recruiter_or_admin')
        cand_url = reverse('only_candidate')

        # anonymous
        self.assertEqual(self.client.get(admin_url).status_code, 403)
        self.assertEqual(self.client.get(rec_url).status_code, 403)
        self.assertEqual(self.client.get(cand_url).status_code, 403)

        # admin
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(admin_url).status_code, 200)
        self.assertEqual(self.client.get(rec_url).status_code, 200)
        self.assertEqual(self.client.get(cand_url).status_code, 403)

        # recruiter
        self.client.force_login(self.recruiter)
        self.assertEqual(self.client.get(admin_url).status_code, 403)
        self.assertEqual(self.client.get(rec_url).status_code, 200)
        self.assertEqual(self.client.get(cand_url).status_code, 403)

        # candidate
        self.client.force_login(self.candidate)
        self.assertEqual(self.client.get(admin_url).status_code, 403)
        self.assertEqual(self.client.get(rec_url).status_code, 403)
        self.assertEqual(self.client.get(cand_url).status_code, 200)

    def test_login_and_logout(self):
        login_url = reverse('login')
        profile_url = reverse('profile')
        logout_url = reverse('logout')

        resp = self.client.post(login_url, {"username": "canu", "password": "CandPassw0rd!"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn(profile_url, resp.headers.get('Location', ''))

        resp2 = self.client.post(logout_url)
        self.assertEqual(resp2.status_code, 302)

        resp3 = self.client.post(login_url, {"username": "adminu", "password": "Adm1nPassw0rd!"})
        self.assertEqual(resp3.status_code, 302)
        self.assertTrue('/admin/' in resp3.headers.get('Location', '') or profile_url in resp3.headers.get('Location', ''))

    def test_view_permissions(self):
        profile_url = reverse('profile')
        register_url = reverse('register')

        resp = self.client.get(profile_url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.headers.get('Location', ''))

        self.assertEqual(self.client.get(register_url).status_code, 200)

        self.client.force_login(self.candidate)
        resp2 = self.client.get(register_url)
        self.assertEqual(resp2.status_code, 302)
        self.assertIn(profile_url, resp2.headers.get('Location', ''))
