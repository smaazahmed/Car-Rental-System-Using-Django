from django.contrib import admin
from .models import Booking, Payment

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    can_delete = False

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'car', 'pickup_date', 'return_date', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'pickup_date', 'return_date')
    search_fields = ('user__username', 'car__name', 'id')
    actions = ['approve_bookings', 'complete_bookings', 'cancel_bookings']
    inlines = [PaymentInline]

    def approve_bookings(self, request, queryset):
        queryset.update(status='Approved')
    approve_bookings.short_description = "Approve selected bookings"

    def complete_bookings(self, request, queryset):
        queryset.update(status='Completed')
    complete_bookings.short_description = "Mark selected bookings as Completed"

    def cancel_bookings(self, request, queryset):
        queryset.update(status='Cancelled')
    cancel_bookings.short_description = "Cancel selected bookings"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'transaction_id', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('transaction_id', 'booking__id', 'booking__user__username')
