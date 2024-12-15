from django.contrib import admin
from .models import Event, Category, RSVP, Registration, WaitingList

# Register Event and Category as usual
admin.site.register(Event)
admin.site.register(Category)

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event', 'status')  # Add status field
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