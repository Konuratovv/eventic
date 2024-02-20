FROM python:3.11

WORKDIR /usr/src/app

EXPOSE 8000

COPY requirements.txt ./

COPY . .

RUN pip install -r requirements.txt

RUN python manage.py collectstatic

RUN python manage.py makemigrations