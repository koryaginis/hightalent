#!/bin/sh

# Применяем миграции
alembic -c app/alembic.ini upgrade head

# Стартуем сервер
uvicorn app.main:app --host 0.0.0.0 --port 80 --reload