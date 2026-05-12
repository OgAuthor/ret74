import os
import subprocess
import sys


def manage(*args):
    subprocess.check_call([sys.executable, "manage.py", *args])


if __name__ == "__main__":
    manage("migrate", "--noinput")
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
