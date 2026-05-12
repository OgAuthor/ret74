from django.db import migrations


def create_statuses(apps, schema_editor):
    Status = apps.get_model("repairs", "Status")
    statuses = [
        ("review", "На рассмотрении", 10, False),
        ("accepted", "Заявка принята", 20, False),
        ("queued", "Ожидает очереди", 30, False),
        ("in_progress", "В работе", 40, False),
        ("completed", "Ремонт выполнен", 50, True),
    ]
    for slug, title, sort_order, is_terminal in statuses:
        Status.objects.update_or_create(
            slug=slug,
            defaults={
                "title": title,
                "sort_order": sort_order,
                "is_terminal": is_terminal,
            },
        )


def delete_statuses(apps, schema_editor):
    Status = apps.get_model("repairs", "Status")
    Status.objects.filter(slug__in=["review", "accepted", "queued", "in_progress", "completed"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("repairs", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_statuses, delete_statuses),
    ]
