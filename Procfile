release: python3 manage.py migrate && python3 manage.py remove_duplicates
web: gunicorn coresight.wsgi --log-file -