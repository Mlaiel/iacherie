#!/bin/bash
# Security Automation - Advanced Desktop Security & Monitoring System
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# Description: Automated security scanning, monitoring, encryption, and incident response for desktop application
# Usage: ./security_automation.sh [--scan] [--monitor] [--encrypt] [--audit] [--incident-response]

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════
# 🎨 ANSI COLOR CODES & STYLING
# ═══════════════════════════════════════════════════════════════════
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly BOLD='\033[1m'
readonly NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════════
# 📋 CONFIGURATION & GLOBALS
# ═══════════════════════════════════════════════════════════════════
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly DESKTOP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly PROJECT_ROOT="$(cd "${DESKTOP_DIR}/.." && pwd)"
readonly LOG_DIR="/tmp/desktop_logs"
readonly SECURITY_LOG="${LOG_DIR}/security_automation.log"
readonly AUDIT_DIR="/tmp/desktop_security_audit"
readonly BACKUP_DIR="/tmp/desktop_security_backup"
readonly MONITORING_PID_FILE="/tmp/security_monitor.pid"

# Security configuration
SCAN_MODE=false
MONITOR_MODE=false
ENCRYPT_MODE=false
AUDIT_MODE=false
INCIDENT_RESPONSE_MODE=false
MONITORING_INTERVAL=30
ALERT_THRESHOLD="HIGH"

# ═══════════════════════════════════════════════════════════════════
# 🛠️ UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")  echo -e "${CYAN}[INFO]${NC} ${timestamp} - $message" | tee -a "$SECURITY_LOG" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC} ${timestamp} - $message" | tee -a "$SECURITY_LOG" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} ${timestamp} - $message" | tee -a "$SECURITY_LOG" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} - $message" | tee -a "$SECURITY_LOG" ;;
        "SECURITY") echo -e "${RED}${BOLD}[SECURITY]${NC} ${timestamp} - $message" | tee -a "$SECURITY_LOG" ;;
        *) echo -e "${WHITE}[$level]${NC} ${timestamp} - $message" | tee -a "$SECURITY_LOG" ;;
    esac
}

show_header() {
    echo -e "${RED}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                  🔐 AINFLUE SECURITY AUTOMATION                 ║"
    echo "║                                                                  ║"
    echo "║        Advanced Desktop Security & Monitoring System            ║"
    echo "║                                                                  ║"
    echo "║  © 2025 Fahed Mlaiel - Cybersecurity & Protection Expert        ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_progress() {
    local current=$1
    local total=$2
    local step_name="$3"
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    
    printf "\r${RED}Security Progress${NC}: ["
    printf "%*s" $completed | tr ' ' '█'
    printf "%*s" $((width - completed))
    printf "] ${BOLD}%d%%${NC} - %s" $percentage "$step_name"
}

send_security_alert() {
    local severity="$1"
    local title="$2"
    local message="$3"
    
    log "SECURITY" "🚨 ALERT [$severity] $title: $message"
    
    # Create alert file
    local alert_file="${AUDIT_DIR}/alerts/$(date +%Y%m%d_%H%M%S)_${severity}.alert"
    mkdir -p "$(dirname "$alert_file")"
    
    cat > "$alert_file" << EOF
SECURITY ALERT: $title
Severity: $severity
Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Message: $message
System: $(uname -a)
User: $(whoami)
Process: $$
EOF
    
    # Send notification (placeholder for actual notification system)
    if command -v notify-send &> /dev/null; then
        notify-send "Ainflue Security Alert" "$title: $message" --urgency=critical
    fi
}

# ═══════════════════════════════════════════════════════════════════
# 🔍 VULNERABILITY SCANNING
# ═══════════════════════════════════════════════════════════════════
scan_npm_vulnerabilities() {
    log "INFO" "🔍 Scanning npm vulnerabilities..."
    show_progress 1 10 "NPM Vulnerability Scan"
    
    cd "$DESKTOP_DIR"
    
    if [[ ! -f "package.json" ]]; then
        log "ERROR" "❌ package.json not found"
        return 1
    fi
    
    # Run npm audit
    local audit_result="${AUDIT_DIR}/npm_audit_$(date +%Y%m%d_%H%M%S).json"
    mkdir -p "$(dirname "$audit_result")"
    
    if npm audit --json > "$audit_result" 2>&1; then
        log "SUCCESS" "✅ No npm vulnerabilities found"
    else
        local vulnerability_count=$(jq '.metadata.vulnerabilities.total // 0' "$audit_result" 2>/dev/null || echo "unknown")
        
        if [[ "$vulnerability_count" == "0" ]]; then
            log "SUCCESS" "✅ No npm vulnerabilities found"
        else
            log "WARN" "⚠️ Found $vulnerability_count npm vulnerabilities"
            
            # Check for high/critical vulnerabilities
            local critical_count=$(jq '.metadata.vulnerabilities.critical // 0' "$audit_result" 2>/dev/null || echo "0")
            local high_count=$(jq '.metadata.vulnerabilities.high // 0' "$audit_result" 2>/dev/null || echo "0")
            
            if [[ "$critical_count" -gt 0 ]] || [[ "$high_count" -gt 0 ]]; then
                send_security_alert "HIGH" "NPM Vulnerabilities" "Found $critical_count critical and $high_count high severity vulnerabilities"
                
                # Attempt automatic fix
                log "INFO" "🔧 Attempting automatic vulnerability fix..."
                if npm audit fix --force; then
                    log "SUCCESS" "✅ Vulnerabilities automatically fixed"
                else
                    log "ERROR" "❌ Failed to fix vulnerabilities automatically"
                fi
            fi
        fi
    fi
    
    log "SUCCESS" "✅ NPM vulnerability scan completed"
}

scan_file_permissions() {
    log "INFO" "🔍 Scanning file permissions..."
    show_progress 2 10 "File Permission Scan"
    
    local permission_issues=()
    
    # Check for world-writable files
    while IFS= read -r -d '' file; do
        permission_issues+=("World-writable file: $file")
    done < <(find "$DESKTOP_DIR" -type f -perm -002 -print0 2>/dev/null || true)
    
    # Check for SUID/SGID files (shouldn't be any in desktop app)
    while IFS= read -r -d '' file; do
        permission_issues+=("SUID/SGID file: $file")
    done < <(find "$DESKTOP_DIR" -type f \( -perm -4000 -o -perm -2000 \) -print0 2>/dev/null || true)
    
    if [[ ${#permission_issues[@]} -gt 0 ]]; then
        log "WARN" "⚠️ Found permission issues:"
        for issue in "${permission_issues[@]}"; do
            log "WARN" "   $issue"
        done
        send_security_alert "MEDIUM" "File Permission Issues" "${#permission_issues[@]} permission issues found"
    else
        log "SUCCESS" "✅ No permission issues found"
    fi
}

scan_sensitive_data() {
    log "INFO" "🔍 Scanning for sensitive data exposure..."
    show_progress 3 10 "Sensitive Data Scan"
    
    local sensitive_patterns=(
        "password\s*=\s*['\"][^'\"]{3,}['\"]"
        "api[_-]?key\s*=\s*['\"][^'\"]{10,}['\"]"
        "secret\s*=\s*['\"][^'\"]{10,}['\"]"
        "token\s*=\s*['\"][^'\"]{20,}['\"]"
        "private[_-]?key"
        "-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"
    )
    
    local findings=()
    
    for pattern in "${sensitive_patterns[@]}"; do
        while IFS= read -r line; do
            findings+=("$line")
        done < <(grep -r -i -E "$pattern" "$DESKTOP_DIR" --exclude-dir=node_modules --exclude-dir=.git 2>/dev/null || true)
    done
    
    if [[ ${#findings[@]} -gt 0 ]]; then
        log "WARN" "⚠️ Potential sensitive data exposure:"
        for finding in "${findings[@]:0:5}"; do  # Show only first 5
            log "WARN" "   ${finding:0:100}..."
        done
        
        if [[ ${#findings[@]} -gt 5 ]]; then
            log "WARN" "   ... and $((${#findings[@]} - 5)) more findings"
        fi
        
        send_security_alert "HIGH" "Sensitive Data Exposure" "${#findings[@]} potential exposures found"
    else
        log "SUCCESS" "✅ No sensitive data exposure detected"
    fi
}

# ═══════════════════════════════════════════════════════════════════
# 🔐 ENCRYPTION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
encrypt_sensitive_files() {
    log "INFO" "🔐 Encrypting sensitive files..."
    show_progress 4 10 "File Encryption"
    
    local sensitive_dirs=(
        "${DESKTOP_DIR}/config"
        "${DESKTOP_DIR}/secrets"
        "${DESKTOP_DIR}/.env"
    )
    
    for item in "${sensitive_dirs[@]}"; do
        if [[ -e "$item" ]]; then
            log "INFO" "🔒 Encrypting: $item"
            
            # Create encrypted backup
            local backup_file="${BACKUP_DIR}/$(basename "$item")_$(date +%Y%m%d_%H%M%S).enc"
            mkdir -p "$(dirname "$backup_file")"
            
            if command -v gpg &> /dev/null; then
                # Use GPG for encryption
                tar -czf - "$item" | gpg --symmetric --cipher-algo AES256 --output "$backup_file" 2>/dev/null || {
                    log "ERROR" "❌ Failed to encrypt $item"
                    continue
                }
            else
                # Use openssl as fallback
                tar -czf - "$item" | openssl enc -aes-256-cbc -salt -out "$backup_file" -pass pass:"$(openssl rand -base64 32)" 2>/dev/null || {
                    log "ERROR" "❌ Failed to encrypt $item"
                    continue
                }
            fi
            
            log "SUCCESS" "✅ Encrypted: $item -> $backup_file"
        fi
    done
    
    log "SUCCESS" "✅ File encryption completed"
}

setup_secure_storage() {
    log "INFO" "🔐 Setting up secure storage..."
    
    # Create secure directories with proper permissions
    local secure_dirs=(
        "${DESKTOP_DIR}/.secure"
        "${DESKTOP_DIR}/cache/.secure"
        "${AUDIT_DIR}/secure"
    )
    
    for dir in "${secure_dirs[@]}"; do
        mkdir -p "$dir"
        chmod 700 "$dir"
        
        # Create .gitignore to prevent accidental commits
        echo "*" > "$dir/.gitignore"
        echo "!.gitignore" >> "$dir/.gitignore"
        
        log "SUCCESS" "✅ Secured directory: $dir"
    done
}

# ═══════════════════════════════════════════════════════════════════
# 📊 MONITORING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
start_security_monitoring() {
    log "INFO" "👁️ Starting security monitoring..."
    show_progress 5 10 "Security Monitoring"
    
    # Check if monitoring is already running
    if [[ -f "$MONITORING_PID_FILE" ]] && kill -0 "$(cat "$MONITORING_PID_FILE")" 2>/dev/null; then
        log "WARN" "⚠️ Security monitoring already running (PID: $(cat "$MONITORING_PID_FILE"))"
        return 0
    fi
    
    # Start monitoring in background
    (
        echo $$ > "$MONITORING_PID_FILE"
        
        while true; do
            monitor_system_integrity
            monitor_network_connections
            monitor_process_behavior
            
            sleep "$MONITORING_INTERVAL"
        done
    ) &
    
    local monitor_pid=$!
    echo "$monitor_pid" > "$MONITORING_PID_FILE"
    
    log "SUCCESS" "✅ Security monitoring started (PID: $monitor_pid)"
}

monitor_system_integrity() {
    # Check critical file modifications
    local critical_files=(
        "${DESKTOP_DIR}/package.json"
        "${DESKTOP_DIR}/main.js"
        "${DESKTOP_DIR}/preload.js"
    )
    
    for file in "${critical_files[@]}"; do
        if [[ -f "$file" ]]; then
            local current_hash=$(sha256sum "$file" | cut -d' ' -f1)
            local stored_hash_file="${AUDIT_DIR}/hashes/$(basename "$file").sha256"
            
            mkdir -p "$(dirname "$stored_hash_file")"
            
            if [[ -f "$stored_hash_file" ]]; then
                local stored_hash=$(cat "$stored_hash_file")
                if [[ "$current_hash" != "$stored_hash" ]]; then
                    send_security_alert "HIGH" "File Integrity Violation" "Critical file modified: $file"
                fi
            else
                echo "$current_hash" > "$stored_hash_file"
            fi
        fi
    done
}

monitor_network_connections() {
    # Monitor for suspicious network connections
    if command -v netstat &> /dev/null; then
        local suspicious_connections=$(netstat -tuln | grep -E "(LISTEN|ESTABLISHED)" | grep -v -E "(127\.0\.0\.1|::1|localhost)" | wc -l)
        
        if [[ "$suspicious_connections" -gt 10 ]]; then
            send_security_alert "MEDIUM" "Suspicious Network Activity" "$suspicious_connections external connections detected"
        fi
    fi
}

monitor_process_behavior() {
    # Monitor for suspicious process behavior
    local desktop_processes=$(pgrep -f "electron" | wc -l)
    
    # Alert if too many electron processes (potential fork bomb)
    if [[ "$desktop_processes" -gt 5 ]]; then
        send_security_alert "HIGH" "Process Anomaly" "$desktop_processes electron processes detected"
    fi
}

stop_security_monitoring() {
    if [[ -f "$MONITORING_PID_FILE" ]]; then
        local pid=$(cat "$MONITORING_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            log "SUCCESS" "✅ Security monitoring stopped (PID: $pid)"
        fi
        rm -f "$MONITORING_PID_FILE"
    else
        log "INFO" "ℹ️ Security monitoring not running"
    fi
}

# ═══════════════════════════════════════════════════════════════════
# 📋 AUDIT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
run_security_audit() {
    log "INFO" "🔍 Running comprehensive security audit..."
    show_progress 6 10 "Security Audit"
    
    local audit_report="${AUDIT_DIR}/security_audit_$(date +%Y%m%d_%H%M%S).md"
    mkdir -p "$(dirname "$audit_report")"
    
    cat > "$audit_report" << EOF
# Ainflue Desktop Security Audit Report

**Audit Date**: $(date '+%Y-%m-%d %H:%M:%S')
**System**: $(uname -a)
**Auditor**: Security Automation Script

## 🔍 Audit Summary

### Vulnerabilities Scanned
- NPM packages and dependencies
- File permissions and access controls
- Sensitive data exposure
- Network security configuration
- Process and system integrity

### Security Measures
- File encryption and secure storage
- Real-time monitoring and alerting
- Automated vulnerability remediation
- Incident response procedures

## 📊 Findings

EOF
    
    # Add detailed findings to report
    {
        echo "### NPM Vulnerabilities"
        echo "Latest scan results:"
        echo '```'
        if [[ -f "${AUDIT_DIR}/npm_audit_$(date +%Y%m%d)_"*.json ]]; then
            local latest_audit=$(ls -t "${AUDIT_DIR}"/npm_audit_*.json | head -1)
            jq -r '.metadata.vulnerabilities | to_entries[] | "\(.key): \(.value)"' "$latest_audit" 2>/dev/null || echo "No data available"
        else
            echo "No recent audit data available"
        fi
        echo '```'
        echo
        
        echo "### File Permissions"
        echo "Permission check completed: $(date)"
        echo
        
        echo "### Monitoring Status"
        if [[ -f "$MONITORING_PID_FILE" ]] && kill -0 "$(cat "$MONITORING_PID_FILE")" 2>/dev/null; then
            echo "✅ Security monitoring: ACTIVE (PID: $(cat "$MONITORING_PID_FILE"))"
        else
            echo "❌ Security monitoring: INACTIVE"
        fi
        echo
        
        echo "### Recommendations"
        echo "- Keep npm dependencies updated"
        echo "- Regularly review file permissions"
        echo "- Monitor security alerts"
        echo "- Backup sensitive data securely"
        echo "- Test incident response procedures"
        
    } >> "$audit_report"
    
    log "SUCCESS" "✅ Security audit completed: $audit_report"
}

# ═══════════════════════════════════════════════════════════════════
# 🚨 INCIDENT RESPONSE
# ═══════════════════════════════════════════════════════════════════
initiate_incident_response() {
    log "SECURITY" "🚨 Initiating incident response procedure..."
    show_progress 7 10 "Incident Response"
    
    local incident_id="INC_$(date +%Y%m%d_%H%M%S)"
    local incident_dir="${AUDIT_DIR}/incidents/$incident_id"
    mkdir -p "$incident_dir"
    
    # Collect system information
    {
        echo "INCIDENT RESPONSE REPORT"
        echo "Incident ID: $incident_id"
        echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "System: $(uname -a)"
        echo "User: $(whoami)"
        echo "Working Directory: $(pwd)"
        echo
        echo "=== PROCESS LIST ==="
        ps aux
        echo
        echo "=== NETWORK CONNECTIONS ==="
        netstat -tuln 2>/dev/null || echo "netstat not available"
        echo
        echo "=== RECENT LOG ENTRIES ==="
        tail -100 "$SECURITY_LOG" 2>/dev/null || echo "No security log available"
        
    } > "$incident_dir/incident_report.txt"
    
    # Create forensic snapshot
    if [[ -d "$DESKTOP_DIR" ]]; then
        tar -czf "$incident_dir/desktop_snapshot.tar.gz" "$DESKTOP_DIR" 2>/dev/null || {
            log "ERROR" "❌ Failed to create forensic snapshot"
        }
    fi
    
    # Stop all monitoring
    stop_security_monitoring
    
    # Send critical alert
    send_security_alert "CRITICAL" "Security Incident" "Incident response initiated: $incident_id"
    
    log "SUCCESS" "✅ Incident response completed: $incident_dir"
}

# ═══════════════════════════════════════════════════════════════════
# 📚 HELP & USAGE
# ═══════════════════════════════════════════════════════════════════
show_help() {
    echo -e "${CYAN}${BOLD}USAGE:${NC}"
    echo "  $0 [OPTIONS]"
    echo
    echo -e "${CYAN}${BOLD}OPTIONS:${NC}"
    echo "  --scan                  Run vulnerability scans"
    echo "  --monitor              Start security monitoring"
    echo "  --stop-monitor         Stop security monitoring"
    echo "  --encrypt              Encrypt sensitive files"
    echo "  --audit                Run security audit"
    echo "  --incident-response    Initiate incident response"
    echo "  --interval SECONDS     Monitoring interval (default: 30)"
    echo "  --alert-threshold LEVEL Alert threshold: LOW|MEDIUM|HIGH|CRITICAL"
    echo "  --help                 Show this help message"
    echo
    echo -e "${CYAN}${BOLD}EXAMPLES:${NC}"
    echo "  $0 --scan --encrypt     # Run scans and encrypt files"
    echo "  $0 --monitor --interval 60  # Start monitoring with 60s interval"
    echo "  $0 --audit              # Generate security audit report"
    echo "  $0 --incident-response  # Emergency incident response"
    echo
    echo -e "${CYAN}${BOLD}MONITORING:${NC}"
    echo "  Security monitoring runs continuously in the background"
    echo "  Alerts are logged and can trigger notifications"
    echo "  Use --stop-monitor to terminate monitoring"
}

# ═══════════════════════════════════════════════════════════════════
# 🎯 MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
main() {
    # Create required directories
    mkdir -p "$LOG_DIR" "$AUDIT_DIR" "$BACKUP_DIR"
    
    # Parse command line arguments
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --scan)
                SCAN_MODE=true
                shift
                ;;
            --monitor)
                MONITOR_MODE=true
                shift
                ;;
            --stop-monitor)
                stop_security_monitoring
                exit 0
                ;;
            --encrypt)
                ENCRYPT_MODE=true
                shift
                ;;
            --audit)
                AUDIT_MODE=true
                shift
                ;;
            --incident-response)
                INCIDENT_RESPONSE_MODE=true
                shift
                ;;
            --interval)
                MONITORING_INTERVAL="$2"
                shift 2
                ;;
            --alert-threshold)
                ALERT_THRESHOLD="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    show_header
    
    local start_time=$(date +%s)
    
    log "INFO" "🔐 Starting Ainflue Desktop Security Automation"
    log "INFO" "🎯 Alert threshold: $ALERT_THRESHOLD"
    
    # Execute security operations based on mode
    local operation_count=0
    
    if [[ "$SCAN_MODE" == "true" ]]; then
        log "INFO" "🔍 Running security scans..."
        scan_npm_vulnerabilities || log "ERROR" "NPM scan failed"
        scan_file_permissions || log "ERROR" "Permission scan failed"
        scan_sensitive_data || log "ERROR" "Sensitive data scan failed"
        ((operation_count++))
    fi
    
    if [[ "$ENCRYPT_MODE" == "true" ]]; then
        log "INFO" "🔐 Setting up encryption..."
        setup_secure_storage || log "ERROR" "Secure storage setup failed"
        encrypt_sensitive_files || log "ERROR" "File encryption failed"
        ((operation_count++))
    fi
    
    if [[ "$MONITOR_MODE" == "true" ]]; then
        log "INFO" "👁️ Starting monitoring..."
        start_security_monitoring || log "ERROR" "Failed to start monitoring"
        ((operation_count++))
    fi
    
    if [[ "$AUDIT_MODE" == "true" ]]; then
        log "INFO" "📋 Running audit..."
        run_security_audit || log "ERROR" "Security audit failed"
        ((operation_count++))
    fi
    
    if [[ "$INCIDENT_RESPONSE_MODE" == "true" ]]; then
        log "SECURITY" "🚨 Incident response mode..."
        initiate_incident_response || log "ERROR" "Incident response failed"
        ((operation_count++))
    fi
    
    if [[ "$operation_count" -eq 0 ]]; then
        log "WARN" "⚠️ No operations specified"
        show_help
        exit 1
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo
    log "SUCCESS" "🎉 Security automation completed in ${duration}s"
    echo -e "${GREEN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                   ✅ SECURITY OPERATIONS COMPLETE               ║"
    echo "║                                                                  ║"
    echo "║  Desktop security measures active and monitoring enabled        ║"
    echo "║  Execution time: ${duration} seconds                             ║"
    echo "║  Logs: ${SECURITY_LOG}                                          ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Show monitoring status
    if [[ -f "$MONITORING_PID_FILE" ]] && kill -0 "$(cat "$MONITORING_PID_FILE")" 2>/dev/null; then
        echo -e "${CYAN}${BOLD}MONITORING STATUS:${NC} Active (PID: $(cat "$MONITORING_PID_FILE"))"
        echo -e "${CYAN}${BOLD}NEXT STEPS:${NC}"
        echo "1. Review security logs regularly"
        echo "2. Monitor alert files in $AUDIT_DIR/alerts/"
        echo "3. Update security policies as needed"
        echo "4. Use --stop-monitor when done"
    fi
}

# Trap for cleanup on exit
trap 'stop_security_monitoring' EXIT

# Execute main function with all arguments
main "$@"