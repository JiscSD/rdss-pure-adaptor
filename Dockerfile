FROM python:3.6

COPY startup.sh /
COPY . /app
WORKDIR /app

RUN apt-get update && apt-get -y install cron && \
chmod 0744 /startup.sh && \
make deps && \
python ./certificates/certifi_append.py ./certificates/QuoVadis_Global_SSL_ICA_G2.pem && \
apt-get -y autoclean && apt-get -y autoremove && \
apt-get -y purge $(dpkg --get-selections | grep deinstall | sed s/deinstall//g) && \
rm -rf /var/lib/apt/lists/*

CMD printenv >> /etc/environment && /startup.sh
