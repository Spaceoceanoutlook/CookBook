# Настройка проекта CookBook

Клонирование репозитория
```bash
git clone git@github.com:Spaceoceanoutlook/CookBook.git
```
Открыть проект в редакторе, в корне проекта создать файл `.env` и добавить следующие переменные (порт должен быть свободный):
```
POSTGRES_USER=user
POSTGRES_PASSWORD=1234
POSTGRES_DB=cookbookdb
POSTGRES_HOST=localhost
POSTGRES_PORT=5435

JWT_SECRET=cookbookismysecret
JWT_EXPIRE_MINUTES=30
REFRESH_EXPIRE_DAYS=7
```
В системе должен быть установлен poetry. 
Для корректной работы приложения, версия python должны быть < 3.14.
Если глобальная версия python >= 3.14, то установить 3.13.0 через pyenv, после чего выполнить
```bash 
poetry env use ~/.pyenv/versions/3.13.0/bin/python
```
Активируем и добавляем полученный путь в Select Interpreter
```bash
poetry env activate
```
Установка библиотек:
```bash 
poetry install
```
Запуск базы данных 
```bash 
docker compose -f docker-compose.dev.yml up -d
```
Применить миграции:
```bash 
alembic upgrade head
```
Запуск приложения:
```bash 
python cookbook/main.py
```
API будет доступен в браузере по `http://127.0.0.1:8000/docs`