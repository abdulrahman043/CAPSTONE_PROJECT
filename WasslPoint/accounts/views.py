from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpRequest
from django.db import transaction
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from profiles.models import CompanyProfile,StudentProfile,PersonalInformation,Experience,Education,Skill,Language,Certification,ContactInformation,Industry,Major,City,CompanyProfileEditRequest
from django.contrib.admin.views.decorators import staff_member_required 
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from subscriptions.models import SubscriptionPlan,UserSubscription
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.urls import reverse

from .models import EmailOTP
from django.core.mail   import send_mail
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions                   import ValidationError
import random
from django.utils import timezone
from datetime import timedelta
import ssl
from django.db.models       import Q
from posts.models import Application,TrainingOpportunity
# Create your views here.
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import re
PRICE_REGEX = re.compile(r"^\d{1,4}(\.\d{1,2})?$")   # يسمح حتى 9999.99

def signup_company_email(request):
    if request.user.is_authenticated:
        return redirect('main:home_view')

    if request.method == 'POST':
        email = request.POST.get('email','').strip().lower()
        if not email:
            messages.error(request, "يرجى إدخال البريد الإلكتروني.")
            return render(request, 'accounts/signup_company_email.html')

        # أرسل OTP
        code = f"{random.randint(0,999999):06d}"
        EmailOTP.objects.create(user_email=email, code=code)
        send_mail(
            subject="رمز التحقق لتسجيل الشركة",
            message=f"رمز التحقق: {code}\nصالِح 10 دقائق.",
            from_email=None,
            recipient_list=[email],
        )
        request.session['pending_signup'] = {
            'type': 'company',
            'email': email
        }
        return redirect('accounts:verify_signup_otp')

    return render(request, 'accounts/signup_company_email.html')
def signup_view(request: HttpRequest):
    if  request.user.is_authenticated:
        return redirect('main:home_view')
    if request.method == 'POST':
        full_name   = request.POST.get('full_name', '').strip()
        email       = request.POST.get('email', '').strip().lower()
        password    = request.POST.get('password', '')
        password2   = request.POST.get('password2', '')
        agree_terms = request.POST.get('terms')

        missing = []
        if not full_name:    missing.append('الاسم الكامل')
        if not email:        missing.append('البريد الإلكتروني')
        if not password:     missing.append('كلمة السر')
        if not password2:    missing.append('تأكيد كلمة السر')
        if not agree_terms:  missing.append('الموافقة على الشروط')
        if missing:
            messages.error(request,
                "هذه الحقول مطلوبة: " + ", ".join(missing)
            )
            return render(request, 'accounts/signup.html',{"full_name":full_name,"email":email})

        if password != password2:
            messages.error(request, "كلمتا السر غير متطابقتين.")
            return render(request, 'accounts/signup.html',{"full_name":full_name,"email":email})

        if User.objects.filter(username=email).exists():
            messages.error(request, "هذا البريد مسجل مسبقًا.")
            return render(request, 'accounts/signup.html',{"full_name":full_name,"email":email})
        try:
            validate_password(password, user=None)

        except ValidationError as error:
            for e in error.error_list:
                if e.code=='password_too_short':
                    messages.error(request, 'يجب أن تتكون كلمة المرور من 8 أحرف على الأقل.')
                    return render(request, 'accounts/signup.html',{"full_name":full_name,"email":email})
                elif e.code == 'password_entirely_numeric':
                    messages.error(request,"لا يمكن أن تكون كلمة المرور أرقامًا فقط.")
                    return render(request, 'accounts/signup.html',{"full_name":full_name,"email":email})

                elif e.code == 'password_too_common':
                    messages.error(request,"هذه كلمة مرور شائعة جدًا، اختر كلمة أخرى أكثر أمانًا.")
                    return render(request, 'accounts/signup.html',{"full_name":full_name,"email":email})

                elif e.code == 'password_similar_to_username':
                    messages.error(request,"كلمة المرور قريبة من البريد الإلكتروني أو الاسم، اختر كلمة أخرى.")
                    return render(request, 'accounts/signup.html',{"full_name":full_name,"email":email})

                else:
                    messages.error(request,error)
                    return render(request, 'accounts/signup.html',{"full_name":full_name,"email":email})


        otp_code = f"{random.randint(0, 999999):06d}"
        EmailOTP.objects.create(user_email=email, code=otp_code)

        send_mail(
            subject="رمز التحقق للتسجيل",
            message=(
                f"مرحبًا بك بنقطة وصل,\n\n"
                f"الرمز الخاص بك لتفعيل الحساب هو: {otp_code}\n"
                "سوف تنتهي صلاحيته خلال 10 دقائق."
            ),
            from_email=None,              
            recipient_list=[email],
            fail_silently=False,
        )

        request.session['pending_signup'] = {
            'type': 'student',
            'full_name': full_name,
            'email': email,
            'password': password,
        }

        return redirect('accounts:verify_signup_otp')

    return render(request, 'accounts/signup.html')

def verify_signup_otp(request):
    if request.user.is_authenticated:
        return redirect('main:home_view')

    data = request.session.get('pending_signup')
    if not data:
        return redirect('accounts:signup_view')

    if request.method == 'POST':
        entered = request.POST.get('otp','').strip()
        cutoff  = timezone.now() - timedelta(minutes=10)

        otp_qs = EmailOTP.objects.filter(
            user_email=data['email'],
            code=entered,
            used=False,
            created_at__gte=cutoff
        )
        if otp_qs.exists():
            otp = otp_qs.first()
            otp.used = True
            otp.save()

            if data['type'] == 'student':
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=data['email'],
                        email=data['email'],
                        password=data['password']
                    )
                    profile = StudentProfile.objects.create(user=user)
                    PersonalInformation.objects.create(
                        profile=profile,
                        full_name=data['full_name']
                    )
                    ContactInformation.objects.create(
                        profile=profile,
                        email=data['email']
                    )
                    del request.session['pending_signup']

                login(request, user)
                messages.success(request, "تم التحقق وتسجيل الدخول بنجاح!")
                return redirect('main:home_view')

            elif data['type'] == 'company':  
                return redirect('accounts:signup_company_detail_view')

        messages.error(request, "رمز غير صحيح أو منتهي الصلاحية.")

    return render(request, 'accounts/verify_otp.html')
    

def signup_company_detail_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('main:home_view')

    data = request.session.get('pending_signup')
    if not data or data.get('type') != 'company':
        return redirect('accounts:signup_company_email')

    industries = Industry.objects.filter(status=True)
    # --- START Modification for Cities Data ---
    # Fetch cities and structure them as a list of dictionaries
    cities_list = list(City.objects.filter(status=True).values('id', 'arabic_name'))
    # --- END Modification for Cities Data ---

    email = data['email'] # Email is already validated from the previous step

    if request.method == 'POST':
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        company_name = request.POST.get('company_name', '').strip()
        commercial_register_number = request.POST.get('commercial_register_number', '').strip()
        reg_file = request.FILES.get('commercial_register_file')
        industry_id = request.POST.get('industry')
        # city_id is now correctly received from the hidden input with name="city"
        city_id = request.POST.get('city')

        print(request.POST) # Good for debugging submitted data

        missing = []
        # The email is from session, so it's not checked here as a missing POST field
        if not password:   missing.append('كلمة السر')
        if not password2:  missing.append('تأكيد كلمة السر')
        if not company_name: missing.append('اسم الشركة')
        if not commercial_register_number: missing.append('رقم السجل التجاري')
        if not reg_file:   missing.append('ملف السجل التجاري')
        if not industry_id: missing.append('مجال العمل')
        if not city_id: missing.append(' المدينة') # Check if the city ID from hidden input is present

        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, 'accounts/signup_company.html', {
                'industries': industries,
                'cites': cities_list, # Pass the formatted list
                'email': email,
                'company_name': company_name,
                'commercial_register_number': commercial_register_number,
            })

        if password != password2:
            messages.error(request, "كلمتا السر غير متطابقتين.")
            return render(request, 'accounts/signup_company.html', {
                'industries': industries,
                'email': email,
                'cites': cities_list, # Pass the formatted list
                'company_name': company_name,
                'commercial_register_number': commercial_register_number,
            })

        # Using username=email for unique identification as per your code
        if User.objects.filter(username=email).exists():
            messages.error(request, "هذا البريد مسجل مسبقًا.")
            return render(request, 'accounts/signup_company.html', {
                'industries': industries,
                'email': email,
                'cites': cities_list, # Pass the formatted list
                'company_name': company_name,
                'commercial_register_number': commercial_register_number,
            })

        try:
            # User=None is fine for general password policy checks
            validate_password(password, user=None)
        except ValidationError as error:
            # Improved handling of validation errors
            for e in error.error_list:
                 # Check specific error codes and provide user-friendly messages
                 if e.code == 'password_too_short':
                     messages.error(request, 'يجب أن تتكون كلمة المرور من 8 أحرف على الأقل.')
                 elif e.code == 'password_entirely_numeric':
                     messages.error(request, "لا يمكن أن تكون كلمة المرور أرقامًا فقط.")
                 elif e.code == 'password_too_common':
                     messages.error(request, "هذه كلمة مرور شائعة جدًا، اختر كلمة أخرى أكثر أمانًا.")
                 elif e.code == 'password_similar_to_username':
                     messages.error(request, "كلمة المرور قريبة من البريد الإلكتروني أو الاسم، اختر كلمة أخرى.")
                 else:
                     # Fallback for other potential validation errors
                     messages.error(request, f"خطأ في كلمة المرور: {e.message}")

            # Return render after displaying messages
            return render(request, 'accounts/signup_company.html', {
                'industries': industries,
                'email': email,
                'cites': cities_list, # Pass the formatted list
                'company_name': company_name,
                'commercial_register_number': commercial_register_number,
            })


        try:
            industry = Industry.objects.get(pk=industry_id, status=True) # Ensure status is true
        except Industry.DoesNotExist:
            messages.error(request, "اختر مجالًا صالحًا للصناعة.")
            return render(request, 'accounts/signup_company.html', {
                'industries': industries,
                'email': email,
                'cites': cities_list, # Pass the formatted list
                'company_name': company_name,
                'commercial_register_number': commercial_register_number,
            })

        try:
            city = City.objects.get(pk=city_id, status=True) # Ensure status is true
        except City.DoesNotExist:
            messages.error(request, "اختر مدينة صالحة.")
            return render(request, 'accounts/signup_company.html', {
                'industries': industries,
                'email': email,
                'cites': cities_list, # Pass the formatted list
                'company_name': company_name,
                'commercial_register_number': commercial_register_number,
            })


        with transaction.atomic():
            user = User.objects.create_user(
                username=email, # Using email as username
                email=email,
                password=password,
                is_active=False # User is inactive until verified
            )

            # Check specifically for 'commercial_register_file' in request.FILES
            # No need for an 'if "logo" in request.FILES' block here based on form
            company_profile = CompanyProfile.objects.create(
                user=user,
                company_name=company_name,
                commercial_register=commercial_register_number,
                crm_certificate=reg_file, # This will be None if file wasn't uploaded (handled by missing check)
                industry=industry,
                city=city,
            )

            # If you were expecting a logo file besides the CRM certificate, you'd handle it here
            # if 'logo' in request.FILES:
            #     company_profile.logo = request.FILES['logo']
            #     company_profile.save()


            # Clear the session data after successful creation
            if 'pending_signup' in request.session:
                del request.session['pending_signup']

        messages.success(request,
            "تم استلام طلب تسجيل شركتكم بنجاح! 📩\n"
            "سيتولى مسؤول الموقع تفعيل حسابكم مباشرةً بعد التحقق من صحة البيانات."
        )
        return redirect('accounts:login_view')

    # This block handles GET requests and returning the form initially or on validation errors
    return render(request, 'accounts/signup_company.html', {
        'industries': industries,
        'email': email,
        'cites': cities_list, # Pass the formatted list for GET requests too
        # Include other fields here if you want them to persist on GET reload after error
        'company_name': request.POST.get('company_name', ''), # Retain value on POST error
        'commercial_register_number': request.POST.get('commercial_register_number', ''), # Retain value on POST error
        # Note: file inputs cannot have their value pre-filled for security reasons
    })

def login_view(request: HttpRequest):
    if  request.user.is_authenticated:
        return redirect('main:home_view')
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        print(password)
        missing = []
        if not email:    missing.append('البريد الإلكتروني')
        if not password: missing.append('كلمة السر')
        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, 'accounts/login.html',{'email':email})

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "✅ تم تسجيل الدخول بنجاح.")

            return redirect('main:home_view')
        try:
            existing = User.objects.get(username=email)
        except User.DoesNotExist:
            existing = None

        if existing and existing.check_password(password) and not existing.is_active:
            messages.error(request,
        "🔒 لقد استلمنا طلب تسجيل شركتكم وهو الآن قيد الفحص والمراجعة لدى فريق الإدارة. "
        "سيتم تفعيل الحساب تلقائيًا فور الانتهاء من المراجعة. شكرًا لصبركم وتفهمكم.")
            return render(request, 'accounts/login.html')

        # 4) باقي الحالات (خطأ بالإيميل أو الباسوورد)
        messages.error(request, "❌ البريد الإلكتروني أو كلمة السر غير صحيحة.")
        return render(request, 'accounts/login.html',{'email':email})

    return render(request, 'accounts/login.html')
def logout_view(request:HttpRequest):
    logout(request)
    messages.success(request, "✅ تم تسجيل الخروج بنجاح.")

    return redirect('main:home_view')
@login_required
@staff_member_required
def user_list_view(request):
    q = request.GET.get('q', '').strip()
    user_type = request.GET.get('type', '').strip()   
    users     = User.objects.all()

    if q:
        users = users.filter(
              Q(id__exact=q) |
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(student_profile__personal_info__full_name__icontains=q) |
            Q(company_profile__company_name__icontains=q)
        ).distinct()

    if user_type == 'student':
        users = users.filter(student_profile__isnull=False)
    elif user_type == 'company':
        users = users.filter(company_profile__isnull=False)
    elif user_type == 'staff':
        users = users.filter(is_staff=True)
    users=users.order_by('-date_joined')
    paginator = Paginator(users, 10)
    page_num  = request.GET.get('page')
    user_page = paginator.get_page(page_num)

    return render(request, 'accounts/user_list.html', {
        'user_page': user_page,
        'q': q,
        'user_type': user_type,   
    })
@login_required
@staff_member_required
def user_delete(request, user_id):
    user=User.objects.get(pk=user_id)
    if user.is_superuser or user.is_staff:
        pass
    elif request.user!=user:
        user.delete()
    
    return redirect('accounts:user_list_view')
@login_required
@staff_member_required
def user_reject(request, user_id):
    user=User.objects.get(pk=user_id)
    if user.is_superuser or user.is_staff:
        pass
    elif request.user!=user:
        subject = "❌ تم رفض طلب تسجيل شركتكم"
        email = "wasslpoint@gmail.com"

        body = (
        f"مرحبًا {user.company_profile.company_name}\n\n"
        "نأسف لإبلاغكم بأن طلب تسجيل شركتكم في منصتنا قد تم رفضه\n\n"
        "للاستفسار أو لمزيد من المعلومات يرجى التواصل مع فريق الدعم عبر البريد الإلكتروني\n"
        f"\u202A{email}\u202C\n\n"
        "شكرًا لتفهمكم"
    )
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        user.delete()
        messages.success(request, f"تم رفض وحذف حساب {user.username} بنجاح.")

    
    return redirect('accounts:user_list_view')

@login_required
@staff_member_required
def company_user_list_view(request: HttpRequest):
    q = request.GET.get('q', '').strip()

    user_qs = User.objects.filter(company_profile__isnull=False)

    if q:
        user_qs = user_qs.filter(
            Q(id__exact=q) |

            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(company_profile__company_name__icontains=q)
        ).distinct()
    user_qs=user_qs.order_by('-date_joined')

    paginator=Paginator(user_qs,10)
    page=request.GET.get('page')
    user_page=paginator.get_page(page)
    context={"user_page":user_page,'q': q}

    return render(request, 'accounts/company_users_list.html',context)
@login_required
@staff_member_required
def student_user_list_view(request: HttpRequest):
    q = request.GET.get('q', '').strip()
    users_qs = User.objects.filter(student_profile__isnull=False)
    if q:
        users_qs = users_qs.filter(
            Q(id__icontains=q) |

            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(student_profile__personal_info__full_name__icontains=q) 
        ).distinct()
    users_qs=users_qs.order_by('-date_joined')

    paginator=Paginator(users_qs,10)
    page=request.GET.get('page')
    user_page=paginator.get_page(page)
    context={"user_page":user_page, 'q': q}

    return render(request, 'accounts/student_users_list.html',context)
@login_required
@staff_member_required
def applications_list_view(request: HttpRequest):
    q = request.GET.get('q', '').strip()
    applications_qs = Application.objects.all().order_by('-applied_at')
    if q:
        applications_qs = applications_qs.filter(
            Q(opportunity__company__company_name__icontains=q) |
            Q(id__icontains=q) |

            Q(student__user__username__icontains=q) |
            Q(student__user__email__icontains=q) |
            Q(student__personal_info__full_name__icontains=q) 
        ).distinct()
    applications_qs=applications_qs.order_by('-applied_at')
    paginator=Paginator(applications_qs,10)
    page=request.GET.get('page')
    user_page=paginator.get_page(page)
    context={"applications_page":user_page,'q': q}

    return render(request, 'accounts/applications_list.html',context)
@login_required
@staff_member_required
def subscription_view(request: HttpRequest):
    q = request.GET.get('q', '').strip()
    subscription_qs = SubscriptionPlan.objects.all().order_by('-id')

    if q:
        subscription_qs = subscription_qs.filter(
            Q(name__icontains=q) |
            Q(id__icontains=q) |

            Q(duration_days__icontains=q) |
            Q(status__icontains=q) 
        ).distinct()
    
    paginator=Paginator(subscription_qs,10)
    page=request.GET.get('page')
    user_page=paginator.get_page(page)
    context={"subscription_page":user_page,'q': q}

    return render(request, 'accounts/subscription.html',context)
@login_required
@staff_member_required
def major_view(request: HttpRequest):
    q = request.GET.get('q', '').strip()
    major_qs = Major.objects.all().order_by('-id')

    if q:
        major_qs = major_qs.filter(
            Q(ar_name__icontains=q) |
            Q(id__icontains=q) |

            Q(en_name__icontains=q) |
            Q(status__icontains=q) 
        ).distinct()
    
    paginator=Paginator(major_qs,5)
    page=request.GET.get('page')
    user_page=paginator.get_page(page)
    context={"major_page":user_page,'q': q}

    return render(request, 'accounts/major_list.html',context)
@login_required
@staff_member_required
def opportunity_list_view(request: HttpRequest):
    q = request.GET.get('q', '').strip()
    opportunity_qs = TrainingOpportunity.objects.all().order_by('-created_at')
    if q:
        opportunity_qs = opportunity_qs.filter(
            Q(company__company_name__icontains=q) |
            Q(id__icontains=q) |
                        Q(city__arabic_name__icontains=q) |


            Q(company__user__username__icontains=q) |
            Q(company__user__email__icontains=q) 
            
        ).distinct()
    opportunity_qs=opportunity_qs.order_by('-created_at')
    paginator=Paginator(opportunity_qs,10)
    page=request.GET.get('page')
    user_page=paginator.get_page(page)
    context={"opportunity_page":user_page,'q': q}

    return render(request, 'accounts/opportunity_list.html',context)
@login_required
@staff_member_required
def pending_company_requests_view(request: HttpRequest):
    q = request.GET.get('q', '').strip()
    user_qs = User.objects.filter(is_active=False)
    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(company_profile__company_name__icontains=q)
        ).distinct()
    user_qs=user_qs.order_by('-date_joined')

    paginator=Paginator(user_qs,10)
    page=request.GET.get('page')
    user_page=paginator.get_page(page)
    context={"user_page":user_page,'q': q}

    return render(request, 'accounts/pending_company_requests.html',context)
@login_required
@staff_member_required
@require_POST
def user_delete(request, user_id):
    user=User.objects.get(pk=user_id)
    if user.is_superuser or user.is_staff:
        messages.warning(request, "لا يمكنك تغيير صلاحيات مسؤول آخر.")
    elif request.user!=user:
        messages.success(request, f"✅ تم حذف المستخدم  بنجاح.")

        user.delete()
    
    return redirect('accounts:pending_company_requests_view')
@login_required
@staff_member_required
@require_POST
def approve_company(request, user_id):
    user=User.objects.get(pk=user_id)
    if user.is_superuser or user.is_staff:
        messages.warning(request, "لا يمكنك تغيير صلاحيات مسؤول آخر.")
    elif request.user!=user:
        user.is_active=True
        user.save()
        messages.success(request, f"تم تفعيل حساب {user.username} بنجاح.")
        

        subject = "✅ تم تفعيل حساب شركتكم"
        email = "wasslpoint@gmail.com"

        body = (
        f"مرحبًا {user.company_profile.company_name}\n\n"
        "يسرنا إبلاغكم بأنه قد تم تفعيل حساب شركتكم في منصتنا بنجاح\n\n"
        "يمكنكم الآن تسجيل الدخول إلى حسابكم والاستفادة من جميع الميزات\n\n"
        "للاستفسار أو الدعم يمكنكم التواصل معنا عبر البريد الإلكتروني\n"
        f"\u202A{email}\u202C\n\n"
        "شكرًا لاستخدامكم منصتنا"
    )
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


    
    return redirect('accounts:pending_company_requests_view')
@login_required
@staff_member_required
@require_POST
def delete_all(request:HttpRequest):
    try:
        if request.method=='POST':
            ids=request.POST.getlist('selected_users')
            if ids:
                User.objects.filter(id__in=ids,is_staff=False, is_superuser=False).exclude(id=request.user.id).delete()
                messages.success(request,"✅ تم حذف المستخدمين المحددين بنجاح.")
    except:
        messages.error(
            request,
            "❌ حدث خطأ أثناء حذف المستخدمين. حاول مرة أخرى لاحقًا."
        )
    return redirect('accounts:user_list_view')
@login_required
@staff_member_required
@require_POST
def app_delete_all(request:HttpRequest):
    try:
        if request.method=='POST':
            ids=request.POST.getlist('selected_users')
            if ids:
                Application.objects.filter(id__in=ids).delete()
                messages.success(request,"✅ تم حذف التقديمات المحددة بنجاح.")
    except:
        messages.error(
            request,
            "❌ حدث خطأ أثناء حذف المحددة. حاول مرة أخرى لاحقًا."
        )
    return redirect('accounts:applications_list_view')
@login_required
@staff_member_required
@require_POST
def sub_delete_all(request:HttpRequest):
    try:
        if request.method=='POST':
            ids=request.POST.getlist('selected_users')
            if ids:
                SubscriptionPlan.objects.filter(id__in=ids).delete()
                messages.success(request,"✅ تم حذف الاشتراكات المحددة بنجاح.")
    except:
        messages.error(
            request,
            "❌ حدث خطأ أثناء حذف الاشتراكات المحددة. حاول مرة أخرى لاحقًا."
        )
    return redirect('accounts:subscription_view')
@login_required
@staff_member_required
@require_POST
def major_delete_all(request:HttpRequest):
    try:
        if request.method=='POST':
            ids=request.POST.getlist('selected_users')
            if ids:
                Major.objects.filter(id__in=ids).delete()
                messages.success(request,"✅ تم حذف التخخصات المحددة بنجاح.")
    except:
        messages.error(
            request,
            "❌ حدث خطأ أثناء حذف التخصصات المحددة. حاول مرة أخرى لاحقًا."
        )
    return redirect('accounts:major_view')
@login_required
@staff_member_required
@require_POST
def opp_delete_all(request:HttpRequest):
    try:
        if request.method=='POST':
            ids=request.POST.getlist('selected_users')
            if ids:
                TrainingOpportunity.objects.filter(id__in=ids).delete()
                messages.success(request,"✅ تم حذف التدريبات المحددة بنجاح.")
    except:
        messages.error(
            request,
            "❌ حدث خطأ أثناء حذف التدريبات. حاول مرة أخرى لاحقًا."
        )
    return redirect('accounts:opportunity_list_view')



@login_required
@staff_member_required
def add_subscription_view(request):
    if request.method == "POST":
        name        = request.POST.get("name", "").strip()
        duration    = request.POST.get("duration_days", "").strip()
        price_raw   = request.POST.get("price", "").strip()
        description = request.POST.get("description", "").strip()
        status      = bool(request.POST.get("status"))

        missing = []
        if not name:      missing.append("اسم الاشتراك")
        if not duration:  missing.append("المدة")
        if not price_raw: missing.append("السعر")
        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return redirect("accounts:add_subscription_view")

        try:
            duration_days = int(duration)
            if duration_days < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "المدة يجب أن تكون عدداً صحيحاً أكبر من صفر.")
            return redirect("accounts:add_subscription_view")

        if not PRICE_REGEX.match(price_raw):
            messages.error(request, "السعر يجب أن يكون بصيغة صحيحة مثل 99 أو 99.99")
            return redirect("accounts:add_subscription_view")

        try:
            price = (
                Decimal(price_raw)
                .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)  # منزلتان فقط
            )
            if price > Decimal("9999.99") or price < Decimal("0.00"):
                raise ValueError  # يتعدى max_digits أو سالب
        except (InvalidOperation, ValueError):
            messages.error(request, "السعر غير صالح.")
            return redirect("accounts:add_subscription_view")

        try:
            with transaction.atomic():
                SubscriptionPlan.objects.create(
                    name=name,
                    duration_days=duration_days,
                    price=price,
                    description=description,
                    status=status,
                )
        except Exception as e:
            print(e)  
            messages.error(
                request,
                "❌ عذرًا، لم نتمكن من إضافة خطة الاشتراك. الرجاء التحقق من البيانات والمحاولة مرة أخرى.",
            )
            return redirect("accounts:add_subscription_view")

        messages.success(request, "تم إضافة الاشتراك بنجاح!")
        return redirect("accounts:subscription_view")

    return render(request, "accounts/subscription_add.html")

@login_required
@staff_member_required
def edit_subscription_view(request, id):
    subscription = get_object_or_404(SubscriptionPlan, pk=id)

    if request.method == "POST":
        name        = request.POST.get("name", "").strip()
        duration    = request.POST.get("duration_days", "").strip()
        price_raw   = request.POST.get("price", "").strip()
        description = request.POST.get("description", "").strip()
        status      = bool(request.POST.get("status"))

        ctx = {
            "subscription": subscription,
            "name":         name,
            "duration":     duration,
            "price":        price_raw,
            "description":  description,
            "status":       status,
        }

        missing = []
        if not name:      missing.append("اسم الاشتراك")
        if not duration:  missing.append("المدة")
        if not price_raw: missing.append("السعر")
        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, "accounts/subscription_edit.html", ctx)

        try:
            duration_days = int(duration)
            if duration_days < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "المدة يجب أن تكون عدداً صحيحاً أكبر من صفر.")
            return render(request, "accounts/subscription_edit.html", ctx)

        if not PRICE_REGEX.match(price_raw):
            messages.error(request, "السعر يجب أن يكون بصيغة صحيحة مثل 99 أو 99.99")
            return render(request, "accounts/subscription_edit.html", ctx)

        try:
            price = (
                Decimal(price_raw)
                .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            )
            if price < 0 or price > Decimal("9999.99"):
                raise ValueError
        except (InvalidOperation, ValueError):
            messages.error(request, "السعر غير صالح.")
            return render(request, "accounts/subscription_edit.html", ctx)

        try:
            with transaction.atomic():
                subscription.name          = name
                subscription.duration_days = duration_days
                subscription.price         = price
                subscription.description   = description
                subscription.status        = status
                subscription.save()
        except Exception as e:
            print(e)  
            messages.error(
                request,
                "❌ عذرًا، لم نتمكن من التعديل على خطة الاشتراك. الرجاء التحقق من البيانات والمحاولة مرة أخرى.",
            )
            return render(request, "accounts/subscription_edit.html", ctx)

        messages.success(request, "تم تعديل الاشتراك بنجاح!")
        return redirect("accounts:subscription_view")

    return render(request, "accounts/subscription_edit.html", {"subscription": subscription})
@login_required
@staff_member_required
def edit_major_view(request:HttpRequest,id):
    major=Major.objects.get(pk=id)

    if request.method=='POST':
        ar_name          = request.POST.get('ar_name', '').strip()
        en_name = request.POST.get('en_name', '').strip()
      
        status        = bool(request.POST.get('status')) 

        missing = []
        if not ar_name:
            missing.append('اسم المدينة بالعربي')
      

        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, 'accounts/major_edit.html', {
                'ar_name': ar_name,
                'en_name':         en_name,
                
                'status':       status,
            })
       
        with transaction.atomic():
            try:
                major.ar_name=ar_name
                major.en_name=en_name
                major.status=status
                major.save()
               
            except Exception as e:
                messages.error(
                    request,
                    "❌ عذرًا، لم نتمكن من التعديل على التخصص . الرجاء التحقق من البيانات والمحاولة مرة أخرى."
                )
                return render(request, 'accounts/major_edit.html', {
                'ar_name': ar_name,
                'en_name':         en_name,
                'status':       status,
            })



        messages.success(request, "تم التعديل التخصص بنجاح!")
        return redirect('accounts:major_view')
    return render(request,'accounts/major_edit.html',{"major":major})
@login_required
@staff_member_required
def add_major_view(request:HttpRequest):

    if request.method=='POST':
        ar_name          = request.POST.get('ar_name', '').strip()
        en_name = request.POST.get('en_name', '').strip()
      
        status        = bool(request.POST.get('status')) 
        print(request.POST)

        missing = []
        if not ar_name:
            missing.append('اسم المدينة بالعربي')
       
       

        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, 'accounts/major_add.html', {
                'ar_name': ar_name,
                'en_name':         en_name,
                
                'status':       status,
            })
       
        with transaction.atomic():
            try:
                Major.objects.create(ar_name=ar_name,en_name=en_name,status=status)
                
               
            except Exception as e:
                messages.error(
                    request,
                    "❌ عذرًا، لم نتمكن من الاضافة على التخصص . الرجاء التحقق من البيانات والمحاولة مرة أخرى."
                )
                return render(request, 'accounts/major_add.html', {
                'ar_name': ar_name,
                'en_name':         en_name,
                'status':       status,
            })



        messages.success(request, "تم اضافة التخصص بنجاح!")
        return redirect('accounts:major_view')
    return render(request,'accounts/major_add.html')

def resend_signup_otp(request):
    data = request.session.get('pending_signup')
    if not data:
        return redirect('accounts:signup_view')

    email = data['email']
    now = timezone.now()
    last_otp = EmailOTP.objects.filter(
        user_email=email,
        used=False
    ).order_by('-created_at').first()

    if last_otp and now - last_otp.created_at < timedelta(minutes=2):
        remaining = 120 - int((now - last_otp.created_at).total_seconds())
        messages.error(request, f"📥 يمكنك إعادة الإرسال بعد {remaining} ثانية.")
        return redirect('accounts:verify_signup_otp')

    EmailOTP.objects.filter(user_email=email, used=False).update(used=True)

    otp_code = f"{random.randint(0, 999999):06d}"
    EmailOTP.objects.create(user_email=email, code=otp_code)

    send_mail(
        subject="رمز التحقق",
        message=(
            f"مرحبًا {data['full_name']},\n\n"
            f"هذا رمز التحقق الجديد: {otp_code}\n"
            "صالح لمدة 10 دقائق."
        ),
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )
    messages.success(request, "📥 تم إعادة إرسال الرمز إلى بريدك الإلكتروني.")

    return redirect('accounts:verify_signup_otp')


@login_required
@staff_member_required
@require_POST
def city_delete_all(request:HttpRequest):
    try:
        if request.method=='POST':
            ids=request.POST.getlist('selected_users')
            if ids:
                City.objects.filter(id__in=ids).delete()
                messages.success(request,"✅ تم حذف المدن المحددة بنجاح.")
    except:
        messages.error(
            request,
            "❌ حدث خطأ أثناء حذف المدن المحددة. حاول مرة أخرى لاحقًا."
        )
    return redirect('accounts:city_view')
@login_required
@staff_member_required
def city_view(request: HttpRequest):
    q = request.GET.get('q', '').strip()
    city_qs = City.objects.all().order_by('-id')

    if q:
        city_qs = city_qs.filter(
            Q(arabic_name__icontains=q) |
            Q(id__icontains=q) |

            Q(english_name__icontains=q) |
            Q(status__icontains=q) 
        ).distinct()
    
    paginator=Paginator(city_qs,5)
    page=request.GET.get('page')
    user_page=paginator.get_page(page)
    context={"city_page":user_page,'q': q}

    return render(request, 'accounts/city_list.html',context)
@login_required
@staff_member_required
def edit_city_view(request:HttpRequest,id):
    city=City.objects.get(pk=id)

    if request.method=='POST':
        arabic_name          = request.POST.get('arabic_name', '').strip()
        english_name = request.POST.get('english_name', '').strip()
      
        status        = bool(request.POST.get('status')) 

        missing = []
        if not arabic_name:
            missing.append('اسم المدينة بالعربي')
      

        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, 'accounts/city_edit.html', {
                'arabic_name': arabic_name,
                'english_name':         english_name,
                
                'status':       status,
            })
       
        with transaction.atomic():
            try:
                city.arabic_name=arabic_name
                city.english_name=english_name
                city.status=status
                city.save()
               
            except Exception as e:
                messages.error(
                    request,
                    "❌ عذرًا، لم نتمكن من التعديل على المدينة . الرجاء التحقق من البيانات والمحاولة مرة أخرى."
                )
                return render(request, 'accounts/city_edit.html', {
                'arabic_name': arabic_name,
                'english_name':         english_name,
                'status':       status,
            })



        messages.success(request, "تم التعديل على المدينة بنجاح!")
        return redirect('accounts:city_view')
    return render(request,'accounts/city_edit.html',{"city":city})
@login_required
@staff_member_required
def add_city_view(request:HttpRequest):

    if request.method=='POST':
        arabic_name          = request.POST.get('arabic_name', '').strip()
        english_name = request.POST.get('english_name', '').strip()
      
        status        = bool(request.POST.get('status')) 

        missing = []
        if not arabic_name:
            missing.append('اسم المدينة بالعربي')
       
       

        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, 'accounts/city_add.html', {
                'arabic_name': arabic_name,
                'english_name':         english_name,
                
                'status':       status,
            })
       
        with transaction.atomic():
            try:
                City.objects.create(arabic_name=arabic_name,english_name=english_name,status=status)
                
               
            except Exception as e:
                messages.error(
                    request,
                    "❌ عذرًا، لم نتمكن من اضافة المدينة . الرجاء التحقق من البيانات والمحاولة مرة أخرى."
                )
                return render(request, 'accounts/major_add.html', {
                'arabic_name': arabic_name,
                'english_name':         english_name,
                'status':       status,
            })



        messages.success(request, "تم اضافة المدينة بنجاح!")
        return redirect('accounts:city_view')
    return render(request,'accounts/city_add.html')
#industry
@login_required
@staff_member_required
@require_POST
def industry_delete_all(request:HttpRequest):
    try:
        if request.method=='POST':
            ids=request.POST.getlist('selected_users')
            if ids:
                Industry.objects.filter(id__in=ids).delete()
                messages.success(request,"✅ تم حذف المجالات المحددة بنجاح.")
    except:
        messages.error(
            request,
            "❌ حدث خطأ أثناء حذف المجالات المحددة. حاول مرة أخرى لاحقًا."
        )
    return redirect('accounts:industry_view')
@login_required
@staff_member_required
def industry_view(request: HttpRequest):
    q = request.GET.get('q', '').strip()
    industry_qs = Industry.objects.all().order_by('-id')

    if q:
        industry_qs = industry_qs.filter(
            Q(arabic_name__icontains=q) |
            Q(id__icontains=q) |

            Q(english_name__icontains=q) |
            Q(status__icontains=q) 
        ).distinct()
    
    paginator=Paginator(industry_qs,5)
    page=request.GET.get('page')
    user_page=paginator.get_page(page)
    context={"industry_page":user_page,'q': q}

    return render(request, 'accounts/industry_list.html',context)
@login_required
@staff_member_required
def edit_industry_view(request:HttpRequest,id):
    industry=Industry.objects.get(pk=id)

    if request.method=='POST':
        arabic_name          = request.POST.get('arabic_name', '').strip()
        english_name = request.POST.get('english_name', '').strip()
      
        status        = bool(request.POST.get('status')) 

        missing = []
        if not arabic_name:
            missing.append('اسم المجال بالعربي')
      

        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, 'accounts/industry_edit.html', {
                'arabic_name': arabic_name,
                'english_name':         english_name,
                
                'status':       status,
            })
       
        with transaction.atomic():
            try:
                industry.arabic_name=arabic_name
                industry.english_name=english_name
                industry.status=status
                industry.save()
               
            except Exception as e:
                messages.error(
                    request,
                    "❌ عذرًا، لم نتمكن من التعديل على المجال . الرجاء التحقق من البيانات والمحاولة مرة أخرى."
                )
                return render(request, 'accounts/industry_edit.html', {
                'arabic_name': arabic_name,
                'english_name':         english_name,
                'status':       status,
            })



        messages.success(request, "تم التعديل على المدينة بنجاح!")
        return redirect('accounts:industry_view')
    return render(request,'accounts/industry_edit.html',{"industry":industry})
@login_required
@staff_member_required
def add_industry_view(request:HttpRequest):

    if request.method=='POST':
        arabic_name          = request.POST.get('arabic_name', '').strip()
        english_name = request.POST.get('english_name', '').strip()
      
        status        = bool(request.POST.get('status')) 

        missing = []
        if not arabic_name:
            missing.append('اسم المجال بالعربي')
       
       

        if missing:
            messages.error(request, "هذه الحقول مطلوبة: " + ", ".join(missing))
            return render(request, 'accounts/industry_add.html', {
                'arabic_name': arabic_name,
                'english_name':         english_name,
                
                'status':       status,
            })
       
        with transaction.atomic():
            try:
                Industry.objects.create(arabic_name=arabic_name,english_name=english_name,status=status)
                
               
            except Exception as e:
                messages.error(
                    request,
                    "❌ عذرًا، لم نتمكن من اضافة المجال . الرجاء التحقق من البيانات والمحاولة مرة أخرى."
                )
                return render(request, 'accounts/industry_add.html', {
                'arabic_name': arabic_name,
                'english_name':         english_name,
                'status':       status,
            })



        messages.success(request, "تم اضافة المجال بنجاح!")
        return redirect('accounts:industry_view')
    return render(request,'accounts/industry_add.html')

@login_required
@staff_member_required
def subscription_detail_view(request, id):
    q = request.GET.get('q', '').strip()

    plan = get_object_or_404(SubscriptionPlan, pk=id)

    subscriber_qs = plan.user_subscriptions.order_by('-id')

    if q:
        subscriber_qs = subscriber_qs.filter(
            Q(payment_id__icontains=q) |
            Q(user__username__icontains=q) |
            Q(id__icontains=q)
        ).distinct()

    paginator = Paginator(subscriber_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accounts/subscription_detail.html', {
        'plan': plan,
        'subscriber_page': page_obj,
        'q': q,
    })
@login_required
@staff_member_required
@require_POST
def subscription_detail_delete_all(request, id):
    plan = get_object_or_404(SubscriptionPlan, pk=id)

    ids = request.POST.getlist('selected_users')
    if ids:
        UserSubscription.objects.filter(id__in=ids).delete()
        messages.success(request, "✅ تم حذف المشتركين المحددين بنجاح.")
    else:
        messages.warning(request, "لم يتم تحديد أي مشتركين للحذف.")

    return redirect('accounts:subscription_detail_view', id=plan.id)

@login_required
@staff_member_required
def company_edit_request_list(request):
    q = request.GET.get('q','').strip()
    qs = CompanyProfileEditRequest.objects.filter(status='PENDING')\
          .select_related('company__user','industry','city')\
          .order_by('-submitted_at')
    if q:
        qs = qs.filter(company__company_name__icontains=q)

    # simple pagination
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    edit_page = paginator.get_page(page)

    return render(request, 'accounts/company_edit_request_list.html', {
        'edit_page': edit_page,
        'q': q,
    })

@login_required
@staff_member_required
def approve_company_edit_request(request, pk):
    edit = get_object_or_404(
        CompanyProfileEditRequest, pk=pk, status='PENDING'
    )
    edit.approve(admin_user=request.user)
    messages.success(request, "تم قبول طلب التعديل وحُفظ بنجاح.")
    return redirect('accounts:company_edit_request_list')

@login_required
@staff_member_required
def reject_company_edit_request(request, pk):
    edit = get_object_or_404(
        CompanyProfileEditRequest, pk=pk, status='PENDING'
    )
    edit.reject(admin_user=request.user)
    messages.success(request, "تم رفض طلب التعديل وحُذف.")
    return redirect('accounts:company_edit_request_list')