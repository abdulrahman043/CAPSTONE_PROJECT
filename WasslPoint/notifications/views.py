from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from notifications.models import Notification

@login_required
def notifications_page(request):
    # fetch all notifications, newest first
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')

    # mark any unread as read
    notifs.filter(is_read=False).update(is_read=True)

    return render(request, 'notifications/notifications.html', {
        'notifications': notifs
    })
