from django.shortcuts import render,redirect
from django.http import HttpRequest
from .models import PersonalInformation,Country,ContactInformation,City,Experience
from datetime import date
# Create your views here.
def profile_view(request:HttpRequest):
    profile = request.user.student_profile


    if request.method=='POST':
        if 'personal-submit' in request.POST:
            personal, _ = PersonalInformation.objects.get_or_create(profile=profile)

            personal.full_name_en  = request.POST.get('name', personal.full_name_en)
            personal.full_name_ar  = request.POST.get('full_name_ar', personal.full_name_ar)
            personal.date_of_birth = request.POST.get('date_of_birth') or None
            personal.gender        = request.POST.get('gender', personal.gender)
            nat_id = request.POST.get('nationality')
            if nat_id:
                personal.nationality = Country.objects.get(pk=nat_id)
            personal.save()
            print(personal.full_name_ar)
            return redirect('profiles:profile_view')
        if 'contact-submit' in request.POST:
            contact, _ = ContactInformation.objects.get_or_create(profile=profile)

            contact.email  = request.POST.get('email')
            contact.phone  = request.POST.get('phone')
            contact.address_line = request.POST.get('address_line') 
            city_id = request.POST.get('city')
            if city_id:
                contact.city = City.objects.get(pk=city_id)
            contact.save()
            return redirect('profiles:profile_view')
        if 'experience-submit' in request.POST:
            experience = Experience.objects.create(profile=profile)

            experience.job_title  = request.POST.get('job_title')
            experience.company_name  = request.POST.get('company_name')
            experience.description  = request.POST.get('description')
            start_date = request.POST.get('start_date')   # e.g. "2025-04"
            if start_date:
                year, month = map(int, start_date.split('-'))
                experience.start_date = date(year, month, 1)
            end_date = request.POST.get('end_date')   # e.g. "2025-04"
            if end_date:
                year, month = map(int, end_date.split('-'))
                experience.end_date = date(year, month, 1)
                    
            experience.save()
            return redirect('profiles:profile_view')
            
    countries = Country.objects.filter(status=True) 
    cities = City.objects.filter(status=True) 


    context = {
    "gender_choices": PersonalInformation.Gender.choices,
    'countries':countries,
    'cities':cities,
}
    return render(request,'profiles/profile.html',context)

def delate_exp(request:HttpRequest,exp_id):
    try:
        experience=Experience.objects.get(pk=exp_id)
        experience.delete()
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')