from django.shortcuts import render
from django.http import HttpRequest
# Create your views here.
def home_view(request:HttpRequest):
    return render(request,'main/home.html')

def training_view(request:HttpRequest):
    return render(request,'main/training.html')

def about_view(request:HttpRequest):
    return render(request,'main/about.html')

def contact_view(request:HttpRequest):
    return render(request,'main/contact.html')

