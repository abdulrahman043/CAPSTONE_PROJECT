# WasslPoint/subscriptions/urls.py
from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.subscription_plans_view, name='plans'),
    path('payment/<int:plan_id>/', views.payment_view, name='payment'),
    path('payment/success/', views.payment_success_view, name='payment_success'), # Placeholder
    path('payment/cancel/', views.payment_cancel_view, name='payment_cancel'),   # Placeholder
    path('my/', views.my_subscription_view, name='my_subscription'),
]