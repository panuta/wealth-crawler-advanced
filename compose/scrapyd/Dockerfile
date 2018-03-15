FROM python:3.6-alpine3.6
ENV PYTHONUNBUFFERED 1

# System dependencies
RUN apk add --no-cache \
        tzdata \
        linux-headers \
        build-base \
        ethtool \
        bash \
        libffi-dev \
        openssl-dev \
        libxml2-dev \
        libxslt-dev

# Set Timezone
RUN cp /usr/share/zoneinfo/Asia/Bangkok /etc/localtime
RUN echo "Asia/Bangkok" > /etc/timezone

# Python environments
COPY ./compose/scrapyd/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# scrapyd
RUN mkdir -p /scrapyd/data
COPY ./compose/scrapyd/scrapyd.conf /scrapyd/scrapyd.conf

VOLUME /scrapyd/data
EXPOSE 6800

WORKDIR /scrapyd
CMD ["scrapyd"]
