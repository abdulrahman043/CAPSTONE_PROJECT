from django.urls import path
from . import views

app_name = "post" 

urlpatterns = [
    path('training/', views.training_list_view, name="training_list_view"),
    path('training/<int:training_id>/', views.training_detail_view, name="training_detail_view"),
    path('training/add/', views.add_training_view, name="add_training_view"),
    path('training/update/<int:training_id>/', views.update_training_view, name="update_training_view"),
    path('training/delete/<int:training_id>/', views.delete_training_view, name="delete_training_view"),
]
