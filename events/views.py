from .serializers import UserProfileSerializer, BookingSerializer, EventSerializer, RegisterSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import User
from .models import Booking, Event , UserProfile, TicketType
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from .permissions import IsOrganizerOrReadOnly, IsOwnerOrReadOnly, IsAdminOrReadOnly
from .pagination import StandardResultsSetPagination
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework import status
from rest_framework.views import APIView
from .utils import send_booking_email
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
        booking = serializer.save(user=self.request.user)
        send_booking_email(
            subject=f"Booking Confirmation: {booking.event.title}",
            message=(
                f"Hello {booking.user.username},\n\n"
                f"Your booking is confirmed! Here are your ticket details:\n- Event: {booking.event.title}\n- Ticket Type: {booking.ticket_type.name}\n- Quantity: {booking.tickets_booked}\n- Total price: ${booking.total_price} is confirmed!\n\n"
                f"Thank you for booking with us!"
            ),
            recipient_email=booking.user.email,
        )
        send_booking_email(
            subject=f"New Booking Alert: {booking.event.title}",
            message=(
                f"Hello {booking.event.organizer.username},\n\n"
                f"New booking received for {booking.event.title}:\n- Customer: {booking.user.username}\n- Ticket Type: {booking.ticket_type.name}\n- Tickets Booked: {booking.tickets_booked}\n- Total Amount: ${booking.total_price}"
            ),
            recipient_email=booking.event.organizer.email,
        )
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
        send_booking_email(
            subject=f"Booking Cancelled: {booking.event.title}",
            message=(
                f"Hello {booking.user.username},\n\n"
                f"Your booking has been cancelled! Here are the cancellation details:\n- Event: {booking.event.title}\n- Ticket type: {booking.ticket_type.name}\n- Quantity Cancelled: {booking.tickets_booked}\n- Refund Amount: ${booking.total_price}\n\n"
                f"We hope to see you at future events!"
            ),
            recipient_email=booking.user.email,
        )
        send_booking_email(
            subject=f"Booking Cancellation Alert: {booking.event.title}",
            message=(
                f"Hello {booking.event.organizer.username},\n\n"
                f"A booking has been cancelled for {booking.event.title}:\n- Customer: {booking.user.username}\n- Ticket Type: {booking.ticket_type.name}\n- Tickets Cancelled: {booking.tickets_booked}\n- Refunded Amount: ${booking.total_price}"
                ),
            recipient_email=booking.event.organizer.email,
        )
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
    
class OrganizerAnalyticsView(APIView):
    permission_classes = [IsAuthenticated,IsOrganizerOrReadOnly]

    def get(self, request):
        total_events = Event.objects.filter(organizer = request.user).count()
        booking_stats = Booking.objects.filter(
            event__organizer = request.user,
            status = 'Confirmed'
        ).aggregate(
            tickets_booked = Sum('tickets_booked'),
            total_price = Sum('total_price')
        )
        tickets_sold = booking_stats['tickets_booked'] or 0
        revenue = booking_stats['total_price'] or 0
        ticket_stats = TicketType.objects.filter(
            event__organizer=request.user
        ).aggregate(total_remaining=Sum('available_quantity'))

        remaining_tickets = ticket_stats['total_remaining'] or 0
        return Response({
            "total_events": total_events,
            "total_tickets_sold": tickets_sold,
            "total_revenue": revenue,
            "remaining_tickets": remaining_tickets
        })