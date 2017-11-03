FROM python:3.6

RUN addgroup pure_adaptor_group
RUN useradd -ms /bin/bash pure_adaptor_user -G pure_adaptor_group

WORKDIR /app
COPY . /app

RUN make deps

RUN python ./certificates/certifi_append.py ./certificates/QuoVadis_Global_SSL_ICA_G2.pem

USER pure_adaptor_user
CMD ["python", "pure_adaptor/pure_adaptor.py"]
