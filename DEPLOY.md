# Деплой RET 74 на Render

Эта инструкция рассчитана на Render, потому что проект уже содержит `render.yaml`.

## 1. Подготовить GitHub

1. Создай репозиторий на GitHub.
2. Загрузи туда проект.
3. Убедись, что в репозиторий не попали `.env`, `.venv`, `db.sqlite3`, `staticfiles`.

Они уже добавлены в `.gitignore`.

## 2. Создать сервис через Blueprint

1. Зайди в Render.
2. Нажми `New` -> `Blueprint`.
3. Выбери GitHub-репозиторий с проектом.
4. Render прочитает `render.yaml` и предложит создать:
   - Web Service `telemaster74`;
   - PostgreSQL Database `telemaster74-db`.

## 3. Переменные окружения

В `render.yaml` уже указаны основные переменные:

- `DEBUG=False`
- `SECRET_KEY` генерируется Render автоматически
- `DATABASE_URL` берется из PostgreSQL
- `ALLOWED_HOSTS` нужно заполнить вручную
- `CSRF_TRUSTED_ORIGINS` нужно заполнить вручную
- `SITE_DOMAIN` нужно заполнить своим доменом
- `CONTACT_EMAIL`, `DEFAULT_FROM_EMAIL`, `MANAGER_NOTIFICATION_EMAILS` нужны для корпоративной почты и уведомлений
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` нужны для SMTP

Для домена Render укажи:

```text
ALLOWED_HOSTS=имя-сервиса.onrender.com
CSRF_TRUSTED_ORIGINS=https://имя-сервиса.onrender.com
```

Если подключишь свой домен:

```text
ALLOWED_HOSTS=example.ru,www.example.ru,имя-сервиса.onrender.com
CSRF_TRUSTED_ORIGINS=https://example.ru,https://www.example.ru,https://имя-сервиса.onrender.com
```

Проект также автоматически подхватывает `RENDER_EXTERNAL_HOSTNAME`, если Render его передает.

Для корпоративной почты укажи SMTP-параметры почтового провайдера:

```text
CONTACT_EMAIL=info@example.ru
DEFAULT_FROM_EMAIL=info@example.ru
MANAGER_NOTIFICATION_EMAILS=manager@example.ru
EMAIL_HOST=smtp.example.ru
EMAIL_PORT=587
EMAIL_HOST_USER=info@example.ru
EMAIL_HOST_PASSWORD=пароль-или-app-password
EMAIL_USE_TLS=True
```

Если `MANAGER_NOTIFICATION_EMAILS` не заполнен, уведомления будут отправляться staff-пользователям с заполненным email.

## 4. Миграции

В `render.yaml` добавлен:

```yaml
preDeployCommand: python manage.py migrate
```

Render рекомендует pre-deploy command для миграций. Если на выбранном тарифе эта команда недоступна, после первого деплоя открой Shell сервиса и выполни:

```bash
python manage.py migrate
```

## 5. Создать администратора

После первого успешного деплоя открой Shell сервиса на Render и выполни:

```bash
python manage.py createsuperuser
```

После этого админка будет доступна по адресу:

```text
https://твой-домен/admin/
```

## 6. Выдать права менеджера

1. Клиент регистрируется на сайте.
2. Администратор заходит в `/admin/`.
3. Открывает `Пользователи`.
4. Выбирает нужный аккаунт.
5. Ставит галочку `Статус персонала`.
6. Сохраняет.

После этого пользователь увидит доступ к панели мастерской.

## 7. Проверка после деплоя

Проверь страницы:

- `/`
- `/zayavka/`
- `/accounts/register/`
- `/accounts/login/`
- `/admin/`

Создай тестовую заявку и проверь, что она видна в админке и панели мастерской.

## 8. Что уже добавлено для реальной эксплуатации

- уведомления менеджеру о новой заявке через SMTP;
- журнал изменений статуса в карточке заявки и Django admin;
- антиспам в публичной форме заявки;
- политика обработки персональных данных по адресу `/privacy/`;
- обязательное согласие с политикой перед отправкой заявки;
- экспорт заявок в CSV в панели мастерской;
- команда резервного копирования:

```bash
python manage.py backup_database
```

Для Render/PostgreSQL также включи автоматические бэкапы у провайдера или настрой регулярный запуск backup-команды по расписанию.

## 9. Домен

1. Добавь домен в Render: `Settings` -> `Custom Domains`.
2. Пропиши DNS-записи, которые покажет Render.
3. После выпуска HTTPS-сертификата заполни:

```text
SITE_DOMAIN=example.ru
ALLOWED_HOSTS=example.ru,www.example.ru,имя-сервиса.onrender.com
CSRF_TRUSTED_ORIGINS=https://example.ru,https://www.example.ru,https://имя-сервиса.onrender.com
```
