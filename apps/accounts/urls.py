from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('favorites/toggle/<int:car_id>/', views.toggle_favorite, name='toggle_favorite'),
]
