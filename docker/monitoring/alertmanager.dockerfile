# AlertManager Service - Alert routing and notifications
FROM prom/alertmanager:latest AS production
COPY alertmanager.yml /etc/alertmanager/alertmanager.yml
USER nobody
EXPOSE 9093
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD wget --no-verbose --tries=1 --spider http://localhost:9093/-/healthy || exit 1