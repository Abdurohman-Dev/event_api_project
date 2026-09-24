from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Booking, Event
from django.db.models import Sum

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, min_length= 6)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data.get('email', ''),
            password= validated_data['password']
        )
        UserProfile.objects.create(user=user)
        return user
        
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = UserProfile
        fields = ['user','id','role','bio','phone_number','profile_picture']
        read_only_fields = ['id','user']

class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.ReadOnlyField(source='organizer.username')
    class Meta:
        model = Event
        fields = '__all__'

class EventSummarySerializer(serializers.ModelSerializer):
     class Meta:
          model = Event
          fields = ['id', 'title', 'location', 'date_time', 'ticket_price']

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    event_detail = EventSummarySerializer(source= 'event',read_only = True)
    class Meta: 
        model = Booking
        fields = ['id','user','event','event_detail','tickets_booked','booking_date','status']
        read_only_fields = ['user', 'booking_date']
        
    def validate(self, data):
        if self.instance and self.instance.status == 'Cancelled':
                    raise serializers.ValidationError("ይህ ቲኬት አስቀድሞ ተሰርዟል!")
        if not self.instance:
            event = data.get('event')
            tickets_booked = data.get('tickets_booked')

            if tickets_booked <= 0 :
                raise serializers.ValidationError("መግዛት የሚቻለው ትኬት ከ 0 በላይ መሆን አለበት! ")
            
            total_booked = Booking.objects.filter(status = "Confirmed" , event=event)
            total_tickets = total_booked.aggregate(Sum('tickets_booked'))['tickets_booked__sum'] or 0
            remaining_tickets = event.total_tickets - total_tickets

            if tickets_booked > remaining_tickets :
                raise serializers.ValidationError (f"በቂ ቲኬት የለም የቀረው ቲኬት ብዛት {remaining_tickets} ብቻ ነው።")
        return data