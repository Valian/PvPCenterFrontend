FROM python:2.7.9

COPY . ./opt/PvpCenterFrontend
WORKDIR ./opt/PvpCenterFrontend

ENV FLASK_ENV vagrant

RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get update
RUN apt-get install -y nodejs
RUN apt-get install -y npm
RUN npm install
RUN npm install -g grunt-cli bower less coffee-script
RUN bower install
RUN pip install -r requirements/prod.txt
RUN grunt dev
RUN python run_app.py

EXPOSE 5000

CMD ["python", "run_app.py"]
