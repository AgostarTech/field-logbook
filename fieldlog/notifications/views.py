from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def notification_history(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-sent_at')

    data = [{
        'subject': n.subject,
        'message': n.message,
        'sent_at': n.sent_at.strftime('%Y-%m-%d %H:%M'),
        'read': n.read,
    } for n in notifications]

    return JsonResponse({'notifications': data})
