# 1. Use a slim Python base image
FROM python:3.11-slim

# 2. Make sure Python output is unbuffered & no .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Install OS libraries for WeasyPrint (Cairo, Pango, GObject, etc.)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libcairo2 \
      libpango-1.0-0 \
      libgdk-pixbuf2.0-0 \
      libffi-dev \
      shared-mime-info \
      libgirepository1.0-dev \
 && rm -rf /var/lib/apt/lists/*

# 4. Set the working directory inside the container
WORKDIR /app

# 5. Copy and install Python dependencies first (for better layer caching)
COPY requirements.txt /app/
RUN pip install --upgrade pip \
 && pip install -r /app/requirements.txt

# 6. Copy the rest of your project code into /app
COPY . /app

# 7. Verify manage.py is present (optional debug step)
#    RUN ls -l /app

# 8. Pre-collect static files (optional; you can also do this at runtime)
RUN python manage.py collectstatic --noinput

# 9. Expose the port your app will run on
EXPOSE 8000

# 10. Final command: apply migrations & launch Gunicorn
CMD python manage.py migrate --noinput \
 && exec gunicorn WasslPoint.wsgi:application --bind 0.0.0.0:8000 --workers 3
