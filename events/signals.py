from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Registration, Event, Notification, VendorProfile, WaitingList

User = get_user_model()

@receiver(post_save, sender=Registration)
def create_registration_notification(sender, instance, created, **kwargs):
    if created and instance.user and not instance.user.is_staff:
        Notification.objects.create(
            user=instance.user,
            message=f"You successfully registered for {instance.event.title}",
            is_read=False
        )

# Create a notification when a new event is added — only for admins!
@receiver(post_save, sender=Event)
def create_event_notification(sender, instance, created, **kwargs):
    if created:
        # Send event notification only to admin/staff users
        admin_users = User.objects.filter(is_staff=True)
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                message=f"New event created: {instance.title}",
                is_read=False
            )

# Automatically create VendorProfile when a Vendor User is created
@receiver(post_save, sender=User)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created and instance.groups.filter(name='Vendor').exists():
        VendorProfile.objects.create(user=instance)

@receiver(post_save, sender=WaitingList)
def create_registration_from_waiting(sender, instance, created, **kwargs):
    if not created and instance.status == 'approved':
        # Check if already registered
        registration_exists = Registration.objects.filter(user=instance.user, event=instance.event).exists()
        if not registration_exists:
            Registration.objects.create(
                user=instance.user,
                event=instance.event,
                phone=instance.phone_number,
                message="Auto-registered from waiting list approval",
                status='approved',  # Set status as approved
            )
            
            # Create a notification to user
            Notification.objects.create(
                user=instance.user,
                message=f"You have been registered for {instance.event.title} after approval!",
                is_read=False
            )
