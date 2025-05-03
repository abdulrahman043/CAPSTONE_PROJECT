# WasslPoint/subscriptions/urls.py
from django.urls import path
from . import views

# Define the namespace for this app's URLs
app_name = 'subscriptions'

urlpatterns = [
    #لعرض الاشتراكات
    path('plans/', views.subscription_plans_view, name='plans'),
    #لدفع قيمة الاشتراك
    path('payment/<int:plan_id>/', views.payment_view, name='payment'),
    #عملية ناحجه
    path('payment/success/', views.payment_success_view, name='payment_success'),
    #إلغاء العملية
    path('payment/cancel/', views.payment_cancel_view, name='payment_cancel'),
    #لعرض اشتراكاتي
    path('my/', views.my_subscription_view, name='my_subscription'),
]