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
    # Organizer role ያለው ወይም staff/superuser የሆነ ዩዘር መፍጠር
    user = User.objects.create_user(
        username='organizeruser', 
        password='password123',
        is_staff=True  # ወይም role='organizer' ካለህ
    )
    # ካስፈለገ እንደ ሞዴልህ አቀማመጥ ፊልድ ካለህ: user.role = 'organizer'; user.save()
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
    Event.objects.all().delete()  # ከፊት ያሉትን ኢቨንቶች ሁሉ አጥፋ
    user = User.objects.create_user(username='organizer1', password='password123')
    
    # ለ organizer ሁልጊዜ User instance መስጠት አለብን
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