from celery.decorators import task
from celery.utils.log import get_task_logger
from django.core.mail import EmailMultiAlternatives
logger = get_task_logger(__name__)


@task(name='Email')
def send_emails(from_email, recipients, subject, body, html):
    """ Send list of emails """

    # Create emails for each recipient
    for recipient in recipients:
        email = EmailMultiAlternatives(
            subject=subject,
            from_email=from_email,
            to=[recipient],
            body=body
        )
        email.attach_alternative(html, "text/html")
        email.send(fail_silently=True)
