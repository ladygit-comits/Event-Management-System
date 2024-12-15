from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.timezone import now

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
        # If the registration status has been updated, send an email
        if self.pk:
            old_status = Registration.objects.get(pk=self.pk).status
            if old_status != self.status:
                self.send_status_email()

        super().save(*args, **kwargs)

    def send_status_email(self):
        # Email content based on status
        if self.status == 'approved':
            subject = "Registration Approved!"
            message = f"Dear {self.user.first_name},\n\nYour registration for the event '{self.event.title}' has been approved. We look forward to your participation!"
        elif self.status == 'declined':
            subject = "Registration Declined"
            message = f"Dear {self.user.first_name},\n\nWe're sorry to inform you that your registration for the event '{self.event.title}' has been declined."
        else:
            subject = "Registration Waiting for Approval"
            message = f"Dear {self.user.first_name},\n\nYour registration for the event '{self.event.title}' is currently waiting for approval."

        # Send the email
        send_mail(
            subject,
            message,
            'faithwanjiiri@gmail.com',  # Sender's email (you can change this to the sender's email you prefer)
            [self.user.email],       # Recipient's email
            fail_silently=False,
        )

    def __str__(self):
        return self.name
    
class Participant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.event.name}"

class WaitingList(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1) 
    name = models.CharField(max_length=200)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # If the status changes, send an email
        if self.pk:
            old_status = WaitingList.objects.get(pk=self.pk).status
            if old_status != self.status:
                self.send_status_notification()

        super().save(*args, **kwargs)

    def send_status_notification(self):
        # Email content based on status
        if self.status == 'approved':
            subject = "You're Approved!"
            message = f"Hi {self.name},\n\nYour request to join the event '{self.event.title}' has been approved! We look forward to seeing you there."
        elif self.status == 'declined':
            subject = "Request Declined"
            message = f"Hi {self.name},\n\nWe're sorry, but your request to join the event '{self.event.title}' has been declined."
        else:
            subject = "Waiting for Approval"
            message = f"Hi {self.name},\n\nYour request to join the event '{self.event.title}' is currently waiting for approval."

        # Send the email
        send_mail(
            subject,
            message,
            'faithwanjiiri@gmail.com',  # Sender's email
            [self.email],            # Recipient's email
            fail_silently=False,
        )