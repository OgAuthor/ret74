from secrets import choice
from string import ascii_uppercase, digits

from django.conf import settings
from django.db import models


class Status(models.Model):
    slug = models.SlugField("Код статуса", unique=True)
    title = models.CharField("Название", max_length=80, unique=True)
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_terminal = models.BooleanField("Завершающий статус", default=False)

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.title


class RepairRequest(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="repair_requests",
        verbose_name="Клиент",
        null=True,
        blank=True,
    )
    code = models.CharField("Код заявки", max_length=16, unique=True, editable=False, db_index=True)
    customer_name = models.CharField("ФИО", max_length=160)
    phone = models.CharField("Телефон", max_length=32)
    device = models.CharField("Устройство", max_length=160)
    problem_description = models.TextField("Описание проблемы")
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="requests",
        verbose_name="Статус",
    )
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.code} — {self.customer_name}"

    @staticmethod
    def generate_code() -> str:
        alphabet = ascii_uppercase + digits
        suffix = "".join(choice(alphabet) for _ in range(6))
        return f"TM74-{suffix}"

    def save(self, *args, **kwargs):
        if not self.code:
            while True:
                candidate = self.generate_code()
                if not RepairRequest.objects.filter(code=candidate).exists():
                    self.code = candidate
                    break
        super().save(*args, **kwargs)


class StatusChangeLog(models.Model):
    repair_request = models.ForeignKey(
        RepairRequest,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Заявка",
    )
    old_status = models.ForeignKey(
        Status,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Предыдущий статус",
        null=True,
        blank=True,
    )
    new_status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="status_changes",
        verbose_name="Новый статус",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="repair_status_changes",
        verbose_name="Кто изменил",
        null=True,
        blank=True,
    )
    comment = models.CharField("Комментарий", max_length=255, blank=True)
    created_at = models.DateTimeField("Дата изменения", auto_now_add=True)

    class Meta:
        verbose_name = "Изменение статуса"
        verbose_name_plural = "Журнал изменений статусов"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.repair_request.code}: {self.old_status or '—'} -> {self.new_status}"


class ManagerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="manager_profile",
        verbose_name="Пользователь",
    )
    full_name = models.CharField("ФИО менеджера", max_length=160)
    phone = models.CharField("Телефон", max_length=32, blank=True)

    class Meta:
        verbose_name = "Профиль менеджера"
        verbose_name_plural = "Профили менеджеров"

    def __str__(self) -> str:
        return self.full_name
