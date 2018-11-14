web: waitress-serve --port=$PORT slackerparadise.wsgi:application
worker: celery -A slackerparadise.celery_app worker -l info
