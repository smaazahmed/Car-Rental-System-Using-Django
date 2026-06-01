from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from apps.cars.models import Car, Review
from apps.bookings.models import Booking, Payment
import datetime

def home(request):
    featured_cars = Car.objects.filter(is_available=True)[:6]
    # Unique brands for search dropdown & brands showcase
    brands = Car.objects.values_list('brand', flat=True).distinct()
    # Simple hardcoded testimonials to wow the user
    testimonials = [
        {
            'name': 'Sophia Martinez',
            'role': 'Business Consultant',
            'comment': 'Outstanding experience! The Tesla Model S was in immaculate condition, and the contactless key delivery was absolute magic. Highly recommended.',
            'stars': 5,
            'avatar': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces'
        },
        {
            'name': 'Marcus Vance',
            'role': 'Tech Entrepreneur',
            'comment': 'I rented a Range Rover for a family road trip. The booking was seamless, customer support was available 24/7, and the vehicle drove like a dream.',
            'stars': 5,
            'avatar': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=faces'
        },
        {
            'name': 'Elena Rostova',
            'role': 'Travel Photographer',
            'comment': 'Affordable prices, clean cars, and amazing customer service. Will definitely be renting again from Antigravity Rentals!',
            'stars': 5,
            'avatar': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=faces'
        }
    ]
    return render(request, 'core/home.html', {
        'featured_cars': featured_cars,
        'brands': brands,
        'testimonials': testimonials
    })

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        # Simulate saving or sending message
        messages.success(request, f"Thank you, {name}! Your message has been received. We will get back to you shortly.")
        return redirect('contact')
    return render(request, 'core/contact.html')

@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
        return redirect('admin_dashboard')
    return redirect('customer_dashboard')

@login_required
def admin_dashboard(request):
    # Verify user is admin
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, "Access denied. Admins only.")
        return redirect('home')

    # Aggregations
    total_users = User.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Payment.objects.filter(status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0.00
    total_cars = Car.objects.count()

    recent_bookings = Booking.objects.select_related('user', 'car').order_index = Booking.objects.all()[:8]
    most_rented_cars = Car.objects.annotate(booking_count=Count('bookings')).order_by('-booking_count')[:5]

    all_bookings = Booking.objects.select_related('user', 'car').all()
    all_users = User.objects.select_related('profile').all()
    all_cars = Car.objects.all()

    return render(request, 'core/admin_dashboard.html', {
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'total_cars': total_cars,
        'recent_bookings': recent_bookings,
        'most_rented_cars': most_rented_cars,
        'all_bookings': all_bookings,
        'all_users': all_users,
        'all_cars': all_cars
    })

@login_required
def admin_revenue_api(request):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Aggregate revenues by month for the last 6 months
    today = datetime.date.today()
    months_data = []
    labels = []

    for i in range(5, -1, -1):
        # Calculate start and end of target month
        year = today.year
        month = today.month - i
        if month <= 0:
            month += 12
            year -= 1
        
        month_name = datetime.date(year, month, 1).strftime('%B')
        labels.append(month_name)

        # Aggregate paid amount
        monthly_rev = Payment.objects.filter(
            status='Paid',
            created_at__year=year,
            created_at__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0.00
        
        months_data.append(float(monthly_rev))

    return JsonResponse({
        'labels': labels,
        'data': months_data
    })
