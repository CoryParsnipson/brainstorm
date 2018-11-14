web: waitress-serve --port=$PORT slackerparadise.wsgi:application
worker: celery -A slackerparadise worker -l info
