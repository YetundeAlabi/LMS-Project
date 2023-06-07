from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from LMS import settings

@shared_task
def send_verification_mail(subject, recipient, message):
    send_mail(
        subject=subject,
        message="",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient,
        fail_silently=False,
        html_message=message
        )
    
    msg = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=recipient,
    )
    msg.content_subtype = 'html'
    msg.send()
    print("Email sent")
    return "Done"