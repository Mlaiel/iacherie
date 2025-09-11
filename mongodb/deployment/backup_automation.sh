#!/bin/bash
# =============================================================================
# MONGODB BACKUP AUTOMATION SCRIPT
# =============================================================================
# Automated backup and restore solution for MongoDB with compression,
# encryption, and cloud storage integration.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/ainflue/mongodb-backup.log"

# Default configuration
MONGODB_HOST="${MONGODB_HOST:-localhost:27017}"
MONGODB_DATABASE="${MONGODB_DATABASE:-ainflue}"
MONGODB_USERNAME="${MONGODB_USERNAME:-backup_user}"
MONGODB_PASSWORD="${MONGODB_PASSWORD:-}"
BACKUP_DIR="${BACKUP_DIR:-/backup/mongodb}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
COMPRESSION="${COMPRESSION:-gzip}"
ENCRYPTION="${ENCRYPTION:-false}"
ENCRYPTION_KEY="${ENCRYPTION_KEY:-}"
CLOUD_STORAGE="${CLOUD_STORAGE:-false}"
CLOUD_PROVIDER="${CLOUD_PROVIDER:-aws}"
CLOUD_BUCKET="${CLOUD_BUCKET:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() { log "INFO" "${BLUE}$1${NC}"; }
warn() { log "WARN" "${YELLOW}$1${NC}"; }
error() { log "ERROR" "${RED}$1${NC}"; }
success() { log "SUCCESS" "${GREEN}$1${NC}"; }

# Function to check prerequisites
check_prerequisites() {
    info "Checking backup prerequisites..."
    
    # Check mongodump
    if ! command -v mongodump &> /dev/null; then
        error "mongodump is not installed or not in PATH"
        exit 1
    fi
    
    # Check mongoexport
    if ! command -v mongoexport &> /dev/null; then
        warn "mongoexport not found - collection exports will be skipped"
    fi
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Check disk space (require at least 10GB free)
    local available_space=$(df "$BACKUP_DIR" | awk 'NR==2 {print $4}')
    local required_space=10485760  # 10GB in KB
    
    if [ "$available_space" -lt "$required_space" ]; then
        warn "Low disk space available: $(($available_space / 1024 / 1024))GB"
    fi
    
    success "Prerequisites check completed"
}

# Function to perform MongoDB backup
perform_backup() {
    local backup_type="$1"
    local backup_date=$(date +%Y%m%d_%H%M%S)
    local backup_name="mongodb_${backup_type}_${backup_date}"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    info "Starting $backup_type backup: $backup_name"
    
    case $backup_type in
        "full")
            perform_full_backup "$backup_path"
            ;;
        "incremental")
            perform_incremental_backup "$backup_path"
            ;;
        "collections")
            perform_collections_backup "$backup_path"
            ;;
        *)
            error "Unknown backup type: $backup_type"
            exit 1
            ;;
    esac
    
    # Post-process backup
    post_process_backup "$backup_path"
    
    success "$backup_type backup completed: $backup_path"
}

# Function to perform full database backup
perform_full_backup() {
    local backup_path="$1"
    
    info "Performing full database backup..."
    
    # Build mongodump command
    local mongodump_cmd="mongodump"
    mongodump_cmd+=" --host=$MONGODB_HOST"
    
    if [ -n "$MONGODB_USERNAME" ]; then
        mongodump_cmd+=" --username=$MONGODB_USERNAME"
        mongodump_cmd+=" --password=$MONGODB_PASSWORD"
        mongodump_cmd+=" --authenticationDatabase=admin"
    fi
    
    if [ "$MONGODB_DATABASE" != "all" ]; then
        mongodump_cmd+=" --db=$MONGODB_DATABASE"
    fi
    
    mongodump_cmd+=" --out=$backup_path"
    mongodump_cmd+=" --gzip"
    
    # Execute backup
    if eval "$mongodump_cmd"; then
        success "Full backup completed successfully"
    else
        error "Full backup failed"
        exit 1
    fi
}

# Function to perform incremental backup (oplog)
perform_incremental_backup() {
    local backup_path="$1"
    
    info "Performing incremental backup (oplog)..."
    
    # Get the last oplog timestamp
    local last_oplog_file="$BACKUP_DIR/.last_oplog_timestamp"
    local start_time=""
    
    if [ -f "$last_oplog_file" ]; then
        start_time=$(cat "$last_oplog_file")
        info "Starting from oplog timestamp: $start_time"
    else
        warn "No previous oplog timestamp found, performing full oplog backup"
    fi
    
    # Build mongodump command for oplog
    local mongodump_cmd="mongodump"
    mongodump_cmd+=" --host=$MONGODB_HOST"
    
    if [ -n "$MONGODB_USERNAME" ]; then
        mongodump_cmd+=" --username=$MONGODB_USERNAME"
        mongodump_cmd+=" --password=$MONGODB_PASSWORD"
        mongodump_cmd+=" --authenticationDatabase=admin"
    fi
    
    mongodump_cmd+=" --db=local"
    mongodump_cmd+=" --collection=oplog.rs"
    mongodump_cmd+=" --out=$backup_path"
    mongodump_cmd+=" --gzip"
    
    if [ -n "$start_time" ]; then
        mongodump_cmd+=" --query='{\"ts\": {\$gt: $start_time}}'"
    fi
    
    # Execute backup
    if eval "$mongodump_cmd"; then
        # Save current timestamp for next incremental backup
        local current_time=$(date +%s)
        echo "$current_time" > "$last_oplog_file"
        success "Incremental backup completed successfully"
    else
        error "Incremental backup failed"
        exit 1
    fi
}

# Function to perform collections backup (JSON export)
perform_collections_backup() {
    local backup_path="$1"
    
    info "Performing collections backup (JSON export)..."
    
    if ! command -v mongoexport &> /dev/null; then
        warn "mongoexport not available, skipping collections backup"
        return
    fi
    
    mkdir -p "$backup_path/collections"
    
    # Get list of collections
    local collections_list=$(mongo "$MONGODB_HOST/$MONGODB_DATABASE" --quiet --eval "db.getCollectionNames().join('\n')")
    
    while IFS= read -r collection; do
        if [ -n "$collection" ]; then
            info "Exporting collection: $collection"
            
            local export_cmd="mongoexport"
            export_cmd+=" --host=$MONGODB_HOST"
            export_cmd+=" --db=$MONGODB_DATABASE"
            export_cmd+=" --collection=$collection"
            
            if [ -n "$MONGODB_USERNAME" ]; then
                export_cmd+=" --username=$MONGODB_USERNAME"
                export_cmd+=" --password=$MONGODB_PASSWORD"
                export_cmd+=" --authenticationDatabase=admin"
            fi
            
            export_cmd+=" --out=$backup_path/collections/${collection}.json"
            export_cmd+=" --jsonArray"
            
            eval "$export_cmd"
        fi
    done <<< "$collections_list"
    
    success "Collections backup completed"
}

# Function to post-process backup (compression, encryption, cloud upload)
post_process_backup() {
    local backup_path="$1"
    local final_path="$backup_path"
    
    # Compression
    if [ "$COMPRESSION" = "gzip" ]; then
        info "Compressing backup..."
        tar -czf "${backup_path}.tar.gz" -C "$(dirname "$backup_path")" "$(basename "$backup_path")"
        rm -rf "$backup_path"
        final_path="${backup_path}.tar.gz"
        success "Backup compressed"
    elif [ "$COMPRESSION" = "xz" ]; then
        info "Compressing backup with xz..."
        tar -cJf "${backup_path}.tar.xz" -C "$(dirname "$backup_path")" "$(basename "$backup_path")"
        rm -rf "$backup_path"
        final_path="${backup_path}.tar.xz"
        success "Backup compressed with xz"
    fi
    
    # Encryption
    if [ "$ENCRYPTION" = "true" ] && [ -n "$ENCRYPTION_KEY" ]; then
        info "Encrypting backup..."
        gpg --symmetric --cipher-algo AES256 --batch --yes --passphrase "$ENCRYPTION_KEY" "$final_path"
        rm -f "$final_path"
        final_path="${final_path}.gpg"
        success "Backup encrypted"
    fi
    
    # Cloud storage upload
    if [ "$CLOUD_STORAGE" = "true" ]; then
        upload_to_cloud "$final_path"
    fi
    
    # Generate checksum
    sha256sum "$final_path" > "${final_path}.sha256"
    
    # Save metadata
    save_backup_metadata "$final_path"
}

# Function to upload backup to cloud storage
upload_to_cloud() {
    local backup_file="$1"
    local filename=$(basename "$backup_file")
    
    info "Uploading backup to cloud storage ($CLOUD_PROVIDER)..."
    
    case $CLOUD_PROVIDER in
        "aws")
            if command -v aws &> /dev/null; then
                aws s3 cp "$backup_file" "s3://$CLOUD_BUCKET/mongodb-backups/$filename"
                aws s3 cp "${backup_file}.sha256" "s3://$CLOUD_BUCKET/mongodb-backups/${filename}.sha256"
                success "Backup uploaded to AWS S3"
            else
                warn "AWS CLI not available, skipping cloud upload"
            fi
            ;;
        "gcp")
            if command -v gsutil &> /dev/null; then
                gsutil cp "$backup_file" "gs://$CLOUD_BUCKET/mongodb-backups/$filename"
                gsutil cp "${backup_file}.sha256" "gs://$CLOUD_BUCKET/mongodb-backups/${filename}.sha256"
                success "Backup uploaded to Google Cloud Storage"
            else
                warn "Google Cloud SDK not available, skipping cloud upload"
            fi
            ;;
        "azure")
            if command -v az &> /dev/null; then
                az storage blob upload --file "$backup_file" --container-name mongodb-backups --name "$filename"
                az storage blob upload --file "${backup_file}.sha256" --container-name mongodb-backups --name "${filename}.sha256"
                success "Backup uploaded to Azure Blob Storage"
            else
                warn "Azure CLI not available, skipping cloud upload"
            fi
            ;;
        *)
            warn "Unknown cloud provider: $CLOUD_PROVIDER"
            ;;
    esac
}

# Function to save backup metadata
save_backup_metadata() {
    local backup_file="$1"
    local metadata_file="${backup_file}.metadata.json"
    
    cat > "$metadata_file" <<EOF
{
  "backup_date": "$(date -Iseconds)",
  "backup_file": "$(basename "$backup_file")",
  "backup_size": "$(stat -c%s "$backup_file" 2>/dev/null || echo 0)",
  "mongodb_host": "$MONGODB_HOST",
  "mongodb_database": "$MONGODB_DATABASE",
  "compression": "$COMPRESSION",
  "encryption": "$ENCRYPTION",
  "cloud_storage": "$CLOUD_STORAGE",
  "cloud_provider": "$CLOUD_PROVIDER",
  "checksum": "$(cat "${backup_file}.sha256" 2>/dev/null | cut -d' ' -f1)"
}
EOF
    
    info "Backup metadata saved: $metadata_file"
}

# Function to clean up old backups
cleanup_old_backups() {
    info "Cleaning up backups older than $RETENTION_DAYS days..."
    
    # Find and remove old backups
    find "$BACKUP_DIR" -name "mongodb_*" -type f -mtime +$RETENTION_DAYS -exec rm -f {} \;
    
    # Also clean up associated files (checksums, metadata)
    find "$BACKUP_DIR" -name "*.sha256" -type f -mtime +$RETENTION_DAYS -exec rm -f {} \;
    find "$BACKUP_DIR" -name "*.metadata.json" -type f -mtime +$RETENTION_DAYS -exec rm -f {} \;
    
    success "Old backups cleaned up"
}

# Function to restore backup
restore_backup() {
    local backup_file="$1"
    local restore_db="${2:-$MONGODB_DATABASE}"
    
    info "Restoring backup: $backup_file to database: $restore_db"
    
    # Verify backup file exists
    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
        exit 1
    fi
    
    # Verify checksum if available
    if [ -f "${backup_file}.sha256" ]; then
        info "Verifying backup integrity..."
        if sha256sum -c "${backup_file}.sha256"; then
            success "Backup integrity verified"
        else
            error "Backup integrity check failed"
            exit 1
        fi
    fi
    
    # Extract backup if compressed
    local restore_dir="/tmp/mongodb_restore_$$"
    mkdir -p "$restore_dir"
    
    if [[ "$backup_file" == *.tar.gz ]]; then
        tar -xzf "$backup_file" -C "$restore_dir"
    elif [[ "$backup_file" == *.tar.xz ]]; then
        tar -xJf "$backup_file" -C "$restore_dir"
    else
        cp -r "$backup_file" "$restore_dir/"
    fi
    
    # Find the backup directory
    local backup_dir=$(find "$restore_dir" -type d -name "mongodb_*" | head -1)
    
    if [ -z "$backup_dir" ]; then
        error "Cannot find backup directory in extracted files"
        exit 1
    fi
    
    # Build mongorestore command
    local mongorestore_cmd="mongorestore"
    mongorestore_cmd+=" --host=$MONGODB_HOST"
    mongorestore_cmd+=" --db=$restore_db"
    
    if [ -n "$MONGODB_USERNAME" ]; then
        mongorestore_cmd+=" --username=$MONGODB_USERNAME"
        mongorestore_cmd+=" --password=$MONGODB_PASSWORD"
        mongorestore_cmd+=" --authenticationDatabase=admin"
    fi
    
    mongorestore_cmd+=" --gzip"
    mongorestore_cmd+=" --drop"  # Drop existing collections before restore
    mongorestore_cmd+=" $backup_dir/$MONGODB_DATABASE"
    
    # Execute restore
    if eval "$mongorestore_cmd"; then
        success "Backup restored successfully"
    else
        error "Backup restore failed"
        exit 1
    fi
    
    # Cleanup temporary files
    rm -rf "$restore_dir"
}

# Function to list available backups
list_backups() {
    info "Available backups in $BACKUP_DIR:"
    echo ""
    
    # List local backups
    for backup in "$BACKUP_DIR"/mongodb_*; do
        if [ -f "$backup" ]; then
            local size=$(stat -c%s "$backup" 2>/dev/null | numfmt --to=iec)
            local date=$(stat -c%y "$backup" 2>/dev/null | cut -d' ' -f1,2)
            printf "%-50s %10s %s\n" "$(basename "$backup")" "$size" "$date"
        fi
    done
    
    echo ""
}

# Function to verify backup
verify_backup() {
    local backup_file="$1"
    
    info "Verifying backup: $backup_file"
    
    # Check file exists
    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Check checksum
    if [ -f "${backup_file}.sha256" ]; then
        if sha256sum -c "${backup_file}.sha256"; then
            success "Backup checksum verification passed"
        else
            error "Backup checksum verification failed"
            return 1
        fi
    else
        warn "No checksum file found for verification"
    fi
    
    # Check metadata
    if [ -f "${backup_file}.metadata.json" ]; then
        info "Backup metadata:"
        cat "${backup_file}.metadata.json" | jq .
    fi
    
    success "Backup verification completed"
}

# Main function
main() {
    local command="$1"
    shift
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    case $command in
        "backup")
            local backup_type="${1:-full}"
            check_prerequisites
            perform_backup "$backup_type"
            cleanup_old_backups
            ;;
        "restore")
            local backup_file="$1"
            local restore_db="${2:-}"
            restore_backup "$backup_file" "$restore_db"
            ;;
        "list")
            list_backups
            ;;
        "verify")
            local backup_file="$1"
            verify_backup "$backup_file"
            ;;
        "cleanup")
            cleanup_old_backups
            ;;
        *)
            echo "Usage: $0 {backup|restore|list|verify|cleanup} [options]"
            echo ""
            echo "Commands:"
            echo "  backup [type]           Perform backup (full|incremental|collections)"
            echo "  restore <file> [db]     Restore backup to database"
            echo "  list                    List available backups"
            echo "  verify <file>           Verify backup integrity"
            echo "  cleanup                 Clean up old backups"
            echo ""
            echo "Environment variables:"
            echo "  MONGODB_HOST           MongoDB connection host (default: localhost:27017)"
            echo "  MONGODB_DATABASE       Database name (default: ainflue)"
            echo "  MONGODB_USERNAME       MongoDB username"
            echo "  MONGODB_PASSWORD       MongoDB password"
            echo "  BACKUP_DIR             Backup directory (default: /backup/mongodb)"
            echo "  RETENTION_DAYS         Backup retention days (default: 7)"
            echo "  COMPRESSION            Compression type (gzip|xz|none)"
            echo "  ENCRYPTION             Enable encryption (true|false)"
            echo "  CLOUD_STORAGE          Enable cloud upload (true|false)"
            exit 1
            ;;
    esac
}

# Execute main function if script is run directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    if [ $# -lt 1 ]; then
        main "help"
    else
        main "$@"
    fi
fi