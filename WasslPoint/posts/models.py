from django.db import models
from profiles.models import CompanyProfile,Major,StudentProfile
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]
# Create your models here.
class CoopPosting(models.Model):
    company=models.ForeignKey(CompanyProfile,on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    coop_requirements= models.TextField()
    posting_date= models.DateField()
    expiration_date= models.DateField()
    start_date= models.DateField()
    major=models.ManyToManyField(Major)
    description= models.TextField()
    
    
    
class Application(models.Model):
    student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE)
    coop_posting=models.ForeignKey(CoopPosting,on_delete=models.CASCADE)
    application_date= models.DateField(auto_now_add=True)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    cover_letter=models.FileField(upload_to='applications/')