from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Booking, Event
from django.db.models import Sum

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = UserProfile
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.ReadOnlyField(source='organizer.username')
    class Meta:
        model = Event
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta: 
        model = Booking
        fields = ['id','user','event','tickets_booked','booking_date','status']
        read_only_fields = ['user', 'booking_date']

    def validate(self, data):
        event = data.get('event')
        tickets_booked = data.get('tickets_booked')
        booked_tickets = Booking.objects.filter(event=event)
        total_tickets = booked_tickets.aggregate(Sum('tickets_booked'))['tickets_booked__sum'] or 0
        remaining_tickets = event.total_tickets - total_tickets
        if tickets_booked > remaining_tickets:
            raise serializers.ValidationError("በቂ ቲኬት የለም...!")
        return data