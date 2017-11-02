FROM python:3.6

RUN apt-get update && apt-get -y install cron

RUN addgroup pure_adaptor_group
RUN useradd -ms /bin/bash pure_adaptor_user -G pure_adaptor_group,crontab
RUN echo "pure_adaptor_user" >> /etc/cron.allow

RUN touch /etc/environment
RUN chown :pure_adaptor_group /etc/environment
RUN chmod g+rw /etc/environment

COPY crontab /etc/cron.d/run-pure-adaptor-cron
RUN chmod 0644 /etc/cron.d/run-pure-adaptor-cron
RUN touch /var/log/cron.log

WORKDIR /app
COPY . /app

RUN make deps

RUN python ./certificates/certifi_append.py ./certificates/QuoVadis_Global_SSL_ICA_G2.pem

CMD printenv >> /etc/environment && cron -f
