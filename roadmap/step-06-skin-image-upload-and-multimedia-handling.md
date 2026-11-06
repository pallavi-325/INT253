# Step 06: Skin Image Upload & Multimedia Handling

## 1. What Previous We Have Done
From **Step 05**:
- Built appointment scheduling, doctor directory, and double-booking prevention.
- Implemented parent and doctor dashboard views.
- Verified slot reservation constraints and appointment status lifecycle.

---

## 2. What We Are Going to Do in This Step

### A. Dynamic & Secure Upload Paths (`patients/models.py`)
Isolate patient images into scoped subdirectories on the filesystem:
```python
import os
import uuid

def child_skin_image_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return os.path.join(
        'skin_images',
        f'child_{instance.child.id}',
        instance.uploaded_at.strftime('%Y/%m'),
        unique_name
    )
```

### B. Medical Image Validation Service (`patients/validators.py`)
Ensure high image quality for clinical assessment and prevent malicious uploads:
1. **File Size Enforcement**: Limit to 10 MB per image.
2. **Format Whitelist**: Only `.jpg`, `.jpeg`, `.png`, `.webp`.
3. **Pillow Byte Inspection**: Validates binary header signatures to detect spoofed files.
4. **Resolution Minimum**: Requires minimum resolution of `400 x 400` pixels for dermatological clarity.

```python
from django.core.exceptions import ValidationError
from PIL import Image

def validate_medical_image(file_obj):
    # Max file size: 10MB
    if file_obj.size > 10 * 1024 * 1024:
        raise ValidationError("Image file size exceeds the 10MB limit.")

    try:
        file_obj.seek(0)
        with Image.open(file_obj) as img:
            img.verify()
            width, height = img.size
            if width < 400 or height < 400:
                raise ValidationError("Image resolution too low. Minimum 400x400 pixels required for clinical review.")
    except Exception:
        raise ValidationError("Invalid or corrupted image format.")
    finally:
        file_obj.seek(0)
```

### C. SkinImage Model (`patients/models.py`)
```python
class SkinImage(models.Model):
    class BodyPart(models.TextChoices):
        FACE = 'FACE', 'Face / Cheeks'
        SCALP = 'SCALP', 'Scalp / Forehead'
        TRUNK = 'TRUNK', 'Chest / Back / Stomach'
        ARMS = 'ARMS', 'Arms / Elbow Folds'
        LEGS = 'LEGS', 'Legs / Knee Folds'
        DIAPER_AREA = 'DIAPER', 'Diaper Area / Groin'
        HANDS_FEET = 'HANDS_FEET', 'Hands / Feet'
        GENERALIZED = 'GENERALIZED', 'Multiple Areas / Widespread'

    class ViewType(models.TextChoices):
        OVERVIEW = 'OVERVIEW', 'Overview (showing area in context)'
        CLOSE_UP = 'CLOSE_UP', 'Close-up (detailed lesion/rash view)'

    child = models.ForeignKey('patients.ChildProfile', on_delete=models.CASCADE, related_name='skin_images')
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='skin_images'
    )
    image = models.ImageField(upload_to=child_skin_image_path, validators=[validate_medical_image])
    body_part = models.CharField(max_length=20, choices=BodyPart.choices, default=BodyPart.FACE)
    view_type = models.CharField(max_length=20, choices=ViewType.choices, default=ViewType.CLOSE_UP)
    notes = models.TextField(blank=True, help_text="Specific observations (e.g., 'started 2 days ago, blisters forming')")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.child.full_name} - {self.get_body_part_display()} ({self.uploaded_at.strftime('%Y-%m-%d')})"
```

### D. Interactive Upload & Review UI (Tailwind + Vanilla JS)
- **Drag-and-Drop Uploader** (`static/js/image_uploader.js`):
  - Interactive drop-zone with dynamic border animation (`border-dashed border-teal-500 bg-teal-50/50 dark:bg-teal-950/20`).
  - Instant client-side thumbnail generation using `FileReader` API.
  - Multi-image file list preview with delete buttons prior to form submit.
- **Doctor Clinical Lightbox** (`templates/consultations/components/image_lightbox.html`):
  - High-resolution modal with zoom in/out, side-by-side comparison of overview vs. close-up photos, and dark-mode backdrop.

---

## 3. Verification (Non-Browser Tests)

### Command 1: Migrations
```bash
python manage.py makemigrations patients
python manage.py migrate
```
*Expected Output:* `Applying patients.0002_skinimage... OK`.

### Command 2: Unit Tests Execution
Create `patients/tests/test_images.py` testing:
1. Valid PNG/JPEG uploads pass validation and are persisted in `media/skin_images/`.
2. Corrupted file or renamed text file (`fake.jpg`) is caught by `validate_medical_image`.
3. Image smaller than 400x400px triggers a validation error.
4. Unauthorized parent cannot view or delete another family's skin images.

Run tests:
```bash
python manage.py test patients.tests.test_images
```
*Expected Output:*
```text
Ran 4 tests in 0.52s
OK
```

### Command 3: Django Shell Synthetic Image Upload Test
```bash
python manage.py shell -c "
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from patients.models import ChildProfile, SkinImage
from patients.validators import validate_medical_image

child = ChildProfile.objects.first()

# Generate a synthetic 500x500 valid image in memory
img_buffer = io.BytesIO()
img = Image.new('RGB', (500, 500), color=(73, 109, 137))
img.save(img_buffer, format='JPEG')
img_buffer.seek(0)

upload_file = SimpleUploadedFile('test_lesion.jpg', img_buffer.read(), content_type='image/jpeg')
validate_medical_image(upload_file)

skin_img = SkinImage.objects.create(child=child, image=upload_file, body_part=SkinImage.BodyPart.FACE)
assert skin_img.image.path.endswith('.jpg')
print('Skin image creation and validation logic verified successfully.')
"
```
*Expected Output:* `Skin image creation and validation logic verified successfully.`

