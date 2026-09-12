from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Booking, Event

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
        fields = '__all__'