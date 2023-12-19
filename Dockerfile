FROM python

WORKDIR /usr/src/app

EXPOSE 8000

COPY requirements.txt ./

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN ./manage.py collectstatic