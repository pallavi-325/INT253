from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Appointment

@receiver(pre_save, sender=Appointment)
def track_appointment_status_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Appointment.objects.get(pk=instance.pk)
            instance._previous_status = previous.status
        except Appointment.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Appointment)
def handle_appointment_status_post_save(sender, instance, created, **kwargs):
    if created:
        instance._lifecycle_event = 'CREATED'
    elif hasattr(instance, '_previous_status') and instance._previous_status != instance.status:
        instance._lifecycle_event = f"TRANSITION_{instance._previous_status}_TO_{instance.status}"
    else:
        instance._lifecycle_event = 'UPDATED'

