# Step 01: Environment & Project Foundation

## 1. What Previous We Have Done
This is the kickoff step for the **Pediatric Teledermatology** system:
- Initialized project workspace at the repository root.
- Established the technical specifications: Django 5.x, SQLite, Tailwind CSS with Dark/Light mode, and OpenAI API integration.
- Identified the 5 core Django applications: `accounts`, `patients`, `appointments`, `consultations`, and `ai_assistant`.
- Prior state: Clean workspace with no existing code or dependencies.

---

## 2. What We Are Going to Do in This Step

### A. Virtual Environment & Dependencies
Create an isolated Python environment and install core project packages:
- `django >= 5.0`: Core web framework.
- `pillow`: Required by Django `ImageField` for patient skin photograph processing.
- `openai >= 1.0.0`: Official SDK for OpenAI GPT-4o text and multimodal vision models.
- `reportlab` and `xhtml2pdf`: For generating clinical consultation report PDFs.
- `python-dotenv`: Secure configuration loading from `.env`.

### B. Django Project & Apps Architecture
Initialize the project structure with `config` as the root configuration package and register the 5 targeted apps:
```
pediatric_teledermatology/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
├── patients/
├── appointments/
├── consultations/
├── ai_assistant/
├── templates/
│   └── base.html
├── static/
│   ├── css/
│   │   └── custom.css
│   └── js/
│       └── theme.js
├── media/
│   └── skin_images/
├── manage.py
├── .env.example
├── .gitignore
└── requirements.txt
```

### C. Django Settings Configuration (`config/settings.py`)
1. **Installed Apps**: Register `accounts`, `patients`, `appointments`, `consultations`, and `ai_assistant`.
2. **Database**: Configure SQLite3 with thread safety settings.
3. **Template Engine**: Set `DIRS` to `[BASE_DIR / 'templates']` and register future context processors.
4. **Static & Media Configuration**:
   ```python
   STATIC_URL = '/static/'
   STATICFILES_DIRS = [BASE_DIR / 'static']
   STATIC_ROOT = BASE_DIR / 'staticfiles'

   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR / 'media'
   ```
5. **Tailwind CSS & Dark Mode Baseline**:
   - Include Tailwind CSS via official CDN script with `darkMode: 'class'` configuration.
   - Extend colors with pediatric health tokens:
     - `teal-brand`: `#0D9488`
     - `mint-brand`: `#10B981`
     - `slate-dark`: `#0F172A`
     - `surface-dark`: `#1E293B`

---

## 3. Verification (Non-Browser Tests)

Run the following terminal and shell commands to verify this step without browser automation:

### Command 1: Verify Dependencies and Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import django, PIL, openai, dotenv; print('Django version:', django.__version__, '| OpenAI version:', openai.__version__)"
```
*Expected Output:* Prints Django and OpenAI versions without import errors.

### Command 2: Django System Check
```bash
python manage.py check
```
*Expected Output:* `System check identified no issues (0 silenced).`

### Command 3: Initial Migration & SQLite File Creation
```bash
python manage.py migrate
```
*Expected Output:* Operations performed successfully, creating standard tables in `db.sqlite3`.

### Command 4: Static & Media Path Assertion via Django Shell
```bash
python manage.py shell -c "
from django.conf import settings
import os
assert os.path.exists(settings.BASE_DIR / 'templates'), 'Templates dir missing'
assert os.path.exists(settings.BASE_DIR / 'static'), 'Static dir missing'
print('Project paths and Django configuration validated successfully.')
"
```
*Expected Output:* `Project paths and Django configuration validated successfully.`
