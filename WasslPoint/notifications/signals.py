# notifications/signals.py

from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth.models import User

from profiles.models import CompanyProfile
from profiles.models import CompanyProfileEditRequest
from notifications.models import Notification
from django.core.mail import send_mail
from django.conf import settings
from posts.models import Message,TrainingOpportunity,Application
@receiver(post_save, sender=CompanyProfile)
def notify_staff_new_company(sender, instance, created, **kwargs):
    """
    When a new CompanyProfile is created (i.e. registration request),
    notify all staff users.
    """
    # only on create, and only if the user isn't active yet
    if not created or instance.user.is_active:
        return

    url = reverse('accounts:pending_company_requests_view')
    message = f"طلب تسجيل شركة جديد: {instance.company_name}"

    for staff in User.objects.filter(is_staff=True, is_active=True):
        Notification.objects.create(
            user    = staff,
            message = message,
            url     = url
        )


@receiver(post_save, sender=CompanyProfileEditRequest)
def notify_staff_edit_request(sender, instance, created, **kwargs):
    """
    When a company submits an edit request, notify all staff users.
    """
    # only on create, and only if it's still pending
    if not created or instance.status != CompanyProfileEditRequest.STATUS_PENDING:
        return

    url = reverse('accounts:company_edit_request_list')
    message = f"طلب تعديل معلومات شركة: {instance.company.company_name}"

    for staff in User.objects.filter(is_staff=True, is_active=True):
        Notification.objects.create(
            user    = staff,
            message = message,
            url     = url
        )
@receiver(post_save, sender=Application)
def notify_company_on_new_application(sender, instance, created, **kwargs):
    """
    Notify the company when a student applies to an opportunity.
    """
    if not created:
        return
    company_user = instance.opportunity.company.user
    url = reverse('posts:opportunity_applications', args=[instance.opportunity.id])
    message = (
        f"قام الطالب {instance.student.user.get_full_name() or instance.student.user.username} "
        f"بالتقديم على الفرصة \"{instance.opportunity.title}\""
    )
    Notification.objects.create(user=company_user, message=message, url=url)

@receiver(pre_save, sender=Application)
def track_application_status_change(sender, instance, **kwargs):
    """
    Store the old status before saving to detect changes.
    """
    if not instance.pk:
        return
    previous = sender.objects.get(pk=instance.pk)
    instance._old_status = previous.status

@receiver(post_save, sender=Application)
def notify_student_on_status_change(sender, instance, created, **kwargs):
   
    if created:
        return
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status
    if old_status and old_status != new_status:
        old_status = Application.ApplicationStatus(old_status).label
        new_status = Application.ApplicationStatus(new_status).label
       
        student_user = instance.student.user
        url = reverse('posts:my_applications')
        message = (
            f"  تم تحديث حالة طلبكم للفرصة التدريبية, "
            f"من {old_status} إلى {new_status}"
        )
        # Create notification
        Notification.objects.create(user=student_user, message=message, url=url)
        # Send email
        email = "wasslpoint@gmail.com"

        subject = "تحديث حالة طلب التدريب التعاوني"
        name = student_user.get_full_name() or student_user.student_profile.personal_info.full_name

        body = (
        f"مرحبًا {name}\n\n"
        f"{message}\n\n"
        "يمكنك مراجعة الطلب من خلال الموقع\n\n"
        "للاستفسار يرجى التواصل مع الدعم عبر البريد الإلكتروني\n"
        f"{email}\n\n"
        "شكرًا لاستخدامك منصتنا"
    )
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [student_user.email], fail_silently=True)

@receiver(post_save, sender=Message)
def notify_on_message(sender, instance, created, **kwargs):
    
    if not created:
        return
    app = instance.application
    recipient = None
    if instance.sender == app.student.user:
        recipient = app.opportunity.company.user
    else:
        recipient = app.student.user
    url = reverse('posts:application_chat', args=[app.id])
    message = (
        f"رسالة جديدة من {instance.sender.get_full_name() or instance.sender.username} "
        f"بخصوص طلب التدريب"
    )
    Notification.objects.create(user=recipient, message=message, url=url)
   