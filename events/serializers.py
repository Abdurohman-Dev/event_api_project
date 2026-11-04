from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Booking, Event, TicketType
from django.db.models import Sum
from django.db import transaction

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
class TicketTypeSerializer(serializers.ModelSerializer):
     class Meta:
          model = TicketType
          fields = ['id', 'name', 'price', 'total_quantity', 'available_quantity']
          read_only_fields = ['available_quantity']
class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.ReadOnlyField(source='organizer.username')
    ticket_type = TicketTypeSerializer(many = True)
    class Meta:
        model = Event
        fields = ['id', 'title', 'ticket_type', 'description', 'location', 'date_time', 'category', 'organizer']
        read_only_fields = ['id', 'ticket_type', 'organizer']
class EventSummarySerializer(serializers.ModelSerializer):
     class Meta:
          model = Event
          fields = ['id', 'title', 'location', 'date_time']

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    event_detail = EventSummarySerializer(source= 'event', read_only = True)
    class Meta: 
        model = Booking
        fields = ['id','user','event','ticket_type','event_detail','tickets_booked', 'total_price','booking_date','status']
        read_only_fields = ['user', 'booking_date']
        
    def validate(self, data):
        if self.instance and self.instance.status == 'Cancelled':
                    raise serializers.ValidationError("ይህ ቲኬት አስቀድሞ ተሰርዟል!")
        if not self.instance:
            tickets_booked = data.get('tickets_booked', 1)
            ticket_type = data.get('ticket_type')
            
            if tickets_booked <= 0 :
                raise serializers.ValidationError("መግዛት የሚቻለው ትኬት ከ 0 በላይ መሆን አለበት! ")
            
            if ticket_type and tickets_booked:
                if tickets_booked > ticket_type.available_quantity:
                    raise serializers.ValidationError(f"ለመረጡት የቲኬት አይነት በቂ ቀሪ ትኬት የለም! የቀረው {ticket_type.available_quantity} ብቻ ነው።")
        return data
    def create(self, validated_data):
        qty = validated_data.get("tickets_booked", 1)
        with transaction.atomic():
            ticket = TicketType.objects.select_for_update().get(pk=validated_data["ticket_type"].pk)
            if ticket.available_quantity < qty:
                 raise serializers.ValidationError({"tickets_booked": f"only {ticket.available_quantity} tickets left."})
            ticket.available_quantity -= qty
            ticket.save(update_fields=["available_quantity"])

            validated_data["total_price"] = ticket.price * qty
            return Booking.objects.create(**validated_data)