from django import forms
from .models import Car, Review

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'name', 'brand', 'model_year', 'color', 'transmission_type', 
            'fuel_type', 'seating_capacity', 'rent_price_per_day', 
            'is_available', 'description', 'location', 'mileage', 'registration_number'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Model S'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tesla'}),
            'model_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Midnight Cherry Red'}),
            'transmission_type': forms.Select(attrs={'class': 'form-select'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'seating_capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5'}),
            'rent_price_per_day': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 150.00'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the vehicle specs, luxury features...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Los Angeles, CA'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 15000'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CA-99X-Z12'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your review here...'}),
        }
