from django.contrib import admin
from .models import Event, Category, RSVP, Registration

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
    list_display = ('name', 'email', 'event', 'status')  # Add status field
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
