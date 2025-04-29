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
from django.contrib import messages

# Create your views here.
@login_required
def get_target_profile(request, user_id=None):
    if user_id:
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
            messages.error(request, "عذراً، ليس لديك صلاحية للاطلاع على ملف مستخدم آخر.")

            return redirect("main:home_view")
        user = get_object_or_404(User, pk=user_id)
        profile=user.student_profile
    else:
        try:
            profile=request.user.student_profile
        except StudentProfile.DoesNotExist:
            messages.error(
                        request,
                        "عذراً، لا يوجد ملف شخصي مرتبط بحسابك بعد. الرجاء إعداد ملفك الشخصي أولاً."
                    )
            return redirect('main:home_view')
    if request.method=='POST':
        if 'picture' in request.FILES:
            try:
                personal, _ = PersonalInformation.objects.get_or_create(profile=profile)
                personal.picture = request.FILES['picture']
                personal.save()
                messages.success(request, "تمت إضافة الصورة الشخصية بنجاح.")
            except Exception:
                messages.error(request, "عذراً، حدث خطأ أثناء رفع الصورة. حاول مرة أخرى.")

            if user_id:
                return redirect('profiles:profile_view_admin', user_id=user_id)
            else:
                return redirect('profiles:profile_view')
        if 'personal-submit' in request.POST:
            try:
                personal, _ = PersonalInformation.objects.get_or_create(profile=profile)
                personal.full_name     = request.POST.get('name')
                personal.date_of_birth = request.POST.get('date_of_birth') or None
                personal.gender        = request.POST.get('gender')
                nat_id = request.POST.get('nationality')
                if nat_id:
                    personal.nationality = Country.objects.get(pk=nat_id)
                personal.save()
                messages.success(request, "تم التعديل على المعلومات الشخصية بنجاح.")
            except Exception:
                messages.error(request, "عذراً، حدث خطأ أثناء تحديث المعلومات الشخصية. حاول مرة أخرى.")

            if user_id:
                return redirect('profiles:profile_view_admin', user_id=user_id)
            else:
                return redirect('profiles:profile_view')
        if 'contact-submit' in request.POST:
            try:
                contact, _ = ContactInformation.objects.get_or_create(profile=profile)
                contact.email        = request.POST.get('email')
                contact.phone        = request.POST.get('phone')
                contact.address_line = request.POST.get('address_line')
                city_id = request.POST.get('city')
                if city_id:
                    contact.city = City.objects.get(pk=city_id)
                contact.save()
                messages.success(request, "تم التعديل على بيانات الاتصال بنجاح.")
            except Exception:
                messages.error(request, "عذراً، حدث خطأ أثناء تحديث بيانات الاتصال. حاول مرة أخرى.")
            if user_id:
                return redirect('profiles:profile_view_admin', user_id=user_id)
            else:
                return redirect('profiles:profile_view')
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
        messages.success(request, "تم حذف الخبرة بنجاح.")

    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء حذف الخبرة. حاول مرة أخرى.")

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
            messages.success(request, "تم التعديل على الخبرة بنجاح.")

    
    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء تعديل الخبرة. حاول مرة أخرى.")

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
        messages.success(request, "تم حذف المهارة بنجاح.")

    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء حذف المهارة. حاول مرة أخرى.")

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
            messages.success(request, "تم التعديل على المهارة بنجاح.")

    
    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء تعديل المهارة. حاول مرة أخرى.")

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
        messages.success(request, "تم حذف اللغة بنجاح.")

    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء حذف اللغة. حاول مرة أخرى.")

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
            messages.success(request, "تم التعديل على اللغة بنجاح.")

    
    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء تعديل اللغة. حاول مرة أخرى.")

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
        messages.success(request, "تم حذف المؤهل التعليمي بنجاح.")

    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء حذف المؤهل التعليمي. حاول مرة أخرى.")

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
            messages.success(request, "تم التعديل على المؤهل التعليمي بنجاح.")

    
    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء تعديل المؤهل التعليمي. حاول مرة أخرى.")

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
        messages.success(request, "تم حذف الشهادة بنجاح.")

    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء حذف الشهادة. حاول مرة أخرى.")

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
            messages.success(request, "تم التعديل على الشهادة بنجاح.")

    
    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء تعديل الشهادة. حاول مرة أخرى.")

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
            messages.success(request, "تم إضافة الشهادة بنجاح.")
   
    
    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء إضافة الشهادة. حاول مرة أخرى.")

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
            messages.success(request, "تم إضافة الخبرة بنجاح.")

    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء إضافة الخبرة. حاول مرة أخرى.")

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
            messages.success(request, "تم إضافة المهارة بنجاح.")

    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء إضافة المهارة. حاول مرة أخرى.")

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
            messages.success(request, "تم إضافة اللغة بنجاح.")

    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء إضافة اللغة. حاول مرة أخرى.")

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
            messages.success(request, "تم إضافة المؤهل التعليمي بنجاح.")

      
    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء إضافة المؤهل التعليمي. حاول مرة أخرى.")

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
            messages.error(request, "عذراً، لم يتم العثور على ملف الشركة.")

            return redirect('main:home_view')
    if request.method=='POST':
        if 'company-submit' in request.POST:
            profile.company_name  = request.POST.get('company_name')
            profile.commercial_register = request.POST.get('commercial_register')
            industry_id = request.POST.get('industry')
            if industry_id:
                profile.industry = Industry.objects.get(pk=industry_id)
            profile.save()
            messages.success(request, "تم التعديل على بيانات الشركة بنجاح.")
            if user_id:
                return redirect('profiles:profile_company_view_admin', user_id=user_id)
            return redirect('profiles:profile_company_view')
   

        
    return render(request,'profiles/company_profile.html',{'profile':profile,'admin_view':bool(user_id)})


@login_required
def export_cv_pdf(request,user_id=None):
    profile = get_target_profile(request, user_id)
    try:
        html=render_to_string('profiles/cv_pdf.html',{'profile':profile})
        response=HttpResponse(content_type='application/pdf')
        response['Content-Disposition']=f'filename={request.user.username}_cv.pdf'
        HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(response)
        return response

    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء تصدير السيرة الذاتية. حاول مرة أخرى.")

        print(e)
        if user_id:
            return redirect('profiles:profile_view_admin', user_id=user_id)
        return redirect('profiles:profile_view')
