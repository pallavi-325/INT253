from django.core.exceptions import ValidationError
from PIL import Image

def validate_medical_image(file_obj):
    # Max file size: 10MB
    max_size_bytes = 10 * 1024 * 1024
    if file_obj.size > max_size_bytes:
        raise ValidationError("Image file size exceeds the 10MB limit.")

    try:
        file_obj.seek(0)
        with Image.open(file_obj) as img:
            img.verify()
            width, height = img.size
            if width < 400 or height < 400:
                raise ValidationError("Image resolution too low. Minimum 400x400 pixels required for clinical dermatological review.")
    except Exception as e:
        if isinstance(e, ValidationError):
            raise e
        raise ValidationError("Invalid or corrupted medical image file.")
    finally:
        file_obj.seek(0)

