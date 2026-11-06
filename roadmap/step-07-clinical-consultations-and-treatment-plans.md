# Step 07: Clinical Consultations & Treatment Plans

## 1. What Previous We Have Done
From **Step 06**:
- Implemented `SkinImage` model with secure dynamic paths and Pillow byte verification.
- Built interactive drag-and-drop upload with client-side preview and resolution checks.
- Integrated doctor image review tools into the appointment workspace.

---

## 2. What We Are Going to Do in This Step

### A. Consultation & Treatment Plan Models (`consultations/models.py`)
Establish the clinical diagnosis, prescription records, and follow-up schedule:
```python
from django.db import models
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
        'accounts.User',
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

    def finalize(self):
        self.is_finalized = True
        self.finalized_at = timezone.now()
        self.appointment.status = 'COMPLETED'
        self.appointment.save()
        self.save()

class TreatmentPlan(TimeStampedModel):
    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name='treatment_plan'
    )
    prescribed_medications = models.TextField(
        help_text="List medications, dosage, frequency, and duration (e.g., 'Hydrocortisone 1% cream, apply twice daily for 5 days')"
    )
    care_instructions = models.TextField(
        help_text="Bathing, moisturizing, trigger avoidance instructions for parents"
    )
    warning_signs = models.TextField(
        default="Seek immediate emergency pediatric care if fever develops (>100.4°F), rapid spreading redness occurs, or child is inconsolable.",
        help_text="Red flags requiring in-person evaluation"
    )
    follow_up_recommended = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_instructions = models.TextField(blank=True)
```

### B. PDF Report Generation (`consultations/services/pdf_generator.py`)
Utilize `xhtml2pdf` to transform a styled HTML template into a PDF consultation report:
- CareNest Clinic Header with logo, date, and report reference ID.
- Patient Demographics: Child's name, age, allergies, blood group.
- Clinical Diagnosis & Severity Level.
- Prescribed Medications & Administration guidelines.
- Parent Care Advice & Warning Signs.
- Verified Physician Signature & License Number block.

### C. Clinician Workspace View (`consultations/views.py`)
- `DoctorConsultationWorkspaceView`:
  - **Left Pane (Context)**: Patient medical history, known allergies badge, uploaded skin images gallery, parent symptom description, and AI triage suggestions.
  - **Right Pane (Clinical Action)**: Combined `ConsultationForm` and `TreatmentPlanForm`.
  - Supports "Save Draft" and "Finalize & Issue Report" actions wrapped in `transaction.atomic()`.

### D. Parent Report View & PDF Download (`consultations/views.py`)
- `ParentConsultationDetailView`: Accessible to the child's parent once `is_finalized=True`.
- `DownloadReportPDFView`: Generates the branded PDF on the fly and streams it as `application/pdf; filename="CareNest_Report_<id>.pdf"`.

---

## 3. Verification (Non-Browser Tests)

### Command 1: Migrations
```bash
python manage.py makemigrations consultations
python manage.py migrate
```
*Expected Output:* `Applying consultations.0001_initial... OK`.

### Command 2: Unit Tests Execution
Create `consultations/tests.py` testing:
1. Finalizing a consultation automatically transitions the related `Appointment.status` to `COMPLETED`.
2. Unfinalized consultation reports are inaccessible to parents (returns 404 or pending notification).
3. Parent A cannot access consultation reports for Parent B's child (verifies HTTP 403 Forbidden).
4. `DownloadReportPDFView` returns HTTP 200 with `Content-Type: application/pdf` and valid binary content (`%PDF-` magic header).

Execute tests:
```bash
python manage.py test consultations
```
*Expected Output:*
```text
Ran 5 tests in 0.65s
OK
```

### Command 3: PDF Generation Assertion via Django Shell
```bash
python manage.py shell -c "
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from consultations.models import Consultation, TreatmentPlan
from consultations.services.pdf_generator import render_consultation_pdf

consultation = Consultation.objects.filter(is_finalized=True).first()
if consultation:
    pdf_bytes = render_consultation_pdf(consultation)
    assert pdf_bytes.startswith(b'%PDF'), 'Generated document is not a valid PDF'
    print(f'Successfully rendered PDF report ({len(pdf_bytes)} bytes).')
else:
    print('Seed an appointment and finalized consultation to verify PDF byte output.')
"
```
*Expected Output:* `Successfully rendered PDF report (...) bytes.`

