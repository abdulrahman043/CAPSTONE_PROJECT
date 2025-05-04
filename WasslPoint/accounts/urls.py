from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name='accounts'
urlpatterns=[
    path('Login/',views.login_view,name='login_view'),
    path('signup/',views.signup_view,name='signup_view'),
    path('logout/',views.logout_view,name='logout'),
    path('detail_signup/company/',views.signup_company_detail_view,name='signup_company_detail_view'),
    path('users/',views.user_list_view,name='user_list_view'),
    path('company/users/',views.company_user_list_view,name='company_user_list_view'),
    path('student/users/',views.student_user_list_view,name='student_user_list_view'),
    path('applications/users/',views.applications_list_view,name='applications_list_view'),
    path('opportunity/users/',views.opportunity_list_view,name='opportunity_list_view'),

    path('pending/company/requests/',views.pending_company_requests_view,name='pending_company_requests_view'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/approve_company/', views.approve_company, name='approve_company'),
    path('signup/verify-otp/', views.verify_signup_otp, name='verify_signup_otp'),
    path('verify-otp/resend/', views.resend_signup_otp, name='resend_signup_otp'),

    path('users/delete_all/', views.delete_all, name='delete_all'),
    path('applications/delete_all/', views.app_delete_all, name='app_delete_all'),
    path('opportunity/delete_all/', views.opp_delete_all, name='opp_delete_all'),
    path('company/signup/email/',   views.signup_company_email, name='signup_company_email'),

]