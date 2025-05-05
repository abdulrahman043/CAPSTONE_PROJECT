from django.shortcuts import render , redirect
from django.http import HttpRequest
from django.core.mail import send_mail
from django.conf import settings
from posts.models import TrainingOpportunity, Application
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from profiles.models import StudentProfile, Industry, CompanyProfile, City
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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

def training_view(request:HttpRequest):
    active_opportunities = TrainingOpportunity.objects.filter(
        status=TrainingOpportunity.Status.ACTIVE,
        application_deadline__gte=timezone.now().date()
        ).select_related('company', 'city').order_by('-created_at')
    return render(request,'main/training.html',{"opportunities":active_opportunities})

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
    """ Displays a paginated list of registered companies with filters and search. """

    # Base queryset
    company_list = CompanyProfile.objects.filter(
        user__is_active=True
    ).select_related('user', 'industry').order_by('company_name')

    # Get filter and search parameters from GET request
    selected_industry_id = request.GET.get('industry')
    company_name_search = request.GET.get('company_name_search', '').strip() # Get search term, default to empty string

    # Apply Industry Filter
    if selected_industry_id:
        try:
            selected_industry_id_int = int(selected_industry_id)
            company_list = company_list.filter(industry__id=selected_industry_id_int)
        except (ValueError, TypeError):
            selected_industry_id = None

    # Apply Company Name Search Filter
    if company_name_search:
        # Using case-insensitive contains search on company_name
        company_list = company_list.filter(company_name__icontains=company_name_search)

    # Pagination
    paginator = Paginator(company_list, 9) # 9 companies per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # Data for Filter Dropdowns
    industries = Industry.objects.filter(status=True).order_by('arabic_name')

    context = {
        'page_obj': page_obj,
        'industries': industries,
        'selected_industry_id': selected_industry_id,
        'company_name_search': company_name_search, # Pass search term back to template
    }
    return render(request, 'main/company.html', context)