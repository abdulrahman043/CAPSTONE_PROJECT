FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libgirepository1.0-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

WORKDIR /app/WasslPoint

RUN mkdir -p /app/WasslPoint/static

EXPOSE 8000

CMD bash -c "\
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn WasslPoint.wsgi:application --bind 0.0.0.0:8000 --workers 3"
