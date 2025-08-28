#!/bin/bash
# =============================================================================
# AINFLUE PLATFORM - CONTAINER SECURITY SCANNING SCRIPT
# =============================================================================
# Comprehensive security scanning for Docker images and containers
# with vulnerability assessment and compliance checking.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REPORT_DIR="$PROJECT_ROOT/security-reports"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$REPORT_DIR/security-scan-$TIMESTAMP.log"

# Security tools configuration
TRIVY_CACHE_DIR="$HOME/.cache/trivy"
CLAIR_CONFIG_FILE="$PROJECT_ROOT/security/clair-config.yaml"
DOCKER_BENCH_SCRIPT="/tmp/docker-bench-security.sh"

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
    log "Setting up security scanning environment..."
    
    # Create report directory
    mkdir -p "$REPORT_DIR"
    
    # Create Trivy cache directory
    mkdir -p "$TRIVY_CACHE_DIR"
    
    success "Environment setup completed"
}

# Install security tools
install_security_tools() {
    log "Installing/updating security scanning tools..."
    
    # Install Trivy if not present
    if ! command -v trivy &> /dev/null; then
        log "Installing Trivy vulnerability scanner..."
        
        # For Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y wget apt-transport-https gnupg lsb-release
            wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
            echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
            sudo apt-get update
            sudo apt-get install -y trivy
        else
            # Install via direct download
            curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
        fi
    fi
    
    # Download Docker Bench for Security
    if [[ ! -f "$DOCKER_BENCH_SCRIPT" ]]; then
        log "Downloading Docker Bench for Security..."
        curl -L https://raw.githubusercontent.com/docker/docker-bench-security/master/docker-bench-security.sh -o "$DOCKER_BENCH_SCRIPT"
        chmod +x "$DOCKER_BENCH_SCRIPT"
    fi
    
    success "Security tools installation completed"
}

# Scan individual image
scan_image() {
    local image=$1
    local report_prefix=$2
    
    log "Scanning image: $image"
    
    # Create image-specific report directory
    local image_report_dir="$REPORT_DIR/images/$report_prefix"
    mkdir -p "$image_report_dir"
    
    # Trivy vulnerability scan
    log "Running Trivy vulnerability scan on $image..."
    trivy image \
        --format json \
        --output "$image_report_dir/trivy-vulnerabilities.json" \
        --severity HIGH,CRITICAL \
        "$image" || warn "Trivy scan completed with warnings for $image"
    
    # Trivy configuration scan
    log "Running Trivy configuration scan on $image..."
    trivy config \
        --format json \
        --output "$image_report_dir/trivy-config.json" \
        "$image" || warn "Trivy config scan completed with warnings for $image"
    
    # Trivy secret scan
    log "Running Trivy secret scan on $image..."
    trivy image \
        --scanners secret \
        --format json \
        --output "$image_report_dir/trivy-secrets.json" \
        "$image" || warn "Trivy secret scan completed with warnings for $image"
    
    # Docker image history and inspection
    log "Analyzing Docker image metadata for $image..."
    docker history "$image" > "$image_report_dir/docker-history.txt" 2>/dev/null || warn "Failed to get history for $image"
    docker inspect "$image" > "$image_report_dir/docker-inspect.json" 2>/dev/null || warn "Failed to inspect $image"
    
    # Generate summary report
    generate_image_summary_report "$image" "$image_report_dir"
    
    success "Security scan completed for $image"
}

# Generate image summary report
generate_image_summary_report() {
    local image=$1
    local report_dir=$2
    local summary_file="$report_dir/security-summary.txt"
    
    {
        echo "=== SECURITY SCAN SUMMARY FOR $image ==="
        echo "Scan Date: $(date)"
        echo "Image: $image"
        echo ""
        
        # Vulnerability summary
        if [[ -f "$report_dir/trivy-vulnerabilities.json" ]]; then
            echo "=== VULNERABILITY SUMMARY ==="
            local critical_count=$(jq '.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL") | .VulnerabilityID' "$report_dir/trivy-vulnerabilities.json" 2>/dev/null | wc -l || echo "0")
            local high_count=$(jq '.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH") | .VulnerabilityID' "$report_dir/trivy-vulnerabilities.json" 2>/dev/null | wc -l || echo "0")
            echo "Critical Vulnerabilities: $critical_count"
            echo "High Vulnerabilities: $high_count"
            echo ""
        fi
        
        # Configuration issues
        if [[ -f "$report_dir/trivy-config.json" ]]; then
            echo "=== CONFIGURATION ISSUES ==="
            local config_issues=$(jq '.Results[]?.Misconfigurations[]?.Type' "$report_dir/trivy-config.json" 2>/dev/null | wc -l || echo "0")
            echo "Configuration Issues Found: $config_issues"
            echo ""
        fi
        
        # Secret scan results
        if [[ -f "$report_dir/trivy-secrets.json" ]]; then
            echo "=== SECRET SCAN RESULTS ==="
            local secrets_found=$(jq '.Results[]?.Secrets[]?.Title' "$report_dir/trivy-secrets.json" 2>/dev/null | wc -l || echo "0")
            echo "Potential Secrets Found: $secrets_found"
            echo ""
        fi
        
        # Image information
        echo "=== IMAGE INFORMATION ==="
        if [[ -f "$report_dir/docker-inspect.json" ]]; then
            echo "Image ID: $(jq -r '.[0].Id' "$report_dir/docker-inspect.json" 2>/dev/null || echo "N/A")"
            echo "Created: $(jq -r '.[0].Created' "$report_dir/docker-inspect.json" 2>/dev/null || echo "N/A")"
            echo "Size: $(jq -r '.[0].Size' "$report_dir/docker-inspect.json" 2>/dev/null | numfmt --to=iec 2>/dev/null || echo "N/A")"
            echo "Architecture: $(jq -r '.[0].Architecture' "$report_dir/docker-inspect.json" 2>/dev/null || echo "N/A")"
        fi
        
        echo ""
        echo "=== RECOMMENDATIONS ==="
        if [[ $critical_count -gt 0 ]]; then
            echo "❌ CRITICAL: $critical_count critical vulnerabilities found. Immediate action required."
        fi
        if [[ $high_count -gt 0 ]]; then
            echo "⚠️  HIGH: $high_count high severity vulnerabilities found. Update recommended."
        fi
        if [[ $critical_count -eq 0 && $high_count -eq 0 ]]; then
            echo "✅ GOOD: No critical or high severity vulnerabilities found."
        fi
        
    } > "$summary_file"
}

# Scan all Ainflue images
scan_ainflue_images() {
    log "Scanning all Ainflue platform images..."
    
    local images=(
        "ainflue/platform:latest:platform"
        "ainflue/ai:latest:ai-service"
        "ainflue/crawler:latest:crawler-service"
        "ainflue/analytics:latest:analytics-service"
        "ainflue/monetization:latest:monetization-service"
    )
    
    for image_info in "${images[@]}"; do
        local image="${image_info%:*:*}"
        local report_name="${image_info##*:}"
        
        # Check if image exists
        if docker inspect "$image" &> /dev/null; then
            scan_image "$image" "$report_name"
        else
            warn "Image $image not found, skipping scan"
        fi
    done
    
    success "All image scans completed"
}

# Run Docker Bench Security
run_docker_bench() {
    log "Running Docker Bench for Security..."
    
    local bench_report="$REPORT_DIR/docker-bench-security-$TIMESTAMP.log"
    
    if [[ -f "$DOCKER_BENCH_SCRIPT" ]]; then
        sudo "$DOCKER_BENCH_SCRIPT" > "$bench_report" 2>&1 || warn "Docker Bench completed with warnings"
        success "Docker Bench security scan completed. Report: $bench_report"
    else
        warn "Docker Bench script not found, skipping Docker host security scan"
    fi
}

# Container runtime security scan
scan_running_containers() {
    log "Scanning running containers for security issues..."
    
    local containers_report="$REPORT_DIR/running-containers-$TIMESTAMP.json"
    
    # Get running containers
    local running_containers=$(docker ps --format "{{.Names}}" | grep "ainflue" || true)
    
    if [[ -z "$running_containers" ]]; then
        warn "No running Ainflue containers found"
        return
    fi
    
    {
        echo "{"
        echo "  \"scan_time\": \"$(date -Iseconds)\","
        echo "  \"containers\": ["
        
        local first=true
        while IFS= read -r container; do
            [[ -z "$container" ]] && continue
            
            if [[ "$first" == true ]]; then
                first=false
            else
                echo ","
            fi
            
            echo "    {"
            echo "      \"name\": \"$container\","
            echo "      \"inspect\": $(docker inspect "$container" | jq '.[0]'),"
            echo "      \"stats\": $(timeout 5 docker stats --no-stream --format json "$container" 2>/dev/null || echo '{}'),"
            echo -n "      \"processes\": $(docker exec "$container" ps aux 2>/dev/null | jq -R . | jq -s . 2>/dev/null || echo '[]')"
            echo "    }"
            
        done <<< "$running_containers"
        
        echo "  ]"
        echo "}"
    } > "$containers_report"
    
    success "Container runtime scan completed. Report: $containers_report"
}

# Network security analysis
analyze_network_security() {
    log "Analyzing Docker network security..."
    
    local network_report="$REPORT_DIR/network-security-$TIMESTAMP.json"
    
    {
        echo "{"
        echo "  \"scan_time\": \"$(date -Iseconds)\","
        echo "  \"networks\": $(docker network ls --format json | jq -s .),"
        echo "  \"network_details\": ["
        
        local networks=$(docker network ls --filter "name=ainflue" --format "{{.Name}}")
        local first=true
        
        while IFS= read -r network; do
            [[ -z "$network" ]] && continue
            
            if [[ "$first" == true ]]; then
                first=false
            else
                echo ","
            fi
            
            echo "    $(docker network inspect "$network" | jq '.[0]')"
            
        done <<< "$networks"
        
        echo "  ]"
        echo "}"
    } > "$network_report"
    
    success "Network security analysis completed. Report: $network_report"
}

# Generate comprehensive security report
generate_comprehensive_report() {
    log "Generating comprehensive security report..."
    
    local comprehensive_report="$REPORT_DIR/comprehensive-security-report-$TIMESTAMP.html"
    
    {
        cat << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Ainflue Platform Security Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #007cba; }
        .critical { border-left-color: #d32f2f; background-color: #ffebee; }
        .warning { border-left-color: #f57c00; background-color: #fff3e0; }
        .good { border-left-color: #388e3c; background-color: #e8f5e8; }
        .code { background-color: #f5f5f5; padding: 10px; border-radius: 3px; font-family: monospace; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Ainflue Platform Security Report</h1>
        <p><strong>Generated:</strong> $(date)</p>
        <p><strong>Platform:</strong> Ainflue AI-Powered Content Protection & Monetization</p>
    </div>
EOF
        
        # Image scan summaries
        echo "<div class='section'>"
        echo "<h2>📋 Image Security Summary</h2>"
        echo "<table>"
        echo "<tr><th>Image</th><th>Critical</th><th>High</th><th>Status</th></tr>"
        
        for summary_file in "$REPORT_DIR"/images/*/security-summary.txt; do
            if [[ -f "$summary_file" ]]; then
                local image_name=$(grep "Image:" "$summary_file" | cut -d' ' -f2-)
                local critical=$(grep "Critical Vulnerabilities:" "$summary_file" | cut -d' ' -f3 || echo "0")
                local high=$(grep "High Vulnerabilities:" "$summary_file" | cut -d' ' -f3 || echo "0")
                
                local status_class="good"
                local status_text="✅ Good"
                
                if [[ $critical -gt 0 ]]; then
                    status_class="critical"
                    status_text="❌ Critical Issues"
                elif [[ $high -gt 0 ]]; then
                    status_class="warning"
                    status_text="⚠️ High Issues"
                fi
                
                echo "<tr class='$status_class'>"
                echo "<td>$image_name</td>"
                echo "<td>$critical</td>"
                echo "<td>$high</td>"
                echo "<td>$status_text</td>"
                echo "</tr>"
            fi
        done
        
        echo "</table>"
        echo "</div>"
        
        # Security recommendations
        echo "<div class='section'>"
        echo "<h2>📝 Security Recommendations</h2>"
        echo "<ul>"
        echo "<li>Regularly update base images to latest versions</li>"
        echo "<li>Implement automated vulnerability scanning in CI/CD pipeline</li>"
        echo "<li>Use minimal base images (alpine, distroless) where possible</li>"
        echo "<li>Enable Docker Content Trust for image signing</li>"
        echo "<li>Implement runtime security monitoring</li>"
        echo "<li>Regular security audits and penetration testing</li>"
        echo "</ul>"
        echo "</div>"
        
        echo "</body></html>"
        
    } > "$comprehensive_report"
    
    success "Comprehensive security report generated: $comprehensive_report"
}

# Main scanning function
main() {
    echo "
===============================================================================
🔒 AINFLUE PLATFORM - SECURITY SCANNING SUITE
===============================================================================
Timestamp: $(date)
Report Directory: $REPORT_DIR
===============================================================================
"
    
    setup_environment
    install_security_tools
    scan_ainflue_images
    run_docker_bench
    scan_running_containers
    analyze_network_security
    generate_comprehensive_report
    
    success "🎉 Security scanning completed successfully!"
    log "Reports available in: $REPORT_DIR"
    log "Comprehensive report: $REPORT_DIR/comprehensive-security-report-$TIMESTAMP.html"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi