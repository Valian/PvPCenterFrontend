FROM python:2.7.9

COPY . ./pvpc-frontend
WORKDIR ./pvpc-frontend

ENV FLASK_ENV vagrant

RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get update && apt-get install -y nodejs && apt-get install -y npm
RUN npm install && npm install -g grunt-cli bower less coffee-script && bower install && pip install -r requirements/prod.txt
RUN grunt dev

EXPOSE 5000

CMD ["python", "run_app.py"]
