from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import DoctorProfile, ParentProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Role.DOCTOR:
            DoctorProfile.objects.get_or_create(
                user=instance,
                defaults={'license_number': f"MED-PENDING-{instance.id}"}
            )
        elif instance.role == User.Role.PARENT:
            ParentProfile.objects.get_or_create(user=instance)

