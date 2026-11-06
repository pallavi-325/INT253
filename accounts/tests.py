import os
from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory

from accounts.models import DoctorProfile, ParentProfile
from accounts.permissions import role_required, RoleRequiredMixin

User = get_user_model()

class AccountsAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Create test parent
        self.parent_user = User.objects.create_user(
            username='parent_jane',
            email='jane@example.com',
            password='password123',
            role=User.Role.PARENT,
            first_name='Jane',
            last_name='Doe'
        )

        # Create test doctor
        self.doctor_user = User.objects.create_user(
            username='dr_smith',
            email='dr.smith@example.com',
            password='password123',
            role=User.Role.DOCTOR,
            first_name='John',
            last_name='Smith'
        )

    def test_parent_profile_auto_created_via_signal(self):
        self.assertTrue(hasattr(self.parent_user, 'parent_profile'))
        self.assertIsInstance(self.parent_user.parent_profile, ParentProfile)
        self.assertTrue(self.parent_user.is_parent())
        self.assertFalse(self.parent_user.is_doctor())

    def test_doctor_profile_auto_created_via_signal(self):
        self.assertTrue(hasattr(self.doctor_user, 'doctor_profile'))
        self.assertIsInstance(self.doctor_user.doctor_profile, DoctorProfile)
        self.assertTrue(self.doctor_user.is_doctor())
        self.assertFalse(self.doctor_user.is_parent())

    def test_role_based_redirect_for_parent(self):
        self.client.force_login(self.parent_user)
        response = self.client.get(reverse('accounts:dashboard_redirect'))
        self.assertEqual(response.status_code, 302)
        # Should redirect towards patients dashboard (URL is /patients/dashboard/)
        redirect_url = response.url if hasattr(response, 'url') else ''
        self.assertTrue(
            '/parent/' in redirect_url or '/patients/' in redirect_url,
            f"Expected parent redirect, got: {redirect_url}"
        )

    def test_role_based_redirect_for_doctor(self):
        self.client.force_login(self.doctor_user)
        response = self.client.get(reverse('accounts:dashboard_redirect'))
        self.assertEqual(response.status_code, 302)
        # Should redirect towards doctor dashboard
        self.assertIn('/doctor/', response.url if hasattr(response, 'url') else '')

    def test_role_required_decorator_blocks_unauthorized(self):
        @role_required(['DOCTOR'])
        def dummy_doctor_view(request):
            return HttpResponse("Doctor Only Area")

        # Parent attempting to access doctor-only view
        req = self.factory.get('/dummy-doctor-route/')
        req.user = self.parent_user

        with self.assertRaises(PermissionDenied):
            dummy_doctor_view(req)

        # Doctor accessing doctor-only view
        req.user = self.doctor_user
        res = dummy_doctor_view(req)
        self.assertEqual(res.status_code, 200)

    def test_login_and_logout_views(self):
        login_url = reverse('accounts:login')
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

        # Perform login
        post_response = self.client.post(login_url, {
            'username': 'parent_jane',
            'password': 'password123'
        })
        self.assertEqual(post_response.status_code, 302)

    def test_parent_registration_view(self):
        url = reverse('accounts:register_parent')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'accounts/register_parent.html')

        post_data = {
            'username': 'newparent',
            'first_name': 'Mary',
            'last_name': 'Johnson',
            'email': 'mary.j@example.com',
            'phone_number': '555-123-4567',
            'emergency_contact': '555-987-6543',
            'consent_to_telehealth': 'on',
            'password1': 'StrongP@ssw0rd123',
            'password2': 'StrongP@ssw0rd123',
        }
        post_res = self.client.post(url, post_data)
        self.assertEqual(post_res.status_code, 302)
        created_user = User.objects.get(username='newparent')
        self.assertEqual(created_user.role, User.Role.PARENT)
        self.assertTrue(hasattr(created_user, 'parent_profile'))
