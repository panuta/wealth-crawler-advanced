FROM python:2.7-alpine3.6
ENV PYTHONUNBUFFERED 1

# System dependencies
RUN apk add --no-cache \
        tzdata \
        build-base \
        bash \
        git \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        openssl-dev \
        openssh \
        curl \
        curl-dev \
        python3 \
        python3-dev \
        supervisor

# NOTE: 'curl-dev' see -> https://github.com/JJ/alpine-perl6/issues/3

# Set Timezone
RUN cp /usr/share/zoneinfo/Asia/Bangkok /etc/localtime
RUN echo "Asia/Bangkok" > /etc/timezone

# Install Python 3 along side Python 2
RUN echo 'alias python=python3' >> ~/.bashrc
RUN echo 'alias pip=pip3' >> ~/.bashrc

COPY ./compose/server/production/requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Git
VOLUME /root/.ssh

# gunicorn
RUN mkdir /app
COPY ./compose/server/supervisor/gunicorn.ini /etc/supervisor.d/gunicorn.ini

# celery
COPY ./compose/server/supervisor/celery_worker.ini /etc/supervisor.d/celery_worker.ini
COPY ./compose/server/supervisor/celery_beat.ini /etc/supervisor.d/celery_beat.ini

# Place to keep server database
VOLUME /data

VOLUME /app
EXPOSE 8000

CMD ["supervisord", "--nodaemon", "--configuration", "/etc/supervisord.conf"]
