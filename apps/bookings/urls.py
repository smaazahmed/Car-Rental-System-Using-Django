from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:car_id>/', views.init_booking, name='init_booking'),
    path('checkout/<int:car_id>/confirm/', views.confirm_booking, name='confirm_booking'),
    path('receipt/<int:booking_id>/', views.booking_receipt, name='booking_receipt'),
    path('admin/action/<int:booking_id>/<str:action>/', views.admin_booking_action, name='admin_booking_action'),
    path('api/calendar/<int:car_id>/', views.api_car_availability_calendar, name='api_car_availability_calendar'),
]
