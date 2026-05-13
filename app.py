import os
import subprocess
import sys


def manage(*args):
    subprocess.check_call([sys.executable, "manage.py", *args])


def ensure_superuser():
    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
    email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "").strip()
    if not username or not password:
        return

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "telemaster74.settings")
    import django

    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()
    if User.objects.filter(username=username).exists():
        return

    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser {username!r} created.", flush=True)


if __name__ == "__main__":
    manage("migrate", "--noinput")
    ensure_superuser()
    manage("collectstatic", "--noinput")
    os.execvp(
        sys.executable,
        [
            sys.executable,
            "-m",
            "gunicorn",
            "telemaster74.wsgi:application",
            "--bind",
            "0.0.0.0:80",
        ],
    )
