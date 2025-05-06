from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from notifications.models import Notification


@login_required
def notifications_page(request):
    # 1. جلب الإشعارات
    qs = Notification.objects.filter(user=request.user).order_by('-created_at')
    # 2. حول الـ QuerySet إلى قائمة لكي نضيف لها خاصية was_unread
    notifs = list(qs)
    # 3. علمها بناءً على is_read
    for n in notifs:
        n.was_unread = not n.is_read
    # 4. بعد العلامة، حدّث جميع الغير مقروءة لتصبح مقروءة
    qs.filter(is_read=False).update(is_read=True)

    return render(request, 'notifications/notifications.html', {
        'notifications': notifs
    })