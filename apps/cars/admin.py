from django.contrib import admin
from .models import Car, CarImage, Review

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 2

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'model_year', 'transmission_type', 'fuel_type', 'rent_price_per_day', 'is_available', 'location')
    list_filter = ('brand', 'transmission_type', 'fuel_type', 'is_available', 'location')
    search_fields = ('name', 'brand', 'registration_number', 'location')
    inlines = [CarImageInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('car', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('car__name', 'user__username', 'comment')
