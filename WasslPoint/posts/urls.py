# WasslPoint/posts/urls.py
from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Public/Student Views
    path('', views.opportunity_list, name='opportunity_list'), # Renamed from 'opportunities/'
    path('<int:opportunity_id>/', views.opportunity_detail, name='opportunity_detail'),
    path('<int:opportunity_id>/apply/', views.apply_opportunity, name='apply_opportunity'),
    path('applications/', views.my_applications_list, name='my_applications'), # Renamed from application_status
    path('applications/<int:application_id>/withdraw/', views.withdraw_application, name='withdraw_application'),
    path('applications/<int:application_id>/chat/', views.application_chat, name='application_chat'),

    # Company Views
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'), # New dashboard
    path('company/create/', views.create_opportunity, name='create_opportunity'),
    path('company/<int:opportunity_id>/edit/', views.edit_opportunity, name='edit_opportunity'),
    path('company/<int:opportunity_id>/delete/', views.delete_opportunity, name='delete_opportunity'),
    path('company/<int:opportunity_id>/applications/', views.opportunity_applications, name='opportunity_applications'),
    path('company/applications/<int:application_id>/update_status/', views.update_application_status, name='update_application_status'),
    path('opportunity/<int:opportunity_id>/applications/', views.opportunity_applications, name='opportunity_applications'),
    path('opportunity/<int:opportunity_id>/applications/export/excel/', views.export_opportunity_applications_excel, name='export_applications_excel'),
    path('application/<int:application_id>/status/<str:status>/', views.update_application_status, name='update_application_status'),
]
