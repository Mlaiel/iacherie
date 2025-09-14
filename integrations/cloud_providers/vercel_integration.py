"""
AINFLUE INTEGRATIONS - VERCEL DEPLOYMENT PLATFORM
================================================

Enterprise Vercel integration for creator economy platform deployment.
Combines multiple expert roles for comprehensive serverless deployment management.

Author: Fahed Mlaiel <mlaiel@live.de>
Platform: Ainflue - IA Influencer Agent + Content Protection Platform
Architecture Level: Level 3 (integrations/cloud_providers)

Expert Roles Applied:
- Lead Dev IA: AI-powered deployment optimization, intelligent scaling decisions
- Backend Senior: Robust deployment architecture, enterprise deployment patterns
- ML Engineer: Performance analytics, predictive scaling, optimization algorithms
- DBA: Deployment metadata management, performance tracking, audit trails
- Security: Secure deployment practices, environment protection, secret management
- Microservices: Multi-service deployment orchestration, edge function management
- Audio Engineer: Media optimization for edge delivery, CDN configuration
- DevOps: Automated CI/CD, monitoring, deployment automation, rollback strategies
- IA Prompt Engineer: AI-driven deployment recommendations, optimization insights

Business Logic Integration:
Creator → Content Deploy → Edge Optimization → Global Distribution → Performance Monitoring → Revenue Tracking
"""

import asyncio
import base64
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import aiofiles
from pydantic import BaseModel, Field, validator
import tarfile
import zipfile

# Security and Authentication
import hmac
import hashlib
import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Monitoring and Performance
import psutil
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics for DevOps monitoring
DEPLOYMENT_COUNTER = Counter('vercel_deployments_total', 'Total Vercel deployments', ['status', 'type'])
DEPLOYMENT_DURATION = Histogram('vercel_deployment_duration_seconds', 'Deployment duration')
ACTIVE_DEPLOYMENTS = Gauge('vercel_active_deployments', 'Active deployments')
ERROR_COUNTER = Counter('vercel_errors_total', 'Vercel API errors', ['error_type'])
BUILD_TIME_HISTOGRAM = Histogram('vercel_build_time_seconds', 'Build time distribution')

class DeploymentStatus(Enum):
    """Vercel deployment status"""
    QUEUED = "QUEUED"
    BUILDING = "BUILDING" 
    DEPLOYING = "DEPLOYING"
    READY = "READY"
    ERROR = "ERROR"
    CANCELED = "CANCELED"

class ProjectType(Enum):
    """Project framework types"""
    NEXTJS = "nextjs"
    REACT = "react"
    VUE = "vue"
    NUXT = "nuxt"
    STATIC = "static"
    NODEJS = "nodejs"
    PYTHON = "python"
    UNKNOWN = "unknown"

class Environment(Enum):
    """Deployment environments"""
    PRODUCTION = "production"
    PREVIEW = "preview"
    DEVELOPMENT = "development"

@dataclass
class VercelDeployment:
    """Vercel deployment information"""
    deployment_id: str
    project_id: str
    creator_id: str
    name: str
    url: str
    status: DeploymentStatus
    environment: Environment
    framework: ProjectType
    created_at: datetime
    ready_at: Optional[datetime] = None
    source: Optional[Dict] = None
    build_output: Optional[List[str]] = None
    functions: Optional[List[Dict]] = None
    routes: Optional[List[Dict]] = None
    meta: Optional[Dict] = None
    
@dataclass 
class VercelProject:
    """Vercel project information"""
    project_id: str
    name: str
    account_id: str
    creator_id: str
    framework: ProjectType
    root_directory: Optional[str]
    build_command: Optional[str]
    output_directory: Optional[str]
    install_command: Optional[str]
    dev_command: Optional[str]
    env_vars: Dict[str, str]
    domains: List[str]
    created_at: datetime
    updated_at: datetime

class VercelConfig(BaseModel):
    """Configuration for Vercel integration"""
    # API Configuration
    api_token: str = Field(..., description="Vercel API token")
    team_id: Optional[str] = Field(default=None, description="Vercel team ID")
    api_base_url: str = Field(default="https://api.vercel.com", description="Vercel API base URL")
    
    # Deployment Configuration
    default_framework: ProjectType = Field(default=ProjectType.NEXTJS, description="Default framework")
    auto_promote_production: bool = Field(default=False, description="Auto-promote to production")
    enable_analytics: bool = Field(default=True, description="Enable Vercel Analytics")
    
    # Build Configuration
    build_timeout: int = Field(default=900, description="Build timeout in seconds (15 minutes)")
    node_version: str = Field(default="18.x", description="Node.js version")
    max_build_size: int = Field(default=100 * 1024 * 1024, description="Maximum build size (100MB)")
    
    # Security Configuration
    enable_preview_protection: bool = Field(default=True, description="Enable preview protection")
    enable_edge_config: bool = Field(default=True, description="Enable Edge Config")
    webhook_secret: Optional[str] = Field(default=None, description="Webhook secret for validation")
    
    # Performance Configuration
    edge_functions_enabled: bool = Field(default=True, description="Enable Edge Functions")
    image_optimization: bool = Field(default=True, description="Enable image optimization")
    serverless_functions: bool = Field(default=True, description="Enable serverless functions")
    
    # Monitoring Configuration
    enable_logging: bool = Field(default=True, description="Enable deployment logging")
    log_retention_days: int = Field(default=30, description="Log retention period")
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    
    @validator('api_token')
    def validate_api_token(cls, v) -> None:
        if not v or len(v) < 10:
            raise ValueError("Valid Vercel API token required")
        return v

class VercelSecurityManager:
    """Security manager for Vercel deployments - Security Expert role"""
    
    def __init__(self, config -> None: VercelConfig) -> None:
        self.config = config
        
    def generate_deployment_signature(self, payload: str, secret: str) -> str:
        """Generate deployment signature for webhook validation"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Validate webhook signature from Vercel"""
        expected_signature = self.generate_deployment_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    def sanitize_environment_variables(self, env_vars: Dict[str, str]) -> Dict[str, str]:
        """Sanitize environment variables for security"""
        sanitized = {}
        
        # Remove sensitive keys
        sensitive_keys = ['password', 'secret', 'key', 'token', 'private']
        
        for key, value in env_vars.items():
            # Skip sensitive variables in logs
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def generate_secure_preview_password(self) -> str:
        """Generate secure password for preview deployments"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(16))
    
    def validate_deployment_security(self, deployment_config: Dict) -> Dict[str, Any]:
        """Validate deployment configuration for security"""
        security_check = {
            "secure": True,
            "warnings": [],
            "recommendations": []
        }
        
        # Check for exposed secrets
        env_vars = deployment_config.get("env", {})
        for key, value in env_vars.items():
            if any(secret in key.lower() for secret in ['password', 'secret', 'key']):
                if not value.startswith('$'):  # Not a reference
                    security_check["warnings"].append(f"Potential secret exposed in environment variable: {key}")
        
        # Check build commands for security
        build_command = deployment_config.get("build", {}).get("command", "")
        if "curl" in build_command or "wget" in build_command:
            security_check["warnings"].append("Build command contains network requests - review for security")
        
        # Security recommendations
        if not deployment_config.get("regions"):
            security_check["recommendations"].append("Consider specifying deployment regions for better control")
        
        if not deployment_config.get("functions", {}).get("memory"):
            security_check["recommendations"].append("Consider setting memory limits for functions")
        
        return security_check

class VercelMLOptimizer:
    """ML-powered deployment optimization - ML Engineer + Lead Dev IA roles"""
    
    def __init__(self, config -> None: VercelConfig) -> None:
        self.config = config
        self.performance_history = []
        
    async def optimize_deployment_config(self, project_type: ProjectType, historical_data: List[Dict]) -> Dict[str, Any]:
        """AI-powered deployment configuration optimization"""
        optimization = {
            "build_config": {},
            "performance_config": {},
            "scaling_config": {},
            "recommendations": []
        }
        
        try:
            # Analyze historical performance
            if historical_data:
                performance_analysis = self._analyze_performance_patterns(historical_data)
                optimization.update(performance_analysis)
            
            # Framework-specific optimizations
            framework_optimizations = self._get_framework_optimizations(project_type)
            optimization["build_config"].update(framework_optimizations)
            
            # Predictive scaling recommendations
            scaling_recommendations = await self._predict_scaling_needs(historical_data)
            optimization["scaling_config"].update(scaling_recommendations)
            
            # Performance optimizations
            performance_optimizations = self._generate_performance_optimizations(project_type)
            optimization["performance_config"].update(performance_optimizations)
            
        except Exception as e:
            logger.error(f"Deployment optimization failed: {e}")
            optimization["error"] = str(e)
        
        return optimization
    
    def _analyze_performance_patterns(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Analyze performance patterns from historical deployments"""
        if not historical_data:
            return {}
        
        # Calculate performance metrics
        build_times = [d.get("build_time", 0) for d in historical_data if d.get("build_time")]
        deploy_times = [d.get("deploy_time", 0) for d in historical_data if d.get("deploy_time")]
        
        analysis = {
            "average_build_time": sum(build_times) / len(build_times) if build_times else 0,
            "average_deploy_time": sum(deploy_times) / len(deploy_times) if deploy_times else 0,
            "build_time_trend": self._calculate_trend(build_times),
            "success_rate": self._calculate_success_rate(historical_data)
        }
        
        # Generate insights
        recommendations = []
        if analysis["average_build_time"] > 300:  # 5 minutes
            recommendations.append("Consider optimizing build process - average build time is high")
        
        if analysis["success_rate"] < 0.95:
            recommendations.append("Deployment success rate is below 95% - review common failure patterns")
        
        analysis["recommendations"] = recommendations
        return analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for metrics"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        x = list(range(len(values)))
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x ** 2 == 0:
            return "stable"
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_success_rate(self, deployments: List[Dict]) -> float:
        """Calculate deployment success rate"""
        if not deployments:
            return 0.0
        
        successful = sum(1 for d in deployments if d.get("status") == "READY")
        return successful / len(deployments)
    
    def _get_framework_optimizations(self, project_type: ProjectType) -> Dict[str, Any]:
        """Get framework-specific optimizations"""
        optimizations = {
            ProjectType.NEXTJS: {
                "output": "standalone",
                "images": {"unoptimized": False},
                "experimental": {"esmExternals": True},
                "env": {"NEXT_TELEMETRY_DISABLED": "1"}
            },
            ProjectType.REACT: {
                "build": {"command": "npm run build"},
                "output_directory": "build",
                "node_version": "18.x"
            },
            ProjectType.VUE: {
                "build": {"command": "npm run build"},
                "output_directory": "dist",
                "node_version": "18.x"
            },
            ProjectType.STATIC: {
                "output_directory": ".",
                "build": {"command": "echo 'Static site - no build required'"}
            }
        }
        
        return optimizations.get(project_type, {})
    
    async def _predict_scaling_needs(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Predict scaling needs based on historical data"""
        scaling_config = {
            "regions": ["iad1", "sfo1"],  # Default regions
            "functions": {
                "memory": 1024,
                "maxDuration": 30
            },
            "edge_functions": {
                "regions": ["auto"]
            }
        }
        
        if historical_data:
            # Analyze traffic patterns
            avg_requests = sum(d.get("requests", 0) for d in historical_data) / len(historical_data)
            
            if avg_requests > 10000:  # High traffic
                scaling_config["regions"].extend(["lhr1", "hnd1"])  # Add more regions
                scaling_config["functions"]["memory"] = 2048
            
            # Analyze error rates
            error_rate = 1 - self._calculate_success_rate(historical_data)
            if error_rate > 0.1:  # High error rate
                scaling_config["functions"]["maxDuration"] = 60  # Increase timeout
        
        return scaling_config
    
    def _generate_performance_optimizations(self, project_type: ProjectType) -> Dict[str, Any]:
        """Generate performance optimization recommendations"""
        optimizations = {
            "caching": {
                "static_files": "max-age=31536000",
                "api_routes": "max-age=0, s-maxage=86400"
            },
            "compression": {
                "enabled": True,
                "algorithms": ["gzip", "br"]
            },
            "image_optimization": {
                "enabled": self.config.image_optimization,
                "formats": ["webp", "avif"],
                "quality": 85
            }
        }
        
        # Framework-specific performance optimizations
        if project_type == ProjectType.NEXTJS:
            optimizations["next_optimizations"] = {
                "swcMinify": True,
                "compiler": {"styledComponents": True},
                "experimental": {"optimizeCss": True}
            }
        
        return optimizations

class VercelAPIClient:
    """Vercel API client - Backend Senior role"""
    
    def __init__(self, config -> None: VercelConfig) -> None:
        self.config = config
        self.session = None
        
    async def __aenter__(self) -> None:
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_token}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()
    
    async def create_deployment(self, project_name: str, files: Dict[str, str], config: Dict = None) -> Dict[str, Any]:
        """Create a new deployment"""
        try:
            deployment_data = {
                "name": project_name,
                "files": files,
                "target": "production" if config and config.get("production") else "preview",
                "projectSettings": config or {}
            }
            
            if self.config.team_id:
                deployment_data["teamId"] = self.config.team_id
            
            async with self.session.post(
                f"{self.config.api_base_url}/v13/deployments",
                json=deployment_data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    DEPLOYMENT_COUNTER.labels(status="success", type="create").inc()
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Deployment creation failed: {response.status} - {error_text}")
                    ERROR_COUNTER.labels(error_type="create_deployment").inc()
                    return {"error": error_text, "status": response.status}
                    
        except Exception as e:
            logger.error(f"Deployment creation error: {e}")
            ERROR_COUNTER.labels(error_type="api_error").inc()
            return {"error": str(e)}
    
    async def get_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment information"""
        try:
            url = f"{self.config.api_base_url}/v13/deployments/{deployment_id}"
            if self.config.team_id:
                url += f"?teamId={self.config.team_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Get deployment failed: {response.status} - {error_text}")
                    return {"error": error_text, "status": response.status}
                    
        except Exception as e:
            logger.error(f"Get deployment error: {e}")
            return {"error": str(e)}
    
    async def list_deployments(self, project_id: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """List deployments"""
        try:
            url = f"{self.config.api_base_url}/v6/deployments?limit={limit}"
            if project_id:
                url += f"&projectId={project_id}"
            if self.config.team_id:
                url += f"&teamId={self.config.team_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"List deployments failed: {response.status} - {error_text}")
                    return {"error": error_text, "status": response.status}
                    
        except Exception as e:
            logger.error(f"List deployments error: {e}")
            return {"error": str(e)}
    
    async def create_project(self, name: str, framework: str = "nextjs") -> Dict[str, Any]:
        """Create a new project"""
        try:
            project_data = {
                "name": name,
                "framework": framework
            }
            
            if self.config.team_id:
                project_data["teamId"] = self.config.team_id
            
            async with self.session.post(
                f"{self.config.api_base_url}/v10/projects",
                json=project_data
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Project creation failed: {response.status} - {error_text}")
                    return {"error": error_text, "status": response.status}
                    
        except Exception as e:
            logger.error(f"Project creation error: {e}")
            return {"error": str(e)}
    
    async def update_project_settings(self, project_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update project settings"""
        try:
            url = f"{self.config.api_base_url}/v10/projects/{project_id}"
            if self.config.team_id:
                settings["teamId"] = self.config.team_id
            
            async with self.session.patch(url, json=settings) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Project update failed: {response.status} - {error_text}")
                    return {"error": error_text, "status": response.status}
                    
        except Exception as e:
            logger.error(f"Project update error: {e}")
            return {"error": str(e)}
    
    async def get_deployment_logs(self, deployment_id: str) -> List[str]:
        """Get deployment build logs"""
        try:
            url = f"{self.config.api_base_url}/v2/deployments/{deployment_id}/events"
            if self.config.team_id:
                url += f"?teamId={self.config.team_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    events = await response.json()
                    return [event.get("text", "") for event in events if event.get("text")]
                else:
                    logger.error(f"Get logs failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Get logs error: {e}")
            return []

class VercelFileManager:
    """File management for Vercel deployments - Backend Senior + DevOps roles"""
    
    def __init__(self, config -> None: VercelConfig) -> None:
        self.config = config
    
    async def prepare_deployment_files(self, source_path: str, framework: ProjectType) -> Dict[str, str]:
        """Prepare files for deployment"""
        files = {}
        
        try:
            source_path = Path(source_path)
            
            # Get file list based on framework
            file_patterns = self._get_framework_file_patterns(framework)
            
            for pattern in file_patterns:
                for file_path in source_path.rglob(pattern):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(source_path)
                        
                        # Read file content
                        if self._is_binary_file(file_path):
                            async with aiofiles.open(file_path, 'rb') as f:
                                content = await f.read()
                                files[str(relative_path)] = base64.b64encode(content).decode()
                        else:
                            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                                content = await f.read()
                                files[str(relative_path)] = content
            
            logger.info(f"Prepared {len(files)} files for deployment")
            return files
            
        except Exception as e:
            logger.error(f"File preparation failed: {e}")
            return {}
    
    def _get_framework_file_patterns(self, framework: ProjectType) -> List[str]:
        """Get file patterns for different frameworks"""
        patterns = {
            ProjectType.NEXTJS: [
                "*.json", "*.js", "*.jsx", "*.ts", "*.tsx", "*.css", "*.scss",
                "pages/**/*", "components/**/*", "public/**/*", "styles/**/*",
                ".env*", "next.config.js"
            ],
            ProjectType.REACT: [
                "*.json", "*.js", "*.jsx", "*.ts", "*.tsx", "*.css", "*.scss",
                "src/**/*", "public/**/*", "build/**/*"
            ],
            ProjectType.VUE: [
                "*.json", "*.js", "*.vue", "*.ts", "*.css", "*.scss",
                "src/**/*", "public/**/*", "dist/**/*"
            ],
            ProjectType.STATIC: [
                "*.html", "*.css", "*.js", "*.png", "*.jpg", "*.jpeg", "*.gif",
                "*.svg", "*.ico", "assets/**/*", "images/**/*"
            ]
        }
        
        return patterns.get(framework, ["*"])
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary"""
        binary_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.pdf',
            '.zip', '.tar', '.gz', '.mp4', '.mp3', '.avi', '.mov'
        }
        
        return file_path.suffix.lower() in binary_extensions
    
    async def create_build_archive(self, source_path: str, output_path: str) -> bool:
        """Create deployment archive"""
        try:
            with tarfile.open(output_path, 'w:gz') as tar:
                tar.add(source_path, arcname=os.path.basename(source_path))
            
            logger.info(f"Build archive created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Archive creation failed: {e}")
            return False

class VercelMonitor:
    """Monitoring and analytics for Vercel deployments - DevOps role"""
    
    def __init__(self, config -> None: VercelConfig) -> None:
        self.config = config
        
    async def monitor_deployment(self, deployment_id: str, api_client: VercelAPIClient) -> AsyncGenerator[Dict[str, Any], None]:
        """Monitor deployment progress"""
        try:
            max_attempts = 60  # 5 minutes with 5-second intervals
            attempt = 0
            
            while attempt < max_attempts:
                deployment_info = await api_client.get_deployment(deployment_id)
                
                if "error" in deployment_info:
                    yield {"status": "ERROR", "error": deployment_info["error"]}
                    break
                
                status = deployment_info.get("readyState", "UNKNOWN")
                yield {
                    "status": status,
                    "progress": (attempt / max_attempts) * 100,
                    "deployment": deployment_info
                }
                
                if status in ["READY", "ERROR", "CANCELED"]:
                    break
                
                await asyncio.sleep(5)
                attempt += 1
            
            if attempt >= max_attempts:
                yield {"status": "TIMEOUT", "error": "Deployment monitoring timeout"}
                
        except Exception as e:
            logger.error(f"Deployment monitoring failed: {e}")
            yield {"status": "ERROR", "error": str(e)}
    
    async def collect_deployment_metrics(self, deployment_id: str, api_client: VercelAPIClient) -> Dict[str, Any]:
        """Collect comprehensive deployment metrics"""
        metrics = {
            "deployment_id": deployment_id,
            "timestamp": datetime.utcnow().isoformat(),
            "build_metrics": {},
            "performance_metrics": {},
            "error_metrics": {}
        }
        
        try:
            # Get deployment info
            deployment_info = await api_client.get_deployment(deployment_id)
            
            if "error" not in deployment_info:
                # Build metrics
                created_at = deployment_info.get("createdAt")
                ready_at = deployment_info.get("readyAt")
                
                if created_at and ready_at:
                    created_time = datetime.fromtimestamp(created_at / 1000)
                    ready_time = datetime.fromtimestamp(ready_at / 1000)
                    build_duration = (ready_time - created_time).total_seconds()
                    
                    metrics["build_metrics"] = {
                        "build_duration": build_duration,
                        "created_at": created_time.isoformat(),
                        "ready_at": ready_time.isoformat()
                    }
                    
                    BUILD_TIME_HISTOGRAM.observe(build_duration)
                
                # Performance metrics
                metrics["performance_metrics"] = {
                    "functions_count": len(deployment_info.get("functions", [])),
                    "routes_count": len(deployment_info.get("routes", [])),
                    "file_count": len(deployment_info.get("files", []))
                }
                
                # Collect logs for error analysis
                logs = await api_client.get_deployment_logs(deployment_id)
                error_logs = [log for log in logs if "error" in log.lower() or "failed" in log.lower()]
                
                metrics["error_metrics"] = {
                    "error_count": len(error_logs),
                    "error_logs": error_logs[:10]  # Limit to first 10 errors
                }
        
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            metrics["collection_error"] = str(e)
        
        return metrics
    
    def generate_deployment_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive deployment report"""
        report = {
            "summary": {},
            "performance_analysis": {},
            "recommendations": [],
            "alerts": []
        }
        
        try:
            build_metrics = metrics.get("build_metrics", {})
            performance_metrics = metrics.get("performance_metrics", {})
            error_metrics = metrics.get("error_metrics", {})
            
            # Summary
            build_duration = build_metrics.get("build_duration", 0)
            report["summary"] = {
                "deployment_id": metrics.get("deployment_id"),
                "build_duration": f"{build_duration:.2f}s",
                "status": "success" if build_duration > 0 else "unknown",
                "functions_deployed": performance_metrics.get("functions_count", 0),
                "errors_detected": error_metrics.get("error_count", 0)
            }
            
            # Performance analysis
            report["performance_analysis"] = {
                "build_speed": "fast" if build_duration < 60 else "slow" if build_duration > 300 else "normal",
                "complexity_score": performance_metrics.get("functions_count", 0) + performance_metrics.get("routes_count", 0),
                "optimization_potential": "high" if build_duration > 180 else "medium" if build_duration > 90 else "low"
            }
            
            # Recommendations
            if build_duration > 300:  # 5 minutes
                report["recommendations"].append("Consider optimizing build process - build time is above 5 minutes")
            
            if error_metrics.get("error_count", 0) > 0:
                report["recommendations"].append("Review build errors to improve deployment reliability")
            
            if performance_metrics.get("functions_count", 0) > 50:
                report["recommendations"].append("Consider function optimization - large number of functions detected")
            
            # Alerts
            if error_metrics.get("error_count", 0) > 5:
                report["alerts"].append({"type": "high_error_count", "message": "High number of build errors detected"})
            
            if build_duration > 600:  # 10 minutes
                report["alerts"].append({"type": "slow_build", "message": "Build time exceeds 10 minutes"})
        
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            report["generation_error"] = str(e)
        
        return report

class VercelIntegration:
    """Main Vercel integration orchestrator - Lead Dev IA + Backend Senior roles"""
    
    def __init__(self, config -> None: VercelConfig) -> None:
        self.config = config
        self.security_manager = VercelSecurityManager(config)
        self.ml_optimizer = VercelMLOptimizer(config)
        self.file_manager = VercelFileManager(config)
        self.monitor = VercelMonitor(config)
        
        # Active deployments tracking
        self.active_deployments = {}
        
    async def deploy_project(self, source_path: str, project_name: str, creator_id: str, 
                           framework: ProjectType = ProjectType.NEXTJS, 
                           environment: Environment = Environment.PREVIEW) -> VercelDeployment:
        """Deploy a project to Vercel with full enterprise features"""
        
        deployment_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            ACTIVE_DEPLOYMENTS.inc()
            logger.info(f"Starting Vercel deployment: {deployment_id} - {project_name}")
            
            # Step 1: Security validation
            security_check = self.security_manager.validate_deployment_security({
                "source_path": source_path,
                "project_name": project_name
            })
            
            if not security_check["secure"]:
                raise ValueError(f"Security validation failed: {security_check['warnings']}")
            
            # Step 2: Prepare deployment files
            files = await self.file_manager.prepare_deployment_files(source_path, framework)
            if not files:
                raise ValueError("No files prepared for deployment")
            
            # Step 3: ML-powered optimization
            optimization = await self.ml_optimizer.optimize_deployment_config(framework, [])
            
            # Step 4: Create deployment via API
            async with VercelAPIClient(self.config) as api_client:
                deployment_config = {
                    "production": environment == Environment.PRODUCTION,
                    "framework": framework.value,
                    **optimization.get("build_config", {})
                }
                
                deployment_result = await api_client.create_deployment(
                    project_name, files, deployment_config
                )
                
                if "error" in deployment_result:
                    raise ValueError(f"Deployment creation failed: {deployment_result['error']}")
                
                vercel_deployment_id = deployment_result.get("id")
                deployment_url = deployment_result.get("url", "")
                
                # Step 5: Create deployment metadata
                deployment = VercelDeployment(
                    deployment_id=deployment_id,
                    project_id=deployment_result.get("projectId", ""),
                    creator_id=creator_id,
                    name=project_name,
                    url=f"https://{deployment_url}",
                    status=DeploymentStatus.BUILDING,
                    environment=environment,
                    framework=framework,
                    created_at=datetime.utcnow(),
                    source={"path": source_path, "files_count": len(files)},
                    meta=optimization
                )
                
                # Step 6: Monitor deployment
                self.active_deployments[deployment_id] = deployment
                
                async for status_update in self.monitor.monitor_deployment(vercel_deployment_id, api_client):
                    deployment.status = DeploymentStatus(status_update["status"])
                    
                    if deployment.status == DeploymentStatus.READY:
                        deployment.ready_at = datetime.utcnow()
                        break
                    elif deployment.status == DeploymentStatus.ERROR:
                        raise ValueError(f"Deployment failed: {status_update.get('error')}")
                
                # Step 7: Collect metrics
                metrics = await self.monitor.collect_deployment_metrics(vercel_deployment_id, api_client)
                deployment.meta["metrics"] = metrics
                
                # Step 8: Generate deployment report
                report = self.monitor.generate_deployment_report(metrics)
                deployment.meta["report"] = report
                
                DEPLOYMENT_COUNTER.labels(status="success", type=framework.value).inc()
                
                processing_time = time.time() - start_time
                logger.info(f"Vercel deployment completed: {deployment_id} in {processing_time:.2f}s")
                
                return deployment
                
        except Exception as e:
            logger.error(f"Vercel deployment failed: {deployment_id} - {e}")
            ERROR_COUNTER.labels(error_type="deployment_failure").inc()
            DEPLOYMENT_COUNTER.labels(status="error", type=framework.value).inc()
            
            # Create error deployment
            error_deployment = VercelDeployment(
                deployment_id=deployment_id,
                project_id="",
                creator_id=creator_id,
                name=project_name,
                url="",
                status=DeploymentStatus.ERROR,
                environment=environment,
                framework=framework,
                created_at=datetime.utcnow(),
                meta={"error": str(e)}
            )
            return error_deployment
            
        finally:
            ACTIVE_DEPLOYMENTS.dec()
            if deployment_id in self.active_deployments:
                del self.active_deployments[deployment_id]
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[VercelDeployment]:
        """Get deployment status"""
        return self.active_deployments.get(deployment_id)
    
    async def list_creator_deployments(self, creator_id: str) -> List[VercelDeployment]:
        """List deployments for a creator"""
        # In real implementation, this would query the database
        return [dep for dep in self.active_deployments.values() if dep.creator_id == creator_id]
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for Vercel integration"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "metrics": {
                "active_deployments": len(self.active_deployments),
                "system_memory_usage": psutil.virtual_memory().percent,
                "system_cpu_usage": psutil.cpu_percent()
            },
            "services": {
                "api_connectivity": await self._check_api_connectivity(),
                "file_system": self._check_file_system_health()
            }
        }
        
        # Determine overall health
        if health_status["metrics"]["system_memory_usage"] > 90:
            health_status["status"] = "degraded"
        
        return health_status
    
    async def _check_api_connectivity(self) -> str:
        """Check Vercel API connectivity"""
        try:
            async with VercelAPIClient(self.config) as api_client:
                # Simple API call to check connectivity
                result = await api_client.list_deployments(limit=1)
                return "healthy" if "error" not in result else "unhealthy"
        except Exception:
            return "unavailable"
    
    def _check_file_system_health(self) -> str:
        """Check file system health"""
        try:
            # Check disk space
            disk_usage = psutil.disk_usage('/')
            free_percentage = (disk_usage.free / disk_usage.total) * 100
            
            if free_percentage > 10:
                return "healthy"
            elif free_percentage > 5:
                return "degraded"
            else:
                return "critical"
        except Exception:
            return "unknown"

# Service factory and configuration
class VercelService:
    """Main Vercel service facade - DevOps + Integration role"""
    
    def __init__(self, config -> None: Optional[VercelConfig] = None) -> None:
        self.config = config or VercelConfig(
            api_token="your-vercel-token-here",  # Should be configured via environment
            enable_analytics=True,
            edge_functions_enabled=True,
            image_optimization=True
        )
        self.integration = VercelIntegration(self.config)
    
    async def initialize(self) -> None:
        """Initialize the Vercel service"""
        logger.info("Initializing Vercel Integration Service")
        
        # Validate configuration
        await self._validate_configuration()
        
        # Test API connectivity
        await self._test_connectivity()
        
        logger.info("Vercel Integration Service initialized successfully")
    
    async def _validate_configuration(self) -> None:
        """Validate service configuration"""
        if not self.config.api_token or self.config.api_token == "your-vercel-token-here":
            logger.warning("Vercel API token not configured - deployments will fail")
    
    async def _test_connectivity(self) -> None:
        """Test Vercel API connectivity"""
        try:
            async with VercelAPIClient(self.config) as api_client:
                result = await api_client.list_deployments(limit=1)
                if "error" in result:
                    logger.warning("Vercel API connectivity test failed")
                else:
                    logger.info("Vercel API connectivity test successful")
        except Exception as e:
            logger.warning(f"Vercel API connectivity test error: {e}")
    
    async def deploy(self, source_path: str, project_name: str, creator_id: str,
                    framework: ProjectType = ProjectType.NEXTJS,
                    environment: Environment = Environment.PREVIEW) -> VercelDeployment:
        """Deploy with full enterprise features"""
        return await self.integration.deploy_project(source_path, project_name, creator_id, framework, environment)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return await self.integration.health_check()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get deployment metrics"""
        return {
            "deployments_total": DEPLOYMENT_COUNTER._value.sum(),
            "active_deployments": ACTIVE_DEPLOYMENTS._value.get(),
            "error_count": ERROR_COUNTER._value.sum()
        }

# Export main classes and functions
__all__ = [
    'VercelService',
    'VercelConfig',
    'VercelDeployment',
    'VercelProject',
    'ProjectType',
    'Environment',
    'DeploymentStatus',
    'VercelIntegration'
]

if __name__ == "__main__":
    # Example usage and testing
    async def main() -> None:
        # Initialize service
        service = VercelService()
        await service.initialize()
        
        # Health check
        health = await service.get_health_status()
        print(f"Service Health: {health}")
        
        # Example deployment (would need actual source path)
        # deployment = await service.deploy("./my-app", "ainflue-creator-site", "creator123")
        # print(f"Deployment: {deployment}")
    
    # Run example
    # asyncio.run(main())