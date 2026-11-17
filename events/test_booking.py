import pytest 
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from events.models import Booking, Event, TicketType
from django.urls import reverse
from django.core import mail
User = get_user_model()

@pytest.mark.django_db
def test_user_cannot_book_more_tickets_than_available():
    user = User.objects.create_user(username= 'organizer', password='password123')
    event = Event.objects.create(
            title="Event B", description="Desc", location="Addis Ababa", 
            total_tickets=10, available_tickets=5,
            date_time="2026-10-16T10:00:00Z", ticket_price="100.00", category ="Tech", organizer=user
        )
    customer = User.objects.create_user(username='customer1', password='password123')
    client = APIClient()
    client.force_authenticate(user=customer)
    url = reverse('bookings')
    payload = {
            "event": event.id ,
            "tickets_booked": 11
        }
    response = client.post(url, payload, format='json')
    assert response.status_code == 400, f"Error detail: {response.data}"
    assert Booking.objects.count() == 0

@pytest.mark.django_db
def test_user_can_successfully_book_tickets():
    user = User.objects.create_user(username='organizer2', password='password123')
    event = Event.objects.create(
                title="Event B", description="Desc", location="Addis Ababa", 
                total_tickets=10, available_tickets=10,
                date_time="2026-10-16T10:00:00Z", ticket_price="100.00",category ="Tech", organizer=user
            )
    client = APIClient()
    client.force_authenticate(user=user)
    payload={
        "event": event.id ,
        "tickets_booked" : 3
    }
    url = reverse('bookings')
    response = client.post(url, payload, format='json')

    assert response.status_code == 201
    assert Booking.objects.count() == 1 
    booking = Booking.objects.first()
    assert booking.tickets_booked == 3

@pytest.mark.django_db
def test_cannot_book_zero_or_negative_tickets():
    user = User.objects.create_user(username='organizer2', password='password123')
    event = Event.objects.create(
                title="Event B", description="Desc", location="Addis Ababa", 
                total_tickets=10, available_tickets=10,
                date_time="2026-10-16T10:00:00Z", ticket_price="100.00",category ="Tech", organizer=user
            )
    client = APIClient()
    client.force_authenticate(user=user)
    payload={
        "event": event.id,
        "tickets_booked": 0
    }
    url = reverse('bookings')
    response = client.post(url, payload, format='json')

    assert response.status_code == 400
    assert Booking.objects.count() == 0

@pytest.mark.django_db
def test_multiple_bookings_accumulate_correctly():
    user = User.objects.create_user(username='customer1', password='password1234')
    userb = User.objects.create_user(username='customer2', password='password123')
    event = Event.objects.create(
            title="Event B", description="Desc", location="Addis Ababa", 
            total_tickets=10, available_tickets=10,
            date_time="2026-10-16T10:00:00Z", ticket_price="100.00",category ="Tech", organizer=user
        )
    client = APIClient()
    client.force_authenticate(user=user)
    payload= {
        "event": event.id , 
        "tickets_booked": 4
    }
    url = reverse('bookings')
    response = client.post(url, payload, format='json')

    assert response.status_code == 201

    client2 = APIClient()
    client2.force_authenticate(user = userb)
    response = client2.post(url, payload, format='json')

    assert response.status_code == 201

    client = APIClient()
    client.force_authenticate(user = user)
    response = client.post(url, payload, format='json')

    assert response.status_code == 400
    assert Booking.objects.count() == 2

@pytest.mark.django_db
def test_user_can_get_their_own_bookings():
    usera = User.objects.create_user(username='organizer', password='password123')
    userb = User.objects.create_user(username='organizer2', password='password123')
    event = Event.objects.create(
        title="Event B", description="Desc", location="Addis Ababa", 
        total_tickets=10, available_tickets=10,
        date_time="2026-10-16T10:00:00Z", ticket_price="100.00",category ="Tech", organizer=usera
    )
    payload = {
        "event": event.id ,
        "tickets_booked":  4
    }
    client1 = APIClient()
    client1.force_authenticate(user=usera)
    url = reverse('bookings')
    response = client1.post(url, payload, format='json')
    assert response.status_code == 201

    client2 = APIClient()
    client2.force_authenticate(user = userb)
    response = client2.post(url, payload, format='json')
    assert response.status_code == 201
    response = client1.get(url)

    assert response.status_code == 200
    assert len(response.data['results']) == 1

@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_bookings():
    user = User.objects.create_user(username='organizer2', password='password123')
    event = Event.objects.create(
        title="Event B", description="Desc", location="Addis Ababa", 
        total_tickets=10, available_tickets=10,
        date_time="2026-10-16T10:00:00Z", ticket_price="100.00",category ="Tech", organizer=user
    )
    payload = {
        "event": event.id ,
        "tickets_booked":  4
    }
    client = APIClient()
    url = reverse('bookings')
    response = client.post(url, payload, format='json')
    response = client.get(url)

    assert response.status_code == 401

@pytest.mark.django_db
def test_user_can_cancel_booking_and_tickets_are_freed():
    user1 = User.objects.create_user(username='customer1', password='password123')
    user2 = User.objects.create_user(username='customer2', password='password123')
    event = Event.objects.create(
            title="Event B", description="Desc", location="Addis Ababa", 
            total_tickets=5, available_tickets=5,
            date_time="2026-10-16T10:00:00Z", ticket_price="100.00",category ="Tech", organizer=user1
        )
    payload = {
            "event": event.id ,
            "tickets_booked":  5
        }
    client1 = APIClient()
    client1.force_authenticate(user = user1)
    url = reverse('bookings')
    response = client1.post(url, payload, format='json')

    assert response.status_code == 201
    payload2 = {
                "event": event.id ,
                "tickets_booked":  1
            }
    booking = Booking.objects.first()
    client2 = APIClient()
    client2.force_authenticate(user = user2)
    response = client2.post(url, payload2, format='json')

    assert response.status_code == 400

    response = client1.post(reverse('booking-cancel', kwargs={'pk': booking.id}))

    assert response.status_code == 200

    response = client2.post(url, payload2, format='json')

    assert response.status_code == 201
    assert Booking.objects.count() == 2

@pytest.mark.django_db
def test_booking_list_includes_event_detail():
    user = User.objects.create_user(username='organizer', password='password123')
    event = Event.objects.create(
        title="Tech Expo 2026", description="Desc", location="Addis Ababa", 
        total_tickets=10, available_tickets=10,
        date_time="2026-10-16T10:00:00Z", ticket_price="100.00",category ="Tech", organizer=user
    )
    payload = {
        "event": event.id ,
        "tickets_booked":  4
    }
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse('bookings')
    response = client.post(url, payload, format='json')

    booking = Booking.objects.first()
    assert response.status_code == 201 

    response = client.get(url)

    assert response.status_code == 200
    assert 'event_detail' in response.data['results'][0]
    assert response.data['results'][0]['event_detail']['title'] == "Tech Expo 2026"

@pytest.mark.django_db
def test_prevent_double_booking_cancellation_attempt():
    user = User.objects.create_user(username='organizer', password='password123')
    event = Event.objects.create(
        title="Tech Expo 2026", description="Desc", location="Addis Ababa", 
        total_tickets=10, available_tickets=10,
        date_time="2026-10-16T10:00:00Z", ticket_price="100.00",category ="Tech", organizer=user
    )
    payload = {
        "event": event.id ,
        "tickets_booked":  2
    }
    client = APIClient()
    client.force_authenticate(user = user)
    url = reverse('bookings')
    response = client.post(url, payload, format='json')
    booking = Booking.objects.first()
    assert response.status_code == 201 

    response = client.post(reverse('booking-cancel', kwargs={'pk': booking.id}))
    assert response.status_code == 200

    response = client.post(reverse('booking-cancel', kwargs={'pk': booking.id}))
    assert response.status_code == 400 

@pytest.mark.django_db
def test_user_cannot_cancel_others_booking():
    user1 = User.objects.create_user(username='customer1', password='password123')
    user2 = User.objects.create_user(username='customer2', password='password123')
    event = Event.objects.create(
        title="Tech Expo 2026", description="Desc", location="Addis Ababa", 
        total_tickets=10, available_tickets=10,
        date_time="2026-10-16T10:00:00Z", ticket_price="100.00",category ="Tech", organizer=user1
    )
    payload = {
        "event": event.id ,
        "tickets_booked":  2
    }    
    client1 = APIClient()
    client1.force_authenticate(user=user1)
    url = reverse('bookings')
    response = client1.post(url, payload, format='json')
    booking = Booking.objects.first()

    assert response.status_code == 201

    client2 = APIClient()
    client2.force_authenticate(user = user2)
    response = client2.post(reverse('booking-cancel', kwargs={'pk': booking.id}))

    assert response.status_code == 404
    booking.refresh_from_db()
    assert booking.status == "Confirmed"
@pytest.mark.django_db
def test_booking_creation_sends_confirmation_email():
    organizer = User.objects.create_user(username="org1", password="password")
    customer = User.objects.create_user(username='cust1', email='cust1@gmail.com', password='password1234')
    event = Event.objects.create(
        title = "Django Summit",
        description = "Tech conference", 
        location = "Addis Ababa", 
        date_time= "2026-11-20T10:00:00Z",
        category = "Tech", 
        organizer = organizer
    )
    ticket_type = TicketType.objects.create(
        event = event,
        name = "Regular", 
        price = "100.00", 
        total_quantity = 20
    )
    payload = {
        "event": event.id,
        "ticket_type": ticket_type.id, 
        "tickets_booked": 10
    }
    client = APIClient()
    client.force_authenticate(user = customer)
    url = reverse('bookings')
    response = client.post(url, payload, format='json')

    assert response.status_code == 201
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Booking Confirmation: Django Summit"
    assert mail.outbox[0].to == ['cust1@gmail.com']
    assert "Hello cust1" in mail.outbox[0].body
@pytest.mark.django_db
def test_booking_cancellation_sends_cancellation_email():
    organizer = User.objects.create_user(username="org2", password="password")
    customer = User.objects.create_user(username='cust2', email='cust2@gmail.com', password='password1234')
    event = Event.objects.create(
        title = "Python Meetup",
        description = "Community meetup", 
        location = "semera", 
        date_time= "2026-11-20T10:00:00Z",
        category = "Tech", 
        organizer = organizer
    )
    ticket_type = TicketType.objects.create(
        event = event,
        name = "VIP", 
        price = "250.00", 
        total_quantity = 10
    )
    client = APIClient()
    client.force_authenticate(user = customer)
    
    create_res = client.post(reverse('bookings'), {
        "event": event.id,
        "ticket_type": ticket_type.id, 
        "tickets_booked": 1
    }, format= 'json')

    assert create_res.status_code == 201
    booking = Booking.objects.first()
    cancel_url = reverse('booking-cancel', args=[booking.id])
    cancel_res = client.post(cancel_url)

    assert cancel_res.status_code == 200
    assert len(mail.outbox) == 2
    assert mail.outbox[1].subject == "Booking Cancelled: Python Meetup"
    assert mail.outbox[1].to == ['cust2@gmail.com']