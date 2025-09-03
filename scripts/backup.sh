#!/bin/bash

# =================================================================
# Ainflue Platform Backup Script
# Author: Fahed Mlaiel (mlaiel@live.de)
# Description: Automated backup system for Ainflue Platform
# Usage: ./scripts/backup.sh [options]
# =================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${ENVIRONMENT:-production}"
BACKUP_TYPE="${BACKUP_TYPE:-full}"
BACKUP_TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_BASE_DIR="${BACKUP_DIR:-/var/backups/ainflue}"
BACKUP_DIR="$BACKUP_BASE_DIR/$ENVIRONMENT/$BACKUP_TIMESTAMP"
LOG_FILE="$BACKUP_DIR/backup_$BACKUP_TIMESTAMP.log"

# Storage configuration
AWS_S3_BUCKET="${AWS_S3_BUCKET:-ainflue-backups-$ENVIRONMENT}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# Database configuration
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-ainflue_$ENVIRONMENT}"
POSTGRES_DB="${POSTGRES_DB:-ainflue_platform_$ENVIRONMENT}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

# Notification
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-mlaiel@live.de}"

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

header() {
    echo -e "${PURPLE}========================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${PURPLE}$1${NC}" | tee -a "$LOG_FILE"
    echo -e "${PURPLE}========================================${NC}" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    error "Backup failed at step: $1"
    error "Check log file: $LOG_FILE"
    cleanup_on_failure
    exit 1
}

cleanup_on_failure() {
    log "Cleaning up failed backup..."
    if [[ -d "$BACKUP_DIR" ]]; then
        rm -rf "$BACKUP_DIR" || true
    fi
}

# Initialize backup environment
initialize_backup() {
    log "Initializing backup environment..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Load environment variables
    if [[ -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]]; then
        log "Loading environment configuration from .env.$ENVIRONMENT"
        set -a
        source "$PROJECT_ROOT/.env.$ENVIRONMENT"
        set +a
    fi
    
    success "Backup environment initialized"
}

# Backup PostgreSQL database
backup_postgresql() {
    log "Starting PostgreSQL database backup..."
    
    local db_backup_file="$BACKUP_DIR/postgresql_${POSTGRES_DB}_$BACKUP_TIMESTAMP.sql"
    local db_compressed_file="$db_backup_file.gz"
    
    # Perform database dump
    if PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --verbose \
        --no-owner \
        --no-privileges \
        > "$db_backup_file"; then
        
        # Compress the backup
        gzip "$db_backup_file"
        success "PostgreSQL backup completed: $db_compressed_file"
        
        # Verify backup integrity
        if gzip -t "$db_compressed_file"; then
            success "PostgreSQL backup integrity verified"
        else
            handle_error "PostgreSQL backup corruption detected"
        fi
    else
        handle_error "PostgreSQL backup failed"
    fi
}

# Backup Redis data
backup_redis() {
    log "Starting Redis backup..."
    
    local redis_backup_file="$BACKUP_DIR/redis_$BACKUP_TIMESTAMP.rdb"
    
    # Create Redis backup using BGSAVE
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ${REDIS_PASSWORD:+-a "$REDIS_PASSWORD"} BGSAVE; then
        # Wait for background save to complete
        while redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ${REDIS_PASSWORD:+-a "$REDIS_PASSWORD"} LASTSAVE | grep -q "$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ${REDIS_PASSWORD:+-a "$REDIS_PASSWORD"} LASTSAVE)"; do
            sleep 1
        done
        
        # Copy the RDB file
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ${REDIS_PASSWORD:+-a "$REDIS_PASSWORD"} --rdb "$redis_backup_file"; then
            success "Redis backup completed: $redis_backup_file"
        else
            warning "Redis backup may have failed"
        fi
    else
        warning "Redis backup failed"
    fi
}

# Backup application files
backup_application() {
    log "Starting application files backup..."
    
    local app_backup_file="$BACKUP_DIR/application_$BACKUP_TIMESTAMP.tar.gz"
    
    # Create application backup excluding unnecessary files
    if tar -czf "$app_backup_file" \
        -C "$PROJECT_ROOT" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        --exclude='logs' \
        --exclude='tmp' \
        --exclude='backups' \
        .; then
        success "Application backup completed: $app_backup_file"
    else
        handle_error "Application backup failed"
    fi
}

# Backup configuration files
backup_configuration() {
    log "Starting configuration backup..."
    
    local config_backup_file="$BACKUP_DIR/configuration_$BACKUP_TIMESTAMP.tar.gz"
    
    # Backup critical configuration
    if tar -czf "$config_backup_file" \
        -C "$PROJECT_ROOT" \
        config/ \
        kubernetes/ \
        docker/ \
        scripts/ \
        .env.* \
        docker-compose*.yml \
        requirements*.txt \
        pytest.ini \
        2>/dev/null; then
        success "Configuration backup completed: $config_backup_file"
    else
        warning "Some configuration files may be missing"
    fi
}

# Upload backup to cloud storage
upload_to_cloud() {
    log "Uploading backup to cloud storage..."
    
    if command -v aws &> /dev/null && [[ -n "${AWS_ACCESS_KEY_ID:-}" ]]; then
        # Upload to AWS S3
        if aws s3 sync "$BACKUP_DIR" "s3://$AWS_S3_BUCKET/$ENVIRONMENT/$BACKUP_TIMESTAMP/" \
            --exclude "*.log" \
            --storage-class STANDARD_IA; then
            success "Backup uploaded to S3: s3://$AWS_S3_BUCKET/$ENVIRONMENT/$BACKUP_TIMESTAMP/"
        else
            warning "Failed to upload backup to S3"
        fi
    else
        warning "AWS CLI not configured, skipping cloud upload"
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up old backups..."
    
    # Remove local backups older than retention period
    find "$BACKUP_BASE_DIR/$ENVIRONMENT" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true
    
    # Cleanup cloud backups if AWS CLI is available
    if command -v aws &> /dev/null && [[ -n "${AWS_ACCESS_KEY_ID:-}" ]]; then
        local cutoff_date=$(date -d "$RETENTION_DAYS days ago" '+%Y%m%d')
        aws s3 ls "s3://$AWS_S3_BUCKET/$ENVIRONMENT/" | \
        awk '{print $2}' | \
        while read -r folder; do
            if [[ "${folder%/}" < "$cutoff_date" ]]; then
                aws s3 rm "s3://$AWS_S3_BUCKET/$ENVIRONMENT/$folder" --recursive
                log "Removed old cloud backup: $folder"
            fi
        done
    fi
    
    success "Old backups cleaned up"
}

# Generate backup report
generate_report() {
    log "Generating backup report..."
    
    local report_file="$BACKUP_DIR/backup_report_$BACKUP_TIMESTAMP.json"
    
    cat > "$report_file" << EOF
{
    "backup_info": {
        "timestamp": "$BACKUP_TIMESTAMP",
        "environment": "$ENVIRONMENT",
        "backup_type": "$BACKUP_TYPE",
        "status": "completed",
        "duration": "$((SECONDS / 60)) minutes"
    },
    "files": [
$(find "$BACKUP_DIR" -name "*.gz" -o -name "*.sql" -o -name "*.rdb" | while read -r file; do
    echo "        {\"file\": \"$(basename "$file")\", \"size\": \"$(du -h "$file" | cut -f1)\"}"
done | paste -sd ',' -)
    ],
    "storage": {
        "local_path": "$BACKUP_DIR",
        "cloud_path": "s3://$AWS_S3_BUCKET/$ENVIRONMENT/$BACKUP_TIMESTAMP/",
        "retention_days": $RETENTION_DAYS
    }
}
EOF
    
    success "Backup report generated: $report_file"
}

# Send notification
send_notification() {
    local status="$1"
    local message="$2"
    
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "Ainflue Backup $status - $ENVIRONMENT" "$NOTIFICATION_EMAIL"
        log "Notification sent to $NOTIFICATION_EMAIL"
    else
        log "Mail command not available, skipping notification"
    fi
}

# Show usage information
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    --environment ENV    Environment to backup (default: production)
    --type TYPE         Backup type: full, incremental (default: full)
    --retention DAYS    Retention period in days (default: 30)
    --help, -h          Show this help message

Environment Variables:
    BACKUP_DIR          Base backup directory (default: /var/backups/ainflue)
    AWS_S3_BUCKET       S3 bucket for cloud storage
    NOTIFICATION_EMAIL  Email for notifications (default: mlaiel@live.de)

Examples:
    $0 --environment production --type full
    $0 --environment staging --retention 7
    BACKUP_DIR=/custom/backup $0

EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --type)
                BACKUP_TYPE="$2"
                shift 2
                ;;
            --retention)
                RETENTION_DAYS="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Main backup function
main() {
    header "Ainflue Platform Backup - $ENVIRONMENT Environment"
    
    local start_time=$(date +%s)
    
    # Execute backup steps
    initialize_backup || handle_error "initialization"
    backup_postgresql || handle_error "postgresql_backup"
    backup_redis || handle_error "redis_backup"
    backup_application || handle_error "application_backup"
    backup_configuration || handle_error "configuration_backup"
    upload_to_cloud || warning "cloud_upload failed"
    cleanup_old_backups || warning "cleanup failed"
    generate_report || warning "report_generation failed"
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    success "Backup completed successfully in $((duration / 60)) minutes"
    log "Backup location: $BACKUP_DIR"
    
    send_notification "SUCCESS" "Backup completed successfully for $ENVIRONMENT environment in $((duration / 60)) minutes. Location: $BACKUP_DIR"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_arguments "$@"
    main
fi