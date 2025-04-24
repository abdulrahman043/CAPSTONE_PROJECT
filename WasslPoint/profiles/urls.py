from django.urls import path
from . import views
app_name = "profiles"
urlpatterns = [path('profile/',views.profile_view,name='profile_view'),
               path('delate_exp/<exp_id>',views.delate_exp,name='delate_exp'),
               path('edit_exp/<exp_id>',views.edit_exp,name='edit_exp'),
                path('delate_skill/<skill_id>',views.delate_skill,name='delate_skill'),
               path('edit_skill/<skill_id>',views.edit_skill,name='edit_skill'),
                 path('delate_lan/<lan_id>',views.delate_language,name='delate_language'),
               path('edit_lan/<lan_id>',views.edit_language,name='edit_language'),
               ]
