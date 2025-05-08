# 1. Base Python image
FROM python:3.11-slim

# 2. Unbuffered output & no pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Install OS libs for WeasyPrint (incl. GObject & Pango FreeType)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
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

# 5. Copy & install Python deps
COPY requirements.txt /app/
RUN pip install --upgrade pip \
 && pip install -r /app/requirements.txt

# 6. Copy your code (brings in WasslPoint/ with manage.py)
COPY . /app

# 7. Switch into the directory holding manage.py
WORKDIR /app/WasslPoint

# 8. (Optional) Pre-collect static files
RUN python manage.py collectstatic --noinput

# 9. Expose port
EXPOSE 8000

# 10. Migrate & start Gunicorn
CMD python manage.py migrate --noinput \
 && exec gunicorn WasslPoint.wsgi:application --bind 0.0.0.0:8000 --workers 3
