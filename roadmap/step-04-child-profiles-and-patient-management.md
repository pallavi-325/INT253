# Step 04: Child Profiles & Patient Management

## 1. What Previous We Have Done
From **Step 03**:
- Built the Tailwind CSS design system with interactive Dark/Light mode switcher and responsive layout.
- Established the base layout (`base.html`), navigation components, and alert messages.
- Verified custom user authentication and role routing.

---

## 2. What We Are Going to Do in This Step

### A. Abstract Timestamp Model (`patients/models.py`)
Implement a reusable `TimeStampedModel` with `created_at` and `updated_at` to inherit across all medical data entities:
```python
from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

### B. ChildProfile Model & Custom Manager (`patients/models.py`)
Create the core pediatric patient record:
```python
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

class ChildProfileQuerySet(models.QuerySet):
    def for_parent(self, user):
        return self.filter(parent=user)

class ChildProfile(TimeStampedModel):
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'
        PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY', 'Prefer not to say'

    parent = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='children',
        limit_choices_to={'role': 'PARENT'}
    )
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    date_of_birth = models.DateField(help_text="Patient must be under 18 years old")
    gender = models.CharField(max_length=20, choices=Gender.choices)
    blood_group = models.CharField(max_length=10, blank=True)
    known_allergies = models.TextField(blank=True, help_text="e.g. Penicillin, Peanuts, Latex, Topical ointments")
    previous_skin_conditions = models.TextField(blank=True, help_text="e.g. Infantile eczema, Contact dermatitis")
    current_medications = models.TextField(blank=True)
    medical_history_notes = models.TextField(blank=True)

    objects = ChildProfileQuerySet.as_manager()

    def clean(self):
        super().clean()
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError({'date_of_birth': "Date of birth cannot be in the future."})
        
        # Pediatric validation (< 18 years old)
        today = timezone.now().date()
        age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        if age >= 18:
            raise ValidationError({'date_of_birth': "Patient must be under 18 years old for pediatric care."})

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name
```

### C. Custom Template Tags (`patients/templatetags/patient_tags.py`)
- `calculate_age`: Computes accurate pediatric age (e.g., "4 months" for infants, "3 years, 2 months" for toddlers).
- `allergy_badges`: Formats comma-delimited strings into alert badges using Tailwind (`bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300`).

### D. Forms & Validation (`patients/forms.py`)
- `ChildProfileForm`: ModelForm with HTML5 datepicker widget (`type: 'date'`), dynamic Tailwind classes, and field-level validation messages.

### E. Class-Based Views (`patients/views.py`)
Protected by `LoginRequiredMixin` and `RoleRequiredMixin(['PARENT'])`:
- `ParentDashboardView`: Summarizes registered children, upcoming consultations, and recent reports.
- `ChildListView`: Grid of child profile cards with health stats and quick consultation booking buttons.
- `ChildCreateView`: Multi-step friendly form for registering a child.
- `ChildUpdateView`: Edit existing details with strict object ownership validation (`get_queryset().filter(parent=request.user)`).
- `ChildDetailView`: Full patient overview tabbed with medical records, upcoming appointments, and skin image history.

---

## 3. Verification (Non-Browser Tests)

### Command 1: Migrations
```bash
python manage.py makemigrations patients
python manage.py migrate
```
*Expected Output:* `Applying patients.0001_initial... OK`.

### Command 2: Unit Tests Execution
Create `patients/tests.py` testing:
1. `ChildProfile` date of birth in the future raises `ValidationError`.
2. Adult patient age (>= 18) raises `ValidationError`.
3. Parent A cannot retrieve or edit Parent B's child (verifies 404/permission isolation).
4. `calculate_age` template tag handles infants under 1 year and multi-year children properly.

Execute test run:
```bash
python manage.py test patients
```
*Expected Output:*
```text
Ran 4 tests in 0.38s
OK
```

### Command 3: Django Shell Ownership & QuerySet Test
```bash
python manage.py shell -c "
from datetime import date
from django.contrib.auth import get_user_model
from patients.models import ChildProfile

User = get_user_model()
p1 = User.objects.create_user(username='parent_1', email='p1@example.com', password='pw', role=User.Role.PARENT)
p2 = User.objects.create_user(username='parent_2', email='p2@example.com', password='pw', role=User.Role.PARENT)

c1 = ChildProfile.objects.create(parent=p1, first_name='Baby', last_name='Doe', date_of_birth=date(2022, 1, 1), gender=ChildProfile.Gender.MALE)

assert ChildProfile.objects.for_parent(p1).count() == 1
assert ChildProfile.objects.for_parent(p2).count() == 0
print('ChildProfile ownership isolation and custom manager validated.')
"
```
*Expected Output:* `ChildProfile ownership isolation and custom manager validated.`

