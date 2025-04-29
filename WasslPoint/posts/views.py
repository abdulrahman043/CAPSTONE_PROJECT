from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from .models import CoopPosting, Application
from profiles.models import Major

# عرض كل التدريبات لجميع المستخدمين
def training_list_view(request: HttpRequest):
    major_filter = request.GET.get('major')
    trainings = CoopPosting.objects.all()
    majors = Major.objects.all()

    if major_filter:
        trainings = trainings.filter(major__id=major_filter)

    return render(request, "post/training.html", {"trainings": trainings, "majors": majors})

# تفاصيل تدريب واحد
def training_detail_view(request: HttpRequest, training_id: int):
    training = get_object_or_404(CoopPosting, id=training_id)
    return render(request, "post/post_details.html", {"training": training})

# اضافة تدريب
@login_required
def add_training_view(request: HttpRequest):
   
    if not hasattr(request.user, 'company_profile'):
        messages.error(request, "يجب إنشاء ملف شركة أولاً قبل إضافة تدريب.")
        return redirect("main:company_view") 

    if request.method == "POST":
        company = request.user.companyprofile
        new_training = CoopPosting(
            company=company,
            title=request.POST["title"],
            coop_requirements=request.POST["coop_requirements"],
            posting_date=request.POST["posting_date"],
            expiration_date=request.POST["expiration_date"],
            start_date=request.POST["start_date"],
            description=request.POST["description"],
        )
        new_training.save()

        majors_ids = request.POST.getlist("majors")
        new_training.major.set(majors_ids)

        messages.success(request, "تم إضافة التدريب بنجاح ✅")
        return redirect("main:company_view")  # رجوع لصفحة الشركة بعد الاضافة

    majors = Major.objects.all()
    return render(request, "post/add_training.html", {"majors": majors})

# تحديث تدريب
@login_required
def update_training_view(request: HttpRequest, training_id: int):
    training = get_object_or_404(CoopPosting, id=training_id)

    if training.company.user != request.user:
        return HttpResponse("غير مصرح", status=401)

    if request.method == "POST":
        training.title = request.POST["title"]
        training.coop_requirements = request.POST["coop_requirements"]
        training.posting_date = request.POST["posting_date"]
        training.expiration_date = request.POST["expiration_date"]
        training.start_date = request.POST["start_date"]
        training.description = request.POST["description"]
        majors_ids = request.POST.getlist("majors")
        training.major.set(majors_ids)
        training.save()

        messages.success(request, "تم تحديث التدريب بنجاح ✅")
        return redirect("main:company_view")

    majors = Major.objects.all()
    return render(request, "post/post_update.html", {"training": training, "majors": majors})

# حذف تدريب
@login_required
def delete_training_view(request: HttpRequest, training_id: int):
    training = get_object_or_404(CoopPosting, id=training_id)

    if training.company.user != request.user:
        return HttpResponse("غير مصرح", status=401)

    training.delete()
    messages.success(request, "تم حذف التدريب بنجاح 🗑️")
    return redirect("main:company_view")

# عرض تدريبات الشركة الحالية فقط (صفحة company.html)
@login_required
def company_view(request: HttpRequest):
    if not hasattr(request.user, 'company_profile'):
        messages.error(request, "لا يمكنك عرض تدريبات بدون حساب شركة.")
        return redirect("profiles:create_company_profile_view")

    company = request.user.companyprofile
    trainings = CoopPosting.objects.filter(company=company)

    return render(request, "main/company.html", {"trainings": trainings})
