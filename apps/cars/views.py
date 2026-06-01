from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from .models import Car, CarImage, Review
from .forms import CarForm, ReviewForm

def car_list(request):
    query = request.GET.get('q', '')
    brand = request.GET.get('brand', '')
    transmission = request.GET.get('transmission', '')
    fuel = request.GET.get('fuel', '')
    seats = request.GET.get('seats', '')
    max_price = request.GET.get('max_price', '')
    is_available = request.GET.get('is_available', '')
    sort_by = request.GET.get('sort_by', 'latest')

    cars = Car.objects.all()

    # Search filter
    if query:
        cars = cars.filter(Q(name__icontains=query) | Q(brand__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))

    # Dropdown filters
    if brand:
        cars = cars.filter(brand__iexact=brand)
    if transmission:
        cars = cars.filter(transmission_type__iexact=transmission)
    if fuel:
        cars = cars.filter(fuel_type__iexact=fuel)
    if seats:
        cars = cars.filter(seating_capacity=seats)
    if max_price:
        cars = cars.filter(rent_price_per_day__lte=max_price)
    if is_available == 'true':
        cars = cars.filter(is_available=True)

    # Sorting
    if sort_by == 'price_low':
        cars = cars.order_by('rent_price_per_day')
    elif sort_by == 'price_high':
        cars = cars.order_by('-rent_price_per_day')
    elif sort_by == 'rating':
        # Simple sorting by model average rating is tricky because it's a property. 
        # For simplicity, we order by average reviews rating using DB aggregation
        from django.db.models import Avg
        cars = cars.annotate(avg_rate=Avg('reviews__rating')).order_by('-avg_rate')
    else: # Latest added
        cars = cars.order_by('-created_at')

    # Get distinct brands and categories for filter UI
    brands = Car.objects.values_list('brand', flat=True).distinct()
    
    # Recently viewed cars (using session)
    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed_cars = Car.objects.filter(id__in=recently_viewed_ids) if recently_viewed_ids else []

    context = {
        'cars': cars,
        'brands': brands,
        'recently_viewed_cars': recently_viewed_cars,
        'selected_filters': {
            'q': query,
            'brand': brand,
            'transmission': transmission,
            'fuel': fuel,
            'seats': seats,
            'max_price': max_price,
            'is_available': is_available,
            'sort_by': sort_by,
        }
    }

    # Render a partial for AJAX live filtering or full page
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'cars/car_list_partial.html', context)
    return render(request, 'cars/list.html', context)

def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    reviews = car.reviews.select_related('user').all()
    similar_cars = Car.objects.filter(brand=car.brand).exclude(id=car.id)[:3]
    if not similar_cars.exists():
        similar_cars = Car.objects.exclude(id=car.id)[:3]

    # Session tracking for recently viewed
    recently_viewed = request.session.get('recently_viewed', [])
    if car.id in recently_viewed:
        recently_viewed.remove(car.id)
    recently_viewed.insert(0, car.id)
    request.session['recently_viewed'] = recently_viewed[:4] # Keep top 4 recently viewed

    # User review check
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(car=car, user=request.user).first()

    review_form = ReviewForm()

    return render(request, 'cars/detail.html', {
        'car': car,
        'reviews': reviews,
        'similar_cars': similar_cars,
        'user_review': user_review,
        'review_form': review_form
    })

def search_suggestions(request):
    term = request.GET.get('term', '')
    suggestions = []
    if term:
        cars = Car.objects.filter(Q(name__icontains=term) | Q(brand__icontains=term))[:5]
        for car in cars:
            suggestions.append({
                'label': f"{car.brand} {car.name}",
                'id': car.id
            })
    return JsonResponse(suggestions, safe=False)

@login_required
def add_review(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        # Check if already reviewed
        if Review.objects.filter(user=request.user, car=car).exists():
            messages.error(request, "You have already reviewed this car. You can edit your existing review.")
            return redirect('car_detail', car_id=car.id)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.car = car
            review.save()
            messages.success(request, "Your review has been posted!")
        else:
            messages.error(request, "Failed to submit review. Check your inputs.")
    return redirect('car_detail', car_id=car.id)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user and not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        return HttpResponseForbidden("You are not allowed to delete this review.")
    
    car_id = review.car.id
    review.delete()
    messages.success(request, "Your review has been successfully removed.")
    return redirect('car_detail', car_id=car_id)

# Admin car management views
@login_required
def admin_add_car(request):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save()
            # Handle multiple images
            images = request.FILES.getlist('images')
            for index, img in enumerate(images):
                CarImage.objects.create(car=car, image=img, is_primary=(index == 0))
            messages.success(request, f"Successfully added {car.brand} {car.name}!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Failed to add vehicle. Please correct errors.")
    else:
        form = CarForm()
    return render(request, 'cars/admin_car_form.html', {'form': form, 'title': 'Add New Car'})

@login_required
def admin_edit_car(request, car_id):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            
            # Handle additional multiple images if uploaded
            images = request.FILES.getlist('images')
            for img in images:
                # If there are no images yet, set as primary
                is_primary = not car.images.exists()
                CarImage.objects.create(car=car, image=img, is_primary=is_primary)

            messages.success(request, f"Successfully updated {car.brand} {car.name}!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Failed to update vehicle. Please correct errors.")
    else:
        form = CarForm(instance=car)
    return render(request, 'cars/admin_car_form.html', {'form': form, 'car': car, 'title': f'Edit {car.name}'})

@login_required
def admin_delete_car(request, car_id):
    if not (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    car = get_object_or_404(Car, id=car_id)
    car.delete()
    messages.success(request, f"Successfully deleted vehicle.")
    return redirect('admin_dashboard')
