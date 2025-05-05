from django.urls import path
from notifications.views import notifications_page

app_name = 'notifications'

urlpatterns = [
    path('', notifications_page, name='notifications_page'),
]
