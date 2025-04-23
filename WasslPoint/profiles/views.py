from django.shortcuts import render
from django.http import HttpRequest
# Create your views here.
def profile_view(request:HttpRequest):
    return render(request,'profiles/profile.html')