import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import SubscriptionPlan, UserSubscription, has_active_subscription

# اربط مفتاح Stripe السرّي فور تحميل الملف
stripe.api_key = settings.STRIPE_SECRET_KEY
def _ensure_price(plan):
    """إنشاء Product/Price على Stripe إذا لم يوجد، ثم إرجاع price_id."""
    if plan.stripe_price_id:
        return plan.stripe_price_id

    # ❶ إنشاء منتج
    product = stripe.Product.create(name=plan.name)

    # ❷ إنشاء سعر one‑time (القيمة بالهللات)
    price = stripe.Price.create(
        product     = product.id,
        unit_amount = int(plan.price * 100),  # 100 هللة = 1 SAR
        currency    = "sar",
    )

    # ❸ حفظ المعرّف في قاعدة البيانات
    plan.stripe_price_id = price.id
    plan.save(update_fields=["stripe_price_id"])

    return price.id

@login_required
def subscription_plans_view(request):
    plans = (
        SubscriptionPlan.objects
        .filter(status=True)
        .order_by("price")
    )
    current_subscription = (
        UserSubscription.objects
        .filter(user=request.user, end_date__gte=timezone.now())
        .first()
    )
    return render(
        request, "Subscription/plans.html",
        {"plans": plans, "current_subscription": current_subscription}
    )

@login_required
def checkout_view(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id, status=True)

    if has_active_subscription(request.user):
        messages.warning(request, "لديك اشتراك نشط بالفعل.")
        return redirect("subscriptions:plans")

    try:
        price_id = _ensure_price(plan)               

        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            client_reference_id=str(request.user.id),
            metadata={"plan_id": plan.id},
            success_url=request.build_absolute_uri(
                reverse("subscriptions:payment_success")
            ) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(
                reverse("subscriptions:payment_cancel")
            ),
        )

        return redirect(session.url, code=303)

    except Exception as exc:
        messages.error(request, f"تعذّر إنشاء جلسة الدفع: {exc}")
        return redirect("subscriptions:plans")

@login_required
def payment_success_view(request):
    """
    صفحة نجاح بسيطة (Stripe عاد المستخدم بالفعل).
    لا ننشئ الاشتراك هنا بل في الـ webhook.
    """
    return render(request, "Subscription/payment_success.html")


@login_required
def payment_cancel_view(request):
    messages.info(request, "تم إلغاء عملية الدفع الخاصة بك.")
    return render(request, "Subscription/payment_cancel.html")


@login_required
def my_subscription_view(request):
    latest = (
        UserSubscription.objects
        .filter(user=request.user)
        .order_by("-end_date")
        .first()
    )
    history = (
        UserSubscription.objects
        .filter(user=request.user)
        .order_by("-start_date")
    )
    return render(
        request, "Subscription/my_subscription.html",
        {
            "subscription": latest,
            "history": history,
            "is_currently_active": has_active_subscription(request.user),
        },
    )
