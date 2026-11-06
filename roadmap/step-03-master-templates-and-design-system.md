# Step 03: Master Templates & Interactive Design System

## 1. What Previous We Have Done
From **Step 02**:
- Custom User model (`accounts.User`) with role enumerations (`PARENT`, `DOCTOR`, `ADMIN`).
- One-to-one doctor and parent profile models with post-save signals.
- Role-based redirection logic and permission decorators.
- Basic authentication forms and views.

---

## 2. What We Are Going to Do in This Step

### A. Responsive Master Layout (`templates/base.html`)
Build a high-fidelity, accessible base template incorporating:
1. **Tailwind CSS Configuration**:
   Inline script configuring Tailwind with `darkMode: 'class'` and custom healthcare colors:
   ```javascript
   tailwind.config = {
     darkMode: 'class',
     theme: {
       extend: {
         colors: {
           brand: {
             50: '#F0FDFA',
             100: '#CCFBF1',
             500: '#14B8A6',
             600: '#0D9488',
             700: '#0F766E',
             900: '#134E4A',
           },
           darkbg: '#0F172A',
           darksurface: '#1E293B',
           darkcard: '#334155'
         }
       }
     }
   }
   ```
2. **Anti-FOUC Theme Script**:
   Inline early execution in `<head>` to prevent Flash of Unstyled Content:
   ```javascript
   if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
     document.documentElement.classList.add('dark');
   } else {
     document.documentElement.classList.remove('dark');
   }
   ```

### B. Interactive Theme Switcher (`static/js/theme.js`)
- Toggles `dark` class on `document.documentElement`.
- Updates the sun/moon icon dynamically.
- Persists user choice in `localStorage`.
- Dispatches custom DOM events `themeChanged` for charts and dynamic components.

### C. Reusable UI Component Sub-Templates (`templates/components/`)
- `navbar.html`: Top navigation containing brand identity, dynamic role pills, notification trigger, theme toggle, and authenticated user menu.
- `sidebar.html`: Dynamic dashboard sidebar with collapsible state on mobile screens.
- `alert_messages.html`: Toast-style dismissal alerts rendering Django `messages` (success, warning, error, info) with smooth fade-out animations.
- `modal.html`: Accessible modal wrapper triggered by data attributes (`data-modal-target="modal-id"`), supporting ESC key and outside-click dismissals.

### D. Public Landing Page (`templates/public/home.html`)
A welcoming, pediatric-oriented public homepage:
- **Hero Section**: Heading, value proposition, badges ("HIPAA & Privacy Focused", "Board-Certified Dermatologists"), and Call-to-Action buttons.
- **Workflow Section**: 4-step illustrated interactive cards:
  1. Add Child Profile & Symptoms
  2. Upload Clear Skin Photos
  3. AI Pre-Consultation Triage Check
  4. Receive Doctor Assessment & Prescriptions
- **Clinicians Highlight**: Directory preview of featured dermatologists.
- **Urgent Care Safety Banner**: Clear warning directing parents to emergency services for acute symptoms.

---

## 3. Verification (Non-Browser Tests)

### Command 1: Django Template Render & View Test
Create `accounts/tests/test_views.py` with tests for public pages:
```python
from django.test import TestCase, Client
from django.urls import reverse

class PublicPagesTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_status_code_and_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'public/home.html')
        self.assertContains(response, 'Pediatric Teledermatology')

    def test_theme_js_asset_exists(self):
        from django.conf import settings
        import os
        theme_js = settings.BASE_DIR / 'static' / 'js' / 'theme.js'
        self.assertTrue(os.path.exists(theme_js), "theme.js must exist in static/js/")
```

### Command 2: Execute Tests
```bash
python manage.py test accounts.tests.test_views
```
*Expected Output:*
```text
Ran 2 tests in 0.25s
OK
```

### Command 3: Template Syntax Check
Ensure zero template compilation errors across all new files:
```bash
python manage.py shell -c "
from django.template.loader import get_template
for t in ['base.html', 'public/home.html', 'components/navbar.html', 'components/sidebar.html']:
    get_template(t)
print('All master templates and components compiled successfully.')
"
```
*Expected Output:* `All master templates and components compiled successfully.`

