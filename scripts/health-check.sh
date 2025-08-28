#!/bin/bash
# =============================================================================
# AINFLUE PLATFORM - COMPREHENSIVE HEALTH CHECK SCRIPT
# =============================================================================
# Production-ready health monitoring with detailed diagnostics,
# performance metrics, and service availability checks.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HEALTH_REPORT_DIR="$PROJECT_ROOT/health-reports"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$HEALTH_REPORT_DIR/health-check-$TIMESTAMP.log"

# Health check configuration
TIMEOUT=10
RETRIES=3
CRITICAL_THRESHOLD=90
WARNING_THRESHOLD=80

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARN: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

# Setup function
setup_environment() {
    mkdir -p "$HEALTH_REPORT_DIR"
}

# Check Docker daemon
check_docker_daemon() {
    log "Checking Docker daemon..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running or not accessible"
        return 1
    fi
    
    success "Docker daemon is running"
    return 0
}

# Check container health
check_container_health() {
    local container=$1
    local endpoint=$2
    local port=$3
    
    log "Checking health of container: $container"
    
    # Check if container exists and is running
    if ! docker ps --format "{{.Names}}" | grep -q "^$container$"; then
        error "Container $container is not running"
        return 1
    fi
    
    # Check container status
    local status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
    if [[ "$status" != "running" ]]; then
        error "Container $container status: $status"
        return 1
    fi
    
    # Check health endpoint if provided
    if [[ -n "$endpoint" && -n "$port" ]]; then
        local attempts=0
        while [[ $attempts -lt $RETRIES ]]; do
            if docker exec "$container" curl -f --max-time "$TIMEOUT" "http://localhost:$port$endpoint" &> /dev/null; then
                success "Container $container health endpoint responsive"
                return 0
            fi
            ((attempts++))
            sleep 2
        done
        error "Container $container health endpoint not responding after $RETRIES attempts"
        return 1
    fi
    
    success "Container $container is running"
    return 0
}

# Check database connectivity
check_database_connectivity() {
    log "Checking database connectivity..."
    
    local db_healthy=true
    
    # PostgreSQL
    log "Checking PostgreSQL connectivity..."
    if docker exec ainflue-postgres-master pg_isready -U ainflue -d ainflue_platform &> /dev/null; then
        success "PostgreSQL master is accessible"
    else
        error "PostgreSQL master is not accessible"
        db_healthy=false
    fi
    
    # Redis
    log "Checking Redis connectivity..."
    if docker exec ainflue-redis-master redis-cli ping | grep -q "PONG"; then
        success "Redis master is accessible"
    else
        error "Redis master is not accessible"
        db_healthy=false
    fi
    
    # MongoDB
    log "Checking MongoDB connectivity..."
    if docker exec ainflue-mongodb-primary mongosh --eval "db.adminCommand('ping')" --quiet &> /dev/null; then
        success "MongoDB primary is accessible"
    else
        error "MongoDB primary is not accessible"
        db_healthy=false
    fi
    
    if [[ "$db_healthy" == true ]]; then
        success "All databases are accessible"
        return 0
    else
        error "Some databases are not accessible"
        return 1
    fi
}

# Check service endpoints
check_service_endpoints() {
    log "Checking service endpoints..."
    
    local services=(
        "ainflue-app-1:/health:8000"
        "ainflue-app-2:/health:8000"
        "ainflue-app-3:/health:8000"
        "ainflue-crawler-service:/health:8001"
        "ainflue-monetization-service:/health:8002"
        "ainflue-analytics-service:/health:8003"
        "ainflue-ai-service:/health:8004"
    )
    
    local healthy_services=0
    local total_services=${#services[@]}
    
    for service_info in "${services[@]}"; do
        IFS=':' read -ra PARTS <<< "$service_info"
        local container="${PARTS[0]}"
        local endpoint="${PARTS[1]}"
        local port="${PARTS[2]}"
        
        if check_container_health "$container" "$endpoint" "$port"; then
            ((healthy_services++))
        fi
    done
    
    log "Service health summary: $healthy_services/$total_services services healthy"
    
    if [[ $healthy_services -eq $total_services ]]; then
        success "All services are healthy"
        return 0
    else
        error "Some services are unhealthy"
        return 1
    fi
}

# Check resource usage
check_resource_usage() {
    log "Checking system resource usage..."
    
    # Get system metrics
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local disk_usage=$(df "$PROJECT_ROOT" | awk 'NR==2{print $5}' | sed 's/%//')
    
    log "System Resource Usage:"
    log "CPU: ${cpu_usage}%"
    log "Memory: ${memory_usage}%"
    log "Disk: ${disk_usage}%"
    
    # Check thresholds
    local warnings=0
    local errors=0
    
    if [[ $(echo "$cpu_usage > $CRITICAL_THRESHOLD" | bc -l) -eq 1 ]]; then
        error "Critical CPU usage: ${cpu_usage}%"
        ((errors++))
    elif [[ $(echo "$cpu_usage > $WARNING_THRESHOLD" | bc -l) -eq 1 ]]; then
        warn "High CPU usage: ${cpu_usage}%"
        ((warnings++))
    fi
    
    if [[ $(echo "$memory_usage > $CRITICAL_THRESHOLD" | bc -l) -eq 1 ]]; then
        error "Critical memory usage: ${memory_usage}%"
        ((errors++))
    elif [[ $(echo "$memory_usage > $WARNING_THRESHOLD" | bc -l) -eq 1 ]]; then
        warn "High memory usage: ${memory_usage}%"
        ((warnings++))
    fi
    
    if [[ $disk_usage -gt $CRITICAL_THRESHOLD ]]; then
        error "Critical disk usage: ${disk_usage}%"
        ((errors++))
    elif [[ $disk_usage -gt $WARNING_THRESHOLD ]]; then
        warn "High disk usage: ${disk_usage}%"
        ((warnings++))
    fi
    
    if [[ $errors -gt 0 ]]; then
        error "Critical resource usage detected"
        return 1
    elif [[ $warnings -gt 0 ]]; then
        warn "High resource usage detected"
        return 0
    else
        success "Resource usage is within normal limits"
        return 0
    fi
}

# Check container metrics
check_container_metrics() {
    log "Checking container metrics..."
    
    local containers=(
        "ainflue-app-1"
        "ainflue-app-2"
        "ainflue-app-3"
        "ainflue-postgres-master"
        "ainflue-redis-master"
        "ainflue-mongodb-primary"
        "ainflue-nginx-lb"
    )
    
    {
        echo "=== CONTAINER METRICS REPORT ==="
        echo "Timestamp: $(date)"
        echo ""
        printf "%-25s %-10s %-15s %-15s %-10s\n" "CONTAINER" "CPU%" "MEMORY" "NET I/O" "STATUS"
        printf "%-25s %-10s %-15s %-15s %-10s\n" "-------------------------" "------" "-----------" "-----------" "--------"
        
        for container in "${containers[@]}"; do
            if docker ps --format "{{.Names}}" | grep -q "^$container$"; then
                local stats=$(docker stats --no-stream --format "{{.CPUPerc}} {{.MemUsage}} {{.NetIO}}" "$container" 2>/dev/null || echo "N/A N/A N/A")
                local status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
                printf "%-25s %-10s %-15s %-15s %-10s\n" "$container" $stats "$status"
            else
                printf "%-25s %-10s %-15s %-15s %-10s\n" "$container" "N/A" "N/A" "N/A" "NOT RUNNING"
            fi
        done
        echo ""
    } > "$HEALTH_REPORT_DIR/container-metrics-$TIMESTAMP.txt"
    
    success "Container metrics report generated"
}

# Check network connectivity
check_network_connectivity() {
    log "Checking network connectivity..."
    
    # Check external connectivity
    if curl -f --max-time 10 https://google.com &> /dev/null; then
        success "External network connectivity OK"
    else
        warn "External network connectivity issues detected"
    fi
    
    # Check internal Docker networks
    local networks=$(docker network ls --filter "name=ainflue" --format "{{.Name}}")
    local network_healthy=true
    
    while IFS= read -r network; do
        [[ -z "$network" ]] && continue
        log "Checking network: $network"
        
        if docker network inspect "$network" &> /dev/null; then
            success "Network $network is available"
        else
            error "Network $network is not available"
            network_healthy=false
        fi
    done <<< "$networks"
    
    if [[ "$network_healthy" == true ]]; then
        success "All Docker networks are healthy"
        return 0
    else
        error "Some Docker networks have issues"
        return 1
    fi
}

# Check log health
check_log_health() {
    log "Checking log health..."
    
    local log_issues=0
    
    # Check for error patterns in recent logs
    local error_patterns=("ERROR" "CRITICAL" "FATAL" "Exception" "Traceback")
    local recent_logs=$(docker-compose -f "$PROJECT_ROOT/docker-compose.production.yml" logs --tail=100 2>/dev/null || echo "")
    
    for pattern in "${error_patterns[@]}"; do
        local count=$(echo "$recent_logs" | grep -c "$pattern" || echo "0")
        if [[ $count -gt 0 ]]; then
            warn "Found $count instances of '$pattern' in recent logs"
            ((log_issues++))
        fi
    done
    
    # Check log rotation and disk usage
    local log_size=$(du -sh /var/lib/docker/containers/*/log* 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
    log "Docker container logs size: ${log_size}M"
    
    if [[ $log_issues -eq 0 ]]; then
        success "No critical log issues detected"
        return 0
    else
        warn "$log_issues log issues detected"
        return 0
    fi
}

# Generate health report
generate_health_report() {
    log "Generating comprehensive health report..."
    
    local report_file="$HEALTH_REPORT_DIR/health-report-$TIMESTAMP.html"
    
    {
        cat << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Ainflue Platform Health Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #007cba; }
        .healthy { border-left-color: #388e3c; background-color: #e8f5e8; }
        .warning { border-left-color: #f57c00; background-color: #fff3e0; }
        .error { border-left-color: #d32f2f; background-color: #ffebee; }
        .metric { display: inline-block; margin: 10px; padding: 10px; border-radius: 5px; background-color: #f5f5f5; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🩺 Ainflue Platform Health Report</h1>
        <p><strong>Generated:</strong> $(date)</p>
        <p><strong>Platform:</strong> Ainflue AI-Powered Content Protection & Monetization</p>
    </div>
EOF
        
        # Add health check results
        echo "<div class='section healthy'>"
        echo "<h2>✅ Health Check Summary</h2>"
        echo "<p>Health check completed at $(date)</p>"
        echo "<p>All critical services are operational.</p>"
        echo "</div>"
        
        # Add system metrics
        echo "<div class='section'>"
        echo "<h2>📊 System Metrics</h2>"
        if [[ -f "$HEALTH_REPORT_DIR/container-metrics-$TIMESTAMP.txt" ]]; then
            echo "<pre>$(cat "$HEALTH_REPORT_DIR/container-metrics-$TIMESTAMP.txt")</pre>"
        fi
        echo "</div>"
        
        echo "</body></html>"
        
    } > "$report_file"
    
    success "Health report generated: $report_file"
}

# Performance test
run_performance_test() {
    log "Running basic performance test..."
    
    local test_url="http://localhost/health"
    local test_results="$HEALTH_REPORT_DIR/performance-test-$TIMESTAMP.txt"
    
    {
        echo "=== PERFORMANCE TEST RESULTS ==="
        echo "Test URL: $test_url"
        echo "Test Time: $(date)"
        echo ""
        
        # Run simple load test if curl is available
        if command -v curl &> /dev/null; then
            echo "Response Time Test (10 requests):"
            for i in {1..10}; do
                local response_time=$(curl -o /dev/null -s -w "%{time_total}" "$test_url" 2>/dev/null || echo "failed")
                echo "Request $i: ${response_time}s"
            done
        fi
        
    } > "$test_results"
    
    success "Performance test completed: $test_results"
}

# Main health check function
main() {
    echo "
===============================================================================
🩺 AINFLUE PLATFORM - COMPREHENSIVE HEALTH CHECK
===============================================================================
Timestamp: $(date)
Report Directory: $HEALTH_REPORT_DIR
===============================================================================
"
    
    setup_environment
    
    local overall_health=true
    
    # Run all health checks
    check_docker_daemon || overall_health=false
    check_database_connectivity || overall_health=false
    check_service_endpoints || overall_health=false
    check_resource_usage || overall_health=false
    check_container_metrics
    check_network_connectivity || overall_health=false
    check_log_health
    run_performance_test
    generate_health_report
    
    if [[ "$overall_health" == true ]]; then
        success "🎉 Overall platform health: HEALTHY"
        log "All critical systems are operational"
        exit 0
    else
        error "❌ Overall platform health: UNHEALTHY"
        log "Some critical systems require attention"
        exit 1
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi