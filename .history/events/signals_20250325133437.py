from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Registration, Event, Notification

# Create a notification when a user registers for an event
@receiver(post_save, sender=Registration)
def create_registration_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            message=f"You successfully registered for {instance.event.title}",
            is_read=False
        )

# Create a notification when a new event is added
@receiver(post_save, sender=Event)
def create_event_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            message=f"New event created: {instance.title}",
            is_read=False
        )
