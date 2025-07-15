
from django.conf import settings
from django.core.mail import send_mail
from .models import Notification

def send_notification_email(subject, message, recipient_email, recipient_user=None):
    # Send the actual email (adjust sender email as needed)
    send_mail(
        subject=subject,
        message=message,
        from_email='no-reply@fieldonline.com',
        recipient_list=[recipient_email],
        fail_silently=False,
    )

    # Save notification to DB if user object is given
    if recipient_user:
        Notification.objects.create(
            recipient=recipient_user,
            subject=subject,
            message=message,
        )
