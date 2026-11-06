# Step 05: Doctor Profiles & Appointment Scheduling

## 1. What Previous We Have Done
From **Step 04**:
- Implemented `ChildProfile` with pediatric age validation and parent data isolation.
- Built parent dashboard, child management CRUD, and custom template tags.
- Verified patient record access restrictions using automated unit tests.

---

## 2. What We Are Going to Do in This Step

### A. Appointment Models (`appointments/models.py`)
Implement the consultation scheduling system with anti-conflict constraints:
```python
from django.db import models
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
        MILD = 'MILD', 'Mild - Not spreading / Minor irritation'
        MODERATE = 'MODERATE', 'Moderate - Spreading / Itching causing sleep distress'
        URGENT = 'URGENT', 'Urgent - Rapid change / Painful (Non-emergency)'

    child = models.ForeignKey(
        'patients.ChildProfile',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    parent = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='parent_appointments'
    )
    doctor = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'DOCTOR'}
    )
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    chief_complaint = models.CharField(max_length=255, help_text="Primary concern, e.g., 'Eczema flare-up on elbow folds'")
    duration_of_symptoms = models.CharField(max_length=100, help_text="e.g. '4 days', '2 weeks'")
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
```

### B. Doctor Directory & Public Discovery (`appointments/views.py`)
- `DoctorDirectoryView`: Public list of board-certified pediatric dermatologists with photo avatar, bio, specialization, years of experience, and a direct "Book Consultation" link.
- Filter by specialization and minimum rating or consultation fee.

### C. Booking Workflow (`appointments/forms.py` & `views.py`)
- `AppointmentBookingForm`:
  - Dynamically filters the `child` queryset to only the authenticated parent's children.
  - Interactive date and time slot selector.
  - Urgency level and symptom description inputs.
- `AppointmentCreateView`: Uses atomic transaction (`transaction.atomic()`) to prevent race conditions during slot reservations.
- `AppointmentStatusUpdateView`: Allows doctors to accept, transition to clinical review, complete, or cancel with explanatory notes.

### D. Interactive Tailwind Templates
- `templates/appointments/doctor_list.html`: Modern healthcare provider grid with specialization tags and availability indicators.
- `templates/appointments/book_appointment.html`: 2-column layout with real-time appointment summary sidebar and dark-mode compatible form controls.
- `templates/appointments/parent_appointments.html`: Filterable tabs (Upcoming, In Review, History) with status badges (`bg-amber-100 text-amber-800 dark:bg-amber-900/40`, `bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40`).
- `templates/appointments/doctor_dashboard.html`: Doctor's command center displaying today's patient queue, pending image reviews, and direct links to clinical assessment tools.

---

## 3. Verification (Non-Browser Tests)

### Command 1: Migrations
```bash
python manage.py makemigrations appointments
python manage.py migrate
```
*Expected Output:* `Applying appointments.0001_initial... OK`.

### Command 2: Execute Unit Tests
Create `appointments/tests.py` testing:
1. Double-booking prevention via `unique_doctor_active_timeslot` constraint raises `IntegrityError` or `ValidationError`.
2. Past-date booking fails validation.
3. Cross-parent booking attempt (parent A booking for parent B's child) is blocked.
4. `Appointment.objects.upcoming()` accurately filters future appointments.
5. Doctor status transition from `PENDING` to `CONFIRMED`.

Execute tests:
```bash
python manage.py test appointments
```
*Expected Output:*
```text
Ran 5 tests in 0.45s
OK
```

### Command 3: Constraint Assertion via Django Shell
```bash
python manage.py shell -c "
from datetime import date, time, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from patients.models import ChildProfile
from appointments.models import Appointment

User = get_user_model()
p = User.objects.filter(role=User.Role.PARENT).first()
d = User.objects.filter(role=User.Role.DOCTOR).first()
c = ChildProfile.objects.filter(parent=p).first()

target_date = timezone.now().date() + timedelta(days=2)
target_time = time(10, 30)

a1 = Appointment.objects.create(child=c, parent=p, doctor=d, scheduled_date=target_date, scheduled_time=target_time)
try:
    a2 = Appointment.objects.create(child=c, parent=p, doctor=d, scheduled_date=target_date, scheduled_time=target_time)
    assert False, 'Double booking constraint failed to trigger'
except IntegrityError:
    print('Double booking constraint verified successfully.')
"
```
*Expected Output:* `Double booking constraint verified successfully.`

