from .models import Notification

def unread_notification_count(request):
    # Check for unread notifications and return the count
    return {
        'unread_notifications_count': Notification.objects.filter(is_read=False).count()
    }
