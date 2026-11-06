import os
import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from .validators import validate_medical_image

def child_skin_image_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    child_id = instance.child_id or 'unknown'
    return os.path.join(
        'skin_images',
        f'child_{child_id}',
        timezone.now().strftime('%Y/%m'),
        unique_name
    )


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ChildProfileQuerySet(models.QuerySet):
    def for_parent(self, user):
        return self.filter(parent=user)


class ChildProfile(TimeStampedModel):
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'
        PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY', 'Prefer not to say'

    class BloodGroup(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        UNKNOWN = 'UNKNOWN', 'Unknown / Not Tested'

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='children',
        limit_choices_to={'role': 'PARENT'}
    )
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    date_of_birth = models.DateField(help_text="Patient must be under 18 years old for pediatric care")
    gender = models.CharField(max_length=20, choices=Gender.choices, default=Gender.PREFER_NOT_TO_SAY)
    blood_group = models.CharField(max_length=15, choices=BloodGroup.choices, default=BloodGroup.UNKNOWN)
    known_allergies = models.TextField(blank=True, help_text="Known drug, topical, or food allergies")
    previous_skin_conditions = models.TextField(blank=True, help_text="e.g., Infantile eczema, cradle cap, viral rash")
    current_medications = models.TextField(blank=True, help_text="Any regular ointments or medications")
    medical_history_notes = models.TextField(blank=True, help_text="Additional pediatric health background notes")

    objects = ChildProfileQuerySet.as_manager()

    class Meta:
        ordering = ['first_name', 'last_name']

    def clean(self):
        super().clean()
        if self.date_of_birth:
            today = timezone.now().date()
            if self.date_of_birth > today:
                raise ValidationError({'date_of_birth': "Date of birth cannot be in the future."})
            
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            if age >= 18:
                raise ValidationError({'date_of_birth': "Patient must be under 18 years old for pediatric care."})

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} (Parent: {self.parent.username})"


class SkinImage(models.Model):
    class BodyPart(models.TextChoices):
        FACE = 'FACE', 'Face / Cheeks / Forehead'
        SCALP = 'SCALP', 'Scalp / Cradle Cap Area'
        TRUNK = 'TRUNK', 'Chest / Back / Abdomen'
        ARMS = 'ARMS', 'Arms / Elbow Folds'
        LEGS = 'LEGS', 'Legs / Knee Folds'
        DIAPER_AREA = 'DIAPER', 'Diaper Area / Groin'
        HANDS_FEET = 'HANDS_FEET', 'Hands / Feet'
        GENERALIZED = 'GENERALIZED', 'Multiple Body Areas / Generalized'

    class ViewType(models.TextChoices):
        OVERVIEW = 'OVERVIEW', 'Overview (showing area in anatomical context)'
        CLOSE_UP = 'CLOSE_UP', 'Close-up (detailed rash/lesion morphology)'

    child = models.ForeignKey(
        ChildProfile,
        on_delete=models.CASCADE,
        related_name='skin_images'
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='skin_images'
    )
    image = models.ImageField(upload_to=child_skin_image_path, validators=[validate_medical_image])
    body_part = models.CharField(max_length=20, choices=BodyPart.choices, default=BodyPart.FACE)
    view_type = models.CharField(max_length=20, choices=ViewType.choices, default=ViewType.CLOSE_UP)
    notes = models.TextField(blank=True, help_text="e.g. Started 3 days ago as small bumps, redder after bathing")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.child.full_name} - {self.get_body_part_display()} ({self.uploaded_at.strftime('%Y-%m-%d')})"
