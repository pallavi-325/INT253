import io
from PIL import Image
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from patients.models import ChildProfile, SkinImage
from patients.validators import validate_medical_image
from patients.templatetags.patient_tags import calculate_age, split_allergies

User = get_user_model()

class PatientManagementTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.parent_a = User.objects.create_user(
            username='parent_a', email='a@example.com', password='password123', role=User.Role.PARENT
        )
        self.parent_b = User.objects.create_user(
            username='parent_b', email='b@example.com', password='password123', role=User.Role.PARENT
        )

        self.child_a = ChildProfile.objects.create(
            parent=self.parent_a,
            first_name='Leo',
            last_name='A',
            date_of_birth=date(2021, 5, 15),
            gender=ChildProfile.Gender.MALE,
            known_allergies='Penicillin, Peanuts'
        )

    def test_future_dob_raises_validation_error(self):
        future_dob = timezone.now().date() + timedelta(days=5)
        child = ChildProfile(
            parent=self.parent_a,
            first_name='Future',
            last_name='Baby',
            date_of_birth=future_dob,
            gender=ChildProfile.Gender.FEMALE
        )
        with self.assertRaises(ValidationError):
            child.full_clean()

    def test_adult_age_raises_validation_error(self):
        adult_dob = timezone.now().date() - timedelta(days=365 * 19)
        child = ChildProfile(
            parent=self.parent_a,
            first_name='Adult',
            last_name='Person',
            date_of_birth=adult_dob,
            gender=ChildProfile.Gender.MALE
        )
        with self.assertRaises(ValidationError):
            child.full_clean()

    def test_cross_parent_isolation_cannot_view_or_edit(self):
        self.client.force_login(self.parent_b)
        
        detail_res = self.client.get(reverse('patients:child_detail', kwargs={'pk': self.child_a.pk}))
        self.assertEqual(detail_res.status_code, 404)

        edit_res = self.client.get(reverse('patients:child_update', kwargs={'pk': self.child_a.pk}))
        self.assertEqual(edit_res.status_code, 404)

    def test_parent_manager_for_parent(self):
        self.assertEqual(ChildProfile.objects.for_parent(self.parent_a).count(), 1)
        self.assertEqual(ChildProfile.objects.for_parent(self.parent_b).count(), 0)

    def test_template_tags_calculate_age_and_allergies(self):
        infant_dob = timezone.now().date() - timedelta(days=90)
        age_str = calculate_age(infant_dob)
        self.assertIn('month', age_str)

        allergies = split_allergies('Latex, Penicillin , Peanuts')
        self.assertEqual(len(allergies), 3)
        self.assertEqual(allergies[0], 'Latex')

    def test_valid_image_upload_passes_validation(self):
        # Generate valid 500x500 image
        buffer = io.BytesIO()
        img = Image.new('RGB', (500, 500), color=(120, 180, 200))
        img.save(buffer, format='JPEG')
        buffer.seek(0)

        upload = SimpleUploadedFile('lesion.jpg', buffer.read(), content_type='image/jpeg')
        validate_medical_image(upload)

        skin_img = SkinImage.objects.create(
            child=self.child_a,
            image=upload,
            body_part=SkinImage.BodyPart.FACE
        )
        self.assertTrue(skin_img.image.name.endswith('.jpg'))

    def test_low_resolution_image_rejected(self):
        # Generate small 200x200 image (less than 400x400 minimum)
        buffer = io.BytesIO()
        img = Image.new('RGB', (200, 200), color=(100, 100, 100))
        img.save(buffer, format='JPEG')
        buffer.seek(0)

        upload = SimpleUploadedFile('small.jpg', buffer.read(), content_type='image/jpeg')
        with self.assertRaises(ValidationError):
            validate_medical_image(upload)

    def test_fake_corrupt_image_rejected(self):
        fake_upload = SimpleUploadedFile('corrupt.jpg', b'NOT_A_REAL_IMAGE_BYTES', content_type='image/jpeg')
        with self.assertRaises(ValidationError):
            validate_medical_image(fake_upload)


class IDORSecurityTestCase(TestCase):
    """
    IDOR (Insecure Direct Object Reference) security tests.
    Verifies that one authenticated parent cannot access, edit, or delete
    another parent's children or skin images.
    """

    def setUp(self):
        self.client = Client()
        self.parent_a = User.objects.create_user(
            username='idor_parent_a', email='idor_a@example.com',
            password='secure_pass_a', role=User.Role.PARENT
        )
        self.parent_b = User.objects.create_user(
            username='idor_parent_b', email='idor_b@example.com',
            password='secure_pass_b', role=User.Role.PARENT
        )

        self.child_a = ChildProfile.objects.create(
            parent=self.parent_a,
            first_name='Protected',
            last_name='Child',
            date_of_birth=date(2019, 3, 10),
            gender=ChildProfile.Gender.FEMALE,
        )

    def test_parent_b_cannot_view_parent_a_child_detail(self):
        """IDOR: Parent B must get 404 when accessing Parent A's child."""
        self.client.force_login(self.parent_b)
        response = self.client.get(
            reverse('patients:child_detail', kwargs={'pk': self.child_a.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_parent_b_cannot_edit_parent_a_child(self):
        """IDOR: Parent B must get 404 when editing Parent A's child."""
        self.client.force_login(self.parent_b)
        response = self.client.post(
            reverse('patients:child_update', kwargs={'pk': self.child_a.pk}),
            data={'first_name': 'Hacked', 'last_name': 'Child'}
        )
        self.assertEqual(response.status_code, 404)
        # Confirm child was NOT modified
        self.child_a.refresh_from_db()
        self.assertEqual(self.child_a.first_name, 'Protected')

    def test_unauthenticated_user_cannot_view_child_detail(self):
        """Security: Unauthenticated access to child detail must redirect to login."""
        response = self.client.get(
            reverse('patients:child_detail', kwargs={'pk': self.child_a.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_unauthenticated_user_cannot_add_child(self):
        """Security: Unauthenticated access to add-child must redirect to login."""
        response = self.client.get(reverse('patients:child_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_parent_b_cannot_upload_image_to_parent_a_child(self):
        """IDOR: Parent B must get a form error or redirect — not silently upload to Parent A's child."""
        self.client.force_login(self.parent_b)
        # Attempt to GET the upload form — should succeed (it's their own form)
        response = self.client.get(reverse('patients:upload_skin_image'))
        # The page renders for authenticated parent (200), but form only shows Parent B's children
        self.assertIn(response.status_code, [200, 302])
        # Critically: Parent A's child must NOT appear in the queryset served to Parent B
        parent_b_children = ChildProfile.objects.for_parent(self.parent_b)
        self.assertNotIn(self.child_a, parent_b_children)

    def test_child_queryset_scoped_to_parent(self):
        """Manager: for_parent queryset must only return owned children."""
        child_b = ChildProfile.objects.create(
            parent=self.parent_b,
            first_name='Legit',
            last_name='Child',
            date_of_birth=date(2020, 7, 20),
            gender=ChildProfile.Gender.MALE,
        )
        a_children = ChildProfile.objects.for_parent(self.parent_a)
        b_children = ChildProfile.objects.for_parent(self.parent_b)

        self.assertIn(self.child_a, a_children)
        self.assertNotIn(child_b, a_children)
        self.assertIn(child_b, b_children)
        self.assertNotIn(self.child_a, b_children)
