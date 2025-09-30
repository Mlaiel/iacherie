# Jaeger Tracing Service - Distributed tracing
FROM jaegertracing/all-in-one:latest AS production
ENV SPAN_STORAGE_TYPE=elasticsearch
ENV ES_SERVER_URLS=http://elasticsearch:9200
EXPOSE 16686 14268 6831/udp 6832/udp
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD wget --no-verbose --tries=1 --spider http://localhost:16686/ || exit 1