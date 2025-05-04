from django.shortcuts import render , redirect
from django.http import HttpRequest
from django.core.mail import send_mail
from django.conf import settings
from posts.models import TrainingOpportunity # Import Opportunity model
from django.utils import timezone
# Create your views here.
def home_view(request:HttpRequest):
    return render(request,'main/home.html')

def training_view(request:HttpRequest):
    active_opportunities = TrainingOpportunity.objects.filter(
        status=TrainingOpportunity.Status.ACTIVE,
        application_deadline__gte=timezone.now().date()
        )
    return render(request,'main/training.html',{"opportunities":active_opportunities})

def about_view(request:HttpRequest):
    return render(request,'main/about.html')

def contact_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"From: {email}\n\nMessage:\n{message}"

        send_mail(
            subject,
            full_message,
            settings.EMAIL_HOST_USER,  # من الإيميل
            ['wasslpoint@gmail.com'],  # إلى الإيميل
            fail_silently=False,
        )
        return render(request, 'main/contact.html', {'success': True}) 

    return render(request, 'main/contact.html')

def company_view(request:HttpRequest):
    """ Displays general company info and lists active opportunities """
    active_opportunities = TrainingOpportunity.objects.filter(
        status=TrainingOpportunity.Status.ACTIVE,
        application_deadline__gte=timezone.now().date()
        ).select_related('company','city').order_by('-created_at')[:10] # Limit for display

    context = {
        'opportunities': active_opportunities
    }
    return render(request,'main/company.html', context)

