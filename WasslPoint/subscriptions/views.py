# WasslPoint/subscriptions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SubscriptionPlan, UserSubscription, has_active_subscription
from django.utils import timezone
from datetime import timedelta

@login_required
def subscription_plans_view(request):
    # Redirect if already subscribed? Or allow upgrades? For now, just show plans.
    # if has_active_subscription(request.user):
    #     messages.info(request, "You already have an active subscription.")
    #     return redirect('subscriptions:my_subscription') # Redirect to manage subscription page

    plans = SubscriptionPlan.objects.filter(status=True).order_by('price')
    current_subscription = UserSubscription.objects.filter(user=request.user, end_date__gte=timezone.now()).first()
    context = {
        'plans': plans,
        'current_subscription': current_subscription,
    }
    return render(request, 'subscriptions/plans.html', context)

@login_required
def payment_view(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id, status=True)

    if has_active_subscription(request.user):
         messages.warning(request, "You already have an active subscription. Upgrades are not yet supported.")
         return redirect('subscriptions:plans')

    if request.method == 'POST':
        # --- Placeholder Payment Logic ---
        # In a real application, you would integrate with a payment gateway here (Stripe, PayPal, etc.)
        # Upon successful payment confirmation from the gateway:
        try:
            # Simulate successful payment
            payment_reference = f"SIM_{timezone.now().strftime('%Y%m%d%H%M%S')}_{request.user.id}" # Dummy ID

            start_time = timezone.now()
            end_time = start_time + timedelta(days=plan.duration_days)

            UserSubscription.objects.create(
                user=request.user,
                plan=plan,
                start_date=start_time,
                end_date=end_time,
                payment_id=payment_reference # Store the dummy ID
            )
            messages.success(request, f"Successfully subscribed to {plan.name}!")
            # In a real app, redirect would come from gateway callback often
            return redirect('subscriptions:payment_success')
        except Exception as e:
             messages.error(request, f"An error occurred while processing your subscription: {e}")
             return redirect('subscriptions:plans')
        # --- End Placeholder Payment Logic ---

    context = {'plan': plan}
    return render(request, 'subscriptions/payment.html', context) # Simple confirmation/payment page

@login_required
def payment_success_view(request):
    # Simple success page
    return render(request, 'subscriptions/payment_success.html')

@login_required
def payment_cancel_view(request):
    # Simple cancellation page
    messages.info(request, "Your payment process was cancelled.")
    return render(request, 'subscriptions/payment_cancel.html')

@login_required
def my_subscription_view(request):
    subscription = UserSubscription.objects.filter(user=request.user).order_by('-end_date').first()
    history = UserSubscription.objects.filter(user=request.user).order_by('-start_date') # Get all history
    context = {
        'subscription': subscription,
        'history': history,
         'is_currently_active': has_active_subscription(request.user),
    }
    return render(request, 'subscriptions/my_subscription.html', context)