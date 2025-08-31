"""
Enterprise Database Management CLI
Command-line interface for database operations and management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Developer IA: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

 ATTENTION IMPORTANTE 
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de
"""

import click
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional
from tabulate import tabulate
from pathlib import Path

from backend.core.logging import get_logger
from backend.deployment.database.postgresql_manager import get_postgresql_manager
from backend.deployment.database.migration_runner import get_migration_runner
from backend.deployment.database.backup_manager import get_backup_manager, BackupType
from backend.deployment.database.replication_manager import get_replication_manager
from backend.deployment.database.performance_monitor import get_performance_monitor
from backend.deployment.database.connection_pool import get_pool_manager


logger = get_logger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', '-c', help='Configuration file path')
@click.pass_context
def database(ctx, verbose: bool, config: Optional[str]):
    """Enterprise Database Management CLI for IA Influencer Agent"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config
    
    if verbose:
        click.echo(" IA Influencer Agent - Database Management CLI")
        click.echo("=" * 50)


@database.group()
def migrate():
    """Database migration management"""
    pass


@migrate.command()
@click.option('--target', '-t', help='Target migration version')
@click.option('--dry-run', is_flag=True, help='Show what would be executed without running')
@click.pass_context
def up(ctx, target: Optional[str], dry_run: bool):
    """Run pending database migrations"""



    try:
        click.echo(" Running database migrations...")
        
        migration_runner = get_migration_runner()
        
        if dry_run:
            status = migration_runner.get_migration_status()
            pending = status.get('pending_migrations', [])
            
            if not pending:
                click.echo(" No pending migrations")
                return
            
            click.echo(f" {len(pending)} pending migrations:")
            for migration in pending:
                click.echo(f"  • {migration['version']}: {migration['name']}")
            return
        
        success = migration_runner.migrate_up(target)
        
        if success:
            click.echo(" Migrations completed successfully")
        else:
            click.echo(" Migration failed", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f" Migration error: {e}", err=True)
        sys.exit(1)


@migrate.command()
@click.argument('target_version')
@click.option('--force', is_flag=True, help='Force rollback even if risky')
@click.pass_context
def down(ctx, target_version: str, force: bool):
    """Rollback database migrations to target version"""



    try:
        if not force:
            click.confirm(
                f"  Are you sure you want to rollback to version {target_version}?",
                abort=True
            )
        
        click.echo(f" Rolling back to version {target_version}...")
        
        migration_runner = get_migration_runner()
        success = migration_runner.migrate_down(target_version)
        
        if success:
            click.echo(" Rollback completed successfully")
        else:
            click.echo(" Rollback failed", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f" Rollback error: {e}", err=True)
        sys.exit(1)


@migrate.command()
@click.pass_context
def status(ctx):
    """Show migration status"""



    try:
        migration_runner = get_migration_runner()
        status = migration_runner.get_migration_status()
        
        click.echo(" Migration Status")
        click.echo("-" * 30)
        click.echo(f"Total migrations: {status['total_migrations']}")
        click.echo(f"Executed: {status['executed_count']}")
        click.echo(f"Pending: {status['pending_count']}")
        click.echo(f"Failed: {status['failed_count']}")
        
        if status['last_migration']:
            click.echo(f"Last migration: {status['last_migration']}")
        
        if status['pending_migrations']:
            click.echo("
 Pending Migrations:")
            for migration in status['pending_migrations']:
                click.echo(f"  • {migration['version']}: {migration['name']}")
                if migration.get('description'):
                    click.echo(f"    {migration['description']}")
        
        if status['failed_migrations']:
            click.echo("
 Failed Migrations:")
            for migration in status['failed_migrations']:
                click.echo(f"  • {migration['version']}: {migration['name']}")
                if migration.get('error_message'):
                    click.echo(f"    Error: {migration['error_message']}")
        
    except Exception as e:
        click.echo(f" Error getting migration status: {e}", err=True)
        sys.exit(1)


@migrate.command()
@click.argument('name')
@click.option('--description', '-d', help='Migration description')
@click.option('--data-migration', is_flag=True, help='Mark as data migration')
@click.pass_context
def create(ctx, name: str, description: Optional[str], data_migration: bool):
    """Create new migration file"""



    try:
        click.echo(f" Creating migration: {name}")
        
        migration_runner = get_migration_runner()
        version = migration_runner.create_migration(
            name=name,
            description=description or "",
            is_data_migration=data_migration
        )
        
        click.echo(f" Created migration: {version}_{name}.py")
        
    except Exception as e:
        click.echo(f" Error creating migration: {e}", err=True)
        sys.exit(1)


@migrate.command()
@click.pass_context
def validate(ctx):
    """Validate all migrations"""



    try:
        click.echo(" Validating migrations...")
        
        migration_runner = get_migration_runner()
        validation = migration_runner.validate_migrations()
        
        if validation['valid']:
            click.echo(" All migrations are valid")
        else:
            click.echo(" Migration validation failed:")
            for error in validation['errors']:
                click.echo(f"  • {error}")
        
        if validation['warnings']:
            click.echo("
  Warnings:")
            for warning in validation['warnings']:
                click.echo(f"  • {warning}")
        
    except Exception as e:
        click.echo(f" Validation error: {e}", err=True)
        sys.exit(1)


@database.group()
def backup():
    """Database backup management"""
    pass


@backup.command()
@click.option('--compress', is_flag=True, default=True, help='Compress backup file')
@click.option('--upload', is_flag=True, help='Upload to cloud storage')
@click.option('--database', '-d', help='Database name (default: configured database)')
@click.pass_context
def create(ctx, compress: bool, upload: bool, database: Optional[str]):
    """Create database backup"""



    try:
        click.echo(" Creating database backup...")
        
        backup_manager = get_backup_manager()
        metadata = backup_manager.create_full_backup(
            database_name=database,
            compress=compress,
            upload_to_cloud=upload
        )
        
        if metadata:
            click.echo(f" Backup created: {metadata.backup_id}")
            click.echo(f" File: {metadata.filename}")
            click.echo(f" Size: {metadata.size_bytes / (1024*1024):.2f} MB")
            click.echo(f"⏱  Duration: {metadata.duration_seconds:.2f} seconds")
            
            if compress:
                click.echo(f"  Compression: {metadata.compression_ratio:.1%}")
        else:
            click.echo(" Backup failed", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f" Backup error: {e}", err=True)
        sys.exit(1)


@backup.command()
@click.option('--type', '-t', 'backup_type', 
              type=click.Choice(['full', 'incremental', 'differential']),
              help='Filter by backup type')
@click.option('--limit', '-l', type=int, default=10, help='Limit number of results')
@click.pass_context
def list(ctx, backup_type: Optional[str], limit: int):
    """List available backups"""



    try:
        backup_manager = get_backup_manager()
        
        filter_type = None
        if backup_type:
            filter_type = BackupType(backup_type.upper())
        
        backups = backup_manager.list_backups(
            backup_type=filter_type,
            limit=limit
        )
        
        if not backups:
            click.echo(" No backups found")
            return
        
        # Prepare table data
        table_data = []
        for backup in backups:
            table_data.append([
                backup.backup_id,
                backup.backup_type.value,
                backup.database_name,
                f"{backup.size_bytes / (1024*1024):.1f} MB",
                f"{backup.duration_seconds:.1f}s",
                backup.status.value,
                backup.created_at.strftime("%Y-%m-%d %H:%M")
            ])
        
        headers = ["Backup ID", "Type", "Database", "Size", "Duration", "Status", "Created"]
        
        click.echo(" Available Backups:")
        click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
        
    except Exception as e:
        click.echo(f" Error listing backups: {e}", err=True)
        sys.exit(1)


@backup.command()
@click.argument('backup_id')
@click.option('--target-database', '-t', help='Target database name')
@click.option('--force', is_flag=True, help='Force restore without confirmation')
@click.pass_context
def restore(ctx, backup_id: str, target_database: Optional[str], force: bool):
    """Restore database from backup"""



    try:
        if not force:
            click.confirm(
                f"  Are you sure you want to restore backup {backup_id}?",
                abort=True
            )
        
        click.echo(f" Restoring backup: {backup_id}")
        
        backup_manager = get_backup_manager()
        success = backup_manager.restore_backup(
            backup_id=backup_id,
            target_database=target_database
        )
        
        if success:
            click.echo(" Restore completed successfully")
        else:
            click.echo(" Restore failed", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f" Restore error: {e}", err=True)
        sys.exit(1)


@backup.command()
@click.option('--retention-days', '-r', type=int, default=30, help='Retention period in days')
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned without doing it')
@click.pass_context
def cleanup(ctx, retention_days: int, dry_run: bool):
    """Clean up old backups"""



    try:
        if dry_run:
            click.echo(f" Checking for backups older than {retention_days} days...")
            # This would require implementing a dry-run mode in BackupManager
            click.echo("Dry-run mode not yet implemented")
            return
        
        click.echo(f"🧹 Cleaning up backups older than {retention_days} days...")
        
        backup_manager = get_backup_manager()
        cleaned_count = backup_manager.cleanup_old_backups(retention_days)
        
        click.echo(f" Cleaned up {cleaned_count} old backups")
        
    except Exception as e:
        click.echo(f" Cleanup error: {e}", err=True)
        sys.exit(1)


@database.group()
def replication():
    """Database replication management"""
    pass


@replication.command()
@click.pass_context
def status(ctx):
    """Show replication status"""



    try:
        replication_manager = get_replication_manager()
        status = replication_manager.get_replication_status()
        
        click.echo(" Replication Status")
        click.echo("-" * 40)
        click.echo(f"Is Primary: {status.get('is_primary', 'Unknown')}")
        click.echo(f"Timestamp: {status.get('timestamp', 'Unknown')}")
        
        if status.get('connected_replicas'):
            click.echo(f"
 Connected Replicas ({len(status['connected_replicas'])}):")
            
            table_data = []
            for replica in status['connected_replicas']:
                table_data.append([
                    replica.get('client_addr', 'Unknown'),
                    replica.get('state', 'Unknown'),
                    replica.get('sync_state', 'Unknown'),
                    replica.get('replay_lag', 'Unknown'),
                    replica.get('sync_priority', 'Unknown')
                ])
            
            headers = ["Address", "State", "Sync State", "Lag", "Priority"]
            click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        if status.get('recovery_status'):
            recovery = status['recovery_status']
            click.echo(f"
 Recovery Status:")
            click.echo(f"In Recovery: {recovery.get('in_recovery', 'Unknown')}")
            click.echo(f"Lag Bytes: {recovery.get('lag_bytes', 'Unknown')}")
        
    except Exception as e:
        click.echo(f" Error getting replication status: {e}", err=True)
        sys.exit(1)


@replication.command()
@click.pass_context
def monitor(ctx):
    """Start replication monitoring"""



    try:
        click.echo(" Starting replication monitoring...")
        
        replication_manager = get_replication_manager()
        replication_manager.start_monitoring()
        
        click.echo(" Replication monitoring started")
        click.echo("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            replication_manager.stop_monitoring()
            click.echo("
 Monitoring stopped")
        
    except Exception as e:
        click.echo(f" Monitoring error: {e}", err=True)
        sys.exit(1)


@database.group()
def performance():
    """Database performance monitoring"""
    pass


@performance.command()
@click.pass_context
def monitor(ctx):
    """Start performance monitoring"""



    try:
        click.echo(" Starting performance monitoring...")
        
        monitor = get_performance_monitor()
        monitor.start_monitoring()
        
        click.echo(" Performance monitoring started")
        click.echo("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                time.sleep(5)
                summary = monitor.get_performance_summary()
                
                # Clear screen and show current status
                click.clear()
                click.echo(" Performance Dashboard")
                click.echo("=" * 50)
                click.echo(f"Overall Status: {summary.get('overall_status', 'Unknown')}")
                click.echo(f"Active Alerts: {summary.get('active_alerts', 0)}")
                click.echo(f"Critical Alerts: {summary.get('critical_alerts', 0)}")
                click.echo(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
                
                # Show key metrics
                metrics = summary.get('metrics', {})
                if metrics:
                    click.echo("
 Key Metrics:")
                    for name, metric in list(metrics.items())[:10]:
                        value = metric.get('value', 0)
                        unit = metric.get('unit', '')
                        click.echo(f"  {name}: {value:.2f} {unit}")
                
                # Show top slow queries
                slow_queries = summary.get('top_slow_queries', [])
                if slow_queries:
                    click.echo("
 Slowest Queries:")
                    for i, query in enumerate(slow_queries[:3], 1):
                        click.echo(f"  {i}. {query['mean_exec_time']:.2f}s - {query['query_text'][:50]}...")
                
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            click.echo("
 Monitoring stopped")
        
    except Exception as e:
        click.echo(f" Monitoring error: {e}", err=True)
        sys.exit(1)


@performance.command()
@click.pass_context
def summary(ctx):
    """Show performance summary"""



    try:
        monitor = get_performance_monitor()
        summary = monitor.get_performance_summary()
        
        click.echo(" Performance Summary")
        click.echo("-" * 40)
        click.echo(f"Overall Status: {summary.get('overall_status', 'Unknown')}")
        click.echo(f"Timestamp: {summary.get('timestamp', 'Unknown')}")
        click.echo(f"Active Alerts: {summary.get('active_alerts', 0)}")
        click.echo(f"Critical Alerts: {summary.get('critical_alerts', 0)}")
        
        # Show metrics
        metrics = summary.get('metrics', {})
        if metrics:
            click.echo("
 Current Metrics:")
            
            table_data = []
            for name, metric in metrics.items():
                table_data.append([
                    name.replace('_', ' ').title(),
                    f"{metric.get('value', 0):.2f}",
                    metric.get('unit', ''),
                ])
            
            headers = ["Metric", "Value", "Unit"]
            click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Show optimization suggestions
        suggestions = summary.get('optimization_suggestions', [])
        if suggestions:
            click.echo("
 Optimization Suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                click.echo(f"  {i}. {suggestion.get('recommendation', 'No recommendation')}")
        
    except Exception as e:
        click.echo(f" Error getting performance summary: {e}", err=True)
        sys.exit(1)


@performance.command()
@click.option('--hours', '-h', type=int, default=24, help='Report period in hours')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def report(ctx, hours: int, output: Optional[str]):
    """Generate performance report"""



    try:
        click.echo(f" Generating {hours}-hour performance report...")
        
        monitor = get_performance_monitor()
        report_data = monitor.generate_performance_report(hours)
        
        if output:
            with open(output, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            click.echo(f" Report saved to: {output}")
        else:
            click.echo(json.dumps(report_data, indent=2, default=str))
        
    except Exception as e:
        click.echo(f" Report generation error: {e}", err=True)
        sys.exit(1)


@database.group()
def pool():
    """Connection pool management"""
    pass


@pool.command()
@click.pass_context
def status(ctx):
    """Show connection pool status"""



    try:
        pool_manager = get_pool_manager()
        status = pool_manager.get_pool_status()
        
        click.echo(" Connection Pool Status")
        click.echo("-" * 40)
        click.echo(f"Total Endpoints: {status.get('total_endpoints', 0)}")
        click.echo(f"Active Endpoints: {status.get('active_endpoints', 0)}")
        click.echo(f"Primary Endpoint: {status.get('primary_endpoint', 'Unknown')}")
        click.echo(f"Read Replicas: {len(status.get('read_replicas', []))}")
        click.echo(f"Failover in Progress: {status.get('failover_in_progress', False)}")
        
        # Show endpoint details
        endpoints = status.get('endpoints', {})
        if endpoints:
            click.echo("
 Endpoints:")
            
            table_data = []
            for endpoint_id, endpoint in endpoints.items():
                stats = status.get('pool_stats', {}).get(endpoint_id, {})
                table_data.append([
                    endpoint_id,
                    endpoint.get('role', 'Unknown'),
                    f"{endpoint.get('host', 'Unknown')}:{endpoint.get('port', 'Unknown')}",
                    "" if endpoint.get('is_active', False) else "",
                    stats.get('active_connections', 0),
                    f"{stats.get('pool_utilization', 0):.1%}",
                    f"{stats.get('success_rate', 0):.1f}%"
                ])
            
            headers = ["Endpoint", "Role", "Address", "Active", "Connections", "Utilization", "Success Rate"]
            click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
        
    except Exception as e:
        click.echo(f" Error getting pool status: {e}", err=True)
        sys.exit(1)


@database.command()
@click.pass_context
def health(ctx):
    """Check database health"""



    try:
        click.echo(" Checking database health...")
        
        db_manager = get_postgresql_manager()
        health = db_manager.health_check()
        
        status_emoji = {
            'healthy': '',
            'warning': ' ',
            'unhealthy': ''
        }.get(health.get('status', 'unknown'), '')
        
        click.echo(f"
{status_emoji} Overall Status: {health.get('status', 'Unknown')}")
        click.echo(f" Timestamp: {health.get('timestamp', 'Unknown')}")
        
        checks = health.get('checks', {})
        if checks:
            click.echo("
 Health Checks:")
            for check_name, result in checks.items():
                check_emoji = '' if 'ok' in str(result).lower() else ''
                click.echo(f"  {check_emoji} {check_name.replace('_', ' ').title()}: {result}")
        
    except Exception as e:
        click.echo(f" Health check error: {e}", err=True)
        sys.exit(1)


@database.command()
@click.pass_context
def info(ctx):
    """Show database information"""



    try:
        click.echo("ℹ  Database Information")
        click.echo("-" * 40)
        
        db_manager = get_postgresql_manager()
        info = db_manager.get_database_info()
        
        if info:
            click.echo(f"Version: {info.get('version', 'Unknown')}")
            click.echo(f"Size: {info.get('size', 'Unknown')}")
            click.echo(f"Active Connections: {info.get('active_connections', 'Unknown')}")
            click.echo(f"Tables: {info.get('table_count', 'Unknown')}")
            click.echo(f"Indexes: {info.get('index_count', 'Unknown')}")
        else:
            click.echo(" Unable to retrieve database information")
        
    except Exception as e:
        click.echo(f" Error getting database info: {e}", err=True)
        sys.exit(1)


@database.command()
@click.argument('table_name')
@click.pass_context
def optimize(ctx, table_name: str):
    """Optimize table performance"""



    try:
        click.echo(f" Optimizing table: {table_name}")
        
        db_manager = get_postgresql_manager()
        success = db_manager.optimize_table(table_name)
        
        if success:
            click.echo(" Table optimization completed")
        else:
            click.echo(" Table optimization failed", err=True)
            sys.exit(1)
        
    except Exception as e:
        click.echo(f" Optimization error: {e}", err=True)
        sys.exit(1)


@database.command()
@click.argument('table_name')
@click.pass_context
def stats(ctx, table_name: str):
    """Show table statistics"""



    try:
        click.echo(f" Table Statistics: {table_name}")
        click.echo("-" * 40)
        
        db_manager = get_postgresql_manager()
        stats = db_manager.get_table_statistics(table_name)
        
        if stats:
            click.echo(f"Rows: {stats.get('row_count', 'Unknown')}")
            click.echo(f"Size: {stats.get('size', 'Unknown')}")
            
            columns = stats.get('columns', [])
            if columns:
                click.echo(f"
 Columns ({len(columns)}):")
                
                table_data = []
                for col in columns:
                    table_data.append([
                        col.get('name', 'Unknown'),
                        col.get('type', 'Unknown'),
                        "Yes" if col.get('nullable', False) else "No"
                    ])
                
                headers = ["Name", "Type", "Nullable"]
                click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            indexes = stats.get('indexes', [])
            if indexes:
                click.echo(f"
 Indexes ({len(indexes)}):")
                for idx in indexes:
                    click.echo(f"  • {idx.get('name', 'Unknown')}")
        else:
            click.echo(" Unable to retrieve table statistics")
        
    except Exception as e:
        click.echo(f" Error getting table stats: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    database()

import click
import json
from typing import Optional
from datetime import datetime
from pathlib import Path

from .postgresql_manager import get_postgresql_manager
from .migration_runner import get_migration_runner
from .backup_manager import get_backup_manager, BackupType
from .replication_manager import get_replication_manager
from backend.core.logging import get_logger


logger = get_logger(__name__)


@click.group()
def database():
    """Database deployment and management commands"""
    pass


@database.group()
def migrate():
    """Database migration commands"""
    pass


@migrate.command()
@click.option('--target', help='Target migration version')
def up(target: Optional[str]):
    """Run pending migrations"""



    try:
        migration_runner = get_migration_runner()
        success = migration_runner.migrate_up(target)
        
        if success:
            click.echo(" Migrations completed successfully")
        else:
            click.echo(" Migration failed", err=True)
            
    except Exception as e:
        click.echo(f" Migration error: {e}", err=True)


@migrate.command()
@click.argument('target_version')
def down(target_version: str):
    """Rollback migrations to target version"""



    try:
        migration_runner = get_migration_runner()
        success = migration_runner.migrate_down(target_version)
        
        if success:
            click.echo(" Rollback completed successfully")
        else:
            click.echo(" Rollback failed", err=True)
            
    except Exception as e:
        click.echo(f" Rollback error: {e}", err=True)


@migrate.command()
def status():
    """Show migration status"""



    try:
        migration_runner = get_migration_runner()
        status = migration_runner.get_migration_status()
        
        click.echo(f"Total migrations: {status['total_migrations']}")
        click.echo(f"Executed: {status['executed_count']}")
        click.echo(f"Pending: {status['pending_count']}")
        click.echo(f"Failed: {status['failed_count']}")
        
        if status['migrations']:
            click.echo("\nMigrations:")
            for migration in status['migrations']:
                status_icon = "" if migration['status'] == 'completed' else "⏳" if migration['status'] == 'pending' else ""
                click.echo(f"{status_icon} {migration['version']} - {migration['name']}")
                
    except Exception as e:
        click.echo(f" Status error: {e}", err=True)


@migrate.command()
@click.argument('name')
@click.option('--description', help='Migration description')
def create(name: str, description: Optional[str]):
    """Create new migration file"""



    try:
        migration_runner = get_migration_runner()
        filepath = migration_runner.create_migration(name, description or "")
        
        click.echo(f" Created migration: {filepath}")
        
    except Exception as e:
        click.echo(f" Creation error: {e}", err=True)


@migrate.command()
def validate():
    """Validate migration files"""



    try:
        migration_runner = get_migration_runner()
        errors = migration_runner.validate_migrations()
        
        total_errors = sum(len(error_list) for error_list in errors.values())
        
        if total_errors == 0:
            click.echo(" All migrations are valid")
        else:
            click.echo(f" Found {total_errors} validation errors:")
            
            for error_type, error_list in errors.items():
                if error_list:
                    click.echo(f"\n{error_type.title()}:")
                    for error in error_list:
                        click.echo(f"  - {error}")
                        
    except Exception as e:
        click.echo(f" Validation error: {e}", err=True)


@database.group()
def backup():
    """Database backup commands"""
    pass


@backup.command()
@click.option('--database', help='Database name')
@click.option('--compress/--no-compress', default=True, help='Compress backup')
@click.option('--upload/--no-upload', default=True, help='Upload to cloud')
def create(database: Optional[str], compress: bool, upload: bool):
    """Create full database backup"""



    try:
        backup_manager = get_backup_manager()
        metadata = backup_manager.create_full_backup(
            database_name=database,
            compress=compress,
            upload_to_cloud=upload
        )
        
        if metadata:
            click.echo(f" Backup created: {metadata.backup_id}")
            click.echo(f"   File: {metadata.filename}")
            click.echo(f"   Size: {metadata.size_bytes} bytes")
            click.echo(f"   Duration: {metadata.duration_seconds:.2f}s")
        else:
            click.echo(" Backup failed", err=True)
            
    except Exception as e:
        click.echo(f" Backup error: {e}", err=True)


@backup.command()
def list():
    """List available backups"""



    try:
        backup_manager = get_backup_manager()
        backups = backup_manager.list_backups(limit=20)
        
        if not backups:
            click.echo("No backups found")
            return
        
        click.echo(f"Found {len(backups)} backups:\n")
        
        for backup in backups:
            status_icon = "" if backup.status.value == 'completed' else ""
            click.echo(
                f"{status_icon} {backup.backup_id} ({backup.backup_type.value})"
            )
            click.echo(f"   Created: {backup.created_at}")
            click.echo(f"   Size: {backup.size_bytes} bytes")
            click.echo(f"   File: {backup.filename}\n")
            
    except Exception as e:
        click.echo(f" List error: {e}", err=True)


@backup.command()
@click.argument('backup_id')
@click.option('--target-database', help='Target database name')
def restore(backup_id: str, target_database: Optional[str]):
    """Restore database from backup"""



    try:
        backup_manager = get_backup_manager()
        success = backup_manager.restore_backup(backup_id, target_database)
        
        if success:
            click.echo(f" Backup {backup_id} restored successfully")
        else:
            click.echo(f" Restore failed", err=True)
            
    except Exception as e:
        click.echo(f" Restore error: {e}", err=True)


@backup.command()
@click.option('--retention-days', default=30, help='Retention period in days')
def cleanup(retention_days: int):
    """Clean up old backup files"""



    try:
        backup_manager = get_backup_manager()
        cleaned_count = backup_manager.cleanup_old_backups(retention_days)
        
        click.echo(f" Cleaned up {cleaned_count} old backups")
        
    except Exception as e:
        click.echo(f" Cleanup error: {e}", err=True)


@backup.command()
def stats():
    """Show backup statistics"""



    try:
        backup_manager = get_backup_manager()
        stats = backup_manager.get_backup_statistics()
        
        click.echo(f"Total backups: {stats['total_backups']}")
        click.echo(f"Total size: {stats['total_size_bytes']} bytes")
        click.echo(f"Failed backups: {stats['failed_backups']}")
        click.echo(f"Average compression: {stats['average_compression_ratio']:.2%}")
        
        if stats['by_type']:
            click.echo("\nBy type:")
            for backup_type, count in stats['by_type'].items():
                click.echo(f"  {backup_type}: {count}")
        
        if stats['latest_backup']:
            latest = stats['latest_backup']
            click.echo(f"\nLatest backup: {latest['backup_id']} ({latest['type']})")
            click.echo(f"Created: {latest['created_at']}")
            
    except Exception as e:
        click.echo(f" Stats error: {e}", err=True)


@database.group()
def replication():
    """Database replication commands"""
    pass


@replication.command()
def status():
    """Show replication status"""



    try:
        replication_manager = get_replication_manager()
        status = replication_manager.get_replication_status()
        
        click.echo(f"Primary server: {status['is_primary']}")
        
        if status['is_primary']:
            click.echo(f"Connected replicas: {status.get('replica_count', 0)}")
            
            for replica in status.get('connected_replicas', []):
                click.echo(f"\nReplica: {replica['client_addr']}")
                click.echo(f"  State: {replica['state']}")
                click.echo(f"  Sync state: {replica['sync_state']}")
                click.echo(f"  Replay lag: {replica.get('replay_lag', 'N/A')}")
        else:
            recovery = status.get('recovery_status', {})
            click.echo(f"In recovery: {recovery.get('in_recovery', False)}")
            click.echo(f"Lag bytes: {recovery.get('lag_bytes', 0)}")
            
    except Exception as e:
        click.echo(f" Replication status error: {e}", err=True)


@replication.command()
@click.argument('slot_name')
@click.option('--type', 'slot_type', default='physical', help='Slot type (physical/logical)')
def create_slot(slot_name: str, slot_type: str):
    """Create replication slot"""



    try:
        replication_manager = get_replication_manager()
        success = replication_manager.create_replication_slot(slot_name, slot_type)
        
        if success:
            click.echo(f" Created {slot_type} replication slot: {slot_name}")
        else:
            click.echo(f" Failed to create slot: {slot_name}", err=True)
            
    except Exception as e:
        click.echo(f" Slot creation error: {e}", err=True)


@replication.command()
@click.argument('slot_name')
def drop_slot(slot_name: str):
    """Drop replication slot"""



    try:
        replication_manager = get_replication_manager()
        success = replication_manager.drop_replication_slot(slot_name)
        
        if success:
            click.echo(f" Dropped replication slot: {slot_name}")
        else:
            click.echo(f" Failed to drop slot: {slot_name}", err=True)
            
    except Exception as e:
        click.echo(f" Slot deletion error: {e}", err=True)


@database.command()
def health():
    """Check database health"""



    try:
        db_manager = get_postgresql_manager()
        health_status = db_manager.health_check()
        
        status_icon = "" if health_status['status'] == 'healthy' else "" if health_status['status'] == 'warning' else ""
        click.echo(f"{status_icon} Database status: {health_status['status']}")
        
        for check_name, check_result in health_status['checks'].items():
            check_icon = "" if 'ok' in str(check_result).lower() else "" if 'warning' in str(check_result).lower() else ""
            click.echo(f"{check_icon} {check_name}: {check_result}")
            
    except Exception as e:
        click.echo(f" Health check error: {e}", err=True)


@database.command()
def info():
    """Show database information"""



    try:
        db_manager = get_postgresql_manager()
        info = db_manager.get_database_info()
        
        click.echo("Database Information:")
        click.echo(f"  Version: {info.get('version', 'N/A')}")
        click.echo(f"  Size: {info.get('size', 'N/A')}")
        click.echo(f"  Active connections: {info.get('active_connections', 'N/A')}")
        click.echo(f"  Tables: {info.get('table_count', 'N/A')}")
        click.echo(f"  Indexes: {info.get('index_count', 'N/A')}")
        
    except Exception as e:
        click.echo(f" Info error: {e}", err=True)


@database.command()
@click.argument('table_name')
def optimize(table_name: str):
    """Optimize table performance"""



    try:
        db_manager = get_postgresql_manager()
        success = db_manager.optimize_table(table_name)
        
        if success:
            click.echo(f" Table {table_name} optimized successfully")
        else:
            click.echo(f" Failed to optimize table {table_name}", err=True)
            
    except Exception as e:
        click.echo(f" Optimization error: {e}", err=True)


if __name__ == '__main__':
    database()
