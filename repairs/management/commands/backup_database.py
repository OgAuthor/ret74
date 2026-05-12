from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.utils import timezone


class Command(BaseCommand):
    help = "Creates a JSON backup of the project database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            default=str(settings.BASE_DIR / "backups"),
            help="Directory where the backup file will be saved.",
        )
        parser.add_argument(
            "--database",
            default="default",
            help="Database alias to dump.",
        )

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
        output_path = output_dir / f"database-backup-{timestamp}.json"

        with output_path.open("w", encoding="utf-8") as backup_file:
            call_command(
                "dumpdata",
                natural_foreign=True,
                natural_primary=True,
                indent=2,
                database=options["database"],
                exclude=["contenttypes", "sessions"],
                stdout=backup_file,
            )

        if options["verbosity"] > 0:
            self.stdout.write(self.style.SUCCESS(f"Backup saved to {output_path}"))
