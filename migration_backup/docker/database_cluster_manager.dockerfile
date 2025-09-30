# Database Cluster Management Service
# Advanced database administration and clustering
# Author: Fahed Mlaiel (mlaiel@live.de) - Database Administrator Role

FROM postgres:15 AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Database Cluster Manager - Enterprise database administration"
LABEL version="1.0.0"

# Install additional database tools
USER root
RUN apt-get update && apt-get install -y \
    # Database administration tools
    postgresql-contrib \
    postgresql-client \
    pgbouncer \
    # Backup and recovery tools
    barman \
    pg_dump \
    pg_restore \
    # Monitoring tools
    postgresql-15-pg-stat-statements \
    postgresql-15-pgaudit \
    # Clustering tools
    postgresql-15-repmgr \
    # Python for management scripts
    python3 \
    python3-pip \
    python3-psycopg2 \
    # System tools
    curl \
    wget \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install Python database libraries
RUN pip3 install --no-cache-dir \
    psycopg2-binary \
    sqlalchemy \
    alembic \
    pg_activity \
    pgcli \
    databases[postgresql]

WORKDIR /app

# Copy database management scripts
COPY ./database/cluster/ ./cluster/
COPY ./database/backup/ ./backup/
COPY ./database/monitoring/ ./monitoring/
COPY ./database/common/ ./common/

# Copy configuration files
COPY ./database/configs/postgresql.conf /etc/postgresql/postgresql.conf
COPY ./database/configs/pg_hba.conf /etc/postgresql/pg_hba.conf
COPY ./database/configs/pgbouncer.ini /etc/pgbouncer/pgbouncer.ini

# Create database directories
RUN mkdir -p \
    /app/backups \
    /app/logs \
    /app/scripts \
    /app/configs \
    /var/lib/postgresql/archive \
    && chown -R postgres:postgres /app \
    && chown -R postgres:postgres /var/lib/postgresql/archive

# Setup backup automation
COPY ./database/scripts/backup_scheduler.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/backup_scheduler.sh

# Create database user for management
RUN useradd -r -g postgres -d /home/dbadmin -s /bin/bash -c "Database Administrator" dbadmin || true

# Switch back to postgres user
USER postgres

# Database environment variables
ENV POSTGRES_DB=ainflue_cluster \
    POSTGRES_USER=ainflue_admin \
    POSTGRES_PASSWORD=secure_cluster_password \
    PGDATA=/var/lib/postgresql/data/cluster \
    POSTGRES_INITDB_ARGS="--auth-host=md5" \
    BACKUP_SCHEDULE="0 2 * * *" \
    REPLICATION_USER=replicator \
    SERVICE_NAME=database_cluster_manager

# Health check for database cluster
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD pg_isready -h localhost -p 5432 -U $POSTGRES_USER || exit 1

# Expose PostgreSQL port
EXPOSE 5432

# Custom initialization script
COPY ./database/init/cluster_init.sql /docker-entrypoint-initdb.d/

# Start database cluster with management
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]