from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from apps.cars.models import Car
from .models import Booking, Payment
import datetime
import uuid

def check_availability(car, pickup_date, return_date):
    """
    Checks if a car is available between pickup_date and return_date.
    Overlapping logic: there is an overlap if:
    (db_pickup_date <= return_date) AND (db_return_date >= pickup_date)
    and the booking is not Cancelled.
    """
    overlapping_bookings = Booking.objects.filter(
        car=car,
        pickup_date__lte=return_date,
        return_date__gte=pickup_date
    ).exclude(status='Cancelled')
    
    return not overlapping_bookings.exists()

@login_required
def init_booking(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if not car.is_available:
        messages.error(request, "This vehicle is currently unavailable for rent.")
        return redirect('car_detail', car_id=car.id)

    pickup_date_str = request.GET.get('pickup_date')
    return_date_str = request.GET.get('return_date')

    pickup_date = None
    return_date = None
    days = 1
    total_price = car.rent_price_per_day

    if pickup_date_str and return_date_str:
        try:
            pickup_date = datetime.datetime.strptime(pickup_date_str, "%Y-%m-%d").date()
            return_date = datetime.datetime.strptime(return_date_str, "%Y-%m-%d").date()
            
            if pickup_date < datetime.date.today():
                messages.error(request, "Pickup date cannot be in the past.")
                return redirect('car_detail', car_id=car.id)
            if return_date < pickup_date:
                messages.error(request, "Return date must be after pickup date.")
                return redirect('car_detail', car_id=car.id)

            delta = return_date - pickup_date
            days = max(delta.days, 1)
            total_price = car.rent_price_per_day * days
            
            # Double booking check
            if not check_availability(car, pickup_date, return_date):
                messages.error(request, f"Sorry, this car is already booked between {pickup_date} and {return_date}.")
                return redirect('car_detail', car_id=car.id)

        except ValueError:
            pass

    # Render checkout page
    return render(request, 'bookings/checkout.html', {
        'car': car,
        'pickup_date': pickup_date,
        'return_date': return_date,
        'days': days,
        'total_price': total_price,
        'service_fee': round(float(total_price) * 0.05, 2), # 5% service fee
        'grand_total': round(float(total_price) * 1.05, 2),
    })

@login_required
def confirm_booking(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        pickup_date_str = request.POST.get('pickup_date')
        return_date_str = request.POST.get('return_date')
        
        try:
            pickup_date = datetime.datetime.strptime(pickup_date_str, "%Y-%m-%d").date()
            return_date = datetime.datetime.strptime(return_date_str, "%Y-%m-%d").date()
            
            # Re-validate
            if pickup_date < datetime.date.today() or return_date < pickup_date:
                messages.error(request, "Invalid rental dates.")
                return redirect('car_detail', car_id=car.id)
                
            if not check_availability(car, pickup_date, return_date):
                messages.error(request, "The vehicle is already booked for these dates.")
                return redirect('car_detail', car_id=car.id)
                
            delta = return_date - pickup_date
            days = max(delta.days, 1)
            base_price = car.rent_price_per_day * days
            grand_total = base_price * 1.05 # Include 5% fee

            # Create Booking
            booking = Booking.objects.create(
                user=request.user,
                car=car,
                pickup_date=pickup_date,
                return_date=return_date,
                total_price=grand_total,
                status='Approved' # Auto-approve upon payment success for mock
            )

            # Create payment record
            transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            Payment.objects.create(
                booking=booking,
                transaction_id=transaction_id,
                amount=grand_total,
                status='Paid',
                payment_method='Credit Card (Mock Gateway)'
            )

            # Send Email alert logs in console
            print("\n" + "="*50)
            print(f"EMAIL NOTIFICATION SENT TO: {request.user.email}")
            print(f"SUBJECT: Booking Confirmation - Rental #{booking.id}")
            print(f"Hello {request.user.first_name or request.user.username},\n")
            print(f"Your reservation for the {car.brand} {car.name} is CONFIRMED!")
            print(f"Pickup Date: {pickup_date}")
            print(f"Return Date: {return_date}")
            print(f"Total Amount Paid: ${grand_total}")
            print(f"Transaction Reference: {transaction_id}")
            print("Thank you for choosing DriveLux Rent A Car!")
            print("="*50 + "\n")

            messages.success(request, f"Congratulations! Your booking for {car.name} is confirmed and payment processed successfully.")
            return redirect('booking_receipt', booking_id=booking.id)

        except Exception as e:
            messages.error(request, f"Checkout failed: {str(e)}")
            return redirect('car_detail', car_id=car.id)

    return redirect('car_detail', car_id=car.id)

@login_required
def booking_receipt(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.user != request.user and not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        return HttpResponseForbidden("Access Denied.")
        
    payment = getattr(booking, 'payment', None)
    
    # Calculate receipt variables
    base_price = booking.car.rent_price_per_day * booking.duration_days
    service_fee = float(base_price) * 0.05

    return render(request, 'bookings/receipt.html', {
        'booking': booking,
        'payment': payment,
        'base_price': base_price,
        'service_fee': service_fee,
        'tax': 0.00
    })

@login_required
def admin_booking_action(request, booking_id, action):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, "Unauthorized.")
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id)
    if action == 'approve':
        booking.status = 'Approved'
        messages.success(request, f"Booking #{booking.id} Approved.")
    elif action == 'complete':
        booking.status = 'Completed'
        messages.success(request, f"Booking #{booking.id} marked as Completed.")
    elif action == 'cancel':
        booking.status = 'Cancelled'
        
        # Mark payment refunded if paid
        if hasattr(booking, 'payment'):
            booking.payment.status = 'Refunded'
            booking.payment.save()
            
        # Send cancellation email log in console
        print("\n" + "="*50)
        print(f"EMAIL NOTIFICATION SENT TO: {booking.user.email}")
        print(f"SUBJECT: Booking Cancellation - Rental #{booking.id}")
        print(f"Hello {booking.user.username},\n")
        print(f"Your reservation for the {booking.car.brand} {booking.car.name} has been CANCELLED.")
        print(f"Refund of ${booking.total_price} has been initiated to your original payment method.")
        print("We apologize for the inconvenience.")
        print("="*50 + "\n")

        messages.success(request, f"Booking #{booking.id} Cancelled. Payment Refunded.")
    
    booking.save()
    return redirect('admin_dashboard')

@login_required
def api_car_availability_calendar(request, car_id):
    """
    Returns dates for which the car is booked so that frontend can disable them on calendar
    """
    car = get_object_or_404(Car, id=car_id)
    bookings = Booking.objects.filter(car=car).exclude(status='Cancelled')
    
    disabled_ranges = []
    for b in bookings:
        # Loop from pickup to return and append string dates
        curr = b.pickup_date
        while curr <= b.return_date:
            disabled_ranges.append(curr.strftime("%Y-%m-%d"))
            curr += datetime.timedelta(days=1)
            
    return JsonResponse({'booked_dates': disabled_ranges})
