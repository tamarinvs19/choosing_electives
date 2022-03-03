FROM python:3.10.1 as build

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

RUN chown -R emkn:emkn /opt/emkn/*

#RUN python manage.py collectstatic --no-input

FROM nginx:1.21.5
COPY --from=build /opt/emkn/static /usr/share/nginx/html/static/electives/static/
COPY nginx.conf /etc/nginx/nginx.conf
