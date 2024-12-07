from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    details = models.TextField(default="No details available")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Link events to users
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return self.title

class RSVP(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attending = models.BooleanField()

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class Registration(models.Model):
   
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=100, default="Eren")
    email = models.EmailField(default="example@example.com")
    phone = models.CharField(max_length=15, null=True, blank=True, default="0000000000")
    message = models.TextField(null=True, blank=True, default="")

    def __str__(self):
        return f'{self.name} registered for {self.event.title}'
    
