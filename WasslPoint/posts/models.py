from django.db import models
from profiles.models import CompanyProfile, StudentProfile, City, Major
from django.conf import settings


class TrainingOpportunity(models.Model):
    """
    Represents a Co-op training opportunity posted by a company.
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "فعال"
        EXPIRED = "EXPIRED", "منتهي الصلاحية"
        DRAFT = "DRAFT", "مسودة"
        CLOSED = "CLOSED", "مغلق"

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(max_length=200, default="Co-op Opportunity")
    city = models.ForeignKey(City, on_delete=models.CASCADE, default=1)
    majors_needed = models.ManyToManyField(Major, related_name='opportunities')
    description = models.TextField(default="Details of this opportunity will be added soon.")
    requirements = models.TextField()
    benefits = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    duration = models.CharField(
        max_length=50, help_text="e.g., '3 months', '6 weeks'"
    )
    application_deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    def __str__(self):
        # Simplified string representation
        return f"{self.company.company_name} - Opportunity"

    class Meta:
        ordering = ['-created_at']


class Application(models.Model):
    class ApplicationStatus(models.TextChoices):
        PENDING = 'PENDING', 'تحت المراجعة'
        ACCEPTED = 'ACCEPTED', 'مقبول'
        REJECTED = 'REJECTED', 'مرفوض'
        WITHDRAWN = 'WITHDRAWN', 'تم الانسحاب' # Added status

    opportunity = models.ForeignKey(TrainingOpportunity, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True, help_text="Optional message to the company") # Added help_text

    class Meta:
        unique_together = ('opportunity', 'student') # Ensures student applies only once
        ordering = ['-applied_at']

    def __str__(self):
        return f"Application by {self.student.user.username} for {self.opportunity}"


class Message(models.Model):
    """
    Represents a message in the communication between a student and a company
    regarding a specific application.
    """

    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )  # Could be a student or a company user
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} on {self.application}"
