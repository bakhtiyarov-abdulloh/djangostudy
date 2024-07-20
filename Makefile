mig:
	  python3 manage.py makemigrations
	  python3 manage.py migrate

celery:
	celery -A core worker -l INFO

beat:
	celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

dumpdata:
	python3 manage.py dumpdata --indent=2 apps.Category > categories.json
	python3 manage.py dumpdata --indent=2 apps.Product > products.json
	python3 manage.py dumpdata --indent=2 apps.User > users.json

loaddata:
	python3 manage.py loaddata categories
	python3 manage.py loaddata products
	python3 manage.py loaddata users



