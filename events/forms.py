from django import forms
from django.forms import DateTimeInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Event, Registration, Category, WaitingList, ContactUs,
    VendorProfile, Product, Profile
)
from .models import Order
from .models import Message

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'})
    )

    class Meta:
        model = User  
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'category', 'details', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Event title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Short event description'}),
            'date': DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'location': forms.TextInput(attrs={'placeholder': 'Event location'}),
            'details': forms.Textarea(attrs={'placeholder': 'Detailed information'}),
        }

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Your phone number'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your message'}),
        }



class AdminLoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Admin username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Category name'}),
        }

class WaitingListForm(forms.ModelForm):
    class Meta:
        model = WaitingList
        fields = ['name', 'email', 'phone_number', 'event']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Your phone number'}),
        }

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
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Your phone number'}),
            'message': forms.Textarea(attrs={'placeholder': 'Type your message'}),
        }

class VendorRegistrationForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email address'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), label="Confirm Password")

    class Meta:
        model = VendorProfile
        fields = ['business_name', 'contact_person', 'phone_number', 'description', 'logo']
        widgets = {
            'business_name': forms.TextInput(attrs={'placeholder': 'Business name'}),
            'contact_person': forms.TextInput(attrs={'placeholder': 'Contact person'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone number'}),
            'description': forms.Textarea(attrs={'placeholder': 'Business description'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        email = self.cleaned_data['email']
        username = email.split('@')[0]  # simple username from email
        password = self.cleaned_data['password1']

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create vendor profile
        vendor_profile = super().save(commit=False)
        vendor_profile.user = user
        if commit:
            vendor_profile.save()
        return vendor_profile

class VendorEditForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'contact_person', 'phone_number', 'description', 'logo']
        widgets = {
            'business_name': forms.TextInput(attrs={'placeholder': 'Business name'}),
            'contact_person': forms.TextInput(attrs={'placeholder': 'Contact person'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone number'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description'}),
        }

class VendorLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email address'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email address'}),
        }

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['notifications_enabled']

class ProductForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('Food', 'Food'),
        ('Drinks', 'Drinks'),
        ('Clothing', 'Clothing'),
        ('Art', 'Art'),
        ('Merchandise', 'Merchandise'),
        ('Electronics', 'Electronics'),
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES)

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image', 'stock', 'event']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Product name', 'class': 'form-control form-control-lg'}),
            'description': forms.Textarea(attrs={'placeholder': 'Product description', 'class': 'form-control form-control-lg', 'rows': 4}),
            'price': forms.NumberInput(attrs={'placeholder': 'Price', 'class': 'form-control form-control-lg'}),
            'stock': forms.NumberInput(attrs={'placeholder': 'Available stock', 'class': 'form-control form-control-lg'}),
            'event': forms.Select(attrs={'class': 'form-select form-select-lg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False

class ManualOrderForm(forms.ModelForm):
    def __init__(self, *args, vendor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if vendor:
            self.fields['product'].queryset = Product.objects.filter(vendor=vendor)
        if 'user' in self.fields:
            self.fields['user'].widget = forms.HiddenInput()  # 👈 hide user field

    class Meta:
        model = Order
        fields = ['product', 'quantity']

class VendorProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'event']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Type your message here...', 'rows': 5}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your reply here...', 'rows': 4}),
        }
