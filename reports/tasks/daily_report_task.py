import os
from django.conf import settings
from django.core.mail import EmailMessage
from celery import shared_task
from users.models import User
from reports.utils import generate_academic_pdf

@shared_task
def send_daily_reports():
    for user in User.objects.filter(role__in=['student', 'teacher']):
        try:
            buffer = generate_academic_pdf(user)
            filename = f"{user.role}_report_{user.username}.pdf"

            # Guardar temporalmente el archivo
            path = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
            with open(path, 'wb') as f:
                f.write(buffer.getvalue())

            # Enviar correo
            email = EmailMessage(
                subject='Your Daily Academic Report',
                body='Please find attached your updated academic report.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach(filename, buffer.getvalue(), 'application/pdf')
            email.send()

        except Exception as e:
            print(f"Error processing {user.email}: {e}")
