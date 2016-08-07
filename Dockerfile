FROM python:3.5-slim


ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8


# Install libs
RUN apt-get update && apt-get install -y supervisor \
    nginx \
    build-essential \
    libsqlite3-dev \
    sqlite3 \
    bzip2 \
    libbz2-dev \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# Copy files
RUN mkdir /app
WORKDIR /app

COPY bviewer bviewer
COPY configs/docker/supervisord.conf /etc/supervisor/supervisord.conf
COPY configs/docker/nginx.conf /etc/nginx/sites-enabled/bviewer.conf
COPY manage.py manage.py
COPY requirements.txt requirements.txt


# Setup
RUN rm -f /etc/nginx/sites-enabled/default
RUN rm bviewer/settings/local.py
RUN pip3 install -r requirements.txt


# Define configs
VOLUME /volume/configs
VOLUME /volume/logs
VOLUME /volume/cache
VOLUME /volume/storage

EXPOSE 80 443


# Create run scripts
RUN echo "python3 /app/manage.py migrate --noinput &&\\" >> bviewer.sh
RUN echo "python3 /app/manage.py collectstatic --noinput &&\\" >> bviewer.sh
RUN echo "python3 /app/manage.py gunicorn;" >> bviewer.sh
RUN chmod +x bviewer.sh

RUN echo "cp /volume/configs/app.conf.py /app/bviewer/settings/local.py &&\\" >> start.sh
RUN echo "/usr/bin/supervisord;" >> start.sh
RUN chmod +x start.sh


# Start
CMD "/app/start.sh"