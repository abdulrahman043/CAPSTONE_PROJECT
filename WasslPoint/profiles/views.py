from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpRequest,HttpResponse
from .models import StudentProfile,PersonalInformation,Country,ContactInformation,City,Experience,Skill,Language,Education,Certification,Major,CompanyProfile,Industry,ContactPerson,CompanyProfileEditRequest
from datetime import date
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import transaction
from posts.models import Application
from django.contrib.admin.views.decorators import staff_member_required 
from decimal import Decimal

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
            start_str = request.POST.get('start_date')
            end_str   = request.POST.get('end_date')
            start_date = end_date = None
            if start_str:
                y, m = map(int, start_str.split('-'))
                start_date = date(y, m, 1)
            if end_str:
                y, m = map(int, end_str.split('-'))
                end_date = date(y, m, 1)
            if start_date and end_date and start_date > end_date:
                messages.error(request, "تاريخ البدء لا يمكن أن يكون بعد تاريخ الانتهاء.")
                return (redirect('profiles:profile_view_admin', user_id=user_id)if user_id else redirect('profiles:profile_view'))


            profile = get_target_profile(request, user_id)

            experience = get_object_or_404(Experience, pk=exp_id, profile=profile)
           
            experience.job_title  = request.POST.get('job_title')
            experience.company_name  = request.POST.get('company_name')
            experience.description  = request.POST.get('description')
            experience.start_date = start_date
            experience.end_date = end_date
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
    gpa_raw   = request.POST.get('gpa', '').strip().replace(',', '.')
    scale_raw = request.POST.get('gpa_scale', '').strip().replace(',', '.')

    try:
        gpa_raw   = Decimal(gpa_raw)
        scale_raw = Decimal(scale_raw)
    except:
        messages.error(request, "يجب أن يكون كل من الـ GPA والمقياس رقمًا صالحًا.")
        if user_id:
            return redirect('profiles:profile_view_admin', user_id=user_id)
        return redirect('profiles:profile_view')

    if gpa_raw > scale_raw:
        messages.error(
            request,
            f'القيمة ({gpa_raw}) لا يمكن أن تتجاوز المقياس ({scale_raw}).'
        )
        if user_id:
            return redirect('profiles:profile_view_admin', user_id=user_id)
        return redirect('profiles:profile_view')
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
            issue_str  = request.POST.get('issue_date')
            expiry_str = request.POST.get('expiry_date')
            issue_dt  = None
            expiry_dt = None
            if issue_str:
                y, m = map(int, issue_str.split('-'))
                issue_dt = date(y, m, 1)
            if expiry_str:
                y, m = map(int, expiry_str.split('-'))
                expiry_dt = date(y, m, 1)

            if issue_dt and expiry_dt and issue_dt > expiry_dt:
                messages.error(request, "تاريخ الإصدار لا يمكن أن يكون بعد تاريخ الانتهاء.")
                return (
                    redirect('profiles:profile_view_admin', user_id=user_id)
                    if user_id else
                    redirect('profiles:profile_view')
                )
            profile = get_target_profile(request, user_id)
            certification = get_object_or_404(Certification, pk=cert_id, profile=profile)
            certification.name  = request.POST.get('name')
            certification.issuer  = request.POST.get('issuer')
            certification.issue_date = issue_dt
            certification.expiry_date = expiry_dt
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
            issue_str  = request.POST.get('issue_date')
            expiry_str = request.POST.get('expiry_date')
            issue_dt  = None
            expiry_dt = None
            if issue_str:
                y, m = map(int, issue_str.split('-'))
                issue_dt = date(y, m, 1)
            if expiry_str:
                y, m = map(int, expiry_str.split('-'))
                expiry_dt = date(y, m, 1)

            if issue_dt and expiry_dt and issue_dt > expiry_dt:
                messages.error(request, "تاريخ الإصدار لا يمكن أن يكون بعد تاريخ الانتهاء.")
                return (
                    redirect('profiles:profile_view_admin', user_id=user_id)
                    if user_id else
                    redirect('profiles:profile_view')
                )


            certification = Certification.objects.create(profile = get_target_profile(request, user_id))
            certification.name  = request.POST.get('name')
            certification.issuer  = request.POST.get('issuer')
            certification.issue_date = issue_dt
            certification.expiry_date = expiry_dt  
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
def add_exp(request: HttpRequest, user_id=None):
    profile = get_target_profile(request, user_id)

    start_str = request.POST.get('start_date')
    end_str   = request.POST.get('end_date')
    start_date = end_date = None
    if start_str:
        y, m = map(int, start_str.split('-'))
        start_date = date(y, m, 1)
    if end_str:
        y, m = map(int, end_str.split('-'))
        end_date = date(y, m, 1)
    if start_date and end_date and start_date > end_date:
        messages.error(request, "تاريخ البدء لا يمكن أن يكون بعد تاريخ الانتهاء.")
        return (redirect('profiles:profile_view_admin', user_id=user_id)if user_id else redirect('profiles:profile_view'))


    try:
        with transaction.atomic():
            experience = Experience.objects.create(profile=profile)

            experience.job_title    = request.POST.get('job_title')
            experience.company_name = request.POST.get('company_name')
            experience.description  = request.POST.get('description')
            experience.start_date   = start_date
            experience.end_date     = end_date
            
            experience.save()
            messages.success(request, "تم إضافة الخبرة بنجاح.")

    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء إضافة الخبرة. حاول مرة أخرى.")
        print(e)

    return (
        redirect('profiles:profile_view_admin', user_id=user_id)
        if user_id else
        redirect('profiles:profile_view')
    )
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
    gpa_raw   = request.POST.get('gpa', '').strip().replace(',', '.')
    scale_raw = request.POST.get('gpa_scale', '').strip().replace(',', '.')

    try:
        gpa_raw   = Decimal(gpa_raw)
        scale_raw = Decimal(scale_raw)
    except:
        messages.error(request, "يجب أن يكون كل من الـ GPA والمقياس رقمًا صالحًا.")
        if user_id:
            return redirect('profiles:profile_view_admin', user_id=user_id)
        return redirect('profiles:profile_view')

    if gpa_raw > scale_raw:
        messages.error(
            request,
            f'القيمة ({gpa_raw}) لا يمكن أن تتجاوز المقياس ({scale_raw}).'
        )
        if user_id:
            return redirect('profiles:profile_view_admin', user_id=user_id)
        return redirect('profiles:profile_view')
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
 
    industries = Industry.objects.filter(status=True)
    cities = City.objects.filter(status=True) 

    total_applications = Application.objects.filter(
        opportunity__company=profile
    ).count()

    return render(request,'profiles/company_profile.html',{'profile':profile,'admin_view':bool(user_id),'industries':industries,'cities':cities,'total_applications':total_applications})

@login_required
def add_edit_contact_person(request:HttpRequest,user_id=None):
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
        

    if request.method=='POST':
        try:
            contact_person,_=ContactPerson.objects.get_or_create(company_profile=profile)
            contact_person.person_name=request.POST.get('name')
            contact_person.email=request.POST.get('email')
            contact_person.phone=request.POST.get('phone')
            contact_person.save()
            if _:
                messages.success(request, "تم إنشاء جهة الاتصال بنجاح.")
            else:
                messages.success(request, "تم تحديث بيانات جهة الاتصال بنجاح.")
        except Exception as e:
                messages.error(request, "حدث خطأ أثناء حفظ بيانات جهة الاتصال. حاول مرة أخرى.")

        if user_id:
            return redirect('profiles:company_profile_view_admin', user_id=user_id)
        return redirect('profiles:company_profile_view')
    if user_id:
        return redirect('profiles:company_profile_view_admin', user_id=user_id)
    return redirect('profiles:company_profile_view')


@login_required
def add_edit_moreinfo_company(request:HttpRequest,user_id=None):
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
        

    if request.method=='POST':
        try:
            company_description=request.POST.get('company_description').strip()
            company_url=request.POST.get('company_url').strip()
            address_line=request.POST.get('address_line').strip()

            profile.company_description=company_description
            profile.company_url=company_url
            profile.address_line=address_line
            profile.save()
            messages.success(request, "تم تحديث بيانات الشركة بنجاح.")
        except Exception as e:
                messages.error(request, "حدث خطأ أثناء حفظ بيانات الشركة. حاول مرة أخرى.")
                print(e)

        if user_id:
            return redirect('profiles:company_profile_view_admin', user_id=user_id)
        return redirect('profiles:company_profile_view')
    if user_id:
        return redirect('profiles:company_profile_view_admin', user_id=user_id)
    return redirect('profiles:company_profile_view')



        
@login_required
@require_POST
@staff_member_required
def add_edit_company_info(request:HttpRequest,user_id):
    user = get_object_or_404(User, pk=user_id)
    profile=user.company_profile
    if request.method=='POST':
        try:
            profile.company_name=request.POST.get('company_name')
            if 'crm_certificate' in request.FILES:
                profile.crm_certificate=request.FILES['crm_certificate']
            profile.commercial_register=request.POST.get('commercial_register')
            ind_id=request.POST.get('industry').strip()
            if ind_id:
                industry=Industry.objects.get(pk=ind_id)
                profile.industry=industry
            profile.address_line=request.POST.get('address_line')
            profile.save()
            messages.success(request, "تم حفظ معلومات الشركة بنجاح.")

        except Industry.DoesNotExist:
            messages.error(request, "المجال المحدد غير صالح. يرجى الاختيار من القائمة.")
        except Exception:
            messages.error(request, "حدث خطأ أثناء حفظ معلومات الشركة. حاول مرة أخرى.")

        if user_id:
            return redirect('profiles:company_profile_view_admin', user_id=user_id)
        return redirect('profiles:company_profile_view')
    if user_id:
        return redirect('profiles:company_profile_view_admin', user_id=user_id)
    return redirect('profiles:company_profile_view')
@login_required
@require_POST
def add_edit_company_info_company(request: HttpRequest):
    profile = get_object_or_404(CompanyProfile, user=request.user)
    if CompanyProfileEditRequest.objects.filter(
        company=profile,
        status=CompanyProfileEditRequest.STATUS_PENDING
    ).exists():
        messages.warning(
            request,
            "لديك طلب تعديل قيد المراجعة بالفعل. لا يمكنك إنشاء طلب جديد حتى يُعالج الطلب الحالي."
        )
        return redirect('profiles:company_profile_view')

    company_name        = request.POST.get('company_name').strip()
    commercial_register = request.POST.get('commercial_register').strip()
    industry_id         = request.POST.get('industry').strip()
    city_id         = request.POST.get('city').strip()
    company_location        = request.POST.get('company_location')
    crm_certificate     = request.FILES.get('crm_certificate')

    missing = []
    if not company_name:        missing.append('اسم الشركة')
    if not commercial_register: missing.append('رقم السجل التجاري')
    if not industry_id:         missing.append('المجال')
    if not city_id:         missing.append('المدينة')


    if missing:
        messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
        return redirect('profiles:company_profile_view')

    try:
        industry = Industry.objects.get(pk=industry_id)
    except Industry.DoesNotExist:
        messages.error(request, "المجال المحدد غير صالح. يرجى الاختيار من القائمة.")
        return redirect('profiles:company_profile_view')
    try:
        city = City.objects.get(pk=city_id)
    except City.DoesNotExist:
        messages.error(request, "المدينة المحددة غير صالحه. يرجى الاختيار من القائمة.")
        return redirect('profiles:company_profile_view')
    print(company_location)
    try:
        with transaction.atomic():
            edit = CompanyProfileEditRequest.objects.create(
                company             = profile,
                company_name        = company_name,
                commercial_register = commercial_register,
                industry            = industry,
                city        =          city ,
                company_location=company_location or None
            )
            if crm_certificate:
                edit.crm_certificate = crm_certificate
            
            edit.save()

    except Exception as e:
        print(e)
        messages.error(request, "حدث خطأ أثناء إنشاء طلب التعديل. حاول مرة أخرى.")
        return redirect('profiles:company_profile_view')

    messages.success(request, "تم إرسال طلب التعديل وسيتم مراجعته من قبل الإدارة.")
    return redirect('profiles:company_profile_view')
@require_POST
@login_required
def edit_logo(request:HttpRequest,user_id=None):
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
    if request.method=='POST':
        try:
            if 'logo' in request.FILES:

                
                profile.logo=request.FILES['logo']
                profile.save()
                messages.success(request, "تم تحديث الشعار بنجاح.")

        except Exception:
            messages.error(request, "حدث خطأ أثناء رفع الشعار. حاول مرة أخرى.")

        if user_id:
            return redirect('profiles:company_profile_view_admin', user_id=user_id)
        return redirect('profiles:company_profile_view')
    if user_id:
        return redirect('profiles:company_profile_view_admin', user_id=user_id)
    return redirect('profiles:company_profile_view')
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
@login_required
def student_company_export_cv_pdf(request,user_id):
    user = get_object_or_404(User, id=user_id)
    profile=user.student_profile
    try:
        html=render_to_string('profiles/cv_pdf.html',{'profile':profile})
        response=HttpResponse(content_type='application/pdf')
        response['Content-Disposition']=f'filename={user.username}_cv.pdf'
        HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(response)
        return response

    except Exception as e:
        messages.error(request, "عذراً، حدث خطأ أثناء تصدير السيرة الذاتية. حاول مرة أخرى.")

        print(e)
       
        return redirect('profiles:company_student_profile' ,user.id)

def public_company_profile_view(request, company_id):
    """
    Displays a public view of a company's profile.
    Fetches the company profile based on its ID and ensures the associated user is active.
    """
    # Fetch the specific company profile, ensuring it's linked to an active user
    # Use select_related for efficiency when accessing Industry and City
    company_profile = get_object_or_404(
        CompanyProfile.objects.select_related('user', 'industry', 'city'),
        pk=company_id,
        user__is_active=True # Only show profiles of active companies
    )

    context = {
        'profile': company_profile,
    }
    return render(request, 'profiles/public_company_profile.html', context)
