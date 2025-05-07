{
    "$schema":"https://railway.app/railway.schema.json",
    "build":{
        "builder":"NIXPACKS"
    },
    "deploy":{
        "startCommand":"cd WasslPoint && python manage.py migrate &&  pyton manage.py collectstatic --noinput && gunicorn WasslPoint.wsgi"
    }
}