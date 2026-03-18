# mailings/management/commands/send_pending_mailings.py

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailings.models import Mailing, Attempt


class Command(BaseCommand):
    help = "Отправляет все рассылки со статусом draft, время начала которых уже наступило"

    def handle(self, *args, **options):
        now = timezone.now()

        pending_mailings = Mailing.objects.filter(
            status="draft",
            start_time__lte=now,
        )

        if not pending_mailings.exists():
            self.stdout.write(self.style.WARNING("Нет рассылок для отправки."))
            return

        sent_count = 0

        for mailing in pending_mailings:
            recipients = mailing.recipients.all()

            if not recipients.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"Рассылка ID={mailing.id} пропущена: нет получателей."
                    )
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

                    Attempt.objects.create(
                        mailing=mailing,
                        status="success",
                        server_response="Email sent successfully",
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Рассылка ID={mailing.id}: письмо отправлено на {recipient.email}"
                        )
                    )

                except Exception as e:
                    Attempt.objects.create(
                        mailing=mailing,
                        status="failure",
                        server_response=str(e),
                    )

                    self.stdout.write(
                        self.style.ERROR(
                            f"Рассылка ID={mailing.id}: ошибка отправки на {recipient.email}: {e}"
                        )
                    )

            mailing.status = "sent"
            mailing.save()
            sent_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Обработано рассылок: {sent_count}")
        )