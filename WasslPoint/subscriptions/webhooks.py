import json
import stripe
from datetime import datetime, timedelta, timezone as dt_timezone

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from django.contrib.auth.models import User
from .models import SubscriptionPlan, UserSubscription

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    """
    يستقبل كل أحداث Stripe.
    نهتم هنا بـ checkout.session.completed فقط.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        _create_subscription_from_session(session)


    return HttpResponse(status=200)



def _create_subscription_from_session(session: dict):
    """
    يحوّل جلسة Checkout إلى سجل UserSubscription.
    • metadata.plan_id أضفناه عند إنشاء الجلسة.
    • client_reference_id = user.id   أضفناه عند إنشاء الجلسة.
    """
    try:
        user_id  = int(session["client_reference_id"])
        plan_id  = int(session["metadata"]["plan_id"])
        intent   = session.get("payment_intent")  
    except (KeyError, ValueError):
        return  

    if UserSubscription.objects.filter(payment_id=intent).exists():
        return

    user = User.objects.filter(id=user_id).first()
    plan = SubscriptionPlan.objects.filter(id=plan_id, status=True).first()
    if not (user and plan):
        return

    start = timezone.now()
    end   = start + timedelta(days=plan.duration_days)

    UserSubscription.objects.create(
        user       = user,
        plan       = plan,
        start_date = start,
        end_date   = end,
        payment_id = intent
    )
