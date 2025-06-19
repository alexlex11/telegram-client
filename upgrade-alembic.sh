#!/bin/bash

echo "Запуск Alembic миграций..."

cd telethonbots
.venv/bin/alembic upgrade head

cd ../api
.venv/bin/alembic upgrade head 