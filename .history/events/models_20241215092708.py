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
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
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
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]


    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='waiting_list')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name