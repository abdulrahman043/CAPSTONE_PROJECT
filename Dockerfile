# 1. Base image
FROM python:3.11-slim

# 2. Env settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Install WeasyPrint dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libgirepository1.0-dev \
 && rm -rf /var/lib/apt/lists/*

# 4. Set working directory
WORKDIR /app

# 5. Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 6. Copy full project into /app
COPY . .

# 7. Set working directory to where manage.py actually is
WORKDIR /app/WasslPoint

# 8. Create static folder (optional)
RUN mkdir -p /app/WasslPoint/static

# 9. Expose port
EXPOSE 8000

# 10. Run migrate + collectstatic + gunicorn
CMD bash -c "\
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn WasslPoint.wsgi:application --bind 0.0.0.0:8000 --workers 3"
