RUN python ./manage.py makemigrations
RUN python ./manage.py migrate
RUN python ./manage.py collectstatic