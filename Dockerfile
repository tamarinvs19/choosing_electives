FROM python:3.10.1

ENV DJANDO_SUPERUSER_PASSWORD=qweqwe

RUN groupadd --gid 1024 emkn \
    && useradd \
        --uid 1024 \
        --gid 1024 \
        --system \
        --create-home \
        --shell /bin/bash \
        emkn

RUN mkdir /opt/emkn
WORKDIR /opt/emkn
 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh

USER 1024

ENTRYPOINT ["/entrypoint.sh"]
