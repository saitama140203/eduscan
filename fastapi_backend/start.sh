#!/bin/bash
set -e

# Chờ database khởi động (nếu cần)
echo "Waiting for PostgreSQL..."
RETRIES=5
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
  echo "Waiting for PostgreSQL server, $((RETRIES--)) remaining attempts..."
  sleep 2
done

# Chạy migrations
echo "Running database migrations"
alembic upgrade head

# Tạo thư mục uploads nếu chưa tồn tại
mkdir -p uploads
chmod -R 777 uploads

# Kiểm tra môi trường
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Starting FastAPI in development mode"
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Starting FastAPI in production mode"
    exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 --bind 0.0.0.0:8000 --access-logfile - --error-logfile -
fi
