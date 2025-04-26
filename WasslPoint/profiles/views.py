from django.shortcuts import render,redirect
from django.http import HttpRequest
from .models import StudentProfile,PersonalInformation,Country,ContactInformation,City,Experience,Skill,Language,Education,Certification,Major,CompanyProfile
from datetime import date
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# Create your views here.
@login_required
def profile_view(request:HttpRequest):
    try:
        profile=request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('main:home_view')
    profile = request.user.student_profile
    if request.method=='POST':
        if 'personal-submit' in request.POST:
            personal, _ = PersonalInformation.objects.get_or_create(profile=profile)
            personal.full_name_en  = request.POST.get('name')
            personal.full_name_ar  = request.POST.get('full_name_ar')
            personal.date_of_birth = request.POST.get('date_of_birth') 
            personal.gender        = request.POST.get('gender')
            nat_id = request.POST.get('nationality')
            if nat_id:
                personal.nationality = Country.objects.get(pk=nat_id)
            personal.save()
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
    countries = Country.objects.filter(status=True) 
    majors = Major.objects.filter(status=True) 
    cities = City.objects.filter(status=True) 
    context = {
    "gender_choices": PersonalInformation.Gender.choices,
    "language_choices": Language.Proficiency.choices,
    'language_name_choices': Language._meta.get_field('name').choices,
    "gpa_scale_choices": Education.GPA_SCALE.choices,
    "degree_choices": Education.Degree.choices,
    "proficiency_choices": Skill.Proficiency.choices,
    'majors':majors,
    'countries':countries,
    'cities':cities,
}
    return render(request,'profiles/profile.html',context)
@login_required
@require_POST
def delate_exp(request:HttpRequest,exp_id):
    try:
        experience=Experience.objects.get(pk=exp_id)
        experience.delete()
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def edit_exp(request:HttpRequest,exp_id):
    try:
        if request.method=='POST':

            experience=Experience.objects.get(pk=exp_id)
           
            experience.job_title  = request.POST.get('job_title')
            experience.company_name  = request.POST.get('company_name')
            experience.description  = request.POST.get('description')
            start_date = request.POST.get('start_date')   
            if start_date:
                year, month = map(int, start_date.split('-'))
                experience.start_date = date(year, month, 1)
            end_date = request.POST.get('end_date')   
            if end_date:
                year, month = map(int, end_date.split('-'))
                experience.end_date = date(year, month, 1)
                    
            experience.save()
            return redirect('profiles:profile_view')
        
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def delate_skill(request:HttpRequest,skill_id):
    try:
        skill=Skill.objects.get(pk=skill_id)
        skill.delete()
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def edit_skill(request:HttpRequest,skill_id):
    try:
        if request.method=='POST':

            skill=Skill.objects.get(pk=skill_id)
           
            skill.name  = request.POST.get('name')
            skill.proficiency  = request.POST.get('proficiency')
                    
            skill.save()
            return redirect('profiles:profile_view')
        
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST

def delate_language(request:HttpRequest,lan_id):
    try:
        language=Language.objects.get(pk=lan_id)
        language.delete()
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def edit_language(request:HttpRequest,lan_id):
    try:
        if request.method=='POST':

            language=Language.objects.get(pk=lan_id)
           
            language.name  = request.POST.get('name')
            language.proficiency  = request.POST.get('proficiency')
                    
            language.save()
            return redirect('profiles:profile_view')
        
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def delate_edu(request:HttpRequest,edu_id):
    try:
        education=Education.objects.get(pk=edu_id)
        education.delete()
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def edit_edu(request:HttpRequest,edu_id):
    try:
        if request.method=='POST':

            education = Education.objects.get(pk=edu_id)
            education.university  = request.POST.get('university')
            education.degree  = request.POST.get('degree')
            education.GPA  = request.POST.get('gpa')
            education.gpa_scale  = request.POST.get('gpa_scale')
            graduating_date = request.POST.get('graduating_date') 
            major_id = request.POST.get('major')
            if major_id:
                education.major = Major.objects.get(pk=major_id)  
            if graduating_date:
                year, month = map(int, graduating_date.split('-'))
                education.graduating_date = date(year, month, 1)
           
                    
            education.save()
            return redirect('profiles:profile_view')
        
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def delate_cert(request:HttpRequest,cert_id):
    try:
        certification=Certification.objects.get(pk=cert_id)
        certification.delete()
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def edit_cert(request:HttpRequest,cert_id):
    try:
        if request.method=='POST':

            certification = Certification.objects.get(pk=cert_id)
            certification.name  = request.POST.get('name')
            certification.issuer  = request.POST.get('issuer')
            issue_date = request.POST.get('issue_date') 
           
            if issue_date:
                year, month = map(int, issue_date.split('-'))
                certification.issue_date = date(year, month, 1)
            expiry_date = request.POST.get('expiry_date') 
           
            if expiry_date:
                year, month = map(int, expiry_date.split('-'))
                certification.expiry_date = date(year, month, 1)
            if 'certificate_file' in request.FILES:
                certification.certificate_file=request.FILES['certificate_file']
                    
            certification.save()
            return redirect('profiles:profile_view')
        
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def add_cert(request:HttpRequest):
    try:
        if request.method=='POST':

            certification = Certification.objects.create(profile=request.user.student_profile)
            certification.name  = request.POST.get('name')
            certification.issuer  = request.POST.get('issuer')
            issue_date = request.POST.get('issue_date') 
           
            if issue_date:
                year, month = map(int, issue_date.split('-'))
                certification.issue_date = date(year, month, 1)
            expiry_date = request.POST.get('expiry_date') 
           
            if expiry_date:
                year, month = map(int, expiry_date.split('-'))
                certification.expiry_date = date(year, month, 1)
            print(request.FILES)
            if 'certificate_file' in request.FILES:
                print(1)
                certification.certificate_file=request.FILES['certificate_file']
                    
            certification.save()
            return redirect('profiles:profile_view')
        
    
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def add_exp(request:HttpRequest):
    try:
        if request.method=='POST':
            experience = Experience.objects.create(profile=request.user.student_profile)

            experience.job_title  = request.POST.get('job_title')
            experience.company_name  = request.POST.get('company_name')
            experience.description  = request.POST.get('description')
            start_date = request.POST.get('start_date')   
            if start_date:
                year, month = map(int, start_date.split('-'))
                experience.start_date = date(year, month, 1)
            end_date = request.POST.get('end_date')   
            if end_date:
                year, month = map(int, end_date.split('-'))
                experience.end_date = date(year, month, 1)
                        
            experience.save()
            return redirect('profiles:profile_view')
    except Exception as e:
        print(e)
        
    return redirect('profiles:profile_view')
@login_required
@require_POST
def add_skill(request:HttpRequest):
    try:
        if request.method=='POST':
            skill = Skill.objects.create(profile=request.user.student_profile)
            skill.name  = request.POST.get('name')
            skill.proficiency  = request.POST.get('proficiency')          
            skill.save()
            return redirect('profiles:profile_view')
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def add_language(request:HttpRequest):
    try:
        if request.method=='POST':
            language = Language.objects.create(profile=request.user.student_profile)
            language.name  = request.POST.get('name')
            language.proficiency  = request.POST.get('proficiency')
            language.save()
            return redirect('profiles:profile_view')
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def add_edu(request:HttpRequest):
    try:
        if request.method=='POST':
            education = Education.objects.create(profile=request.user.student_profile)
            education.university  = request.POST.get('university')
            education.degree  = request.POST.get('degree')
            education.GPA  = request.POST.get('gpa')
            education.gpa_scale  = request.POST.get('gpa_scale')
            graduating_date = request.POST.get('graduating_date') 
            major_id = request.POST.get('major')
            if major_id:
                education.major = Major.objects.get(pk=major_id)  
            if graduating_date:
                year, month = map(int, graduating_date.split('-'))
                education.graduating_date = date(year, month, 1)    
            education.save()
            return redirect('profiles:profile_view')
      
    except Exception as e:
        print(e)
    return redirect('profiles:profile_view')


@login_required
def company_profile_view(request:HttpRequest):
    if not request.user.is_authenticated:
        return redirect('main:home_view')

    try:
        profile=request.user.company_profile
    except CompanyProfile.DoesNotExist:
        return redirect('main:home_view')

        
    return render(request,'profiles/company_profile.html')
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.contrib.auth.decorators import login_required

@login_required
def export_cv_pdf(request):
    pass
    # try:
    #     html=render_to_string('profiles/cv_pdf.html',{'request':request})
    #     response=HttpResponse(content_type='application/pdf')
    #     response['Content-Disposition']=f'filename={request.user.username}_cv.pdf'
    #     HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(response)
    #     return response

    # except Exception as e:
    #     print(e)
