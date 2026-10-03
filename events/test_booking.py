import pytest 
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from events.models import Booking, Event
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
def test_user_cannot_book_more_tickets_than_available():
    user = User.objects.create_user(username= 'organizer', password='password123')
    event = Event.objects.create(
            title="Event B", description="Desc", location="Addis Ababa", 
            total_tickets=10, available_tickets=5,
            date_time="2026-10-16T10:00:00Z", ticket_price="100.00",category ="Tech", organizer=user
        )
    customer = User.objects.create_user(username='customer1', password='password123')
    client = APIClient()
    client.force_authenticate(user=customer)
    url = reverse('bookings')
    payload = {
            "event": event.id ,
            "tickets_booked": 10
        }
    response = client.post(url, payload, format='json')
    assert response.status_code == 400, f"Error detail: {response.data}"
    assert Booking.objects.count() == 0