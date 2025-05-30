from django.contrib import admin
from .models import Event, Category, RSVP, Registration, WaitingList, ContactUs, Product, Notification, Profile, VendorProfile,Message
from django.utils.html import format_html
from django.urls import reverse


# Register Event and Category
admin.site.register(Event)
admin.site.register(Category)
admin.site.register(ContactUs)


@admin.register(VendorProfile)

class VendorAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'contact_person', 'phone_number', 'get_email']

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event', 'status')  
    list_filter = ('status', 'event')  # Filters for easy management
    search_fields = ('name', 'email')  # Search for specific users by name/email

    actions = ['approve_rsvps', 'decline_rsvps']  # Custom actions for bulk updates

    def approve_rsvps(self, request, queryset):
        # Bulk approve selected RSVPs
        queryset.update(status='approved')
        self.message_user(request, "Selected RSVPs have been approved.")

    approve_rsvps.short_description = "Approve selected RSVPs"

    def decline_rsvps(self, request, queryset):
        # Bulk decline selected RSVPs
        queryset.update(status='declined')
        self.message_user(request, "Selected RSVPs have been declined.")

    decline_rsvps.short_description = "Decline selected RSVPs"

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event', 'status')  
    list_filter = ('status', 'event')  # Filters for easy management
    search_fields = ('name', 'email')  # Search for specific users by name/email

    actions = ['approve_registrations', 'decline_registrations']  # Custom actions for bulk updates

    def approve_registrations(self, request, queryset):
        # Bulk approve selected registrations
        queryset.update(status='approved')
        self.message_user(request, "Selected registrations have been approved.")

    approve_registrations.short_description = "Approve selected registrations"

    def decline_registrations(self, request, queryset):
        # Bulk decline selected registrations
        queryset.update(status='declined')
        self.message_user(request, "Selected registrations have been declined.")

    decline_registrations.short_description = "Decline selected registrations"

@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event', 'phone_number', 'created_at', 'status') 
    list_filter = ('status', 'created_at', 'event')  # Filters for easy management
    search_fields = ('name', 'email', 'event__title')  # Search for specific users by name/email

    actions = ['approve_waiting_list', 'decline_waiting_list']  # Custom actions for bulk updates

    def approve_waiting_list(self, request, queryset):
        # Bulk approve selected waiting list entries
        queryset.update(status='approved')
        self.message_user(request, "Selected waiting list entries have been approved.")

    approve_waiting_list.short_description = "Approve selected waiting list entries"

    def decline_waiting_list(self, request, queryset):
        # Bulk decline selected waiting list entries
        queryset.update(status='declined')
        self.message_user(request, "Selected waiting list entries have been declined.")

    decline_waiting_list.short_description = "Decline selected waiting list entries"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'created_at', 'is_read', 'reply_link']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__email', 'subject', 'body']

    def reply_link(self, obj):
        if not obj.reply_to and obj.sender != obj.recipient:
            url = reverse('reply_message', args=[obj.id])
            return format_html('<a class="button" href="{}">Reply</a>', url)
        return "-"
    reply_link.short_description = 'Reply'