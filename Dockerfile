# 1. Base image
FROM python:3.11-slim

# 2. Keep Python output unbuffered and avoid .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Install OS libs required by WeasyPrint (including GObject)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libcairo2 \
      libpango-1.0-0 \
      libgdk-pixbuf2.0-0 \
      libffi-dev \
      shared-mime-info \
      libgirepository1.0-dev \
 && rm -rf /var/lib/apt/lists/*

# 4. Set working directory
WORKDIR /WasslPoint

# 5. Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# 6. Copy entire project
COPY . .

# 7. (Optional) Pre-collect static files
RUN python manage.py collectstatic --noinput

# 8. Expose the port
EXPOSE 8000

# 9. Migrate and run Gunicorn with your project name
CMD python manage.py migrate --noinput \
 && exec gunicorn WasslPoint.wsgi:application --bind 0.0.0.0:8000 --workers 3
