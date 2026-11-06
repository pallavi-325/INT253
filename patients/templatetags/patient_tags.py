from django import template
from django.utils import timezone
from datetime import date

register = template.Library()

@register.filter(name='calculate_age')
def calculate_age(dob):
    if not dob:
        return "Unknown age"
    today = timezone.now().date()
    years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    # Under 1 year old -> show in months
    if years < 1:
        months = (today.year - dob.year) * 12 + (today.month - dob.month)
        if today.day < dob.day:
            months = max(0, months - 1)
        if months == 0:
            days = (today - dob).days
            return f"{days} days old"
        return f"{months} month{'s' if months != 1 else ''} old"
    elif years == 1:
        months = (today.month - dob.month) % 12
        if months > 0:
            return f"1 yr, {months} mo"
        return "1 year old"
    else:
        return f"{years} years old"

@register.filter(name='split_allergies')
def split_allergies(allergy_text):
    if not allergy_text:
        return []
    return [item.strip() for item in allergy_text.split(',') if item.strip()]

