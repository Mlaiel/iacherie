"""Health checking system for monitoring service availability."""import asyncio
import time
import psutil
from typing import Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    def __init__(self):
        self.checks = {}
        self.check_results = {}

    def register_check(self, name: str, check_func: Callable, critical: bool = True, timeout: int = 5):
        """Register a health check function."""        self.checks[name] = {
            "function": check_func,
            "critical": critical,
            "timeout": timeout,
            "last_result": None,
            "last_check": None
        }

    async def run_all_checks(self) -> Dict:
        """Run all registered health checks."""        results = {}
        overall_status = HealthStatus.HEALTHY
        
        for name, check_config in self.checks.items():
            try:
                start_time = time.time()
                
                # Run check with timeout
                result = await asyncio.wait_for(
                    self._run_check(check_config["function"]),
                    timeout=check_config["timeout"]
                )
                
                check_duration = (time.time() - start_time) * 1000  # ms
                
                check_result = {
                    "status": HealthStatus.HEALTHY.value,
                    "response_time_ms": round(check_duration, 2),
                    "details": result,
                    "timestamp": datetime.utcnow().isoformat(),
                    "critical": check_config["critical"]
                }
                
            except asyncio.TimeoutError:
                check_result = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "response_time_ms": check_config["timeout"] * 1000,
                    "error": "Health check timeout",
                    "timestamp": datetime.utcnow().isoformat(),
                    "critical": check_config["critical"]
                }
                if check_config["critical"]:
                    overall_status = HealthStatus.UNHEALTHY
                elif overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                    
            except Exception as e:
                check_result = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                    "critical": check_config["critical"]
                }
                if check_config["critical"]:
                    overall_status = HealthStatus.UNHEALTHY
                elif overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            
            results[name] = check_result
            self.checks[name]["last_result"] = check_result
            self.checks[name]["last_check"] = datetime.utcnow()
        
        return {
            "overall_status": overall_status.value,
            "checks": results,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": self._generate_summary(results)
        }

    def get_system_health(self) -> Dict:
        """Get basic system health metrics."""        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine health based on thresholds
            status = HealthStatus.HEALTHY
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = HealthStatus.UNHEALTHY
            elif cpu_percent > 80 or memory.percent > 80 or disk.percent > 80:
                status = HealthStatus.DEGRADED
            
            return {
                "status": status.value,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free // (1024 * 1024 * 1024),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "error": f"Could not get system metrics: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_database_health(self) -> Dict:
        """Check database connectivity and performance."""        try:
            # Mock database check - in reality would use actual DB connection
            start_time = time.time()
            
            # Simulate database query
            await asyncio.sleep(0.01)  # Simulate query time
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "connected": True,
                "response_time_ms": round(response_time, 2),
                "active_connections": 5,  # Mock value
                "max_connections": 100,
                "database_size_mb": 1250  # Mock value
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }

    async def check_redis_health(self) -> Dict:
        """Check Redis connectivity and performance."""        try:
            # Mock Redis check
            start_time = time.time()
            await asyncio.sleep(0.005)  # Simulate ping
            response_time = (time.time() - start_time) * 1000
            
            return {
                "connected": True,
                "response_time_ms": round(response_time, 2),
                "memory_usage_mb": 64,  # Mock value
                "connected_clients": 12,  # Mock value
                "keyspace_hits": 1500,
                "keyspace_misses": 150
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }

    async def check_storage_health(self) -> Dict:
        """Check file storage health."""        try:
            import os
            storage_path = "/data/storage"
            
            if os.path.exists(storage_path):
                # Check if we can write to storage
                test_file = os.path.join(storage_path, ".health_check")
                with open(test_file, "w") as f:
                    f.write("health_check")
                os.remove(test_file)
                
                # Get storage statistics
                stat = os.statvfs(storage_path)
                free_space = stat.f_bavail * stat.f_frsize
                total_space = stat.f_blocks * stat.f_frsize
                used_percent = ((total_space - free_space) / total_space) * 100
                
                return {
                    "accessible": True,
                    "writable": True,
                    "free_space_gb": round(free_space / (1024**3), 2),
                    "used_percent": round(used_percent, 1),
                    "path": storage_path
                }
            else:
                os.makedirs(storage_path, exist_ok=True)
                return {
                    "accessible": True,
                    "writable": True,
                    "path": storage_path,
                    "created": True
                }
                
        except Exception as e:
            return {
                "accessible": False,
                "error": str(e)
            }

    async def check_external_apis(self) -> Dict:
        """Check external API dependencies."""        # Mock external API checks
        apis = {
            "blockchain_provider": {"status": "healthy", "response_time_ms": 250},
            "storage_provider": {"status": "healthy", "response_time_ms": 150},
            "ml_service": {"status": "healthy", "response_time_ms": 400}
        }
        
        all_healthy = all(api["status"] == "healthy" for api in apis.values())
        
        return {
            "all_apis_healthy": all_healthy,
            "individual_checks": apis,
            "total_apis": len(apis)
        }

    def setup_default_checks(self):
        """Setup default health checks for the system."""        self.register_check("database", self.check_database_health, critical=True)
        self.register_check("redis", self.check_redis_health, critical=False)
        self.register_check("storage", self.check_storage_health, critical=True)
        self.register_check("external_apis", self.check_external_apis, critical=False)

    async def _run_check(self, check_func: Callable) -> Dict:
        """Run a single health check function."""        if asyncio.iscoroutinefunction(check_func):
            return await check_func()
        else:
            return check_func()

    def _generate_summary(self, results: Dict) -> Dict:
        """Generate summary statistics from check results."""        total_checks = len(results)
        healthy_checks = sum(1 for r in results.values() if r["status"] == HealthStatus.HEALTHY.value)
        critical_failures = sum(1 for r in results.values() if r["status"] != HealthStatus.HEALTHY.value and r["critical"])
        
        avg_response_time = 0
        if results:
            avg_response_time = sum(r.get("response_time_ms", 0) for r in results.values()) / total_checks
        
        return {
            "total_checks": total_checks,
            "healthy_checks": healthy_checks,
            "failed_checks": total_checks - healthy_checks,
            "critical_failures": critical_failures,
            "success_rate": round((healthy_checks / total_checks) * 100, 1) if total_checks > 0 else 0,
            "avg_response_time_ms": round(avg_response_time, 2)
        }
