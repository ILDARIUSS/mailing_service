# mailings/admin.py

from django.contrib import admin, messages
from django.core.mail import send_mail
from django.conf import settings

from .models import Mailing, Recipient, Attempt, Message


# ====== MailingAdmin ======
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "start_time",
        "end_time",
        "message",
        "owner",
        "success_count",
        "failure_count",
    )
    actions = ["send_mailing"]
    exclude = ("owner",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.owner == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.owner == request.user

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.owner == request.user

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "message":
                kwargs["queryset"] = Message.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "recipients":
                kwargs["queryset"] = Recipient.objects.filter(user=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Автоподставляем owner при создании новой рассылки"""
        if not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def send_mailing(self, request, queryset):
        """Массовая отправка рассылки"""
        sent_count = 0

        if not request.user.is_superuser:
            queryset = queryset.filter(owner=request.user)

        for mailing in queryset:
            if mailing.status != "draft":
                continue

            recipients = mailing.recipients.all()

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

        if sent_count > 0:
            self.message_user(request, f"Отправлено рассылок: {sent_count}")
        else:
            self.message_user(
                request,
                "Нет рассылок со статусом draft",
                level=messages.WARNING,
            )

    send_mailing.short_description = "Отправить выбранные рассылки"

    def success_count(self, obj):
        return obj.attempt_set.filter(status="success").count()

    success_count.short_description = "Успешно"

    def failure_count(self, obj):
        return obj.attempt_set.filter(status="failure").count()

    failure_count.short_description = "Ошибки"


# ====== MessageAdmin ======
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner")
    exclude = ("owner",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.owner == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.owner == request.user

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.owner == request.user

    def save_model(self, request, obj, form, change):
        """Автоподставляем owner при создании нового сообщения"""
        if not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


# ====== RecipientAdmin ======
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "user")
    exclude = ("user",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.user == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.user == request.user

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.user == request.user

    def save_model(self, request, obj, form, change):
        """Автоподставляем user при создании нового получателя"""
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)


# ====== AttemptAdmin ======
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("mailing", "status", "attempt_time")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(mailing__owner=request.user)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.mailing.owner == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.mailing.owner == request.user

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.mailing.owner == request.user


# ====== Регистрация в админке ======
admin.site.register(Mailing, MailingAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Recipient, RecipientAdmin)
admin.site.register(Attempt, AttemptAdmin)