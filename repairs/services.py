from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse

from .models import StatusChangeLog


def log_status_change(repair_request, old_status=None, changed_by=None, comment=""):
    if old_status and old_status.pk == repair_request.status_id:
        return None

    if changed_by and not changed_by.is_authenticated:
        changed_by = None

    return StatusChangeLog.objects.create(
        repair_request=repair_request,
        old_status=old_status,
        new_status=repair_request.status,
        changed_by=changed_by,
        comment=comment,
    )


def get_manager_notification_recipients():
    configured_emails = list(settings.MANAGER_NOTIFICATION_EMAILS)
    staff_emails = (
        get_user_model()
        .objects.filter(is_staff=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )

    recipients = []
    for email in [*configured_emails, *staff_emails]:
        normalized = email.strip()
        if normalized and normalized not in recipients:
            recipients.append(normalized)

    return recipients


def notify_managers_about_new_request(repair_request, request=None):
    recipients = get_manager_notification_recipients()
    if not recipients:
        return 0

    manager_path = reverse("manager_request_edit", args=[repair_request.pk])
    manager_url = request.build_absolute_uri(manager_path) if request else manager_path
    subject = f"Новая заявка {repair_request.code} на ремонт"
    message = "\n".join(
        [
            f"Поступила новая заявка {repair_request.code}.",
            "",
            f"Клиент: {repair_request.customer_name}",
            f"Телефон: {repair_request.phone}",
            f"Устройство: {repair_request.device}",
            f"Описание: {repair_request.problem_description}",
            "",
            f"Открыть заявку: {manager_url}",
        ]
    )

    return send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=True,
    )
