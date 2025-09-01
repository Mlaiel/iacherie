#!/usr/bin/env python3
"""Content Module Maintenance & Management Utilities
===============================================

Professional maintenance toolkit for the IA Influencer Agent content management system
with automated backups, performance optimization, system cleanup, and monitoring tools.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Expert Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ LEGAL WARNING: This code and concept are protected by intellectual property laws.
Any unauthorized copying, modification, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will 
result in legal action under German and international copyright laws.
"""

import os
import sys
import shutil
import logging
import argparse
import json
import asyncio
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import tarfile
import zipfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentModuleMaintenance:
    """
Comprehensive maintenance toolkit for content management system."""
    
    def __init__(self):
        self.base_path = Path.cwd()
        self.backup_path = Path("backups")
        self.logs_path = Path("logs")
        self.temp_path = Path("temp")
        self.reports_path = Path("reports")
        
        # Ensure required directories exist
        for path in [self.backup_path, self.logs_path, self.temp_path, self.reports_path]:
            path.mkdir(exist_ok=True)
    
    async def create_system_backup(self, backup_name: Optional[str] = None) -> Path:
        """Create comprehensive system backup."""
        logger.info("📦 Creating System Backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = backup_name or f"content_module_backup_{timestamp}"
        backup_file = self.backup_path / f"{backup_name}.tar.gz"
        
        # Files and directories to backup
        backup_items = [
            "*.py",
            "*.json",
            "*.md",
            "*.yml",
            "*.yaml",
            "*.txt",
            "requirements.txt",
            "Dockerfile",
            "docker-compose.yml",
            ".env.template",
            "config/",
            "docs/"
        ]
        
        # Create backup archive
        with tarfile.open(backup_file, "w:gz") as tar:
            for pattern in backup_items:
                for item in self.base_path.glob(pattern):
                    if item.is_file():
                        tar.add(item, arcname=item.name)
                    elif item.is_dir():
                        tar.add(item, arcname=item.name, recursive=True)
        
        # Create backup manifest
        manifest = {
            'backup_name': backup_name,
            'created_at': datetime.now().isoformat(),
            'backup_size_mb': backup_file.stat().st_size / 1024 / 1024,
            'files_backed_up': len(backup_items),
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform,
                'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown'
            }
        }
        
        manifest_file = self.backup_path / f"{backup_name}_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"✅ Backup created: {backup_file}")
        logger.info(f"📋 Manifest saved: {manifest_file}")
        
        return backup_file
    
    async def cleanup_system(self, aggressive: bool = False) -> Dict[str, Any]:
        """Perform system cleanup operations."""
        logger.info("🧹 Performing System Cleanup...")
        
        cleanup_results = {
            'temp_files_removed': 0,
            'logs_archived': 0,
            'cache_cleared': False,
            'space_freed_mb': 0
        }
        
        initial_usage = self._get_disk_usage()
        
        # Clean temporary files
        temp_patterns = ["*.tmp", "*.temp", "*~", ".DS_Store", "Thumbs.db", "*.pyc", "__pycache__"]
        
        for pattern in temp_patterns:
            for temp_file in self.base_path.rglob(pattern):
                try:
                    if temp_file.is_file():
                        file_size = temp_file.stat().st_size
                        temp_file.unlink()
                        cleanup_results['temp_files_removed'] += 1
                        cleanup_results['space_freed_mb'] += file_size / 1024 / 1024
                    elif temp_file.is_dir() and temp_file.name == "__pycache__":
                        shutil.rmtree(temp_file)
                        cleanup_results['temp_files_removed'] += 1
                except Exception as e:
                    logger.warning(f"Could not remove {temp_file}: {e}")
        
        # Archive old logs
        if self.logs_path.exists():
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for log_file in self.logs_path.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    archive_file = self.logs_path / f"archived_{log_file.stem}_{datetime.now().strftime('%Y%m%d')}.gz"
                    
                    try:
                        import gzip
                        with open(log_file, 'rb') as f_in:
                            with gzip.open(archive_file, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        
                        log_file.unlink()
                        cleanup_results['logs_archived'] += 1
                        
                    except Exception as e:
                        logger.warning(f"Could not archive {log_file}: {e}")
        
        # Aggressive cleanup (if requested)
        if aggressive:
            # Remove old backups (keep last 5)
            backups = sorted(self.backup_path.glob("*.tar.gz"), key=lambda x: x.stat().st_mtime, reverse=True)
            for old_backup in backups[5:]:
                try:
                    old_backup.unlink()
                    manifest_file = old_backup.with_suffix('.json')
                    if manifest_file.exists():
                        manifest_file.unlink()
                    cleanup_results['space_freed_mb'] += old_backup.stat().st_size / 1024 / 1024
                except Exception as e:
                    logger.warning(f"Could not remove old backup {old_backup}: {e}")
        
        final_usage = self._get_disk_usage()
        cleanup_results['space_freed_mb'] = round(cleanup_results['space_freed_mb'], 2)
        
        logger.info(f"✅ Cleanup completed: {cleanup_results['temp_files_removed']} files removed, {cleanup_results['space_freed_mb']} MB freed")
        
        return cleanup_results
    
    def _get_disk_usage(self) -> float:
        """Get current disk usage in MB."""
        try:
            return psutil.disk_usage(str(self.base_path)).used / 1024 / 1024
        except Exception:
            return 0.0
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """
Optimize system performance."""
        logger.info("⚡ Optimizing System Performance...")
        
        optimization_results = {
            'python_cache_cleared': False,
            'import_cache_refreshed': False,
            'memory_optimized': False,
            'recommendations': []
        }
        
        # Clear Python cache
        try:
            import sys
            if hasattr(sys, 'path_importer_cache'):
                sys.path_importer_cache.clear()
                optimization_results['python_cache_cleared'] = True
        except Exception as e:
            logger.warning(f"Could not clear import cache: {e}")
        
        # Memory optimization recommendations
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > 500:
            optimization_results['recommendations'].append("Consider restarting the application to free memory")
        
        cpu_percent = process.cpu_percent(interval=1)
        if cpu_percent > 80:
            optimization_results['recommendations'].append("High CPU usage detected - check for resource-intensive operations")
        
        # File system optimization
        if len(list(self.temp_path.glob("*"))) > 100:
            optimization_results['recommendations'].append("Many temporary files detected - consider running cleanup")
        
        # Add general performance recommendations
        optimization_results['recommendations'].extend([
            "Regularly run system cleanup to maintain performance",
            "Monitor memory usage during peak operations",
            "Consider implementing connection pooling for database operations",
            "Use async operations for I/O-bound tasks"
        ])
        
        logger.info(f"✅ Performance optimization completed with {len(optimization_results['recommendations'])} recommendations")
        
        return optimization_results
    
    async def generate_system_report(self) -> Dict[str, Any]:
        """Generate comprehensive system status report."""
        logger.info("📊 Generating System Report...")
        
        # System information
        process = psutil.Process()
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform,
                'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown',
                'working_directory': str(self.base_path),
                'process_id': os.getpid()
            },
            'resource_usage': {
                'memory_mb': round(process.memory_info().rss / 1024 / 1024, 2),
                'cpu_percent': process.cpu_percent(interval=1),
                'open_files': process.num_fds() if hasattr(process, 'num_fds') else 'N/A',
                'threads': process.num_threads()
            },
            'disk_usage': {
                'total_gb': round(psutil.disk_usage(str(self.base_path)).total / 1024 / 1024 / 1024, 2),
                'used_gb': round(psutil.disk_usage(str(self.base_path)).used / 1024 / 1024 / 1024, 2),
                'free_gb': round(psutil.disk_usage(str(self.base_path)).free / 1024 / 1024 / 1024, 2),
                'percent_used': psutil.disk_usage(str(self.base_path)).percent
            },
            'file_counts': {
                'python_files': len(list(self.base_path.glob("*.py"))),
                'config_files': len(list(self.base_path.glob("*.json"))) + len(list(self.base_path.glob("*.yml"))),
                'temp_files': len(list(self.temp_path.glob("*"))) if self.temp_path.exists() else 0,
                'log_files': len(list(self.logs_path.glob("*.log"))) if self.logs_path.exists() else 0,
                'backup_files': len(list(self.backup_path.glob("*.tar.gz"))) if self.backup_path.exists() else 0
            },
            'module_status': {
                'engines_found': len(list(self.base_path.glob("*engine*.py"))),
                'test_files': len(list(self.base_path.glob("test_*.py"))),
                'readme_files': len(list(self.base_path.glob("README*.md"))),
                'docker_files': len(list(self.base_path.glob("*ocker*")))
            }
        }
        
        # Save report
        report_file = self.reports_path / f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ System report saved: {report_file}")
        
        return report
    
    async def monitor_system(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """Monitor system resources for specified duration."""
        logger.info(f"👁️ Monitoring system for {duration_seconds} seconds...")
        
        monitoring_data = {
            'duration_seconds': duration_seconds,
            'start_time': datetime.now().isoformat(),
            'samples': [],
            'summary': {}
        }
        
        sample_interval = 5  # seconds
        samples_to_collect = duration_seconds // sample_interval
        
        process = psutil.Process()
        
        for i in range(samples_to_collect):
            sample = {
                'timestamp': datetime.now().isoformat(),
                'memory_mb': round(process.memory_info().rss / 1024 / 1024, 2),
                'cpu_percent': process.cpu_percent(),
                'threads': process.num_threads(),
                'system_cpu': psutil.cpu_percent(),
                'system_memory': psutil.virtual_memory().percent
            }
            
            monitoring_data['samples'].append(sample)
            
            if i < samples_to_collect - 1:
                await asyncio.sleep(sample_interval)
        
        # Calculate summary statistics
        if monitoring_data['samples']:
            memory_values = [s['memory_mb'] for s in monitoring_data['samples']]
            cpu_values = [s['cpu_percent'] for s in monitoring_data['samples']]
            
            monitoring_data['summary'] = {
                'avg_memory_mb': round(sum(memory_values) / len(memory_values), 2),
                'max_memory_mb': max(memory_values),
                'min_memory_mb': min(memory_values),
                'avg_cpu_percent': round(sum(cpu_values) / len(cpu_values), 2),
                'max_cpu_percent': max(cpu_values),
                'samples_collected': len(monitoring_data['samples'])
            }
        
        # Save monitoring data
        monitor_file = self.reports_path / f"monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(monitor_file, 'w') as f:
            json.dump(monitoring_data, f, indent=2)
        
        logger.info(f"✅ Monitoring completed. Data saved: {monitor_file}")
        
        return monitoring_data
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []
        
        for backup_file in self.backup_path.glob("*.tar.gz"):
            manifest_file = backup_file.with_suffix('.json')
            
            backup_info = {
                'filename': backup_file.name,
                'size_mb': round(backup_file.stat().st_size / 1024 / 1024, 2),
                'created': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                'has_manifest': manifest_file.exists()
            }
            
            if manifest_file.exists():
                try:
                    with open(manifest_file, 'r') as f:
                        manifest = json.load(f)
                        backup_info.update({
                            'backup_name': manifest.get('backup_name'),
                            'files_backed_up': manifest.get('files_backed_up')
                        })
                except Exception as e:
                    logger.warning(f"Could not read manifest for {backup_file.name}: {e}")
            
            backups.append(backup_info)
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    async def restore_backup(self, backup_filename: str, target_dir: Optional[str] = None) -> bool:
        """Restore from backup."""
        logger.info(f"🔄 Restoring from backup: {backup_filename}")
        
        backup_file = self.backup_path / backup_filename
        if not backup_file.exists():
            logger.error(f"Backup file not found: {backup_file}")
            return False
        
        target_path = Path(target_dir) if target_dir else self.base_path / "restored"
        target_path.mkdir(exist_ok=True)
        
        try:
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(target_path)
            
            logger.info(f"✅ Backup restored to: {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False


def main():
    """Main CLI interface for maintenance utilities."""
    parser = argparse.ArgumentParser(
        description="IA Influencer Agent - Content Module Maintenance Utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python maintenance.py backup --name daily_backup
  python maintenance.py cleanup --aggressive
  python maintenance.py optimize
  python maintenance.py report
  python maintenance.py monitor --duration 300
  python maintenance.py list-backups
  python maintenance.py restore --backup backup_file.tar.gz
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create system backup')
    backup_parser.add_argument('--name', help='Custom backup name')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean temporary files and optimize storage')
    cleanup_parser.add_argument('--aggressive', action='store_true', help='Perform aggressive cleanup')
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Optimize system performance')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate system status report')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor system resources')
    monitor_parser.add_argument('--duration', type=int, default=60, help='Monitoring duration in seconds')
    
    # List backups command
    list_parser = subparsers.add_parser('list-backups', help='List all available backups')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('--backup', required=True, help='Backup filename to restore')
    restore_parser.add_argument('--target', help='Target directory for restoration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize maintenance system
    maintenance = ContentModuleMaintenance()
    
    async def run_command():
        if args.command == 'backup':
            backup_file = await maintenance.create_system_backup(args.name)
            print(f"✅ Backup created: {backup_file}")
            
        elif args.command == 'cleanup':
            results = await maintenance.cleanup_system(args.aggressive)
            print(f"✅ Cleanup completed:")
            print(f"   - Files removed: {results['temp_files_removed']}")
            print(f"   - Logs archived: {results['logs_archived']}")
            print(f"   - Space freed: {results['space_freed_mb']} MB")
            
        elif args.command == 'optimize':
            results = await maintenance.optimize_performance()
            print(f"✅ Performance optimization completed")
            print(f"   - Recommendations: {len(results['recommendations'])}")
            for rec in results['recommendations'][:3]:
                print(f"     • {rec}")
            
        elif args.command == 'report':
            report = await maintenance.generate_system_report()
            print(f"✅ System report generated:")
            print(f"   - Memory usage: {report['resource_usage']['memory_mb']} MB")
            print(f"   - CPU usage: {report['resource_usage']['cpu_percent']}%")
            print(f"   - Python files: {report['file_counts']['python_files']}")
            print(f"   - Engines found: {report['module_status']['engines_found']}")
            
        elif args.command == 'monitor':
            results = await maintenance.monitor_system(args.duration)
            summary = results['summary']
            print(f"✅ Monitoring completed ({args.duration}s):")
            print(f"   - Average memory: {summary['avg_memory_mb']} MB")
            print(f"   - Peak memory: {summary['max_memory_mb']} MB")
            print(f"   - Average CPU: {summary['avg_cpu_percent']}%")
            print(f"   - Samples collected: {summary['samples_collected']}")
            
        elif args.command == 'list-backups':
            backups = maintenance.list_backups()
            if backups:
                print("📦 Available backups:")
                for backup in backups:
                    print(f"   • {backup['filename']} ({backup['size_mb']} MB) - {backup['created']}")
            else:
                print("No backups found")
                
        elif args.command == 'restore':
            success = await maintenance.restore_backup(args.backup, args.target)
            if success:
                print(f"✅ Backup restored successfully")
            else:
                print(f"❌ Backup restoration failed")
    
    # Run the async command
    try:
        asyncio.run(run_command())
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
