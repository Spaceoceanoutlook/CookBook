# Настройка проекта CookBook

Клонирование репозитория
```bash
git clone git@github.com:Spaceoceanoutlook/CookBook.git
```
Открыть проект в редакторе, в корне проекта создать файл `.env` и добавить следующие переменные:
```
POSTGRES_USER=user
POSTGRES_PASSWORD=1234
POSTGRES_DB=cookbookdb
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```
Для создание виртуального окружения и установки библиотек:
```bash 
poetry install
```
Для активации виртуального окружения:
```bash 
poetry env activate
```
Запуск Postgres
```bash 
docker compose -f "docker-compose.dev.yml" up -d
```
Применить миграции:
```bash 
alembic upgrade head
```
Запуск приложения:
```bash 
cd cookbook
python main.py
```
API будет доступен в браузере по `http://127.0.0.1:8000/docs`