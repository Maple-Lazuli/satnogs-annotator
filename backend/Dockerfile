
FROM python:3.10-alpine3.17

RUN apk --update --upgrade add --no-cache  gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev libpq-dev

RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5001
COPY src /opt/app/src
WORKDIR /opt/app/src

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5001"]
