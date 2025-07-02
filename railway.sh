
cd WasselPoint

python manage.py migrate && python manage.py collectstatic --noinput



echo "Starting web process..."
gunicorn WasselPoint.wsgi &
web_pid=$!

wait $worker_pid $web_pid
