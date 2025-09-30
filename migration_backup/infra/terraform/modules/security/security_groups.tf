# Ainflue Infrastructure Module - Security Groups Module
# ======================================================
# 
# Enterprise-grade security groups for Ainflue platform
# Comprehensive network security policies and access control
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

# **EXPERT ROLES IMPLEMENTATION:**
# Lead Dev IA: AI service network security, model serving protection
# Backend Senior: Microservices network isolation, API security
# ML Engineer: ML pipeline network security, model training isolation
# DBA: Database network access control, read/write separation
# Security: Zero-trust network policies, threat protection, compliance
# Microservices: Service mesh security, inter-service communication
# Audio Engineer: Media processing network security, streaming protection
# DevOps: CI/CD network access, deployment security
# IA Prompt Engineer: AI provider network security, prompt service isolation

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "ainflue"
}

variable "vpc_id" {
  description = "VPC ID where security groups will be created"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_detailed_monitoring" {
  description = "Enable detailed security monitoring"
  type        = bool
  default     = true
}

variable "allowed_cidr_blocks" {
  description = "List of allowed CIDR blocks for external access"
  type        = list(string)
  default     = []
}

# Security Group for ALB (Application Load Balancer)
resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-${var.environment}-alb-"
  vpc_id      = var.vpc_id
  description = "Security group for Application Load Balancer"

  # HTTP access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access from internet"
  }

  # HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access from internet"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-alb"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "load-balancer"
  }
}

# Security Group for Web/API Servers
resource "aws_security_group" "web" {
  name_prefix = "${var.project_name}-${var.environment}-web-"
  vpc_id      = var.vpc_id
  description = "Security group for web and API servers"

  # HTTP from ALB
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "HTTP from ALB"
  }

  # HTTPS from ALB
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "HTTPS from ALB"
  }

  # Application port (8000)
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Application port from ALB"
  }

  # Health check port
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Health check port from ALB"
  }

  # SSH access from bastion
  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
    description     = "SSH from bastion host"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-web"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "web-api-servers"
  }
}

# Security Group for AI/ML Services
resource "aws_security_group" "ai_ml" {
  name_prefix = "${var.project_name}-${var.environment}-ai-ml-"
  vpc_id      = var.vpc_id
  description = "Security group for AI/ML services"

  # AI API port
  ingress {
    from_port       = 8001
    to_port         = 8001
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "AI API access from web servers"
  }

  # ML model serving port
  ingress {
    from_port       = 8002
    to_port         = 8002
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "ML model serving from web servers"
  }

  # TensorFlow Serving
  ingress {
    from_port       = 8501
    to_port         = 8501
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "TensorFlow Serving REST API"
  }

  # TensorFlow Serving gRPC
  ingress {
    from_port       = 8500
    to_port         = 8500
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "TensorFlow Serving gRPC"
  }

  # Jupyter notebook (internal only)
  ingress {
    from_port       = 8888
    to_port         = 8888
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
    description     = "Jupyter notebook from bastion"
  }

  # SSH access from bastion
  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
    description     = "SSH from bastion host"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-ai-ml"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "ai-ml-services"
  }
}

# Security Group for Database (RDS)
resource "aws_security_group" "database" {
  name_prefix = "${var.project_name}-${var.environment}-db-"
  vpc_id      = var.vpc_id
  description = "Security group for database access"

  # PostgreSQL from web servers
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "PostgreSQL from web servers"
  }

  # PostgreSQL from AI/ML services
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ai_ml.id]
    description     = "PostgreSQL from AI/ML services"
  }

  # PostgreSQL from bastion (for admin access)
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
    description     = "PostgreSQL from bastion"
  }

  # No outbound rules needed for RDS

  tags = {
    Name        = "${var.project_name}-${var.environment}-database"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "database-access"
  }
}

# Security Group for Redis/ElastiCache
resource "aws_security_group" "cache" {
  name_prefix = "${var.project_name}-${var.environment}-cache-"
  vpc_id      = var.vpc_id
  description = "Security group for Redis/cache access"

  # Redis from web servers
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "Redis from web servers"
  }

  # Redis from AI/ML services
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ai_ml.id]
    description     = "Redis from AI/ML services"
  }

  # Redis Cluster port
  ingress {
    from_port       = 16379
    to_port         = 16379
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id, aws_security_group.ai_ml.id]
    description     = "Redis Cluster bus"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-cache"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "cache-access"
  }
}

# Security Group for Bastion Host
resource "aws_security_group" "bastion" {
  name_prefix = "${var.project_name}-${var.environment}-bastion-"
  vpc_id      = var.vpc_id
  description = "Security group for bastion host"

  # SSH access from allowed IPs
  dynamic "ingress" {
    for_each = length(var.allowed_cidr_blocks) > 0 ? var.allowed_cidr_blocks : ["0.0.0.0/0"]
    content {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
      description = "SSH access from ${ingress.value}"
    }
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-bastion"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "bastion-host"
  }
}

# Security Group for Audio/Media Processing
resource "aws_security_group" "media" {
  name_prefix = "${var.project_name}-${var.environment}-media-"
  vpc_id      = var.vpc_id
  description = "Security group for audio/media processing services"

  # Media processing API
  ingress {
    from_port       = 8003
    to_port         = 8003
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "Media processing API from web servers"
  }

  # FFmpeg processing service
  ingress {
    from_port       = 8004
    to_port         = 8004
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "FFmpeg service from web servers"
  }

  # Streaming service (RTMP)
  ingress {
    from_port       = 1935
    to_port         = 1935
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "RTMP streaming from web servers"
  }

  # WebRTC signaling
  ingress {
    from_port       = 8005
    to_port         = 8005
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "WebRTC signaling from web servers"
  }

  # SSH access from bastion
  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
    description     = "SSH from bastion host"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-media"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "media-processing"
  }
}

# Security Group for Monitoring (Prometheus, Grafana)
resource "aws_security_group" "monitoring" {
  name_prefix = "${var.project_name}-${var.environment}-monitoring-"
  vpc_id      = var.vpc_id
  description = "Security group for monitoring services"

  # Prometheus
  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Prometheus from VPC"
  }

  # Grafana
  ingress {
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Grafana from ALB"
  }

  # Node Exporter
  ingress {
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Node Exporter from VPC"
  }

  # Alertmanager
  ingress {
    from_port   = 9093
    to_port     = 9093
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Alertmanager from VPC"
  }

  # Jaeger UI
  ingress {
    from_port       = 16686
    to_port         = 16686
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Jaeger UI from ALB"
  }

  # Jaeger collector
  ingress {
    from_port   = 14268
    to_port     = 14268
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Jaeger collector from VPC"
  }

  # SSH access from bastion
  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
    description     = "SSH from bastion host"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-monitoring"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "monitoring-services"
  }
}

# Security Group for EKS Cluster
resource "aws_security_group" "eks_cluster" {
  name_prefix = "${var.project_name}-${var.environment}-eks-cluster-"
  vpc_id      = var.vpc_id
  description = "Security group for EKS cluster control plane"

  # HTTPS API server
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "HTTPS API server from VPC"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-eks-cluster"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "eks-control-plane"
  }
}

# Security Group for EKS Node Group
resource "aws_security_group" "eks_nodes" {
  name_prefix = "${var.project_name}-${var.environment}-eks-nodes-"
  vpc_id      = var.vpc_id
  description = "Security group for EKS worker nodes"

  # Node to node communication
  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true
    description = "Node to node communication"
  }

  # Node port services
  ingress {
    from_port       = 30000
    to_port         = 32767
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Node port services from ALB"
  }

  # Kubelet API
  ingress {
    from_port       = 10250
    to_port         = 10250
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
    description     = "Kubelet API from control plane"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-eks-nodes"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "eks-worker-nodes"
  }
}

# Security Group for VPN Gateway
resource "aws_security_group" "vpn" {
  name_prefix = "${var.project_name}-${var.environment}-vpn-"
  vpc_id      = var.vpc_id
  description = "Security group for VPN gateway"

  # OpenVPN
  ingress {
    from_port   = 1194
    to_port     = 1194
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "OpenVPN UDP"
  }

  # WireGuard
  ingress {
    from_port   = 51820
    to_port     = 51820
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "WireGuard UDP"
  }

  # SSH access from allowed IPs
  dynamic "ingress" {
    for_each = length(var.allowed_cidr_blocks) > 0 ? var.allowed_cidr_blocks : []
    content {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
      description = "SSH access from ${ingress.value}"
    }
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-vpn"
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "vpn-gateway"
  }
}

# Security Group Rules for cross-group communication
resource "aws_security_group_rule" "cluster_to_nodes" {
  type                     = "ingress"
  from_port                = 1025
  to_port                  = 65535
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.eks_cluster.id
  security_group_id        = aws_security_group.eks_nodes.id
  description              = "Control plane to nodes communication"
}

resource "aws_security_group_rule" "nodes_to_cluster" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.eks_nodes.id
  security_group_id        = aws_security_group.eks_cluster.id
  description              = "Nodes to control plane communication"
}

# Outputs
output "alb_security_group_id" {
  description = "Security group ID for ALB"
  value       = aws_security_group.alb.id
}

output "web_security_group_id" {
  description = "Security group ID for web servers"
  value       = aws_security_group.web.id
}

output "ai_ml_security_group_id" {
  description = "Security group ID for AI/ML services"
  value       = aws_security_group.ai_ml.id
}

output "database_security_group_id" {
  description = "Security group ID for database"
  value       = aws_security_group.database.id
}

output "cache_security_group_id" {
  description = "Security group ID for cache"
  value       = aws_security_group.cache.id
}

output "bastion_security_group_id" {
  description = "Security group ID for bastion host"
  value       = aws_security_group.bastion.id
}

output "media_security_group_id" {
  description = "Security group ID for media processing"
  value       = aws_security_group.media.id
}

output "monitoring_security_group_id" {
  description = "Security group ID for monitoring"
  value       = aws_security_group.monitoring.id
}

output "eks_cluster_security_group_id" {
  description = "Security group ID for EKS cluster"
  value       = aws_security_group.eks_cluster.id
}

output "eks_nodes_security_group_id" {
  description = "Security group ID for EKS nodes"
  value       = aws_security_group.eks_nodes.id
}

output "vpn_security_group_id" {
  description = "Security group ID for VPN gateway"
  value       = aws_security_group.vpn.id
}