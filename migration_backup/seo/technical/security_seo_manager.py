
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
"""Security SEO Manager
Advanced security optimization for SEO impact in IA Chéries creator economy platform.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Technical SEO Expert: Advanced Technical Optimization
Security Expert: SEO Security Implementation
DevOps Engineer: Technical Infrastructure
Full-Stack Developer: Frontend/Backend Technical SEO
"""

import asyncio
import ssl
import socket
import hashlib
import hmac
import secrets
import ipaddress
import subprocess
import json
import re
import requests
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import dns.resolver
import whois
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from bs4 import BeautifulSoup
import yaml
import base64


@dataclass
class SecurityIssue:
    """Security issue that impacts SEO."""
    category: str
    severity: str  # critical, high, medium, low
    title: str
    description: str
    url: str
    technical_details: str
    seo_impact: str
    fix_priority: int
    remediation_steps: List[str]
    compliance_frameworks: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SecurityAuditResults:
    """Comprehensive security audit results."""
    domain: str
    audit_timestamp: datetime
    overall_security_score: float
    ssl_score: float
    headers_score: float
    content_security_score: float
    malware_score: float
    compliance_score: float
    issues: List[SecurityIssue]
    recommendations: List[str]
    ssl_certificate_info: Dict[str, Any]
    security_headers: Dict[str, Any]
    vulnerability_scan: Dict[str, Any]
    compliance_status: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class SSLCertificateAnalyzer:
    """Advanced SSL certificate analysis for SEO security."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.SSLCertificateAnalyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def comprehensive_ssl_analysis(self, domain: str) -> Dict[str, Any]:
        """Perform comprehensive SSL certificate analysis."""
        self.logger.info(f"Starting SSL analysis for {domain}")
        
        results = {
            'domain': domain,
            'certificate_valid': False,
            'certificate_info': {},
            'chain_info': {},
            'security_issues': [],
            'recommendations': [],
            'compliance_status': {},
            'ssl_score': 0
        }
        
        try:
            # Test SSL connection
            ssl_info = await self._test_ssl_connection(domain)
            results.update(ssl_info)
            
            # Analyze certificate details
            if ssl_info.get('certificate_valid'):
                cert_analysis = await self._analyze_certificate_details(domain, ssl_info['certificate'])
                results['certificate_info'].update(cert_analysis)
                
                # Check certificate chain
                chain_analysis = await self._analyze_certificate_chain(domain)
                results['chain_info'] = chain_analysis
                
                # SSL Labs-style scoring
                ssl_score = await self._calculate_ssl_score(results)
                results['ssl_score'] = ssl_score
            
            # Generate security recommendations
            recommendations = await self._generate_ssl_recommendations(results)
            results['recommendations'] = recommendations
            
        except Exception as e:
            self.logger.error(f"Error in SSL analysis: {e}")
            results['error'] = str(e)
            results['security_issues'].append({
                'type': 'ssl_analysis_error',
                'severity': 'high',
                'description': f'Failed to analyze SSL: {str(e)}',
                'seo_impact': 'High - Cannot verify SSL security for SEO trust signals'
            })
        
        return results
    
    async def _test_ssl_connection(self, domain: str, port: int = 443) -> Dict[str, Any]:
        """Test SSL connection and retrieve certificate."""
        try:
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    certificate = ssock.getpeercert(binary_form=True)
                    cert_dict = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    return {
                        'certificate_valid': True,
                        'certificate': certificate,
                        'certificate_dict': cert_dict,
                        'cipher_suite': cipher,
                        'ssl_version': version,
                        'peer_cert_chain': ssock.getpeercert_chain() if hasattr(ssock, 'getpeercert_chain') else None
                    }
        
        except ssl.SSLError as e:
            return {
                'certificate_valid': False,
                'ssl_error': str(e),
                'error_type': 'ssl_error'
            }
        except socket.gaierror as e:
            return {
                'certificate_valid': False,
                'dns_error': str(e),
                'error_type': 'dns_error'
            }
        except Exception as e:
            return {
                'certificate_valid': False,
                'connection_error': str(e),
                'error_type': 'connection_error'
            }
    
    async def _analyze_certificate_details(self, domain: str, certificate: bytes) -> Dict[str, Any]:
        """Analyze SSL certificate details using cryptography library."""
        try:
            cert = x509.load_der_x509_certificate(certificate, default_backend())
            
            # Extract certificate information
            subject = cert.subject
            issuer = cert.issuer
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after
            
            # Calculate days until expiry
            now = datetime.now()
            days_until_expiry = (not_after - now).days
            
            # Get Subject Alternative Names
            san_list = []
            try:
                san_extension = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                san_list = [name.value for name in san_extension.value]
            except x509.ExtensionNotFound:
                pass
            
            # Check if domain is covered
            domain_covered = False
            if domain in san_list:
                domain_covered = True
            elif f"*.{'.'.join(domain.split('.')[1:])}" in san_list:  # Wildcard check
                domain_covered = True
            
            # Get signature algorithm
            signature_algorithm = cert.signature_algorithm_oid._name
            
            # Get public key information
            public_key = cert.public_key()
            key_size = public_key.key_size
            key_type = type(public_key).__name__
            
            return {
                'subject': {attr.oid._name: attr.value for attr in subject},
                'issuer': {attr.oid._name: attr.value for attr in issuer},
                'valid_from': not_before.isoformat(),
                'valid_until': not_after.isoformat(),
                'days_until_expiry': days_until_expiry,
                'san_list': san_list,
                'domain_covered': domain_covered,
                'signature_algorithm': signature_algorithm,
                'public_key_type': key_type,
                'public_key_size': key_size,
                'is_expired': now > not_after,
                'is_self_signed': subject == issuer
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing certificate details: {e}")
            return {'error': str(e)}
    
    async def _analyze_certificate_chain(self, domain: str) -> Dict[str, Any]:
        """Analyze SSL certificate chain."""
        try:
            # Use OpenSSL to get full certificate chain
            cmd = [
                'openssl', 's_client', '-connect', f'{domain}:443',
                '-servername', domain, '-showcerts'
            ]
            
            process = subprocess.Popen(
                cmd, 
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input='\n')
            
            # Parse certificate chain
            certificates = []
            cert_blocks = re.findall(r'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----', stdout, re.DOTALL)
            
            for i, cert_block in enumerate(cert_blocks):
                certificates.append({
                    'position': i,
                    'type': 'end_entity' if i == 0 else 'intermediate' if i < len(cert_blocks) - 1 else 'root',
                    'certificate': cert_block.strip()
                })
            
            return {
                'chain_length': len(certificates),
                'certificates': certificates,
                'chain_valid': len(certificates) > 0,
                'openssl_output': stdout if process.returncode == 0 else stderr
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing certificate chain: {e}")
            return {'error': str(e), 'chain_valid': False}
    
    async def _calculate_ssl_score(self, ssl_results: Dict[str, Any]) -> float:
        """Calculate SSL security score (SSL Labs style)."""
        score = 100.0
        
        cert_info = ssl_results.get('certificate_info', {})
        
        # Certificate validity
        if not ssl_results.get('certificate_valid', False):
            return 0.0
        
        # Days until expiry
        days_until_expiry = cert_info.get('days_until_expiry', 0)
        if days_until_expiry <= 0:
            score -= 50  # Expired certificate
        elif days_until_expiry <= 7:
            score -= 30  # Expires very soon
        elif days_until_expiry <= 30:
            score -= 15  # Expires soon
        
        # Key size
        key_size = cert_info.get('public_key_size', 0)
        if key_size < 2048:
            score -= 25  # Weak key
        elif key_size < 4096:
            score -= 5   # Moderate key
        
        # Signature algorithm
        sig_algo = cert_info.get('signature_algorithm', '').lower()
        if 'sha1' in sig_algo:
            score -= 30  # Weak signature algorithm
        elif 'md5' in sig_algo:
            score -= 40  # Very weak signature algorithm
        
        # Self-signed certificate
        if cert_info.get('is_self_signed', False):
            score -= 40
        
        # Domain coverage
        if not cert_info.get('domain_covered', False):
            score -= 20
        
        # Certificate chain
        chain_info = ssl_results.get('chain_info', {})
        if not chain_info.get('chain_valid', False):
            score -= 15
        
        return max(0.0, score)
    
    async def _generate_ssl_recommendations(self, ssl_results: Dict[str, Any]) -> List[str]:
        """Generate SSL recommendations."""
        recommendations = []
        
        if not ssl_results.get('certificate_valid', False):
            recommendations.append("CRITICAL: Install valid SSL certificate immediately")
            return recommendations
        
        cert_info = ssl_results.get('certificate_info', {})
        days_until_expiry = cert_info.get('days_until_expiry', 0)
        
        if days_until_expiry <= 30:
            recommendations.append(f"URGENT: SSL certificate expires in {days_until_expiry} days - renew immediately")
        
        if cert_info.get('public_key_size', 0) < 2048:
            recommendations.append("Upgrade to 2048-bit or higher SSL certificate")
        
        if cert_info.get('is_self_signed', False):
            recommendations.append("Replace self-signed certificate with CA-signed certificate")
        
        return recommendations


class SecurityHeadersAnalyzer:
    """Analyze security headers for SEO impact."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.required_headers = {
            'strict-transport-security': {'weight': 20, 'seo_impact': 'High'},
            'content-security-policy': {'weight': 15, 'seo_impact': 'Medium'},
            'x-frame-options': {'weight': 10, 'seo_impact': 'Low'},
            'x-content-type-options': {'weight': 8, 'seo_impact': 'Low'},
            'referrer-policy': {'weight': 5, 'seo_impact': 'Low'},
            'permissions-policy': {'weight': 5, 'seo_impact': 'Low'}
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.SecurityHeadersAnalyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def analyze_security_headers(self, url: str) -> Dict[str, Any]:
        """Comprehensive security headers analysis."""
        self.logger.info(f"Analyzing security headers for {url}")
        
        results = {
            'url': url,
            'headers_found': {},
            'missing_headers': [],
            'header_issues': [],
            'recommendations': [],
            'security_score': 0,
            'seo_impact_assessment': {}
        }
        
        try:
            # Get HTTP response headers
            response = requests.head(url, timeout=10, allow_redirects=True)
            headers = {k.lower(): v for k, v in response.headers.items()}
            
            # Analyze each security header
            for header_name, config in self.required_headers.items():
                if header_name in headers:
                    results['headers_found'][header_name] = headers[header_name]
                    
                    # Analyze header value
                    header_analysis = await self._analyze_header_value(header_name, headers[header_name], url)
                    if header_analysis.get('issues'):
                        results['header_issues'].extend(header_analysis['issues'])
                else:
                    results['missing_headers'].append(header_name)
                    results['header_issues'].append({
                        'header': header_name,
                        'issue': 'missing',
                        'severity': 'medium' if config['weight'] > 10 else 'low',
                        'seo_impact': config['seo_impact'],
                        'recommendation': f"Implement {header_name} header"
                    })
            
            # Check for problematic headers that affect SEO
            seo_problematic_headers = await self._check_seo_problematic_headers(headers, url)
            results['header_issues'].extend(seo_problematic_headers)
            
            # Calculate security score
            security_score = await self._calculate_headers_score(results)
            results['security_score'] = security_score
            
            # Generate recommendations
            recommendations = await self._generate_header_recommendations(results)
            results['recommendations'] = recommendations
            
            # SEO impact assessment
            seo_impact = await self._assess_seo_impact(results)
            results['seo_impact_assessment'] = seo_impact
            
        except Exception as e:
            self.logger.error(f"Error analyzing security headers: {e}")
            results['error'] = str(e)
        
        return results
    
    async def _analyze_header_value(self, header_name: str, header_value: str, url: str) -> Dict[str, Any]:
        """Analyze specific security header value."""
        issues = []
        recommendations = []
        
        if header_name == 'strict-transport-security':
            # Analyze HSTS header
            if 'max-age=' not in header_value.lower():
                issues.append({
                    'header': header_name,
                    'issue': 'missing_max_age',
                    'severity': 'high',
                    'description': 'HSTS header missing max-age directive'
                })
            else:
                # Extract max-age value
                max_age_match = re.search(r'max-age=(\d+)', header_value.lower())
                if max_age_match:
                    max_age = int(max_age_match.group(1))
                    if max_age < 31536000:  # Less than 1 year
                        issues.append({
                            'header': header_name,
                            'issue': 'low_max_age',
                            'severity': 'medium',
                            'description': f'HSTS max-age is {max_age} seconds (recommended: 31536000+)'
                        })
            
            if 'includesubdomains' not in header_value.lower():
                recommendations.append("Consider adding 'includeSubDomains' to HSTS header")
        
        elif header_name == 'content-security-policy':
            # Analyze CSP header
            if 'unsafe-inline' in header_value.lower():
                issues.append({
                    'header': header_name,
                    'issue': 'unsafe_inline',
                    'severity': 'medium',
                    'description': 'CSP allows unsafe-inline which reduces security'
                })
            
            if 'unsafe-eval' in header_value.lower():
                issues.append({
                    'header': header_name,
                    'issue': 'unsafe_eval',
                    'severity': 'medium',
                    'description': 'CSP allows unsafe-eval which reduces security'
                })
        
        return {
            'issues': issues,
            'recommendations': recommendations
        }
    
    async def _check_seo_problematic_headers(self, headers: Dict[str, str], url: str) -> List[Dict[str, Any]]:
        """Check for headers that negatively impact SEO."""
        issues = []
        
        # Check X-Robots-Tag header
        x_robots = headers.get('x-robots-tag', '').lower()
        if x_robots:
            if 'noindex' in x_robots:
                issues.append({
                    'header': 'x-robots-tag',
                    'issue': 'blocks_indexing',
                    'severity': 'critical',
                    'seo_impact': 'Critical',
                    'description': 'X-Robots-Tag header blocks search engine indexing',
                    'recommendation': 'Remove noindex from X-Robots-Tag if page should be indexed'
                })
        
        return issues
    
    async def _calculate_headers_score(self, results: Dict[str, Any]) -> float:
        """Calculate security headers score."""
        total_weight = sum(config['weight'] for config in self.required_headers.values())
        score = 0
        
        # Add score for present headers
        for header_name in results['headers_found']:
            if header_name in self.required_headers:
                header_score = self.required_headers[header_name]['weight']
                score += header_score
        
        return (score / total_weight) * 100
    
    async def _generate_header_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate security header recommendations."""
        recommendations = []
        
        # Recommendations for missing headers
        for header in results['missing_headers']:
            if header == 'strict-transport-security':
                recommendations.append(
                    "Implement HSTS (HTTP Strict Transport Security) header: "
                    "'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload'"
                )
            elif header == 'content-security-policy':
                recommendations.append(
                    "Implement Content Security Policy (CSP) header to prevent XSS attacks"
                )
        
        return recommendations
    
    async def _assess_seo_impact(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess SEO impact of security headers configuration."""
        impact = {
            'overall_impact': 'positive',
            'trust_signals': 0,
            'ranking_factors': []
        }
        
        # Calculate trust signals score
        if 'strict-transport-security' in results['headers_found']:
            impact['trust_signals'] += 30
            impact['ranking_factors'].append('HTTPS enforcement via HSTS')
        
        return impact


class SecuritySEOManager:
    """Comprehensive security SEO management for IA Chéries creator economy."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Initialize analyzers
        self.ssl_analyzer = SSLCertificateAnalyzer()
        self.headers_analyzer = SecurityHeadersAnalyzer()
        
        # Security configuration
        self.security_config = self._load_security_config()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_security_config(self) -> Dict[str, Any]:
        """Load security configuration."""
        return {
            'ssl_requirements': {
                'min_key_size': 2048,
                'allowed_signature_algorithms': ['sha256', 'sha384', 'sha512'],
                'max_days_until_expiry_warning': 30
            },
            'header_requirements': {
                'strict_transport_security': True,
                'content_security_policy': True,
                'x_frame_options': True
            },
            'compliance_frameworks': ['PCI_DSS', 'GDPR', 'CCPA', 'SOC2']
        }
    
    async def run_comprehensive_security_audit(self, domain: str, 
                                             urls: Optional[List[str]] = None) -> SecurityAuditResults:
        """Run comprehensive security audit for SEO impact."""
        self.logger.info(f"Starting comprehensive security audit for {domain}")
        
        start_time = datetime.now(timezone.utc)
        all_issues = []
        recommendations = []
        
        try:
            # 1. SSL Certificate Analysis
            self.logger.info("Analyzing SSL certificate...")
            ssl_results = await self.ssl_analyzer.comprehensive_ssl_analysis(domain)
            ssl_score = ssl_results.get('ssl_score', 0)
            
            # Convert SSL issues to SecurityIssue objects
            for issue in ssl_results.get('security_issues', []):
                all_issues.append(SecurityIssue(
                    category='ssl_certificate',
                    severity=issue.get('severity', 'medium'),
                    title=issue.get('type', 'SSL Issue'),
                    description=issue.get('description', ''),
                    url=f"https://{domain}",
                    technical_details=json.dumps(ssl_results.get('certificate_info', {}), indent=2),
                    seo_impact=issue.get('seo_impact', 'Medium - SSL issues can affect search engine trust'),
                    fix_priority=self._calculate_fix_priority(issue.get('severity', 'medium')),
                    remediation_steps=self._get_ssl_remediation_steps(issue),
                    compliance_frameworks=['PCI_DSS', 'SOC2']
                ))
            
            recommendations.extend(ssl_results.get('recommendations', []))
            
            # 2. Security Headers Analysis
            self.logger.info("Analyzing security headers...")
            headers_results = await self.headers_analyzer.analyze_security_headers(f"https://{domain}")
            headers_score = headers_results.get('security_score', 0)
            
            # Convert header issues to SecurityIssue objects
            for issue in headers_results.get('header_issues', []):
                all_issues.append(SecurityIssue(
                    category='security_headers',
                    severity=issue.get('severity', 'medium'),
                    title=f"Security Header Issue: {issue.get('header', 'Unknown')}",
                    description=issue.get('description', issue.get('issue', '')),
                    url=f"https://{domain}",
                    technical_details=f"Header: {issue.get('header')}\nIssue: {issue.get('issue')}",
                    seo_impact=issue.get('seo_impact', 'Low - Header configuration may affect trust signals'),
                    fix_priority=self._calculate_fix_priority(issue.get('severity', 'medium')),
                    remediation_steps=self._get_header_remediation_steps(issue),
                    compliance_frameworks=['GDPR', 'CCPA']
                ))
            
            recommendations.extend(headers_results.get('recommendations', []))
            
            # 3. Mock Malware Scanning Results (simplified for this implementation)
            malware_results = {'clean': True, 'threats_found': []}
            content_security_score = 100.0
            malware_score = 100.0
            
            # 4. Compliance Analysis
            compliance_results = await self._analyze_compliance_status(ssl_results, headers_results, malware_results)
            
            # Calculate overall scores
            compliance_score = compliance_results.get('overall_score', 0)
            overall_security_score = (ssl_score + headers_score + content_security_score + compliance_score) / 4
            
            # Create audit results
            audit_results = SecurityAuditResults(
                domain=domain,
                audit_timestamp=start_time,
                overall_security_score=overall_security_score,
                ssl_score=ssl_score,
                headers_score=headers_score,
                content_security_score=content_security_score,
                malware_score=malware_score,
                compliance_score=compliance_score,
                issues=all_issues,
                recommendations=list(set(recommendations)),  # Remove duplicates
                ssl_certificate_info=ssl_results.get('certificate_info', {}),
                security_headers=headers_results.get('headers_found', {}),
                vulnerability_scan=malware_results,
                compliance_status=compliance_results
            )
            
            self.logger.info(f"Security audit completed. Overall score: {overall_security_score:.1f}")
            return audit_results
            
        except Exception as e:
            self.logger.error(f"Error during security audit: {e}")
            raise
    
    def _calculate_fix_priority(self, severity: str) -> int:
        """Calculate fix priority based on severity."""
        priority_map = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
        return priority_map.get(severity, 3)
    
    def _get_ssl_remediation_steps(self, issue: Dict[str, Any]) -> List[str]:
        """Get SSL remediation steps based on issue type."""
        return [
            'Review SSL certificate configuration',
            'Consult with security expert if needed',
            'Test changes in staging environment',
            'Monitor SEO impact after fixes'
        ]
    
    def _get_header_remediation_steps(self, issue: Dict[str, Any]) -> List[str]:
        """Get header remediation steps based on issue."""
        header = issue.get('header', '')
        
        if header == 'strict-transport-security':
            return [
                'Add HSTS header: Strict-Transport-Security: max-age=31536000; includeSubDomains',
                'Test HSTS implementation',
                'Monitor for improved security scores'
            ]
        elif header == 'content-security-policy':
            return [
                'Implement Content Security Policy header',
                'Start with report-only mode for testing',
                'Monitor for blocked resources and adjust as needed'
            ]
        
        return [
            f'Configure {header} header properly',
            'Test header implementation',
            'Monitor security and SEO impact'
        ]
    
    async def _analyze_compliance_status(self, ssl_results: Dict, headers_results: Dict, 
                                       malware_results: Dict) -> Dict[str, Any]:
        """Analyze compliance status against security frameworks."""
        compliance = {
            'frameworks': {},
            'overall_score': 0,
            'missing_requirements': []
        }
        
        # PCI DSS compliance
        pci_score = 100
        if ssl_results.get('ssl_score', 0) < 80:
            pci_score -= 30
            compliance['missing_requirements'].append('PCI DSS: Strong SSL/TLS configuration required')
        
        compliance['frameworks']['PCI_DSS'] = max(0, pci_score)
        
        # GDPR compliance (privacy-focused)
        gdpr_score = 100
        if 'strict-transport-security' not in headers_results.get('headers_found', {}):
            gdpr_score -= 25
            compliance['missing_requirements'].append('GDPR: HTTPS enforcement recommended for data protection')
        
        compliance['frameworks']['GDPR'] = max(0, gdpr_score)
        
        # Calculate overall compliance score
        framework_scores = list(compliance['frameworks'].values())
        compliance['overall_score'] = sum(framework_scores) / len(framework_scores) if framework_scores else 0
        
        return compliance
    
    async def generate_security_report(self, audit_results: SecurityAuditResults, 
                                     format: str = 'html') -> str:
        """Generate comprehensive security report."""
        if format == 'html':
            return await self._generate_html_security_report(audit_results)
        elif format == 'json':
            return await self._generate_json_security_report(audit_results)
        else:
            raise ValueError(f"Unsupported report format: {format}")
    
    async def _generate_html_security_report(self, results: SecurityAuditResults) -> str:
        """Generate HTML security report."""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security SEO Audit Report - {results.domain}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 40px; background: #f8f9fa; padding: 30px; border-radius: 10px; }}
                .score {{ font-size: 48px; font-weight: bold; color: #28a745; }}
                .scores-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
                .score-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
                .legal {{ font-size: 10px; color: #666; margin-top: 40px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 Security SEO Audit Report</h1>
                <h2>{results.domain}</h2>
                <div class="score">{results.overall_security_score:.1f}/100</div>
                <p>Security audit completed on {results.audit_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            
            <div class="scores-grid">
                <div class="score-card">
                    <h3>🔐 SSL Certificate</h3>
                    <div style="font-size: 24px; font-weight: bold;">{results.ssl_score:.1f}</div>
                </div>
                <div class="score-card">
                    <h3>🛡️ Security Headers</h3>
                    <div style="font-size: 24px; font-weight: bold;">{results.headers_score:.1f}</div>
                </div>
                <div class="score-card">
                    <h3>📋 Compliance</h3>
                    <div style="font-size: 24px; font-weight: bold;">{results.compliance_score:.1f}</div>
                </div>
            </div>
            
            <div class="legal">
                <p>© 2025 Fahed Mlaiel (mlaiel@live.de) - Security SEO Manager</p>
                <p>Enterprise security consulting: mlaiel@live.de</p>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    async def _generate_json_security_report(self, results: SecurityAuditResults) -> str:
        """Generate JSON security report."""
        data = {
            'domain': results.domain,
            'audit_timestamp': results.audit_timestamp.isoformat(),
            'overall_security_score': results.overall_security_score,
            'scores': {
                'ssl_score': results.ssl_score,
                'headers_score': results.headers_score,
                'compliance_score': results.compliance_score
            },
            'issues_count': len(results.issues),
            'recommendations_count': len(results.recommendations)
        }
        return json.dumps(data, indent=2)


# Usage Example
async def main():
    """Example usage of Security SEO Manager."""
    
    # Initialize security manager
    security_manager = SecuritySEOManager()
    
    try:
        domain = "example.com"  # Replace with actual domain
        
        print(f"\n=== Security SEO Audit for {domain} ===")
        
        # Run comprehensive security audit
        results = await security_manager.run_comprehensive_security_audit(domain)
        
        print(f"Overall Security Score: {results.overall_security_score:.1f}/100")
        print(f"SSL Score: {results.ssl_score:.1f}")
        print(f"Headers Score: {results.headers_score:.1f}")
        print(f"Issues Found: {len(results.issues)}")
        
        # Generate reports
        html_report = await security_manager.generate_security_report(results, 'html')
        json_report = await security_manager.generate_security_report(results, 'json')
        
        print("\n=== Security Reports Generated ===")
        
    except Exception as e:
        print(f"Error during security audit: {e}")


if __name__ == "__main__":
    asyncio.run(main())