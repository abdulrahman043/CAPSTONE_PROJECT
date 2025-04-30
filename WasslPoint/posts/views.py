from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TrainingOpportunity, Application, Message
from profiles.models import CompanyProfile, StudentProfile, Major, City
from django.core.exceptions import PermissionDenied
from django.utils import timezone

@login_required
def opportunity_list(request):
    """
    Displays a list of all active training opportunities for students.
    """
    opportunities = TrainingOpportunity.objects.filter(status=TrainingOpportunity.Status.ACTIVE).select_related('company', 'city').prefetch_related('majors_needed')
    print(f"Number of opportunities: {opportunities.count()}") # Add this line
    print(f"Opportunities: {opportunities}")
    return render(request, 'posts/opportunity_list.html', {'opportunities': opportunities})

@login_required
def company_opportunities(request):
    """
    Displays all training opportunities for a company.
    """
    try:
        company_profile = request.user.company_profile
        # Fetch opportunities related to the logged-in company
        opportunities = TrainingOpportunity.objects.filter(company=company_profile).select_related('city').prefetch_related('majors_needed')
        print(f"Company: {company_profile}")  # Print the company profile
        print(f"Number of opportunities for company: {opportunities.count()}")  # Print the count
        print(f"Opportunities for company: {opportunities}") # Print the opportunities
        return render(request, 'main/company.html', {'opportunities': opportunities, 'company_profile': company_profile}) # Pass company_profile to the template
    except CompanyProfile.DoesNotExist:
        return redirect('profiles:company_profile_view')  # Redirect to company profile creation if it doesn't exist

@login_required
def create_opportunity(request):
    """
    Allows a company to create a new training opportunity.
    """
    try:
        company_profile = request.user.company_profile
        majors = Major.objects.filter(status=True)
        cities = City.objects.filter(status=True)
        if request.method == 'POST':
            major_ids = request.POST.getlist('majors_needed')
            city_id = request.POST.get('city')
            start_date_str = request.POST.get('start_date')
            duration = request.POST.get('duration')
            application_deadline_str = request.POST.get('application_deadline')
            requirements = request.POST.get('requirements')
            benefits = request.POST.get('benefits')
            status = request.POST.get('status')

            if all([major_ids, city_id, start_date_str, duration, application_deadline_str, requirements]):
                opportunity = TrainingOpportunity.objects.create(
                    company=company_profile,
                    city=City.objects.get(pk=city_id),
                    start_date=timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date(),
                    duration=duration,
                    application_deadline=timezone.datetime.strptime(application_deadline_str, '%Y-%m-%d').date(),
                    requirements=requirements,
                    benefits=benefits,
                    status=status,
                )
                opportunity.majors_needed.set(major_ids)
                return redirect('posts:company_opportunities')
            else:
                return render(
                    request,
                    'posts/create_opportunity.html',
                    {
                        'errors': 'All required fields must be filled.',
                        'majors': majors,
                        'cities': cities,
                        'statuses': TrainingOpportunity.Status.choices,
                    },
                )
        else:
            return render(
                request, 'posts/create_opportunity.html', {'majors': majors, 'cities': cities, 'statuses': TrainingOpportunity.Status.choices}
            )
    except CompanyProfile.DoesNotExist:
        return redirect('profiles:company_profile_view')

@login_required
def opportunity_detail(request, opportunity_id):
    """
    Displays the details of a specific training opportunity.
    """
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)
    applied = False
    if hasattr(request.user, 'student_profile'):
        applied = Application.objects.filter(opportunity=opportunity, student=request.user.student_profile).exists()
    return render(request, 'posts/opportunity_detail.html', {'opportunity': opportunity, 'applied': applied})

@login_required
def apply_opportunity(request, opportunity_id):
    """
    Allows a student to apply for a training opportunity.
    """
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)
    try:
        student_profile = request.user.student_profile
        if request.method == 'POST':
            message = request.POST.get('message')
            if not Application.objects.filter(opportunity=opportunity, student=student_profile).exists():
                Application.objects.create(opportunity=opportunity, student=student_profile, message=message)
                return redirect('posts:application_status')
            else:
                return render(
                    request,
                    'posts/apply_opportunity.html',
                    {'opportunity': opportunity, 'error': 'You have already applied for this opportunity.'},
                )
        else:
            if Application.objects.filter(opportunity=opportunity, student=student_profile).exists():
                return redirect('posts:application_status')  # Or display a message
            return render(request, 'posts/apply_opportunity.html', {'opportunity': opportunity})
    except StudentProfile.DoesNotExist:
        return redirect('profiles:profile_view')  # Redirect to create student profile

@login_required
def application_status(request):
    """
    Displays the application status for a student.
    """
    try:
        student_profile = request.user.student_profile
        applications = Application.objects.filter(student=student_profile).select_related('opportunity__company', 'opportunity__city').prefetch_related('opportunity__majors_needed')
        return render(request, 'posts/application_status.html', {'applications': applications})
    except StudentProfile.DoesNotExist:
        return redirect('profiles:profile_view')

@login_required
def opportunity_applications(request, opportunity_id):
    """
    Displays the applications for a specific training opportunity to the company.
    """
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)
    try:
        company_profile = request.user.company_profile
        if opportunity.company != company_profile:
            raise PermissionDenied
        applications = Application.objects.filter(opportunity=opportunity).select_related('student__user')
        return render(
            request,