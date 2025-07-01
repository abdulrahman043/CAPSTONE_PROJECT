from django.shortcuts import render , redirect
from django.http import HttpRequest
from django.core.mail import send_mail
from django.conf import settings
from posts.models import TrainingOpportunity, Application
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from profiles.models import StudentProfile, Industry, CompanyProfile, City,Major
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q



def home_view(request:HttpRequest):
    # Redirect student to dashboard if logged in
    if request.user.is_authenticated and hasattr(request.user, 'student_profile') and request.user.student_profile:
        return redirect('main:student_dashboard')
    # Redirect company maybe?
    elif request.user.is_authenticated and hasattr(request.user, 'company_profile') and request.user.company_profile:
       return redirect('posts:company_dashboard') # Example redirect for company
    return render(request, 'main/home.html')

@login_required
def student_dashboard_view(request):
    # Ensure user has a student profile
    if not hasattr(request.user, 'student_profile') or not request.user.student_profile:
        return redirect('main:home_view')

    student = request.user.student_profile
    applications = Application.objects.filter(student=student).select_related('opportunity__company', 'opportunity__city').order_by('-applied_at')

    student_major = None
    if hasattr(student, 'education') and student.education.exists():
         education = student.education.first()
         if education and hasattr(education, 'major'):
            student_major = education.major

    related_opps = []
    if student_major:
        related_opps = TrainingOpportunity.objects.filter(
            majors_needed=student_major,
            status=TrainingOpportunity.Status.ACTIVE,
            application_deadline__gte=timezone.now().date()
        ).exclude(
            applications__student=student
        ).select_related('company', 'city').distinct().order_by('-created_at')[:5]

    return render(request, 'main/student_dashboard.html', {
        'student_profile': student,
        'applications': applications,
        'related_opps': related_opps,
    })

def training_view(request):
    """
    Displays Training Opportunities with filtering, search, pagination,
    and default major filtering for logged-in students on initial load.
    """
    # --- Get Filter, Search, and Page Parameters ---
    selected_city_id = request.GET.get('city', '').strip()
    selected_industry_id = request.GET.get('industry', '').strip()
    # Check if majors_needed was explicitly passed in the GET request
    majors_filter_applied = 'majors_needed' in request.GET
    selected_major_ids = request.GET.getlist('majors_needed') # Get list even if empty
    search_query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page')
    selected_city = City.objects.filter(id=selected_city_id).first() if selected_city_id else None
    selected_industry = Industry.objects.filter(id=selected_industry_id).first() if selected_industry_id else None
    # Convert submitted major IDs to integers for filtering, handle potential errors
    major_ids_int = []
    if majors_filter_applied:
        try:
            major_ids_int = [int(mid) for mid in selected_major_ids if mid]
        except ValueError:
            # Handle error if non-integer values are passed
            pass # Or add a message

    # --- Prepare Base Queryset ---
    opportunities_list = TrainingOpportunity.objects.filter(
        status=TrainingOpportunity.Status.ACTIVE,
        application_deadline__gte=timezone.now().date()
    ).select_related(
        'company__industry', 'city'
    ).prefetch_related(
        'majors_needed'
    ).order_by('-created_at')

    # --- Apply Text Search Filter ---
    if search_query:
        opportunities_list = opportunities_list.filter(
            Q(company__company_name__icontains=search_query) |
            Q(city__arabic_name__icontains=search_query) |
            Q(requirements__icontains=search_query) |
            Q(benefits__icontains=search_query)
        ).distinct()

    # --- Apply Explicit Dropdown/Select Filters ---
    if selected_city_id:
        opportunities_list = opportunities_list.filter(city__id=selected_city_id)

    if selected_industry_id:
        opportunities_list = opportunities_list.filter(company__industry__id=selected_industry_id)

    # --- Determine and Apply Major Filter (Default or Explicit) ---
    student_major_ids_for_default = []
    apply_default_major_filter = False

    # Check for default filtering conditions
    if not majors_filter_applied and request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        # Attempt to get student's primary major ID(s)
        # ** IMPORTANT: Adjust this logic based on your data model **
        # Example: Get major ID from the *first* Education record found (if any)
        try:
            first_education = request.user.student_profile.education.filter(major__isnull=False).first()
            if first_education and first_education.major:
                student_major_ids_for_default = [first_education.major.id] # Use a list
                apply_default_major_filter = True
                # If using default, set the selected IDs for the template context
                current_selected_major_ids_str = [str(mid) for mid in student_major_ids_for_default]
            else:
                 # Student has no major defined, don't apply default filter
                 current_selected_major_ids_str = []
        except Exception:
            current_selected_major_ids_str = []
            pass # Fail silently or log error

    else:
        # User applied filters explicitly or is not a student
        current_selected_major_ids_str = [str(mid) for mid in major_ids_int]
        if major_ids_int: # Apply filter only if valid IDs were selected/passed
             opportunities_list = opportunities_list.filter(majors_needed__id__in=major_ids_int).distinct()

    # Apply the default filter AFTER other explicit filters if needed
    if apply_default_major_filter:
         opportunities_list = opportunities_list.filter(majors_needed__id__in=student_major_ids_for_default).distinct()


    # --- Pagination ---
    paginator = Paginator(opportunities_list, 9) # Adjust items per page
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # --- Prepare Context Data for Template ---
    all_cities = City.objects.filter(status=True).order_by('arabic_name')
    all_industries = Industry.objects.filter(status=True).order_by('arabic_name')
    all_majors = Major.objects.filter(status=True).order_by('ar_name')

    context = {
        'opportunities': page_obj.object_list, # Renamed to match template loop var
        'page_obj': page_obj,
        'selected_city': selected_city,
        'selected_industry': selected_industry,
        'all_cities': all_cities,
        'all_industries': all_industries,
        'all_majors': all_majors,
        'selected_city_id': selected_city_id,
        'selected_industry_id': selected_industry_id,
        # This now correctly reflects either default or explicit major selection
        'selected_major_ids': current_selected_major_ids_str,
        'search_query': search_query,
    }
    return render(request, 'main/training.html', context)

def about_view(request:HttpRequest):
    return render(request,'main/about.html')

def contact_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not email or not subject or not message:
            return render(request, 'main/contact.html', {'error': 'يرجى ملء جميع الحقول.'})

        full_message = f"From: {email}\n\nSubject: {subject}\n\nMessage:\n{message}"

        try:
            # Use a setting for the recipient email if possible
            recipient_list = [getattr(settings, 'CONTACT_EMAIL', 'wasslpoint@gmail.com')]
            send_mail(
                f"WasslPoint Contact: {subject}",
                full_message,
                settings.EMAIL_HOST_USER,
                recipient_list,
                fail_silently=False,
            )
            return render(request, 'main/contact.html', {'success': True})
        except Exception as e:
            print(f"Error sending contact email: {e}") # Log error
            return render(request, 'main/contact.html', {'error': 'حدث خطأ أثناء إرسال الرسالة. يرجى المحاولة مرة أخرى.'})

    return render(request, 'main/contact.html')

def company_view(request):
    """
    Displays a paginated list of registered companies with filters for Industry AND City,
    and search by company name.
    """
    company_list = CompanyProfile.objects.filter(
        user__is_active=True
    ).select_related('user', 'industry', 'city').order_by('company_name')

    selected_industry_id = request.GET.get('industry')
    selected_city_id = request.GET.get('city')
    company_name_search = request.GET.get('company_name_search', '').strip()
    selected_city = City.objects.filter(id=selected_city_id).first() if selected_city_id else None
    selected_industry = Industry.objects.filter(id=selected_industry_id).first() if selected_industry_id else None

    # Apply Industry Filter
    if selected_industry_id:
        try:
            selected_industry_id_int = int(selected_industry_id)
            company_list = company_list.filter(industry__id=selected_industry_id_int)
        except (ValueError, TypeError):
            selected_industry_id = None

    # Apply City Filter
    if selected_city_id:
       try:
           selected_city_id_int = int(selected_city_id)
           company_list = company_list.filter(city__id=selected_city_id_int)
       except (ValueError, TypeError):
           selected_city_id = None

    # Apply Company Name Search Filter
    if company_name_search:
        company_list = company_list.filter(company_name__icontains=company_name_search)

    # Pagination
    paginator = Paginator(company_list, 9)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # --- >>>>> FIX: Order by 'arabic_name' based on FieldError <<<<< ---
    industries = Industry.objects.filter(status=True).order_by('arabic_name')
    # --- >>>>> END FIX <<<<< ---
    cities = City.objects.filter(status=True).order_by('arabic_name')

    context = {
        'page_obj': page_obj,
        'industries': industries,
        'selected_city': selected_city,
        'selected_industry': selected_industry,

        'cities': cities,
        'selected_industry_id': selected_industry_id,
        'selected_city_id': selected_city_id,
        'company_name_search': company_name_search,
    }
    return render(request, 'main/company.html', context)