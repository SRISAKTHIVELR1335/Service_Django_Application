FROM nginx:stable

COPY ops/nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443
