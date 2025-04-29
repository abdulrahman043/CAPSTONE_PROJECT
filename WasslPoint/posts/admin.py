# WasslPoint/posts/admin.py
from django.contrib import admin
from .models import TrainingOpportunity, Application, Message

admin.site.register(TrainingOpportunity)
admin.site.register(Application)
admin.site.register(Message)