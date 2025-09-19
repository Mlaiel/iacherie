#!/usr/bin/env python3
"""
Log Rotator & Archival System - Ainflue Platform
Author: Fahed Mlaiel (mlaiel@live.de)  
Role: DevOps Engineer
Purpose: Enterprise log management, rotation and archival automation
"""

import asyncio
import gzip
import logging
import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tarfile
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogRotator:
    """Enterprise log rotation and archival system"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path("/home/runner/work/Ainfluencer/Ainfluencer")
        self.log_dirs = self._identify_log_directories()
        self.archive_dir = self.project_root / "logs" / "archives"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Default rotation policies
        self.rotation_policies = {
            "application": {"max_size_mb": 100, "max_age_days": 30, "keep_archives": 12},
            "access": {"max_size_mb": 500, "max_age_days": 7, "keep_archives": 24}, 
            "error": {"max_size_mb": 50, "max_age_days": 90, "keep_archives": 36},
            "debug": {"max_size_mb": 200, "max_age_days": 3, "keep_archives": 6},
            "audit": {"max_size_mb": 1000, "max_age_days": 365, "keep_archives": 60},
            "security": {"max_size_mb": 100, "max_age_days": 180, "keep_archives": 48}
        }
        
        self.stats = {
            "files_rotated": 0,
            "files_archived": 0, 
            "space_freed_mb": 0,
            "archives_created": 0,
            "errors": 0
        }
    
    def _identify_log_directories(self) -> Dict[str, List[Path]]:
        """Identify all log directories and files in the project"""
        log_patterns = {
            "application": [
                "logs/*.log",
                "logs/app/*.log", 
                "logs/application/*.log",
                "*.log"
            ],
            "access": [
                "logs/access/*.log",
                "logs/nginx/*.log",
                "access.log*"
            ],
            "error": [
                "logs/error/*.log",
                "logs/errors/*.log", 
                "error.log*"
            ],
            "debug": [
                "logs/debug/*.log",
                "debug.log*"
            ],
            "audit": [
                "logs/audit/*.log",
                "audit.log*"
            ],
            "security": [
                "logs/security/*.log",
                "security.log*"
            ],
            "ml": [
                "logs/ml/*.log",
                "logs/training/*.log",
                "mlruns/*/meta.yaml",
                "tensorboard_logs/*"
            ],
            "docker": [
                "logs/docker/*.log",
                "logs/containers/*.log"
            ]
        }
        
        found_logs = {category: [] for category in log_patterns}
        
        for category, patterns in log_patterns.items():
            for pattern in patterns:
                matches = list(self.project_root.rglob(pattern))
                for match in matches:
                    if match.is_file() and match.suffix in ['.log', '.txt', '.out', '']:
                        found_logs[category].append(match)
                        
        return found_logs
    
    async def get_file_size_mb(self, file_path: Path) -> float:
        """Get file size in megabytes"""
        try:
            return file_path.stat().st_size / (1024 * 1024)
        except OSError:
            return 0.0
    
    async def get_file_age_days(self, file_path: Path) -> float:
        """Get file age in days"""
        try:
            mtime = file_path.stat().st_mtime
            age_seconds = time.time() - mtime
            return age_seconds / (24 * 3600)
        except OSError:
            return 0.0
    
    async def compress_log_file(self, log_file: Path, compressed_path: Path) -> bool:
        """Compress log file using gzip"""
        try:
            with open(log_file, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Verify compression
            if compressed_path.exists() and compressed_path.stat().st_size > 0:
                return True
            else:
                logger.error(f"Compression verification failed for {log_file}")
                return False
                
        except Exception as e:
            logger.error(f"Compression failed for {log_file}: {e}")
            return False
    
    async def rotate_log_file(self, log_file: Path, category: str) -> bool:
        """Rotate a single log file"""
        try:
            policy = self.rotation_policies.get(category, self.rotation_policies["application"])
            
            file_size_mb = await self.get_file_size_mb(log_file)
            file_age_days = await self.get_file_age_days(log_file)
            
            # Check if rotation is needed
            needs_rotation = (
                file_size_mb > policy["max_size_mb"] or 
                file_age_days > policy["max_age_days"]
            )
            
            if not needs_rotation:
                return False
            
            # Create archive filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{log_file.stem}_{timestamp}.gz"
            archive_path = self.archive_dir / category / archive_name
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Compress and archive
            if await self.compress_log_file(log_file, archive_path):
                # Truncate original log file (keep it for continued logging)
                with open(log_file, 'w') as f:
                    f.write(f"# Log rotated at {datetime.now().isoformat()}\n")
                
                self.stats["files_rotated"] += 1
                self.stats["space_freed_mb"] += file_size_mb
                self.stats["archives_created"] += 1
                
                logger.info(f"Rotated {log_file} -> {archive_path}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Rotation failed for {log_file}: {e}")
            self.stats["errors"] += 1
            return False
    
    async def create_daily_archive(self, category: str, date: datetime) -> bool:
        """Create daily archive of all rotated logs for a category"""
        try:
            category_archive_dir = self.archive_dir / category
            if not category_archive_dir.exists():
                return False
            
            # Find all compressed logs for the date
            date_str = date.strftime("%Y%m%d")
            compressed_logs = list(category_archive_dir.glob(f"*{date_str}_*.gz"))
            
            if not compressed_logs:
                return False
            
            # Create tar archive
            daily_archive = category_archive_dir / f"{category}_{date_str}.tar.gz"
            
            with tarfile.open(daily_archive, 'w:gz') as tar:
                for log_file in compressed_logs:
                    tar.add(log_file, arcname=log_file.name)
            
            # Remove individual compressed files after archiving
            for log_file in compressed_logs:
                log_file.unlink()
            
            self.stats["files_archived"] += len(compressed_logs)
            logger.info(f"Created daily archive: {daily_archive}")
            return True
            
        except Exception as e:
            logger.error(f"Daily archive creation failed for {category}: {e}")
            self.stats["errors"] += 1
            return False
    
    async def cleanup_old_archives(self, category: str) -> int:
        """Clean up old archives based on retention policy"""
        try:
            policy = self.rotation_policies.get(category, self.rotation_policies["application"])
            category_archive_dir = self.archive_dir / category
            
            if not category_archive_dir.exists():
                return 0
            
            # Get all archive files
            archives = list(category_archive_dir.glob("*.tar.gz"))
            archives.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the specified number of archives
            keep_count = policy["keep_archives"]
            removed_count = 0
            
            for archive in archives[keep_count:]:
                try:
                    archive_size_mb = await self.get_file_size_mb(archive)
                    archive.unlink()
                    removed_count += 1
                    self.stats["space_freed_mb"] += archive_size_mb
                    logger.info(f"Removed old archive: {archive}")
                except OSError as e:
                    logger.error(f"Failed to remove archive {archive}: {e}")
                    
            return removed_count
            
        except Exception as e:
            logger.error(f"Archive cleanup failed for {category}: {e}")
            self.stats["errors"] += 1
            return 0
    
    async def analyze_logs(self) -> Dict:
        """Analyze current log state and provide insights"""
        analysis = {
            "categories": {},
            "total_log_size_mb": 0,
            "recommendations": []
        }
        
        for category, log_files in self.log_dirs.items():
            category_info = {
                "file_count": len(log_files),
                "total_size_mb": 0,
                "files_needing_rotation": 0,
                "largest_file": None,
                "oldest_file": None
            }
            
            largest_size = 0
            oldest_age = 0
            
            for log_file in log_files:
                if log_file.exists():
                    size_mb = await self.get_file_size_mb(log_file)
                    age_days = await self.get_file_age_days(log_file)
                    
                    category_info["total_size_mb"] += size_mb
                    
                    # Check if needs rotation
                    policy = self.rotation_policies.get(category, self.rotation_policies["application"])
                    if size_mb > policy["max_size_mb"] or age_days > policy["max_age_days"]:
                        category_info["files_needing_rotation"] += 1
                    
                    # Track largest and oldest
                    if size_mb > largest_size:
                        largest_size = size_mb
                        category_info["largest_file"] = {
                            "path": str(log_file),
                            "size_mb": round(size_mb, 2)
                        }
                    
                    if age_days > oldest_age:
                        oldest_age = age_days
                        category_info["oldest_file"] = {
                            "path": str(log_file), 
                            "age_days": round(age_days, 1)
                        }
            
            category_info["total_size_mb"] = round(category_info["total_size_mb"], 2)
            analysis["categories"][category] = category_info
            analysis["total_log_size_mb"] += category_info["total_size_mb"]
            
            # Generate recommendations
            if category_info["files_needing_rotation"] > 0:
                analysis["recommendations"].append({
                    "type": "rotation_needed",
                    "category": category,
                    "message": f"{category_info['files_needing_rotation']} files need rotation",
                    "priority": "medium"
                })
        
        analysis["total_log_size_mb"] = round(analysis["total_log_size_mb"], 2)
        
        # Global recommendations
        if analysis["total_log_size_mb"] > 1000:  # > 1GB
            analysis["recommendations"].append({
                "type": "disk_space",
                "message": f"High log disk usage: {analysis['total_log_size_mb']} MB",
                "priority": "high"
            })
        
        return analysis
    
    async def comprehensive_rotation(self, categories: List[str] = None) -> Dict:
        """Perform comprehensive log rotation for specified categories"""
        if categories is None:
            categories = list(self.log_dirs.keys())
        
        results = {
            "rotated_by_category": {},
            "archives_created": 0,
            "old_archives_cleaned": 0,
            "total_space_freed_mb": 0,
            "errors": 0
        }
        
        for category in categories:
            if category not in self.log_dirs:
                continue
                
            print(f"  📋 Processing {category} logs...")
            
            category_results = {
                "files_rotated": 0,
                "files_processed": 0
            }
            
            # Rotate individual files
            for log_file in self.log_dirs[category]:
                if log_file.exists():
                    category_results["files_processed"] += 1
                    if await self.rotate_log_file(log_file, category):
                        category_results["files_rotated"] += 1
            
            # Create daily archives for yesterday
            yesterday = datetime.now() - timedelta(days=1)
            if await self.create_daily_archive(category, yesterday):
                results["archives_created"] += 1
            
            # Cleanup old archives
            cleaned = await self.cleanup_old_archives(category)
            results["old_archives_cleaned"] += cleaned
            
            results["rotated_by_category"][category] = category_results
        
        results["total_space_freed_mb"] = round(self.stats["space_freed_mb"], 2)
        results["errors"] = self.stats["errors"]
        
        return results

async def main():
    """Main log rotator execution"""
    rotator = LogRotator()
    
    print("📄 Log Rotator - Ainflue Platform")
    print("=" * 35)
    
    # Analyze current log state
    print("📊 Analyzing log files...")
    analysis = await rotator.analyze_logs()
    
    print(f"\n📋 Log Analysis:")
    for category, info in analysis["categories"].items():
        if info["file_count"] > 0:
            print(f"   {category}: {info['file_count']} files, {info['total_size_mb']} MB")
            if info["files_needing_rotation"] > 0:
                print(f"      ⚠️ {info['files_needing_rotation']} files need rotation")
    
    print(f"   Total log size: {analysis['total_log_size_mb']} MB")
    
    # Show recommendations
    if analysis["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in analysis["recommendations"]:
            priority_icon = "🔴" if rec["priority"] == "high" else "🟡"
            print(f"   {priority_icon} {rec['message']}")
    
    # Perform rotation
    print("\n📄 Performing log rotation...")
    results = await rotator.comprehensive_rotation()
    
    print(f"\n✅ Log rotation completed!")
    print(f"   Files rotated: {rotator.stats['files_rotated']}")
    print(f"   Archives created: {results['archives_created']}")
    print(f"   Old archives cleaned: {results['old_archives_cleaned']}")
    print(f"   Space freed: {results['total_space_freed_mb']} MB")
    
    if results["errors"] > 0:
        print(f"   ⚠️ Errors encountered: {results['errors']}")
    
    # Save rotation report
    report = {
        "timestamp": time.time(),
        "analysis": analysis,
        "rotation_results": results,
        "stats": rotator.stats
    }
    
    reports_dir = rotator.project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / f"log_rotation_{int(time.time())}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"   💾 Report saved to: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())