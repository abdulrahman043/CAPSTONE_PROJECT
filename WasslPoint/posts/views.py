# WasslPoint/posts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import TrainingOpportunity, Application, Message
from profiles.models import CompanyProfile, StudentProfile, Major, City
from subscriptions.models import has_active_subscription # Import subscription check
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods
from django.urls import reverse

# --- Helper Decorators ---
def company_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'company_profile'):
            messages.error(request, "Access denied. Company profile required.")
            # Decide where to redirect non-companies (e.g., home or profile page)
            return redirect('main:home_view')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def student_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'student_profile'):
            messages.error(request, "Access denied. Student profile required.")
             # Redirect non-students (e.g., home or company profile if they have one)
            if hasattr(request.user, 'company_profile'):
                 return redirect('profiles:company_profile_view')
            return redirect('main:home_view') # Or perhaps profile creation page
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# --- Public/Student Views ---

def opportunity_list(request):
    """ Displays active opportunities viewable by anyone. """
    opportunities = TrainingOpportunity.objects.filter(
        status=TrainingOpportunity.Status.ACTIVE,
        application_deadline__gte=timezone.now().date() # Only show if deadline hasn't passed
    ).select_related('company', 'city').prefetch_related('majors_needed')
    return render(request, 'posts/opportunity_list.html', {'opportunities': opportunities})

def opportunity_detail(request, opportunity_id):
    """ Displays details of a specific opportunity. Viewable by anyone. """
    opportunity = get_object_or_404(
        TrainingOpportunity.objects.select_related('company', 'city').prefetch_related('majors_needed'),
        pk=opportunity_id
    )

    context = {'opportunity': opportunity}
    application = None
    can_apply = False
    can_withdraw = False

    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        student_profile = request.user.student_profile
        try:
            application = Application.objects.get(opportunity=opportunity, student=student_profile)
            context['application'] = application
            if application.status == Application.ApplicationStatus.PENDING or application.status == Application.ApplicationStatus.ACCEPTED:
                 can_withdraw = True
        except Application.DoesNotExist:
            # Check if eligible to apply
            if opportunity.status == TrainingOpportunity.Status.ACTIVE and opportunity.application_deadline >= timezone.now().date():
                 # Check subscription status before enabling apply button visually
                 if has_active_subscription(request.user):
                      can_apply = True
                 else:
                      # Optionally add a message indicating subscription needed
                      context['subscription_needed'] = True


    context['can_apply'] = can_apply
    context['can_withdraw'] = can_withdraw

    return render(request, 'posts/opportunity_detail.html', context)


@login_required # Must be logged in
@student_required # Must have student profile
@require_POST # Only allow POST requests
def apply_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)
    student_profile = request.user.student_profile

    # 1. Check Subscription
    if not has_active_subscription(request.user):
        messages.error(request, "You need an active subscription to apply for opportunities.")
        # Redirect to subscription plans page
        return redirect('subscriptions:plans')

    # 2. Check Opportunity Status and Deadline
    if opportunity.status != TrainingOpportunity.Status.ACTIVE:
        messages.error(request, "This opportunity is no longer active.")
        return redirect('posts:opportunity_detail', opportunity_id=opportunity_id)
    if opportunity.application_deadline < timezone.now().date():
        messages.error(request, "The application deadline for this opportunity has passed.")
        return redirect('posts:opportunity_detail', opportunity_id=opportunity_id)

    # 3. Check if already applied (or withdrawn)
    existing_application, created = Application.objects.get_or_create(
        opportunity=opportunity,
        student=student_profile,
        defaults={'status': Application.ApplicationStatus.PENDING} # Default status if creating
    )

    if not created:
        # Application already existed
        if existing_application.status == Application.ApplicationStatus.WITHDRAWN:
             # Allow re-applying if withdrawn by changing status back to PENDING
             existing_application.status = Application.ApplicationStatus.PENDING
             existing_application.applied_at = timezone.now() # Reset application time? Optional.
             existing_application.message = request.POST.get('message', '') # Update message if provided
             existing_application.save()
             messages.success(request, "You have re-applied for this opportunity.")
             return redirect('posts:my_applications')
        else:
            # Already applied and not withdrawn
            messages.warning(request, "You have already applied for this opportunity.")
            return redirect('posts:opportunity_detail', opportunity_id=opportunity_id)
    else:
         # Application was newly created
         existing_application.message = request.POST.get('message', '')
         existing_application.save()
         messages.success(request, "Application submitted successfully!")
         # Redirect to list of their applications
         return redirect('posts:my_applications')


@login_required
@student_required
def my_applications_list(request):
    """ Shows the logged-in student their applications. """
    applications = Application.objects.filter(
        student=request.user.student_profile
    ).select_related('opportunity__company', 'opportunity__city').order_by('-applied_at')
    return render(request, 'posts/my_applications.html', {'applications': applications})


@login_required
@student_required
@require_POST # Ensure this action is done via POST
def withdraw_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id, student=request.user.student_profile)

    if application.status not in [Application.ApplicationStatus.PENDING, Application.ApplicationStatus.ACCEPTED]:
         messages.warning(request, f"Cannot withdraw application with status '{application.get_status_display()}'.")
         return redirect('posts:my_applications')

    application.status = Application.ApplicationStatus.WITHDRAWN
    application.save()
    messages.success(request, "Application withdrawn successfully.")
    return redirect('posts:my_applications')


# --- Company Views ---

@company_required # Use the decorator
def company_dashboard(request):
    """ Displays opportunities created by the logged-in company. """
    company_profile = request.user.company_profile
    opportunities = TrainingOpportunity.objects.filter(company=company_profile).prefetch_related('applications')
    context = {
        'opportunities': opportunities,
        'company_profile': company_profile
    }
    return render(request, 'posts/company_dashboard.html', context)


@company_required
def create_opportunity(request):
    company_profile = request.user.company_profile # Already checked by decorator
    majors = Major.objects.filter(status=True)
    cities = City.objects.filter(status=True)

    if request.method == 'POST':
        # Extract data
        major_ids = request.POST.getlist('majors_needed')
        city_id = request.POST.get('city')
        start_date_str = request.POST.get('start_date')
        duration = request.POST.get('duration')
        application_deadline_str = request.POST.get('application_deadline')
        requirements = request.POST.get('requirements')
        benefits = request.POST.get('benefits', '') # Optional
        status = request.POST.get('status', TrainingOpportunity.Status.ACTIVE) # Default to ACTIVE

        # Basic Validation
        errors = []
        if not major_ids: errors.append("At least one major must be selected.")
        if not city_id: errors.append("City is required.")
        if not start_date_str: errors.append("Start date is required.")
        if not duration: errors.append("Duration is required.")
        if not application_deadline_str: errors.append("Application deadline is required.")
        if not requirements: errors.append("Requirements are required.")

        try:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            application_deadline = timezone.datetime.strptime(application_deadline_str, '%Y-%m-%d').date() if application_deadline_str else None
            city = City.objects.get(pk=city_id) if city_id else None
        except (ValueError, City.DoesNotExist):
             errors.append("Invalid date format or city selection.")

        if start_date and application_deadline and application_deadline < start_date:
             errors.append("Application deadline cannot be before the start date.")

        if errors:
             for error in errors:
                 messages.error(request, error)
        else:
            try:
                opportunity = TrainingOpportunity.objects.create(
                    company=company_profile,
                    city=city,
                    start_date=start_date,
                    duration=duration,
                    application_deadline=application_deadline,
                    requirements=requirements,
                    benefits=benefits,
                    status=status
                )
                opportunity.majors_needed.set(major_ids)
                messages.success(request, "Training opportunity created successfully!")
                return redirect('posts:company_dashboard')
            except Exception as e:
                 messages.error(request, f"An error occurred while creating the opportunity: {e}")

    # Prepare context for GET request or if POST had errors
    context = {
        'majors': majors,
        'cities': cities,
        'statuses': TrainingOpportunity.Status.choices,
        'form_data': request.POST if request.method == 'POST' else {} # Repopulate form on error
    }
    return render(request, 'posts/opportunity_form.html', context)


@require_http_methods(["GET", "POST"]) # Allow GET for form display, POST for submission
@login_required # Must be logged in
def edit_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)

    # Permission Check: Must be staff OR the company owner
    is_owner = hasattr(request.user, 'company_profile') and opportunity.company == request.user.company_profile
    if not request.user.is_staff and not is_owner:
        messages.error(request, "You do not have permission to edit this opportunity.")
        return redirect('posts:opportunity_list') # Or appropriate redirect

    majors = Major.objects.filter(status=True)
    cities = City.objects.filter(status=True)

    if request.method == 'POST':
        # Extract data
        major_ids = request.POST.getlist('majors_needed')
        city_id = request.POST.get('city')
        start_date_str = request.POST.get('start_date')
        duration = request.POST.get('duration')
        application_deadline_str = request.POST.get('application_deadline')
        requirements = request.POST.get('requirements')
        benefits = request.POST.get('benefits', '')
        status = request.POST.get('status')

        # Basic Validation (similar to create)
        errors = []
        if not major_ids: errors.append("At least one major must be selected.")
        # ... (add other validations as in create_opportunity) ...
        try:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            application_deadline = timezone.datetime.strptime(application_deadline_str, '%Y-%m-%d').date() if application_deadline_str else None
            city = City.objects.get(pk=city_id) if city_id else None
        except (ValueError, City.DoesNotExist):
             errors.append("Invalid date format or city selection.")

        if start_date and application_deadline and application_deadline < start_date:
             errors.append("Application deadline cannot be before the start date.")

        if errors:
             for error in errors:
                 messages.error(request, error)
             # Re-render form with errors and existing data
             form_data = request.POST.copy() # Keep submitted data
             context = {
                 'opportunity': opportunity, # Pass opportunity being edited
                 'majors': majors, 'cities': cities, 'statuses': TrainingOpportunity.Status.choices,
                 'form_data': form_data, # Show submitted data again
                 'is_edit': True
             }
             return render(request, 'posts/opportunity_form.html', context)
        else:
             # Update opportunity
            try:
                opportunity.city = city
                opportunity.start_date = start_date
                opportunity.duration = duration
                opportunity.application_deadline = application_deadline
                opportunity.requirements = requirements
                opportunity.benefits = benefits
                opportunity.status = status
                opportunity.majors_needed.set(major_ids) # Update ManyToMany field
                opportunity.save()
                messages.success(request, "Opportunity updated successfully!")
                # Redirect based on user type
                if request.user.is_staff:
                    # Maybe an admin list view or back to detail?
                    return redirect('posts:opportunity_detail', opportunity_id=opportunity.id)
                else:
                    return redirect('posts:company_dashboard')
            except Exception as e:
                 messages.error(request, f"An error occurred while updating the opportunity: {e}")
                 # Re-render form if save fails unexpectedly
                 context = {
                     'opportunity': opportunity,
                     'majors': majors, 'cities': cities, 'statuses': TrainingOpportunity.Status.choices,
                     'form_data': request.POST, # Show submitted data again
                     'is_edit': True
                 }
                 return render(request, 'posts/opportunity_form.html', context)

    # GET Request: Populate form with existing data
    else:
        form_data = {
            'majors_needed': list(opportunity.majors_needed.values_list('id', flat=True)),
            'city': opportunity.city.id if opportunity.city else '',
            'start_date': opportunity.start_date.strftime('%Y-%m-%d') if opportunity.start_date else '',
            'duration': opportunity.duration,
            'application_deadline': opportunity.application_deadline.strftime('%Y-%m-%d') if opportunity.application_deadline else '',
            'requirements': opportunity.requirements,
            'benefits': opportunity.benefits,
            'status': opportunity.status,
        }
        context = {
            'opportunity': opportunity, # Pass opportunity being edited
            'majors': majors,
            'cities': cities,
            'statuses': TrainingOpportunity.Status.choices,
            'form_data': form_data, # Populate with existing data
            'is_edit': True
        }
        return render(request, 'posts/opportunity_form.html', context)


@require_POST # Only allow POST requests for deletion
@login_required
def delete_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)

    # Permission Check: Must be staff OR the company owner
    is_owner = hasattr(request.user, 'company_profile') and opportunity.company == request.user.company_profile
    if not request.user.is_staff and not is_owner:
        messages.error(request, "You do not have permission to delete this opportunity.")
         # Decide redirect target (e.g., opportunity list or detail)
        return redirect(request.META.get('HTTP_REFERER', reverse('posts:opportunity_list')))


    try:
        opportunity_name = str(opportunity) # Get a name before deleting
        opportunity.delete()
        messages.success(request, f"Opportunity '{opportunity_name}' deleted successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred while deleting the opportunity: {e}")
        # Redirect back if deletion fails
        return redirect(request.META.get('HTTP_REFERER', reverse('posts:opportunity_detail', args=[opportunity_id])))

    # Redirect after successful deletion
    if request.user.is_staff and not is_owner:
         # If admin deleted it, maybe go to an admin list? For now, main list.
         return redirect('posts:opportunity_list')
    else: # If company owner deleted it
        return redirect('posts:company_dashboard')



@login_required
def opportunity_applications(request, opportunity_id):
    """ Company or Admin views applications for a specific opportunity """
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)

    # Permission Check: Staff or Company Owner
    is_owner = hasattr(request.user, 'company_profile') and opportunity.company == request.user.company_profile
    if not request.user.is_staff and not is_owner:
        raise PermissionDenied("You don't have permission to view these applications.")

    applications = Application.objects.filter(
        opportunity=opportunity
    ).select_related('student__user', 'student__personal_info').order_by('status', '-applied_at') # Group by status?

    context = {
        'opportunity': opportunity,
        'applications': applications,
        'statuses': Application.ApplicationStatus.choices # Pass choices for the update form
    }
    return render(request, 'posts/opportunity_applications.html', context)


@require_POST # Ensure status updates happen via POST
@login_required
def update_application_status(request, application_id):
    """ Company or Admin updates the status of an application """
    application = get_object_or_404(Application.objects.select_related('opportunity'), pk=application_id)
    opportunity = application.opportunity

    # Permission Check: Staff or Company Owner
    is_owner = hasattr(request.user, 'company_profile') and opportunity.company == request.user.company_profile
    if not request.user.is_staff and not is_owner:
        messages.error(request, "You do not have permission to update this application status.")
        # Redirect back to the list of applications for that opportunity
        return redirect('posts:opportunity_applications', opportunity_id=opportunity.id)

    new_status = request.POST.get('status')
    if new_status in Application.ApplicationStatus.values:
        # Prevent student from changing status back from withdrawn via this view
        if application.status == Application.ApplicationStatus.WITHDRAWN and request.user == application.student.user:
             messages.error(request, "Cannot update status from 'Withdrawn' here.")
        else:
            application.status = new_status
            application.save()
            messages.success(request, f"Application status updated to {application.get_status_display()}.")
            
    else:
        messages.error(request, "Invalid status selected.")

    return redirect('posts:opportunity_applications', opportunity_id=opportunity.id)


# --- Chat View ---
# Keep application_chat view as it was, ensuring permissions are checked implicitly
# (only users involved should access the chat link, which originates from application lists they have access to)
@login_required
def application_chat(request, application_id):
    application = get_object_or_404(Application.objects.select_related('student__user', 'opportunity__company__user'), pk=application_id)

    # Permission Check: Student applicant or Company representative/admin
    is_student = request.user == application.student.user
    is_company = request.user == application.opportunity.company.user
    is_admin = request.user.is_staff

    if not (is_student or is_company or is_admin):
         raise PermissionDenied("You do not have permission to view this chat.")


    messages_qs = Message.objects.filter(application=application).select_related('sender').order_by('sent_at')

    if request.method == 'POST':
        content = request.POST.get('content','').strip()
        if content:
            Message.objects.create(application=application, sender=request.user, content=content)
            # Redirect back to the chat page (or use AJAX for real-time)
            return redirect('posts:application_chat', application_id=application_id)
        else:
             messages.warning(request, "Cannot send an empty message.")


    context = {
        'application': application,
        'messages': messages_qs,
        'is_student_view': is_student, # Pass flag to template if needed
        'is_company_view': is_company, # Pass flag to template if needed
    }
    return render(request, 'posts/application_chat.html', context)
