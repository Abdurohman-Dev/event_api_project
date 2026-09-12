from .serializers import UserProfileSerializer, BookingSerializer, EventSerializer
from django.contrib.auth.models import User
from rest_framework import generics

class EventListCreateView(generics.ListCreateAPIView):


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):


class BookinglistCreateView(generics.ListCreateAPIView):
    

