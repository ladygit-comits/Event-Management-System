import json
import os
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import requests
from requests.auth import HTTPBasicAuth
from django.contrib.auth import logout
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from events.credentials import LipanaMpesaPpassword, MpesaAccessToken
from .models import Event, Registration, WaitingList, VendorProfile
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import RSVP,Event, WaitingList
from .forms import EventForm,VendorProductForm, RegistrationForm, CategoryForm, WaitingListForm, CustomUserCreationForm, ContactUsForm, VendorRegistrationForm, VendorEditForm, AdminLoginForm, VendorLoginForm,ProductForm,UserUpdateForm, NotificationForm,ManualOrderForm,MessageForm,ReplyForm
from django.utils import timezone
from django.core import serializers
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .utils import send_confirmation_email, send_mail
from django.contrib import messages
from django.utils.text import slugify
from django.shortcuts import render
from django.http import JsonResponse
from .models import Notification,Product,Profile,User, Order, Message
from collections import defaultdict
from django.shortcuts import get_object_or_404

def role_selection_view(request):
    return render(request, 'registration/role-selection.html')

@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        profile_form = UserUpdateForm(request.POST, instance=user)
        notif_form = NotificationForm(request.POST, instance=profile)
        profile_image = request.FILES.get('profile_image')

        # Remove profile picture
        if 'remove_picture' in request.POST:
            profile.profile_image.delete(save=True)
            messages.success(request, 'Your profile picture has been removed.')
            return redirect('profile')

        if profile_form.is_valid() and notif_form.is_valid():
            profile_form.save()
            notif_form.save()

            if profile_image:
                profile.profile_image = profile_image
                profile.save()

            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        profile_form = UserUpdateForm(instance=user)
        notif_form = NotificationForm(instance=profile)

    return render(request, 'events/profile.html', {
        'profile_form': profile_form,
        'notif_form': notif_form,
        'profile': profile,
    })

# 🛑 Delete account view
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been permanently deleted.')
        return redirect('roleselection')  # or wherever you want to send them after deletion

    
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

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    # If the event is full, allow the user to join the waiting list
    waiting_list_form = None
    if event.is_full():  
        if request.method == 'POST':
            waiting_list_form = WaitingListForm(request.POST)
            if waiting_list_form.is_valid():
                instance = waiting_list_form.save(commit=False)
                instance.event = event
                instance.save()
                messages.success(request, "You have been added to the waiting list.")
                return redirect('waiting_list_success', event_id=event.id)  # Redirect after adding to waiting list
        else:
            waiting_list_form = WaitingListForm()

    context = {
        'event': event,
        'is_full': event.is_full(),
        'waiting_list_form': waiting_list_form,
    }
    return render(request, 'events/event_detail.html', context)

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

# Category view
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

# Update an existing event
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

# Delete an event
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.user:
        return redirect('event_list')
    if request.method == "POST":
        event.delete()
        return redirect('event_list')
    return render(request, 'events/delete_event.html', {'event': event})
@login_required
def register_for_event(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.is_full():
        if request.method == 'POST':
            waiting_list_form = WaitingListForm(request.POST)
            if waiting_list_form.is_valid():
                waiting_entry = waiting_list_form.save(commit=False)
                waiting_entry.event = event
                waiting_entry.user = request.user
                waiting_entry.save()

                if not request.user.is_staff:
                    messages.success(request, "You've been added to the waiting list.")

                # Redirect differently for staff
                if request.user.is_staff:
                    return redirect('admin:index')
                return redirect('event_detail', event_id=event.id)
        else:
            waiting_list_form = WaitingListForm()

        return render(request, 'events/event_detail.html', {
            'event': event,
            'waiting_list_form': waiting_list_form,
            'is_full': True
        })

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.event = event
            registration.save()

            send_confirmation_email(form.cleaned_data['email'], event.title)

            if not request.user.is_staff:
                messages.success(request, f"You have successfully registered for {event.title}. A confirmation email has been sent.")

            # Redirect differently for staff
            if request.user.is_staff:
                return redirect('admin:index')  # Send staff back to admin dashboard quietly
            # Pass event_id in the redirect
            return redirect('registration_success', event_id=event.id)  # <-- Pass event_id here
    else:
        form = RegistrationForm()

    return render(request, 'events/register_for_event.html', {
        'form': form,
        'event': event
    })



    
def registration_success(request, event_id):
    event = get_object_or_404(Event, id=event_id)  # Fetch the event using event_id
    return render(request, 'events/registration_success.html', {'event': event})
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

def pay(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/pay.html', {'event': event})
def stk(request):
    if request.method == "POST":
        phone = request.POST['phone']
        event_id = request.POST.get('event_id')
        event = get_object_or_404(Event, pk=event_id)
        
        # Convert amount to float to avoid Decimal serialization issue
        amount = float(event.price)  # Convert to float

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
            "TransactionDesc": f"Payment for {event.title}"
        }

        response = requests.post(api_url, json=request_data, headers=headers)
        response_data = response.json()

        if response_data.get('ResponseCode') == '0':
            return HttpResponse('<p>Success! <a href="/event_list">Go Home</a></p>')
        else:
            return render(request, 'events/pay.html', {'error': 'Payment was not successful. Please try again.', 'event': event})
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
            # Assign the logged-in user before saving
            waiting_list_entry = form.save(commit=False)  # Do not commit yet
            waiting_list_entry.user = request.user  # Set the user explicitly
            waiting_list_entry.save()  # Save it

            # Redirect to success page
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
    user_id = request.user.id  # Use the user ID to filter registrations and waiting list
    user_registrations = Registration.objects.filter(user_id=user_id)  # Filter by user ID
    user_waiting_list = WaitingList.objects.filter(user_id=user_id)  # Filter by user ID

    context = {
        "user_registrations": user_registrations,
        "user_waiting_list": user_waiting_list,
    }

    return render(request, "events/user_dashboard.html", context)

def contact_us(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            # Save the form to the database (optional)
            form.save()

            # Send an email (optional)
            subject = f"New Contact Us Message from {form.cleaned_data['name']}"
            message = form.cleaned_data['message']
            email_from = form.cleaned_data['email']
            recipient_list = ['admin@example.com']  # Add your admin email here

            send_mail(subject, message, email_from, recipient_list)

            # Redirect to a thank you page or display a success message
            return redirect('contact_us_success')

    else:
        form = ContactUsForm()

    return render(request, 'events/contact_us.html', {'form': form})

def contact_us_success(request):
    return render(request, 'events/contact_us_success.html')

def vendor_register(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            vendor_profile = form.save()
            login(request, vendor_profile.user)  # Login the created user
            return redirect('vendor_login')  # make sure this url name exists
        else:
            print(form.errors)
    else:
        form = VendorRegistrationForm()

    return render(request, 'events/register_vendor.html', {'form': form})


def vendor_registration_success(request):
    return render(request, 'events/vendor_registration_success.html')


def vendor_login(request):
    form = VendorLoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None
                form.add_error(None, "Invalid email or password.")

            if user:
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    if hasattr(user, 'vendorprofile'):
                        login(request, user)
                        return redirect('vendor_dashboard')
                    else:
                        form.add_error(None, "This account is not registered as a vendor.")
                else:
                    form.add_error(None, "Invalid email or password.")

    return render(request, 'events/vendor_login.html', {'form': form})

def is_vendor(user):
    return hasattr(user, 'vendor') or user.__class__.__name__ == 'Vendor'
@login_required
def check_unread_counts(request):
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    unread_messages = Message.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({
        'unread_notifications': unread_notifications,
        'unread_messages': unread_messages
    })
    
@login_required(login_url='/accounts/vendor_login/')
def vendor_dashboard(request):
    try:
        vendor = request.user.vendorprofile
    except VendorProfile.DoesNotExist:
        vendor = None

    # Handle logo upload
    if request.method == 'POST' and 'logo' in request.FILES:
        logo = request.FILES['logo']
        vendor.logo = logo
        vendor.save()
        messages.success(request, '✅ Your logo has been updated!')
        return redirect('vendor_dashboard')  # Redirect to avoid resubmitting form on refresh

    orders = Order.objects.filter(product__vendor=vendor) if vendor else []
    total_orders = orders.count()
    pending_orders = orders.filter(status='Pending').count()

    # Group recent orders by event
    grouped_orders = defaultdict(list)
    for order in orders.order_by('-date')[:10]:
        event_title = order.product.event.title if order.product and order.product.event else "Unassigned Event"
        grouped_orders[event_title].append(order)

    # Prepare sales data for the chart
    sales_data = defaultdict(int)
    for order in orders:
        day = order.date.strftime('%Y-%m-%d')
        sales_data[day] += 1

    sales_data = sorted(sales_data.items())

    form = ManualOrderForm(request.POST or None, vendor=vendor)

    return render(request, 'events/vendor_dashboard.html', {
        'vendor': vendor,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'grouped_orders': grouped_orders.items(),
        'sales_data': sales_data,
        'form': form,
    })

@login_required
def add_product(request):
    try:
        vendor = request.user.vendorprofile
    except VendorProfile.DoesNotExist:
        vendor = None

    if not vendor:
        return redirect('vendor_login')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = vendor
            product.save()
            return redirect('vendor_dashboard')  # after saving
    else:
        form = ProductForm()

    return render(request, 'events/add_product.html', {'form': form})
@login_required
def edit_vendor_profile(request):
    vendor = Vendor.objects.get(user=request.user)
    if request.method == 'POST':
        form = VendorEditForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')
    else:
        form = VendorEditForm(instance=vendor)
    return render(request, 'edit_vendor_profile.html', {'form': form})



def edit_vendor_profile(request):
    return render(request, 'events/edit_vendor_profile.html')  

def view_orders(request):
    return render(request, 'events/view_orders.html') 

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = VendorProfile.objects.get(user=request.user)
            product.save()
            return redirect('vendor_products')
    else:
        form = ProductForm()
    return render(request, 'events/add_product.html', {'form': form})

# Display notification panel
@login_required
def notification_panel(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'events/notification.html', {'notifications': notifications})


# Mark a notification as read/unread
def toggle_notification_read_status(request, notification_id, action):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    if action == "read":
        notification.is_read = True
    elif action == "unread":
        notification.is_read = False
    
    notification.save()
    return JsonResponse({'status': 'success'})

# Mark all notifications as read
@login_required
def mark_all_notifications_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def vendor_products(request):
    try:
        vendor = VendorProfile.objects.get(user=request.user)
        products = Product.objects.filter(vendor=vendor)
    except Vendor.DoesNotExist:
        products = []

    return render(request, 'events/vendor_products.html', {'products': products})


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('vendor_products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'events/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.delete()
        return redirect('vendor_products')

    return render(request, 'events/confirm_delete.html', {'product': product})

@login_required(login_url='/accounts/vendor_login/')
def add_manual_order(request):
    vendor = request.user.vendorprofile

    if request.method == 'POST':
        form = ManualOrderForm(request.POST, vendor=vendor)
        if form.is_valid():
            order = form.save(commit=False)
            order.status = 'Completed'
            order.user = request.user  # 👈 Automatically set user here
            order.save()
            messages.success(request, '✅ Sale recorded successfully!')
            return redirect('vendor_dashboard')
    else:
        form = ManualOrderForm(vendor=vendor)
    
    return render(request, 'events/add_manual_order.html', {'form': form})
@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            admin_user = User.objects.filter(is_superuser=True).first()
            message.recipient = admin_user
            message.save()

            return redirect('message_sent')
    else:
        form = MessageForm()
    return render(request, 'messages/send_message.html', {'form': form})

@login_required
def vendor_send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            admin_user = User.objects.filter(is_superuser=True).first()
            message.recipient = admin_user
            message.save()

            return redirect('message_sent')
    else:
        form = MessageForm()
    return render(request, 'messages/vendor_send_message.html', {'form': form})

@login_required
def message_sent(request):
    return render(request, 'messages/message_sent.html')

@login_required
def message_sent_admin(request):
    return render(request, 'messages/message_sent_admin.html')

@login_required
def reply_to_message(request, message_id):
    original_message = get_object_or_404(Message, id=message_id)

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.recipient = original_message.sender
            reply.subject = f"Re: {original_message.subject}"
            reply.reply_to = original_message
            reply.save()

            # ✨ Mark the original message as read
            original_message.is_read = True
            original_message.save()

            return redirect('/admin/events/message/')

    else:
        form = ReplyForm()

        # ✨ Mark as read when the admin just *opens* the reply page
        if not original_message.is_read:
            original_message.is_read = True
            original_message.save()

    return render(request, 'messages/reply_message.html', {
        'form': form,
        'original_message': original_message
    })

@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'messages/inbox.html', {'messages': messages})

@login_required
def vendor_inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'messages/vendor_inbox.html', {'messages': messages})

@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)

    # Mark as read if not already
    if not message.is_read:
        message.is_read = True
        message.save()

    return render(request, 'messages/view_message.html', {'message': message})