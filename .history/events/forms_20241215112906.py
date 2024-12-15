from django import forms
from .models import Event, Registration, Category, WaitingList
from django.forms import DateTimeInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
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
        
    def __init__(self, *args, **kwargs):
        user = kwargs.get('user')  # Pass user dynamically from view
        super().__init__(*args, **kwargs)
        if user:
            self.instance.user = user  # Ensure user is set in registration form

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
        fields = ['event']  

    def save(self, user=None, commit=True):
        instance = super().save(commit=False)
        if user:
            instance.user = user  # Set the user explicitly
        if commit:
            instance.save()
        return instance
