# Телемастерская74

Небольшой рабочий сайт мастерской по ремонту техники на Django.

## Возможности
- публичная главная страница с описанием компании, FAQ и контактами;
- форма создания заявки на ремонт;
- регистрация и вход клиента;
- личный кабинет клиента со списком своих заявок;
- автоматическая генерация кода заявки;
- отслеживание статуса по коду;
- панель мастерской для пользователей со `Статусом персонала`:
  - просмотр всех заявок;
  - поиск и фильтрация;
  - изменение статуса;
  - журнал изменений статуса;
  - экспорт заявок в CSV;
  - редактирование;
  - удаление;
- уведомления менеджерам о новых заявках по email;
- антиспам в форме заявки;
- страница политики обработки персональных данных и согласие в форме заявки;
- команда резервного копирования БД;
- светлая и тёмная тема;
- подготовка к локальному запуску и деплою.

## Стек
- Python 3.12+
- Django 5.2 LTS
- PostgreSQL в продакшене
- SQLite локально по умолчанию
- Bootstrap 5.3
- WhiteNoise для статики
- Gunicorn для запуска в продакшене

## Структура БД
### `repairs_status`
- `id`
- `slug`
- `title`
- `sort_order`
- `is_terminal`

### `repairs_repairrequest`
- `id`
- `customer_id`
- `code`
- `customer_name`
- `phone`
- `device`
- `problem_description`
- `status_id`
- `created_at`
- `updated_at`

### `repairs_statuschangelog`
- `id`
- `repair_request_id`
- `old_status_id`
- `new_status_id`
- `changed_by_id`
- `comment`
- `created_at`

### `repairs_managerprofile`
- `id`
- `user_id`
- `full_name`
- `phone`

Таблица пользователей Django (`auth_user`) хранит аккаунты клиентов, менеджеров и администраторов.

## Локальный запуск

### 1. Установить Python
Нужен Python 3.12 или новее.

### 2. Создать виртуальное окружение
```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Создать файл окружения
Скопируйте `.env.example` в `.env`.

Windows:
```bash
copy .env.example .env
```

macOS/Linux:
```bash
cp .env.example .env
```

Для локальной разработки можно оставить `DATABASE_URL` пустым: будет использоваться SQLite.

### 5. Выполнить миграции
```bash
python manage.py migrate
```

После миграций автоматически создаются базовые статусы:
- На рассмотрении
- Заявка принята
- Ожидает очереди
- В работе
- Ремонт выполнен

### 6. Создать администратора
```bash
python manage.py createsuperuser
```

### 7. Запустить сайт
```bash
python manage.py runserver
```

Открыть:
- сайт: http://127.0.0.1:8000/
- вход клиента/менеджера: http://127.0.0.1:8000/accounts/login/
- панель мастерской: http://127.0.0.1:8000/manager/requests/
- встроенная админка Django: http://127.0.0.1:8000/admin/

## Как дать менеджеру доступ
1. Пользователь регистрируется на сайте или создаётся через Django admin.
2. В Django admin откройте пользователя.
3. Поставьте отметку `Статус персонала` / `is_staff = True`.
4. Сохраните.

После этого пользователь входит через обычную страницу входа и получает доступ к панели мастерской.

## Продакшен
В продакшене обязательно:
- задать `DEBUG=False`;
- задать длинный `SECRET_KEY`;
- заполнить `ALLOWED_HOSTS`;
- использовать PostgreSQL;
- включить HTTPS;
- выполнять резервное копирование БД;
- не хранить `.env` в Git;
- использовать отдельного пользователя БД с минимальными правами.

### Email-уведомления и корпоративная почта
Для уведомлений менеджеров заполните переменные:
```env
CONTACT_EMAIL=info@example.ru
DEFAULT_FROM_EMAIL=info@example.ru
MANAGER_NOTIFICATION_EMAILS=manager@example.ru,service@example.ru
EMAIL_HOST=smtp.example.ru
EMAIL_PORT=587
EMAIL_HOST_USER=info@example.ru
EMAIL_HOST_PASSWORD=пароль-или-app-password
EMAIL_USE_TLS=True
```

Если `MANAGER_NOTIFICATION_EMAILS` пустой, сайт попробует отправлять уведомления staff-пользователям, у которых указан email.

### Резервное копирование
Локально или в Shell сервиса можно создать JSON-резервную копию:
```bash
python manage.py backup_database
```

Файлы сохраняются в `backups/`, эта папка не попадает в Git. На продакшене настройте регулярный запуск команды или используйте автоматические backups PostgreSQL у провайдера.

## Деплой на Amvera Cloud: общий порядок
1. Создать репозиторий GitHub и загрузить проект.
2. Создать PostgreSQL в Amvera.
3. Создать Python-приложение в Amvera из GitHub-репозитория.
4. Убедиться, что Amvera использует `amvera.yaml`.
5. Заполнить `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SITE_DOMAIN`.
6. Запустить деплой.
7. После первого запуска создать администратора:
```bash
python3 manage.py createsuperuser
```

Команда запуска уже указана в `amvera.yaml`:
```bash
python3 app.py
```

Скрипт `app.py` выполняет миграции, собирает статику и запускает Gunicorn.
Постоянное хранилище в Amvera указано как `/data`.

Подробная инструкция лежит в `HOSTING_AMVERA_INSTRUCTION.md`.

## Перед реальной эксплуатацией
В коде уже добавлены уведомления о новых заявках, журнал статусов, антиспам, политика персональных данных, CSV-экспорт и команда backup. Перед запуском останется подключить реальный домен, заполнить `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, SMTP-переменные и корпоративную почту.
