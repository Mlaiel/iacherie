#!/usr/bin/env python3
"""
System Cache Cleaner - Ainflue Platform
Author: Fahed Mlaiel (mlaiel@live.de)
Role: DevOps Engineer  
Purpose: Enterprise cache management and cleanup automation
"""

import asyncio
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple
import psutil
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CacheCleaner:
    """Enterprise cache cleaning system with smart cleanup policies"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path("/home/runner/work/Ainfluencer/Ainfluencer")
        self.cache_dirs = self._identify_cache_directories()
        self.stats = {
            "files_removed": 0,
            "directories_removed": 0,
            "space_freed_mb": 0,
            "errors": 0
        }
        
    def _identify_cache_directories(self) -> Dict[str, List[Path]]:
        """Identify all cache directories in the project"""
        cache_patterns = {
            "python": [
                "__pycache__",
                ".pytest_cache", 
                ".mypy_cache",
                ".tox",
                "*.egg-info",
                "build",
                "dist"
            ],
            "nodejs": [
                "node_modules/.cache",
                ".next",
                ".nuxt",
                "coverage",
                ".jest-cache"
            ],
            "system": [
                ".cache",
                "tmp",
                "temp",
                ".tmp"
            ],
            "docker": [
                ".docker",
                "docker-cache"
            ],
            "ml": [
                ".wandb",
                "mlruns",
                "tensorboard_logs",
                "checkpoints/.cache"
            ]
        }
        
        found_caches = {category: [] for category in cache_patterns}
        
        for category, patterns in cache_patterns.items():
            for pattern in patterns:
                # Find all matching directories
                if "*" in pattern:
                    # Handle glob patterns
                    matches = list(self.project_root.rglob(pattern))
                else:
                    # Handle exact directory names
                    matches = list(self.project_root.rglob(pattern))
                
                for match in matches:
                    if match.is_dir():
                        found_caches[category].append(match)
                        
        return found_caches
    
    async def get_cache_size(self, cache_dir: Path) -> int:
        """Get total size of cache directory in bytes"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(cache_dir):
                for filename in filenames:
                    file_path = Path(dirpath) / filename
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, PermissionError):
                        continue
            return total_size
        except Exception as e:
            logger.error(f"Error calculating size for {cache_dir}: {e}")
            return 0
    
    async def analyze_caches(self) -> Dict[str, Dict]:
        """Analyze all cache directories and their sizes"""
        analysis = {}
        total_cache_size = 0
        
        for category, cache_dirs in self.cache_dirs.items():
            category_size = 0
            category_info = {
                "directories": [],
                "total_size_mb": 0,
                "count": len(cache_dirs)
            }
            
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    size_bytes = await self.get_cache_size(cache_dir)
                    size_mb = size_bytes / (1024 * 1024)
                    
                    category_info["directories"].append({
                        "path": str(cache_dir),
                        "size_mb": round(size_mb, 2),
                        "last_modified": cache_dir.stat().st_mtime
                    })
                    
                    category_size += size_bytes
                    
            category_info["total_size_mb"] = round(category_size / (1024 * 1024), 2)
            analysis[category] = category_info
            total_cache_size += category_size
            
        analysis["total_cache_size_mb"] = round(total_cache_size / (1024 * 1024), 2)
        return analysis
    
    async def clean_python_caches(self, older_than_days: int = 7) -> Dict:
        """Clean Python-specific cache files"""
        cleaned = {"files": 0, "directories": 0, "size_mb": 0}
        
        for cache_dir in self.cache_dirs["python"]:
            if cache_dir.exists():
                try:
                    # Check if cache is old enough
                    cache_age = time.time() - cache_dir.stat().st_mtime
                    if cache_age > (older_than_days * 24 * 3600):
                        size_before = await self.get_cache_size(cache_dir)
                        
                        if cache_dir.name == "__pycache__":
                            # Clean .pyc files only
                            for pyc_file in cache_dir.rglob("*.pyc"):
                                pyc_file.unlink()
                                cleaned["files"] += 1
                                
                            # Remove empty __pycache__ directories  
                            try:
                                if not list(cache_dir.iterdir()):
                                    shutil.rmtree(cache_dir)
                                    cleaned["directories"] += 1
                            except OSError:
                                pass
                        else:
                            # Remove entire directory
                            shutil.rmtree(cache_dir)
                            cleaned["directories"] += 1
                            
                        cleaned["size_mb"] += size_before / (1024 * 1024)
                        
                except Exception as e:
                    logger.error(f"Error cleaning {cache_dir}: {e}")
                    self.stats["errors"] += 1
                    
        return cleaned
    
    async def clean_nodejs_caches(self, preserve_node_modules: bool = True) -> Dict:
        """Clean Node.js cache directories"""
        cleaned = {"files": 0, "directories": 0, "size_mb": 0}
        
        for cache_dir in self.cache_dirs["nodejs"]:
            if cache_dir.exists():
                try:
                    # Skip node_modules unless explicitly allowed
                    if preserve_node_modules and "node_modules" in str(cache_dir):
                        continue
                        
                    size_before = await self.get_cache_size(cache_dir)
                    
                    if cache_dir.name in [".next", ".nuxt", ".jest-cache"]:
                        # Safe to remove completely
                        shutil.rmtree(cache_dir)
                        cleaned["directories"] += 1
                        cleaned["size_mb"] += size_before / (1024 * 1024)
                        
                except Exception as e:
                    logger.error(f"Error cleaning {cache_dir}: {e}")
                    self.stats["errors"] += 1
                    
        return cleaned
    
    async def clean_ml_caches(self, preserve_checkpoints: bool = True) -> Dict:
        """Clean ML/AI cache directories"""
        cleaned = {"files": 0, "directories": 0, "size_mb": 0}
        
        for cache_dir in self.cache_dirs["ml"]:
            if cache_dir.exists():
                try:
                    # Be careful with ML caches - they might contain valuable data
                    if preserve_checkpoints and "checkpoints" in str(cache_dir):
                        # Only clean cache subdirectories, not model files
                        cache_subdir = cache_dir / ".cache"
                        if cache_subdir.exists():
                            size_before = await self.get_cache_size(cache_subdir)
                            shutil.rmtree(cache_subdir)
                            cleaned["directories"] += 1
                            cleaned["size_mb"] += size_before / (1024 * 1024)
                    else:
                        # Safe to clean wandb and tensorboard logs
                        if cache_dir.name in [".wandb", "tensorboard_logs"]:
                            # Keep recent logs (last 30 days)
                            cache_age = time.time() - cache_dir.stat().st_mtime
                            if cache_age > (30 * 24 * 3600):
                                size_before = await self.get_cache_size(cache_dir)
                                shutil.rmtree(cache_dir)
                                cleaned["directories"] += 1
                                cleaned["size_mb"] += size_before / (1024 * 1024)
                                
                except Exception as e:
                    logger.error(f"Error cleaning {cache_dir}: {e}")
                    self.stats["errors"] += 1
                    
        return cleaned
    
    async def clean_system_temps(self) -> Dict:
        """Clean system temporary directories"""
        cleaned = {"files": 0, "directories": 0, "size_mb": 0}
        
        # Clean system temp directory
        temp_dir = Path(tempfile.gettempdir())
        
        try:
            for item in temp_dir.iterdir():
                try:
                    # Only clean files/dirs older than 24 hours
                    item_age = time.time() - item.stat().st_mtime
                    if item_age > (24 * 3600):
                        if item.is_file():
                            size_mb = item.stat().st_size / (1024 * 1024)
                            item.unlink()
                            cleaned["files"] += 1
                            cleaned["size_mb"] += size_mb
                        elif item.is_dir():
                            size_before = await self.get_cache_size(item)
                            shutil.rmtree(item)
                            cleaned["directories"] += 1
                            cleaned["size_mb"] += size_before / (1024 * 1024)
                            
                except (PermissionError, OSError) as e:
                    # Skip files that can't be deleted (in use, etc.)
                    continue
                    
        except Exception as e:
            logger.error(f"Error cleaning system temp: {e}")
            self.stats["errors"] += 1
            
        return cleaned
    
    async def get_disk_usage(self) -> Dict:
        """Get current disk usage statistics"""
        try:
            usage = psutil.disk_usage(str(self.project_root))
            return {
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "usage_percent": round((usage.used / usage.total) * 100, 2)
            }
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {}
    
    async def comprehensive_cleanup(self, 
                                  clean_python: bool = True,
                                  clean_nodejs: bool = True, 
                                  clean_ml: bool = False,
                                  clean_system: bool = True,
                                  older_than_days: int = 7) -> Dict:
        """Perform comprehensive cache cleanup"""
        
        print("🧹 Starting comprehensive cache cleanup...")
        
        # Get initial disk usage
        disk_before = await self.get_disk_usage()
        
        cleanup_results = {
            "disk_before": disk_before,
            "cleaned_categories": {},
            "total_cleaned": {"files": 0, "directories": 0, "size_mb": 0},
            "errors": 0
        }
        
        # Clean Python caches
        if clean_python:
            print("  🐍 Cleaning Python caches...")
            python_cleaned = await self.clean_python_caches(older_than_days)
            cleanup_results["cleaned_categories"]["python"] = python_cleaned
            
        # Clean Node.js caches  
        if clean_nodejs:
            print("  📦 Cleaning Node.js caches...")
            nodejs_cleaned = await self.clean_nodejs_caches()
            cleanup_results["cleaned_categories"]["nodejs"] = nodejs_cleaned
            
        # Clean ML caches
        if clean_ml:
            print("  🤖 Cleaning ML caches...")
            ml_cleaned = await self.clean_ml_caches()
            cleanup_results["cleaned_categories"]["ml"] = ml_cleaned
            
        # Clean system temps
        if clean_system:
            print("  🗑️ Cleaning system temporary files...")
            system_cleaned = await self.clean_system_temps()
            cleanup_results["cleaned_categories"]["system"] = system_cleaned
            
        # Calculate totals
        for category_result in cleanup_results["cleaned_categories"].values():
            cleanup_results["total_cleaned"]["files"] += category_result["files"]
            cleanup_results["total_cleaned"]["directories"] += category_result["directories"]  
            cleanup_results["total_cleaned"]["size_mb"] += category_result["size_mb"]
            
        # Get final disk usage
        cleanup_results["disk_after"] = await self.get_disk_usage()
        cleanup_results["errors"] = self.stats["errors"]
        
        return cleanup_results

async def main():
    """Main cache cleaner execution"""
    cleaner = CacheCleaner()
    
    print("🧹 Cache Cleaner - Ainflue Platform")
    print("=" * 40)
    
    # Analyze current cache state
    print("📊 Analyzing cache directories...")
    analysis = await cleaner.analyze_caches()
    
    print(f"\n📋 Cache Analysis:")
    for category, info in analysis.items():
        if category != "total_cache_size_mb":
            print(f"   {category}: {info['count']} dirs, {info['total_size_mb']} MB")
    
    print(f"   Total cache size: {analysis['total_cache_size_mb']} MB")
    
    # Perform cleanup
    print("\n🧹 Performing cleanup...")
    results = await cleaner.comprehensive_cleanup()
    
    print(f"\n✅ Cleanup completed!")
    print(f"   Files removed: {results['total_cleaned']['files']}")
    print(f"   Directories removed: {results['total_cleaned']['directories']}")
    print(f"   Space freed: {results['total_cleaned']['size_mb']:.2f} MB")
    
    if results["errors"] > 0:
        print(f"   ⚠️ Errors encountered: {results['errors']}")
    
    # Show disk usage improvement
    if results.get("disk_before") and results.get("disk_after"):
        before = results["disk_before"]["usage_percent"]
        after = results["disk_after"]["usage_percent"]
        improvement = before - after
        print(f"   💾 Disk usage: {before:.1f}% → {after:.1f}% (-{improvement:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main())