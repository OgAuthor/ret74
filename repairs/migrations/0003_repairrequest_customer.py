from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("repairs", "0002_seed_statuses"),
    ]

    operations = [
        migrations.AddField(
            model_name="repairrequest",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="repair_requests",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Клиент",
            ),
        ),
    ]
