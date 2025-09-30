# Grafana Dashboard Service - Visualization and dashboards
FROM grafana/grafana:latest AS production
ENV GF_SECURITY_ADMIN_PASSWORD=admin
ENV GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
COPY dashboards /etc/grafana/provisioning/dashboards
COPY datasources /etc/grafana/provisioning/datasources
USER grafana
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:3000/api/health || exit 1