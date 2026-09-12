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

class Event(models.Model):
    CATEGORY_CHOICES=[
        ('Conference', 'Conference'),
        ('Workshop', 'Workshop'),
        ('Concert', 'Concert'),
        ('Tech', 'Tech'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=250)
    date_time = models.DateTimeField()
    total_tickets = models.IntegerField()
    available_tickets = models.IntegerField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')

    def __str__(self):
        return f"{self.title}"

class Booking(models.Model):
    STATUS_CHOICES=[
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, related_name='event_bookings')
    tickets_booked = models.IntegerField(default= 1)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20 , choices=STATUS_CHOICES, default='Confirmed')

    def __str__(self):
        return f"Booking by {self.user.username} - {self.status}"

