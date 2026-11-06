from django.db import models
from django.conf import settings
from django.utils import timezone
from patients.models import TimeStampedModel

class Consultation(TimeStampedModel):
    class Severity(models.TextChoices):
        MILD = 'MILD', 'Mild'
        MODERATE = 'MODERATE', 'Moderate'
        SEVERE = 'SEVERE', 'Severe'

    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='consultation'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='authored_consultations',
        limit_choices_to={'role': 'DOCTOR'}
    )
    clinical_assessment = models.TextField(help_text="Primary clinical diagnosis and examination findings")
    differential_diagnosis = models.TextField(blank=True, help_text="Alternative diagnoses considered")
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MILD)
    clinical_notes = models.TextField(blank=True, help_text="Confidential clinician notes (not shown to parent)")
    is_finalized = models.BooleanField(default=False, help_text="Once finalized, report is visible to parent")
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def finalize(self):
        self.is_finalized = True
        self.finalized_at = timezone.now()
        self.save()
        self.appointment.status = 'COMPLETED'
        self.appointment.save()

    def __str__(self):
        return f"Consultation for Case #{self.appointment.id} by Dr. {self.doctor.username}"


class TreatmentPlan(TimeStampedModel):
    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name='treatment_plan'
    )
    prescribed_medications = models.TextField(
        help_text="Prescribed ointments, dosage, frequency, and duration (e.g. Hydrocortisone 1% cream, apply twice daily for 5 days)"
    )
    care_instructions = models.TextField(
        help_text="Bathing, moisturizing, trigger avoidance instructions for parents"
    )
    warning_signs = models.TextField(
        default="Seek immediate in-person medical care if child develops high fever (>100.4°F), rapid spreading redness, or pustules.",
        help_text="Red flags requiring in-person evaluation"
    )
    follow_up_recommended = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_instructions = models.TextField(blank=True)

    def __str__(self):
        return f"Treatment Plan for Consultation #{self.consultation.id}"
