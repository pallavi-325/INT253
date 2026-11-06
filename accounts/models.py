from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    class Role(models.TextChoices):
        PARENT = 'PARENT', 'Parent / Guardian'
        DOCTOR = 'DOCTOR', 'Pediatric Dermatologist'
        ADMIN = 'ADMIN', 'Hospital Administrator'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.PARENT,
        help_text="Designates the user persona within the telemedicine platform."
    )
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    def is_parent(self):
        return self.role == self.Role.PARENT

    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    license_number = models.CharField(max_length=50, unique=True, help_text="Medical board certification or license number")
    specialization = models.CharField(
        max_length=120,
        default="Pediatric Dermatology",
        help_text="e.g. Infantile Hemangiomas, Atopic Dermatitis, General Pediatric Dermatology"
    )
    experience_years = models.PositiveIntegerField(default=1)
    bio = models.TextField(blank=True, help_text="Brief background and clinical approach")
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)
    is_verified = models.BooleanField(default=False, help_text="Hospital admin verification status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialization}"


class ParentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parent_profile'
    )
    emergency_contact = models.CharField(max_length=20, blank=True)
    preferred_language = models.CharField(max_length=50, default="English")
    consent_to_telehealth = models.BooleanField(default=True, help_text="Consent for teledermatology evaluation of minors")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Parent: {self.user.get_full_name() or self.user.username}"
