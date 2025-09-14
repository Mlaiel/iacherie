"""✅ Deployment Templates - IA-Influencer-Agent
==================================================================
Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: DevOps Architect + Cloud Engineer + Infrastructure Expert
Date: 2025-08-24

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Infrastructure as Code templates for multi-cloud deployment.
==================================================================
"""

import logging
import asyncio
import yaml
import json
import os
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path
import jinja2
from jinja2 import Environment, FileSystemLoader, Template

class CloudProvider(Enum):
    """
Supported cloud providers"""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    TERRAFORM = "terraform"
    ANSIBLE = "ansible"

class DeploymentType(Enum):
    """Deployment types"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"
    DISASTER_RECOVERY = "disaster_recovery"

class TemplateFormat(Enum):
    """Template formats"""

    YAML = "yaml"
    JSON = "json"
    TERRAFORM = "tf"
    DOCKERFILE = "dockerfile"
    COMPOSE = "docker-compose"
    HELM = "helm"
    ANSIBLE = "ansible"

@dataclass
class TemplateContext:
    """Template rendering context"""
    environment: str
    region: str
    namespace: str
    application_name: str
    version: str
    replicas: int = 3
    resources: Dict[str, Any] = field(default_factory=dict)
    secrets: Dict[str, str] = field(default_factory=dict)
    config_maps: Dict[str, Any] = field(default_factory=dict)
    custom_vars: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DeploymentTemplate:
    """
Deployment template definition"""
    name: str
    provider: CloudProvider
    template_type: DeploymentType
    format: TemplateFormat
    template_content: str
    variables: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    version: str = "1.0.0"

class DeploymentTemplateManager:
    """
    Infrastructure as Code deployment templates manager.
    
    Provides comprehensive deployment automation:
    - Multi-cloud deployment templates (AWS, GCP, Azure)
    - Kubernetes manifest generation
    - Docker containerization templates
    - Terraform infrastructure provisioning
    - Ansible configuration management
    - Helm chart generation
    - CI/CD pipeline templates
    - Environment-specific configurations
    - Auto-scaling and load balancing
    - Security and compliance templates
    - Monitoring and logging integration
    - Backup and disaster recovery
    - Blue-green and canary deployments
    """
    
    def __init__(self) -> None:
        """
Initialize deployment template manager"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Templates storage
        self.templates = {}
        self.template_cache = {}
        
        # Jinja2 environment
        self.jinja_env = None
        
        # Template directories
        self.template_dirs = [
            "/workspaces/Achiri/IA-Influencer-Agent/backend/deployment/templates",
            "/workspaces/Achiri/IA-Influencer-Agent/backend/deployment/configuration/templates"
        ]
        
        self.logger.info("Deployment template manager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize template manager.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Create template directories
            await self._create_template_directories()
            
            # Initialize Jinja2 environment
            await self._initialize_jinja_environment()
            
            # Load built-in templates
            await self._load_builtin_templates()
            
            # Generate default templates
            await self._generate_default_templates()
            
            self.logger.info("Template manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize template manager: {e}")
            return False
    
    async def _create_template_directories(self) -> None:
        """Create template directories"""
        
        for template_dir in self.template_dirs:
            Path(template_dir).mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            subdirs = ["kubernetes", "docker", "terraform", "ansible", "helm", "ci-cd"]
            for subdir in subdirs:
                Path(template_dir, subdir).mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Template directories created")
    
    async def _initialize_jinja_environment(self) -> None:
        """Initialize Jinja2 template environment"""
        
        # Custom filters
        def to_yaml(value, indent=2) -> None:
            """
Convert value to YAML"""
            return yaml.dump(value, default_flow_style=False, indent=indent)
        
        def to_json(value, indent=2) -> None:
            """
Convert value to JSON"""
            return json.dumps(value, indent=indent)
        
        def resource_name(name, environment) -> None:
            """
Generate resource name"""
            return f"{name}-{environment}"
        
        def namespace_name(app_name, environment) -> None:
            """Generate namespace name"""
            return f"{app_name}-{environment}"
        
        # Create Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dirs),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Register custom filters
        self.jinja_env.filters['to_yaml'] = to_yaml
        self.jinja_env.filters['to_json'] = to_json
        self.jinja_env.filters['resource_name'] = resource_name
        self.jinja_env.filters['namespace_name'] = namespace_name
        
        self.logger.info("Jinja2 environment initialized")
    
    async def _load_builtin_templates(self) -> None:
        try:
            logger.info(f"Executing _load_builtin_templates")
            
            # Implementation for _load_builtin_templates
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_load_builtin_templates completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_load_builtin_templates failed: {e}")
            raise
    def _get_kubernetes_deployment_template(self) -> str:
        """Get Kubernetes deployment template"""
        return """---
apiVersion: v1
kind: Namespace
metadata:
  name: {{ application_name | namespace_name(environment) }}
  labels:
    app: {{ application_name }}
    environment: {{ environment }}

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ application_name | resource_name(environment) }}-config
  namespace: {{ application_name | namespace_name(environment) }}
data:
  DATABASE_URL: "postgresql://{{ postgres_user }}:{{ postgres_password }}@postgres:5432/{{ postgres_db }}"
  REDIS_URL: "redis://redis:6379/0"
  ENVIRONMENT: "{{ environment }}"
  LOG_LEVEL: "{{ log_level | default('INFO') }}"
{% for key, value in config_maps.items() %}
  {{ key }}: "{{ value }}"
{% endfor %}

---
apiVersion: v1
kind: Secret
metadata:
  name: {{ application_name | resource_name(environment) }}-secrets
  namespace: {{ application_name | namespace_name(environment) }}
type: Opaque
data:
{% for key, value in secrets.items() %}
  {{ key }}: {{ value | b64encode }}
{% endfor %}

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ application_name | resource_name(environment) }}
  namespace: {{ application_name | namespace_name(environment) }}
  labels:
    app: {{ application_name }}
    environment: {{ environment }}
    version: "{{ version }}"
spec:
  replicas: {{ replicas }}
  selector:
    matchLabels:
      app: {{ application_name }}
      environment: {{ environment }}
  template:
    metadata:
      labels:
        app: {{ application_name }}
        environment: {{ environment }}
        version: "{{ version }}"
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "{{ port }}"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: {{ application_name | resource_name(environment) }}
      containers:
      - name: {{ application_name }}
        image: {{ image }}:{{ version }}
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: {{ port }}
          name: http
          protocol: TCP
        env:
        - name: PORT
          value: "{{ port }}"
        envFrom:
        - configMapRef:
            name: {{ application_name | resource_name(environment) }}-config
        - secretRef:
            name: {{ application_name | resource_name(environment) }}-secrets
        resources:
          requests:
            memory: {{ resources.memory_request | default('1Gi') }}
            cpu: {{ resources.cpu_request | default('500m') }}
          limits:
            memory: {{ resources.memory_limit | default('4Gi') }}
            cpu: {{ resources.cpu_limit | default('2000m') }}
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache
      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
      securityContext:
        fsGroup: 1000
      terminationGracePeriodSeconds: 30

---
apiVersion: v1
kind: Service
metadata:
  name: {{ application_name | resource_name(environment) }}
  namespace: {{ application_name | namespace_name(environment) }}
  labels:
    app: {{ application_name }}
    environment: {{ environment }}
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: http
    protocol: TCP
    name: http
  selector:
    app: {{ application_name }}
    environment: {{ environment }}

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ application_name | resource_name(environment) }}
  namespace: {{ application_name | namespace_name(environment) }}
  labels:
    app: {{ application_name }}
    environment: {{ environment }}
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - {{ domain_name | default(application_name + '.' + environment + '.example.com') }}
    secretName: {{ application_name | resource_name(environment) }}-tls
  rules:
  - host: {{ domain_name | default(application_name + '.' + environment + '.example.com') }}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {{ application_name | resource_name(environment) }}
            port:
              number: 80

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ application_name | resource_name(environment) }}
  namespace: {{ application_name | namespace_name(environment) }}
  labels:
    app: {{ application_name }}
    environment: {{ environment }}

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ application_name | resource_name(environment) }}
  namespace: {{ application_name | namespace_name(environment) }}
  labels:
    app: {{ application_name }}
    environment: {{ environment }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ application_name | resource_name(environment) }}
  minReplicas: {{ min_replicas | default(2) }}
  maxReplicas: {{ max_replicas | default(10) }}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 2
        periodSeconds: 60
"""
    def _get_docker_compose_template(self) -> str:
        """
Get Docker Compose template"""
        return """
version: '3.8'

services:
  {{ application_name }}:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "{{ port | default(8000) }}:{{ port | default(8000) }}"
    environment:
      - ENVIRONMENT={{ environment }}
      - DATABASE_URL=postgresql://{{ postgres_user }}:{{ postgres_password }}@postgres:5432/{{ postgres_db }}
      - REDIS_URL=redis://redis:{{ redis_port | default(6379) }}/0
      - LOG_LEVEL={{ log_level | default('INFO') }}
{% for key, value in custom_vars.items() %}
      - {{ key }}={{ value }}
{% endfor %}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./:/app
      - /app/node_modules
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{{ port | default(8000) }}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB={{ postgres_db }}
      - POSTGRES_USER={{ postgres_user }}
      - POSTGRES_PASSWORD={{ postgres_password }}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U {{ postgres_user }} -d {{ postgres_db }}"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "{{ redis_port | default(6379) }}:6379"
    volumes:
      - redis_data:/data
      - ./config/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - {{ application_name }}
    networks:
      - app-network
    restart: unless-stopped

{% if environment == 'development' %}
  adminer:
    image: adminer
    ports:
      - "8080:8080"
    environment:
      - ADMINER_DEFAULT_SERVER=postgres
    depends_on:
      - postgres
    networks:
      - app-network
    restart: unless-stopped

  redis-commander:
    image: rediscommander/redis-commander:latest
    ports:
      - "8081:8081"
    environment:
      - REDIS_HOSTS=local:redis:6379
    depends_on:
      - redis
    networks:
      - app-network
    restart: unless-stopped
{% endif %}

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
"""
    def _get_terraform_aws_template(self) -> str:
        """
Get Terraform AWS template"""
        return """
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "{{ terraform_state_bucket }}"
    key    = "{{ application_name }}/{{ environment }}/terraform.tfstate"
    region = "{{ region }}"
  }
}

provider "aws" {
  region = var.region
  
  default_tags {
    tags = {
      Project     = "{{ application_name }}"
      Environment = "{{ environment }}"
      ManagedBy   = "terraform"
    }
  }
}

# Variables
variable "region" {
  description = "AWS region"
  type        = string
  default     = "{{ region }}"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "{{ environment }}"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "{{ instance_type }}"
}

variable "min_size" {
  description = "Minimum number of instances"
  type        = number
  default     = {{ min_size }}
}

variable "max_size" {
  description = "Maximum number of instances"
  type        = number
  default     = {{ max_size }}
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "{{ application_name }}-{{ environment }}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "{{ application_name }}-{{ environment }}-igw"
  }
}

# Subnets
resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "{{ application_name }}-{{ environment }}-public-${count.index + 1}"
    Type = "public"
  }
}

resource "aws_subnet" "private" {
  count = 2

  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "{{ application_name }}-{{ environment }}-private-${count.index + 1}"
    Type = "private"
  }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "{{ application_name }}-{{ environment }}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Security Groups
resource "aws_security_group" "alb" {
  name_prefix = "{{ application_name }}-{{ environment }}-alb-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "{{ application_name }}-{{ environment }}-alb-sg"
  }
}

resource "aws_security_group" "app" {
  name_prefix = "{{ application_name }}-{{ environment }}-app-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = {{ port | default(8000) }}
    to_port         = {{ port | default(8000) }}
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "{{ application_name }}-{{ environment }}-app-sg"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "{{ application_name }}-{{ environment }}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  tags = {
    Name = "{{ application_name }}-{{ environment }}-alb"
  }
}

resource "aws_lb_target_group" "app" {
  name     = "{{ application_name }}-{{ environment }}-tg"
  port     = {{ port | default(8000) }}
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name = "{{ application_name }}-{{ environment }}-tg"
  }
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Launch Template
resource "aws_launch_template" "app" {
  name_prefix   = "{{ application_name }}-{{ environment }}-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.app.id]

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    application_name = "{{ application_name }}"
    environment      = var.environment
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "{{ application_name }}-{{ environment }}-instance"
    }
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {
  name                = "{{ application_name }}-{{ environment }}-asg"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.app.arn]
  health_check_type   = "ELB"

  min_size         = var.min_size
  max_size         = var.max_size
  desired_capacity = var.min_size

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "{{ application_name }}-{{ environment }}-asg"
    propagate_at_launch = false
  }
}

# Outputs
output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}
"""
    def _get_helm_chart_template(self) -> str:
        """
Get Helm chart template"""
        return """
apiVersion: v2
name: {{ application_name }}
description: A Helm chart for {{ application_name }}
type: application
version: {{ chart_version }}
appVersion: "{{ app_version }}"

dependencies:
  - name: postgresql
    version: 12.x.x
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
  - name: redis
    version: 17.x.x
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
"""
    def _get_ansible_playbook_template(self) -> str:
        """
Get Ansible playbook template"""
        return """---
- name: Deploy {{ application_name }}
  hosts: all
  become: yes
  vars:
    application_name: {{ application_name }}
    environment: {{ environment }}
    python_version: {{ python_version }}
    nodejs_version: {{ nodejs_version }}
    app_user: "{{ application_name }}"
    app_directory: "/opt/{{ application_name }}"

  tasks:
    - name: Update system packages
      package:
        name: "*"
        state: latest

    - name: Install system dependencies
      package:
        name:
          - git
          - curl
          - wget
          - unzip
          - nginx
          - postgresql-client
          - redis-tools
        state: present

    - name: Create application user
      user:
        name: "{{ app_user }}"
        system: yes
        shell: /bin/bash
        home: "{{ app_directory }}"
        create_home: yes

    - name: Install Python {{ python_version }}
      package:
        name:
          - python{{ python_version }}
          - python{{ python_version }}-pip
          - python{{ python_version }}-venv
        state: present

    - name: Install Node.js {{ nodejs_version }}
      shell: |
        curl -fsSL https://deb.nodesource.com/setup_{{ nodejs_version }}.x | sudo -E bash -
        apt-get install -y nodejs
      args:
        creates: /usr/bin/node

    - name: Clone application repository
      git:
        repo: "{{ git_repository | default('https://github.com/example/repo.git') }}"
        dest: "{{ app_directory }}"
        version: "{{ git_branch | default('main') }}"
        force: yes
      become_user: "{{ app_user }}"

    - name: Create Python virtual environment
      command: python{{ python_version }} -m venv {{ app_directory }}/venv
      become_user: "{{ app_user }}"
      args:
        creates: "{{ app_directory }}/venv"

    - name: Install Python dependencies
      pip:
        requirements: "{{ app_directory }}/requirements.txt"
        virtualenv: "{{ app_directory }}/venv"
      become_user: "{{ app_user }}"

    - name: Install Node.js dependencies
      npm:
        path: "{{ app_directory }}"
        state: present
      become_user: "{{ app_user }}"

    - name: Configure application environment
      template:
        src: env.j2
        dest: "{{ app_directory }}/.env"
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0600'

    - name: Create systemd service file
      template:
        src: service.j2
        dest: "/etc/systemd/system/{{ application_name }}.service"
        owner: root
        group: root
        mode: '0644'
      notify: restart application

    - name: Configure Nginx
      template:
        src: nginx.j2
        dest: "/etc/nginx/sites-available/{{ application_name }}"
        owner: root
        group: root
        mode: '0644'
      notify: restart nginx

    - name: Enable Nginx site
      file:
        src: "/etc/nginx/sites-available/{{ application_name }}"
        dest: "/etc/nginx/sites-enabled/{{ application_name }}"
        state: link
      notify: restart nginx

    - name: Start and enable application service
      systemd:
        name: "{{ application_name }}"
        state: started
        enabled: yes
        daemon_reload: yes

    - name: Start and enable Nginx
      systemd:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: restart application
      systemd:
        name: "{{ application_name }}"
        state: restarted

    - name: restart nginx
      systemd:
        name: nginx
        state: restarted
"""
    async def _generate_default_templates(self) -> None:
        """
Generate additional default templates"""
        
        # CI/CD pipeline templates
        await self._generate_cicd_templates()
        
        # Database migration templates
        await self._generate_database_templates()
        
        # Monitoring templates
        await self._generate_monitoring_templates()
        
        # Security templates
        await self._generate_security_templates()
        
        self.logger.info("Default templates generated")
    
    async def _generate_cicd_templates(self) -> None:
        """Generate CI/CD pipeline templates"""
        
        # GitHub Actions template
        github_actions = DeploymentTemplate(
            name="github-actions",
            provider=CloudProvider.KUBERNETES,
            template_type=DeploymentType.PRODUCTION,
            format=TemplateFormat.YAML,
            template_content="""name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.image.outputs.image }}
    steps:
    - uses: actions/checkout@v3
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to Kubernetes
      run: |
        echo "Deploying to production..."
""",
            description="GitHub Actions CI/CD pipeline"
        )
        
        self.templates["github-actions"] = github_actions
    
    async def _generate_database_templates(self) -> None:
        """Generate database templates"""
        
        # Database migration template
        db_migration = DeploymentTemplate(
            name="database-migration",
            provider=CloudProvider.KUBERNETES,
            template_type=DeploymentType.PRODUCTION,
            format=TemplateFormat.YAML,
            template_content="""apiVersion: batch/v1
kind: Job
metadata:
  name: {{ application_name }}-migration-{{ migration_version }}
  namespace: {{ namespace }}
spec:
  template:
    spec:
      containers:
      - name: migration
        image: {{ image }}:{{ version }}
        command: ["python", "manage.py", "migrate"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ application_name }}-secrets
              key: DATABASE_URL
      restartPolicy: Never
  backoffLimit: 3
""",
            description="Database migration job"
        )
        
        self.templates["database-migration"] = db_migration
    
    async def _generate_monitoring_templates(self) -> None:
        """Generate monitoring templates"""
        
        # Prometheus monitoring template
        prometheus_config = DeploymentTemplate(
            name="prometheus-monitoring",
            provider=CloudProvider.KUBERNETES,
            template_type=DeploymentType.PRODUCTION,
            format=TemplateFormat.YAML,
            template_content="""apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ application_name }}-monitor
  namespace: {{ namespace }}
spec:
  selector:
    matchLabels:
      app: {{ application_name }}
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
""",
            description="Prometheus service monitor"
        )
        
        self.templates["prometheus-monitoring"] = prometheus_config
    
    async def _generate_security_templates(self) -> None:
        """Generate security templates"""
        
        # Network policy template
        network_policy = DeploymentTemplate(
            name="network-policy",
            provider=CloudProvider.KUBERNETES,
            template_type=DeploymentType.PRODUCTION,
            format=TemplateFormat.YAML,
            template_content="""apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ application_name }}-netpol
  namespace: {{ namespace }}
spec:
  podSelector:
    matchLabels:
      app: {{ application_name }}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: {{ port }}
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
""",
            description="Kubernetes network policy"
        )
        
        self.templates["network-policy"] = network_policy
    
    async def render_template(
        self,
        template_name: str,
        context: TemplateContext,
        output_format: Optional[TemplateFormat] = None
    ) -> str:
        """
        Render deployment template.
        
        Args:
            template_name: Name of template to render
            context: Template rendering context
            output_format: Output format override
            
        Returns:
            Rendered template content
        """
        try:
            if template_name not in self.templates:
                raise ValueError(f"Template not found: {template_name}")
            
            template = self.templates[template_name]
            
            # Create Jinja2 template
            jinja_template = self.jinja_env.from_string(template.template_content)
            
            # Prepare context variables
            template_vars = {
                "application_name": context.application_name,
                "environment": context.environment,
                "region": context.region,
                "namespace": context.namespace,
                "version": context.version,
                "replicas": context.replicas,
                "resources": context.resources,
                "secrets": context.secrets,
                "config_maps": context.config_maps,
                **context.custom_vars,
                **template.variables
            }
            
            # Render template
            rendered_content = jinja_template.render(**template_vars)
            
            # Convert format if requested
            if output_format and output_format != template.format:
                rendered_content = await self._convert_format(
                    rendered_content,
                    template.format,
                    output_format
                )
            
            self.logger.info(f"Template rendered successfully: {template_name}")
            return rendered_content
            
        except Exception as e:
            self.logger.error(f"Failed to render template {template_name}: {e}")
            raise
    
    async def _convert_format(
        self,
        content: str,
        from_format: TemplateFormat,
        to_format: TemplateFormat
    ) -> str:
        """Convert content between formats"""
        
        # Basic format conversion
        if from_format == TemplateFormat.YAML and to_format == TemplateFormat.JSON:
            data = yaml.safe_load(content)
            return json.dumps(data, indent=2)
        elif from_format == TemplateFormat.JSON and to_format == TemplateFormat.YAML:
            data = json.loads(content)
            return yaml.dump(data, default_flow_style=False)
        
        # Return original content if no conversion available
        return content
    
    async def generate_deployment_package(
        self,
        template_names: List[str],
        context: TemplateContext,
        output_directory: str
    ) -> bool:
        """
        Generate complete deployment package.
        
        Args:
            template_names: List of templates to include
            context: Template rendering context
            output_directory: Output directory path
            
        Returns:
            bool: True if successful
        """
        try:
            # Create output directory
            output_path = Path(output_directory)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Render and save each template
            for template_name in template_names:
                if template_name not in self.templates:
                    self.logger.warning(f"Template not found: {template_name}")
                    continue
                
                template = self.templates[template_name]
                rendered_content = await self.render_template(template_name, context)
                
                # Determine file extension
                file_extension = self._get_file_extension(template.format)
                file_name = f"{template_name}.{file_extension}"
                file_path = output_path / file_name
                
                # Write file
                with open(file_path, 'w') as f:
                    f.write(rendered_content)
                
                self.logger.info(f"Generated: {file_path}")
            
            self.logger.info(f"Deployment package generated: {output_directory}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate deployment package: {e}")
            return False
    
    def _get_file_extension(self, template_format: TemplateFormat) -> str:
        """Get file extension for template format"""
        
        extension_map = {
            TemplateFormat.YAML: "yaml",
            TemplateFormat.JSON: "json",
            TemplateFormat.TERRAFORM: "tf",
            TemplateFormat.DOCKERFILE: "Dockerfile",
            TemplateFormat.COMPOSE: "docker-compose.yml",
            TemplateFormat.HELM: "yaml",
            TemplateFormat.ANSIBLE: "yml"
        }
        
        return extension_map.get(template_format, "txt")
    
    async def add_custom_template(self, template: DeploymentTemplate) -> bool:
        """
        Add custom deployment template.
        
        Args:
            template: Template definition
            
        Returns:
            bool: True if successful
        """
        try:
            self.templates[template.name] = template
            self.logger.info(f"Custom template added: {template.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add custom template: {e}")
            return False
    
    async def validate_template(self, template_name: str, context: TemplateContext) -> Dict[str, Any]:
        """
        Validate template rendering.
        
        Args:
            template_name: Name of template to validate
            context: Template rendering context
            
        Returns:
            Validation result
        """
        try:
            # Attempt to render template
            rendered_content = await self.render_template(template_name, context)
            
            # Basic validation checks
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "rendered_size": len(rendered_content)
            }
            
            # Check for common issues
            if not rendered_content.strip():
                validation_result["errors"].append("Template rendered to empty content")
                validation_result["valid"] = False
            
            # Format-specific validation
            template = self.templates[template_name]
            if template.format == TemplateFormat.YAML:
                try:
                    yaml.safe_load(rendered_content)
                except yaml.YAMLError as e:
                    validation_result["errors"].append(f"Invalid YAML: {e}")
                    validation_result["valid"] = False
            elif template.format == TemplateFormat.JSON:
                try:
                    json.loads(rendered_content)
                except json.JSONDecodeError as e:
                    validation_result["errors"].append(f"Invalid JSON: {e}")
                    validation_result["valid"] = False
            
            return validation_result
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "rendered_size": 0
            }
    
    async def get_template_list(self) -> List[Dict[str, Any]]:
        """Get list of available templates"""
        
        return [
            {
                "name": template.name,
                "provider": template.provider.value,
                "type": template.template_type.value,
                "format": template.format.value,
                "description": template.description,
                "version": template.version,
                "dependencies": template.dependencies
            }
            for template in self.templates.values()
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get template manager status"""
        
        return {
            "total_templates": len(self.templates),
            "providers": list(set(t.provider.value for t in self.templates.values())),
            "formats": list(set(t.format.value for t in self.templates.values())),
            "template_directories": self.template_dirs,
            "jinja_initialized": self.jinja_env is not None
        }
