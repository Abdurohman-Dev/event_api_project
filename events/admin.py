from django.contrib import admin
from .models import Event, Booking, UserProfile, TicketType

class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title', 'location')
    inlines = [TicketTypeInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'event', 'tickets_booked', 'booking_date', 'status')
    list_filter = ('status', 'booking_date')
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'bio', 'role', 'phone_number','profile_picture')
    list_filter = ('role',)
    search_fields = ('user__username', 'phone_number')