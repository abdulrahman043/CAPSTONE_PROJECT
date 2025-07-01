# 1. Base Python image
FROM python:3.11-slim

# 2. Environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Install OS dependencies (WeasyPrint needs these)
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

# 6. Copy entire project
COPY . .

# 7. Ensure static folder exists to avoid warnings
RUN mkdir -p /app/static

# 8. Expose port for Gunicorn
EXPOSE 8000

# 9. Runtime command
CMD bash -c "\
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn WasslPoint.wsgi:application --bind 0.0.0.0:8000 --workers 3"
