from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from patients.models import TimeStampedModel

class AppointmentQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(
            scheduled_date__gte=timezone.now().date(),
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('scheduled_date', 'scheduled_time')

    def for_user(self, user):
        if user.is_doctor():
            return self.filter(doctor=user)
        return self.filter(parent=user)


class Appointment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        IN_REVIEW = 'IN_REVIEW', 'Clinical Review In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class Severity(models.TextChoices):
        MILD = 'MILD', 'Mild – Localized / Minor discomfort'
        MODERATE = 'MODERATE', 'Moderate – Spreading / Itching disturbing sleep'
        URGENT = 'URGENT', 'Urgent – Rapidly changing / Discomfort (Non-emergency)'

    child = models.ForeignKey(
        'patients.ChildProfile',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parent_appointments'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'DOCTOR'}
    )
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    chief_complaint = models.CharField(max_length=255, help_text="e.g. Red scaling rash around elbows and cheeks")
    duration_of_symptoms = models.CharField(max_length=100, help_text="e.g. 5 days, 3 weeks")
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MILD)
    cancellation_reason = models.TextField(blank=True)

    objects = AppointmentQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'scheduled_date', 'scheduled_time'],
                condition=~models.Q(status='CANCELLED'),
                name='unique_doctor_active_timeslot'
            )
        ]
        ordering = ['-scheduled_date', '-scheduled_time']

    def clean(self):
        super().clean()
        if self.scheduled_date and self.scheduled_date < timezone.now().date():
            raise ValidationError({'scheduled_date': "Appointments cannot be booked for past dates."})
        if hasattr(self, 'child') and hasattr(self, 'parent'):
            if self.child.parent != self.parent:
                raise ValidationError({'child': "Selected child does not belong to your account."})

    def __str__(self):
        return f"{self.child.full_name} with Dr. {self.doctor.get_full_name() or self.doctor.username} on {self.scheduled_date}"
