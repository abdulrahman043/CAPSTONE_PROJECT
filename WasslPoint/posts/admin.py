from django.contrib import admin
from .models import TrainingOpportunity, Application, Message

# Customize the admin interface for TrainingOpportunity
@admin.register(TrainingOpportunity)
class TrainingOpportunityAdmin(admin.ModelAdmin):
    list_display = ('company', 'city', 'start_date', 'application_deadline', 'status')
    list_filter = ('company', 'city', 'status')
    search_fields = ('company__company_name', 'city__arabic_name')
    date_hierarchy = 'start_date'
    filter_horizontal = ('majors_needed',)  # Use filter_horizontal for ManyToMany fields
    fieldsets = (
        ('Opportunity Details', {
            'fields': ('company', 'majors_needed', 'city', 'start_date', 'duration', 'application_deadline', 'status')
        }),
        ('Requirements and Benefits', {
            'fields': ('requirements', 'benefits')
        }),
    )

# Customize the admin interface for Application
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'student', 'status', 'applied_at', 'updated_at')
    list_filter = ('opportunity', 'student', 'status')
    search_fields = ('opportunity__company__company_name', 'student__user__username')
    date_hierarchy = 'applied_at'
    readonly_fields = ('applied_at', 'updated_at')
    fieldsets = (
        ('Application Details', {
            'fields': ('opportunity', 'student', 'status', 'applied_at', 'updated_at')
        }),
        ('Message', {
            'fields': ('message',)
        }),
    )

# Customize the admin interface for Message
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('application', 'sender', 'sent_at')
    list_filter = ('application', 'sender')
    date_hierarchy = 'sent_at'
    readonly_fields = ('sent_at',)
    search_fields = ('application__opportunity__company__company_name', 'sender__username')
    fieldsets = (
        ('Message Details', {
            'fields': ('application', 'sender', 'content', 'sent_at')
        }),
    )
