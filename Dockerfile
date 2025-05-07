# 1. Base Python image
FROM python:3.11-slim

# 2. Unbuffered output & no pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Install OS libs for WeasyPrint (incl. GObject)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libcairo2 \
      libpango-1.0-0 \
      libgdk-pixbuf2.0-0 \
      libffi-dev \
      shared-mime-info \
      libgirepository1.0-dev \
 && rm -rf /var/lib/apt/lists/*

# 4. Set a stable workdir for Python deps
WORKDIR /app

# 5. Copy & install Python requirements
COPY requirements.txt /app/
RUN pip install --upgrade pip \
 && pip install -r /app/requirements.txt

# 6. Copy your entire repo into /app
#    This brings in the WasslPoint/ folder (with manage.py inside it)
COPY . /app

# 7. Switch into the directory that actually holds manage.py
WORKDIR /app/WasslPoint

# 8. (Optional) Collect static files now
RUN python manage.py collectstatic --noinput

# 9. Expose the port your app will bind to
EXPOSE 8000

# 10. Apply migrations, then launch Gunicorn
CMD python manage.py migrate --noinput \
 && exec gunicorn WasslPoint.wsgi:application --bind 0.0.0.0:8000 --workers 3
