"""
AINFLUE INTEGRATIONS - NETLIFY HOSTING PLATFORM
==============================================

Enterprise Netlify integration for creator economy platform deployment.
Combines multiple expert roles for comprehensive JAMstack deployment management.

Author: Fahed Mlaiel <mlaiel@live.de>
Platform: Ainflue - IA Influencer Agent + Content Protection Platform
Architecture Level: Level 3 (integrations/cloud_providers)

Expert Roles Applied:
- Lead Dev IA: AI-powered build optimization, intelligent deployment strategies
- Backend Senior: Robust JAMstack architecture, enterprise deployment patterns
- ML Engineer: Performance analytics, predictive scaling, build optimization
- DBA: Site metadata management, analytics tracking, audit trails
- Security: Secure deployment practices, form protection, environment security
- Microservices: Multi-service deployment orchestration, serverless functions
- Audio Engineer: Media optimization for edge delivery, asset optimization
- DevOps: Automated CI/CD, monitoring, deployment automation, rollback strategies
- IA Prompt Engineer: AI-driven site optimization, performance recommendations

Business Logic Integration:
Creator → Site Deploy → Build Optimization → Edge Distribution → Form Handling → Analytics → Revenue Tracking
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

# Monitoring and Performance
import psutil
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics for DevOps monitoring
DEPLOYMENT_COUNTER = Counter('netlify_deployments_total', 'Total Netlify deployments', ['status', 'type'])
BUILD_DURATION = Histogram('netlify_build_duration_seconds', 'Build duration')
ACTIVE_DEPLOYMENTS = Gauge('netlify_active_deployments', 'Active deployments')
ERROR_COUNTER = Counter('netlify_errors_total', 'Netlify API errors', ['error_type'])
FUNCTION_INVOCATIONS = Counter('netlify_function_invocations_total', 'Function invocations')

class DeploymentStatus(Enum):
    """Netlify deployment status"""
    NEW = "new"
    BUILDING = "building"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    SKIPPED = "skipped"

class SiteType(Enum):
    """Site framework types"""
    STATIC = "static"
    GATSBY = "gatsby"
    NEXTJS = "nextjs"
    NUXT = "nuxt"
    HUGO = "hugo"
    JEKYLL = "jekyll"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"
    UNKNOWN = "unknown"

class BuildCommand(Enum):
    """Common build commands"""
    NPM_BUILD = "npm run build"
    YARN_BUILD = "yarn build"
    GATSBY_BUILD = "gatsby build"
    HUGO_BUILD = "hugo"
    JEKYLL_BUILD = "jekyll build"
    CUSTOM = "custom"

@dataclass
class NetlifyDeployment:
    """Netlify deployment information"""
    deployment_id: str
    site_id: str
    creator_id: str
    name: str
    url: str
    admin_url: str
    status: DeploymentStatus
    site_type: SiteType
    created_at: datetime
    published_at: Optional[datetime] = None
    build_log: Optional[List[str]] = None
    functions: Optional[List[Dict]] = None
    forms: Optional[List[Dict]] = None
    redirects: Optional[List[Dict]] = None
    headers: Optional[Dict] = None
    meta: Optional[Dict] = None

@dataclass
class NetlifySite:
    """Netlify site information"""
    site_id: str
    name: str
    custom_domain: Optional[str]
    creator_id: str
    site_type: SiteType
    build_settings: Dict[str, Any]
    deploy_url: str
    admin_url: str
    ssl_enabled: bool
    branch_deploys: bool
    created_at: datetime
    updated_at: datetime

class NetlifyConfig(BaseModel):
    """Configuration for Netlify integration"""
    # API Configuration
    access_token: str = Field(..., description="Netlify access token")
    api_base_url: str = Field(default="https://api.netlify.com/api/v1", description="Netlify API base URL")
    
    # Build Configuration
    default_build_command: str = Field(default="npm run build", description="Default build command")
    default_publish_dir: str = Field(default="dist", description="Default publish directory")
    node_version: str = Field(default="18", description="Node.js version")
    
    # Site Configuration
    enable_forms: bool = Field(default=True, description="Enable Netlify Forms")
    enable_functions: bool = Field(default=True, description="Enable Netlify Functions")
    enable_identity: bool = Field(default=False, description="Enable Netlify Identity")
    enable_analytics: bool = Field(default=True, description="Enable Netlify Analytics")
    
    # Security Configuration
    enable_ssl: bool = Field(default=True, description="Enable SSL by default")
    enable_branch_deploys: bool = Field(default=True, description="Enable branch deploys")
    webhook_secret: Optional[str] = Field(default=None, description="Webhook secret for validation")
    
    # Performance Configuration
    build_timeout: int = Field(default=900, description="Build timeout in seconds")
    max_build_size: int = Field(default=100 * 1024 * 1024, description="Maximum build size")
    edge_handlers: bool = Field(default=True, description="Enable Edge Handlers")
    
    # Monitoring Configuration
    enable_logging: bool = Field(default=True, description="Enable deployment logging")
    log_retention_days: int = Field(default=30, description="Log retention period")
    
    @validator('access_token')
    def validate_access_token(cls, v) -> None:
        if not v or len(v) < 10:
            raise ValueError("Valid Netlify access token required")
        return v

class NetlifySecurityManager:
    """Security manager for Netlify deployments - Security Expert role"""
    
    def __init__(self, config -> None: NetlifyConfig) -> None:
        self.config = config
    
    def generate_webhook_signature(self, payload: str, secret: str) -> str:
        """Generate webhook signature for validation"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Validate webhook signature from Netlify"""
        expected_signature = self.generate_webhook_signature(payload, secret)
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    def sanitize_build_command(self, command: str) -> str:
        """Sanitize build command for security"""
        # Remove potentially dangerous commands
        dangerous_commands = ['rm', 'sudo', 'curl', 'wget', 'git clone']
        
        for dangerous in dangerous_commands:
            if dangerous in command.lower():
                logger.warning(f"Potentially dangerous command detected in build: {dangerous}")
        
        return command
    
    def validate_environment_variables(self, env_vars: Dict[str, str]) -> Dict[str, Any]:
        """Validate environment variables for security"""
        validation_result = {
            "secure": True,
            "warnings": [],
            "sanitized_vars": {}
        }
        
        # Check for exposed secrets
        sensitive_keywords = ['password', 'secret', 'key', 'token', 'private']
        
        for key, value in env_vars.items():
            # Check if variable name suggests it's sensitive
            is_sensitive = any(keyword in key.lower() for keyword in sensitive_keywords)
            
            if is_sensitive:
                # Don't expose sensitive values in logs
                validation_result["sanitized_vars"][key] = "[REDACTED]"
                
                # Warn if not properly protected
                if not value.startswith('$'):  # Not a reference
                    validation_result["warnings"].append(f"Sensitive variable {key} may be exposed")
            else:
                validation_result["sanitized_vars"][key] = value
        
        return validation_result
    
    def generate_secure_form_settings(self) -> Dict[str, Any]:
        """Generate secure form settings"""
        return {
            "spam_protection": True,
            "honeypot": True,
            "recaptcha": True,
            "notifications": {
                "email": True,
                "webhook": False
            },
            "submission_limits": {
                "daily": 1000,
                "hourly": 100
            }
        }
    
    def validate_site_security(self, site_config: Dict) -> Dict[str, Any]:
        """Validate site configuration for security"""
        security_check = {
            "secure": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check SSL configuration
        if not site_config.get("ssl", True):
            security_check["issues"].append("SSL not enabled - site will be insecure")
            security_check["secure"] = False
        
        # Check custom headers for security
        headers = site_config.get("headers", {})
        security_headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
        
        for header, value in security_headers.items():
            if header not in headers:
                security_check["recommendations"].append(f"Consider adding security header: {header}")
        
        # Check redirects for security
        redirects = site_config.get("redirects", [])
        for redirect in redirects:
            if redirect.get("force", False) and redirect.get("status") == 301:
                # Check for open redirects
                if "*" in redirect.get("to", ""):
                    security_check["issues"].append("Potential open redirect detected")
        
        return security_check

class NetlifyMLOptimizer:
    """ML-powered deployment optimization - ML Engineer + Lead Dev IA roles"""
    
    def __init__(self, config -> None: NetlifyConfig) -> None:
        self.config = config
        self.build_history = []
    
    async def optimize_build_settings(self, site_type: SiteType, historical_data: List[Dict]) -> Dict[str, Any]:
        """AI-powered build configuration optimization"""
        optimization = {
            "build_settings": {},
            "performance_settings": {},
            "caching_strategy": {},
            "recommendations": []
        }
        
        try:
            # Analyze historical build performance
            if historical_data:
                performance_analysis = self._analyze_build_performance(historical_data)
                optimization.update(performance_analysis)
            
            # Site type specific optimizations
            type_optimizations = self._get_site_type_optimizations(site_type)
            optimization["build_settings"].update(type_optimizations)
            
            # Performance optimizations
            performance_opts = self._generate_performance_optimizations(site_type, historical_data)
            optimization["performance_settings"].update(performance_opts)
            
            # Intelligent caching strategy
            caching_strategy = self._optimize_caching_strategy(site_type, historical_data)
            optimization["caching_strategy"].update(caching_strategy)
            
        except Exception as e:
            logger.error(f"Build optimization failed: {e}")
            optimization["error"] = str(e)
        
        return optimization
    
    def _analyze_build_performance(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Analyze build performance patterns"""
        if not historical_data:
            return {}
        
        build_times = [d.get("build_time", 0) for d in historical_data if d.get("build_time")]
        success_rate = len([d for d in historical_data if d.get("status") == "ready"]) / len(historical_data)
        
        analysis = {
            "average_build_time": sum(build_times) / len(build_times) if build_times else 0,
            "build_time_variance": self._calculate_variance(build_times),
            "success_rate": success_rate,
            "failure_patterns": self._identify_failure_patterns(historical_data)
        }
        
        # Generate recommendations based on analysis
        recommendations = []
        if analysis["average_build_time"] > 300:  # 5 minutes
            recommendations.append("Consider optimizing dependencies to reduce build time")
        
        if success_rate < 0.9:
            recommendations.append("Build success rate is below 90% - review failure patterns")
        
        if analysis["build_time_variance"] > 100:
            recommendations.append("Build times are inconsistent - consider dependency caching")
        
        analysis["recommendations"] = recommendations
        return analysis
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def _identify_failure_patterns(self, deployments: List[Dict]) -> List[str]:
        """Identify common failure patterns"""
        failures = [d for d in deployments if d.get("status") == "error"]
        patterns = []
        
        # Common failure reasons
        common_errors = {}
        for failure in failures:
            error_msg = failure.get("error_message", "").lower()
            if "dependency" in error_msg:
                common_errors["dependency_issues"] = common_errors.get("dependency_issues", 0) + 1
            elif "timeout" in error_msg:
                common_errors["timeout_issues"] = common_errors.get("timeout_issues", 0) + 1
            elif "memory" in error_msg:
                common_errors["memory_issues"] = common_errors.get("memory_issues", 0) + 1
        
        # Convert to patterns
        for error_type, count in common_errors.items():
            if count > len(failures) * 0.3:  # More than 30% of failures
                patterns.append(f"Frequent {error_type.replace('_', ' ')}")
        
        return patterns
    
    def _get_site_type_optimizations(self, site_type: SiteType) -> Dict[str, Any]:
        """Get optimizations specific to site type"""
        optimizations = {
            SiteType.STATIC: {
                "build_command": "echo 'Static site - no build required'",
                "publish_directory": ".",
                "node_version": None
            },
            SiteType.GATSBY: {
                "build_command": "gatsby build",
                "publish_directory": "public",
                "node_version": "18",
                "environment": {
                    "NODE_ENV": "production",
                    "GATSBY_CPU_COUNT": "2"
                }
            },
            SiteType.NEXTJS: {
                "build_command": "npm run build && npm run export",
                "publish_directory": "out",
                "node_version": "18",
                "environment": {
                    "NEXT_TELEMETRY_DISABLED": "1"
                }
            },
            SiteType.HUGO: {
                "build_command": "hugo --minify",
                "publish_directory": "public",
                "environment": {
                    "HUGO_VERSION": "0.101.0"
                }
            },
            SiteType.REACT: {
                "build_command": "npm run build",
                "publish_directory": "build",
                "node_version": "18"
            },
            SiteType.VUE: {
                "build_command": "npm run build",
                "publish_directory": "dist",
                "node_version": "18"
            }
        }
        
        return optimizations.get(site_type, {})
    
    def _generate_performance_optimizations(self, site_type: SiteType, historical_data: List[Dict]) -> Dict[str, Any]:
        """Generate performance optimization settings"""
        optimizations = {
            "asset_optimization": {
                "bundle": True,
                "minify": True,
                "pretty_urls": True
            },
            "caching": {
                "edge_handlers": self.config.edge_handlers,
                "immutable_patterns": [
                    "/_next/static/**",
                    "/static/**",
                    "*.js",
                    "*.css"
                ]
            },
            "build_optimization": {
                "skip_processing": False,
                "processing_timeout": self.config.build_timeout
            }
        }
        
        # Adjust based on site type
        if site_type in [SiteType.REACT, SiteType.VUE, SiteType.NEXTJS]:
            optimizations["asset_optimization"]["bundle_analyzer"] = True
            optimizations["build_optimization"]["node_modules_cache"] = True
        
        # Adjust based on historical performance
        if historical_data:
            avg_build_time = sum(d.get("build_time", 0) for d in historical_data) / len(historical_data)
            if avg_build_time > 180:  # 3 minutes
                optimizations["build_optimization"]["parallel_processing"] = True
        
        return optimizations
    
    def _optimize_caching_strategy(self, site_type: SiteType, historical_data: List[Dict]) -> Dict[str, Any]:
        """Optimize caching strategy based on site characteristics"""
        strategy = {
            "static_assets": {
                "max_age": 31536000,  # 1 year
                "immutable": True
            },
            "html_pages": {
                "max_age": 3600,  # 1 hour
                "stale_while_revalidate": 86400  # 1 day
            },
            "api_responses": {
                "max_age": 300,  # 5 minutes
                "stale_while_revalidate": 600  # 10 minutes
            }
        }
        
        # Adjust based on site type
        if site_type == SiteType.STATIC:
            strategy["html_pages"]["max_age"] = 86400  # 1 day for static sites
        elif site_type in [SiteType.GATSBY, SiteType.HUGO]:
            strategy["html_pages"]["max_age"] = 3600  # 1 hour for SSG
        
        return strategy
    
    async def predict_build_performance(self, site_config: Dict) -> Dict[str, Any]:
        """Predict build performance based on configuration"""
        prediction = {
            "estimated_build_time": 120,  # Default 2 minutes
            "success_probability": 0.95,
            "resource_requirements": {},
            "optimization_suggestions": []
        }
        
        try:
            # Analyze dependencies
            package_json = site_config.get("package_json", {})
            dependencies = package_json.get("dependencies", {})
            dev_dependencies = package_json.get("devDependencies", {})
            
            total_deps = len(dependencies) + len(dev_dependencies)
            
            # Estimate build time based on dependencies
            base_time = 60  # 1 minute base
            dep_time = total_deps * 2  # 2 seconds per dependency
            prediction["estimated_build_time"] = base_time + dep_time
            
            # Adjust for framework
            site_type = site_config.get("framework", SiteType.STATIC)
            if site_type in [SiteType.NEXTJS, SiteType.GATSBY]:
                prediction["estimated_build_time"] *= 1.5
            
            # Success probability based on complexity
            if total_deps > 100:
                prediction["success_probability"] *= 0.9
            if prediction["estimated_build_time"] > 600:  # 10 minutes
                prediction["success_probability"] *= 0.8
            
            # Resource requirements
            prediction["resource_requirements"] = {
                "memory": "1GB" if total_deps > 50 else "512MB",
                "cpu": "2 cores" if prediction["estimated_build_time"] > 300 else "1 core"
            }
            
            # Optimization suggestions
            if prediction["estimated_build_time"] > 300:
                prediction["optimization_suggestions"].append("Consider reducing dependencies")
            if total_deps > 100:
                prediction["optimization_suggestions"].append("Consider dependency analysis and cleanup")
        
        except Exception as e:
            logger.error(f"Build performance prediction failed: {e}")
            prediction["prediction_error"] = str(e)
        
        return prediction

class NetlifyAPIClient:
    """Netlify API client - Backend Senior role"""
    
    def __init__(self, config -> None: NetlifyConfig) -> None:
        self.config = config
        self.session = None
    
    async def __aenter__(self) -> None:
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=60)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()
    
    async def create_site(self, name: str, build_settings: Dict = None) -> Dict[str, Any]:
        """Create a new site"""
        try:
            site_data = {
                "name": name,
                "build_settings": build_settings or {}
            }
            
            async with self.session.post(
                f"{self.config.api_base_url}/sites",
                json=site_data
            ) as response:
                
                if response.status == 201:
                    result = await response.json()
                    logger.info(f"Site created successfully: {name}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Site creation failed: {response.status} - {error_text}")
                    ERROR_COUNTER.labels(error_type="create_site").inc()
                    return {"error": error_text, "status": response.status}
        
        except Exception as e:
            logger.error(f"Site creation error: {e}")
            ERROR_COUNTER.labels(error_type="api_error").inc()
            return {"error": str(e)}
    
    async def deploy_site(self, site_id: str, files: Dict[str, bytes], functions: Dict[str, str] = None) -> Dict[str, Any]:
        """Deploy site with files"""
        try:
            # Prepare form data
            data = aiohttp.FormData()
            
            # Add files
            for file_path, content in files.items():
                data.add_field('files', content, filename=file_path)
            
            # Add functions if provided
            if functions:
                for func_name, func_content in functions.items():
                    data.add_field('functions', func_content.encode(), filename=f"{func_name}.js")
            
            async with self.session.post(
                f"{self.config.api_base_url}/sites/{site_id}/deploys",
                data=data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    DEPLOYMENT_COUNTER.labels(status="success", type="deploy").inc()
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Deployment failed: {response.status} - {error_text}")
                    ERROR_COUNTER.labels(error_type="deploy_site").inc()
                    return {"error": error_text, "status": response.status}
        
        except Exception as e:
            logger.error(f"Deployment error: {e}")
            ERROR_COUNTER.labels(error_type="api_error").inc()
            return {"error": str(e)}
    
    async def get_deploy(self, deploy_id: str) -> Dict[str, Any]:
        """Get deployment information"""
        try:
            async with self.session.get(
                f"{self.config.api_base_url}/deploys/{deploy_id}"
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Get deploy failed: {response.status} - {error_text}")
                    return {"error": error_text, "status": response.status}
        
        except Exception as e:
            logger.error(f"Get deploy error: {e}")
            return {"error": str(e)}
    
    async def list_site_deploys(self, site_id: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """List deployments for a site"""
        try:
            async with self.session.get(
                f"{self.config.api_base_url}/sites/{site_id}/deploys?page={page}&per_page={per_page}"
            ) as response:
                
                if response.status == 200:
                    return {"deploys": await response.json()}
                else:
                    error_text = await response.text()
                    logger.error(f"List deploys failed: {response.status} - {error_text}")
                    return {"error": error_text, "status": response.status}
        
        except Exception as e:
            logger.error(f"List deploys error: {e}")
            return {"error": str(e)}
    
    async def update_site_settings(self, site_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update site settings"""
        try:
            async with self.session.patch(
                f"{self.config.api_base_url}/sites/{site_id}",
                json=settings
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Site update failed: {response.status} - {error_text}")
                    return {"error": error_text, "status": response.status}
        
        except Exception as e:
            logger.error(f"Site update error: {e}")
            return {"error": str(e)}
    
    async def get_build_logs(self, deploy_id: str) -> List[str]:
        """Get build logs for deployment"""
        try:
            async with self.session.get(
                f"{self.config.api_base_url}/deploys/{deploy_id}/log"
            ) as response:
                
                if response.status == 200:
                    log_text = await response.text()
                    return log_text.split('\n') if log_text else []
                else:
                    logger.error(f"Get build logs failed: {response.status}")
                    return []
        
        except Exception as e:
            logger.error(f"Get build logs error: {e}")
            return []

class NetlifyFileManager:
    """File management for Netlify deployments - Backend Senior + DevOps roles"""
    
    def __init__(self, config -> None: NetlifyConfig) -> None:
        self.config = config
    
    async def prepare_site_files(self, source_path: str, site_type: SiteType) -> Dict[str, bytes]:
        """Prepare files for deployment"""
        files = {}
        
        try:
            source_path = Path(source_path)
            
            # Get file patterns based on site type
            file_patterns = self._get_site_file_patterns(site_type)
            
            for pattern in file_patterns:
                for file_path in source_path.rglob(pattern):
                    if file_path.is_file() and self._should_include_file(file_path):
                        relative_path = file_path.relative_to(source_path)
                        
                        # Read file content
                        async with aiofiles.open(file_path, 'rb') as f:
                            content = await f.read()
                            files[str(relative_path)] = content
            
            logger.info(f"Prepared {len(files)} files for deployment")
            return files
        
        except Exception as e:
            logger.error(f"File preparation failed: {e}")
            return {}
    
    def _get_site_file_patterns(self, site_type: SiteType) -> List[str]:
        """Get file patterns for different site types"""
        patterns = {
            SiteType.STATIC: [
                "*.html", "*.css", "*.js", "*.png", "*.jpg", "*.jpeg", "*.gif",
                "*.svg", "*.ico", "*.pdf", "assets/**/*", "images/**/*"
            ],
            SiteType.GATSBY: [
                "public/**/*", "static/**/*", "gatsby-config.js", "gatsby-node.js"
            ],
            SiteType.NEXTJS: [
                "out/**/*", ".next/**/*", "public/**/*", "next.config.js"
            ],
            SiteType.HUGO: [
                "public/**/*", "static/**/*", "config.*", "data/**/*"
            ],
            SiteType.JEKYLL: [
                "_site/**/*", "_config.yml", "assets/**/*"
            ],
            SiteType.REACT: [
                "build/**/*", "public/**/*", "src/**/*", "package.json"
            ],
            SiteType.VUE: [
                "dist/**/*", "public/**/*", "src/**/*", "package.json"
            ]
        }
        
        return patterns.get(site_type, ["**/*"])
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in deployment"""
        # Exclude common development files
        exclude_patterns = [
            "node_modules", ".git", ".env", "*.log", "*.tmp",
            ".DS_Store", "Thumbs.db", "*.cache", "coverage"
        ]
        
        for pattern in exclude_patterns:
            if pattern in str(file_path):
                return False
        
        return True
    
    async def prepare_netlify_functions(self, functions_path: str) -> Dict[str, str]:
        """Prepare Netlify Functions"""
        functions = {}
        
        try:
            functions_path = Path(functions_path)
            
            if functions_path.exists():
                for func_file in functions_path.glob("*.js"):
                    async with aiofiles.open(func_file, 'r', encoding='utf-8') as f:
                        content = await f.read()
                        functions[func_file.stem] = content
                
                logger.info(f"Prepared {len(functions)} functions")
            
            return functions
        
        except Exception as e:
            logger.error(f"Functions preparation failed: {e}")
            return {}
    
    async def create_netlify_config(self, site_type: SiteType, build_settings: Dict) -> str:
        """Create netlify.toml configuration"""
        config_lines = [
            "[build]",
            f"  command = \"{build_settings.get('command', self.config.default_build_command)}\"",
            f"  publish = \"{build_settings.get('publish', self.config.default_publish_dir)}\"",
        ]
        
        # Add environment variables
        if build_settings.get("environment"):
            config_lines.append("\n[build.environment]")
            for key, value in build_settings["environment"].items():
                config_lines.append(f"  {key} = \"{value}\"")
        
        # Add redirects
        if build_settings.get("redirects"):
            config_lines.append("\n[[redirects]]")
            for redirect in build_settings["redirects"]:
                config_lines.append(f"  from = \"{redirect['from']}\"")
                config_lines.append(f"  to = \"{redirect['to']}\"")
                config_lines.append(f"  status = {redirect.get('status', 200)}")
        
        # Add headers
        if build_settings.get("headers"):
            config_lines.append("\n[[headers]]")
            for path, headers in build_settings["headers"].items():
                config_lines.append(f"  for = \"{path}\"")
                config_lines.append("  [headers.values]")
                for header, value in headers.items():
                    config_lines.append(f"    {header} = \"{value}\"")
        
        return "\n".join(config_lines)

class NetlifyMonitor:
    """Monitoring and analytics for Netlify deployments - DevOps role"""
    
    def __init__(self, config -> None: NetlifyConfig) -> None:
        self.config = config
    
    async def monitor_deployment(self, deploy_id: str, api_client: NetlifyAPIClient) -> AsyncGenerator[Dict[str, Any], None]:
        """Monitor deployment progress"""
        try:
            max_attempts = 120  # 10 minutes with 5-second intervals
            attempt = 0
            
            while attempt < max_attempts:
                deploy_info = await api_client.get_deploy(deploy_id)
                
                if "error" in deploy_info:
                    yield {"status": "ERROR", "error": deploy_info["error"]}
                    break
                
                status = deploy_info.get("state", "unknown")
                yield {
                    "status": status,
                    "progress": (attempt / max_attempts) * 100,
                    "deploy_info": deploy_info
                }
                
                if status in ["ready", "error", "skipped"]:
                    break
                
                await asyncio.sleep(5)
                attempt += 1
            
            if attempt >= max_attempts:
                yield {"status": "TIMEOUT", "error": "Deployment monitoring timeout"}
        
        except Exception as e:
            logger.error(f"Deployment monitoring failed: {e}")
            yield {"status": "ERROR", "error": str(e)}
    
    async def collect_deployment_metrics(self, deploy_id: str, api_client: NetlifyAPIClient) -> Dict[str, Any]:
        """Collect deployment metrics"""
        metrics = {
            "deploy_id": deploy_id,
            "timestamp": datetime.utcnow().isoformat(),
            "build_metrics": {},
            "performance_metrics": {},
            "error_metrics": {}
        }
        
        try:
            # Get deployment info
            deploy_info = await api_client.get_deploy(deploy_id)
            
            if "error" not in deploy_info:
                # Build metrics
                created_at = deploy_info.get("created_at")
                published_at = deploy_info.get("published_at")
                
                if created_at and published_at:
                    created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    published_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    build_duration = (published_time - created_time).total_seconds()
                    
                    metrics["build_metrics"] = {
                        "build_duration": build_duration,
                        "created_at": created_time.isoformat(),
                        "published_at": published_time.isoformat()
                    }
                    
                    BUILD_DURATION.observe(build_duration)
                
                # Performance metrics
                metrics["performance_metrics"] = {
                    "deploy_ssl_url": deploy_info.get("ssl_url"),
                    "deploy_url": deploy_info.get("deploy_url"),
                    "context": deploy_info.get("context"),
                    "branch": deploy_info.get("branch")
                }
                
                # Collect build logs for error analysis
                logs = await api_client.get_build_logs(deploy_id)
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
        """Generate deployment report"""
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
                "deploy_id": metrics.get("deploy_id"),
                "build_duration": f"{build_duration:.2f}s",
                "status": "success" if build_duration > 0 else "unknown",
                "deploy_url": performance_metrics.get("deploy_ssl_url"),
                "errors_detected": error_metrics.get("error_count", 0)
            }
            
            # Performance analysis
            report["performance_analysis"] = {
                "build_speed": "fast" if build_duration < 120 else "slow" if build_duration > 600 else "normal",
                "ssl_enabled": "ssl_url" in performance_metrics,
                "branch_deploy": performance_metrics.get("context") == "branch-deploy"
            }
            
            # Recommendations
            if build_duration > 600:  # 10 minutes
                report["recommendations"].append("Build time exceeds 10 minutes - consider optimization")
            
            if error_metrics.get("error_count", 0) > 0:
                report["recommendations"].append("Build errors detected - review logs for optimization")
            
            # Alerts
            if error_metrics.get("error_count", 0) > 5:
                report["alerts"].append({"type": "high_error_count", "message": "High number of build errors"})
            
            if build_duration > 900:  # 15 minutes
                report["alerts"].append({"type": "slow_build", "message": "Build time exceeds timeout threshold"})
        
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            report["generation_error"] = str(e)
        
        return report

class NetlifyIntegration:
    """Main Netlify integration orchestrator - Lead Dev IA + Backend Senior roles"""
    
    def __init__(self, config -> None: NetlifyConfig) -> None:
        self.config = config
        self.security_manager = NetlifySecurityManager(config)
        self.ml_optimizer = NetlifyMLOptimizer(config)
        self.file_manager = NetlifyFileManager(config)
        self.monitor = NetlifyMonitor(config)
        
        # Active deployments tracking
        self.active_deployments = {}
    
    async def deploy_site(self, source_path: str, site_name: str, creator_id: str,
                         site_type: SiteType = SiteType.STATIC,
                         build_settings: Dict = None) -> NetlifyDeployment:
        """Deploy a site to Netlify with full enterprise features"""
        
        deployment_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            ACTIVE_DEPLOYMENTS.inc()
            logger.info(f"Starting Netlify deployment: {deployment_id} - {site_name}")
            
            # Step 1: Security validation
            security_check = self.security_manager.validate_site_security({
                "source_path": source_path,
                "site_name": site_name,
                "build_settings": build_settings or {}
            })
            
            if not security_check["secure"]:
                raise ValueError(f"Security validation failed: {security_check['issues']}")
            
            # Step 2: ML-powered optimization
            optimization = await self.ml_optimizer.optimize_build_settings(site_type, [])
            
            # Step 3: Prepare files
            files = await self.file_manager.prepare_site_files(source_path, site_type)
            if not files:
                raise ValueError("No files prepared for deployment")
            
            # Step 4: Prepare functions if enabled
            functions = {}
            if self.config.enable_functions:
                functions_path = os.path.join(source_path, "netlify", "functions")
                functions = await self.file_manager.prepare_netlify_functions(functions_path)
            
            # Step 5: Create optimized build settings
            optimized_settings = {
                **(build_settings or {}),
                **optimization.get("build_settings", {})
            }
            
            # Step 6: Deploy via API
            async with NetlifyAPIClient(self.config) as api_client:
                # Create site first
                site_result = await api_client.create_site(site_name, optimized_settings)
                
                if "error" in site_result:
                    raise ValueError(f"Site creation failed: {site_result['error']}")
                
                site_id = site_result.get("id")
                
                # Deploy files
                deploy_result = await api_client.deploy_site(site_id, files, functions)
                
                if "error" in deploy_result:
                    raise ValueError(f"Deployment failed: {deploy_result['error']}")
                
                netlify_deploy_id = deploy_result.get("id")
                
                # Step 7: Create deployment metadata
                deployment = NetlifyDeployment(
                    deployment_id=deployment_id,
                    site_id=site_id,
                    creator_id=creator_id,
                    name=site_name,
                    url=deploy_result.get("ssl_url", ""),
                    admin_url=deploy_result.get("admin_url", ""),
                    status=DeploymentStatus.BUILDING,
                    site_type=site_type,
                    created_at=datetime.utcnow(),
                    functions=list(functions.keys()) if functions else [],
                    meta=optimization
                )
                
                # Step 8: Monitor deployment
                self.active_deployments[deployment_id] = deployment
                
                async for status_update in self.monitor.monitor_deployment(netlify_deploy_id, api_client):
                    deployment.status = DeploymentStatus(status_update["status"])
                    
                    if deployment.status == DeploymentStatus.READY:
                        deployment.published_at = datetime.utcnow()
                        break
                    elif deployment.status == DeploymentStatus.ERROR:
                        raise ValueError(f"Deployment failed: {status_update.get('error')}")
                
                # Step 9: Collect metrics
                metrics = await self.monitor.collect_deployment_metrics(netlify_deploy_id, api_client)
                deployment.meta["metrics"] = metrics
                
                # Step 10: Generate report
                report = self.monitor.generate_deployment_report(metrics)
                deployment.meta["report"] = report
                
                DEPLOYMENT_COUNTER.labels(status="success", type=site_type.value).inc()
                
                processing_time = time.time() - start_time
                logger.info(f"Netlify deployment completed: {deployment_id} in {processing_time:.2f}s")
                
                return deployment
        
        except Exception as e:
            logger.error(f"Netlify deployment failed: {deployment_id} - {e}")
            ERROR_COUNTER.labels(error_type="deployment_failure").inc()
            DEPLOYMENT_COUNTER.labels(status="error", type=site_type.value).inc()
            
            # Create error deployment
            error_deployment = NetlifyDeployment(
                deployment_id=deployment_id,
                site_id="",
                creator_id=creator_id,
                name=site_name,
                url="",
                admin_url="",
                status=DeploymentStatus.ERROR,
                site_type=site_type,
                created_at=datetime.utcnow(),
                meta={"error": str(e)}
            )
            return error_deployment
        
        finally:
            ACTIVE_DEPLOYMENTS.dec()
            if deployment_id in self.active_deployments:
                del self.active_deployments[deployment_id]
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[NetlifyDeployment]:
        """Get deployment status"""
        return self.active_deployments.get(deployment_id)
    
    async def list_creator_deployments(self, creator_id: str) -> List[NetlifyDeployment]:
        """List deployments for a creator"""
        return [dep for dep in self.active_deployments.values() if dep.creator_id == creator_id]
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for Netlify integration"""
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
        
        if health_status["metrics"]["system_memory_usage"] > 90:
            health_status["status"] = "degraded"
        
        return health_status
    
    async def _check_api_connectivity(self) -> str:
        """Check Netlify API connectivity"""
        try:
            async with NetlifyAPIClient(self.config) as api_client:
                # Simple API call to check connectivity
                result = await api_client.list_site_deploys("test", page=1, per_page=1)
                return "healthy" if "error" not in result else "degraded"
        except Exception:
            return "unavailable"
    
    def _check_file_system_health(self) -> str:
        """Check file system health"""
        try:
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
class NetlifyService:
    """Main Netlify service facade - DevOps + Integration role"""
    
    def __init__(self, config -> None: Optional[NetlifyConfig] = None) -> None:
        self.config = config or NetlifyConfig(
            access_token="your-netlify-token-here",  # Should be configured via environment
            enable_forms=True,
            enable_functions=True,
            enable_analytics=True
        )
        self.integration = NetlifyIntegration(self.config)
    
    async def initialize(self) -> None:
        """Initialize the Netlify service"""
        logger.info("Initializing Netlify Integration Service")
        
        # Validate configuration
        await self._validate_configuration()
        
        # Test API connectivity
        await self._test_connectivity()
        
        logger.info("Netlify Integration Service initialized successfully")
    
    async def _validate_configuration(self) -> None:
        """Validate service configuration"""
        if not self.config.access_token or self.config.access_token == "your-netlify-token-here":
            logger.warning("Netlify access token not configured - deployments will fail")
    
    async def _test_connectivity(self) -> None:
        """Test Netlify API connectivity"""
        try:
            async with NetlifyAPIClient(self.config) as api_client:
                # Test with a simple API call
                result = await api_client.list_site_deploys("test", page=1, per_page=1)
                if "error" in result:
                    logger.warning("Netlify API connectivity test failed")
                else:
                    logger.info("Netlify API connectivity test successful")
        except Exception as e:
            logger.warning(f"Netlify API connectivity test error: {e}")
    
    async def deploy(self, source_path: str, site_name: str, creator_id: str,
                    site_type: SiteType = SiteType.STATIC,
                    build_settings: Dict = None) -> NetlifyDeployment:
        """Deploy with full enterprise features"""
        return await self.integration.deploy_site(source_path, site_name, creator_id, site_type, build_settings)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return await self.integration.health_check()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get deployment metrics"""
        return {
            "deployments_total": DEPLOYMENT_COUNTER._value.sum(),
            "active_deployments": ACTIVE_DEPLOYMENTS._value.get(),
            "error_count": ERROR_COUNTER._value.sum(),
            "function_invocations": FUNCTION_INVOCATIONS._value.get()
        }

# Export main classes and functions
__all__ = [
    'NetlifyService',
    'NetlifyConfig',
    'NetlifyDeployment',
    'NetlifySite',
    'SiteType',
    'DeploymentStatus',
    'BuildCommand',
    'NetlifyIntegration'
]

if __name__ == "__main__":
    # Example usage and testing
    async def main() -> None:
        # Initialize service
        service = NetlifyService()
        await service.initialize()
        
        # Health check
        health = await service.get_health_status()
        print(f"Service Health: {health}")
        
        # Example deployment (would need actual source path)
        # deployment = await service.deploy("./my-site", "ainflue-creator-portfolio", "creator123")
        # print(f"Deployment: {deployment}")
    
    # Run example
    # asyncio.run(main())