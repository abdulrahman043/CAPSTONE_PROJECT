
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    name          = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField()
    price         = models.DecimalField(max_digits=6, decimal_places=2)
    stripe_price_id = models.CharField(max_length=60, blank=True)   # NEW
    status        = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.duration_days} days) - {self.price} SAR"


# اشتراكات الطالب
class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, related_name='user_subscriptions')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True) # Placeholder for payment reference

    @property
    def is_active(self):
        return self.end_date >= timezone.now()

    def save(self, *args, **kwargs):
        # Calculate end_date if not set (e.g., upon creation)
        if not self.pk and self.plan and not self.end_date: # Only on creation if end_date not provided
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s subscription to {self.plan.name if self.plan else 'N/A'}"

    class Meta:
        ordering = ['-end_date'] # Show latest subscription first


# تاكيد ان الطالب يمتلك اشتراك
def has_active_subscription(user):
    if not user or not user.is_authenticated:
        return False
    return UserSubscription.objects.filter(user=user, end_date__gte=timezone.now()).exists()