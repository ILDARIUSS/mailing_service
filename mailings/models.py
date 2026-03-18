# mailings/models.py

from django.db import models
from users.models import User  # Импортируем User для связи с пользователем


# Модель для получателя
class Recipient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.full_name


# Модель для сообщения
class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject


# Модель для рассылки
class Mailing(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    ]

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(choices=STATUS_CHOICES, default='draft', max_length=10)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Mailing {self.id} ({self.status})"


# Модель для попыток отправки рассылки
class Attempt(models.Model):
    status_choices = [
        ('success', 'Success'),
        ('failure', 'Failure')
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=status_choices, max_length=10)
    server_response = models.TextField()

    def __str__(self):
        return f"Attempt {self.id} - {self.status}"