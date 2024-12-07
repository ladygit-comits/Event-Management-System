from django.contrib import admin
from .models import Event, Category, RSVP, Registration

admin.site.register(Event)
admin.site.register(Category)
admin.site.register(RSVP)
admin.site.register(Registration)
