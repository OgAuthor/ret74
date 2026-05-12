# Пошаговая инструкция деплоя RET 74 на Amvera Cloud

Эта инструкция написана для папки `ForHost`. В ней лежит чистая версия сайта для хостинга: без `.env`, локальной базы `db.sqlite3`, виртуальных окружений, логов, `staticfiles` и Python-кэшей.

## 1. Что уже подготовлено

В папке `ForHost` есть все, что нужно для Amvera:

```text
manage.py
requirements.txt
amvera.yaml
app.py
repairs/
telemaster74/
templates/
static/
```

Файл `amvera.yaml` говорит Amvera:

```yaml
meta:
  environment: python
  toolchain:
    name: pip
    version: 3.12

build:
  requirementsPath: requirements.txt
  useCache: true

run:
  command: python3 app.py
  persistenceMount: /data
  containerPort: 80
```

То есть Amvera сама установит зависимости из `requirements.txt`, а при запуске вызовет `app.py`. Скрипт выполнит миграции, соберет статику и запустит сайт через Gunicorn.

## 2. Открыть проект в Visual Studio Code

1. Открой Visual Studio Code.
2. Нажми `File` -> `Open Folder`.
3. Выбери папку:

```text
C:\Users\facke\OneDrive\Рабочий стол\Web CODEX\ForHost
```

4. Открой терминал: `Terminal` -> `New Terminal`.

Важно: команды Git выполняй именно из папки `ForHost`, не из родительской папки `Web CODEX`.

## 3. Проверить проект локально

Если локально уже проверял, этот раздел можно пропустить.

Создай виртуальное окружение:

```powershell
py -m venv .venv
```

Активируй его:

```powershell
.\.venv\Scripts\Activate.ps1
```

Если PowerShell не дает активировать окружение:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Потом снова:

```powershell
.\.venv\Scripts\Activate.ps1
```

Установи зависимости:

```powershell
pip install -r requirements.txt
```

Создай локальный `.env`:

```powershell
copy .env.example .env
```

Выполни миграции:

```powershell
python manage.py migrate
```

Проверь проект:

```powershell
python manage.py check
```

Запусти сайт:

```powershell
python manage.py runserver
```

Открой:

```text
http://127.0.0.1:8000/
```

Остановить сервер: `Ctrl + C`.

## 4. Загрузить изменения в GitHub

Ты уже создал репозиторий:

```text
https://github.com/OgAuthor/ret74.git
```

После перехода с Render на Amvera надо загрузить новые файлы: `amvera.yaml`, `app.py`, новую инструкцию и удаление `render.yaml`.

В терминале VS Code из папки `ForHost` выполни:

```powershell
git status
git add .
git commit -m "Switch hosting config to Amvera Cloud"
git push
```

Если Git скажет `nothing to commit`, значит изменения уже отправлены или не были изменены.

## 5. Зарегистрироваться в Amvera Cloud

1. Открой сайт Amvera Cloud:

```text
https://amvera.ru/
```

2. Зарегистрируйся или войди в аккаунт.
3. Пополни баланс, если сервис попросит. Amvera принимает оплату российскими картами.

## 6. Создать PostgreSQL в Amvera

Сначала лучше создать базу, потом приложение.

1. В панели Amvera нажми создание нового сервиса/базы данных.
2. Выбери `PostgreSQL`.
3. Создай базу для проекта.
4. Сохрани данные подключения:
   - host;
   - port;
   - database;
   - user;
   - password.

Для приложения понадобится переменная `DATABASE_URL`.

Формат такой:

```text
postgres://USER:PASSWORD@HOST:PORT/DBNAME
```

Пример:

```text
postgres://ret74_user:super-password@postgres-host:5432/ret74_db
```

Важно: используй внутренний host PostgreSQL из Amvera, если база и приложение находятся внутри Amvera. Так соединение будет быстрее и безопаснее.

## 7. Создать приложение в Amvera

1. В панели Amvera нажми создать новое приложение.
2. Выбери деплой из GitHub/Git-репозитория.
3. Подключи репозиторий:

```text
https://github.com/OgAuthor/ret74.git
```

4. Выбери ветку:

```text
main
```

5. Проверь, что Amvera видит файл:

```text
amvera.yaml
```

6. Создай приложение.

## 8. Заполнить переменные окружения в Amvera

В настройках приложения найди раздел переменных окружения.

Минимально нужно заполнить:

```text
DEBUG=False
SECRET_KEY=сюда-длинный-случайный-секрет
DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DBNAME
ALLOWED_HOSTS=домен-приложения.amvera.io
CSRF_TRUSTED_ORIGINS=https://домен-приложения.amvera.io
SITE_DOMAIN=домен-приложения.amvera.io
COMPANY_LEGAL_NAME=RET 74
```

`SECRET_KEY` можно сгенерировать локально в VS Code:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Скопируй результат в переменную `SECRET_KEY` в Amvera.

## 9. Переменные для почты

Если корпоративной почты пока нет, этот блок можно оставить пустым. Сайт будет работать, но email-уведомления менеджеру не будут отправляться.

Когда почта будет готова, добавь:

```text
CONTACT_EMAIL=info@твой-домен.ru
DEFAULT_FROM_EMAIL=info@твой-домен.ru
MANAGER_NOTIFICATION_EMAILS=manager@твой-домен.ru
EMAIL_HOST=smtp.твой-почтовый-сервис
EMAIL_PORT=587
EMAIL_HOST_USER=info@твой-домен.ru
EMAIL_HOST_PASSWORD=пароль-или-app-password
EMAIL_USE_TLS=True
```

Если менеджеров несколько:

```text
MANAGER_NOTIFICATION_EMAILS=manager1@твой-домен.ru,manager2@твой-домен.ru
```

## 10. Запустить деплой

1. Нажми запуск сборки/деплоя в Amvera.
2. Открой логи приложения.
3. Дождись успешного запуска.

Во время запуска должны выполниться команды из `amvera.yaml`:

```bash
python3 app.py
```

В интерфейсе Amvera также заполни:

```text
persistenceMount=/data
```

А внутри `app.py` выполняются:

```bash
python3 manage.py migrate
python3 manage.py collectstatic --noinput
gunicorn telemaster74.wsgi:application --bind 0.0.0.0:80
```

Если деплой успешный, Amvera даст ссылку на сайт.

## 11. Что проверить после первого запуска

Открой страницы:

```text
/
/zayavka/
/otsledit/
/privacy/
/admin/
```

Проверь:

- главная страница открывается;
- форма заявки открывается;
- политика персональных данных открывается;
- страница админки открывается;
- нет ошибки `DisallowedHost`;
- нет ошибки подключения к базе.

## 12. Создать администратора

В Amvera открой консоль/терминал приложения, если она доступна.

Выполни:

```bash
python3 manage.py createsuperuser
```

Создай логин, email и пароль.

Потом открой:

```text
https://домен-приложения.amvera.io/admin/
```

Войди под созданным администратором.

Если консоли в тарифе нет, можно временно добавить отдельную команду создания суперпользователя через переменные окружения или management command, но сначала попробуй штатную консоль Amvera.

## 13. Выдать доступ менеджеру

Вариант 1: менеджер сам регистрируется.

1. Менеджер открывает:

```text
/accounts/register/
```

2. Создает аккаунт.
3. Администратор входит в `/admin/`.
4. Открывает `Пользователи`.
5. Выбирает аккаунт менеджера.
6. Ставит галочку `Статус персонала`.
7. Сохраняет.

После этого менеджер сможет открыть:

```text
/manager/requests/
```

Вариант 2: администратор сам создает пользователя через `/admin/` и сразу ставит `Статус персонала`.

## 14. Проверить рабочий сценарий

1. Открой сайт как обычный клиент.
2. Перейди в `Оставить заявку`.
3. Заполни форму.
4. Поставь согласие на обработку персональных данных.
5. Реши антиспам-пример.
6. Отправь заявку.
7. Сохрани код заявки.
8. Войди как менеджер.
9. Открой:

```text
/manager/requests/
```

10. Проверь, что заявка появилась.
11. Измени статус заявки.
12. Открой страницу статуса заявки.
13. Проверь, что история статусов отображается.

## 15. Подключить свой домен

Когда будет домен:

1. В Amvera открой настройки домена приложения.
2. Добавь домен, например:

```text
ret74.ru
www.ret74.ru
```

3. Amvera покажет DNS-записи.
4. В панели регистратора домена добавь эти DNS-записи.
5. Дождись проверки домена и HTTPS.
6. Обнови переменные окружения:

```text
SITE_DOMAIN=ret74.ru
ALLOWED_HOSTS=ret74.ru,www.ret74.ru,домен-приложения.amvera.io
CSRF_TRUSTED_ORIGINS=https://ret74.ru,https://www.ret74.ru,https://домен-приложения.amvera.io
CONTACT_EMAIL=info@ret74.ru
DEFAULT_FROM_EMAIL=info@ret74.ru
```

7. Перезапусти приложение.

## 16. Резервное копирование

Для реальной эксплуатации включи резервные копии PostgreSQL в Amvera, если они доступны на выбранном тарифе.

В проекте также есть команда:

```bash
python3 manage.py backup_database
```

Она создает JSON-копию базы в папке `backups/`.

Важно: backups лучше хранить вне контейнера приложения. Контейнер может пересоздаваться, поэтому локальная папка `backups/` не должна быть единственным местом хранения копий.

## 17. Частые ошибки

### Ошибка `DisallowedHost`

Нужно правильно заполнить `ALLOWED_HOSTS`.

Пример:

```text
ALLOWED_HOSTS=ret74.ru,www.ret74.ru,домен-приложения.amvera.io
```

### Ошибка CSRF

Нужно правильно заполнить `CSRF_TRUSTED_ORIGINS`.

Пример:

```text
CSRF_TRUSTED_ORIGINS=https://ret74.ru,https://www.ret74.ru,https://домен-приложения.amvera.io
```

### Ошибка подключения к базе

Проверь `DATABASE_URL`.

Формат должен быть:

```text
postgres://USER:PASSWORD@HOST:PORT/DBNAME
```

Если в пароле есть специальные символы `@`, `:`, `/`, `#`, лучше поменять пароль на простой или URL-кодировать символы.

### Статика не загружается

Проверь логи команды:

```bash
python3 manage.py collectstatic --noinput
```

Она запускается автоматически через `amvera.yaml`.

### Email не отправляется

Проверь:

- `EMAIL_HOST`;
- `EMAIL_PORT`;
- `EMAIL_HOST_USER`;
- `EMAIL_HOST_PASSWORD`;
- `EMAIL_USE_TLS`;
- `DEFAULT_FROM_EMAIL`;
- `MANAGER_NOTIFICATION_EMAILS`.

## 18. Мини-чеклист перед запуском клиентам

- сайт открывается по HTTPS;
- заявка создается;
- `/privacy/` открывается;
- менеджер видит заявки;
- история статусов работает;
- экспорт CSV работает;
- email-уведомления проверены;
- создан администратор;
- создан менеджер;
- PostgreSQL подключен через `DATABASE_URL`;
- backups PostgreSQL включены или настроены;
- домен и корпоративная почта подключены.

## 19. Полезные официальные ссылки

- Amvera Cloud: https://amvera.ru/
- Python pip окружение в Amvera: https://docs.amvera.ru/applications/environments/python-pip.html
- Переменные окружения: https://docs.amvera.ru/applications/configuration/variables.html
- PostgreSQL: https://docs.amvera.ru/databases/postgreSQL.html
- Пополнение баланса: https://docs.amvera.ru/general/topup.html
