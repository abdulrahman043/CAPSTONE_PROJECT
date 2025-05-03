# WasslPoint/posts/admin.py
from django.contrib import admin
from .models import TrainingOpportunity, Application, Message

# Customize the admin interface for TrainingOpportunity
@admin.register(TrainingOpportunity)
class TrainingOpportunityAdmin(admin.ModelAdmin):
    list_display = ('company', 'city', 'start_date', 'application_deadline', 'status', 'created_at') # Added created_at
    list_filter = ('company', 'city', 'status', 'start_date', 'application_deadline') # Added date filters
    search_fields = ('company__company_name', 'city__arabic_name', 'requirements', 'benefits') # Added search fields
    date_hierarchy = 'created_at' # Changed to created_at for better hierarchy
    filter_horizontal = ('majors_needed',)
    list_per_page = 20 # Added pagination
    fieldsets = (
        ('Opportunity Details', {
            'fields': ('company', 'majors_needed', 'city', 'start_date', 'duration', 'application_deadline', 'status')
        }),
        ('Requirements and Benefits', {
            'fields': ('requirements', 'benefits')
        }),
         ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
             'classes': ('collapse',) # Make collapsible
        }),
    )
    readonly_fields = ('created_at', 'updated_at') # Add timestamps here


# Customize the admin interface for Application
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'student', 'status', 'applied_at', 'updated_at') # Corrected field names
    list_filter = ('status', 'applied_at', 'opportunity__city', 'opportunity__company') # Improved filters
    search_fields = ('opportunity__company__company_name', 'student__user__username', 'student__user__email', 'message') # Improved search
    date_hierarchy = 'applied_at' # Corrected field name
    readonly_fields = ('applied_at', 'updated_at') # Corrected field names
    list_per_page = 25 # Added pagination
    fieldsets = (
        ('Application Details', {
            'fields': ('opportunity', 'student', 'status')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
             'classes': ('collapse',)
        }),
    )
    # Autocomplete fields can improve usability if you have many opportunities/students
    # autocomplete_fields = ['opportunity', 'student']


# Customize the admin interface for Message
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('application', 'sender', 'sent_at', 'content_preview') # Added preview
    list_filter = ('sender', 'sent_at', 'application__opportunity__company') # Improved filters
    date_hierarchy = 'sent_at'
    readonly_fields = ('sent_at',)
    search_fields = ('application__opportunity__company__company_name', 'sender__username', 'content')
    list_per_page = 30 # Added pagination
    fieldsets = (
        ('Message Details', {
            'fields': ('application', 'sender', 'content')
        }),
         ('Timestamps', {
            'fields': ('sent_at',),
             'classes': ('collapse',)
        }),
    )
    # autocomplete_fields = ['application', 'sender']

    def content_preview(self, obj):
        # Show a short preview of the message content
        from django.utils.html import escape
        from django.utils.text import Truncator
        return Truncator(escape(obj.content)).chars(50)
    content_preview.short_description = 'Content Preview'