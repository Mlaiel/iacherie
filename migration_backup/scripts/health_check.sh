#!/bin/bash

# Ainflue Platform Health Check Script
# Comprehensive health monitoring for all platform components
# 
# Author: Fahed Mlaiel (mlaiel@live.de)
# Version: 1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="ainflue"
TIMEOUT=30
VERBOSE=false
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
EMAIL_RECIPIENTS="${EMAIL_RECIPIENTS:-mlaiel@live.de}"

# Health check results
OVERALL_STATUS="healthy"
FAILED_CHECKS=()
WARNING_CHECKS=()

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to record check result
record_result() {
    local check_name="$1"
    local status="$2"
    local message="$3"
    
    case $status in
        "success")
            print_success "$check_name: $message"
            ;;
        "warning")
            print_warning "$check_name: $message"
            WARNING_CHECKS+=("$check_name: $message")
            if [[ $OVERALL_STATUS == "healthy" ]]; then
                OVERALL_STATUS="warning"
            fi
            ;;
        "error")
            print_error "$check_name: $message"
            FAILED_CHECKS+=("$check_name: $message")
            OVERALL_STATUS="critical"
            ;;
    esac
}

# Check if kubectl is available and configured
check_kubectl() {
    print_status "Checking kubectl connectivity..."
    
    if ! command -v kubectl &> /dev/null; then
        record_result "kubectl" "error" "kubectl command not found"
        return 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        record_result "kubectl" "error" "Cannot connect to Kubernetes cluster"
        return 1
    fi
    
    record_result "kubectl" "success" "Kubernetes connectivity OK"
    return 0
}

# Check namespace existence
check_namespace() {
    print_status "Checking namespace '$NAMESPACE'..."
    
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        record_result "namespace" "success" "Namespace '$NAMESPACE' exists"
        return 0
    else
        record_result "namespace" "error" "Namespace '$NAMESPACE' not found"
        return 1
    fi
}

# Check API service health
check_api_service() {
    print_status "Checking API service health..."
    
    # Check if pods are running
    local ready_pods
    ready_pods=$(kubectl get pods -n "$NAMESPACE" -l app=ainflue-api --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    
    if [[ $ready_pods -eq 0 ]]; then
        record_result "api-pods" "error" "No API pods running"
        return 1
    fi
    
    # Check pod readiness
    local total_pods
    total_pods=$(kubectl get pods -n "$NAMESPACE" -l app=ainflue-api --no-headers 2>/dev/null | wc -l)
    
    if [[ $ready_pods -lt $total_pods ]]; then
        record_result "api-pods" "warning" "$ready_pods/$total_pods API pods ready"
    else
        record_result "api-pods" "success" "All $ready_pods API pods ready"
    fi
    
    # Check service endpoint
    local service_ip
    service_ip=$(kubectl get svc ainflue-api -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null)
    
    if [[ -n "$service_ip" ]]; then
        # Test health endpoint if possible
        if kubectl run health-check-temp --rm -i --restart=Never --image=curlimages/curl:latest -n "$NAMESPACE" -- curl -f -m 10 "http://$service_ip/health" &> /dev/null; then
            record_result "api-health" "success" "Health endpoint responding"
        else
            record_result "api-health" "warning" "Health endpoint not accessible"
        fi
    else
        record_result "api-service" "error" "API service not found"
        return 1
    fi
    
    return 0
}

# Check database health
check_databases() {
    print_status "Checking database health..."
    
    # PostgreSQL
    local pg_pods
    pg_pods=$(kubectl get pods -n "$NAMESPACE" -l app=ainflue-postgresql --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    
    if [[ $pg_pods -gt 0 ]]; then
        record_result "postgresql" "success" "$pg_pods PostgreSQL pods running"
    else
        record_result "postgresql" "error" "No PostgreSQL pods running"
    fi
    
    # Redis
    local redis_pods
    redis_pods=$(kubectl get pods -n "$NAMESPACE" -l app=ainflue-redis --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    
    if [[ $redis_pods -gt 0 ]]; then
        record_result "redis" "success" "$redis_pods Redis pods running"
    else
        record_result "redis" "error" "No Redis pods running"
    fi
    
    # MongoDB
    local mongo_pods
    mongo_pods=$(kubectl get pods -n "$NAMESPACE" -l app=ainflue-mongodb --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    
    if [[ $mongo_pods -gt 0 ]]; then
        record_result "mongodb" "success" "$mongo_pods MongoDB pods running"
    else
        record_result "mongodb" "error" "No MongoDB pods running"
    fi
}

# Check crawler service
check_crawler_service() {
    print_status "Checking crawler service..."
    
    local crawler_pods
    crawler_pods=$(kubectl get pods -n "$NAMESPACE" -l app=ainflue-crawler --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    
    if [[ $crawler_pods -gt 0 ]]; then
        record_result "crawler" "success" "$crawler_pods crawler pods running"
    else
        record_result "crawler" "warning" "No crawler pods running"
    fi
}

# Check analytics service
check_analytics_service() {
    print_status "Checking analytics service..."
    
    local analytics_pods
    analytics_pods=$(kubectl get pods -n "$NAMESPACE" -l app=ainflue-analytics --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    
    if [[ $analytics_pods -gt 0 ]]; then
        record_result "analytics" "success" "$analytics_pods analytics pods running"
    else
        record_result "analytics" "warning" "No analytics pods running"
    fi
}

# Check resource usage
check_resource_usage() {
    print_status "Checking resource usage..."
    
    # Check CPU usage
    local high_cpu_pods
    high_cpu_pods=$(kubectl top pods -n "$NAMESPACE" 2>/dev/null | awk 'NR>1 && $2 ~ /[0-9]+m/ {gsub(/m/, "", $2); if($2 > 1000) print $1}' | wc -l)
    
    if [[ $high_cpu_pods -gt 0 ]]; then
        record_result "cpu-usage" "warning" "$high_cpu_pods pods with high CPU usage"
    else
        record_result "cpu-usage" "success" "CPU usage within normal limits"
    fi
    
    # Check memory usage
    local high_memory_pods
    high_memory_pods=$(kubectl top pods -n "$NAMESPACE" 2>/dev/null | awk 'NR>1 && $3 ~ /[0-9]+Mi/ {gsub(/Mi/, "", $3); if($3 > 2000) print $1}' | wc -l)
    
    if [[ $high_memory_pods -gt 0 ]]; then
        record_result "memory-usage" "warning" "$high_memory_pods pods with high memory usage"
    else
        record_result "memory-usage" "success" "Memory usage within normal limits"
    fi
}

# Check ingress and external access
check_ingress() {
    print_status "Checking ingress configuration..."
    
    local ingress_ready
    ingress_ready=$(kubectl get ingress -n "$NAMESPACE" ainflue-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    
    if [[ -n "$ingress_ready" ]]; then
        record_result "ingress" "success" "Ingress has external IP: $ingress_ready"
        
        # Test external endpoint if available
        if curl -f -m 10 -s "https://api.ainflue.com/health" &> /dev/null; then
            record_result "external-access" "success" "External API endpoint accessible"
        else
            record_result "external-access" "warning" "External API endpoint not responding"
        fi
    else
        record_result "ingress" "warning" "Ingress not ready or no external IP"
    fi
}

# Check persistent volumes
check_storage() {
    print_status "Checking storage..."
    
    local pvc_issues
    pvc_issues=$(kubectl get pvc -n "$NAMESPACE" --no-headers 2>/dev/null | grep -v "Bound" | wc -l)
    
    if [[ $pvc_issues -eq 0 ]]; then
        local total_pvcs
        total_pvcs=$(kubectl get pvc -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
        record_result "storage" "success" "All $total_pvcs PVCs bound"
    else
        record_result "storage" "error" "$pvc_issues PVCs not bound"
    fi
}

# Check monitoring stack
check_monitoring() {
    print_status "Checking monitoring stack..."
    
    # Check Prometheus
    if kubectl get pods -n "$NAMESPACE" -l app=prometheus --field-selector=status.phase=Running --no-headers 2>/dev/null | grep -q prometheus; then
        record_result "prometheus" "success" "Prometheus running"
    else
        record_result "prometheus" "warning" "Prometheus not running"
    fi
    
    # Check Grafana
    if kubectl get pods -n "$NAMESPACE" -l app=grafana --field-selector=status.phase=Running --no-headers 2>/dev/null | grep -q grafana; then
        record_result "grafana" "success" "Grafana running"
    else
        record_result "grafana" "warning" "Grafana not running"
    fi
}

# Check recent events for issues
check_events() {
    print_status "Checking recent events..."
    
    local error_events
    error_events=$(kubectl get events -n "$NAMESPACE" --field-selector type=Warning --no-headers 2>/dev/null | wc -l)
    
    if [[ $error_events -eq 0 ]]; then
        record_result "events" "success" "No warning events in the last hour"
    elif [[ $error_events -lt 5 ]]; then
        record_result "events" "warning" "$error_events warning events found"
    else
        record_result "events" "error" "$error_events warning events found"
    fi
}

# Generate summary report
generate_summary() {
    echo ""
    echo "========================================="
    echo "     AINFLUE HEALTH CHECK SUMMARY"
    echo "========================================="
    echo "Overall Status: $OVERALL_STATUS"
    echo "Check Time: $(date)"
    echo ""
    
    if [[ ${#FAILED_CHECKS[@]} -gt 0 ]]; then
        echo "❌ FAILED CHECKS:"
        for check in "${FAILED_CHECKS[@]}"; do
            echo "  - $check"
        done
        echo ""
    fi
    
    if [[ ${#WARNING_CHECKS[@]} -gt 0 ]]; then
        echo "⚠️  WARNING CHECKS:"
        for check in "${WARNING_CHECKS[@]}"; do
            echo "  - $check"
        done
        echo ""
    fi
    
    case $OVERALL_STATUS in
        "healthy")
            echo -e "${GREEN}✅ All systems operational${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  Some issues detected, but system is functional${NC}"
            ;;
        "critical")
            echo -e "${RED}🚨 Critical issues detected, immediate attention required${NC}"
            ;;
    esac
    
    echo ""
    echo "========================================="
}

# Send notifications
send_notifications() {
    if [[ $OVERALL_STATUS != "healthy" ]]; then
        local message="Ainflue Health Check Alert - Status: $OVERALL_STATUS"
        
        # Slack notification
        if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
            local color
            case $OVERALL_STATUS in
                "warning") color="warning" ;;
                "critical") color="danger" ;;
            esac
            
            local payload=$(cat <<EOF
{
    "attachments": [
        {
            "color": "$color",
            "title": "Ainflue Health Check Alert",
            "fields": [
                {
                    "title": "Status",
                    "value": "$OVERALL_STATUS",
                    "short": true
                },
                {
                    "title": "Time",
                    "value": "$(date)",
                    "short": true
                },
                {
                    "title": "Failed Checks",
                    "value": "${#FAILED_CHECKS[@]}",
                    "short": true
                },
                {
                    "title": "Warning Checks", 
                    "value": "${#WARNING_CHECKS[@]}",
                    "short": true
                }
            ],
            "text": "$message"
        }
    ]
}
EOF
            )
            
            curl -X POST -H 'Content-type: application/json' \
                --data "$payload" \
                "$SLACK_WEBHOOK_URL" &> /dev/null || true
        fi
        
        # Email notification (if mail is available)
        if command -v mail &> /dev/null && [[ -n "$EMAIL_RECIPIENTS" ]]; then
            {
                echo "Subject: Ainflue Health Check Alert - $OVERALL_STATUS"
                echo ""
                generate_summary
            } | mail "$EMAIL_RECIPIENTS" || true
        fi
    fi
}

# Main execution
main() {
    echo "🏥 Starting Ainflue Platform Health Check..."
    echo "Namespace: $NAMESPACE"
    echo "Timestamp: $(date)"
    echo ""
    
    # Run all health checks
    check_kubectl || exit 1
    check_namespace || exit 1
    check_api_service
    check_databases
    check_crawler_service
    check_analytics_service
    check_resource_usage
    check_ingress
    check_storage
    check_monitoring
    check_events
    
    # Generate and display summary
    generate_summary
    
    # Send notifications if needed
    send_notifications
    
    # Exit with appropriate code
    case $OVERALL_STATUS in
        "healthy") exit 0 ;;
        "warning") exit 1 ;;
        "critical") exit 2 ;;
    esac
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            cat << EOF
Usage: $0 [OPTIONS]

Ainflue Platform Health Check Script

OPTIONS:
    -n, --namespace NAME    Kubernetes namespace [default: ainflue]
    -t, --timeout SECONDS  Timeout for operations [default: 30]
    -v, --verbose          Enable verbose output
    -h, --help             Show this help message

ENVIRONMENT VARIABLES:
    SLACK_WEBHOOK_URL      Slack webhook for notifications
    EMAIL_RECIPIENTS       Email addresses for notifications (comma-separated)

EXIT CODES:
    0  - All checks passed (healthy)
    1  - Some warnings detected (warning)
    2  - Critical issues found (critical)

EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main