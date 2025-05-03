# WasslPoint/subscriptions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SubscriptionPlan, UserSubscription, has_active_subscription
from django.utils import timezone
from datetime import timedelta

@login_required
def subscription_plans_view(request):
    # You can add logic here later to perhaps redirect users with active subscriptions
    # or tailor the view based on their current subscription status.

    plans = SubscriptionPlan.objects.filter(status=True).order_by('price')
    current_subscription = UserSubscription.objects.filter(user=request.user, end_date__gte=timezone.now()).first()
    context = {
        'plans': plans,
        'current_subscription': current_subscription,
    }
    # *** Use the specified template path ***
    return render(request, 'Subscription/plans.html', context)

@login_required
def payment_view(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id, status=True)

    # Prevent subscribing again if already active
    if has_active_subscription(request.user):
         messages.warning(request, "لديك اشتراك فعال بالفعل. الترقيات غير مدعومة بعد.") # "You already have an active subscription. Upgrades are not yet supported."
         return redirect('subscriptions:plans')

    if request.method == 'POST':
        # --- Placeholder Payment Logic ---
        # In a real application, integrate with a payment gateway here.
        try:
            # Simulate successful payment
            payment_reference = f"SIM_{timezone.now().strftime('%Y%m%d%H%M%S')}_{request.user.id}" # Dummy ID

            start_time = timezone.now()
            end_time = start_time + timedelta(days=plan.duration_days)

            # Create the new subscription record
            UserSubscription.objects.create(
                user=request.user,
                plan=plan,
                start_date=start_time,
                end_date=end_time,
                payment_id=payment_reference # Store the dummy ID
            )
            messages.success(request, f"تم الاشتراك بنجاح في {plan.name}!") # Subscribed successfully to {plan.name}!
            return redirect('subscriptions:payment_success') # Redirect to success page
        except Exception as e:
             # Log the error in a real app: log.error(f"Subscription error for user {request.user.id}: {e}")
             messages.error(request, f"حدث خطأ أثناء معالجة اشتراكك: {e}") # "An error occurred while processing your subscription: {e}"
             return redirect('subscriptions:plans')
        # --- End Placeholder Payment Logic ---

    context = {'plan': plan}
    # *** Use the specified template path ***
    return render(request, 'Subscription/payment.html', context)

@login_required
def payment_success_view(request):
    # Simple success page
    # *** Use the specified template path ***
    return render(request, 'Subscription/payment_success.html')

@login_required
def payment_cancel_view(request):
    # Simple cancellation page
    messages.info(request, "تم إلغاء عملية الدفع الخاصة بك.") # "Your payment process was cancelled."
    # *** Use the specified template path ***
    return render(request, 'Subscription/payment_cancel.html')

@login_required
def my_subscription_view(request):
    # Get the most recent subscription (active or expired)
    subscription = UserSubscription.objects.filter(user=request.user).order_by('-end_date').first()
    # Get all past subscriptions for history display
    history = UserSubscription.objects.filter(user=request.user).order_by('-start_date')
    context = {
        'subscription': subscription, # The latest one
        'history': history,
         'is_currently_active': has_active_subscription(request.user), # Check if the latest is actually active now
    }
    # *** Use the specified template path ***
    return render(request, 'Subscription/my_subscription.html', context)