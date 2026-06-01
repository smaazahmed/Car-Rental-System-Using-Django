from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from apps.bookings.models import Booking, Payment
from apps.cars.models import Car

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Update user profile with role, phone, and address
            profile = user.profile
            profile.role = form.cleaned_data.get('role', 'customer')
            profile.phone_number = form.cleaned_data.get('phone_number')
            profile.address = form.cleaned_data.get('address')
            profile.save()

            messages.success(request, f"Account created successfully for {user.username}! You are now logged in.")
            login(request, user)
            return redirect('dashboard_redirect')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')

@login_required
def customer_dashboard(request):
    user = request.user
    bookings = Booking.objects.filter(user=user).select_related('car')
    active_rentals = bookings.filter(status='Approved', return_date__gte=datetime.date.today())
    favorites = user.profile.favorites.all()
    
    # Calculate simple stats
    total_spent = Payment.objects.filter(booking__user=user, status='Paid').aggregate(total=Sum('amount'))['total'] or 0.00
    
    return render(request, 'accounts/dashboard.html', {
        'bookings': bookings,
        'active_rentals': active_rentals,
        'favorites': favorites,
        'total_spent': total_spent
    })

import datetime
from django.db.models import Sum

@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })

@login_required
def toggle_favorite(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    profile = request.user.profile
    if profile.favorites.filter(id=car.id).exists():
        profile.favorites.remove(car)
        is_favorite = False
        message = f"Removed {car.name} from your wishlist."
    else:
        profile.favorites.add(car)
        is_favorite = True
        message = f"Added {car.name} to your wishlist."
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })
        
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'home'))
