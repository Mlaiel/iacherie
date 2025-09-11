# Advanced Deployment Automation Service
# Intelligent CI/CD and deployment orchestration
# Author: Fahed Mlaiel (mlaiel@live.de) - DevOps Engineer Role

FROM ubuntu:22.04 AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue DevOps Automation - Advanced deployment orchestration"
LABEL version="1.0.0"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install DevOps tools and dependencies
RUN apt-get update && apt-get install -y \
    # Core tools
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    jq \
    yq \
    # Docker tools
    docker.io \
    docker-compose \
    # Kubernetes tools
    kubectl \
    helm \
    # Monitoring tools
    prometheus-node-exporter \
    # Security tools
    gnupg2 \
    ca-certificates \
    # Build tools
    make \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform
RUN wget -O terraform.zip https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip && \
    unzip terraform.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform.zip

# Install Ansible
RUN pip3 install --no-cache-dir \
    ansible \
    ansible-runner \
    docker \
    kubernetes \
    pyyaml \
    requests \
    boto3 \
    azure-cli \
    google-cloud-sdk

# Security: Create dedicated DevOps user
RUN groupadd --gid 1000 devops && \
    useradd --uid 1000 --gid devops --shell /bin/bash --create-home devops && \
    usermod -aG docker devops

WORKDIR /app

# Copy DevOps automation scripts and configurations
COPY ./devops/automation/ ./automation/
COPY ./devops/playbooks/ ./playbooks/
COPY ./devops/terraform/ ./terraform/
COPY ./devops/common/ ./common/

# Create necessary directories with proper permissions
RUN mkdir -p \
    /app/deployments \
    /app/backups \
    /app/logs \
    /app/secrets \
    /app/configs \
    && chown -R devops:devops /app \
    && chmod 755 /app \
    && chmod 700 /app/secrets

# Security: Remove package lists and temporary files
RUN rm -rf /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/* \
    && find /app -name "*.pyc" -delete

# Switch to DevOps user
USER devops

# DevOps environment variables
ENV PYTHONPATH=/app \
    SERVICE_NAME=devops_automation \
    DEPLOYMENT_ENV=production \
    AUTOMATION_LEVEL=enterprise

# Health check for DevOps service
HEALTHCHECK --interval=30s --timeout=15s --retries=3 \
    CMD curl -f http://localhost:8000/devops/health || exit 1

EXPOSE 8000

# Start DevOps automation service
CMD ["python3", "-m", "uvicorn", "automation.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--log-level", "info"]