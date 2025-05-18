from django.db import models
from django.contrib.auth.models import User, AbstractUser
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
    capacity = models.PositiveIntegerField(default=10)# Maximum number of participants
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    details = models.TextField(default="No details available")
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    
    def is_full(self):
        """Check if the event has reached its full capacity."""
        return self.registrations.count() >= self.capacity

    def __str__(self):
        return self.title

class RSVP(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class Registration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    registered_on = models.DateTimeField(auto_now_add=True)

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
        ('pending', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]


    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='waiting_list')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class Vendor(AbstractUser):
    business_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)

    groups = models.ManyToManyField('auth.Group', related_name='vendor_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='vendor_permissions', blank=True)

    class Meta:
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"

    def __str__(self):
        return self.business_name

class Notification(models.Model):
    message = models.TextField()
    is_read = models.BooleanField(default=False)  # Tracks if read or unread
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message