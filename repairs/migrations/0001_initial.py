# Generated manually for the starter project.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Status",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(unique=True, verbose_name="Код статуса")),
                ("title", models.CharField(max_length=80, unique=True, verbose_name="Название")),
                ("sort_order", models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")),
                ("is_terminal", models.BooleanField(default=False, verbose_name="Завершающий статус")),
            ],
            options={
                "verbose_name": "Статус",
                "verbose_name_plural": "Статусы",
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="ManagerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=160, verbose_name="ФИО менеджера")),
                ("phone", models.CharField(blank=True, max_length=32, verbose_name="Телефон")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="manager_profile", to=settings.AUTH_USER_MODEL, verbose_name="Пользователь")),
            ],
            options={
                "verbose_name": "Профиль менеджера",
                "verbose_name_plural": "Профили менеджеров",
            },
        ),
        migrations.CreateModel(
            name="RepairRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(db_index=True, editable=False, max_length=16, unique=True, verbose_name="Код заявки")),
                ("customer_name", models.CharField(max_length=160, verbose_name="ФИО")),
                ("phone", models.CharField(max_length=32, verbose_name="Телефон")),
                ("device", models.CharField(max_length=160, verbose_name="Устройство")),
                ("problem_description", models.TextField(verbose_name="Описание проблемы")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создана")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлена")),
                ("status", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="requests", to="repairs.status", verbose_name="Статус")),
            ],
            options={
                "verbose_name": "Заявка",
                "verbose_name_plural": "Заявки",
                "ordering": ["-created_at"],
            },
        ),
    ]
