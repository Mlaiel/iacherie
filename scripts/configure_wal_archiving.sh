#!/bin/bash
"""WAL Archiving Configuration for Point-in-Time Recovery

This script configures WAL (Write-Ahead Logging) archiving for PostgreSQL
to enable point-in-time recovery capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

Usage:
    ./scripts/configure_wal_archiving.sh setup
    ./scripts/configure_wal_archiving.sh archive <wal_file>
    ./scripts/configure_wal_archiving.sh restore <target_time>
"""

set -euo pipefail

# Configuration variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/postgresql/wal_archiving.log"
WAL_ARCHIVE_DIR="/backup/postgresql/wal_archives"
S3_BUCKET="${BACKUP_S3_BUCKET:-ainflue-db-backups}"
S3_PREFIX="wal_archives"
RETENTION_DAYS="${WAL_RETENTION_DAYS:-30}"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Check if running as postgres user
check_postgres_user() {
    if [[ $EUID -ne 0 ]] && [[ "$(whoami)" != "postgres" ]]; then
        error_exit "This script must be run as postgres user or root"
    fi
}

# Setup WAL archiving
setup_wal_archiving() {
    log "Setting up WAL archiving configuration..."
    
    # Create WAL archive directory
    mkdir -p "$WAL_ARCHIVE_DIR"
    chown postgres:postgres "$WAL_ARCHIVE_DIR"
    chmod 750 "$WAL_ARCHIVE_DIR"
    
    # Create archive status directory
    mkdir -p "$WAL_ARCHIVE_DIR/archive_status"
    chown postgres:postgres "$WAL_ARCHIVE_DIR/archive_status"
    
    # Configure PostgreSQL for WAL archiving
    local pg_config_file="/var/lib/postgresql/data/postgresql.conf"
    
    if [[ ! -f "$pg_config_file" ]]; then
        error_exit "PostgreSQL configuration file not found: $pg_config_file"
    fi
    
    # Backup original config
    cp "$pg_config_file" "${pg_config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Update WAL archiving settings
    log "Updating WAL archiving configuration..."
    
    # Enable archiving
    sed -i "s/#archive_mode = off/archive_mode = on/" "$pg_config_file"
    sed -i "s/archive_mode = off/archive_mode = on/" "$pg_config_file"
    
    # Set archive command
    local archive_command="$SCRIPT_DIR/configure_wal_archiving.sh archive %f %p"
    sed -i "s|#archive_command = ''|archive_command = '$archive_command'|" "$pg_config_file"
    sed -i "s|archive_command = ''|archive_command = '$archive_command'|" "$pg_config_file"
    
    # Set WAL level for archiving
    sed -i "s/#wal_level = replica/wal_level = replica/" "$pg_config_file"
    sed -i "s/wal_level = minimal/wal_level = replica/" "$pg_config_file"
    
    # Increase max_wal_senders for replication
    sed -i "s/#max_wal_senders = 10/max_wal_senders = 10/" "$pg_config_file"
    
    # Set checkpoint settings for better archiving performance
    sed -i "s/#checkpoint_completion_target = 0.9/checkpoint_completion_target = 0.9/" "$pg_config_file"
    sed -i "s/#checkpoint_timeout = 5min/checkpoint_timeout = 15min/" "$pg_config_file"
    sed -i "s/#max_wal_size = 1GB/max_wal_size = 4GB/" "$pg_config_file"
    sed -i "s/#min_wal_size = 80MB/min_wal_size = 1GB/" "$pg_config_file"
    
    # Add archive_timeout for timely archiving
    if ! grep -q "archive_timeout" "$pg_config_file"; then
        echo "archive_timeout = 300s  # Archive WAL files every 5 minutes" >> "$pg_config_file"
    fi
    
    log "WAL archiving configuration completed"
    log "Please restart PostgreSQL to apply changes: sudo systemctl restart postgresql"
}

# Archive a single WAL file
archive_wal_file() {
    local wal_file="$1"
    local wal_path="$2"
    
    if [[ -z "$wal_file" ]] || [[ -z "$wal_path" ]]; then
        error_exit "Usage: archive <wal_file> <wal_path>"
    fi
    
    log "Archiving WAL file: $wal_file"
    
    # Check if WAL file exists
    if [[ ! -f "$wal_path" ]]; then
        error_exit "WAL file not found: $wal_path"
    fi
    
    # Create archive filename with timestamp
    local archive_name="${wal_file}.$(date +%Y%m%d_%H%M%S).gz"
    local archive_path="$WAL_ARCHIVE_DIR/$archive_name"
    
    # Compress and copy WAL file
    if gzip -c "$wal_path" > "$archive_path"; then
        log "WAL file compressed and archived: $archive_path"
        
        # Verify archive integrity
        if gunzip -t "$archive_path"; then
            log "Archive integrity verified: $archive_name"
            
            # Upload to S3 if configured
            if command -v aws >/dev/null 2>&1 && [[ -n "$S3_BUCKET" ]]; then
                upload_to_s3 "$archive_path" "$archive_name"
            fi
            
            # Record archive status
            echo "$(date '+%Y-%m-%d %H:%M:%S') - Archived: $wal_file -> $archive_name" >> "$WAL_ARCHIVE_DIR/archive_status/archive.log"
            
        else
            error_exit "Archive integrity check failed: $archive_name"
        fi
    else
        error_exit "Failed to archive WAL file: $wal_file"
    fi
}

# Upload archive to S3
upload_to_s3() {
    local local_file="$1"
    local archive_name="$2"
    
    log "Uploading to S3: s3://$S3_BUCKET/$S3_PREFIX/$archive_name"
    
    if aws s3 cp "$local_file" "s3://$S3_BUCKET/$S3_PREFIX/$archive_name" \
        --storage-class STANDARD_IA \
        --server-side-encryption AES256; then
        log "Successfully uploaded to S3: $archive_name"
        
        # Add metadata
        aws s3api put-object-tagging \
            --bucket "$S3_BUCKET" \
            --key "$S3_PREFIX/$archive_name" \
            --tagging "TagSet=[{Key=Type,Value=WALArchive},{Key=Date,Value=$(date +%Y-%m-%d)},{Key=RetentionDays,Value=$RETENTION_DAYS}]"
            
    else
        log "WARNING: Failed to upload to S3: $archive_name"
    fi
}

# Cleanup old archives
cleanup_old_archives() {
    log "Cleaning up archives older than $RETENTION_DAYS days..."
    
    # Clean local archives
    find "$WAL_ARCHIVE_DIR" -name "*.gz" -type f -mtime +$RETENTION_DAYS -delete
    local deleted_count=$(find "$WAL_ARCHIVE_DIR" -name "*.gz" -type f -mtime +$RETENTION_DAYS | wc -l)
    log "Deleted $deleted_count local archive files"
    
    # Clean S3 archives if configured
    if command -v aws >/dev/null 2>&1 && [[ -n "$S3_BUCKET" ]]; then
        local cutoff_date=$(date -d "$RETENTION_DAYS days ago" '+%Y-%m-%d')
        
        # List and delete old S3 objects
        aws s3api list-objects-v2 \
            --bucket "$S3_BUCKET" \
            --prefix "$S3_PREFIX/" \
            --query "Contents[?LastModified<='$cutoff_date'].Key" \
            --output text | \
        while read -r key; do
            if [[ -n "$key" ]] && [[ "$key" != "None" ]]; then
                aws s3 rm "s3://$S3_BUCKET/$key"
                log "Deleted S3 object: $key"
            fi
        done
    fi
}

# Point-in-time recovery setup
setup_pitr() {
    local target_time="$1"
    local recovery_dir="/tmp/postgresql_recovery_$(date +%Y%m%d_%H%M%S)"
    
    if [[ -z "$target_time" ]]; then
        error_exit "Usage: restore <target_time> (format: '2024-01-15 14:30:00')"
    fi
    
    log "Setting up point-in-time recovery to: $target_time"
    
    # Create recovery directory
    mkdir -p "$recovery_dir"
    
    # Create recovery.conf
    cat > "$recovery_dir/recovery.conf" << EOF
# Point-in-time recovery configuration
# Generated on $(date)

# Recovery target
recovery_target_time = '$target_time'
recovery_target_timeline = 'latest'

# Archive recovery
restore_command = '$SCRIPT_DIR/configure_wal_archiving.sh restore_wal %f %p'
archive_cleanup_command = 'pg_archivecleanup $WAL_ARCHIVE_DIR %r'

# Recovery behavior
recovery_target_action = 'promote'

# Logging
log_min_messages = info
log_line_prefix = '%t [%p]: [%l-1] '
EOF

    log "Recovery configuration created: $recovery_dir/recovery.conf"
    log "To perform recovery:"
    log "1. Stop PostgreSQL: sudo systemctl stop postgresql"
    log "2. Backup current data directory"
    log "3. Restore base backup to data directory"
    log "4. Copy recovery.conf to data directory"
    log "5. Start PostgreSQL: sudo systemctl start postgresql"
    log "6. Monitor logs for recovery completion"
}

# Restore WAL file for recovery
restore_wal() {
    local wal_file="$1"
    local target_path="$2"
    
    if [[ -z "$wal_file" ]] || [[ -z "$target_path" ]]; then
        error_exit "Usage: restore_wal <wal_file> <target_path>"
    fi
    
    log "Restoring WAL file for recovery: $wal_file"
    
    # Look for local archive first
    local archive_pattern="$WAL_ARCHIVE_DIR/${wal_file}.*.gz"
    local archive_file=$(ls $archive_pattern 2>/dev/null | head -1)
    
    if [[ -f "$archive_file" ]]; then
        log "Found local archive: $archive_file"
        gunzip -c "$archive_file" > "$target_path"
        return 0
    fi
    
    # Try to download from S3
    if command -v aws >/dev/null 2>&1 && [[ -n "$S3_BUCKET" ]]; then
        log "Attempting to download from S3..."
        
        # Find the WAL file in S3
        local s3_object=$(aws s3api list-objects-v2 \
            --bucket "$S3_BUCKET" \
            --prefix "$S3_PREFIX/$wal_file." \
            --query "Contents[0].Key" \
            --output text)
        
        if [[ "$s3_object" != "None" ]] && [[ -n "$s3_object" ]]; then
            local temp_file="/tmp/${wal_file}.gz"
            
            if aws s3 cp "s3://$S3_BUCKET/$s3_object" "$temp_file"; then
                gunzip -c "$temp_file" > "$target_path"
                rm -f "$temp_file"
                log "Successfully restored WAL file from S3: $wal_file"
                return 0
            fi
        fi
    fi
    
    log "WARNING: Could not restore WAL file: $wal_file"
    return 1
}

# Show archive status
show_status() {
    log "WAL Archiving Status Report"
    log "=========================="
    
    # Check if archiving is enabled
    local pg_config="/var/lib/postgresql/data/postgresql.conf"
    if [[ -f "$pg_config" ]]; then
        local archive_mode=$(grep "^archive_mode" "$pg_config" || echo "archive_mode = off")
        local archive_command=$(grep "^archive_command" "$pg_config" || echo "archive_command = ''")
        
        log "PostgreSQL Configuration:"
        log "  $archive_mode"
        log "  $archive_command"
    fi
    
    # Check archive directory
    if [[ -d "$WAL_ARCHIVE_DIR" ]]; then
        local archive_count=$(find "$WAL_ARCHIVE_DIR" -name "*.gz" | wc -l)
        local total_size=$(du -sh "$WAL_ARCHIVE_DIR" 2>/dev/null | cut -f1)
        
        log "Local Archives:"
        log "  Directory: $WAL_ARCHIVE_DIR"
        log "  Archive count: $archive_count files"
        log "  Total size: $total_size"
        
        # Show recent archives
        log "Recent archives:"
        find "$WAL_ARCHIVE_DIR" -name "*.gz" -type f -printf "%T@ %p\n" | \
            sort -n | tail -5 | \
            while read timestamp file; do
                local date_str=$(date -d "@$timestamp" '+%Y-%m-%d %H:%M:%S')
                log "  $date_str - $(basename "$file")"
            done
    fi
    
    # Check S3 status
    if command -v aws >/dev/null 2>&1 && [[ -n "$S3_BUCKET" ]]; then
        local s3_count=$(aws s3 ls "s3://$S3_BUCKET/$S3_PREFIX/" --recursive | wc -l)
        log "S3 Archives:"
        log "  Bucket: s3://$S3_BUCKET/$S3_PREFIX/"
        log "  Archive count: $s3_count files"
    fi
    
    # Check PostgreSQL archiving stats
    if command -v psql >/dev/null 2>&1; then
        log "PostgreSQL Archiving Statistics:"
        psql -d ainflue_production -c "
            SELECT 
                archived_count,
                last_archived_wal,
                last_archived_time,
                failed_count,
                last_failed_wal,
                last_failed_time
            FROM pg_stat_archiver;
        " 2>/dev/null || log "  Could not retrieve archiving statistics"
    fi
}

# Main function
main() {
    local action="${1:-}"
    
    case "$action" in
        setup)
            check_postgres_user
            setup_wal_archiving
            ;;
        archive)
            archive_wal_file "$2" "$3"
            ;;
        restore)
            setup_pitr "$2"
            ;;
        restore_wal)
            restore_wal "$2" "$3"
            ;;
        cleanup)
            cleanup_old_archives
            ;;
        status)
            show_status
            ;;
        *)
            echo "Usage: $0 {setup|archive|restore|cleanup|status}"
            echo ""
            echo "Commands:"
            echo "  setup                     - Configure WAL archiving"
            echo "  archive <wal_file> <path> - Archive a WAL file"
            echo "  restore <target_time>     - Setup point-in-time recovery"
            echo "  cleanup                   - Clean up old archives"
            echo "  status                    - Show archiving status"
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"