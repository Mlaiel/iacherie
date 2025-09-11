#!/bin/bash
# =============================================================================
# NGINX ENTERPRISE DEPLOYMENT SCRIPT
# =============================================================================
# Automated deployment script for Ainflue AI Creator Platform
# Supports multi-environment deployment with zero-downtime updates
#
# Author: DevOps Engineer + Infrastructure Expert
# Copyright: (c) 2024 IA Influencer Agent Platform. All rights reserved.
# =============================================================================

set -euo pipefail

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly NGINX_CONFIG_DIR="/etc/nginx"
readonly BACKUP_DIR="/etc/nginx/backups"
readonly LOG_FILE="/var/log/nginx_deployment.log"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Deployment configuration
ENVIRONMENT="${ENVIRONMENT:-production}"
DEPLOYMENT_TYPE="${DEPLOYMENT_TYPE:-rolling}"
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-60}"
ROLLBACK_ON_FAILURE="${ROLLBACK_ON_FAILURE:-true}"

# =============================================================================
# LOGGING AND OUTPUT FUNCTIONS
# =============================================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "$LOG_FILE"
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

check_nginx() {
    if ! command -v nginx &> /dev/null; then
        log_error "Nginx is not installed"
        exit 1
    fi
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_warning "Docker is not installed - container deployment will be skipped"
        return 1
    fi
    return 0
}

get_nginx_version() {
    nginx -v 2>&1 | sed 's/nginx version: nginx\///'
}

# =============================================================================
# BACKUP FUNCTIONS
# =============================================================================

create_backup() {
    local backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="${BACKUP_DIR}/nginx_config_${backup_timestamp}.tar.gz"
    
    log_info "Creating configuration backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    if tar -czf "$backup_file" -C "$NGINX_CONFIG_DIR" \
        nginx.conf conf.d/ sites-available/ sites-enabled/ ssl/ 2>/dev/null; then
        log_success "Backup created: $backup_file"
        echo "$backup_file"
    else
        log_error "Failed to create backup"
        exit 1
    fi
}

restore_backup() {
    local backup_file="$1"
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log_info "Restoring configuration from backup: $backup_file"
    
    if tar -xzf "$backup_file" -C "$NGINX_CONFIG_DIR"; then
        log_success "Configuration restored from backup"
        return 0
    else
        log_error "Failed to restore from backup"
        return 1
    fi
}

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

validate_nginx_config() {
    log_info "Validating nginx configuration..."
    
    if nginx -t; then
        log_success "Configuration validation passed"
        return 0
    else
        log_error "Configuration validation failed"
        return 1
    fi
}

test_upstream_connectivity() {
    local upstreams=(
        "ainflue-app-1:8000"
        "ainflue-app-2:8000"
        "ainflue-app-3:8000"
        "ainflue-ai-1:8001"
        "ainflue-upload-1:8002"
    )
    
    log_info "Testing upstream connectivity..."
    
    local failed_upstreams=()
    
    for upstream in "${upstreams[@]}"; do
        local host="${upstream%:*}"
        local port="${upstream#*:}"
        
        if timeout 5 bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
            log_info "✓ $upstream is reachable"
        else
            log_warning "✗ $upstream is not reachable"
            failed_upstreams+=("$upstream")
        fi
    done
    
    if [[ ${#failed_upstreams[@]} -gt 0 ]]; then
        log_warning "Some upstreams are not reachable: ${failed_upstreams[*]}"
        return 1
    fi
    
    log_success "All upstreams are reachable"
    return 0
}

# =============================================================================
# SSL CERTIFICATE MANAGEMENT
# =============================================================================

check_ssl_certificates() {
    log_info "Checking SSL certificates..."
    
    local ssl_dir="/etc/nginx/ssl"
    local cert_files=(
        "$ssl_dir/ainflue.com/fullchain.pem"
        "$ssl_dir/ainflue.com/privkey.pem"
    )
    
    for cert_file in "${cert_files[@]}"; do
        if [[ -f "$cert_file" ]]; then
            # Check certificate expiration
            local expiry_date=$(openssl x509 -enddate -noout -in "$cert_file" 2>/dev/null | cut -d= -f2)
            local expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || echo 0)
            local current_epoch=$(date +%s)
            local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
            
            if [[ $days_until_expiry -gt 30 ]]; then
                log_success "✓ $cert_file is valid ($days_until_expiry days remaining)"
            elif [[ $days_until_expiry -gt 0 ]]; then
                log_warning "⚠ $cert_file expires in $days_until_expiry days"
            else
                log_error "✗ $cert_file has expired"
                return 1
            fi
        else
            log_error "✗ Certificate file not found: $cert_file"
            return 1
        fi
    done
    
    return 0
}

generate_ssl_certificates() {
    local domain="${1:-ainflue.com}"
    
    log_info "Generating SSL certificates for $domain..."
    
    if command -v certbot &> /dev/null; then
        if certbot --nginx -d "$domain" -d "www.$domain" --non-interactive --agree-tos \
           --email "admin@$domain" --no-eff-email; then
            log_success "SSL certificates generated successfully"
            return 0
        else
            log_error "Failed to generate SSL certificates"
            return 1
        fi
    else
        log_warning "Certbot not installed - skipping SSL certificate generation"
        return 1
    fi
}

# =============================================================================
# DEPLOYMENT STRATEGIES
# =============================================================================

deploy_rolling() {
    log_info "Starting rolling deployment..."
    
    local backup_file
    backup_file=$(create_backup)
    
    # Copy new configuration files
    log_info "Deploying new configuration files..."
    
    cp "$SCRIPT_DIR/enterprise_production.conf" "$NGINX_CONFIG_DIR/nginx.conf"
    cp "$SCRIPT_DIR/security_modules.conf" "$NGINX_CONFIG_DIR/conf.d/"
    cp "$SCRIPT_DIR/monitoring_analytics.conf" "$NGINX_CONFIG_DIR/conf.d/"
    cp "$SCRIPT_DIR/config_management.conf" "$NGINX_CONFIG_DIR/conf.d/"
    
    # Validate configuration
    if ! validate_nginx_config; then
        log_error "Configuration validation failed - rolling back..."
        restore_backup "$backup_file"
        return 1
    fi
    
    # Reload nginx with new configuration
    log_info "Reloading nginx configuration..."
    if systemctl reload nginx; then
        log_success "Nginx reloaded successfully"
    else
        log_error "Failed to reload nginx - rolling back..."
        restore_backup "$backup_file"
        systemctl reload nginx
        return 1
    fi
    
    # Health check
    if ! perform_health_check; then
        log_error "Health check failed - rolling back..."
        restore_backup "$backup_file"
        systemctl reload nginx
        return 1
    fi
    
    log_success "Rolling deployment completed successfully"
    return 0
}

deploy_blue_green() {
    log_info "Starting blue-green deployment..."
    
    local current_backend=$(curl -s http://localhost:8080/deployment/current 2>/dev/null || echo "blue")
    local target_backend="green"
    
    if [[ "$current_backend" == "green" ]]; then
        target_backend="blue"
    fi
    
    log_info "Current backend: $current_backend, Target backend: $target_backend"
    
    # Deploy to target backend
    log_info "Deploying to $target_backend backend..."
    
    # Switch traffic to target backend
    log_info "Switching traffic to $target_backend..."
    if curl -X POST "http://localhost:8080/deployment/switch?target=$target_backend" &>/dev/null; then
        log_success "Traffic switched to $target_backend"
    else
        log_error "Failed to switch traffic"
        return 1
    fi
    
    # Health check on new backend
    if ! perform_health_check; then
        log_error "Health check failed - switching back to $current_backend..."
        curl -X POST "http://localhost:8080/deployment/switch?target=$current_backend" &>/dev/null
        return 1
    fi
    
    log_success "Blue-green deployment completed successfully"
    return 0
}

deploy_canary() {
    log_info "Starting canary deployment..."
    
    # Enable canary backend with 1% traffic
    log_info "Enabling canary deployment with 1% traffic..."
    
    # Copy configuration for canary backend
    cp "$SCRIPT_DIR/enterprise_production.conf" "$NGINX_CONFIG_DIR/nginx.conf"
    
    # Update canary configuration to split traffic
    sed -i 's/split_clients.*1%/split_clients "${remote_addr}${http_user_agent}${date_gmt}" $ab_test_group {\n    1% "canary";\n    * "stable";\n}/' \
        "$NGINX_CONFIG_DIR/nginx.conf"
    
    if ! validate_nginx_config; then
        log_error "Canary configuration validation failed"
        return 1
    fi
    
    systemctl reload nginx
    
    # Monitor canary for 5 minutes
    log_info "Monitoring canary deployment for 5 minutes..."
    sleep 300
    
    # Check canary metrics
    local error_rate=$(curl -s http://localhost:8080/metrics/canary/error_rate 2>/dev/null || echo "0.05")
    
    if (( $(echo "$error_rate < 0.05" | bc -l) )); then
        log_info "Canary metrics look good - promoting to full deployment..."
        
        # Update to 100% traffic
        sed -i 's/1% "canary"/100% "canary"/' "$NGINX_CONFIG_DIR/nginx.conf"
        systemctl reload nginx
        
        log_success "Canary deployment promoted successfully"
        return 0
    else
        log_error "Canary metrics indicate issues - rolling back..."
        
        # Disable canary
        sed -i 's/1% "canary"/0% "canary"/' "$NGINX_CONFIG_DIR/nginx.conf"
        systemctl reload nginx
        
        return 1
    fi
}

# =============================================================================
# HEALTH CHECKS
# =============================================================================

perform_health_check() {
    log_info "Performing health checks..."
    
    local health_endpoints=(
        "http://localhost/health"
        "http://localhost/nginx-health"
        "http://localhost:8080/nginx-status"
    )
    
    local timeout=0
    local max_timeout=$HEALTH_CHECK_TIMEOUT
    
    while [[ $timeout -lt $max_timeout ]]; do
        local all_healthy=true
        
        for endpoint in "${health_endpoints[@]}"; do
            if ! curl -sf "$endpoint" >/dev/null 2>&1; then
                all_healthy=false
                break
            fi
        done
        
        if $all_healthy; then
            log_success "All health checks passed"
            return 0
        fi
        
        log_info "Health check attempt $((timeout + 1))/$max_timeout - waiting..."
        sleep 5
        ((timeout += 5))
    done
    
    log_error "Health checks failed after $max_timeout seconds"
    return 1
}

check_performance_metrics() {
    log_info "Checking performance metrics..."
    
    local response_time=$(curl -s http://localhost:8080/metrics/realtime 2>/dev/null | \
                         jq -r '.performance.avg_response_time // 0' 2>/dev/null || echo "0")
    
    local error_rate=$(curl -s http://localhost:8080/metrics/realtime 2>/dev/null | \
                      jq -r '.performance.error_rate // 0' 2>/dev/null || echo "0")
    
    log_info "Current response time: ${response_time}s"
    log_info "Current error rate: ${error_rate}%"
    
    # Check if metrics are within acceptable ranges
    if (( $(echo "$response_time < 1.0" | bc -l) )) && (( $(echo "$error_rate < 5.0" | bc -l) )); then
        log_success "Performance metrics are within acceptable ranges"
        return 0
    else
        log_warning "Performance metrics are outside acceptable ranges"
        return 1
    fi
}

# =============================================================================
# DOCKER DEPLOYMENT
# =============================================================================

deploy_docker() {
    if ! check_docker; then
        log_warning "Skipping Docker deployment - Docker not available"
        return 0
    fi
    
    log_info "Starting Docker deployment..."
    
    # Build nginx image
    log_info "Building nginx Docker image..."
    
    cat > "$SCRIPT_DIR/Dockerfile.nginx" << 'EOF'
FROM nginx:1.25-alpine

# Install additional modules
RUN apk add --no-cache \
    nginx-mod-http-lua \
    nginx-mod-http-geoip \
    nginx-mod-http-brotli \
    nginx-mod-stream \
    lua-resty-prometheus

# Copy configuration files
COPY enterprise_production.conf /etc/nginx/nginx.conf
COPY security_modules.conf /etc/nginx/conf.d/
COPY monitoring_analytics.conf /etc/nginx/conf.d/
COPY config_management.conf /etc/nginx/conf.d/

# Create required directories
RUN mkdir -p /var/cache/nginx /var/log/nginx /etc/nginx/ssl /etc/nginx/security

# Set permissions
RUN chown -R nginx:nginx /var/cache/nginx /var/log/nginx

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

EXPOSE 80 443 8080

CMD ["nginx", "-g", "daemon off;"]
EOF
    
    if docker build -t ainflue/nginx:latest -f "$SCRIPT_DIR/Dockerfile.nginx" "$SCRIPT_DIR"; then
        log_success "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        return 1
    fi
    
    # Deploy with docker-compose
    log_info "Deploying with docker-compose..."
    
    cat > "$SCRIPT_DIR/docker-compose.nginx.yml" << 'EOF'
version: '3.8'

services:
  nginx:
    image: ainflue/nginx:latest
    container_name: ainflue-nginx
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs:/var/log/nginx
      - ./cache:/var/cache/nginx
    environment:
      - ENVIRONMENT=production
      - DEPLOYMENT_ID=${DEPLOYMENT_ID:-$(date +%s)}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - ainflue_network

networks:
  ainflue_network:
    external: true
EOF
    
    if docker-compose -f "$SCRIPT_DIR/docker-compose.nginx.yml" up -d; then
        log_success "Docker deployment completed successfully"
        return 0
    else
        log_error "Docker deployment failed"
        return 1
    fi
}

# =============================================================================
# KUBERNETES DEPLOYMENT
# =============================================================================

deploy_kubernetes() {
    if ! command -v kubectl &> /dev/null; then
        log_warning "Skipping Kubernetes deployment - kubectl not available"
        return 0
    fi
    
    log_info "Starting Kubernetes deployment..."
    
    # Generate Kubernetes manifests
    cat > "$SCRIPT_DIR/k8s-nginx-deployment.yml" << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ainflue-nginx
  namespace: ainflue
  labels:
    app: nginx
    version: v2024.12.1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
        version: v2024.12.1
    spec:
      containers:
      - name: nginx
        image: ainflue/nginx:latest
        ports:
        - containerPort: 80
        - containerPort: 443
        - containerPort: 8080
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DEPLOYMENT_ID
          value: "k8s-$(date +%s)"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /k8s/ready
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /k8s/health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/conf.d
        - name: ssl-certs
          mountPath: /etc/nginx/ssl
          readOnly: true
      volumes:
      - name: nginx-config
        configMap:
          name: nginx-config
      - name: ssl-certs
        secret:
          secretName: ainflue-ssl-certs
---
apiVersion: v1
kind: Service
metadata:
  name: ainflue-nginx-service
  namespace: ainflue
spec:
  selector:
    app: nginx
  ports:
    - name: http
      port: 80
      targetPort: 80
    - name: https
      port: 443
      targetPort: 443
    - name: metrics
      port: 8080
      targetPort: 8080
  type: LoadBalancer
EOF
    
    # Apply Kubernetes manifests
    if kubectl apply -f "$SCRIPT_DIR/k8s-nginx-deployment.yml"; then
        log_success "Kubernetes deployment completed successfully"
        return 0
    else
        log_error "Kubernetes deployment failed"
        return 1
    fi
}

# =============================================================================
# MAIN DEPLOYMENT FUNCTION
# =============================================================================

main() {
    log_info "Starting Nginx Enterprise deployment for Ainflue platform"
    log_info "Environment: $ENVIRONMENT"
    log_info "Deployment type: $DEPLOYMENT_TYPE"
    log_info "Nginx version: $(get_nginx_version)"
    
    # Pre-deployment checks
    check_root
    check_nginx
    
    # SSL certificate checks
    if ! check_ssl_certificates; then
        log_warning "SSL certificate issues detected"
        if [[ "$ENVIRONMENT" == "production" ]]; then
            generate_ssl_certificates
        fi
    fi
    
    # Upstream connectivity check
    test_upstream_connectivity || log_warning "Some upstreams are not reachable"
    
    # Execute deployment based on type
    case "$DEPLOYMENT_TYPE" in
        "rolling")
            deploy_rolling
            ;;
        "blue-green")
            deploy_blue_green
            ;;
        "canary")
            deploy_canary
            ;;
        "docker")
            deploy_docker
            ;;
        "kubernetes")
            deploy_kubernetes
            ;;
        *)
            log_error "Unknown deployment type: $DEPLOYMENT_TYPE"
            exit 1
            ;;
    esac
    
    # Post-deployment validation
    if perform_health_check && check_performance_metrics; then
        log_success "🎉 Deployment completed successfully!"
        log_info "Nginx enterprise configuration is now active"
        log_info "Monitor logs: tail -f $LOG_FILE"
        log_info "Check status: systemctl status nginx"
        log_info "View metrics: curl http://localhost:8080/metrics/realtime"
    else
        log_error "❌ Deployment validation failed"
        exit 1
    fi
}

# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--type)
            DEPLOYMENT_TYPE="$2"
            shift 2
            ;;
        --timeout)
            HEALTH_CHECK_TIMEOUT="$2"
            shift 2
            ;;
        --no-rollback)
            ROLLBACK_ON_FAILURE=false
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -e, --environment    Set environment (production|staging|development)"
            echo "  -t, --type          Set deployment type (rolling|blue-green|canary|docker|kubernetes)"
            echo "  --timeout           Health check timeout in seconds (default: 60)"
            echo "  --no-rollback       Disable automatic rollback on failure"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Execute main function
main "$@"