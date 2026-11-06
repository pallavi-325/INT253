from django.db import models
from patients.models import TimeStampedModel

class AIAnalysis(TimeStampedModel):
    class AnalysisType(models.TextChoices):
        SYMPTOM_CHAT = 'SYMPTOM_CHAT', 'Pre-consultation Symptom Interview'
        IMAGE_OBSERVATION = 'IMAGE_OBSERVATION', 'Preliminary Skin Vision Analysis'
        CONSULT_SUMMARY = 'CONSULT_SUMMARY', 'Parent-Friendly Consultation Simplification'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Analysis'
        COMPLETED = 'COMPLETED', 'Completed'
        FLAGGED = 'FLAGGED', 'Red Flag Detected – Urgent Clinical Attention'
        FAILED = 'FAILED', 'Analysis Failed'

    child = models.ForeignKey(
        'patients.ChildProfile',
        on_delete=models.CASCADE,
        related_name='ai_analyses'
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_analyses'
    )
    analysis_type = models.CharField(max_length=30, choices=AnalysisType.choices)
    input_context = models.JSONField(default=dict)
    structured_output = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    doctor_reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_analysis_type_display()} for {self.child.full_name} ({self.get_status_display()})"
