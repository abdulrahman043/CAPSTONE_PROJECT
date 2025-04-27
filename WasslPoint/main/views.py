from django.shortcuts import render , redirect
from django.http import HttpRequest
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.
def home_view(request:HttpRequest):
    return render(request,'main/home.html')

def training_view(request:HttpRequest):
    return render(request,'main/training.html')

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
    return render(request,'main/company.html')

