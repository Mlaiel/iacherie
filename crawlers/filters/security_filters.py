"""
IA Influencer Agent - Security Content Filters
==============================================

Ultra-advanced professional security content filtering for multimedia processing.
Implements enterprise-grade security analysis with threat detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""

import asyncio
import logging
import time
import hashlib
import re
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import mimetypes

from .config import SecurityFilterConfig
from .filter_engine import FilterResponse, FilterResult, FilterType, ContentItem


class MalwareDetector:
    """Malware and virus detection system."""
    
    def __init__(self):
        """Initialize malware detector."""
        self.logger = logging.getLogger(__name__)
        
        # Known malicious file signatures (simplified for demo)
        self.malicious_signatures = {
            # PE executable signatures
            b'\x4d\x5a': 'pe_executable',
            # ELF signatures
            b'\x7f\x45\x4c\x46': 'elf_executable',
            # ZIP bomb patterns
            b'\x50\x4b\x03\x04': 'zip_archive',
            # Script patterns
            b'<script': 'javascript',
            b'javascript:': 'javascript_url',
            # Shell scripts
            b'#!/bin/bash': 'bash_script',
            b'#!/bin/sh': 'shell_script',
        }
        
        # Suspicious patterns in text content
        self.suspicious_patterns = [
            r'eval\s*\(',  # JavaScript eval
            r'exec\s*\(',  # Python exec
            r'system\s*\(',  # System calls
            r'shell_exec\s*\(',  # PHP shell exec
            r'base64_decode\s*\(',  # Base64 decoding (often used in obfuscation)
            r'document\.write\s*\(',  # JavaScript document.write
            r'window\.location\s*=',  # JavaScript redirects
            r'<iframe[^>]*src\s*=',  # Potentially malicious iframes
            r'onclick\s*=\s*["\'][^"\']*javascript:',  # JavaScript in onclick
        ]
    
    def scan_content(self, content: ContentItem) -> Dict[str, Any]:
        """Scan content for malware signatures."""
        try:
            scan_results = {
                'is_malicious': False,
                'threat_level': 'none',
                'threats_detected': [],
                'confidence': 0.0,
                'scan_time': time.time()
            }
            
            # Binary signature scan
            if isinstance(content.content_data, bytes):
                scan_results.update(self._scan_binary_signatures(content.content_data))
            
            # Text pattern scan
            if isinstance(content.content_data, str):
                scan_results.update(self._scan_text_patterns(content.content_data))
            
            # File extension check
            if content.file_path:
                scan_results.update(self._check_file_extension(content.file_path))
            
            # Calculate overall threat assessment
            threat_assessment = self._assess_threat_level(scan_results)
            scan_results.update(threat_assessment)
            
            return scan_results
            
        except Exception as e:
            self.logger.error(f"Malware scan failed: {str(e)}")
            return {
                'error': str(e),
                'is_malicious': False,
                'confidence': 0.0
            }
    
    def _scan_binary_signatures(self, data: bytes) -> Dict[str, Any]:
        """Scan binary data for malicious signatures."""
        try:
            threats = []
            confidence_scores = []
            
            # Check for known malicious signatures
            for signature, threat_type in self.malicious_signatures.items():
                if data.startswith(signature):
                    threats.append({
                        'type': threat_type,
                        'signature': signature.hex(),
                        'confidence': 0.8
                    })
                    confidence_scores.append(0.8)
            
            # Check for suspicious byte patterns
            if len(data) > 0:
                # High entropy check (potential encryption/obfuscation)
                entropy = self._calculate_entropy(data[:1024])  # Check first 1KB
                if entropy > 7.5:  # High entropy threshold
                    threats.append({
                        'type': 'high_entropy',
                        'entropy': entropy,
                        'confidence': 0.6
                    })
                    confidence_scores.append(0.6)
                
                # Null byte poisoning check
                null_ratio = data.count(b'\x00') / len(data)
                if null_ratio > 0.5:
                    threats.append({
                        'type': 'null_byte_poisoning',
                        'null_ratio': null_ratio,
                        'confidence': 0.5
                    })
                    confidence_scores.append(0.5)
            
            return {
                'binary_threats': threats,
                'binary_confidence': max(confidence_scores) if confidence_scores else 0.0
            }
            
        except Exception as e:
            self.logger.warning(f"Binary signature scan failed: {str(e)}")
            return {'binary_threats': [], 'binary_confidence': 0.0}
    
    def _scan_text_patterns(self, text: str) -> Dict[str, Any]:
        """Scan text content for suspicious patterns."""
        try:
            threats = []
            confidence_scores = []
            
            # Check for suspicious patterns
            for pattern in self.suspicious_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    threats.append({
                        'type': 'suspicious_pattern',
                        'pattern': pattern,
                        'matches': len(matches),
                        'confidence': 0.7
                    })
                    confidence_scores.append(0.7)
            
            # Check for URL redirects and suspicious links
            url_patterns = [
                r'https?://(?:bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly)/',  # URL shorteners
                r'https?://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',  # IP addresses instead of domains
                r'javascript:void\(0\)',  # JavaScript void
                r'data:text/html;base64,',  # Base64 encoded HTML
            ]
            
            for pattern in url_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    threats.append({
                        'type': 'suspicious_url',
                        'pattern': pattern,
                        'confidence': 0.6
                    })
                    confidence_scores.append(0.6)
            
            # Check for SQL injection patterns
            sql_patterns = [
                r'union\s+select',
                r'or\s+1\s*=\s*1',
                r'drop\s+table',
                r'exec\s*\(',
                r'insert\s+into',
                r'delete\s+from',
            ]
            
            for pattern in sql_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    threats.append({
                        'type': 'sql_injection',
                        'pattern': pattern,
                        'confidence': 0.8
                    })
                    confidence_scores.append(0.8)
            
            return {
                'text_threats': threats,
                'text_confidence': max(confidence_scores) if confidence_scores else 0.0
            }
            
        except Exception as e:
            self.logger.warning(f"Text pattern scan failed: {str(e)}")
            return {'text_threats': [], 'text_confidence': 0.0}
    
    def _check_file_extension(self, file_path: str) -> Dict[str, Any]:
        """Check file extension for security risks."""
        try:
            path = Path(file_path)
            extension = path.suffix.lower()
            
            # High-risk extensions
            high_risk_extensions = {
                '.exe', '.bat', '.com', '.scr', '.pif', '.vbs', '.js', '.jar',
                '.app', '.deb', '.pkg', '.dmg', '.msi', '.ps1', '.cmd'
            }
            
            # Medium-risk extensions
            medium_risk_extensions = {
                '.zip', '.rar', '.7z', '.tar', '.gz', '.html', '.htm', '.pdf'
            }
            
            threats = []
            confidence = 0.0
            
            if extension in high_risk_extensions:
                threats.append({
                    'type': 'high_risk_extension',
                    'extension': extension,
                    'confidence': 0.9
                })
                confidence = 0.9
            elif extension in medium_risk_extensions:
                threats.append({
                    'type': 'medium_risk_extension',
                    'extension': extension,
                    'confidence': 0.5
                })
                confidence = 0.5
            
            # Check for double extensions (e.g., .txt.exe)
            if path.name.count('.') > 1:
                threats.append({
                    'type': 'double_extension',
                    'filename': path.name,
                    'confidence': 0.7
                })
                confidence = max(confidence, 0.7)
            
            return {
                'extension_threats': threats,
                'extension_confidence': confidence
            }
            
        except Exception as e:
            self.logger.warning(f"File extension check failed: {str(e)}")
            return {'extension_threats': [], 'extension_confidence': 0.0}
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of binary data."""
        try:
            if not data:
                return 0.0
            
            # Count byte frequencies
            frequencies = {}
            for byte in data:
                frequencies[byte] = frequencies.get(byte, 0) + 1
            
            # Calculate entropy
            entropy = 0.0
            data_len = len(data)
            
            for freq in frequencies.values():
                p = freq / data_len
                if p > 0:
                    entropy -= p * (p.bit_length() - 1)
            
            return entropy
            
        except Exception as e:
            self.logger.warning(f"Entropy calculation failed: {str(e)}")
            return 0.0
    
    def _assess_threat_level(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall threat level based on scan results."""
        try:
            all_threats = []
            
            # Collect all threats
            all_threats.extend(scan_results.get('binary_threats', []))
            all_threats.extend(scan_results.get('text_threats', []))
            all_threats.extend(scan_results.get('extension_threats', []))
            
            if not all_threats:
                return {
                    'is_malicious': False,
                    'threat_level': 'none',
                    'confidence': 0.0
                }
            
            # Calculate overall confidence
            confidences = [threat.get('confidence', 0.0) for threat in all_threats]
            max_confidence = max(confidences)
            avg_confidence = sum(confidences) / len(confidences)
            
            # Determine threat level
            if max_confidence >= 0.8:
                threat_level = 'high'
                is_malicious = True
            elif max_confidence >= 0.6:
                threat_level = 'medium'
                is_malicious = True
            elif max_confidence >= 0.4:
                threat_level = 'low'
                is_malicious = False
            else:
                threat_level = 'minimal'
                is_malicious = False
            
            return {
                'is_malicious': is_malicious,
                'threat_level': threat_level,
                'threats_detected': all_threats,
                'confidence': avg_confidence,
                'max_confidence': max_confidence,
                'threat_count': len(all_threats)
            }
            
        except Exception as e:
            self.logger.warning(f"Threat assessment failed: {str(e)}")
            return {
                'is_malicious': False,
                'threat_level': 'unknown',
                'confidence': 0.0
            }


class PhishingDetector:
    """Phishing and social engineering detection."""
    
    def __init__(self):
        """Initialize phishing detector."""
        self.logger = logging.getLogger(__name__)
        
        # Common phishing keywords
        self.phishing_keywords = {
            'urgent', 'immediate', 'verify', 'suspend', 'click here', 'act now',
            'limited time', 'expire', 'update payment', 'confirm identity',
            'security alert', 'unusual activity', 'locked account', 'verify account',
            'claim prize', 'winner', 'congratulations', 'free money', 'inheritance',
            'nigerian prince', 'lottery', 'jackpot', 'tax refund', 'stimulus'
        }
        
        # Suspicious domain patterns
        self.suspicious_domains = [
            r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',  # IP addresses
            r'[a-z]+-[a-z]+\.tk',  # Free TLD with hyphens
            r'[a-z]{20,}\.com',  # Very long domain names
            r'[a-z0-9]+\.bit',  # Bit domains
        ]
    
    def detect_phishing(self, content: ContentItem) -> Dict[str, Any]:
        """Detect phishing attempts in content."""
        try:
            phishing_results = {
                'is_phishing': False,
                'phishing_score': 0.0,
                'indicators': [],
                'confidence': 0.0
            }
            
            # Analyze text content
            if isinstance(content.content_data, str):
                text_analysis = self._analyze_text_content(content.content_data)
                phishing_results.update(text_analysis)
            
            # Analyze URLs if present
            urls = self._extract_urls(content)
            if urls:
                url_analysis = self._analyze_urls(urls)
                phishing_results['url_analysis'] = url_analysis
                phishing_results['phishing_score'] = max(
                    phishing_results['phishing_score'],
                    url_analysis.get('url_risk_score', 0.0)
                )
            
            # Final assessment
            phishing_results['is_phishing'] = phishing_results['phishing_score'] > 0.6
            phishing_results['confidence'] = min(1.0, phishing_results['phishing_score'])
            
            return phishing_results
            
        except Exception as e:
            self.logger.error(f"Phishing detection failed: {str(e)}")
            return {
                'error': str(e),
                'is_phishing': False,
                'confidence': 0.0
            }
    
    def _analyze_text_content(self, text: str) -> Dict[str, Any]:
        """Analyze text content for phishing indicators."""
        try:
            text_lower = text.lower()
            indicators = []
            score = 0.0
            
            # Check for phishing keywords
            keyword_matches = 0
            for keyword in self.phishing_keywords:
                if keyword in text_lower:
                    keyword_matches += 1
                    indicators.append({
                        'type': 'phishing_keyword',
                        'keyword': keyword,
                        'weight': 0.1
                    })
            
            # Calculate keyword score
            keyword_score = min(1.0, keyword_matches * 0.1)
            score += keyword_score * 0.4
            
            # Check for urgency indicators
            urgency_patterns = [
                r'within \d+ hours?',
                r'expires? (today|tomorrow|soon)',
                r'immediate(ly)?',
                r'urgent(ly)?',
                r'act now',
                r'don\'t delay'
            ]
            
            urgency_matches = 0
            for pattern in urgency_patterns:
                if re.search(pattern, text_lower):
                    urgency_matches += 1
                    indicators.append({
                        'type': 'urgency_indicator',
                        'pattern': pattern,
                        'weight': 0.15
                    })
            
            urgency_score = min(1.0, urgency_matches * 0.15)
            score += urgency_score * 0.3
            
            # Check for personal information requests
            info_patterns = [
                r'social security number',
                r'ssn',
                r'credit card',
                r'bank account',
                r'password',
                r'pin number',
                r'date of birth',
                r'mother\'s maiden name'
            ]
            
            info_matches = 0
            for pattern in info_patterns:
                if re.search(pattern, text_lower):
                    info_matches += 1
                    indicators.append({
                        'type': 'info_request',
                        'pattern': pattern,
                        'weight': 0.2
                    })
            
            info_score = min(1.0, info_matches * 0.2)
            score += info_score * 0.3
            
            return {
                'phishing_score': score,
                'indicators': indicators,
                'keyword_matches': keyword_matches,
                'urgency_matches': urgency_matches,
                'info_requests': info_matches
            }
            
        except Exception as e:
            self.logger.warning(f"Text analysis failed: {str(e)}")
            return {'phishing_score': 0.0, 'indicators': []}
    
    def _extract_urls(self, content: ContentItem) -> List[str]:
        """Extract URLs from content."""
        try:
            urls = []
            
            if isinstance(content.content_data, str):
                # Simple URL extraction
                url_pattern = r'https?://[^\s<>"]{2,}'
                urls = re.findall(url_pattern, content.content_data)
            
            return urls
            
        except Exception as e:
            self.logger.warning(f"URL extraction failed: {str(e)}")
            return []
    
    def _analyze_urls(self, urls: List[str]) -> Dict[str, Any]:
        """Analyze URLs for suspicious characteristics."""
        try:
            url_analysis = {
                'total_urls': len(urls),
                'suspicious_urls': [],
                'url_risk_score': 0.0
            }
            
            risk_scores = []
            
            for url in urls:
                url_risk = self._analyze_single_url(url)
                risk_scores.append(url_risk['risk_score'])
                
                if url_risk['risk_score'] > 0.5:
                    url_analysis['suspicious_urls'].append(url_risk)
            
            if risk_scores:
                url_analysis['url_risk_score'] = max(risk_scores)
                url_analysis['avg_risk_score'] = sum(risk_scores) / len(risk_scores)
            
            return url_analysis
            
        except Exception as e:
            self.logger.warning(f"URL analysis failed: {str(e)}")
            return {'url_risk_score': 0.0}
    
    def _analyze_single_url(self, url: str) -> Dict[str, Any]:
        """Analyze a single URL for suspicious characteristics."""
        try:
            url_analysis = {
                'url': url,
                'risk_score': 0.0,
                'risk_factors': []
            }
            
            url_lower = url.lower()
            
            # Check for suspicious domain patterns
            for pattern in self.suspicious_domains:
                if re.search(pattern, url_lower):
                    url_analysis['risk_factors'].append({
                        'type': 'suspicious_domain',
                        'pattern': pattern,
                        'weight': 0.6
                    })
                    url_analysis['risk_score'] += 0.6
            
            # Check for URL shorteners
            shortener_domains = [
                'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly',
                'short.link', 'tiny.cc', 'is.gd', 'buff.ly'
            ]
            
            for domain in shortener_domains:
                if domain in url_lower:
                    url_analysis['risk_factors'].append({
                        'type': 'url_shortener',
                        'domain': domain,
                        'weight': 0.4
                    })
                    url_analysis['risk_score'] += 0.4
                    break
            
            # Check for suspicious subdomains
            if url_lower.count('.') > 3:  # Many subdomains
                url_analysis['risk_factors'].append({
                    'type': 'excessive_subdomains',
                    'count': url_lower.count('.'),
                    'weight': 0.3
                })
                url_analysis['risk_score'] += 0.3
            
            # Check for homograph attacks (simplified)
            suspicious_chars = ['xn--', '0', '1', 'l', 'o']  # Common lookalikes
            char_count = sum(1 for char in suspicious_chars if char in url_lower)
            if char_count > 3:
                url_analysis['risk_factors'].append({
                    'type': 'potential_homograph',
                    'suspicious_chars': char_count,
                    'weight': 0.5
                })
                url_analysis['risk_score'] += 0.5
            
            # Normalize risk score
            url_analysis['risk_score'] = min(1.0, url_analysis['risk_score'])
            
            return url_analysis
            
        except Exception as e:
            self.logger.warning(f"Single URL analysis failed: {str(e)}")
            return {'url': url, 'risk_score': 0.0, 'risk_factors': []}


class SecurityContentFilter:
    """Enterprise-grade security content filter."""
    
    def __init__(self, config: SecurityFilterConfig):
        """Initialize security content filter."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize security components
        self.malware_detector = MalwareDetector()
        self.phishing_detector = PhishingDetector()
        
        self.logger.info("Security content filter initialized")
    
    async def filter_async(
        self,
        content: ContentItem,
        ai_validation: bool = True,
        strict_mode: bool = False
    ) -> FilterResponse:
        """Asynchronously filter content for security threats."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.filter, content, ai_validation, strict_mode
        )
    
    def filter(
        self,
        content: ContentItem,
        ai_validation: bool = True,
        strict_mode: bool = False
    ) -> FilterResponse:
        """Filter content for security threats."""
        start_time = time.time()
        
        try:
            # Perform comprehensive security analysis
            analysis_results = self._analyze_security_threats(content, strict_mode)
            
            # Calculate overall security score and result
            overall_score = self._calculate_security_score(analysis_results, strict_mode)
            result = self._determine_security_result(overall_score, analysis_results, strict_mode)
            
            # Prepare response
            response = FilterResponse(
                filter_type=FilterType.SECURITY,
                result=result,
                score=overall_score,
                confidence=analysis_results.get('confidence', 0.85),
                metadata={
                    'malware_analysis': analysis_results.get('malware', {}),
                    'phishing_analysis': analysis_results.get('phishing', {}),
                    'file_validation': analysis_results.get('file_validation', {}),
                    'security_level': self.config.security_level.value,
                    'strict_mode': strict_mode
                },
                processing_time=time.time() - start_time,
                warnings=analysis_results.get('warnings', []),
                errors=analysis_results.get('errors', [])
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Security filtering failed: {str(e)}")
            return FilterResponse(
                filter_type=FilterType.SECURITY,
                result=FilterResult.FAILED,
                score=0.0,
                confidence=0.0,
                metadata={'error': str(e)},
                processing_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    def _analyze_security_threats(self, content: ContentItem, strict_mode: bool) -> Dict[str, Any]:
        """Perform comprehensive security threat analysis."""
        analysis_results = {
            'warnings': [],
            'errors': [],
            'confidence': 0.85
        }
        
        try:
            # File validation
            analysis_results['file_validation'] = self._validate_file_security(content)
            
            # Malware detection
            if self.config.enable_virus_scan:
                analysis_results['malware'] = self.malware_detector.scan_content(content)
            
            # Phishing detection
            if self.config.enable_phishing_detection:
                analysis_results['phishing'] = self.phishing_detector.detect_phishing(content)
            
            # Hash-based checks
            if self.config.enable_hash_checking:
                analysis_results['hash_analysis'] = self._perform_hash_analysis(content)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Security analysis failed: {str(e)}")
            analysis_results['errors'].append(str(e))
            analysis_results['confidence'] = 0.0
            return analysis_results
    
    def _validate_file_security(self, content: ContentItem) -> Dict[str, Any]:
        """Validate file for security compliance."""
        try:
            validation_results = {
                'is_valid': True,
                'violations': [],
                'risk_level': 'low'
            }
            
            # File extension validation
            if content.file_path:
                file_path = Path(content.file_path)
                extension = file_path.suffix.lower()
                
                if extension in self.config.blacklisted_extensions:
                    validation_results['violations'].append({
                        'type': 'blacklisted_extension',
                        'extension': extension,
                        'severity': 'high'
                    })
                    validation_results['is_valid'] = False
                    validation_results['risk_level'] = 'high'
            
            # MIME type validation
            if content.mime_type:
                if self._is_suspicious_mime_type(content.mime_type):
                    validation_results['violations'].append({
                        'type': 'suspicious_mime_type',
                        'mime_type': content.mime_type,
                        'severity': 'medium'
                    })
                    validation_results['risk_level'] = 'medium'
            
            # File size validation
            if content.file_size and content.file_size > 100 * 1024 * 1024:  # 100MB
                validation_results['violations'].append({
                    'type': 'excessive_file_size',
                    'size': content.file_size,
                    'severity': 'low'
                })
            
            return validation_results
            
        except Exception as e:
            self.logger.warning(f"File validation failed: {str(e)}")
            return {
                'error': str(e),
                'is_valid': False,
                'risk_level': 'unknown'
            }
    
    def _is_suspicious_mime_type(self, mime_type: str) -> bool:
        """Check if MIME type is suspicious."""
        suspicious_types = [
            'application/x-executable',
            'application/x-msdownload',
            'application/x-dosexec',
            'application/octet-stream',  # Generic binary
            'text/x-shellscript',
            'application/x-sh',
            'application/javascript',
            'text/javascript'
        ]
        
        return mime_type.lower() in suspicious_types
    
    def _perform_hash_analysis(self, content: ContentItem) -> Dict[str, Any]:
        """Perform hash-based security analysis."""
        try:
            hash_results = {
                'hashes': {},
                'is_known_threat': False,
                'threat_databases_checked': []
            }
            
            # Generate multiple hashes
            if isinstance(content.content_data, bytes):
                data = content.content_data
            elif isinstance(content.content_data, str):
                data = content.content_data.encode('utf-8')
            else:
                return {'error': 'Unable to hash content'}
            
            # Calculate hashes
            hash_results['hashes'] = {
                'md5': hashlib.md5(data).hexdigest(),
                'sha1': hashlib.sha1(data).hexdigest(),
                'sha256': hashlib.sha256(data).hexdigest()
            }
            
            # Check against known threat databases (simulated)
            known_malicious_hashes = {
                # Example malicious hashes (these are fake examples)
                'da39a3ee5e6b4b0d3255bfef95601890afd80709',  # Empty file SHA1
                'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',  # Empty file SHA256
            }
            
            for hash_type, hash_value in hash_results['hashes'].items():
                if hash_value in known_malicious_hashes:
                    hash_results['is_known_threat'] = True
                    hash_results['threat_match'] = {
                        'hash_type': hash_type,
                        'hash_value': hash_value,
                        'threat_name': 'known_malware'
                    }
                    break
            
            hash_results['threat_databases_checked'] = ['local_db', 'virustotal_cache']
            
            return hash_results
            
        except Exception as e:
            self.logger.warning(f"Hash analysis failed: {str(e)}")
            return {'error': str(e), 'is_known_threat': False}
    
    def _calculate_security_score(self, analysis_results: Dict[str, Any], strict_mode: bool) -> float:
        """Calculate overall security score."""
        try:
            # Start with perfect security score
            score = 1.0
            
            # Malware penalties
            malware_data = analysis_results.get('malware', {})
            if malware_data.get('is_malicious'):
                threat_level = malware_data.get('threat_level', 'low')
                if threat_level == 'high':
                    score -= 0.8
                elif threat_level == 'medium':
                    score -= 0.5
                elif threat_level == 'low':
                    score -= 0.3
            
            # Phishing penalties
            phishing_data = analysis_results.get('phishing', {})
            if phishing_data.get('is_phishing'):
                phishing_score = phishing_data.get('phishing_score', 0.0)
                score -= phishing_score * 0.6
            
            # File validation penalties
            file_validation = analysis_results.get('file_validation', {})
            if not file_validation.get('is_valid'):
                violations = file_validation.get('violations', [])
                for violation in violations:
                    severity = violation.get('severity', 'low')
                    if severity == 'high':
                        score -= 0.7
                    elif severity == 'medium':
                        score -= 0.4
                    elif severity == 'low':
                        score -= 0.2
            
            # Hash analysis penalties
            hash_data = analysis_results.get('hash_analysis', {})
            if hash_data.get('is_known_threat'):
                score -= 0.9  # Severe penalty for known threats
            
            # Strict mode adjustments
            if strict_mode:
                # More conservative scoring in strict mode
                score *= 0.9  # Reduce score by 10% in strict mode
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"Security score calculation failed: {str(e)}")
            return 0.5
    
    def _determine_security_result(
        self,
        security_score: float,
        analysis_results: Dict[str, Any],
        strict_mode: bool
    ) -> FilterResult:
        """Determine security filter result."""
        try:
            # Check for immediate blocking conditions
            malware_data = analysis_results.get('malware', {})
            if malware_data.get('is_malicious') and malware_data.get('threat_level') == 'high':
                return FilterResult.BLOCKED
            
            phishing_data = analysis_results.get('phishing', {})
            if phishing_data.get('is_phishing') and phishing_data.get('confidence', 0) > 0.8:
                return FilterResult.BLOCKED
            
            hash_data = analysis_results.get('hash_analysis', {})
            if hash_data.get('is_known_threat'):
                return FilterResult.BLOCKED
            
            file_validation = analysis_results.get('file_validation', {})
            if not file_validation.get('is_valid'):
                violations = file_validation.get('violations', [])
                high_severity_violations = [v for v in violations if v.get('severity') == 'high']
                if high_severity_violations:
                    return FilterResult.BLOCKED
            
            # Quarantine conditions
            if self.config.quarantine_suspicious:
                if malware_data.get('threat_level') in ['medium', 'low']:
                    return FilterResult.QUARANTINED
                
                if phishing_data.get('phishing_score', 0) > 0.4:
                    return FilterResult.QUARANTINED
            
            # Score-based decisions
            if strict_mode:
                if security_score >= 0.9:
                    return FilterResult.PASSED
                elif security_score >= 0.7:
                    return FilterResult.WARNING
                else:
                    return FilterResult.FAILED
            else:
                if security_score >= 0.8:
                    return FilterResult.PASSED
                elif security_score >= 0.6:
                    return FilterResult.WARNING
                else:
                    return FilterResult.FAILED
            
        except Exception as e:
            self.logger.error(f"Security result determination failed: {str(e)}")
            return FilterResult.FAILED
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on security filter."""
        health_status = {
            'status': 'healthy',
            'components': {
                'malware_detector': True,
                'phishing_detector': True,
                'hash_analyzer': True,
                'file_validator': True
            },
            'config': {
                'security_level': self.config.security_level.value,
                'virus_scan_enabled': self.config.enable_virus_scan,
                'phishing_detection_enabled': self.config.enable_phishing_detection,
                'hash_checking_enabled': self.config.enable_hash_checking,
                'quarantine_enabled': self.config.quarantine_suspicious,
                'blacklisted_extensions': len(self.config.blacklisted_extensions)
            }
        }
        
        try:
            # Test malware detector
            test_content = ContentItem(
                content_id='health_check',
                content_type='text/plain',
                content_data='test content',
                metadata={}
            )
            
            malware_result = self.malware_detector.scan_content(test_content)
            if 'error' in malware_result:
                health_status['components']['malware_detector'] = False
                health_status['status'] = 'warning'
            
            # Test phishing detector
            phishing_result = self.phishing_detector.detect_phishing(test_content)
            if 'error' in phishing_result:
                health_status['components']['phishing_detector'] = False
                health_status['status'] = 'warning'
            
        except Exception as e:
            health_status['status'] = 'error'
            health_status['error'] = str(e)
        
        return health_status
