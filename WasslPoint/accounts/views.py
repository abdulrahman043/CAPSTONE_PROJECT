from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpRequest
from django.db import transaction
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from profiles.models import CompanyProfile,StudentProfile,PersonalInformation,Experience,Education,Skill,Language,Certification,ContactInformation,Industry
from django.contrib.admin.views.decorators import staff_member_required 
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

# Create your views here.

def signup_view(request: HttpRequest):
    if request.method == 'POST':
        full_name  = request.POST.get('full_name', '').strip()
        email      = request.POST.get('email', '').strip().lower()
        password   = request.POST.get('password', '')
        password2  = request.POST.get('password2', '')
        agree_terms = request.POST.get('terms')

        missing = []
        if not full_name:   missing.append('الاسم الكامل')
        if not email:       missing.append('البريد الإلكتروني')
        if not password:    missing.append('كلمة السر')
        if not password2:   missing.append('تأكيد كلمة السر')
        if not agree_terms: missing.append('الموافقة على الشروط')

        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, 'accounts/signup.html')

        if password != password2:
            messages.error(request, "كلمتا السر غير متطابقتين.")
            return render(request, 'accounts/signup.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, "هذا البريد مسجل مسبقًا.")
            return render(request, 'accounts/signup.html')

        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                password=password,
            )
            profile = StudentProfile.objects.create(user=user)
            PersonalInformation.objects.create(profile=profile, full_name=full_name)
            ContactInformation.objects.create(profile=profile, email=email)

        messages.success(request,
           'تم انشاء الحساب بنجاح'
        )
        return redirect('accounts:login_view')

    return render(request, 'accounts/signup.html')

def signup_company_view(request: HttpRequest):
    industries = Industry.objects.filter(status=True)

    if request.method == 'POST':
        email                     = request.POST.get('email', '').strip().lower()
        password                  = request.POST.get('password', '')
        password2                 = request.POST.get('password2', '')
        company_name              = request.POST.get('company_name', '').strip()
        commercial_register_number= request.POST.get('commercial_register_number', '').strip()
        reg_file                  = request.FILES.get('commercial_register_file')
        industry_id               = request.POST.get('industry')

        missing = []
        if not email:      missing.append('البريد الإلكتروني')
        if not password:   missing.append('كلمة السر')
        if not password2:  missing.append('تأكيد كلمة السر')
        if not company_name:             missing.append('اسم الشركة')
        if not commercial_register_number: missing.append('رقم السجل التجاري')
        if not reg_file:   missing.append('ملف السجل التجاري')
        if not industry_id:missing.append('مجال العمل')

        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, 'accounts/signup_company.html', {
                'industries': industries
            })

        if password != password2:
            messages.error(request, "كلمتا السر غير متطابقتين.")
            return render(request, 'accounts/signup_company.html', {
                'industries': industries
            })

        if User.objects.filter(username=email).exists():
            messages.error(request, "هذا البريد مسجل مسبقًا.")
            return render(request, 'accounts/signup_company.html', {
                'industries': industries
            })

        try:
            industry = industries.get(pk=industry_id)
        except Industry.DoesNotExist:
            messages.error(request, "اختر مجالًا صالحًا للصناعة.")
            return render(request, 'accounts/signup_company.html', {
                'industries': industries
            })

        with transaction.atomic():
            user = User.objects.create_user(
                username = email,
                email    = email,
                password = password,
                is_active= False   
            )
            CompanyProfile.objects.create(
                user                        = user,
                company_name                = company_name,
                commercial_register         = commercial_register_number,
                commercial_CRM_Certificate  = reg_file,
                industry                    = industry,
            )

        messages.success(request,
    "تم استلام طلب تسجيل شركتكم بنجاح! 📩\n"
    "سيتولى مسؤول الموقع تفعيل حسابكم مباشرةً بعد التحقق من صحة البيانات."
)
        return redirect('accounts:login_view')

    return render(request, 'accounts/signup_company.html', {
        'industries': industries
    })

def login_view(request: HttpRequest):
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        missing = []
        if not email:    missing.append('البريد الإلكتروني')
        if not password: missing.append('كلمة السر')
        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('main:home_view')
        else:
            messages.error(request, "بيانات الدخول غير صحيحة.")
            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')
def logout_view(request:HttpRequest):
    logout(request)

    return redirect('main:home_view')

@login_required
@staff_member_required
def user_list(request: HttpRequest):
    user_qs=User.objects.all()
    paginator=Paginator(user_qs,10)
    page=request.GET.get('page')
    user_page=paginator.get_page(page)
    context={"user_page":user_page}

    return render(request, 'accounts/user_list.html',context)
def user_delete(request, user_id):
    user=User.objects.get(pk=user_id)
    if user.is_superuser or user.is_staff:
        pass
    elif request.user!=user:
        user.delete()
    
    return redirect('accounts:user_list')
@login_required
@staff_member_required
@require_POST
def delete_all(request:HttpRequest):
    try:
        if request.method=='POST':
            ids=request.POST.getlist('selected_users')
            if ids:
                User.objects.filter(id__in=ids,is_staff=False, is_superuser=False).exclude(id=request.user.id).delete()
    except:
        pass
    return redirect('accounts:user_list')