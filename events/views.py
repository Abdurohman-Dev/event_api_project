from .serializers import UserProfileSerializer, BookingSerializer, EventSerializer, RegisterSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import User
from .models import Booking, Event , UserProfile
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from .permissions import IsOrganizerOrReadOnly, IsOwnerOrReadOnly, IsAdminOrReadOnly
from .pagination import StandardResultsSetPagination
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.select_related('organizer').all().order_by('-id')
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = {
        'location': ['exact', 'icontains'],
        'organizer': ['exact'], 
        }
    search_fields = ['title','description', 'location'],

    ordering_fields = ['date_time', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(organizer= self.request.user)
class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.select_related('organizer').all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]
class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Booking.objects.filter(user= self.request.user).select_related('event', 'user', 'ticket_type').order_by('-id')
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated,IsOrganizerOrReadOnly]

    def get_object(self):
        profile, created = UserProfile.objects.select_related('user').get_or_create(user=self.request.user)
        return profile
class BookingCancelView(generics.GenericAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Booking.objects.filter(user = self.request.user).select_related('event', 'user', 'ticket_type')
    def post(self, request, pk):
        booking = self.get_object()
        if booking.status == "Cancelled":
            return Response({"error": "This booking is already cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = "Cancelled"
        booking.ticket_type.available_quantity += booking.tickets_booked
        booking.ticket_type.save()
        booking.save()
        return Response({"message": "Booking cancelled successfully!"}, status=status.HTTP_200_OK)
class UserHostedEventsView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(organizer = self.request.user).select_related('organizer')
class UserBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user = self.request.user).select_related('event', 'user', 'ticket_type').order_by('-id')