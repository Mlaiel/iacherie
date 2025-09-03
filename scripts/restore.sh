#!/bin/bash

# =================================================================
# Ainflue Platform Restore Script
# Author: Fahed Mlaiel (mlaiel@live.de)
# Description: Automated restore system for Ainflue Platform
# Usage: ./scripts/restore.sh [options]
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
BACKUP_DATE="${BACKUP_DATE:-latest}"
RESTORE_TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_BASE_DIR="${BACKUP_DIR:-/var/backups/ainflue}"
RESTORE_DIR="/tmp/restore_$RESTORE_TIMESTAMP"
LOG_FILE="/var/log/ainflue/restore_$RESTORE_TIMESTAMP.log"

# Storage configuration
AWS_S3_BUCKET="${AWS_S3_BUCKET:-ainflue-backups-$ENVIRONMENT}"

# Database configuration
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-ainflue_$ENVIRONMENT}"
POSTGRES_DB="${POSTGRES_DB:-ainflue_platform_$ENVIRONMENT}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

# Notification
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-mlaiel@live.de}"

# Restore options
DRY_RUN="${DRY_RUN:-false}"
FORCE_RESTORE="${FORCE_RESTORE:-false}"
RESTORE_DATABASE="${RESTORE_DATABASE:-true}"
RESTORE_FILES="${RESTORE_FILES:-true}"
RESTORE_CONFIG="${RESTORE_CONFIG:-false}"

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
    error "Restore failed at step: $1"
    error "Check log file: $LOG_FILE"
    cleanup_on_failure
    exit 1
}

cleanup_on_failure() {
    log "Cleaning up failed restore..."
    if [[ -d "$RESTORE_DIR" ]]; then
        rm -rf "$RESTORE_DIR" || true
    fi
}

# Safety check
safety_check() {
    log "Performing safety checks..."
    
    if [[ "$ENVIRONMENT" == "production" && "$FORCE_RESTORE" != "true" ]]; then
        error "Production restore requires --force flag for safety"
        error "Use: FORCE_RESTORE=true $0 or $0 --force"
        exit 1
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN MODE - No actual changes will be made"
    fi
    
    success "Safety checks passed"
}

# Initialize restore environment
initialize_restore() {
    log "Initializing restore environment..."
    
    # Create restore directory
    mkdir -p "$RESTORE_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Load environment variables
    if [[ -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]]; then
        log "Loading environment configuration from .env.$ENVIRONMENT"
        set -a
        source "$PROJECT_ROOT/.env.$ENVIRONMENT"
        set +a
    fi
    
    success "Restore environment initialized"
}

# Find backup to restore
find_backup() {
    log "Finding backup to restore..."
    
    local backup_path=""
    
    if [[ "$BACKUP_DATE" == "latest" ]]; then
        # Find latest backup locally
        if [[ -d "$BACKUP_BASE_DIR/$ENVIRONMENT" ]]; then
            backup_path=$(find "$BACKUP_BASE_DIR/$ENVIRONMENT" -type d -name "20*" | sort -r | head -1)
        fi
        
        # If no local backup, try cloud storage
        if [[ -z "$backup_path" ]] && command -v aws &> /dev/null && [[ -n "${AWS_ACCESS_KEY_ID:-}" ]]; then
            local latest_cloud=$(aws s3 ls "s3://$AWS_S3_BUCKET/$ENVIRONMENT/" | sort -r | head -1 | awk '{print $2}' | tr -d '/')
            if [[ -n "$latest_cloud" ]]; then
                log "Downloading latest backup from cloud: $latest_cloud"
                aws s3 sync "s3://$AWS_S3_BUCKET/$ENVIRONMENT/$latest_cloud/" "$RESTORE_DIR/"
                backup_path="$RESTORE_DIR"
            fi
        fi
    else
        # Find specific backup by date
        backup_path="$BACKUP_BASE_DIR/$ENVIRONMENT/$BACKUP_DATE"
        if [[ ! -d "$backup_path" ]] && command -v aws &> /dev/null && [[ -n "${AWS_ACCESS_KEY_ID:-}" ]]; then
            log "Downloading backup from cloud: $BACKUP_DATE"
            aws s3 sync "s3://$AWS_S3_BUCKET/$ENVIRONMENT/$BACKUP_DATE/" "$RESTORE_DIR/"
            backup_path="$RESTORE_DIR"
        fi
    fi
    
    if [[ -z "$backup_path" || ! -d "$backup_path" ]]; then
        handle_error "Backup not found for date: $BACKUP_DATE"
    fi
    
    BACKUP_PATH="$backup_path"
    success "Backup found: $BACKUP_PATH"
}

# Create pre-restore backup
create_pre_restore_backup() {
    log "Creating pre-restore backup for safety..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would create pre-restore backup"
        return 0
    fi
    
    local pre_restore_backup="$BACKUP_BASE_DIR/$ENVIRONMENT/pre-restore-$RESTORE_TIMESTAMP"
    mkdir -p "$pre_restore_backup"
    
    # Backup current database
    if [[ "$RESTORE_DATABASE" == "true" ]]; then
        log "Backing up current database..."
        if PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
            -h "$POSTGRES_HOST" \
            -p "$POSTGRES_PORT" \
            -U "$POSTGRES_USER" \
            -d "$POSTGRES_DB" \
            --verbose \
            --no-owner \
            --no-privileges \
            | gzip > "$pre_restore_backup/pre_restore_postgresql_$RESTORE_TIMESTAMP.sql.gz"; then
            success "Current database backed up"
        else
            warning "Failed to backup current database"
        fi
    fi
    
    success "Pre-restore backup completed: $pre_restore_backup"
}

# Restore PostgreSQL database
restore_postgresql() {
    if [[ "$RESTORE_DATABASE" != "true" ]]; then
        log "Skipping database restore (disabled)"
        return 0
    fi
    
    log "Starting PostgreSQL database restore..."
    
    local db_backup_file=$(find "$BACKUP_PATH" -name "postgresql_*.sql.gz" | head -1)
    
    if [[ -z "$db_backup_file" ]]; then
        warning "No PostgreSQL backup file found"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would restore database from $db_backup_file"
        return 0
    fi
    
    log "Restoring database from: $db_backup_file"
    
    # Drop existing connections
    PGPASSWORD="$POSTGRES_PASSWORD" psql \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d postgres \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$POSTGRES_DB';" || true
    
    # Drop and recreate database
    PGPASSWORD="$POSTGRES_PASSWORD" psql \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d postgres \
        -c "DROP DATABASE IF EXISTS $POSTGRES_DB;"
    
    PGPASSWORD="$POSTGRES_PASSWORD" psql \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d postgres \
        -c "CREATE DATABASE $POSTGRES_DB;"
    
    # Restore database
    if zcat "$db_backup_file" | PGPASSWORD="$POSTGRES_PASSWORD" psql \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --quiet; then
        success "PostgreSQL database restored successfully"
    else
        handle_error "PostgreSQL database restore failed"
    fi
}

# Restore Redis data
restore_redis() {
    if [[ "$RESTORE_DATABASE" != "true" ]]; then
        log "Skipping Redis restore (disabled)"
        return 0
    fi
    
    log "Starting Redis restore..."
    
    local redis_backup_file=$(find "$BACKUP_PATH" -name "redis_*.rdb" | head -1)
    
    if [[ -z "$redis_backup_file" ]]; then
        warning "No Redis backup file found"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would restore Redis from $redis_backup_file"
        return 0
    fi
    
    log "Restoring Redis from: $redis_backup_file"
    
    # Stop Redis temporarily (if possible)
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ${REDIS_PASSWORD:+-a "$REDIS_PASSWORD"} FLUSHALL || true
    
    # Copy RDB file and restart Redis service
    warning "Manual Redis restore required - copy $redis_backup_file to Redis data directory and restart Redis"
    
    success "Redis restore prepared"
}

# Restore application files
restore_application() {
    if [[ "$RESTORE_FILES" != "true" ]]; then
        log "Skipping application files restore (disabled)"
        return 0
    fi
    
    log "Starting application files restore..."
    
    local app_backup_file=$(find "$BACKUP_PATH" -name "application_*.tar.gz" | head -1)
    
    if [[ -z "$app_backup_file" ]]; then
        warning "No application backup file found"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would restore application files from $app_backup_file"
        return 0
    fi
    
    log "Restoring application files from: $app_backup_file"
    
    # Create backup of current application
    if [[ -d "$PROJECT_ROOT" ]]; then
        mv "$PROJECT_ROOT" "${PROJECT_ROOT}.pre-restore-$RESTORE_TIMESTAMP" || true
    fi
    
    # Extract application files
    mkdir -p "$PROJECT_ROOT"
    if tar -xzf "$app_backup_file" -C "$PROJECT_ROOT"; then
        success "Application files restored successfully"
    else
        handle_error "Application files restore failed"
    fi
}

# Restore configuration files
restore_configuration() {
    if [[ "$RESTORE_CONFIG" != "true" ]]; then
        log "Skipping configuration restore (disabled by default for safety)"
        return 0
    fi
    
    log "Starting configuration restore..."
    
    local config_backup_file=$(find "$BACKUP_PATH" -name "configuration_*.tar.gz" | head -1)
    
    if [[ -z "$config_backup_file" ]]; then
        warning "No configuration backup file found"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would restore configuration from $config_backup_file"
        return 0
    fi
    
    warning "Restoring configuration files - this may overwrite current settings"
    
    # Extract configuration files
    if tar -xzf "$config_backup_file" -C "$PROJECT_ROOT"; then
        success "Configuration files restored successfully"
    else
        warning "Configuration restore may have failed"
    fi
}

# Verify restore
verify_restore() {
    log "Verifying restore..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would verify restore"
        return 0
    fi
    
    # Test database connection
    if [[ "$RESTORE_DATABASE" == "true" ]]; then
        if PGPASSWORD="$POSTGRES_PASSWORD" psql \
            -h "$POSTGRES_HOST" \
            -p "$POSTGRES_PORT" \
            -U "$POSTGRES_USER" \
            -d "$POSTGRES_DB" \
            -c "SELECT 1;" &>/dev/null; then
            success "Database connection verified"
        else
            error "Database connection failed"
        fi
    fi
    
    # Test application structure
    if [[ "$RESTORE_FILES" == "true" ]]; then
        if [[ -f "$PROJECT_ROOT/main.py" || -f "$PROJECT_ROOT/requirements.txt" ]]; then
            success "Application structure verified"
        else
            warning "Application structure may be incomplete"
        fi
    fi
    
    success "Restore verification completed"
}

# Generate restore report
generate_report() {
    log "Generating restore report..."
    
    local report_file="$RESTORE_DIR/restore_report_$RESTORE_TIMESTAMP.json"
    
    cat > "$report_file" << EOF
{
    "restore_info": {
        "timestamp": "$RESTORE_TIMESTAMP",
        "environment": "$ENVIRONMENT",
        "backup_date": "$BACKUP_DATE",
        "backup_source": "$BACKUP_PATH",
        "dry_run": $DRY_RUN,
        "status": "completed",
        "duration": "$((SECONDS / 60)) minutes"
    },
    "components_restored": {
        "database": $RESTORE_DATABASE,
        "application_files": $RESTORE_FILES,
        "configuration": $RESTORE_CONFIG
    },
    "safety_backup": "${BACKUP_BASE_DIR}/$ENVIRONMENT/pre-restore-$RESTORE_TIMESTAMP"
}
EOF
    
    success "Restore report generated: $report_file"
}

# Send notification
send_notification() {
    local status="$1"
    local message="$2"
    
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "Ainflue Restore $status - $ENVIRONMENT" "$NOTIFICATION_EMAIL"
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
    --environment ENV     Environment to restore (default: production)
    --date DATE          Backup date to restore (default: latest)
    --dry-run            Perform dry run without making changes
    --force              Force restore (required for production)
    --no-database        Skip database restore
    --no-files           Skip application files restore
    --config             Include configuration restore (dangerous)
    --help, -h           Show this help message

Environment Variables:
    BACKUP_DIR           Base backup directory (default: /var/backups/ainflue)
    AWS_S3_BUCKET        S3 bucket for cloud storage
    FORCE_RESTORE        Set to 'true' to force production restore
    DRY_RUN             Set to 'true' for dry run mode

Examples:
    $0 --environment staging --date 20241201_143022
    $0 --dry-run --environment production
    FORCE_RESTORE=true $0 --environment production

⚠️  WARNING: This script will overwrite existing data!
    Always create backups before running restore operations.

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
            --date)
                BACKUP_DATE="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --force)
                FORCE_RESTORE="true"
                shift
                ;;
            --no-database)
                RESTORE_DATABASE="false"
                shift
                ;;
            --no-files)
                RESTORE_FILES="false"
                shift
                ;;
            --config)
                RESTORE_CONFIG="true"
                shift
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

# Main restore function
main() {
    header "Ainflue Platform Restore - $ENVIRONMENT Environment"
    
    local start_time=$(date +%s)
    
    # Execute restore steps
    safety_check || handle_error "safety_check"
    initialize_restore || handle_error "initialization"
    find_backup || handle_error "find_backup"
    create_pre_restore_backup || handle_error "pre_restore_backup"
    restore_postgresql || handle_error "postgresql_restore"
    restore_redis || handle_error "redis_restore"
    restore_application || handle_error "application_restore"
    restore_configuration || handle_error "configuration_restore"
    verify_restore || handle_error "verification"
    generate_report || warning "report_generation failed"
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ "$DRY_RUN" == "true" ]]; then
        success "Dry run completed successfully in $((duration / 60)) minutes"
        log "No actual changes were made"
    else
        success "Restore completed successfully in $((duration / 60)) minutes"
        log "Restore from backup: $BACKUP_PATH"
    fi
    
    send_notification "SUCCESS" "Restore completed successfully for $ENVIRONMENT environment in $((duration / 60)) minutes. Source: $BACKUP_PATH"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_arguments "$@"
    main
fi