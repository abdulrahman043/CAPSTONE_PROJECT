from django.db import models
from django.contrib.auth.models import User
# Create your models here.
GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]
class City(models.Model):
    name=models.CharField(max_length=100)
    status=models.BooleanField(default=True)
class Industry(models.Model):
    name=models.CharField(max_length=100)
    status=models.BooleanField(default=True)
class CompanyAddress(models.Model):
    address_line1=models.TextField(max_length=255)
    address_line2=models.TextField(max_length=255 ,blank=True)
    city=models.ForeignKey(City,on_delete=models.SET_NULL,null=True)
    postal_code= models.CharField(max_length=20)
class ContactPerson(models.Model):
    company_address=models.OneToOneField(CompanyAddress,models.CASCADE)
    person_name=models.CharField(max_length=100)
    email=models.EmailField()
    phone=models.CharField(max_length=20)

class StudentProfile(models.Model):
    user=models.OneToOneField(User,models.CASCADE,related_name='student_profile')
class Country(models.Model):
    name=models.CharField(max_length=200)
    status=models.BooleanField()
class PersonalInformation(models.Model):
    profile=models.OneToOneField(StudentProfile,models.CASCADE,related_name='personal_info')
    full_name_ar=models.CharField(max_length=100)
    full_name_en=models.CharField(max_length=100,blank=True)
    date_of_birth=models.DateField(blank=True,null=True)
    gender=models.CharField(max_length=1,choices=GENDER_CHOICES,blank=True)
    nationality=models.ForeignKey(Country,on_delete=models.SET_NULL,null=True)
    picture=models.ImageField(default='profiles/' ,blank=True)
class Experience(models.Model):
    profile=models.ForeignKey(StudentProfile,models.CASCADE)
    job_title=models.CharField(max_length=100)
    company_name=models.CharField(max_length=100)
    start_date=models.DateField()
    end_date=models.DateField(null=True,blank=True)
    description=models.CharField(blank=True,max_length=100)

class Major(models.Model):
    name=models.CharField(max_length=100)
    status=models.BooleanField(default=True)
class Education(models.Model):
    profile=models.ForeignKey(StudentProfile,models.CASCADE)
    university  =models.CharField(max_length=200)
    degree=models.CharField(max_length=100)
    major=models.ForeignKey(Major,on_delete=models.SET_NULL,null=True)
    graduating_date= models.DateField()
    GPA=models.DecimalField(max_digits=4,decimal_places=2)
class Skill(models.Model):
    profile=models.ForeignKey(StudentProfile,models.CASCADE)
    name=models.CharField(max_length=100)
    proficiency=models.CharField(max_length=20)
class Language(models.Model):
    profile=models.ForeignKey(StudentProfile,models.CASCADE)
    name=models.CharField(max_length=100)
    proficiency=models.CharField(max_length=20)
class Certification(models.Model):
    profile=models.ForeignKey(StudentProfile,models.CASCADE)
    name=models.CharField(max_length=200)
    issuer=models.CharField(max_length=100)
    issue_date= models.DateField()
    expiry_date= models.DateField(null=True,blank=True)
    certificate_file= models.FileField(upload_to='certs/')


class CompanyProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    company_name = models.TextField(max_length=200)
    commercial_CRM_Certificate = models.FileField(upload_to='crm_certs/')
    commercial_register = models.CharField(max_length=200)
    industry = models.ForeignKey(Industry,on_delete=models.SET_NULL,null=True)
    CompanyAddress = models.ForeignKey(CompanyAddress,on_delete=models.SET_NULL,null=True)
class ContactInformation(models.Model):
    profile=models.OneToOneField(StudentProfile,on_delete=models.CASCADE)
    email=models.EmailField(null=True)
    phone=models.CharField(null=True,max_length=20)
    address_line=models.TextField(null=True)
    City=models.ForeignKey(City,on_delete=models.CASCADE,null=True)