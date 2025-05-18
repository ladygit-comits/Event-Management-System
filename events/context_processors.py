# events/context_processors.py

from .models import Notification, Message

def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        count = 0
    return {'unread_notifications_count': count}

def notification_and_message_counts(request):
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        unread_messages_count = Message.objects.filter(recipient=request.user, is_read=False).count()
    else:
        unread_notifications_count = 0
        unread_messages_count = 0

    return {
        'unread_notifications_count': unread_notifications_count,
        'unread_messages_count': unread_messages_count
    }