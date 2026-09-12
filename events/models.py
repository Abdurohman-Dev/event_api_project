from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Organizer', 'Origanizer'),
        ('Attendee', 'Attendee'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    role= models.CharField(max_length=20 ,choices=ROLE_CHOICES, default='Attendee')

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.role})"

class Booking(models.Model):
    STATUS_CHOICES=[
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='bookings')

    tickets_booked = models.IntegerField(default= 1)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20 , choices=STATUS_CHOICES, default='Confirmed')

    def __str__(self):
        return f"Booking by {self.user.username} - {self.status}"