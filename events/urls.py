from .views import EventDetailView,EventListCreateView,BookingListCreateView, UserProfileView
from django.urls import path

urlpatterns = [
    path('events/', EventListCreateView.as_view(), name='event-list'),
    path('events/<int:pk>/',EventDetailView.as_view() , name='event-detail'),
    path('bookings/', BookingListCreateView.as_view(), name= 'bookings'),
    path('profile/', UserProfileView.as_view(), name= 'user-profile'),
]
