from django import forms
from .models import Event, Registration, Category
from django.forms import DateTimeInput
from django.contrib.auth.models import User

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'category', 'details', 'image']
        widgets = {
            'date': DateTimeInput(attrs={'type': 'datetime-local'}),  # Using datetime-local input type for proper user input format
        }

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['name', 'email', 'phone', 'message']

class AdminLoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

