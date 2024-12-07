from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Registration
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import RSVP,Event
from .forms import EventForm, RegistrationForm, CategoryForm
from django.utils import timezone
from django.core import serializers
from .forms import AdminLoginForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
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
    event = Event.objects.get(pk=pk)
    
    # Check if the request is a POST (form submission)
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save the registration with the current logged-in user and event
            registration = form.save(commit=False)  # Don't save yet
            registration.event = event  # Associate the event with the registration
            registration.save()  # Save the registration

            # Redirect to a registration success page or event detail page
            return redirect('registration_success')  # Adjust to your success URL
    else:
        form = RegistrationForm()  # Initialize an empty form

    # Render the registration page with the form and event data
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


