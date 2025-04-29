from django.urls import path
from . import views

app_name='accounts'
urlpatterns=[
    path('Login/',views.login_view,name='login_view'),
    path('signup/',views.signup_view,name='signup_view'),
    path('logout',views.logout_view,name='logout'),
    path('signup/company/',views.signup_company_view,name='signup_company_view'),
    path('users/',views.user_list,name='user_list'),
        path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/delete_all/', views.delete_all, name='delete_all'),





]