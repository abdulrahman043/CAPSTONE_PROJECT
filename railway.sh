{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "Nixpacks"
  },
  "deploy": {
    "startCommand": "cd WasselPoint && python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn WasselPoint.wsgi:application --bind 0.0.0.0:$PORT"
  }
}
