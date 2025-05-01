from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.opportunity_list, name='opportunity_list'),
    path('company/opportunities/', views.company_opportunities, name='company_opportunities'),
    path('opportunity/create/', views.create_opportunity, name='create_opportunity'),
    path('opportunity/<int:opportunity_id>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunity/<int:opportunity_id>/apply/', views.apply_opportunity, name='apply_opportunity'),
    path('applications/', views.application_status, name='application_status'),
    path('opportunity/<int:opportunity_id>/applications/', views.opportunity_applications, name='opportunity_applications'),
    path('application/<int:application_id>/status/update/', views.update_application_status, name='update_application_status'),
    path('application/<int:application_id>/chat/', views.application_chat, name='application_chat'),
]
