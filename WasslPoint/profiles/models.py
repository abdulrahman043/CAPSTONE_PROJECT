from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from babel import Locale
from datetime import date

locale_ar = Locale('ar')
LANGUAGE_CHOICES = [
    (code, name)
    for code, name in locale_ar.languages.items()
]
class City(models.Model):
    arabic_name=models.CharField(max_length=100)
    english_name=models.CharField(max_length=100)
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
    @property
    def completion_percent(self):
        total = 6
        done = 0
        pi = getattr(self, 'personal_info', None)
        if pi and pi.full_name and pi.date_of_birth and pi.gender and pi.nationality:
            done += 1
        ci = getattr(self, 'contact_info', None)
        if ci and ci.email and ci.phone and ci.address_line and ci.city:
            done += 1
        if self.experience.exists():
            done += 1
        if self.education.exists():
            done += 1
        if self.skill.exists():
            done += 1
        if self.language.exists():
            done += 1
        return int(done / total * 100)
    @property
    def missing_sections(self):
        missing = []

        pi = getattr(self, 'personal_info', None)
        if not (pi and pi.full_name and pi.date_of_birth and pi.gender and pi.nationality):
            missing.append("المعلومات الشخصية")

        ci = getattr(self, 'contact_info', None)
        if not (ci and ci.email and ci.phone and ci.address_line and ci.city):
            missing.append("معلومات الاتصال")

        if not self.experience.exists():
            missing.append("إضافة خبرة واحدة على الأقل")

        if not self.education.exists():
            missing.append("إضافة مؤهل تعليمي واحد على الأقل")

        if not self.skill.exists():
            missing.append("إضافة مهارة واحدة على الأقل")

        if not self.language.exists():
            missing.append("إضافة لغة واحدة على الأقل")

        return missing
class Country(models.Model):
    arabic_name=models.CharField(max_length=200)
    english_name=models.CharField(max_length=200)
    phone_code=models.CharField(max_length=200)

    status=models.BooleanField(default=True)
    def __str__(self):
        return super().__str__()
class PersonalInformation(models.Model):
    class Gender(models.TextChoices):
        MALE   = 'MALE',   'ذكر'
        FEMALE = 'FEMALE', 'أنثى'

    profile=models.OneToOneField(StudentProfile,models.CASCADE,related_name='personal_info')
    full_name=models.CharField(max_length=100)
    date_of_birth=models.DateField(blank=True,null=True)
    gender=models.CharField(max_length=6,choices=Gender.choices,blank=True,null=True)
    nationality=models.ForeignKey(Country,on_delete=models.SET_NULL,null=True)
    picture=models.ImageField(upload_to='profiles/profiles_images/' ,blank=True,null=True,default='profiles/profiles_images/default.png')
    @property
    def age(self):
        dob = self.date_of_birth
        if not dob:
            return None
        today = date.today()
        years = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            years -= 1
        return years
class Experience(models.Model):
    profile=models.ForeignKey(StudentProfile,models.CASCADE,related_name='experience')
    job_title=models.CharField(max_length=100)
    company_name=models.CharField(max_length=100)
    start_date=models.DateField(null=True)
    end_date=models.DateField(null=True,blank=True)
    description=models.CharField(blank=True,max_length=100)

class Major(models.Model):
    ar_name=models.CharField(max_length=100)
    en_name=models.CharField(max_length=100)
    status=models.BooleanField(default=True)

    

    status=models.BooleanField(default=True)
class Education(models.Model):
    class Degree(models.TextChoices):
        HIGH_SCHOOL   = 'HIGH_SCHOOL',   'الثانوية العامة أو ما يعادلها'
        DIPLOMA       = 'DIPLOMA',       'دبلوم'
        BACHELOR      = 'BACHELOR',      'بكالوريوس'
        POST_DIPLOMA  = 'POST_DIPLOMA',  'دبلوم عالي'
        MASTER        = 'MASTER',        'ماجستير'
        DOCTORATE     = 'DOCTORATE',     'دكتوراه'

    class GPA_SCALE(models.TextChoices):
        FOUR_POINT    = '4',   '4.0'
        FIVE_POINT    = '5',   '5.0'
        HUNDRED_POINT = '100', '100.0'

    profile=models.ForeignKey(StudentProfile,models.CASCADE,related_name='education')
    university  =models.CharField(max_length=200)
    degree=models.CharField(max_length=100,choices=Degree.choices)
    major=models.ForeignKey(Major,on_delete=models.SET_NULL,null=True)
    graduating_date= models.DateField(null=True)
    gpa_scale = models.PositiveSmallIntegerField(choices=GPA_SCALE.choices,null=True)
    GPA=models.DecimalField(max_digits=5,decimal_places=2,null=True)
class Skill(models.Model):
    class Proficiency(models.TextChoices):
        BEGINNER     = 'BEGINNER',     'مبتدئ'
        INTERMEDIATE = 'INTERMEDIATE', 'متوسط'
        ADVANCED     = 'ADVANCED',     'متقدم'
    profile=models.ForeignKey(StudentProfile,models.CASCADE,related_name='skill')
    name=models.CharField(max_length=100)
    proficiency=models.CharField(max_length=20,choices=Proficiency.choices)
class Language(models.Model):
    class Proficiency(models.TextChoices):
        BEGINNER     = 'BEGINNER',     'مبتدئ'
        INTERMEDIATE = 'INTERMEDIATE', 'متوسط'
        ADVANCED     = 'ADVANCED',     'متقدم'
        NATIVE       = 'NATIVE',       'اللغة الأم'

    profile=models.ForeignKey(StudentProfile,models.CASCADE,related_name='language')
    name=models.CharField(max_length=100,choices=LANGUAGE_CHOICES)
    proficiency=models.CharField(max_length=20,choices=Proficiency.choices)
class Certification(models.Model):
    profile=models.ForeignKey(StudentProfile,models.CASCADE,related_name='certification')
    name=models.CharField(max_length=200)
    issuer=models.CharField(max_length=100)
    issue_date= models.DateField(null=True)
    expiry_date= models.DateField(null=True,blank=True)
    certificate_file= models.FileField(upload_to='certs/')


class CompanyProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='company_profile')
    company_name = models.TextField(max_length=200)
    commercial_CRM_Certificate = models.FileField(upload_to='crm_certs/')
    commercial_register = models.CharField(max_length=200)
    industry = models.ForeignKey(Industry,on_delete=models.SET_NULL,null=True)
    company_address = models.ForeignKey(CompanyAddress,on_delete=models.SET_NULL,null=True)
    is_active=models.BooleanField(default=False)
class ContactInformation(models.Model):
    profile=models.OneToOneField(StudentProfile,on_delete=models.CASCADE,related_name='contact_info')
    email=models.EmailField(null=True,default='')
    phone=models.CharField(null=True,max_length=20,default='')
    address_line=models.TextField(null=True,default='')
    city=models.ForeignKey(City,on_delete=models.CASCADE,null=True)
