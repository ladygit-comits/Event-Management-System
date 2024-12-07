from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(to_email, event_name):
    subject = f"Registration Confirmation for {event_name}"
    message = f"Thank you for registering for {event_name}. We look forward to seeing you there!"
    from_email = settings.DEFAULT_FROM_EMAIL
    
    send_mail(subject, message, from_email, [to_email])
