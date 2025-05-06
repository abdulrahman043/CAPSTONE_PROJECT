from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from notifications.models import Notification
from django.core.paginator import Paginator


@login_required
def notifications_page(request):
    qs = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)
    
    notifs = list(page_obj)
    for n in notifs:
        n.was_unread = not n.is_read
    
    qs.filter(is_read=False).update(is_read=True)
    
    return render(request, 'notifications/notifications.html', {
        'notifications': notifs,
        'page_obj': page_obj,
    })