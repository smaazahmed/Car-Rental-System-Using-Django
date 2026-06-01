from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Car(models.Model):
    TRANSMISSION_CHOICES = (
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual'),
    )
    FUEL_CHOICES = (
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    )

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    model_year = models.IntegerField()
    color = models.CharField(max_length=30)
    transmission_type = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='Automatic')
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='Petrol')
    seating_capacity = models.IntegerField(default=5)
    rent_price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    description = models.TextField()
    location = models.CharField(max_length=100)
    mileage = models.IntegerField(help_text="Mileage in km")
    registration_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(Avg('rating'))['rating__avg'], 1)
        return 0.0

    @property
    def total_reviews(self):
        return self.reviews.count()

    def __str__(self):
        return f"{self.brand} {self.name} ({self.model_year})"

class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cars/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.car.name}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'car') # Prevent a user from writing multiple reviews for the same car

    def __str__(self):
        return f"Review for {self.car.name} by {self.user.username}"
