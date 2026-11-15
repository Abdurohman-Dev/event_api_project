from django.core.mail import send_mail
from django.conf import settings
def send_booking_email(subject, message, recipient_email):
    if recipient_email:
        send_mail(
            subject= subject,
            message= message,
            from_email= settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently= True,
        )