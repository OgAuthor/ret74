# Пошаговая инструкция деплоя RET 74 на Render

Эта папка `ForHost` уже очищена для хостинга. В ней нет локальной базы `db.sqlite3`, виртуальных окружений, логов, `staticfiles`, `.env` и кэшей Python.

## 1. Открыть проект в Visual Studio Code

1. Открой Visual Studio Code.
2. Нажми `File` -> `Open Folder`.
3. Выбери папку:

```text
C:\Users\facke\OneDrive\Рабочий стол\Web CODEX\ForHost
```

4. Открой терминал: `Terminal` -> `New Terminal`.

Все дальнейшие команды выполняй именно из папки `ForHost`.

## 2. Проверить проект локально перед загрузкой

Создай виртуальное окружение:

```powershell
py -m venv .venv
```

Активируй его:

```powershell
.\.venv\Scripts\Activate.ps1
```

Если PowerShell не дает активировать окружение, выполни один раз:

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

Выполни миграции локально:

```powershell
python manage.py migrate
```

Проверь проект:

```powershell
python manage.py check
```

Запусти сайт локально:

```powershell
python manage.py runserver
```

Открой:

```text
http://127.0.0.1:8000/
```

Если все открылось, останови сервер в терминале: `Ctrl + C`.

## 3. Создать GitHub-репозиторий

Render удобнее всего деплоить из GitHub.

1. Зайди на GitHub.
2. Нажми `New repository`.
3. Назови репозиторий, например:

```text
ret74-site
```

4. Не добавляй `README`, `.gitignore` или лицензию на GitHub, потому что они уже есть в папке.
5. Нажми `Create repository`.

## 4. Загрузить папку ForHost на GitHub

В терминале VS Code, находясь в `ForHost`, выполни:

```powershell
git init
git add .
git commit -m "Prepare RET 74 for Render hosting"
```

Подключи удаленный репозиторий. Адрес возьми на странице созданного GitHub-репозитория:

```powershell
git remote add origin https://github.com/ТВОЙ-ЛОГИН/ret74-site.git
git branch -M main
git push -u origin main
```

Важно: в GitHub не должны попасть `.env`, `.venv`, `db.sqlite3`, `staticfiles`, логи и кэши. Они уже указаны в `.gitignore`.

Если команда `git` не работает, установи Git for Windows, перезапусти VS Code и повтори команды.

## 5. Создать сервис на Render через Blueprint

1. Зайди на Render.
2. Нажми `New` -> `Blueprint`.
3. Подключи GitHub, если Render попросит доступ.
4. Выбери репозиторий `ret74-site`.
5. Render увидит файл `render.yaml`.
6. Подтверди создание:
   - Web Service `telemaster74`;
   - PostgreSQL Database `telemaster74-db`.

Render сам возьмет команды из `render.yaml`:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
python manage.py migrate
gunicorn telemaster74.wsgi:application --bind 0.0.0.0:$PORT
```

## 6. Заполнить переменные окружения на Render

В Render открой созданный Web Service -> `Environment`.

Обязательные переменные:

```text
DEBUG=False
ALLOWED_HOSTS=telemaster74.onrender.com
CSRF_TRUSTED_ORIGINS=https://telemaster74.onrender.com
SITE_DOMAIN=telemaster74.onrender.com
COMPANY_LEGAL_NAME=RET 74
CONTACT_EMAIL=
DEFAULT_FROM_EMAIL=
MANAGER_NOTIFICATION_EMAILS=
```

`SECRET_KEY` Render сгенерирует сам, потому что это указано в `render.yaml`.

`DATABASE_URL` Render подставит сам из PostgreSQL.

Если Render дал другой адрес сайта, используй именно его вместо `telemaster74.onrender.com`.

## 7. Почта для уведомлений менеджеру

Сайт уже умеет отправлять уведомления о новых заявках, но для реальной отправки нужна SMTP-почта.

Когда будет корпоративная почта, заполни:

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

Если почты пока нет, сайт все равно будет работать. Просто уведомления на email не будут реально уходить.

## 8. Первый деплой

1. В Render открой Web Service `telemaster74`.
2. Перейди во вкладку `Events` или `Logs`.
3. Дождись окончания сборки.
4. Если статус стал `Live`, открой адрес сайта.

Проверь страницы:

```text
/
/zayavka/
/otsledit/
/privacy/
/admin/
```

## 9. Создать администратора сайта

После первого успешного деплоя:

1. Открой Web Service в Render.
2. Найди `Shell`.
3. Выполни:

```bash
python manage.py createsuperuser
```

Создай логин, email и пароль.

После этого зайди:

```text
https://адрес-твоего-сайта/admin/
```

## 10. Выдать доступ менеджеру

Есть два варианта.

Первый вариант: менеджер регистрируется на сайте.

1. Менеджер открывает `/accounts/register/`.
2. Создает аккаунт.
3. Администратор заходит в `/admin/`.
4. Открывает `Пользователи`.
5. Выбирает пользователя менеджера.
6. Ставит галочку `Статус персонала`.
7. Сохраняет.

После этого менеджер сможет открыть:

```text
/manager/requests/
```

Второй вариант: администратор сам создает пользователя через `/admin/` и сразу ставит `Статус персонала`.

## 11. Проверить рабочий сценарий

1. Открой сайт.
2. Перейди в `Оставить заявку`.
3. Заполни форму.
4. Поставь согласие на обработку персональных данных.
5. Реши антиспам-пример.
6. Отправь заявку.
7. Сохрани код заявки.
8. Открой панель менеджера `/manager/requests/`.
9. Проверь, что заявка появилась.
10. Измени статус заявки.
11. Открой страницу статуса заявки и проверь историю статусов.

## 12. Подключить свой домен

Когда будет домен:

1. В Render открой Web Service.
2. Перейди в `Settings` -> `Custom Domains`.
3. Добавь домен, например:

```text
ret74.ru
www.ret74.ru
```

4. Render покажет DNS-записи.
5. В панели регистратора домена добавь эти DNS-записи.
6. Дождись проверки домена и HTTPS-сертификата.
7. В Render обнови переменные:

```text
SITE_DOMAIN=ret74.ru
ALLOWED_HOSTS=ret74.ru,www.ret74.ru,telemaster74.onrender.com
CSRF_TRUSTED_ORIGINS=https://ret74.ru,https://www.ret74.ru,https://telemaster74.onrender.com
CONTACT_EMAIL=info@ret74.ru
DEFAULT_FROM_EMAIL=info@ret74.ru
```

После изменения переменных нажми `Manual Deploy` -> `Deploy latest commit`.

## 13. Резервное копирование

В Render лучше включить автоматические backups у PostgreSQL, если тариф это позволяет.

Также в проекте есть команда:

```bash
python manage.py backup_database
```

Ее можно запускать вручную в Render Shell. Она создаст JSON-копию базы в папке `backups/`.

Важно: для настоящей эксплуатации лучше хранить резервные копии вне сервера, например в облачном хранилище или использовать встроенные PostgreSQL backups у Render.

## 14. Что делать при ошибке деплоя

Открой вкладку `Logs` на Render и смотри последнюю красную ошибку.

Частые причины:

- не заполнен `ALLOWED_HOSTS`;
- неправильно заполнен `CSRF_TRUSTED_ORIGINS`;
- ошибка в SMTP-переменных;
- GitHub загружен не из папки `ForHost`, а из родительской папки с лишними файлами;
- в репозиторий попал `.env` или `db.sqlite3`.

После исправления сделай новый commit и push:

```powershell
git add .
git commit -m "Fix Render deploy settings"
git push
```

Render автоматически начнет новый деплой.

## 15. Мини-чеклист перед запуском клиентам

- сайт открывается по HTTPS;
- форма заявки работает;
- `/privacy/` открывается;
- менеджер видит заявки;
- экспорт CSV работает;
- email-уведомления проверены;
- создан администратор;
- создан менеджер;
- включены backups PostgreSQL;
- домен и корпоративная почта подключены.
