# استيراد مكتبات Django للتعريف بالنماذج
from django.db import models
from django.contrib.auth.models import User
# استيراد مكتبة Babel لجلب أسماء اللغات
from babel import Locale
# استيراد لحساب العمر من تاريخ الميلاد
from datetime import date

# تهيئة اللغة العربية في Babel
locale_ar = Locale('ar')
# بناء قائمة اختيارات للغات تحتوي على رمز اللغة واسمها بالعربي
LANGUAGE_CHOICES = [
    (code, name)
    for code, name in locale_ar.languages.items()
]


class City(models.Model):
    # نموذج يمثل مدينة باسم عربي وإنجليزي وحالة التفعيل
    arabic_name = models.CharField(max_length=100)  # الاسم بالعربية
    english_name = models.CharField(max_length=100) # الاسم بالإنجليزية
    status = models.BooleanField(default=True)      # علم لحالة التفعيل


class Industry(models.Model):
    # نموذج يمثل قطاعاً للصناعة مع حالة تفعيل
    name = models.CharField(max_length=100)   # اسم القطاع
    status = models.BooleanField(default=True) # علم التفعيل


class CompanyAddress(models.Model):
    # نموذج عنوان الشركة يتضمن سطرين ورمز بريدي ومدينة
    address_line1 = models.TextField(max_length=255)     # السطر الأول للعنوان
    address_line2 = models.TextField(max_length=255, blank=True)  # السطر الثاني (اختياري)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True) # ربط بنموذج المدينة
    postal_code = models.CharField(max_length=20)        # الرمز البريدي


class ContactPerson(models.Model):
    # نموذج لمنسق التواصل الخاص بالشركة
    company_address = models.OneToOneField(CompanyAddress, models.CASCADE)
    person_name = models.CharField(max_length=100)       # اسم الشخص
    email = models.EmailField()                          # البريد الإلكتروني
    phone = models.CharField(max_length=20)              # رقم الهاتف


class StudentProfile(models.Model):
    # ملف الطالب المرتبط بنموذج المستخدم
    user = models.OneToOneField(User, models.CASCADE, related_name='student_profile')

    @property
    def completion_percent(self):
        """
        يحسب نسبة اكتمال الملف الشخصي بناءً على 6 أقسام
        ويعيد القيمة مؤشرًا مئويًا (0-100)
        """
        total = 6
        done = 0

        # القسم: المعلومات الشخصية
        pi = getattr(self, 'personal_info', None)
        if pi and pi.full_name and pi.date_of_birth and pi.gender and pi.nationality:
            done += 1

        # القسم: معلومات الاتصال
        ci = getattr(self, 'contact_info', None)
        if ci and ci.email and ci.phone and ci.address_line and ci.city:
            done += 1

        # القسم: الخبرة العملية
        if self.experience.exists():
            done += 1

        # القسم: المؤهلات التعليمية
        if self.education.exists():
            done += 1

        # القسم: المهارات
        if self.skill.exists():
            done += 1

        # القسم: اللغات
        if self.language.exists():
            done += 1

        return int(done / total * 100)

    @property
    def missing_sections(self):
        """
        يعيد قائمة بأسماء الأقسام الناقصة لإظهارها للمستخدم
        """
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
    # نموذج الدول مع أسماء بالعربي والإنجليزي وكود الهاتف
    arabic_name = models.CharField(max_length=200)
    english_name = models.CharField(max_length=200)
    phone_code = models.CharField(max_length=200)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.arabic_name  # لعرض الاسم العربي كنص للنموذج


class PersonalInformation(models.Model):
    # نموذج معلومات الطالب الشخصية
    class Gender(models.TextChoices):
        MALE = 'MALE', 'ذكر'
        FEMALE = 'FEMALE', 'أنثى'

    profile = models.OneToOneField(
        StudentProfile,
        models.CASCADE,
        related_name='personal_info'
    )
    full_name = models.CharField(max_length=100)  # الاسم الكامل
    date_of_birth = models.DateField(blank=True, null=True)  # تاريخ الميلاد
    gender = models.CharField(
        max_length=6,
        choices=Gender.choices,
        blank=True,
        null=True
    )  # الجنس
    nationality = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True
    )  # الجنسية
    picture = models.ImageField(
        upload_to='profiles/profiles_images/',
        blank=True,
        null=True,
        default='profiles/profiles_images/default.png'
    )  # صورة شخصية

    @property
    def age(self):
        """
        يحسب العمر بالسنوات بناءً على تاريخ الميلاد
        """
        dob = self.date_of_birth
        if not dob:
            return None
        today = date.today()
        years = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            years -= 1
        return years


class Experience(models.Model):
    # نموذج الخبرة العملية
    profile = models.ForeignKey(
        StudentProfile,
        models.CASCADE,
        related_name='experience'
    )
    job_title = models.CharField(max_length=100)    # المسمى الوظيفي
    company_name = models.CharField(max_length=100) # اسم الشركة
    start_date = models.DateField(null=True)        # تاريخ البدء
    end_date = models.DateField(null=True, blank=True) # تاريخ الانتهاء
    description = models.CharField(blank=True, max_length=100) # وصف مختصر


class Major(models.Model):
    # تخصص دراسي
    ar_name = models.CharField(max_length=100)  # الاسم بالعربية
    en_name = models.CharField(max_length=100)  # الاسم بالإنجليزية
    status = models.BooleanField(default=True)  # حالة التفعيل


class Education(models.Model):
    # نموذج المؤهل التعليمي مع الاختيارات
    class Degree(models.TextChoices):
        HIGH_SCHOOL = 'HIGH_SCHOOL', 'الثانوية العامة أو ما يعادلها'
        DIPLOMA     = 'DIPLOMA',     'دبلوم'
        BACHELOR    = 'BACHELOR',    'بكالوريوس'
        POST_DIPLOMA= 'POST_DIPLOMA','دبلوم عالي'
        MASTER      = 'MASTER',      'ماجستير'
        DOCTORATE   = 'DOCTORATE',   'دكتوراه'

    class GPA_SCALE(models.TextChoices):
        FOUR_POINT    = '4',  '4.0'
        FIVE_POINT    = '5',  '5.0'
        HUNDRED_POINT = '100','100.0'

    profile = models.ForeignKey(
        StudentProfile,
        models.CASCADE,
        related_name='education'
    )
    university       = models.CharField(max_length=200)      # اسم الجامعة
    degree           = models.CharField(max_length=100, choices=Degree.choices) # الدرجة العلمية
    major            = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True) # التخصص
    graduating_date  = models.DateField(null=True)          # تاريخ التخرج
    gpa_scale        = models.PositiveSmallIntegerField(choices=GPA_SCALE.choices, null=True) # المقياس
    GPA              = models.DecimalField(max_digits=5, decimal_places=2, null=True)        # المعدل


class Skill(models.Model):
    # نموذج المهارة مع مستوى الإتقان
    class Proficiency(models.TextChoices):
        BEGINNER     = 'BEGINNER',     'مبتدئ'
        INTERMEDIATE = 'INTERMEDIATE', 'متوسط'
        ADVANCED     = 'ADVANCED',     'متقدم'

    profile     = models.ForeignKey(StudentProfile, models.CASCADE, related_name='skill')
    name        = models.CharField(max_length=100)  # اسم المهارة
    proficiency = models.CharField(max_length=20, choices=Proficiency.choices) # مستوى الإتقان


class Language(models.Model):
    # نموذج اللغات التي يتقنها المستخدم
    class Proficiency(models.TextChoices):
        BEGINNER     = 'BEGINNER',     'مبتدئ'
        INTERMEDIATE = 'INTERMEDIATE', 'متوسط'
        ADVANCED     = 'ADVANCED',     'متقدم'
        NATIVE       = 'NATIVE',       'اللغة الأم'

    profile     = models.ForeignKey(StudentProfile, models.CASCADE, related_name='language')
    name        = models.CharField(max_length=100, choices=LANGUAGE_CHOICES) # اختيار اللغة من القائمة
    proficiency = models.CharField(max_length=20, choices=Proficiency.choices) # مستوى الإتقان


class Certification(models.Model):
    # نموذج الشهادات مع ملف الشهادة
    profile           = models.ForeignKey(StudentProfile, models.CASCADE, related_name='certification')
    name              = models.CharField(max_length=200)  # اسم الشهادة
    issuer            = models.CharField(max_length=100)  # الجهة المانحة
    issue_date        = models.DateField(null=True)      # تاريخ الإصدار
    expiry_date       = models.DateField(null=True, blank=True) # تاريخ الانتهاء
    certificate_file  = models.FileField(upload_to='certs/')    # ملف الشهادة


class CompanyProfile(models.Model):
    # ملف الشركة المرتبط بالمستخدم
    user                          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name                  = models.TextField(max_length=200) # اسم الشركة
    commercial_CRM_Certificate     = models.FileField(upload_to='crm_certs/') # شهادة CRM
    commercial_register            = models.CharField(max_length=200)       # رقم السجل التجاري
    industry                       = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True) # الصناعة
    company_address                = models.ForeignKey(CompanyAddress, on_delete=models.SET_NULL, null=True) # العنوان
    is_active                      = models.BooleanField(default=False)      # حالة التفعيل


class ContactInformation(models.Model):
    # نموذج معلومات الاتصال الخاصة بالطالب
    profile      = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='contact_info')
    email        = models.EmailField(null=True, default='')  # البريد الإلكتروني
    phone        = models.CharField(max_length=20, null=True, default='') # رقم الهاتف
    address_line = models.TextField(null=True, default='')   # عنوان السكن
    city         = models.ForeignKey(City, on_delete=models.CASCADE, null=True) # ربط بالمدينة
