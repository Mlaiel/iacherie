#!/bin/bash
# =============================================================================
# AINFLUE PLATFORM - SCALING AUTOMATION SCRIPT
# =============================================================================
# Intelligent scaling for Ainflue services based on load, metrics, and usage patterns.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

set -euo pipefail

# Configuration
METRICS_ENDPOINT="${METRICS_ENDPOINT:-http://localhost:9090}"
SCALE_UP_THRESHOLD="${SCALE_UP_THRESHOLD:-80}"
SCALE_DOWN_THRESHOLD="${SCALE_DOWN_THRESHOLD:-30}"
MAX_REPLICAS="${MAX_REPLICAS:-10}"
MIN_REPLICAS="${MIN_REPLICAS:-2}"
COOLDOWN_PERIOD="${COOLDOWN_PERIOD:-300}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

info() {
    log "${GREEN}[INFO]${NC} $1"
}

warn() {
    log "${YELLOW}[WARN]${NC} $1"
}

error() {
    log "${RED}[ERROR]${NC} $1"
}

# Function to get service metrics
get_service_metrics() {
    local service="$1"
    local metric_type="${2:-cpu}"
    
    case $metric_type in
        cpu)
            curl -s "${METRICS_ENDPOINT}/api/v1/query?query=rate(container_cpu_usage_seconds_total{name=~\"${service}.*\"}[5m])*100" | \
            jq -r '.data.result[0].value[1] // "0"'
            ;;
        memory)
            curl -s "${METRICS_ENDPOINT}/api/v1/query?query=container_memory_usage_bytes{name=~\"${service}.*\"}/container_spec_memory_limit_bytes{name=~\"${service}.*\"}*100" | \
            jq -r '.data.result[0].value[1] // "0"'
            ;;
        requests)
            curl -s "${METRICS_ENDPOINT}/api/v1/query?query=rate(http_requests_total{service=\"${service}\"}[5m])" | \
            jq -r '.data.result[0].value[1] // "0"'
            ;;
    esac
}

# Function to get current replica count
get_replica_count() {
    local service="$1"
    docker service ls --filter name="$service" --format "{{.Replicas}}" | cut -d'/' -f1
}

# Function to scale service
scale_service() {
    local service="$1"
    local target_replicas="$2"
    local current_replicas=$(get_replica_count "$service")
    
    if [[ "$current_replicas" != "$target_replicas" ]]; then
        info "Scaling $service from $current_replicas to $target_replicas replicas"
        docker service scale "${service}=${target_replicas}"
        
        # Record scaling event
        echo "$(date '+%Y-%m-%d %H:%M:%S'),${service},${current_replicas},${target_replicas}" >> /var/log/ainflue/scaling.log
    fi
}

# Function to make scaling decision
make_scaling_decision() {
    local service="$1"
    local cpu_usage=$(get_service_metrics "$service" "cpu")
    local memory_usage=$(get_service_metrics "$service" "memory")
    local request_rate=$(get_service_metrics "$service" "requests")
    local current_replicas=$(get_replica_count "$service")
    
    info "Service: $service | CPU: ${cpu_usage}% | Memory: ${memory_usage}% | Requests/s: $request_rate | Replicas: $current_replicas"
    
    # Scale up conditions
    if (( $(echo "$cpu_usage > $SCALE_UP_THRESHOLD" | bc -l) )) || \
       (( $(echo "$memory_usage > $SCALE_UP_THRESHOLD" | bc -l) )); then
        if [[ $current_replicas -lt $MAX_REPLICAS ]]; then
            local target_replicas=$((current_replicas + 1))
            scale_service "$service" "$target_replicas"
            return
        fi
    fi
    
    # Scale down conditions
    if (( $(echo "$cpu_usage < $SCALE_DOWN_THRESHOLD" | bc -l) )) && \
       (( $(echo "$memory_usage < $SCALE_DOWN_THRESHOLD" | bc -l) )); then
        if [[ $current_replicas -gt $MIN_REPLICAS ]]; then
            local target_replicas=$((current_replicas - 1))
            scale_service "$service" "$target_replicas"
            return
        fi
    fi
}

# Function to check cooldown
check_cooldown() {
    local service="$1"
    local last_scale_file="/tmp/ainflue-last-scale-${service}"
    
    if [[ -f "$last_scale_file" ]]; then
        local last_scale=$(cat "$last_scale_file")
        local current_time=$(date +%s)
        local time_diff=$((current_time - last_scale))
        
        if [[ $time_diff -lt $COOLDOWN_PERIOD ]]; then
            return 1  # Still in cooldown
        fi
    fi
    
    echo "$(date +%s)" > "$last_scale_file"
    return 0
}

# Main scaling loop
main() {
    info "Starting Ainflue auto-scaling service..."
    
    # Define services to monitor
    local services=(
        "ainflue-audio-processing"
        "ainflue-protection-service"
        "ainflue-revenue-tracker"
        "ainflue-payment-processor"
        "ainflue-fingerprinting-engine"
    )
    
    while true; do
        for service in "${services[@]}"; do
            if check_cooldown "$service"; then
                make_scaling_decision "$service"
            else
                info "Service $service is in cooldown period"
            fi
        done
        
        info "Scaling check completed. Sleeping for 60 seconds..."
        sleep 60
    done
}

# Handle termination signals
trap 'info "Scaling service stopped"; exit 0' SIGTERM SIGINT

# Run main function
main "$@"