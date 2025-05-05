# WasslPoint/posts/views.py
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required # Not used
from .models import TrainingOpportunity, Application, Message
from profiles.models import CompanyProfile, StudentProfile, Major, City
from subscriptions.models import has_active_subscription
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.contrib.messages import get_messages
from django.views.decorators.http import require_POST, require_http_methods
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import openpyxl

# --- Helper Decorators ---
def company_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'company_profile') or not request.user.company_profile:
            # Translated Message
            messages.error(request, "تم رفض الوصول. يتوجب عليك الدخول بحساب شركة.")
            return redirect('main:home_view')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def student_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'student_profile') or not request.user.student_profile:
            # Translated Message
            messages.error(request, "تم رفض الوصول. يتوجب عليك الدخول بحساب طالب.")
            if hasattr(request.user, 'company_profile') and request.user.company_profile:
                 return redirect('profiles:company_profile_view')
            return redirect('main:home_view')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# --- Public/Student Views ---

def opportunity_list(request):
    """ Displays active opportunities viewable by anyone. """
    opportunities = TrainingOpportunity.objects.filter(
        status=TrainingOpportunity.Status.ACTIVE,
        application_deadline__gte=timezone.now().date()
    ).select_related('company', 'city').prefetch_related('majors_needed').order_by('-created_at')
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
    subscription_needed_msg = False # Flag for template message

    if request.user.is_authenticated and hasattr(request.user, 'student_profile') and request.user.student_profile:
        student_profile = request.user.student_profile
        try:
            application = Application.objects.get(opportunity=opportunity, student=student_profile)
            context['application'] = application
            if application.status in [Application.ApplicationStatus.PENDING, Application.ApplicationStatus.ACCEPTED]:
                 can_withdraw = True
        except Application.DoesNotExist:
            if opportunity.status == TrainingOpportunity.Status.ACTIVE and opportunity.application_deadline >= timezone.now().date():
                 if has_active_subscription(request.user):
                      can_apply = True
                 else:
                      subscription_needed_msg = True

    context['can_apply'] = can_apply
    context['can_withdraw'] = can_withdraw
    context['subscription_needed_msg'] = subscription_needed_msg

    return render(request, 'posts/opportunity_detail.html', context)


@login_required
@student_required
@require_POST
def apply_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)
    student_profile = request.user.student_profile
    application_message = request.POST.get('message', '')

    # 1. Check Subscription
    if not has_active_subscription(request.user):
        # Translated Message
        messages.error(request, "تحتاج إلى اشتراك نشط للتقدم بطلب للحصول على الفرص.")
        return redirect('subscriptions:plans')

    # 2. Check Opportunity Status and Deadline
    if opportunity.status != TrainingOpportunity.Status.ACTIVE:
        # Translated Message
        messages.error(request, "هذه الفرصة لم تعد نشطة.")
        return redirect('posts:opportunity_detail', opportunity_id=opportunity_id)
    if opportunity.application_deadline < timezone.now().date():
        # Translated Message
        messages.error(request, "انتهى الموعد النهائي للتقديم لهذه الفرصة.")
        return redirect('posts:opportunity_detail', opportunity_id=opportunity_id)

    # 3. Check if already applied (or withdrawn)
    defaults = {
        'status': Application.ApplicationStatus.PENDING,
        'message': application_message,
        # 'student_has_seen_latest_status': True, # Assumes student knows initial status
        # 'company_has_seen_application': False, # Assumes company needs notification
    }
    existing_application, created = Application.objects.get_or_create(
        opportunity=opportunity,
        student=student_profile,
        defaults=defaults
    )

    if not created:
        if existing_application.status == Application.ApplicationStatus.WITHDRAWN:
             existing_application.status = Application.ApplicationStatus.PENDING
             existing_application.applied_at = timezone.now()
             existing_application.message = application_message # Update message
             # existing_application.student_has_seen_latest_status = True
             # existing_application.company_has_seen_application = False
             existing_application.save()
             # Translated Message
             messages.success(request, "لقد تمت إعادة التقديم على هذه الفرصة.")
             return redirect('posts:my_applications')
        else:
            # Translated Message
            messages.warning(request, "لقد قمت بالتقديم مسبقاً على هذه الفرصة.")
            return redirect('posts:opportunity_detail', opportunity_id=opportunity_id)
    else:
         # Application was newly created
         # Translated Message
         messages.success(request, "تم إرسال طلبك بنجاح!")
         return redirect('posts:my_applications')

@login_required
@student_required
def my_applications_list(request):
    """ Shows the logged-in student their applications with pagination. """
    student_profile = request.user.student_profile
    application_list = Application.objects.filter(
        student=student_profile
    ).select_related('opportunity__company', 'opportunity__city').order_by('-applied_at')

    # --- Placeholder: Mark unseen status updates as seen ---
    # Application.objects.filter(
    #     student=student_profile,
    #     student_has_seen_latest_status=False # Requires model field
    # ).update(student_has_seen_latest_status=True)
    # --- End Placeholder ---

    paginator = Paginator(application_list, 10)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/my_applications.html', context)


@login_required
@student_required
@require_POST
def withdraw_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id, student=request.user.student_profile)

    if application.status not in [Application.ApplicationStatus.PENDING, Application.ApplicationStatus.ACCEPTED]:
         # Translated Message
         messages.warning(request, f"لا يمكن سحب الطلب وهو بالحالة '{application.get_status_display()}'.")
         return redirect('posts:my_applications')

    application.status = Application.ApplicationStatus.WITHDRAWN
    # application.student_has_seen_latest_status = True # Student initiated, they have seen
    # application.company_has_seen_application = False # Company needs notification?
    application.save()
    # Translated Message
    messages.success(request, "تم سحب الطلب بنجاح.")
    return redirect('posts:my_applications')


# --- Company Views ---

@company_required
def company_dashboard(request):
    """ Displays opportunities created by the logged-in company. """
    company_profile = request.user.company_profile
    opportunities = TrainingOpportunity.objects.filter(company=company_profile).prefetch_related('applications').order_by('-created_at')
    context = {
        'opportunities': opportunities,
        'company_profile': company_profile
    }
    return render(request, 'posts/company_dashboard.html', context)


@company_required
def create_opportunity(request):
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
        benefits = request.POST.get('benefits', '')
        status = request.POST.get('status', TrainingOpportunity.Status.ACTIVE)

        errors = []
        # Translated Messages
        if not major_ids: errors.append("يجب اختيار تخصص واحد على الأقل.")
        if not city_id: errors.append("المدينة مطلوبة.")
        if not start_date_str: errors.append("تاريخ البدء مطلوب.")
        if not duration: errors.append("المدة مطلوبة.")
        if not application_deadline_str: errors.append("الموعد النهائي للتقديم مطلوب.")
        if not requirements: errors.append("المتطلبات مطلوبة.")

        city = None
        start_date = None
        application_deadline = None

        try:
            if city_id: city = City.objects.get(pk=city_id)
        except City.DoesNotExist:
             errors.append("المدينة المحددة غير صالحة.")

        try:
            if start_date_str: start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if application_deadline_str: application_deadline = timezone.datetime.strptime(application_deadline_str, '%Y-%m-%d').date()
        except ValueError:
             errors.append("تنسيق التاريخ غير صالح (YYYY-MM-DD).")

        if start_date and application_deadline and application_deadline < start_date:
             errors.append("لا يمكن أن يكون الموعد النهائي للتقديم قبل تاريخ البدء.")

        if errors:
             for error in errors:
                 messages.error(request, error)
        else:
            try:
                opportunity = TrainingOpportunity.objects.create(
                    company=company_profile, city=city, start_date=start_date, duration=duration,
                    application_deadline=application_deadline, requirements=requirements,
                    benefits=benefits, status=status
                )
                opportunity.majors_needed.set(major_ids)
                # Translated Message
                messages.success(request, "تم إنشاء فرصة التدريب بنجاح!")
                return redirect('posts:company_dashboard')
            except Exception as e:
                 # Translated Message
                 messages.error(request, f"حدث خطأ أثناء إنشاء الفرصة: {e}")

    context = {
        'majors': majors, 'cities': cities, 'statuses': TrainingOpportunity.Status.choices,
        'form_data': request.POST if request.method == 'POST' else {}
    }
    return render(request, 'posts/opportunity_form.html', context)


@require_http_methods(["GET", "POST"])
@login_required
def edit_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)

    is_owner = hasattr(request.user, 'company_profile') and opportunity.company == request.user.company_profile
    if not request.user.is_staff and not is_owner:
        # Translated Message
        messages.error(request, "ليس لديك الإذن لتعديل هذه الفرصة.")
        return redirect('posts:opportunity_list')

    majors = Major.objects.filter(status=True)
    cities = City.objects.filter(status=True)

    if request.method == 'POST':
        major_ids = request.POST.getlist('majors_needed')
        city_id = request.POST.get('city')
        start_date_str = request.POST.get('start_date')
        duration = request.POST.get('duration')
        application_deadline_str = request.POST.get('application_deadline')
        requirements = request.POST.get('requirements')
        benefits = request.POST.get('benefits', '')
        status = request.POST.get('status')

        errors = []
        # Translated Messages
        if not major_ids: errors.append("يجب اختيار تخصص واحد على الأقل.")
        if not city_id: errors.append("المدينة مطلوبة.")
        if not start_date_str: errors.append("تاريخ البدء مطلوب.")
        if not duration: errors.append("المدة مطلوبة.")
        if not application_deadline_str: errors.append("الموعد النهائي للتقديم مطلوب.")
        if not requirements: errors.append("المتطلبات مطلوبة.")
        if not status or status not in [choice[0] for choice in TrainingOpportunity.Status.choices]:
            errors.append("الحالة المحددة غير صالحة.")

        city = None
        start_date = None
        application_deadline = None

        try:
            if city_id: city = City.objects.get(pk=city_id)
        except City.DoesNotExist:
            errors.append("المدينة المحددة غير صالحة.")

        try:
            if start_date_str: start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if application_deadline_str: application_deadline = timezone.datetime.strptime(application_deadline_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append("تنسيق التاريخ غير صالح (YYYY-MM-DD).")

        if start_date and application_deadline and application_deadline < start_date:
             errors.append("لا يمكن أن يكون الموعد النهائي للتقديم قبل تاريخ البدء.")

        if errors:
             for error in errors:
                 messages.error(request, error)
             form_data = request.POST.copy()
             context = {
                 'opportunity': opportunity, 'majors': majors, 'cities': cities,
                 'statuses': TrainingOpportunity.Status.choices, 'form_data': form_data, 'is_edit': True
             }
             return render(request, 'posts/opportunity_form.html', context)
        else:
            try:
                opportunity.city = city
                opportunity.start_date = start_date
                opportunity.duration = duration
                opportunity.application_deadline = application_deadline
                opportunity.requirements = requirements
                opportunity.benefits = benefits
                opportunity.status = status
                opportunity.majors_needed.set(major_ids)
                opportunity.save()
                # Translated Message
                messages.success(request, "تم تحديث فرصة التدريب بنجاح!")
                if request.user.is_staff and not is_owner:
                    return redirect('posts:opportunity_detail', opportunity_id=opportunity.id)
                else:
                    return redirect('posts:company_dashboard')
            except Exception as e:
                 # Translated Message
                 messages.error(request, f"حدث خطأ أثناء تحديث الفرصة: {e}")
                 context = {
                     'opportunity': opportunity, 'majors': majors, 'cities': cities,
                     'statuses': TrainingOpportunity.Status.choices, 'form_data': request.POST, 'is_edit': True
                 }
                 return render(request, 'posts/opportunity_form.html', context)
    else: # GET Request
        form_data = {
            'majors_needed': list(opportunity.majors_needed.values_list('id', flat=True)),
            'city': opportunity.city.id if opportunity.city else '',
            'start_date': opportunity.start_date.strftime('%Y-%m-%d') if opportunity.start_date else '',
            'duration': opportunity.duration,
            'application_deadline': opportunity.application_deadline.strftime('%Y-%m-%d') if opportunity.application_deadline else '',
            'requirements': opportunity.requirements, 'benefits': opportunity.benefits, 'status': opportunity.status,
        }
        context = {
            'opportunity': opportunity, 'majors': majors, 'cities': cities,
            'statuses': TrainingOpportunity.Status.choices, 'form_data': form_data, 'is_edit': True
        }
        return render(request, 'posts/opportunity_form.html', context)


@require_POST
@login_required
def delete_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)

    is_owner = hasattr(request.user, 'company_profile') and opportunity.company == request.user.company_profile
    if not request.user.is_staff and not is_owner:
        # Translated Message
        messages.error(request, "لا تملك الصلاحية لحذف هذه الفرصة.")
        return redirect(request.META.get('HTTP_REFERER', reverse('posts:opportunity_list')))

    try:
        opportunity_name = str(opportunity)
        opportunity.delete()
        # Translated Message
        messages.success(request, f"تم حذف الفرصة '{opportunity_name}' بنجاح.")
    except Exception as e:
        # Translated Message
        messages.error(request, f"حدث خطأ أثناء حذف الفرصة: {e}")
        return redirect(request.META.get('HTTP_REFERER', reverse('posts:opportunity_detail', args=[opportunity_id])))

    if request.user.is_staff and not is_owner:
         return redirect('posts:opportunity_list')
    else:
        return redirect('posts:company_dashboard')



@login_required
def opportunity_applications(request, opportunity_id):
    """ Company or Admin views applications for a specific opportunity. """
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)

    # --- Authorization Check (THIS IS CORRECT) ---
    is_owner = hasattr(request.user, 'company_profile') and opportunity.company == request.user.company_profile
    if not request.user.is_staff and not is_owner:
        messages.error(request, "ليس لديك الإذن لعرض المتقدمين على هذه الفرصة.")
        # Consider redirecting instead of raising PermissionDenied if you want a friendlier message flow
        # return redirect('main:home_view') # Or company dashboard
        raise PermissionDenied("ليس لديك الإذن لعرض المتقدمين على هذه الفرصة.")
    # --- End Authorization Check ---

    applications_qs = Application.objects.filter(
        opportunity=opportunity
    ).select_related(
        'student__user',
        'student__personal_info', # For Name
        'student__contact_info'   # For Phone
        ).order_by('status', '-applied_at')

    context = {
        'opportunity': opportunity,
        'applications': applications_qs,
        'statuses': Application.ApplicationStatus.choices
    }
    return render(request, 'posts/opportunity_applications.html', context)


@require_POST
@login_required
def update_application_status(request, application_id):
    """ Company or Admin updates the status of an application. """
    application = get_object_or_404(Application.objects.select_related('opportunity', 'student'), pk=application_id)
    opportunity = application.opportunity

    is_owner = hasattr(request.user, 'company_profile') and opportunity.company == request.user.company_profile
    if not request.user.is_staff and not is_owner:
        # Translated Message
        messages.error(request, "لا تملك الصلاحية للتحديث على حالة التقديم.")
        return redirect('posts:opportunity_applications', opportunity_id=opportunity.id)

    new_status = request.POST.get('status')
    current_status = application.status

    if new_status in Application.ApplicationStatus.values:
        if application.status == Application.ApplicationStatus.WITHDRAWN and request.user == application.student.user:
             # Translated Message
             messages.error(request, "لا يمكن تحديث الحالة من 'مسحوب' هنا.")
        else:
            application.status = new_status
            # --- Placeholder: Mark as unseen by student ---
            # if new_status != current_status:
            #      application.student_has_seen_latest_status = False # Requires model field
            # --- End Placeholder ---
            application.save()
            # Translated Message
            messages.success(request, f"تم تحديث حالة الطلب إلى '{application.get_status_display()}'.")
            # TODO: Notify student
    else:
        # Translated Message
        messages.error(request, "تم اختيار حالة غير صالحة.")

    return redirect('posts:opportunity_applications', opportunity_id=opportunity.id)


# --- Chat View ---
@login_required
@login_required
def application_chat(request, application_id):
    """ Displays chat, marks messages read, handles sending messages.
        Alert filtering is now handled in base.html.
    """
    # REMOVED the message filtering block from here

    application = get_object_or_404(
        Application.objects.select_related("student__user", "opportunity__company__user"),
        pk=application_id,
    )

    # Permission Check
    is_student = hasattr(request.user, 'student_profile') and request.user == application.student.user
    is_company = hasattr(request.user, 'company_profile') and request.user == application.opportunity.company.user
    is_admin = request.user.is_staff

    if not (is_student or is_company or is_admin):
        messages.error(request,"لا تملك الصلاحية للوصول الى هذه المحادثة.")
        raise PermissionDenied("لا تملك الصلاحية للوصول الى هذه المحادثة.")

    # Fetch actual chat messages from the database for display
    messages_qs = Message.objects.filter(application=application).select_related("sender").order_by("sent_at")

    # Mark messages in the database as read by the current user
    if is_student or is_company:
        recipient_filter = Q(application=application, is_read=False) & ~Q(sender=request.user)
        Message.objects.filter(recipient_filter).update(is_read=True)

    # Handle sending a new message (POST request part)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Message.objects.create(
                application=application, sender=request.user, content=content
            )
            # OPTIONAL: Add a success message if desired
            # messages.success(request, "تم إرسال رسالتك بنجاح!")
            return redirect("posts:application_chat", application_id=application_id)
        else:
            messages.warning(request, "لا يمكن إرسال رسالة فارغة!")
            return redirect("posts:application_chat", application_id=application_id)

    # Prepare context for rendering the template (GET request part)
    context = {
        "application": application,
        "messages": messages_qs, # Pass the actual chat messages
        "is_student_view": is_student,
        "is_company_view": is_company,
        # No need to pass 'alert_messages' separately anymore
    }
    return render(request, "posts/application_chat.html", context)

@login_required
def export_opportunity_applications_excel(request, opportunity_id):
    """
    Exports the list of applicants for a specific opportunity to an Excel file.
    Only accessible by the company that owns the opportunity or staff.
    """
    opportunity = get_object_or_404(TrainingOpportunity, pk=opportunity_id)
    user = request.user

    # --- Authorization Check (Same as opportunity_applications view) ---
    is_owner = hasattr(user, 'company_profile') and opportunity.company == user.company_profile
    if not user.is_staff and not is_owner:
        messages.error(request, "ليس لديك الصلاحية لتصدير قائمة المتقدمين لهذه الفرصة.")
        # Redirect or raise permission denied
        return redirect('posts:opportunity_applications', opportunity_id=opportunity_id)
    # --- End Authorization Check ---

    applications = Application.objects.filter(
        opportunity=opportunity
    ).select_related(
        'student__user',
        'student__personal_info',
        'student__contact_info'
    ).order_by('status', '-applied_at')

    # Create Excel Workbook and Sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = f"Applications_{opportunity.id}"
    sheet.sheet_view.rightToLeft = True # Set sheet direction to RTL

    # Define Headers
    headers = [
        "اسم المتقدم", "البريد الإلكتروني", "رقم الهاتف",
        "تاريخ التقديم", "الحالة", "رسالة التقديم"
    ]
    sheet.append(headers)

    # Style Header Row (Optional)
    header_font = Font(bold=True)
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.font = header_font

    # Populate Data
    for app in applications:
        # Safely get related data
        student_name = getattr(app.student.personal_info, 'full_name', None) or \
                       app.student.user.get_full_name() or \
                       app.student.user.username
        email = getattr(app.student.user, 'email', 'N/A')
        phone = getattr(getattr(app.student, 'contact_info', None), 'phone', 'N/A')
        applied_date = app.applied_at.strftime('%Y-%m-%d %H:%M') if app.applied_at else 'N/A'
        status = app.get_status_display()
        message = getattr(app, 'message', '')

        sheet.append([
            student_name, email, phone,
            applied_date, status, message
        ])

    # Adjust Column Widths (Optional)
    for col_num in range(1, sheet.max_column + 1):
         column_letter = get_column_letter(col_num)
         # Simple auto-fit simulation (adjust max length as needed)
         max_length = 0
         column = list(sheet.columns)[col_num-1] # Get column object
         for cell in column:
             try:
                 if len(str(cell.value)) > max_length:
                     max_length = len(str(cell.value))
             except:
                 pass
         adjusted_width = (max_length + 2) * 1.2 # Add padding and factor
         sheet.column_dimensions[column_letter].width = adjusted_width


    # Create HTTP Response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    safe_company_name = "".join(c if c.isalnum() else "_" for c in opportunity.company.company_name)
    filename = f'applicants_{safe_company_name}_{opportunity_id}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Save workbook to response
    workbook.save(response)

    return response
