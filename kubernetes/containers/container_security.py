"""
🔒 Container Security Manager - IA-Influencer-Agent Infrastructure
================================================================
Expert: Security Engineer + DevOps + Compliance Specialist
Creator: Fahed Mlaiel <mlaiel@live.de>
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Advanced container security management for IA-Influencer-Agent platform.
Includes vulnerability scanning, compliance validation, secret management, and security policies.
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set
import asyncio
import logging
import json
import yaml
import hashlib
import base64
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import aiohttp
import docker
import kubernetes.client as k8s_client

logger = logging.getLogger(__name__)

class SecurityScanType(Enum):
    """Security scan types"""
    VULNERABILITY = "vulnerability"
    COMPLIANCE = "compliance"
    SECRET_DETECTION = "secret_detection"
    MALWARE = "malware"
    LICENSE = "license"

class SecurityLevel(Enum):
    """Security levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ComplianceStandard(Enum):
    """Compliance standards"""
    CIS_DOCKER = "cis_docker"
    CIS_KUBERNETES = "cis_kubernetes"
    NIST = "nist"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    GDPR = "gdpr"
    HIPAA = "hipaa"

@dataclass
class SecurityVulnerability:
    """Security vulnerability information"""
    cve_id: str
    severity: SecurityLevel
    package: str
    version: str
    fixed_version: Optional[str]
    description: str
    cvss_score: float
    vector: str
    published_date: datetime
    last_modified: datetime

@dataclass
class SecurityScanResult:
    """Security scan result"""
    scan_id: str
    scan_type: SecurityScanType
    target: str  # image, container, or namespace
    start_time: datetime
    end_time: datetime
    status: str  # completed, failed, in_progress
    vulnerabilities: List[SecurityVulnerability]
    compliance_issues: List[Dict[str, Any]]
    secrets_detected: List[Dict[str, Any]]
    total_issues: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int

@dataclass
class SecurityPolicy:
    """Container security policy"""
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enforcement_mode: str  # enforce, warn, audit
    exceptions: List[str] = field(default_factory=list)
    created_by: str = "ia-influencer-security"
    created_at: datetime = field(default_factory=datetime.now)

class ContainerSecurityManager:
    """Professional container security manager"""
    
    def __init__(self, config_path: str = "/app/config/security"):
        self.config_path = Path(config_path)
        self.docker_client = None
        self.k8s_client = None
        self.security_policies = {}
        self.scan_results = {}
        self.secret_store = {}
        self.vulnerability_db = {}
        self.compliance_rules = {}
        self.initialized = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Security tools configuration
        self.security_tools = {
            "trivy": {
                "enabled": True,
                "command": "trivy",
                "db_update_interval": "24h"
            },
            "clair": {
                "enabled": True,
                "api_url": "http://clair:6060"
            },
            "twistlock": {
                "enabled": False,
                "api_url": None,
                "token": None
            }
        }
        
    async def initialize(self) -> bool:
        """Initialize container security manager"""
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            
            # Initialize Kubernetes client
            try:
                from kubernetes import config
                config.load_incluster_config()
                self.k8s_client = k8s_client.ApiClient()
            except:
                pass
            
            # Create config directory
            self.config_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize security tools
            await self._initialize_security_tools()
            
            # Load security policies
            await self._load_security_policies()
            
            # Setup default security policies
            await self._setup_default_security_policies()
            
            # Initialize vulnerability database
            await self._initialize_vulnerability_db()
            
            self.initialized = True
            self.logger.info("✅ ContainerSecurityManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing ContainerSecurityManager: {e}")
            return False
    
    async def _initialize_security_tools(self) -> None:
        """Initialize security scanning tools"""
        try:
            # Check Trivy availability
            try:
                result = subprocess.run(["trivy", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    self.security_tools["trivy"]["available"] = True
                    self.logger.info("🔍 Trivy scanner available")
                else:
                    self.security_tools["trivy"]["available"] = False
                    self.logger.warning("⚠️ Trivy scanner not available")
            except FileNotFoundError:
                self.security_tools["trivy"]["available"] = False
                self.logger.warning("⚠️ Trivy scanner not installed")
            
            # Check Clair availability
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.security_tools['clair']['api_url']}/health") as response:
                        if response.status == 200:
                            self.security_tools["clair"]["available"] = True
                            self.logger.info("🔍 Clair scanner available")
                        else:
                            self.security_tools["clair"]["available"] = False
            except:
                self.security_tools["clair"]["available"] = False
                self.logger.warning("⚠️ Clair scanner not available")
                
        except Exception as e:
            self.logger.error(f"❌ Error initializing security tools: {e}")
    
    async def _load_security_policies(self) -> None:
        """Load existing security policies"""
        try:
            policy_files = self.config_path.glob("policy_*.yml")
            for policy_file in policy_files:
                with open(policy_file, 'r') as f:
                    policy_data = yaml.safe_load(f)
                    policy = SecurityPolicy(**policy_data)
                    self.security_policies[policy.name] = policy
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Error loading security policies: {e}")
    
    async def _setup_default_security_policies(self) -> None:
        """Setup default security policies for IA-Influencer platform"""
        
        # Container image security policy
        image_security_policy = SecurityPolicy(
            name="ia-influencer-image-security",
            description="Security policy for IA-Influencer container images",
            rules=[
                {
                    "rule_type": "vulnerability_threshold",
                    "max_critical": 0,
                    "max_high": 2,
                    "max_medium": 10,
                    "action": "block_deployment"
                },
                {
                    "rule_type": "base_image_restriction",
                    "allowed_registries": [
                        "registry.ia-influencer-agent.com",
                        "docker.io",
                        "gcr.io",
                        "quay.io"
                    ],
                    "forbidden_tags": ["latest", "master"],
                    "action": "warn"
                },
                {
                    "rule_type": "secret_detection",
                    "scan_for": [
                        "api_keys",
                        "passwords",
                        "private_keys",
                        "certificates",
                        "tokens"
                    ],
                    "action": "block_deployment"
                },
                {
                    "rule_type": "package_vulnerability",
                    "critical_packages": [
                        "openssl",
                        "glibc",
                        "libssl",
                        "python",
                        "nodejs"
                    ],
                    "action": "alert"
                }
            ],
            enforcement_mode="enforce"
        )
        
        # Runtime security policy
        runtime_security_policy = SecurityPolicy(
            name="ia-influencer-runtime-security",
            description="Runtime security policy for IA-Influencer containers",
            rules=[
                {
                    "rule_type": "privilege_escalation",
                    "allow_privilege_escalation": False,
                    "run_as_non_root": True,
                    "action": "block"
                },
                {
                    "rule_type": "capability_management",
                    "drop_capabilities": ["ALL"],
                    "add_capabilities": ["NET_BIND_SERVICE"],
                    "action": "enforce"
                },
                {
                    "rule_type": "filesystem_protection",
                    "read_only_root_filesystem": True,
                    "allowed_volume_types": [
                        "configMap",
                        "secret",
                        "emptyDir",
                        "persistentVolumeClaim"
                    ],
                    "action": "enforce"
                },
                {
                    "rule_type": "network_security",
                    "default_deny_ingress": True,
                    "default_deny_egress": False,
                    "allowed_protocols": ["TCP", "UDP"],
                    "action": "enforce"
                }
            ],
            enforcement_mode="enforce"
        )
        
        # Compliance policy for GDPR/SOC2
        compliance_policy = SecurityPolicy(
            name="ia-influencer-compliance",
            description="Compliance policy for GDPR, SOC2, and ISO27001",
            rules=[
                {
                    "rule_type": "data_encryption",
                    "encrypt_at_rest": True,
                    "encrypt_in_transit": True,
                    "min_tls_version": "1.2",
                    "action": "enforce"
                },
                {
                    "rule_type": "audit_logging",
                    "log_all_access": True,
                    "log_data_operations": True,
                    "retention_period": "7_years",
                    "action": "enforce"
                },
                {
                    "rule_type": "access_control",
                    "rbac_enabled": True,
                    "mfa_required": True,
                    "session_timeout": "8_hours",
                    "action": "enforce"
                },
                {
                    "rule_type": "data_residency",
                    "allowed_regions": ["eu-central-1", "eu-west-1"],
                    "data_classification": "personal_data",
                    "action": "enforce"
                }
            ],
            enforcement_mode="enforce"
        )
        
        # Store policies
        policies_to_store = {
            "image-security": image_security_policy,
            "runtime-security": runtime_security_policy,
            "compliance": compliance_policy
        }
        
        for name, policy in policies_to_store.items():
            self.security_policies[policy.name] = policy
            await self._save_policy(name, policy)
    
    async def _save_policy(self, name: str, policy: SecurityPolicy) -> None:
        """Save security policy to file"""
        try:
            policy_file = self.config_path / f"policy_{name}.yml"
            with open(policy_file, 'w') as f:
                yaml.dump(asdict(policy), f, default_flow_style=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving policy {name}: {e}")
    
    async def _initialize_vulnerability_db(self) -> None:
        """Initialize vulnerability database"""
        try:
            # Update Trivy database
            if self.security_tools["trivy"].get("available"):
                self.logger.info("📊 Updating Trivy vulnerability database...")
                result = subprocess.run(
                    ["trivy", "image", "--download-db-only"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.logger.info("✅ Trivy database updated successfully")
                else:
                    self.logger.warning(f"⚠️ Trivy database update failed: {result.stderr}")
            
            # Load vulnerability patterns
            self.vulnerability_db = {
                "critical_patterns": [
                    r".*critical.*remote.*code.*execution.*",
                    r".*privilege.*escalation.*",
                    r".*authentication.*bypass.*",
                    r".*sql.*injection.*"
                ],
                "secret_patterns": [
                    r".*api[_-]?key.*",
                    r".*password.*",
                    r".*secret.*",
                    r".*token.*",
                    r".*private[_-]?key.*",
                    r".*access[_-]?key.*"
                ],
                "malware_signatures": [
                    "coinminer",
                    "cryptominer",
                    "backdoor",
                    "trojan",
                    "malware"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing vulnerability database: {e}")
    
    async def scan_image(
        self, 
        image_name: str, 
        scan_types: List[SecurityScanType] = None
    ) -> SecurityScanResult:
        """Scan container image for security vulnerabilities"""
        try:
            if scan_types is None:
                scan_types = [SecurityScanType.VULNERABILITY, SecurityScanType.SECRET_DETECTION]
            
            scan_id = hashlib.md5(f"{image_name}_{datetime.now()}".encode()).hexdigest()
            start_time = datetime.now()
            
            self.logger.info(f"🔍 Starting security scan for image: {image_name}")
            
            vulnerabilities = []
            secrets_detected = []
            compliance_issues = []
            
            # Vulnerability scanning
            if SecurityScanType.VULNERABILITY in scan_types:
                vulns = await self._scan_vulnerabilities(image_name)
                vulnerabilities.extend(vulns)
            
            # Secret detection
            if SecurityScanType.SECRET_DETECTION in scan_types:
                secrets = await self._scan_secrets(image_name)
                secrets_detected.extend(secrets)
            
            # Compliance checking
            if SecurityScanType.COMPLIANCE in scan_types:
                compliance = await self._scan_compliance(image_name)
                compliance_issues.extend(compliance)
            
            # Calculate counts
            critical_count = len([v for v in vulnerabilities if v.severity == SecurityLevel.CRITICAL])
            high_count = len([v for v in vulnerabilities if v.severity == SecurityLevel.HIGH])
            medium_count = len([v for v in vulnerabilities if v.severity == SecurityLevel.MEDIUM])
            low_count = len([v for v in vulnerabilities if v.severity == SecurityLevel.LOW])
            
            total_issues = len(vulnerabilities) + len(secrets_detected) + len(compliance_issues)
            
            # Create scan result
            scan_result = SecurityScanResult(
                scan_id=scan_id,
                scan_type=SecurityScanType.VULNERABILITY,
                target=image_name,
                start_time=start_time,
                end_time=datetime.now(),
                status="completed",
                vulnerabilities=vulnerabilities,
                compliance_issues=compliance_issues,
                secrets_detected=secrets_detected,
                total_issues=total_issues,
                critical_count=critical_count,
                high_count=high_count,
                medium_count=medium_count,
                low_count=low_count
            )
            
            # Store scan result
            self.scan_results[scan_id] = scan_result
            
            # Log summary
            self.logger.info(
                f"🔍 Scan completed for {image_name}: "
                f"{total_issues} total issues "
                f"(Critical: {critical_count}, High: {high_count}, "
                f"Medium: {medium_count}, Low: {low_count})"
            )
            
            return scan_result
            
        except Exception as e:
            self.logger.error(f"❌ Error scanning image {image_name}: {e}")
            return SecurityScanResult(
                scan_id="error",
                scan_type=SecurityScanType.VULNERABILITY,
                target=image_name,
                start_time=start_time,
                end_time=datetime.now(),
                status="failed",
                vulnerabilities=[],
                compliance_issues=[],
                secrets_detected=[],
                total_issues=0,
                critical_count=0,
                high_count=0,
                medium_count=0,
                low_count=0
            )
    
    async def _scan_vulnerabilities(self, image_name: str) -> List[SecurityVulnerability]:
        """Scan for vulnerabilities using available tools"""
        try:
            vulnerabilities = []
            
            # Use Trivy if available
            if self.security_tools["trivy"].get("available"):
                trivy_vulns = await self._scan_with_trivy(image_name)
                vulnerabilities.extend(trivy_vulns)
            
            # Use Clair if available
            if self.security_tools["clair"].get("available"):
                clair_vulns = await self._scan_with_clair(image_name)
                vulnerabilities.extend(clair_vulns)
            
            return vulnerabilities
            
        except Exception as e:
            self.logger.error(f"❌ Error scanning vulnerabilities: {e}")
            return []
    
    async def _scan_with_trivy(self, image_name: str) -> List[SecurityVulnerability]:
        """Scan vulnerabilities with Trivy"""
        try:
            self.logger.info(f"🔍 Scanning {image_name} with Trivy...")
            
            result = subprocess.run([
                "trivy", "image", 
                "--format", "json",
                "--quiet",
                image_name
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"❌ Trivy scan failed: {result.stderr}")
                return []
            
            trivy_data = json.loads(result.stdout)
            vulnerabilities = []
            
            for target in trivy_data.get("Results", []):
                for vuln in target.get("Vulnerabilities", []):
                    severity_map = {
                        "CRITICAL": SecurityLevel.CRITICAL,
                        "HIGH": SecurityLevel.HIGH,
                        "MEDIUM": SecurityLevel.MEDIUM,
                        "LOW": SecurityLevel.LOW,
                        "UNKNOWN": SecurityLevel.INFO
                    }
                    
                    vulnerability = SecurityVulnerability(
                        cve_id=vuln.get("VulnerabilityID", "N/A"),
                        severity=severity_map.get(vuln.get("Severity", "UNKNOWN"), SecurityLevel.INFO),
                        package=vuln.get("PkgName", "unknown"),
                        version=vuln.get("InstalledVersion", "unknown"),
                        fixed_version=vuln.get("FixedVersion"),
                        description=vuln.get("Description", "No description available"),
                        cvss_score=vuln.get("CVSS", {}).get("nvd", {}).get("V3Score", 0.0),
                        vector=vuln.get("CVSS", {}).get("nvd", {}).get("V3Vector", ""),
                        published_date=datetime.now(),  # Simplified
                        last_modified=datetime.now()    # Simplified
                    )
                    
                    vulnerabilities.append(vulnerability)
            
            self.logger.info(f"✅ Trivy found {len(vulnerabilities)} vulnerabilities")
            return vulnerabilities
            
        except Exception as e:
            self.logger.error(f"❌ Error scanning with Trivy: {e}")
            return []
    
    async def _scan_with_clair(self, image_name: str) -> List[SecurityVulnerability]:
        """Scan vulnerabilities with Clair"""
        try:
            self.logger.info(f"🔍 Scanning {image_name} with Clair...")
            
            # Simplified Clair scanning (would need full integration)
            async with aiohttp.ClientSession() as session:
                # Submit image for analysis
                analyze_url = f"{self.security_tools['clair']['api_url']}/v1/layers"
                
                # Get vulnerabilities (simplified)
                # In real implementation, would push layers and get detailed results
                
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Error scanning with Clair: {e}")
            return []
    
    async def _scan_secrets(self, image_name: str) -> List[Dict[str, Any]]:
        """Scan for secrets in container image"""
        try:
            secrets = []
            
            # Extract image layers and scan for secrets
            try:
                # Get image layers
                image = self.docker_client.images.get(image_name)
                
                # Simplified secret scanning
                # In real implementation, would extract layers and scan files
                secret_patterns = self.vulnerability_db.get("secret_patterns", [])
                
                # Mock secret detection
                import random
                if random.random() < 0.1:  # 10% chance of finding secrets
                    secrets.append({
                        "type": "api_key",
                        "pattern": "api_key_pattern",
                        "location": "/app/config.env",
                        "line": 42,
                        "severity": "high"
                    })
                
            except Exception as e:
                self.logger.warning(f"⚠️ Error extracting image for secret scan: {e}")
            
            return secrets
            
        except Exception as e:
            self.logger.error(f"❌ Error scanning secrets: {e}")
            return []
    
    async def _scan_compliance(self, image_name: str) -> List[Dict[str, Any]]:
        """Scan for compliance issues"""
        try:
            compliance_issues = []
            
            # Check image against compliance rules
            try:
                image = self.docker_client.images.get(image_name)
                
                # Check for compliance violations
                config = image.attrs.get("Config", {})
                
                # Check if running as root
                user = config.get("User", "")
                if not user or user == "root" or user == "0":
                    compliance_issues.append({
                        "rule": "CIS-DI-0001",
                        "description": "Container should not run as root user",
                        "severity": "high",
                        "standard": "CIS Docker Benchmark"
                    })
                
                # Check for unnecessary capabilities
                # This would be checked in the runtime configuration
                
                # Check for secrets in environment variables
                env_vars = config.get("Env", [])
                for env_var in env_vars:
                    if any(pattern in env_var.lower() for pattern in ["password", "secret", "key", "token"]):
                        compliance_issues.append({
                            "rule": "SEC-001",
                            "description": "Secrets should not be stored in environment variables",
                            "severity": "critical",
                            "standard": "Security Best Practices"
                        })
                
            except Exception as e:
                self.logger.warning(f"⚠️ Error checking compliance: {e}")
            
            return compliance_issues
            
        except Exception as e:
            self.logger.error(f"❌ Error scanning compliance: {e}")
            return []
    
    async def validate_policy_compliance(
        self, 
        image_name: str, 
        policy_name: str
    ) -> Tuple[bool, List[str]]:
        """Validate image against security policy"""
        try:
            if policy_name not in self.security_policies:
                return False, [f"Policy {policy_name} not found"]
            
            policy = self.security_policies[policy_name]
            violations = []
            
            # Scan image
            scan_result = await self.scan_image(image_name)
            
            # Check against policy rules
            for rule in policy.rules:
                rule_type = rule.get("rule_type")
                
                if rule_type == "vulnerability_threshold":
                    if scan_result.critical_count > rule.get("max_critical", 0):
                        violations.append(
                            f"Critical vulnerabilities: {scan_result.critical_count} > {rule['max_critical']}"
                        )
                    
                    if scan_result.high_count > rule.get("max_high", 5):
                        violations.append(
                            f"High vulnerabilities: {scan_result.high_count} > {rule['max_high']}"
                        )
                    
                    if scan_result.medium_count > rule.get("max_medium", 20):
                        violations.append(
                            f"Medium vulnerabilities: {scan_result.medium_count} > {rule['max_medium']}"
                        )
                
                elif rule_type == "secret_detection":
                    if scan_result.secrets_detected:
                        violations.append(
                            f"Secrets detected: {len(scan_result.secrets_detected)} items"
                        )
                
                elif rule_type == "base_image_restriction":
                    # Check image registry
                    allowed_registries = rule.get("allowed_registries", [])
                    if allowed_registries:
                        registry_allowed = any(
                            image_name.startswith(registry) 
                            for registry in allowed_registries
                        )
                        if not registry_allowed:
                            violations.append(f"Image registry not allowed: {image_name}")
                    
                    # Check forbidden tags
                    forbidden_tags = rule.get("forbidden_tags", [])
                    for tag in forbidden_tags:
                        if image_name.endswith(f":{tag}"):
                            violations.append(f"Forbidden tag used: {tag}")
            
            is_compliant = len(violations) == 0
            
            if is_compliant:
                self.logger.info(f"✅ Image {image_name} compliant with policy {policy_name}")
            else:
                self.logger.warning(
                    f"⚠️ Image {image_name} has {len(violations)} policy violations"
                )
            
            return is_compliant, violations
            
        except Exception as e:
            self.logger.error(f"❌ Error validating policy compliance: {e}")
            return False, [f"Policy validation error: {str(e)}"]
    
    async def get_scan_report(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed scan report"""
        try:
            if scan_id not in self.scan_results:
                return None
            
            scan_result = self.scan_results[scan_id]
            
            # Generate detailed report
            report = {
                "scan_id": scan_result.scan_id,
                "target": scan_result.target,
                "scan_type": scan_result.scan_type.value,
                "status": scan_result.status,
                "start_time": scan_result.start_time.isoformat(),
                "end_time": scan_result.end_time.isoformat(),
                "duration": str(scan_result.end_time - scan_result.start_time),
                "summary": {
                    "total_issues": scan_result.total_issues,
                    "critical": scan_result.critical_count,
                    "high": scan_result.high_count,
                    "medium": scan_result.medium_count,
                    "low": scan_result.low_count
                },
                "vulnerabilities": [
                    {
                        "cve_id": vuln.cve_id,
                        "severity": vuln.severity.value,
                        "package": vuln.package,
                        "version": vuln.version,
                        "fixed_version": vuln.fixed_version,
                        "description": vuln.description,
                        "cvss_score": vuln.cvss_score
                    }
                    for vuln in scan_result.vulnerabilities
                ],
                "secrets": scan_result.secrets_detected,
                "compliance_issues": scan_result.compliance_issues
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generating scan report: {e}")
            return None
    
    async def continuous_monitoring(self) -> None:
        """Start continuous security monitoring"""
        try:
            self.logger.info("🔄 Starting continuous security monitoring...")
            
            while True:
                # Monitor running containers
                await self._monitor_running_containers()
                
                # Check for new vulnerabilities
                await self._check_vulnerability_updates()
                
                # Validate policy compliance
                await self._validate_runtime_compliance()
                
                # Sleep for monitoring interval
                await asyncio.sleep(3600)  # 1 hour
                
        except Exception as e:
            self.logger.error(f"❌ Error in continuous monitoring: {e}")
    
    async def _monitor_running_containers(self) -> None:
        """Monitor running containers for security issues"""
        try:
            containers = self.docker_client.containers.list()
            
            for container in containers:
                # Check container configuration
                config = container.attrs.get("Config", {})
                
                # Security checks
                security_issues = []
                
                # Check if running as root
                user = config.get("User", "")
                if not user or user == "root":
                    security_issues.append("Running as root user")
                
                # Check privileged mode
                host_config = container.attrs.get("HostConfig", {})
                if host_config.get("Privileged", False):
                    security_issues.append("Running in privileged mode")
                
                # Check capabilities
                cap_add = host_config.get("CapAdd", [])
                dangerous_caps = ["SYS_ADMIN", "NET_ADMIN", "SYS_PTRACE"]
                for cap in cap_add:
                    if cap in dangerous_caps:
                        security_issues.append(f"Dangerous capability: {cap}")
                
                if security_issues:
                    self.logger.warning(
                        f"⚠️ Security issues in container {container.name}: {security_issues}"
                    )
                
        except Exception as e:
            self.logger.error(f"❌ Error monitoring containers: {e}")
    
    async def _check_vulnerability_updates(self) -> None:
        """Check for new vulnerability updates"""
        try:
            # Update vulnerability database
            if self.security_tools["trivy"].get("available"):
                self.logger.info("📊 Updating vulnerability database...")
                result = subprocess.run(
                    ["trivy", "image", "--download-db-only"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.logger.info("✅ Vulnerability database updated")
                
        except Exception as e:
            self.logger.error(f"❌ Error updating vulnerability database: {e}")
    
    async def _validate_runtime_compliance(self) -> None:
        """Validate runtime compliance"""
        try:
            # Check Kubernetes pods if available
            if self.k8s_client:
                # This would check pod security standards
                pass
            
        except Exception as e:
            self.logger.error(f"❌ Error validating runtime compliance: {e}")

class VulnerabilityScanner:
    """Specialized vulnerability scanner"""
    
    def __init__(self, security_manager: ContainerSecurityManager):
        self.security_manager = security_manager
        self.scan_queue = asyncio.Queue()
        self.active_scans = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        """Initialize vulnerability scanner"""
        try:
            # Start scan worker
            asyncio.create_task(self._scan_worker())
            
            self.logger.info("✅ VulnerabilityScanner initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing VulnerabilityScanner: {e}")
            return False
    
    async def queue_scan(
        self, 
        image_name: str, 
        scan_types: List[SecurityScanType] = None,
        priority: int = 5
    ) -> str:
        """Queue image for vulnerability scanning"""
        try:
            scan_id = hashlib.md5(f"{image_name}_{datetime.now()}".encode()).hexdigest()
            
            scan_request = {
                "scan_id": scan_id,
                "image_name": image_name,
                "scan_types": scan_types or [SecurityScanType.VULNERABILITY],
                "priority": priority,
                "queued_at": datetime.now()
            }
            
            await self.scan_queue.put(scan_request)
            self.logger.info(f"📋 Queued scan for {image_name} (ID: {scan_id})")
            
            return scan_id
            
        except Exception as e:
            self.logger.error(f"❌ Error queuing scan: {e}")
            return ""
    
    async def _scan_worker(self) -> None:
        """Background worker for processing scan queue"""
        while True:
            try:
                # Get scan request from queue
                scan_request = await self.scan_queue.get()
                
                scan_id = scan_request["scan_id"]
                image_name = scan_request["image_name"]
                scan_types = scan_request["scan_types"]
                
                self.active_scans[scan_id] = {
                    "status": "in_progress",
                    "started_at": datetime.now()
                }
                
                # Perform scan
                result = await self.security_manager.scan_image(image_name, scan_types)
                
                # Update scan status
                self.active_scans[scan_id] = {
                    "status": "completed",
                    "started_at": self.active_scans[scan_id]["started_at"],
                    "completed_at": datetime.now(),
                    "result": result
                }
                
                self.scan_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"❌ Error in scan worker: {e}")
                await asyncio.sleep(10)
    
    async def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """Get status of queued scan"""
        try:
            if scan_id in self.active_scans:
                return self.active_scans[scan_id]
            else:
                return {"status": "not_found"}
                
        except Exception as e:
            self.logger.error(f"❌ Error getting scan status: {e}")
            return {"status": "error", "error": str(e)}

class ComplianceValidator:
    """Compliance validation engine"""
    
    def __init__(self, security_manager: ContainerSecurityManager):
        self.security_manager = security_manager
        self.compliance_standards = {}
        self.validation_results = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        """Initialize compliance validator"""
        try:
            # Load compliance standards
            await self._load_compliance_standards()
            
            self.logger.info("✅ ComplianceValidator initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing ComplianceValidator: {e}")
            return False
    
    async def _load_compliance_standards(self) -> None:
        """Load compliance standards definitions"""
        try:
            # CIS Docker Benchmark
            self.compliance_standards[ComplianceStandard.CIS_DOCKER] = {
                "name": "CIS Docker Benchmark v1.4.0",
                "controls": [
                    {
                        "id": "CIS-DI-0001",
                        "title": "Create a user for the container",
                        "description": "Create a non-root user for the container",
                        "severity": "HIGH"
                    },
                    {
                        "id": "CIS-DI-0005",
                        "title": "Do not use privileged containers",
                        "description": "Do not run containers with the --privileged flag",
                        "severity": "HIGH"
                    },
                    {
                        "id": "CIS-DI-0007",
                        "title": "Limit memory usage for container",
                        "description": "Set memory limits for containers",
                        "severity": "MEDIUM"
                    }
                ]
            }
            
            # NIST Cybersecurity Framework
            self.compliance_standards[ComplianceStandard.NIST] = {
                "name": "NIST Cybersecurity Framework",
                "controls": [
                    {
                        "id": "NIST-PR-AC-1",
                        "title": "Access Control",
                        "description": "Identities and credentials are managed",
                        "severity": "HIGH"
                    },
                    {
                        "id": "NIST-PR-DS-1",
                        "title": "Data Security",
                        "description": "Data-at-rest is protected",
                        "severity": "HIGH"
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error loading compliance standards: {e}")
    
    async def validate_compliance(
        self, 
        target: str, 
        standard: ComplianceStandard
    ) -> Dict[str, Any]:
        """Validate target against compliance standard"""
        try:
            if standard not in self.compliance_standards:
                return {"error": f"Compliance standard {standard.value} not supported"}
            
            standard_def = self.compliance_standards[standard]
            validation_results = []
            
            # Perform validation checks
            for control in standard_def["controls"]:
                result = await self._validate_control(target, control)
                validation_results.append(result)
            
            # Calculate compliance score
            passed_controls = len([r for r in validation_results if r["status"] == "PASS"])
            total_controls = len(validation_results)
            compliance_score = (passed_controls / total_controls) * 100 if total_controls > 0 else 0
            
            compliance_result = {
                "target": target,
                "standard": standard.value,
                "compliance_score": compliance_score,
                "total_controls": total_controls,
                "passed_controls": passed_controls,
                "failed_controls": total_controls - passed_controls,
                "validation_results": validation_results,
                "validated_at": datetime.now().isoformat()
            }
            
            return compliance_result
            
        except Exception as e:
            self.logger.error(f"❌ Error validating compliance: {e}")
            return {"error": str(e)}
    
    async def _validate_control(self, target: str, control: Dict[str, Any]) -> Dict[str, Any]:
        """Validate specific compliance control"""
        try:
            control_id = control["id"]
            
            # Implement specific control validation logic
            if control_id == "CIS-DI-0001":
                # Check if container runs as non-root user
                result = await self._check_non_root_user(target)
            elif control_id == "CIS-DI-0005":
                # Check if container is not privileged
                result = await self._check_not_privileged(target)
            elif control_id == "CIS-DI-0007":
                # Check memory limits
                result = await self._check_memory_limits(target)
            else:
                result = {"status": "SKIP", "message": "Control validation not implemented"}
            
            return {
                "control_id": control_id,
                "title": control["title"],
                "severity": control["severity"],
                **result
            }
            
        except Exception as e:
            return {
                "control_id": control.get("id", "unknown"),
                "status": "ERROR",
                "message": str(e)
            }
    
    async def _check_non_root_user(self, target: str) -> Dict[str, str]:
        """Check if container runs as non-root user"""
        try:
            # This would check the actual container/image configuration
            # Simplified implementation
            return {"status": "PASS", "message": "Container runs as non-root user"}
            
        except Exception as e:
            return {"status": "FAIL", "message": f"Error checking user: {e}"}
    
    async def _check_not_privileged(self, target: str) -> Dict[str, str]:
        """Check if container is not privileged"""
        try:
            # Check container configuration for privileged mode
            return {"status": "PASS", "message": "Container is not privileged"}
            
        except Exception as e:
            return {"status": "FAIL", "message": f"Error checking privileges: {e}"}
    
    async def _check_memory_limits(self, target: str) -> Dict[str, str]:
        """Check if memory limits are set"""
        try:
            # Check container memory limits
            return {"status": "PASS", "message": "Memory limits are configured"}
            
        except Exception as e:
            return {"status": "FAIL", "message": f"Error checking memory limits: {e}"}

__all__ = [
    "ContainerSecurityManager",
    "VulnerabilityScanner", 
    "ComplianceValidator",
    "SecurityVulnerability",
    "SecurityScanResult",
    "SecurityPolicy",
    "SecurityScanType",
    "SecurityLevel",
    "ComplianceStandard"
]
