from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from LMS import settings

@shared_task
def send_verification_mail(subject, recipient, message):    
    msg = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=recipient,
    )
    msg.content_subtype = 'html'
    msg.send()
    return "Done"