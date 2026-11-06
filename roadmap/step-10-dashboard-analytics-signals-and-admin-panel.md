# Step 10: Dashboard Analytics, Signals & Admin Panel

## 1. What Previous We Have Done
From **Step 09**:
- Multimodal skin image vision analysis with clinician decision-support integration.
- AI consultation notes simplification with doctor review and approval gate.
- Verified medical disclaimer compliance and offline fallback reliability.

---

## 2. What We Are Going to Do in This Step

### A. System Lifecycle Signals (`appointments/signals.py`)
Decouple notification and audit logging using Django signals:
- On `post_save` of `Appointment`:
  - When status transitions to `CONFIRMED`, generate a notification record for the parent.
  - When status transitions to `COMPLETED`, alert the parent that their consultation report is ready.
  - Record audit log entry in database for clinical traceability.

```python
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from appointments.models import Appointment

@receiver(pre_save, sender=Appointment)
def track_status_change(sender, instance, **kwargs):
    if instance.pk:
        previous = Appointment.objects.get(pk=instance.pk)
        instance._previous_status = previous.status
    else:
        instance._previous_status = None

@receiver(post_save, sender=Appointment)
def handle_appointment_lifecycle(sender, instance, created, **kwargs):
    if created:
        # Trigger doctor notification for new booking
        pass
    elif hasattr(instance, '_previous_status') and instance._previous_status != instance.status:
        # Trigger parent status change alert
        pass
```

### B. Custom Context Processors (`config/context_processors.py`)
Inject role flags and notification badges seamlessly into every template:
```python
def telemed_global_context(request):
    if not request.user.is_authenticated:
        return {'is_parent': False, 'is_doctor': False, 'unread_notifications_count': 0}
    
    return {
        'is_parent': request.user.is_parent(),
        'is_doctor': request.user.is_doctor(),
        'active_child_count': request.user.children.count() if request.user.is_parent() else 0,
        'platform_name': 'CareNest Pediatric Teledermatology',
    }
```
Register in `config/settings.py` under `TEMPLATES['OPTIONS']['context_processors']`.

### C. Interactive Chart.js Dashboards with Dynamic Dark/Light Theming
- **Doctor Metrics Panel** (`templates/appointments/doctor_dashboard.html`):
  - Weekly consultation volume line chart.
  - Diagnosis category distribution doughnut chart.
  - Dynamic JavaScript hook listening to custom `themeChanged` event to switch Chart.js grid and label colors:
    - Light Mode: Grid `#E2E8F0`, Labels `#475569`
    - Dark Mode: Grid `#334155`, Labels `#94A3B8`
- **Parent Health Tracker** (`templates/patients/parent_dashboard.html`):
  - Visual timeline of past appointments and treatment milestones.

### D. Advanced Django Admin Customization (`admin.py`)
Configure enterprise-grade admin interfaces:
- **`accounts/admin.py`**:
  - `UserAdmin` customized with role filters and custom action "Verify Doctor License".
- **`patients/admin.py`**:
  - TabularInline for `SkinImage` inside `ChildProfileAdmin`.
- **`appointments/admin.py`**:
  - `date_hierarchy = 'scheduled_date'`, search by child name, parent email, doctor name.
  - Color-coded status badges in `list_display`.
- **`consultations/admin.py`**:
  - `TreatmentPlanInline` directly editable within `ConsultationAdmin`.

---

## 3. Verification (Non-Browser Tests)

### Command 1: Unit Tests for Signals & Context Processors
Create `appointments/tests/test_signals.py` testing:
1. Updating appointment status triggers lifecycle signals.
2. Context processor injects `is_parent`, `is_doctor`, and `platform_name` into request context.
3. Django admin urls (`/admin/`) return HTTP 200 for staff superuser.

Run tests:
```bash
python manage.py test appointments.tests.test_signals
```
*Expected Output:*
```text
Ran 3 tests in 0.35s
OK
```

### Command 2: Context Processor Assertion via Django Shell
```bash
python manage.py shell -c "
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from config.context_processors import telemed_global_context

User = get_user_model()
doctor = User.objects.filter(role=User.Role.DOCTOR).first()

rf = RequestFactory()
request = rf.get('/')
request.user = doctor

context = telemed_global_context(request)
assert context['is_doctor'] == True
assert context['is_parent'] == False
assert 'platform_name' in context
print('Global context processor verified successfully:', context)
"
```
*Expected Output:* `Global context processor verified successfully: ...`

