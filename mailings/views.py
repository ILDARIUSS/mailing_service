# mailings/views.py

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from .models import Mailing, Recipient, Attempt


def send_mailing(request, mailing_id):
    # Получаем рассылку по ID
    mailing = Mailing.objects.get(id=mailing_id)

    # Проверяем, что рассылка активна (статус "draft")
    if mailing.status != 'draft':
        return HttpResponse("This mailing has already been sent or cancelled", status=400)

    # Получаем всех получателей рассылки
    recipients = mailing.recipients.all()
    attempt_status = "success"
    error_message = ""

    # Отправляем письма получателям
    for recipient in recipients:
        try:
            send_mail(
                mailing.message.subject,
                mailing.message.body,
                settings.DEFAULT_FROM_EMAIL,
                [recipient.email],
                fail_silently=False,
            )
        except Exception as e:
            attempt_status = "failure"
            error_message = str(e)

        # Создаем запись о попытке отправки письма
        Attempt.objects.create(
            mailing=mailing,
            status=attempt_status,
            server_response=error_message if attempt_status == "failure" else "Email sent successfully"
        )

    # Обновляем статус рассылки на "sent"
    mailing.status = 'sent'
    mailing.save()

    # Перенаправляем на страницу с результатом
    return redirect('mailings:mailing_sent', mailing_id=mailing.id)


def mailing_sent(request, mailing_id):
    # Получаем рассылку по ID для отображения на странице
    mailing = Mailing.objects.get(id=mailing_id)
    attempts = Attempt.objects.filter(mailing=mailing)

    # Передаем информацию о рассылке и попытках отправки в шаблон
    return render(request, 'mailings/mailing_sent.html', {'mailing': mailing, 'attempts': attempts})


def dashboard(request):
    # Подсчитываем количество уникальных получателей
    unique_recipients = Recipient.objects.distinct().count()

    # Количество активных рассылок
    active_mailings = Mailing.objects.filter(status="draft")

    # Количество всех рассылок
    total_mailings = Mailing.objects.count()

    return render(request, 'mailings/dashboard.html', {
        'unique_recipients': unique_recipients,
        'active_mailings': active_mailings,
        'total_mailings': total_mailings,
    })