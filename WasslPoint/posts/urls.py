from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [

    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('company/', views.company_opportunities, name='company_opportunities'), # Changed URL
    path('company/opportunities/create/', views.create_opportunity, name='create_opportunity'),
    path('opportunities/<int:opportunity_id>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunities/<int:opportunity_id>/apply/', views.apply_opportunity, name='apply_opportunity'),
    path('applications/', views.application_status, name='application_status'),
    path('company/opportunities/<int:opportunity_id>/applications/', views.opportunity_applications, name='opportunity_applications'),
    path('company/applications/<int:application_id>/update_status/', views.update_application_status, name='update_application_status'),
    path('applications/<int:application_id>/chat/', views.application_chat, name='application_chat'),
]