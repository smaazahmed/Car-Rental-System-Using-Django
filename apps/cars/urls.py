from django.urls import path
from . import views

urlpatterns = [
    path('explore/', views.car_list, name='car_list'),
    path('explore/<int:car_id>/', views.car_detail, name='car_detail'),
    path('suggestions/', views.search_suggestions, name='search_suggestions'),
    path('explore/<int:car_id>/review/add/', views.add_review, name='add_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    
    # Admin actions
    path('admin/car/add/', views.admin_add_car, name='admin_add_car'),
    path('admin/car/edit/<int:car_id>/', views.admin_edit_car, name='admin_edit_car'),
    path('admin/car/delete/<int:car_id>/', views.admin_delete_car, name='admin_delete_car'),
]
