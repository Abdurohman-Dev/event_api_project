import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from events.models import Event

User = get_user_model()

@pytest.mark.django_db
def test_get_events_list():
    client = APIClient()
    url = reverse('event-list')
    response = client.get(url)
    
    assert response.status_code == 200

@pytest.mark.django_db
def test_create_event():
    client = APIClient()
    user = User.objects.create_user(
        username='organizeruser', 
        password='password123',
        is_staff=True
    )
    user.role = 'Organizer'; user.save()
    
    client.force_authenticate(user=user)
    url = reverse('event-list')
    
    payload = {
        "title": "Tech Conference 2026",
        "description": "A big tech event",
        "location": "Semera",
        "total_tickets": 100,
        "category": "Tech",
        "date_time": "2026-10-15T10:00:00Z",
        "ticket_price": "50.00"
    }
    
    response = client.post(url, payload, format='json')
    
    assert response.status_code == 201, f"Error details: {response.data}"
@pytest.mark.django_db
def test_filter_events_by_location():
    Event.objects.all().delete()
    user = User.objects.create_user(username='organizer1', password='password123')

    Event.objects.create(
        title="Event A", description="Desc", location="Semera", total_tickets=100, available_tickets=100,
        date_time="2026-10-15T10:00:00Z", ticket_price="50.00", organizer=user
    )
    Event.objects.create(
        title="Event B", description="Desc", location="Addis Ababa", 
        total_tickets=100, available_tickets=100,
        date_time="2026-10-16T10:00:00Z", ticket_price="100.00", organizer=user
    )
    
    client = APIClient()
    url = reverse('event-list') + "?location=Semera"
    response = client.get(url)
    
    assert response.status_code == 200
    assert len(response.data['results']) == 1 
    assert response.data['results'][0]['location'] == "Semera"

@pytest.mark.django_db
def test_get_single_event_detail():
    user = User.objects.create_user(username = 'organizer2' , password='password123')

    event = Event.objects.create(
        title="Event C", description="Desc", location="Dire Dawa", total_tickets=100, available_tickets=100,
        date_time="2026-10-17T10:00:00Z", ticket_price="75.00", organizer=user
    )
    client = APIClient()

    url = reverse('event-detail', args=[event.id])
    response = client.get(url)

    assert response.status_code == 200
    assert response.data['title'] == event.title

@pytest.mark.django_db
def test_update_event():
    user = User.objects.create_user(username = 'organizer4', password = 'password123')
    event = Event.objects.create(
        title="Event D", description="Desc", location="Dire Dawa", total_tickets=100, available_tickets=100,
        date_time="2026-10-17T10:00:00Z", ticket_price="75.00", organizer=user
    )
    client = APIClient()
    client.force_authenticate(user = user)
    updated_data = {
    "title": "Updated Event Title",
    "description": "Updated Desc",
    "location": "Addis Ababa",
    "total_tickets": 100,
    "available_tickets": 100,
    "date_time": "2026-10-17T10:00:00Z",
    "ticket_price": "43.00", 
    "category": "Tech"
    }
    url = reverse('event-detail', args=[event.id])
    response = client.put(url, updated_data, format='json')

    assert response.status_code == 200, f"Error details: {response.data}"
    assert response.data['title'] == "Updated Event Title"

@pytest.mark.django_db
def test_delete_event():
    user = User.objects.create_user(username= "organizer", password= "password123")
    event = Event.objects.create(
            title="Event E", description="Desc", location="Dire Dawa", total_tickets=100, available_tickets=100,
            date_time="2026-10-17T10:00:00Z", ticket_price="75.00", organizer=user
        )
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse('event-detail', args=[event.id])
    response = client.delete(url)

    assert response.status_code == 204
    assert Event.objects.filter(id=event.id).exists() == False

@pytest.mark.django_db
def test_unauthorized_user_cannot_create_event():
    client = APIClient()
    payload = {
            "title": "Tech Conference 2026",
            "description": "A big tech event",
            "location": "Semera",
            "total_tickets": 100,
            "category": "Tech",
            "date_time": "2026-10-15T10:00:00Z",
            "ticket_price": "50.00"
        }
    url = reverse('event-list')
    response = client.post(url, payload, format='json')

    assert response.status_code == 401, f"Error detail: {response.data}"
    assert Event.objects.count() == 0 

@pytest.mark.django_db
def test_non_organizer_cannot_update_event():
    user = User.objects.create_user(username='organizer', password='password123')
    event = Event.objects.create(
                title="Event F", description="Desc", location="Dire Dawa", total_tickets=100, available_tickets=100,
                date_time="2026-10-17T10:00:00Z", ticket_price="75.00", organizer=user
            )
    user2 = User.objects.create_user(username='Attackerr', password='password1234')
    updated_data = {
        "title": "Hacked Event Title",
        "description": "Updated Desc",
        "location": "Addis Ababa",
        "total_tickets": 100,
        "available_tickets": 100,
        "date_time": "2026-10-17T10:00:00Z",
        "ticket_price": "43.00", 
        "category": "Tech"
        }
    url = reverse('event-detail', args=[event.id])
    client = APIClient()
    client.force_authenticate(user=user2)
    response = client.put(url, updated_data, format= 'json')

    assert response.status_code == 403