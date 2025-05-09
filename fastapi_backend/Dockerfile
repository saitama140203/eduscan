FROM python:3.11-slim

WORKDIR /app

# Cài đặt các dependencies của hệ thống
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt Python dependencies
COPY requirements /app/requirements/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/prod.txt

# Thiết lập biến môi trường
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Ho_Chi_Minh

# Copy source code
COPY . /app/

# Tạo thư mục chứa logs và uploads
RUN mkdir -p /app/logs /app/uploads \
    && chmod -R 755 /app/logs /app/uploads

# Kiểm tra lỗi với alembic và tạo database migrations nếu cần
RUN alembic check && echo "Alembic configuration is valid"

# Script khởi động
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Khởi động server với script khi container chạy
CMD ["/app/start.sh"]