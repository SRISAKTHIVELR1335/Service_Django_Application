# Backend Dockerfile for NIRIX Diagnostics
FROM python:3.11-slim

WORKDIR /app

# Install system deps (e.g., MySQL client for health checks)
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

COPY backend/ ./backend/
COPY pyproject.toml uv.lock ./ 

# Install dependencies with pip as a simple default
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r backend/requirements.txt || true

ENV FLASK_APP=backend.app
ENV DATABASE_URL=mysql+pymysql://nirix_user:nirix_password@mysql:3306/nirix_diagnostics

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:create_app()"]
