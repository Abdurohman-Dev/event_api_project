from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from events.models import Event, Booking

class UserRegistrationTestCase(APITestCase):
    def test_user_registration_success(self):
        url = '/api/register/'
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Password123!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())
class EventAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='attendee', password='password123')
        self.event = Event.objects.create(
            title='Django Testing Workshop',
            description='A workshop on testing Django applications.',
            location='Online',
            date_time='2024-07-01T10:00:00Z',
            total_tickets=100,
            available_tickets=100,
            ticket_price=50.00,
            organizer=self.user
        )
    def test_get_event_list(self):
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_authenticated_user_can_book_tickets(self):
        self.client.force_authenticate(user=self.user)
        url = f'/api/events/{self.event.id}/book/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Booking.objects.filter(user=self.user, event=self.event).exists())