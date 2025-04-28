from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpRequest,HttpResponse
from .models import StudentProfile,PersonalInformation,Country,ContactInformation,City,Experience,Skill,Language,Education,Certification,Major,CompanyProfile,Industry
from datetime import date
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

# Create your views here.
@login_required
def get_target_profile(request, user_id=None):
    if user_id:
        print(user_id)
        if not request.user.is_staff:
            raise PermissionDenied
        user = get_object_or_404(User, pk=user_id)
        return user.student_profile
    return request.user.student_profile
@login_required
def profile_view(request:HttpRequest,user_id=None):
    if user_id:
        print(user_id)
        if not request.user.is_staff:
            return redirect("main:home_view")
        user = get_object_or_404(User, pk=user_id)
        profile=user.student_profile
    else:
        try:
            profile=request.user.student_profile
        except StudentProfile.DoesNotExist:
            return redirect('main:home_view')
    if request.method=='POST':
        if 'personal-submit' in request.POST:
            personal, _ = PersonalInformation.objects.get_or_create(profile=profile)
            personal.full_name  = request.POST.get('name')
            personal.date_of_birth = request.POST.get('date_of_birth') or None
            personal.gender        = request.POST.get('gender')
            nat_id = request.POST.get('nationality')
            if nat_id:
                personal.nationality = Country.objects.get(pk=nat_id)
            personal.save()
            return redirect(
                'profiles:profile_view_admin' if user_id else 'profiles:profile_view',
                user_id=profile.user.id if user_id else None
            )
        if 'contact-submit' in request.POST:
            contact, _ = ContactInformation.objects.get_or_create(profile=profile)

            contact.email  = request.POST.get('email')
            contact.phone  = request.POST.get('phone')
            contact.address_line = request.POST.get('address_line') 
            city_id = request.POST.get('city')
            if city_id:
                contact.city = City.objects.get(pk=city_id)
            contact.save()
            return redirect(
                'profiles:profile_view_admin' if user_id else 'profiles:profile_view',
                user_id=profile.user.id if user_id else None
            )  
    countries = Country.objects.filter(status=True) 
    majors = Major.objects.filter(status=True) 
    cities = City.objects.filter(status=True) 
    context = {
    'admin_view':bool(user_id),
    'profile':profile,
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
def delate_exp(request:HttpRequest,exp_id,user_id=None):
    try:
        profile = get_target_profile(request, user_id)

        experience = get_object_or_404(Experience, pk=exp_id, profile=profile)
        experience.delete()
    
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def edit_exp(request:HttpRequest,exp_id,user_id=None):
    try:
        if request.method=='POST':

            profile = get_target_profile(request, user_id)

            experience = get_object_or_404(Experience, pk=exp_id, profile=profile)
           
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
        
    
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def delate_skill(request:HttpRequest,skill_id,user_id=None):
    try:
        profile = get_target_profile(request, user_id)
        skill = get_object_or_404(Skill, pk=skill_id, profile=profile)
        skill.delete()
    
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def edit_skill(request:HttpRequest,skill_id,user_id=None):
    try:
        if request.method=='POST':

            profile = get_target_profile(request, user_id)
            skill = get_object_or_404(Skill, pk=skill_id, profile=profile)
            print(request.POST)
            skill.name  = request.POST.get('name')
            skill.proficiency  = request.POST.get('proficiency')
            
                    
            skill.save()
        
    
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST

def delate_language(request:HttpRequest,lan_id,user_id=None):
    try:
        profile = get_target_profile(request, user_id)
        language = get_object_or_404(Language, pk=lan_id, profile=profile)
        language.delete()
    
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def edit_language(request:HttpRequest,lan_id,user_id=None):
    try:
        if request.method=='POST':

            profile = get_target_profile(request, user_id)
            language = get_object_or_404(Language, pk=lan_id, profile=profile)           
            language.name  = request.POST.get('name')
            language.proficiency  = request.POST.get('proficiency')
                    
            language.save()
        
    
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def delate_edu(request:HttpRequest,edu_id,user_id=None):
    try:
        profile = get_target_profile(request, user_id)
        education = get_object_or_404(Education, pk=edu_id, profile=profile)
        education.delete()
    
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def edit_edu(request:HttpRequest,edu_id,user_id=None):
    try:
        if request.method=='POST':
            profile = get_target_profile(request, user_id)
            education = get_object_or_404(Education, pk=edu_id, profile=profile)
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
        
    
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def delate_cert(request:HttpRequest,cert_id,user_id=None):
    try:
        profile = get_target_profile(request, user_id)
        certification = get_object_or_404(Certification, pk=cert_id, profile=profile)
        certification.delete()
    
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def edit_cert(request:HttpRequest,cert_id,user_id=None):
    try:
        if request.method=='POST':
            profile = get_target_profile(request, user_id)
            certification = get_object_or_404(Certification, pk=cert_id, profile=profile)
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
        
    
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def add_cert(request:HttpRequest,user_id=None):
    try:
        if request.method=='POST':
            certification = Certification.objects.create(profile = get_target_profile(request, user_id))
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
                certification.certificate_file=request.FILES['certificate_file']
                    
            certification.save()
        
    
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def add_exp(request:HttpRequest,user_id=None):
    try:
        if request.method=='POST':
            experience = Experience.objects.create(profile = get_target_profile(request, user_id))

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
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def add_skill(request:HttpRequest,user_id=None):
    try:
        if request.method=='POST':
            skill = Skill.objects.create(profile=get_target_profile(request, user_id))
            skill.name  = request.POST.get('name')
            skill.proficiency  = request.POST.get('proficiency')          
            skill.save()
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def add_language(request:HttpRequest,user_id=None):
    try:
        if request.method=='POST':
            language = Language.objects.create(profile = get_target_profile(request, user_id))
            language.name  = request.POST.get('name')
            language.proficiency  = request.POST.get('proficiency')
            language.save()
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')
@login_required
@require_POST
def add_edu(request:HttpRequest,user_id=None):
    try:
        if request.method=='POST':
            education = Education.objects.create(profile = get_target_profile(request, user_id))
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
      
    except Exception as e:
        print(e)
    if user_id:
        return redirect('profiles:profile_view_admin', user_id=user_id)
    return redirect('profiles:profile_view')


@login_required
def company_profile_view(request:HttpRequest,user_id=None):
    if not request.user.is_authenticated:
        return redirect('main:home_view')
    if user_id:
        if not request.user.is_staff:
            return redirect("main:home_view")
        user = get_object_or_404(User, pk=user_id)
        profile=user.company_profile
    else:
        try:
            profile=request.user.company_profile
        except CompanyProfile.DoesNotExist:
            return redirect('main:home_view')
    if request.method=='POST':
        if 'company-submit' in request.POST:
            profile.company_name  = request.POST.get('company_name')
            profile.commercial_register = request.POST.get('commercial_register')
            industry_id = request.POST.get('industry')
            if industry_id:
                profile.industry = Industry.objects.get(pk=industry_id)
            profile.save()
            return redirect(
                'profiles:profile_company_view_admin' if user_id else 'profiles:profile_company_view',
                user_id=profile.user.id if user_id else None
            )
   

        
    return render(request,'profiles/company_profile.html',{'profile':profile,'admin_view':bool(user_id)})


@login_required
def export_cv_pdf(request):
    
    try:
        html=render_to_string('profiles/cv_pdf.html',{'request':request})
        response=HttpResponse(content_type='application/pdf')
        response['Content-Disposition']=f'filename={request.user.username}_cv.pdf'
        HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(response)
        return response

    except Exception as e:
        print(e)
