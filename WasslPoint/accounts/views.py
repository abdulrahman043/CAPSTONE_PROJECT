from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpRequest
from django.db import transaction
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from profiles.models import CompanyProfile,StudentProfile,PersonalInformation,Experience,Education,Skill,Language,Certification,ContactInformation
from django.contrib.admin.views.decorators import staff_member_required 
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

def signup_view(request:HttpRequest):
    if request.method=='POST':
        with transaction.atomic():
            try:
                user = User.objects.create_user(username=request.POST["email"], password=request.POST["password"])
                user.save()
                profile=StudentProfile.objects.create(user=user)
                PersonalInformation.objects.create(profile=profile,full_name=request.POST['full_name'])
                ContactInformation.objects.create(profile=profile,email=request.POST["email"])
                return redirect('accounts:login_view')
            except Exception as e:
                print(e)
    return render(request,'accounts/signup.html')


def signup_company_view(request:HttpRequest):
    if request.method=='POST':
        print(request.POST)
        with transaction.atomic():
            try:
                user = User.objects.create_user(username=request.POST["email"], password=request.POST["password"])
                user.save()
                CompanyProfile.objects.create(user=user,commercial_register=request.POST['commercial_register'])
                return redirect('accounts:login_view')
            except Exception as e:
                print(e)

    return render(request,'accounts/signup_company.html')
def login_view(request:HttpRequest):
    if request.method=='POST':
        user=authenticate(request,username=request.POST["email"],password=request.POST['password'])
        if user is not None:
            login(request,user)
            return redirect('main:home_view')
    return render(request,'accounts/login.html')
def logout_view(request:HttpRequest):
    logout(request)

    return redirect('main:home_view')

@login_required
@staff_member_required
def user_list(request: HttpRequest):
    user_qs=User.objects.all()
    paginator=Paginator(user_qs,5)
    page=request.GET.get('page')
    user_page=paginator.get_page(page)
    context={"user_page":user_page}

    return render(request, 'accounts/user_list.html',context)
def user_delete(request, user_id):
    user=User.objects.get(pk=user_id)
    if user.is_superuser or user.is_staff:
        pass
    elif request.user!=user:
        user.delete()
    
    return redirect('accounts:user_list')
@login_required
@staff_member_required
@require_POST
def delete_all(request:HttpRequest):
    try:
        if request.method=='POST':
            ids=request.POST.getlist('selected_users')
            if ids:
                User.objects.filter(id__in=ids,is_staff=False, is_superuser=False).exclude(id=request.user.id).delete()
    except:
        pass
    return redirect('accounts:user_list')