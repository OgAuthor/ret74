# Деплой RET 74 на Amvera Cloud

Основная инструкция находится в файле:

```text
HOSTING_AMVERA_INSTRUCTION.md
```

Коротко:

1. Загрузи папку `ForHost` в GitHub.
2. В Amvera создай PostgreSQL.
3. В Amvera создай Python-приложение из GitHub-репозитория.
4. Убедись, что Amvera видит `amvera.yaml`.
5. Заполни переменные окружения:

```text
DEBUG=False
SECRET_KEY=длинный-секретный-ключ
DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DBNAME
ALLOWED_HOSTS=домен-приложения.amvera.io
CSRF_TRUSTED_ORIGINS=https://домен-приложения.amvera.io
SITE_DOMAIN=домен-приложения.amvera.io
COMPANY_LEGAL_NAME=RET 74
```

6. Запусти деплой.
7. После успешного запуска создай администратора:

```bash
python3 manage.py createsuperuser
```

Amvera запускает проект командой из `amvera.yaml`:

```bash
python3 manage.py migrate && python3 manage.py collectstatic --noinput && gunicorn telemaster74.wsgi:application --bind 0.0.0.0:80
```

Для настоящей эксплуатации также настрой корпоративную почту, домен и резервные копии PostgreSQL.
