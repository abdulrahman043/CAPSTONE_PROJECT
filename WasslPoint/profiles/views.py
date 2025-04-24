from django.shortcuts import render
from django.http import HttpRequest
from .models import PersonalInformation,Country
# Create your views here.
def profile_view(request:HttpRequest):
    countries = Country.objects.filter(status=True)  # only active ones

    context = {
    "gender_choices": PersonalInformation.Gender.choices,
    'countries':countries,
}
    return render(request,'profiles/profile.html',context)