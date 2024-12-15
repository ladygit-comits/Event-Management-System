from django import forms
from .models import Event, Registration, Category, WaitingList
from django.forms import DateTimeInput
from django.contrib.auth.models import User

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'category', 'details', 'image']
        widgets = {
        'date': DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
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
        fields = ['name']

class WaitingListForm(forms.ModelForm):
    class Meta:
        model = WaitingList
        fields = ['name', 'email', 'event']  # Event will be passed dynamically
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email Address'}),
            'event': forms.HiddenInput(),  # Event will not be visible to users
        }