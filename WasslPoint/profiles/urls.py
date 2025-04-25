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
                 path('delate_edu/<edu_id>',views.delate_edu,name='delate_edu'),
               path('edit_edu/<edu_id>',views.edit_edu,name='edit_edu'),
                    path('delate_cert/<cert_id>',views.delate_cert,name='delate_cert'),
               path('edit_cert/<cert_id>',views.edit_cert,name='edit_cert'),
                 path('add_cert/',views.add_cert,name='add_cert'),
                                  path('add_exp/',views.add_exp,name='add_exp'),
                                      path('add_skill/',views.add_skill,name='add_skill'),
                                        path('add_edu/',views.add_edu,name='add_edu'),
                                                path('add_language/',views.add_language,name='add_language'),



               ]
