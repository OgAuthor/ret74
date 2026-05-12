from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("repairs", "0003_repairrequest_customer"),
    ]

    operations = [
        migrations.CreateModel(
            name="StatusChangeLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("comment", models.CharField(blank=True, max_length=255, verbose_name="Комментарий")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения")),
                (
                    "changed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="repair_status_changes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Кто изменил",
                    ),
                ),
                (
                    "new_status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="status_changes",
                        to="repairs.status",
                        verbose_name="Новый статус",
                    ),
                ),
                (
                    "old_status",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="repairs.status",
                        verbose_name="Предыдущий статус",
                    ),
                ),
                (
                    "repair_request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_history",
                        to="repairs.repairrequest",
                        verbose_name="Заявка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Изменение статуса",
                "verbose_name_plural": "Журнал изменений статусов",
                "ordering": ["-created_at", "-id"],
            },
        ),
    ]
