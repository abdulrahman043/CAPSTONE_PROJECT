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
    path('subscription/users/',views.subscription_view,name='subscription_view'),
    path('major/users/',views.major_view,name='major_view'),
    path('city/users/',views.city_view,name='city_view'),
    path('industry/users/',views.industry_view,name='industry_view'),
    path('subscription/add/',views.add_subscription_view,name='add_subscription_view'),
    path('major/add/',views.add_major_view,name='add_major_view'),
    path('city/add/',views.add_city_view,name='add_city_view'),
    path('industry/add/',views.add_industry_view,name='add_industry_view'),
    path('subscription/edit/<int:id>',views.edit_subscription_view,name='edit_subscription_view'),
    path('major/edit/<int:id>',views.edit_major_view,name='edit_major_view'),
    path('city/edit/<int:id>',views.edit_city_view,name='edit_city_view'),
    path('industry/edit/<int:id>',views.edit_industry_view,name='edit_industry_view'),

    path('pending/company/requests/',views.pending_company_requests_view,name='pending_company_requests_view'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/approve_company/', views.approve_company, name='approve_company'),
    path('signup/verify-otp/', views.verify_signup_otp, name='verify_signup_otp'),
    path('verify-otp/resend/', views.resend_signup_otp, name='resend_signup_otp'),

    path('users/delete_all/', views.delete_all, name='delete_all'),
    path('sub/delete_all/', views.sub_delete_all, name='sub_delete_all'),
    path('major/delete_all/', views.major_delete_all, name='major_delete_all'),
    path('city/delete_all/', views.city_delete_all, name='city_delete_all'),
    path('industry/delete_all/', views.industry_delete_all, name='industry_delete_all'),
    path('applications/delete_all/', views.app_delete_all, name='app_delete_all'),
    path('opportunity/delete_all/', views.opp_delete_all, name='opp_delete_all'),
    path('company/signup/email/',   views.signup_company_email, name='signup_company_email'),

]