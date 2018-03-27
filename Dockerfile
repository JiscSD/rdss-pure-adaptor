FROM python:3.6

RUN apt-get update && apt-get -y install cron

COPY startup.sh /
RUN chmod 0744 /startup.sh
WORKDIR /app
COPY . /app

RUN make deps

RUN python ./certificates/certifi_append.py ./certificates/QuoVadis_Global_SSL_ICA_G2.pem

CMD printenv >> /etc/environment && /startup.sh
