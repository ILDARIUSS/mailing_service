# mailings/management/commands/send_scheduled_mailings.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from mailings.models import Mailing, Attempt


class Command(BaseCommand):
    help = "Отправляет все запланированные рассылки, у которых start_time <= текущее время и status='draft'"

    def handle(self, *args, **options):
        now = timezone.now()

        mailings = Mailing.objects.filter(
            status="draft",
            start_time__lte=now,
        )

        if not mailings.exists():
            self.stdout.write(self.style.WARNING("Нет рассылок для автоматической отправки"))
            return

        sent_count = 0

        for mailing in mailings:
            recipients = mailing.recipients.all()

            if not recipients.exists():
                Attempt.objects.create(
                    mailing=mailing,
                    status="failure",
                    server_response="У рассылки нет получателей",
                )
                continue

            for recipient in recipients:
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )
                    status = "success"
                    response = "Email sent successfully"
                except Exception as e:
                    status = "failure"
                    response = str(e)

                Attempt.objects.create(
                    mailing=mailing,
                    status=status,
                    server_response=response,
                )

            mailing.status = "sent"
            mailing.save()
            sent_count += 1

        self.stdout.write(self.style.SUCCESS(f"Автоматически отправлено рассылок: {sent_count}"))