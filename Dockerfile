FROM python:3.6

WORKDIR /app
ADD . /app

RUN make deps

CMD ["python", "./pure_adaptor/pure_adaptor.py"]
