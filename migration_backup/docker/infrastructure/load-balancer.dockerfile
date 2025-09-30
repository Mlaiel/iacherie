# Load Balancer Service
# Advanced load balancing for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM nginx:alpine AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Load Balancer - Advanced load balancing and reverse proxy"
LABEL version="1.0.0"

# Install additional tools
RUN apk add --no-cache \
    curl \
    wget \
    openssl \
    bash \
    certbot \
    certbot-nginx

# Create nginx user for security
RUN addgroup -g 1000 nginx_user && \
    adduser -D -s /bin/sh -u 1000 -G nginx_user nginx_user

# Copy configuration files
COPY ./config/nginx/ /etc/nginx/
COPY ./config/ssl/ /etc/ssl/certs/
COPY ./scripts/nginx/ /usr/local/bin/

# Create necessary directories
RUN mkdir -p /var/log/nginx \
             /var/cache/nginx \
             /var/run/nginx \
             /etc/nginx/conf.d \
             /etc/nginx/sites-enabled \
             /etc/nginx/sites-available \
             /usr/share/nginx/html/health && \
    chown -R nginx_user:nginx_user /var/log/nginx \
                                   /var/cache/nginx \
                                   /var/run/nginx \
                                   /usr/share/nginx/html

# Copy custom nginx configuration
COPY ./config/nginx.conf /etc/nginx/nginx.conf
COPY ./config/sites/ /etc/nginx/sites-available/
COPY ./config/ssl.conf /etc/nginx/conf.d/ssl.conf
COPY ./config/gzip.conf /etc/nginx/conf.d/gzip.conf
COPY ./config/security.conf /etc/nginx/conf.d/security.conf

# Create health check endpoint
RUN echo '{"status":"healthy","service":"load_balancer","timestamp":"'$(date -Iseconds)'"}' > /usr/share/nginx/html/health/index.json

# Copy startup script
COPY ./scripts/start-nginx.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-nginx.sh

# Set environment variables
ENV NGINX_USER=nginx_user
ENV NGINX_WORKER_PROCESSES=auto
ENV NGINX_WORKER_CONNECTIONS=1024
ENV NGINX_KEEPALIVE_TIMEOUT=65
ENV NGINX_CLIENT_MAX_BODY_SIZE=50m

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Expose ports
EXPOSE 80 443

# Switch to non-root user
USER nginx_user

# Default command
CMD ["start-nginx.sh"]