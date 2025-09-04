#!/bin/bash
# Load Testing Runner Script for IA-Influencer Platform
# Supports both K6 and JMeter for 10K+ concurrent users
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

set -euo pipefail

# Default configuration
DEFAULT_BASE_URL="http://localhost:8000"
DEFAULT_USERS=10000
DEFAULT_DURATION="30m"
DEFAULT_TOOL="k6"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Usage function
usage() {
    echo "🚀 IA-Influencer Load Testing Runner"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -u, --url URL          Base URL (default: $DEFAULT_BASE_URL)"
    echo "  -n, --users NUM        Number of concurrent users (default: $DEFAULT_USERS)"
    echo "  -d, --duration TIME    Test duration (default: $DEFAULT_DURATION)"
    echo "  -t, --tool TOOL        Testing tool: k6|jmeter|both (default: $DEFAULT_TOOL)"
    echo "  -r, --report-dir DIR   Report output directory (default: ./reports)"
    echo "  -c, --config FILE      Custom configuration file"
    echo "  -h, --help            Show this help message"
    echo
    echo "Examples:"
    echo "  $0 --users 1000 --duration 10m --tool k6"
    echo "  $0 --url https://api.ainflue.com --users 10000 --tool both"
    echo "  $0 --config load_test_config.json"
    echo
}

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    local missing_tools=()
    
    if [[ "$TOOL" == "k6" || "$TOOL" == "both" ]]; then
        if ! command_exists k6; then
            missing_tools+=("k6")
        fi
    fi
    
    if [[ "$TOOL" == "jmeter" || "$TOOL" == "both" ]]; then
        if ! command_exists jmeter; then
            missing_tools+=("jmeter")
        fi
    fi
    
    if ! command_exists curl; then
        missing_tools+=("curl")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log "Please install the missing tools and try again."
        
        log "Installation hints:"
        for tool in "${missing_tools[@]}"; do
            case $tool in
                k6)
                    log "  K6: https://k6.io/docs/getting-started/installation/"
                    ;;
                jmeter)
                    log "  JMeter: https://jmeter.apache.org/download_jmeter.cgi"
                    ;;
                curl)
                    log "  curl: Usually available via package manager (apt, yum, brew)"
                    ;;
            esac
        done
        
        exit 1
    fi
    
    log_success "All prerequisites satisfied"
}

# Health check
health_check() {
    log "Performing health check on $BASE_URL..."
    
    local health_url="$BASE_URL/health"
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$health_url" > /dev/null 2>&1; then
            log_success "Application is healthy and ready for testing"
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, retrying in 5 seconds..."
        sleep 5
        ((attempt++))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    log_error "Please ensure the application is running at $BASE_URL"
    exit 1
}

# Create report directory
create_report_dir() {
    if [[ ! -d "$REPORT_DIR" ]]; then
        mkdir -p "$REPORT_DIR"
        log "Created report directory: $REPORT_DIR"
    fi
}

# Run K6 test
run_k6_test() {
    log "🎯 Starting K6 load test..."
    log "Configuration:"
    log "  - Users: $USERS"
    log "  - Duration: $DURATION"
    log "  - Base URL: $BASE_URL"
    
    local k6_script="$(dirname "$0")/k6/load_test_10k.js"
    local k6_report="$REPORT_DIR/k6_results_$(date +%Y%m%d_%H%M%S)"
    
    if [[ ! -f "$k6_script" ]]; then
        log_error "K6 script not found: $k6_script"
        return 1
    fi
    
    # K6 environment variables
    export BASE_URL="$BASE_URL"
    
    # Run K6 test
    k6 run \
        --vus "$USERS" \
        --duration "$DURATION" \
        --out json="$k6_report.json" \
        --out csv="$k6_report.csv" \
        --summary-export="$k6_report.summary.json" \
        "$k6_script" | tee "$k6_report.log"
    
    local k6_exit_code=$?
    
    if [[ $k6_exit_code -eq 0 ]]; then
        log_success "K6 test completed successfully"
        log "Reports saved to: $k6_report.*"
    else
        log_error "K6 test failed with exit code: $k6_exit_code"
        return 1
    fi
    
    return 0
}

# Run JMeter test
run_jmeter_test() {
    log "🎯 Starting JMeter load test..."
    log "Configuration:"
    log "  - Users: $USERS"
    log "  - Duration: $DURATION"
    log "  - Base URL: $BASE_URL"
    
    local jmeter_script="$(dirname "$0")/jmeter/load_test_10k.jmx"
    local jmeter_report="$REPORT_DIR/jmeter_results_$(date +%Y%m%d_%H%M%S)"
    
    if [[ ! -f "$jmeter_script" ]]; then
        log_error "JMeter script not found: $jmeter_script"
        return 1
    fi
    
    # Convert duration to seconds for JMeter
    local duration_seconds
    case $DURATION in
        *m) duration_seconds=$((${DURATION%m} * 60)) ;;
        *h) duration_seconds=$((${DURATION%h} * 3600)) ;;
        *s) duration_seconds=${DURATION%s} ;;
        *) duration_seconds=1800 ;; # Default 30 minutes
    esac
    
    # Run JMeter test
    jmeter -n \
        -t "$jmeter_script" \
        -l "$jmeter_report.jtl" \
        -e -o "$jmeter_report" \
        -Jbase_url="$BASE_URL" \
        -Jusers="$USERS" \
        -Jduration="$duration_seconds" \
        -Jramp_up=300
    
    local jmeter_exit_code=$?
    
    if [[ $jmeter_exit_code -eq 0 ]]; then
        log_success "JMeter test completed successfully"
        log "Reports saved to: $jmeter_report"
        log "HTML report: $jmeter_report/index.html"
    else
        log_error "JMeter test failed with exit code: $jmeter_exit_code"
        return 1
    fi
    
    return 0
}

# Generate summary report
generate_summary() {
    log "📊 Generating test summary..."
    
    local summary_file="$REPORT_DIR/load_test_summary_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$summary_file" << EOF
# Load Test Summary - IA-Influencer Platform

**Test Date:** $(date)
**Test Duration:** $DURATION
**Concurrent Users:** $USERS
**Base URL:** $BASE_URL
**Testing Tool(s):** $TOOL

## Test Configuration

- **Target Load:** $USERS concurrent users
- **Test Duration:** $DURATION
- **Ramp-up Strategy:** Gradual increase over 15 minutes
- **User Behavior:** Mixed (30% creators, 30% consumers, 20% brands, 20% admins)

## Performance Thresholds

- **Response Time P95:** < 500ms
- **Response Time P99:** < 1000ms
- **Error Rate:** < 5%
- **Throughput:** > 1000 RPS

## Test Scenarios

### Content Creators (30%)
- User authentication
- Content upload
- Analytics dashboard access
- Content protection management

### Content Consumers (30%)
- Content browsing
- Search functionality
- Content detail views

### Brand Users (20%)
- Influencer search
- Collaboration management
- Campaign analytics

### Admin Users (20%)
- Platform monitoring
- Content moderation
- System metrics

## Reports Generated

EOF

    # Add report file listings
    if [[ "$TOOL" == "k6" || "$TOOL" == "both" ]]; then
        echo "### K6 Reports" >> "$summary_file"
        find "$REPORT_DIR" -name "k6_results_*" -type f | sort | while read -r file; do
            echo "- $(basename "$file")" >> "$summary_file"
        done
        echo >> "$summary_file"
    fi
    
    if [[ "$TOOL" == "jmeter" || "$TOOL" == "both" ]]; then
        echo "### JMeter Reports" >> "$summary_file"
        find "$REPORT_DIR" -name "jmeter_results_*" -type d | sort | while read -r dir; do
            echo "- $(basename "$dir")/index.html" >> "$summary_file"
        done
        echo >> "$summary_file"
    fi
    
    echo "## Next Steps" >> "$summary_file"
    echo >> "$summary_file"
    echo "1. Review response time percentiles" >> "$summary_file"
    echo "2. Analyze error rates and patterns" >> "$summary_file"
    echo "3. Check resource utilization during peak load" >> "$summary_file"
    echo "4. Identify bottlenecks and optimization opportunities" >> "$summary_file"
    echo "5. Plan capacity scaling based on results" >> "$summary_file"
    
    log_success "Summary report generated: $summary_file"
}

# Parse command line arguments
POSITIONAL_ARGS=()

BASE_URL="$DEFAULT_BASE_URL"
USERS="$DEFAULT_USERS"
DURATION="$DEFAULT_DURATION"
TOOL="$DEFAULT_TOOL"
REPORT_DIR="./reports"
CONFIG_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            BASE_URL="$2"
            shift 2
            ;;
        -n|--users)
            USERS="$2"
            shift 2
            ;;
        -d|--duration)
            DURATION="$2"
            shift 2
            ;;
        -t|--tool)
            TOOL="$2"
            shift 2
            ;;
        -r|--report-dir)
            REPORT_DIR="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

# Load config file if specified
if [[ -n "$CONFIG_FILE" && -f "$CONFIG_FILE" ]]; then
    log "Loading configuration from: $CONFIG_FILE"
    # Simple JSON parsing (requires jq in production)
    if command_exists jq; then
        BASE_URL=$(jq -r '.base_url // "'"$BASE_URL"'"' "$CONFIG_FILE")
        USERS=$(jq -r '.users // "'"$USERS"'"' "$CONFIG_FILE")
        DURATION=$(jq -r '.duration // "'"$DURATION"'"' "$CONFIG_FILE")
        TOOL=$(jq -r '.tool // "'"$TOOL"'"' "$CONFIG_FILE")
    else
        log_warning "jq not found, skipping JSON config file parsing"
    fi
fi

# Validate tool selection
if [[ "$TOOL" != "k6" && "$TOOL" != "jmeter" && "$TOOL" != "both" ]]; then
    log_error "Invalid tool selection: $TOOL. Must be one of: k6, jmeter, both"
    exit 1
fi

# Main execution
main() {
    log "🚀 Starting IA-Influencer Platform Load Testing"
    log "Tool: $TOOL | Users: $USERS | Duration: $DURATION | URL: $BASE_URL"
    
    check_prerequisites
    health_check
    create_report_dir
    
    local tests_failed=0
    
    if [[ "$TOOL" == "k6" || "$TOOL" == "both" ]]; then
        if ! run_k6_test; then
            ((tests_failed++))
        fi
    fi
    
    if [[ "$TOOL" == "jmeter" || "$TOOL" == "both" ]]; then
        if ! run_jmeter_test; then
            ((tests_failed++))
        fi
    fi
    
    generate_summary
    
    if [[ $tests_failed -eq 0 ]]; then
        log_success "🎉 All load tests completed successfully!"
        log "📊 Check the reports in: $REPORT_DIR"
    else
        log_error "❌ $tests_failed test(s) failed"
        exit 1
    fi
}

# Run main function
main "$@"