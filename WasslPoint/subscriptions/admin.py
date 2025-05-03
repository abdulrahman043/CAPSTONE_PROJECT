# WasslPoint/subscriptions/admin.py
from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'price', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'description')

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active', 'payment_id')
    list_filter = ('plan', 'start_date', 'end_date')
    search_fields = ('user__username', 'plan__name', 'payment_id')
    readonly_fields = ('created_at', 'updated_at')

    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True # Display as icon