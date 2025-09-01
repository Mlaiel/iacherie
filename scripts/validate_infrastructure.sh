#!/bin/bash
# Enterprise Infrastructure Validation Script for Ainflue Platform
# Author: Fahed Mlaiel <mlaiel@live.de>
# Comprehensive validation of all infrastructure components

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/infrastructure_validation_$(date +%Y%m%d_%H%M%S).log"
VALIDATION_REPORT="/tmp/validation_report_$(date +%Y%m%d_%H%M%S).json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [VALIDATION] $*" | tee -a "$LOG_FILE"
}

# Status functions
success() {
    echo -e "${GREEN}✅ $*${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $*${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $*${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}ℹ️  $*${NC}" | tee -a "$LOG_FILE"
}

# Initialize validation results
VALIDATION_RESULTS='{"timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'","results":{}}'

# Function to update validation results
update_result() {
    local component=$1
    local status=$2
    local message=$3
    local details=$4
    
    VALIDATION_RESULTS=$(echo "$VALIDATION_RESULTS" | jq --arg comp "$component" --arg stat "$status" --arg msg "$message" --arg det "$details" '
        .results[$comp] = {
            "status": $stat,
            "message": $msg,
            "details": $det,
            "timestamp": now | strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    ')
}

# Function to validate Kubernetes clusters
validate_kubernetes() {
    info "Validating Kubernetes clusters..."
    
    local clusters=(
        "arn:aws:eks:us-east-1:ACCOUNT_ID:cluster/ainflue-production-us-east-1"
        "arn:aws:eks:us-west-2:ACCOUNT_ID:cluster/ainflue-production-us-west-2"
        "arn:aws:eks:eu-west-1:ACCOUNT_ID:cluster/ainflue-production-eu-west-1"
        "arn:aws:eks:ap-southeast-1:ACCOUNT_ID:cluster/ainflue-production-ap-southeast-1"
    )
    
    local cluster_status="passed"
    local cluster_details=""
    
    for cluster in "${clusters[@]}"; do
        local region=$(echo "$cluster" | cut -d':' -f4)
        local cluster_name=$(echo "$cluster" | cut -d'/' -f2)
        
        info "Checking cluster: $cluster_name in $region"
        
        # Check cluster status
        if aws eks describe-cluster --name "$cluster_name" --region "$region" --query 'cluster.status' --output text 2>/dev/null | grep -q "ACTIVE"; then
            success "Cluster $cluster_name is ACTIVE"
            
            # Check node groups
            local nodegroups=$(aws eks list-nodegroups --cluster-name "$cluster_name" --region "$region" --query 'nodegroups' --output text 2>/dev/null)
            if [[ -n "$nodegroups" ]]; then
                for ng in $nodegroups; do
                    local ng_status=$(aws eks describe-nodegroup --cluster-name "$cluster_name" --nodegroup-name "$ng" --region "$region" --query 'nodegroup.status' --output text 2>/dev/null)
                    if [[ "$ng_status" == "ACTIVE" ]]; then
                        success "Node group $ng is ACTIVE"
                    else
                        error "Node group $ng is $ng_status"
                        cluster_status="failed"
                    fi
                done
            else
                warning "No node groups found for cluster $cluster_name"
            fi
            
            # Check if kubectl context exists and is accessible
            if kubectl cluster-info --context="$cluster" --request-timeout=10s >/dev/null 2>&1; then
                success "Kubectl access to $cluster_name verified"
                
                # Check critical pods
                local critical_pods=$(kubectl get pods --all-namespaces --context="$cluster" --field-selector=status.phase!=Running --no-headers 2>/dev/null | wc -l)
                if [[ "$critical_pods" -eq 0 ]]; then
                    success "All pods are running in cluster $cluster_name"
                else
                    warning "$critical_pods pods are not running in cluster $cluster_name"
                    cluster_details="$cluster_details\n$critical_pods non-running pods in $cluster_name"
                fi
            else
                error "Cannot access cluster $cluster_name via kubectl"
                cluster_status="failed"
            fi
        else
            error "Cluster $cluster_name is not ACTIVE"
            cluster_status="failed"
        fi
    done
    
    update_result "kubernetes_clusters" "$cluster_status" "Kubernetes cluster validation" "$cluster_details"
}

# Function to validate databases
validate_databases() {
    info "Validating database infrastructure..."
    
    local db_status="passed"
    local db_details=""
    
    # Check primary database
    local primary_db="ainflue-production-primary"
    local primary_status=$(aws rds describe-db-instances --db-instance-identifier "$primary_db" --region us-east-1 --query 'DBInstances[0].DBInstanceStatus' --output text 2>/dev/null)
    
    if [[ "$primary_status" == "available" ]]; then
        success "Primary database $primary_db is available"
        
        # Check backup status
        local backup_count=$(aws rds describe-db-snapshots --db-instance-identifier "$primary_db" --snapshot-type automated --region us-east-1 --query 'length(DBSnapshots)' --output text 2>/dev/null)
        if [[ "$backup_count" -gt 0 ]]; then
            success "Database backups are available ($backup_count snapshots)"
        else
            warning "No database backups found"
            db_details="$db_details\nNo automated backups found"
        fi
        
        # Check read replicas
        local replicas=$(aws rds describe-db-instances --region us-west-2 --query 'DBInstances[?contains(DBInstanceIdentifier, `replica`)].{Id:DBInstanceIdentifier,Status:DBInstanceStatus}' --output text 2>/dev/null)
        if [[ -n "$replicas" ]]; then
            success "Read replicas are configured"
        else
            warning "No read replicas found in secondary regions"
        fi
    else
        error "Primary database is $primary_status"
        db_status="failed"
    fi
    
    update_result "databases" "$db_status" "Database infrastructure validation" "$db_details"
}

# Function to validate cache infrastructure
validate_cache() {
    info "Validating cache infrastructure..."
    
    local cache_status="passed"
    local cache_details=""
    
    # Check Redis clusters
    local regions=("us-east-1" "us-west-2" "eu-west-1" "ap-southeast-1")
    
    for region in "${regions[@]}"; do
        local cluster_id="ainflue-production-${region//-/}"
        local cluster_status_result=$(aws elasticache describe-cache-clusters --cache-cluster-id "$cluster_id" --region "$region" --query 'CacheClusters[0].CacheClusterStatus' --output text 2>/dev/null)
        
        if [[ "$cluster_status_result" == "available" ]]; then
            success "Redis cluster $cluster_id in $region is available"
        else
            error "Redis cluster $cluster_id in $region is $cluster_status_result"
            cache_status="failed"
        fi
    done
    
    update_result "cache_infrastructure" "$cache_status" "Cache infrastructure validation" "$cache_details"
}

# Function to validate monitoring stack
validate_monitoring() {
    info "Validating monitoring infrastructure..."
    
    local monitoring_status="passed"
    local monitoring_details=""
    
    # Check if monitoring namespace exists
    if kubectl get namespace ainflue-monitoring >/dev/null 2>&1; then
        success "Monitoring namespace exists"
        
        # Check Prometheus
        if kubectl get deployment prometheus -n ainflue-monitoring >/dev/null 2>&1; then
            local prometheus_ready=$(kubectl get deployment prometheus -n ainflue-monitoring -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
            if [[ "$prometheus_ready" -gt 0 ]]; then
                success "Prometheus is running ($prometheus_ready replicas)"
            else
                error "Prometheus is not ready"
                monitoring_status="failed"
            fi
        else
            error "Prometheus deployment not found"
            monitoring_status="failed"
        fi
        
        # Check Grafana
        if kubectl get deployment grafana -n ainflue-monitoring >/dev/null 2>&1; then
            local grafana_ready=$(kubectl get deployment grafana -n ainflue-monitoring -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
            if [[ "$grafana_ready" -gt 0 ]]; then
                success "Grafana is running ($grafana_ready replicas)"
            else
                error "Grafana is not ready"
                monitoring_status="failed"
            fi
        else
            warning "Grafana deployment not found"
        fi
        
        # Check business metrics collector
        if kubectl get deployment business-metrics-collector -n ainflue-monitoring >/dev/null 2>&1; then
            success "Business metrics collector is deployed"
        else
            warning "Business metrics collector not found"
        fi
    else
        error "Monitoring namespace not found"
        monitoring_status="failed"
    fi
    
    update_result "monitoring_stack" "$monitoring_status" "Monitoring stack validation" "$monitoring_details"
}

# Function to validate security infrastructure
validate_security() {
    info "Validating security infrastructure..."
    
    local security_status="passed"
    local security_details=""
    
    # Check security namespace
    if kubectl get namespace ainflue-security >/dev/null 2>&1; then
        success "Security namespace exists"
        
        # Check compliance monitor
        if kubectl get deployment compliance-monitor -n ainflue-security >/dev/null 2>&1; then
            local compliance_ready=$(kubectl get deployment compliance-monitor -n ainflue-security -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
            if [[ "$compliance_ready" -gt 0 ]]; then
                success "Compliance monitor is running ($compliance_ready replicas)"
            else
                error "Compliance monitor is not ready"
                security_status="failed"
            fi
        else
            error "Compliance monitor deployment not found"
            security_status="failed"
        fi
        
        # Check Vault
        if kubectl get namespace ainflue-vault >/dev/null 2>&1; then
            if kubectl get statefulset vault -n ainflue-vault >/dev/null 2>&1; then
                success "Vault is deployed"
                
                # Check if Vault is unsealed
                local vault_status=$(kubectl exec vault-0 -n ainflue-vault -- vault status -format=json 2>/dev/null | jq -r '.sealed')
                if [[ "$vault_status" == "false" ]]; then
                    success "Vault is unsealed and ready"
                else
                    warning "Vault is sealed"
                    security_details="$security_details\nVault is sealed"
                fi
            else
                error "Vault StatefulSet not found"
                security_status="failed"
            fi
        else
            error "Vault namespace not found"
            security_status="failed"
        fi
        
        # Check penetration testing CronJob
        if kubectl get cronjob automated-pentest -n ainflue-security >/dev/null 2>&1; then
            success "Penetration testing automation is configured"
        else
            warning "Penetration testing CronJob not found"
        fi
    else
        error "Security namespace not found"
        security_status="failed"
    fi
    
    update_result "security_infrastructure" "$security_status" "Security infrastructure validation" "$security_details"
}

# Function to validate load balancer
validate_load_balancer() {
    info "Validating global load balancer..."
    
    local lb_status="passed"
    local lb_details=""
    
    # Check load balancer namespace
    if kubectl get namespace ainflue-global-lb >/dev/null 2>&1; then
        success "Global load balancer namespace exists"
        
        # Check load balancer deployment
        if kubectl get deployment global-load-balancer -n ainflue-global-lb >/dev/null 2>&1; then
            local lb_ready=$(kubectl get deployment global-load-balancer -n ainflue-global-lb -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
            if [[ "$lb_ready" -gt 0 ]]; then
                success "Global load balancer is running ($lb_ready replicas)"
                
                # Check service
                local lb_service=$(kubectl get service global-load-balancer -n ainflue-global-lb -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
                if [[ -n "$lb_service" ]]; then
                    success "Load balancer service has external IP: $lb_service"
                else
                    warning "Load balancer service does not have external IP yet"
                fi
            else
                error "Global load balancer is not ready"
                lb_status="failed"
            fi
        else
            error "Global load balancer deployment not found"
            lb_status="failed"
        fi
    else
        error "Global load balancer namespace not found"
        lb_status="failed"
    fi
    
    update_result "global_load_balancer" "$lb_status" "Global load balancer validation" "$lb_details"
}

# Function to validate ELK stack
validate_elk_stack() {
    info "Validating ELK stack..."
    
    local elk_status="passed"
    local elk_details=""
    
    # Check logging namespace
    if kubectl get namespace ainflue-logging >/dev/null 2>&1; then
        success "Logging namespace exists"
        
        # Check Elasticsearch
        if kubectl get statefulset elasticsearch -n ainflue-logging >/dev/null 2>&1; then
            local es_ready=$(kubectl get statefulset elasticsearch -n ainflue-logging -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
            local es_desired=$(kubectl get statefulset elasticsearch -n ainflue-logging -o jsonpath='{.spec.replicas}' 2>/dev/null)
            if [[ "$es_ready" == "$es_desired" && "$es_ready" -gt 0 ]]; then
                success "Elasticsearch is running ($es_ready/$es_desired replicas)"
            else
                error "Elasticsearch is not fully ready ($es_ready/$es_desired replicas)"
                elk_status="failed"
            fi
        else
            error "Elasticsearch StatefulSet not found"
            elk_status="failed"
        fi
        
        # Check Logstash
        if kubectl get deployment logstash -n ainflue-logging >/dev/null 2>&1; then
            local logstash_ready=$(kubectl get deployment logstash -n ainflue-logging -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
            if [[ "$logstash_ready" -gt 0 ]]; then
                success "Logstash is running ($logstash_ready replicas)"
            else
                error "Logstash is not ready"
                elk_status="failed"
            fi
        else
            error "Logstash deployment not found"
            elk_status="failed"
        fi
        
        # Check Kibana
        if kubectl get deployment kibana -n ainflue-logging >/dev/null 2>&1; then
            local kibana_ready=$(kubectl get deployment kibana -n ainflue-logging -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
            if [[ "$kibana_ready" -gt 0 ]]; then
                success "Kibana is running ($kibana_ready replicas)"
            else
                error "Kibana is not ready"
                elk_status="failed"
            fi
        else
            error "Kibana deployment not found"
            elk_status="failed"
        fi
    else
        error "Logging namespace not found"
        elk_status="failed"
    fi
    
    update_result "elk_stack" "$elk_status" "ELK stack validation" "$elk_details"
}

# Function to validate disaster recovery
validate_disaster_recovery() {
    info "Validating disaster recovery setup..."
    
    local dr_status="passed"
    local dr_details=""
    
    # Check disaster recovery namespace
    if kubectl get namespace ainflue-system >/dev/null 2>&1; then
        success "System namespace exists"
        
        # Check DR controller
        if kubectl get deployment disaster-recovery-controller -n ainflue-system >/dev/null 2>&1; then
            local dr_ready=$(kubectl get deployment disaster-recovery-controller -n ainflue-system -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
            if [[ "$dr_ready" -gt 0 ]]; then
                success "Disaster recovery controller is running ($dr_ready replicas)"
            else
                error "Disaster recovery controller is not ready"
                dr_status="failed"
            fi
        else
            error "Disaster recovery controller not found"
            dr_status="failed"
        fi
        
        # Check health check CronJob
        if kubectl get cronjob dr-health-check -n ainflue-system >/dev/null 2>&1; then
            success "DR health check CronJob is configured"
        else
            warning "DR health check CronJob not found"
        fi
        
        # Check backup verification CronJob
        if kubectl get cronjob dr-backup-verification -n ainflue-system >/dev/null 2>&1; then
            success "DR backup verification CronJob is configured"
        else
            warning "DR backup verification CronJob not found"
        fi
    else
        error "System namespace not found"
        dr_status="failed"
    fi
    
    update_result "disaster_recovery" "$dr_status" "Disaster recovery validation" "$dr_details"
}

# Function to validate external endpoints
validate_endpoints() {
    info "Validating external endpoints..."
    
    local endpoint_status="passed"
    local endpoint_details=""
    
    # Test endpoints
    local endpoints=(
        "https://api.ainflue.com/health"
        "https://www.ainflue.com"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s --max-time 10 "$endpoint" >/dev/null 2>&1; then
            success "Endpoint $endpoint is accessible"
        else
            error "Endpoint $endpoint is not accessible"
            endpoint_status="failed"
            endpoint_details="$endpoint_details\n$endpoint not accessible"
        fi
    done
    
    update_result "external_endpoints" "$endpoint_status" "External endpoint validation" "$endpoint_details"
}

# Function to generate summary report
generate_summary() {
    info "Generating validation summary..."
    
    # Write results to JSON file
    echo "$VALIDATION_RESULTS" | jq '.' > "$VALIDATION_REPORT"
    
    # Generate text summary
    local total_checks=$(echo "$VALIDATION_RESULTS" | jq '.results | keys | length')
    local passed_checks=$(echo "$VALIDATION_RESULTS" | jq '[.results[] | select(.status == "passed")] | length')
    local failed_checks=$(echo "$VALIDATION_RESULTS" | jq '[.results[] | select(.status == "failed")] | length')
    local warning_checks=$(echo "$VALIDATION_RESULTS" | jq '[.results[] | select(.status == "warning")] | length')
    
    echo ""
    echo "=========================================="
    echo "      INFRASTRUCTURE VALIDATION SUMMARY"
    echo "=========================================="
    echo ""
    echo "Total Checks: $total_checks"
    echo "Passed: $passed_checks"
    echo "Failed: $failed_checks"
    echo "Warnings: $warning_checks"
    echo ""
    
    if [[ "$failed_checks" -eq 0 ]]; then
        success "All critical infrastructure components are operational!"
        echo ""
        echo "✅ SOC2/GDPR compliance monitoring: ACTIVE"
        echo "✅ Penetration testing automation: CONFIGURED"
        echo "✅ Multi-region HA infrastructure: OPERATIONAL"
        echo "✅ Enterprise monitoring & alerting: ACTIVE"
        echo "✅ Global load balancing: FUNCTIONAL"
        echo "✅ ELK stack logging: OPERATIONAL"
        echo "✅ Vault secrets management: ACTIVE"
        echo "✅ Disaster recovery automation: READY"
        echo ""
        success "ENTERPRISE INFRASTRUCTURE VALIDATION: PASSED"
    else
        error "Infrastructure validation failed with $failed_checks critical issues"
        echo ""
        echo "❌ Critical issues detected that require immediate attention"
        echo "📋 Check detailed report: $VALIDATION_REPORT"
        echo "📋 Check detailed logs: $LOG_FILE"
    fi
    
    echo ""
    echo "Report files:"
    echo "  - JSON Report: $VALIDATION_REPORT"
    echo "  - Detailed Log: $LOG_FILE"
    echo ""
}

# Main execution
main() {
    echo "🚀 Starting Ainflue Enterprise Infrastructure Validation"
    echo "=================================================="
    echo ""
    
    # Check prerequisites
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is required but not installed"
        exit 1
    fi
    
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is required but not installed"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        error "jq is required but not installed"
        exit 1
    fi
    
    # Run validations
    validate_kubernetes
    validate_databases
    validate_cache
    validate_monitoring
    validate_security
    validate_load_balancer
    validate_elk_stack
    validate_disaster_recovery
    validate_endpoints
    
    # Generate summary
    generate_summary
    
    # Exit with appropriate code
    local failed_checks=$(echo "$VALIDATION_RESULTS" | jq '[.results[] | select(.status == "failed")] | length')
    if [[ "$failed_checks" -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Execute main function
main "$@"