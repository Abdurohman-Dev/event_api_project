from .serializers import UserProfileSerializer, BookingSerializer, EventSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import User
from .models import Booking, Event , UserProfile
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import IsOrganizerOrReadOnly, IsOwnerOrReadOnly, IsAdminOrReadOnly
from .pagination import StandardResultsSetPagination
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination


    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['location','organizer']
    search_fields = ['title','description']
    ordering_fields = ['date_time', 'created_at']
    

    def perform_create(self, serializer):
        serializer.save(organizer= self.request.user)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]

class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Booking.objects.filter(user= self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated,IsOrganizerOrReadOnly]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class BookingCancelView(generics.RetrieveUpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Booking.objects.filter(user = self.request.user)
    def perform_update(self, serializer):
        serializer.save(status = "Cancelled")

class EventBookingView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def post(self, request, pk):
        event = get_object_or_404(Event , pk=pk)
        if Booking.objects.filter(user=request.user, event=event).exists():
            return Response({"error": "You have already booked a ticket for this event"})
        if event.available_tickets <= 0:
            return Response({"error": "No tickets available"}, status=status.HTTP_400_BAD_REQUEST)
        event.available_tickets -= 1
        event.save()
        Booking.objects.create(user = request.user, event=event)
        return Response ({"message": "Ticket booked successfull!"}, status=status.HTTP_201_CREATED)