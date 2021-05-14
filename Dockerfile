FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE TMTServer.settings
RUN mkdir -p /app/
WORKDIR /app/

COPY . /app/

RUN pip install django
RUN pip install djangorestframework

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]