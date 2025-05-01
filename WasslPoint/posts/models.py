from django.db import models
from profiles.models import Major, City, CompanyProfile, StudentProfile
from django.utils import timezone
from django.contrib.auth.models import User


#مودل فرص التدريب
class TrainingOpportunity(models.Model):
    #حالات فرص التدريب
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        CLOSED = 'CLOSED', 'Closed'
        CANCELED = 'CANCELED', 'Canceled'

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='training_opportunities')
    majors_needed = models.ManyToManyField(Major, related_name='training_opportunities')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField()
    duration = models.CharField(max_length=50, help_text="e.g., 3 months, 1 semester")
    application_deadline = models.DateField()
    requirements = models.TextField()
    benefits = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.company_name} - {', '.join(major.ar_name for major in self.majors_needed.all())} - {self.city.arabic_name}"


#مودل التقديمات
class Application(models.Model):
    #حالات التقديم
    class ApplicationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn'

    opportunity = models.ForeignKey(TrainingOpportunity, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True)

    class Meta:
        unique_together = ('opportunity', 'student')

    def __str__(self):
        return f"Application by {self.student.user.username} for {self.opportunity}"


#مودل الرسائل مع الجهة المقدمة لفرصة التدريب
class Message(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCA