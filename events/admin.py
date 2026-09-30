from django.contrib import admin
from .models import Event, Booking, UserProfile

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'total_tickets', 'available_tickets', 'ticket_price')
    search_fields = ('title', 'location')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'event', 'tickets_booked', 'booking_date', 'status')
    list_filter = ('status', 'booking_date')
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'bio', 'role', 'phone_number','profile_picture')
    list_filter = ('role',)
    search_fields = ('user__username', 'phone_number')
    