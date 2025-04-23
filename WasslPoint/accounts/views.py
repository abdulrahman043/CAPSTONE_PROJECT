from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.db import transaction
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from profiles.models import CompanyProfile,StudentProfile,PersonalInformation,Experience,Education,Skill,Language,Certification,ContactInformation
# Create your views here.

def signup_view(request:HttpRequest):
    if request.method=='POST':
        with transaction.atomic():
            try:
                user = User.objects.create_user(username=request.POST["email"], password=request.POST["password"])
                user.save()
                profile=StudentProfile.objects.create(user=user)
                PersonalInformation.objects.create(profile=profile,full_name_ar=request.POST['full_name'])
                Education.objects.create(profile=profile)
                Experience.objects.create(profile=profile)
                Skill.objects.create(profile=profile)
                Language.objects.create(profile=profile)
                Certification.objects.create(profile=profile)
                ContactInformation.objects.create(profile=profile)

                




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