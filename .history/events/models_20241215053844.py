from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.timezone import now


# Utility function to send emails
def send_status_email(subject, message, recipient_email):
    send_mail(
        subject,
        message,
        'faithwanjiiri@gmail.com',  # Sender's email (configured in settings.py)
        [recipient_email],
        fail_silently=False,
    )


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    details = models.TextField(default="No details available")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.title


class RSVP(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')


class Registration(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    phone = models.CharField(max_length=15)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    registered_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_status = Registration.objects.get(pk=self.pk).status
            if old_status != self.status:
                subject = "Registration Status Update"
                message = f"Hi {self.name},\n\nYour registration for '{self.event.title}' is now '{self.status}'."
                send_status_email(subject, message, self.email)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class WaitingList(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_status = WaitingList.objects.get(pk=self.pk).status
            if old_status != self.status:
                subject = "Waiting List Status Update"
                message = f"Hi {self.name},\n\nYour request for '{self.event.title}' is now '{self.status}'."
                send_status_email(subject, message, self.email)
        super().save(*args, **kwargs)
