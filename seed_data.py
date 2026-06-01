import os
import django
import datetime

# Configure Django settings environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.cars.models import Car, Review
from apps.bookings.models import Booking, Payment

def seed():
    print("Starting database seeding...")

    # 1. Create Admin Account
    admin_user, created = User.objects.get_or_create(
        username='admin',
        email='admin@driveluxrentals.com',
        first_name='Alex',
        last_name='Staff'
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        
    profile = admin_user.profile
    profile.role = 'admin'
    profile.phone_number = '+1 (800) 555-0100'
    profile.address = '700 Fifth Avenue, Suite 40, New York, NY'
    profile.save()
    print("-> Admin account created: admin / admin123")

    # 2. Create Customer Account
    customer_user, created = User.objects.get_or_create(
        username='customer',
        email='customer@gmail.com',
        first_name='John',
        last_name='Doe'
    )
    if created:
        customer_user.set_password('customer123')
        customer_user.save()
        
    c_profile = customer_user.profile
    c_profile.role = 'customer'
    c_profile.phone_number = '+1 (555) 0199-231'
    c_profile.address = '123 Ocean Drive, Miami, FL'
    c_profile.save()
    print("-> Customer account created: customer / customer123")

    # 3. Create Cars
    cars_data = [
        {
            'name': 'Model S Plaid',
            'brand': 'Tesla',
            'model_year': 2024,
            'color': 'Solid Black',
            'transmission_type': 'Automatic',
            'fuel_type': 'Electric',
            'seating_capacity': 5,
            'rent_price_per_day': 150.00,
            'is_available': True,
            'description': 'The Model S Plaid has the quickest acceleration of any vehicle in production. Updated suspension, carbon-sleeved rotors, and a gorgeous glass panoramic roof make this a thrill to drive.',
            'location': 'Los Angeles, CA',
            'mileage': 8500,
            'registration_number': 'CA-99X-Z12'
        },
        {
            'name': '911 GT3 RS',
            'brand': 'Porsche',
            'model_year': 2024,
            'color': 'Guards Red',
            'transmission_type': 'Automatic',
            'fuel_type': 'Petrol',
            'seating_capacity': 2,
            'rent_price_per_day': 350.00,
            'is_available': True,
            'description': 'Pure motorsport technology in a road-legal package. A naturally aspirated 4.0-liter flat-six engine delivering 518 horsepower, an active rear wing, and state-of-the-art aerodynamic downforce controls.',
            'location': 'Miami, FL',
            'mileage': 3200,
            'registration_number': 'FL-77Y-P45'
        },
        {
            'name': 'Autobiography Edition',
            'brand': 'Range Rover',
            'model_year': 2023,
            'color': 'Belgravia Green',
            'transmission_type': 'Automatic',
            'fuel_type': 'Diesel',
            'seating_capacity': 7,
            'rent_price_per_day': 200.00,
            'is_available': True,
            'description': 'The pinnacle of luxury SUV travel. Executive class rear seats, hot stone massage configurations, dynamic air suspension, and an active noise cancellation cabin for ultimate road quietness.',
            'location': 'New York, NY',
            'mileage': 15600,
            'registration_number': 'NY-12A-B34'
        },
        {
            'name': 'M4 Competition',
            'brand': 'BMW',
            'model_year': 2024,
            'color': 'Sao Paulo Yellow',
            'transmission_type': 'Manual',
            'fuel_type': 'Petrol',
            'seating_capacity': 4,
            'rent_price_per_day': 180.00,
            'is_available': True,
            'description': 'Twin-turbo inline-six engine churning out 503 horsepower. Outfitted with carbon fiber bucket seats, aggressive styling cues, and a manual gearbox for pure driving enthusiasts.',
            'location': 'Los Angeles, CA',
            'mileage': 4100,
            'registration_number': 'CA-44R-T88'
        },
        {
            'name': 'Shelby GT500',
            'brand': 'Ford',
            'model_year': 2023,
            'color': 'Rapid Red Metallic',
            'transmission_type': 'Automatic',
            'fuel_type': 'Petrol',
            'seating_capacity': 4,
            'rent_price_per_day': 160.00,
            'is_available': True,
            'description': 'A supercharged 5.2-liter V8 engine pushing out a monstrous 760 horsepower. True American muscle featuring MagneRide damping, Brembo high-performance brakes, and a roaring active exhaust system.',
            'location': 'Chicago, IL',
            'mileage': 6500,
            'registration_number': 'IL-88U-M99'
        },
        {
            'name': 'S-Class S580',
            'brand': 'Mercedes-Benz',
            'model_year': 2024,
            'color': 'Selenite Grey Metallic',
            'transmission_type': 'Automatic',
            'fuel_type': 'Hybrid',
            'seating_capacity': 5,
            'rent_price_per_day': 220.00,
            'is_available': True,
            'description': 'The gold standard of executive luxury. Advanced driver assistance systems, full-cabin ambient lighting, Burmester 4D surround sound system, and a silky-smooth twin-turbo V8 hybrid engine.',
            'location': 'New York, NY',
            'mileage': 9800,
            'registration_number': 'NY-55S-W10'
        }
    ]

    seeded_cars = []
    for c in cars_data:
        car, created = Car.objects.get_or_create(
            registration_number=c['registration_number'],
            defaults=c
        )
        seeded_cars.append(car)
        if created:
            print(f"-> Car added: {car.brand} {car.name}")

    # 4. Create Reviews
    reviews_data = [
        {'user': customer_user, 'car': seeded_cars[0], 'rating': 5, 'comment': 'Unbelievable acceleration. The Tesla Model S Plaid is an absolute spaceship! Extremely clean delivery.'},
        {'user': customer_user, 'car': seeded_cars[1], 'rating': 5, 'comment': 'The GT3 RS is the ultimate track weapon for the street. Mindblowing downforce and cornering.'},
        {'user': customer_user, 'car': seeded_cars[2], 'rating': 4, 'comment': 'Very comfortable ride, perfect for our family weekend trip in upstate New York. Highly spacious.'}
    ]

    for r in reviews_data:
        review, created = Review.objects.get_or_create(
            user=r['user'],
            car=r['car'],
            defaults={'rating': r['rating'], 'comment': r['comment']}
        )
        if created:
            print(f"-> Review seeded for {review.car.name}")

    # 5. Seed historical monthly bookings/payments to populate the Admin Chart.js graph
    print("Seeding monthly billing histories for Chart.js analytics...")
    today = datetime.date.today()
    
    # Let's seed a booking for each of the last 5 months
    for i in range(5, 0, -1):
        year = today.year
        month = today.month - i
        if month <= 0:
            month += 12
            year -= 1

        booking_date = datetime.date(year, month, 10)
        return_date = datetime.date(year, month, 15)
        
        # Calculate simulated total price (e.g. 5 days of Range Rover Autobiography)
        fare = 200.00 * 5 * 1.05 # Include 5% service fee
        
        # Create booking log
        b = Booking.objects.create(
            user=customer_user,
            car=seeded_cars[2], # Range Rover
            pickup_date=booking_date,
            return_date=return_date,
            total_price=fare,
            status='Completed'
        )
        
        # Overwrite booking created_at time using custom save
        Booking.objects.filter(id=b.id).update(created_at=datetime.datetime(year, month, 10, 12, 0))

        # Create payment log
        p = Payment.objects.create(
            booking=b,
            transaction_id=f"TXN-SEED-{year}{month:02d}",
            amount=fare,
            status='Paid',
            payment_method='Credit Card (Mock Gateway)'
        )
        # Overwrite payment created_at
        Payment.objects.filter(id=p.id).update(created_at=datetime.datetime(year, month, 11, 10, 0))

    print("\nDatabase seeded successfully!")
    print("="*50)
    print("Credentials to test:")
    print("Customer:  customer / customer123")
    print("Admin:     admin / admin123")
    print("="*50)

if __name__ == '__main__':
    seed()
