FROM python:3.6

ARG api_url
ENV API_URL ${api_url}

ARG api_version
ENV API_VERSION ${api_version}

ARG api_key
ENV API_KEY ${api_key}

ARG upload_bucket
ENV UPLOAD_BUCKET ${upload_bucket}

WORKDIR /app
ADD . /app

RUN make deps

CMD ["python", "./pure_adaptor/pure_adaptor.py"]
