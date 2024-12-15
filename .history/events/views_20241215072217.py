import json
import os
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import requests
from requests.auth import HTTPBasicAuth


from events.credentials import LipanaMpesaPpassword, MpesaAccessToken
from .models import Event, Registration, WaitingList
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import RSVP,Event, WaitingList
from .forms import EventForm, RegistrationForm, CategoryForm, WaitingListForm, CustomUserCreationForm
from django.utils import timezone
from django.core import serializers
from .forms import AdminLoginForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .utils import send_confirmation_email
from django.contrib import messages
from django.utils.timezone import now

def admin_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:  # Ensures only admin users can log in
                login(request, user)
                return redirect('admin')  # Redirect to event creation page
            else:
                form.add_error(None, "Invalid credentials or you are not an admin.")
    else:
        form = AuthenticationForm()  # No initial data passed
    
    return render(request, 'events/admin_login.html', {'form': form})

def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, pk):
    event = Event.objects.get(pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)  # Use the customized form
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user immediately after registration
            return redirect('login')  # Redirect to login page after registration
    else:
        form = CustomUserCreationForm()  # Initialize the empty form
    return render(request, 'registration/register.html', {'form': form})




def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('event_list')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def event_detail(request, pk):
    event = Event.objects.get(pk=pk)
    rsvp, created = RSVP.objects.get_or_create(event=event, user=request.user)
    if request.method == 'POST':
        rsvp.attending = not rsvp.attending
        rsvp.save()
    return render(request, 'events/event_detail.html', {'event': event, 'rsvp': rsvp})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)  # Fetch event by ID
    return render(request, 'events/event_detail.html', {'event': event})

@staff_member_required
def create_event(request):
    if request.method == 'POST':
        # Handling event form
        event_form = EventForm(request.POST)
        # Handling category form
        category_form = CategoryForm(request.POST)

        if event_form.is_valid() and category_form.is_valid():
            # Save Event
            event = event_form.save(commit=False)
            event.user = request.user  # Assign the event to the logged-in user
            event.save()

            # Save Category
            category = category_form.save()
            
            return redirect('event_list')  # Redirect to the event list page after saving
    else:
        event_form = EventForm()
        category_form = CategoryForm()

    return render(request, 'events/admin.html', {
        'form': event_form,
        'category_form': category_form
    })

# This is the category view
@staff_member_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_event')  # Redirect back to the admin panel after saving
    else:
        form = CategoryForm()

    return render(request, 'events/create_category.html', {'form': form})

# View to update an existing event
def update_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.user:  # Ensure that only the event creator can edit the event
        return redirect('event_list')  # Redirect to the event list if the user is not the owner
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/update_event.html', {'form': form, 'event': event})

# View to delete an event
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.user:
        return redirect('event_list')
    if request.method == "POST":
        event.delete()
        return redirect('event_list')
    return render(request, 'events/delete_event.html', {'event': event})

@login_required  # Ensure only logged-in users can register

def register_for_event(request, pk):
    # Fetch the event using the primary key (pk)
    event = get_object_or_404(Event, pk=pk)
    
    # Check if the request is a POST (form submission)
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            
            registration = form.save(commit=False)
            registration.event = event  # Associate the event with the registration
            registration.save()  # Save the registration

            # Send confirmation email
            send_confirmation_email(form.cleaned_data['email'], event.title)

            # Add a success message
            messages.success(request, f"You have successfully registered for {event.title}. A confirmation email has been sent.")
            
            # Redirect to a registration success page
            return redirect('registration_success') 
    else:
        form = RegistrationForm()  # Initialize an empty form

   
    return render(request, 'events/register_for_event.html', {'form': form, 'event': event})


def registration_success(request):
    return render(request, 'events/registration_success.html')

def creation_success(request):
    return render(request, 'events/creation_success.html')


def event_calendar(request):
    # Get all events that are in the future
    events = Event.objects.filter(date__gte=timezone.now())
    
    # Serialize the queryset
    events_json = serializers.serialize('json', events)

    return render(request, 'events/event_calendar.html', {'events': events_json})

def token(request):
    consumer_key = 'cokWbgm8UsyS4Ar9y1HbJtQjwBfwv1OVMKEnHv2kOu37j9WY'
    consumer_secret = 'XjGA6gMATdwJzAARVE6BadKF99ZjqLL1AA9CqtZXJG4NQNYE9K1juRvKc8XG02FL'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})

def pay(request):
   return render(request, 'events/pay.html')



def stk(request):
    if request.method == "POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        
        request_data = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "Eventify",
            "TransactionDesc": "Event Charges"
        }
        
        response = requests.post(api_url, json=request_data, headers=headers)
        response_data = response.json()
        
        # Check if the payment was successful
        if response_data.get('ResponseCode') == '0':  # Assuming '0' indicates success
            return HttpResponse('<p>Success! <a href="/event_list">Go Home</a></p>')
        else:
            # If payment failed, display an error message on the same page
            return render(request, 'events/pay.html', {'error': 'Payment was not successful. Please try again.'})

    return render(request, 'events/pay.html')

def dashboard(request):
   
    # Get total events
    total_events = Event.objects.count()
    
    # Get total participants (count of all registrations)
    total_participants = Registration.objects.count()

    # Get upcoming events (filter events based on the date)
    upcoming_events = Event.objects.filter(date__gte="2024-12-13").count()

    # Get recent registrations 
    recent_registrations = Registration.objects.order_by('-registered_on')[:5]
    
    context = {
        "total_events": total_events,
        "total_participants": total_participants,
        "upcoming_events": upcoming_events,
        "recent_registrations": recent_registrations,
    }

    return render(request, 'events/dashboard.html', context)

def waiting_list_view(request):
    waiting_list = WaitingList.objects.all()
    return render(request, 'events/waiting_list.html', {'waiting_list': waiting_list})

@login_required
def join_waiting_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = WaitingListForm(request.POST)
        if form.is_valid():
            waiting_list_entry = form.save(commit=False)
            waiting_list_entry.event = event
            waiting_list_entry.save()
            # Redirect to the success page
            return redirect('waiting_list_success', event_id=event.id)
        else:
            messages.error(request, "There was an error joining the waiting list. Please try again.")
    else:
        form = WaitingListForm(initial={'event': event})
    
    return render(request, 'events/join_waiting_list.html', {'form': form, 'event': event})


def waiting_list_success(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/waiting_list_success.html', {'event': event})

# Ensure that the waiting list entries are created for the correct user
@login_required
def user_dashboard(request):
    user = request.user  # Get the current logged-in user

    # Filter the user's registrations and waiting list entries using the user object
    user_registrations = Registration.objects.filter(user=user)  # Use `user` here, not email
    user_waiting_list = WaitingList.objects.filter(user=user)  # Same for waiting list

    # Debugging: Check if data exists
    print("User Registrations:", user_registrations)
    print("User Waiting List:", user_waiting_list)

    context = {
        "user_registrations": user_registrations,
        "user_waiting_list": user_waiting_list,
    }

    return render(request, "events/user_dashboard.html", context)
