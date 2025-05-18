from django import forms
from .models import Event, Registration, Category, WaitingList, ContactUs, Vendor
from django.forms import DateTimeInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


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
        fields = ['name', 'email', 'phone_number', 'event']  

    def save(self, user=None, commit=True):
        instance = super().save(commit=False)
        if user:
            instance.user = user 
        if commit:
            instance.save()
        return instance

class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'phone', 'message']

class VendorRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    username = forms.CharField(max_length=100)

    class Meta:
        model = Vendor
        fields = ['username', 'email', 'password1', 'password2', 'business_name', 'contact_person', 'phone_number', 'category', 'description', 'logo']

class VendorEditForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['business_name', 'contact_person', 'phone_number', 'email', 'category', 'description', 'logo']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class VendorLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Password'
    )
