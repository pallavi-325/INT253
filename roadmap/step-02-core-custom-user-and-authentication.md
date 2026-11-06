# Step 02: Core Custom User & Authentication

## 1. What Previous We Have Done
From **Step 01**:
- Initialized the Django 5.x project with the 5 designated apps (`accounts`, `patients`, `appointments`, `consultations`, `ai_assistant`).
- Created foundational project structure, `settings.py`, and base template/static directories.
- Prior state: Default Django configuration without a custom user model or authentication logic.

---

## 2. What We Are Going to Do in This Step

### A. Custom User Model (`accounts/models.py`)
To prevent future database migration conflicts and support distinct roles, define a custom user inheriting from `AbstractUser`:
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

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
```
*Django Best Practice:* Add `AUTH_USER_MODEL = 'accounts.User'` to `config/settings.py` before running initial migrations.

### B. Doctor & Parent Profiles (`accounts/models.py`)
- **`DoctorProfile`**:
  - `user`: OneToOneField linked to `accounts.User` (`related_name='doctor_profile'`).
  - `license_number`: Unique medical license identifier.
  - `specialization`: e.g., "Pediatric Atopic Dermatitis", "General Pediatric Dermatology".
  - `experience_years`: Positive integer.
  - `bio`: Clinical background and approach.
  - `is_verified`: Boolean flag indicating hospital admin review.
  - `consultation_fee`: Decimal field.
- **`ParentProfile`**:
  - `user`: OneToOneField linked to `accounts.User` (`related_name='parent_profile'`).
  - `emergency_contact`: Phone number.
  - `preferred_language`: English, Spanish, etc.
  - `consent_to_telehealth`: Boolean flag required before booking.

### C. Signals for Profile Auto-Creation (`accounts/signals.py`)
Use `post_save` on `User` to automatically instantiate the corresponding profile model whenever a parent or doctor user is registered.

### D. Role-Based Access Control (RBAC) Decorators & Mixins (`accounts/permissions.py`)
- Implement `RoleRequiredMixin` and `@role_required(['PARENT'])` / `@role_required(['DOCTOR'])`.
- Implement `RoleBasedRedirectView` at `/accounts/dashboard-redirect/` that dynamically routes users upon login:
  - `Role.PARENT` -> `reverse_lazy('patients:parent_dashboard')`
  - `Role.DOCTOR` -> `reverse_lazy('appointments:doctor_dashboard')`
  - `Role.ADMIN` -> `/admin/`

### E. Forms & Tailwind-Styled Auth Templates
- `ParentRegistrationForm` and `DoctorRegistrationForm`: Custom forms styled using Tailwind utility classes (`border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-teal-500`).
- Templates:
  - `templates/accounts/login.html`: High-conversion split-layout card with light/dark theme support.
  - `templates/accounts/register_parent.html`: Clean onboarding flow emphasizing privacy and HIPAA/health security.
  - `templates/accounts/register_doctor.html`: Professional medical provider application view.

---

## 3. Verification (Non-Browser Tests)

### Command 1: Make and Apply Custom User Migrations
```bash
python manage.py makemigrations accounts
python manage.py migrate
```
*Expected Output:* `Applying accounts.0001_initial... OK`.

### Command 2: Execute Django Unit Test Suite for Accounts
Create `accounts/tests.py` testing:
1. User registration with `PARENT` role creates linked `ParentProfile`.
2. User registration with `DOCTOR` role creates linked `DoctorProfile`.
3. Unauthorized access to doctor-only routes returns HTTP 403 Forbidden.
4. Role redirection route forwards doctors to `/doctor/` and parents to `/parent/`.

Run test execution:
```bash
python manage.py test accounts
```
*Expected Output:*
```text
Ran 5 tests in 0.42s
OK
```

### Command 3: Django Shell User Creation & Role Check
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.create_user(username='parent_test', email='test@example.com', password='password123', role=User.Role.PARENT)
assert u.is_parent() == True
assert hasattr(u, 'parent_profile')
print('Custom user model and automatic profile creation validated.')
"
```
*Expected Output:* `Custom user model and automatic profile creation validated.`

