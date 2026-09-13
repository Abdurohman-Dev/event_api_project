from .serializers import UserProfileSerializer, BookingSerializer, EventSerializer
from django.contrib.auth.models import User
from .models import Booking, Event , UserProfile
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsOrganizerOrReadOnly

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizer= self.request.user)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]

class BookingListCreateView(generics.ListCreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer