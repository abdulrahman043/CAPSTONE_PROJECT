from django.urls import path
from . import views
app_name = "profiles"
urlpatterns = [path('profile/',views.profile_view,name='profile_view'),
               path('delate/<exp_id>',views.delate_exp,name='delate_exp'),
               ]
