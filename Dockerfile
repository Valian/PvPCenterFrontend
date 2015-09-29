FROM python:2.7.9

COPY . ./pvpc-frontend
WORKDIR ./pvpc-frontend

ENV FLASK_ENV vagrant

RUN rm /bin/sh && ln -s /bin/bash /bin/sh \
    && apt-get update \
    && apt-get install -y nodejs \
    && apt-get install -y npm \
    && ln -s /usr/bin/nodejs /usr/bin/node \
    && npm install \
    && npm install -g grunt-cli bower less coffee-script \
    && bower install --allow-root \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && grunt dev

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "localhost:5000", "run_app:app"]
