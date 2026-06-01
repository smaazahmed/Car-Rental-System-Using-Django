from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('api/revenue/', views.admin_revenue_api, name='admin_revenue_api'),
]
