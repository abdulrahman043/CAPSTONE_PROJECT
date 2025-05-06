from django.urls import path
from . import views

app_name = "subscriptions"

urlpatterns = [
    path("plans/", views.subscription_plans_view, name="plans"),
    path("checkout/<int:plan_id>/", views.checkout_view, name="checkout"),  # NEW
    path("payment/success/", views.payment_success_view, name="payment_success"),
    path("payment/cancel/", views.payment_cancel_view, name="payment_cancel"),
    path("my/", views.my_subscription_view, name="my_subscription"),
]
