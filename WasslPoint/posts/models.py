from django.db import models
from profiles.models import CompanyProfile, StudentProfile, City, Major
from django.conf import settings


class TrainingOpportunity(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "فعال"
        EXPIRED = "EXPIRED", "منتهي الصلاحية"
        DRAFT = "DRAFT", "مسودة"
        CLOSED = "CLOSED", "مغلق"

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(max_length=200, default="New Co-op Training Vacancy")
    city = models.ForeignKey(City, on_delete=models.CASCADE, default=1)
    majors_needed = models.ManyToManyField(Major, related_name='opportunities')
    description = models.TextField(default="Details of this opportunity will be added soon.")
    requirements = models.TextField()
    benefits = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    duration = models.CharField(max_length=50, help_text="e.g., '3 months', '6 weeks'")
    application_deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self):
        return f"{self.company.company_name} - Opportunity"

    class Meta:
        ordering = ['-created_at']


class Application(models.Model):
    class ApplicationStatus(models.TextChoices):
        PENDING = 'PENDING', 'تحت المراجعة'
        ACCEPTED = 'ACCEPTED', 'مقبول'
        REJECTED = 'REJECTED', 'مرفوض'
        WITHDRAWN = 'WITHDRAWN', 'تم الانسحاب'

    opportunity = models.ForeignKey(TrainingOpportunity, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True, help_text="Optional message to the company")

    class Meta:
        unique_together = ('opportunity', 'student')
        ordering = ['-applied_at']

    def __str__(self):
        return f"Application by {self.student.user.username} for {self.opportunity}"


class Message(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f'Message from {self.sender.username} on {self.application.id} at {self.sent_at}'