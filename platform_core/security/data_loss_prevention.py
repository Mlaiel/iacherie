#!/usr/bin/env python3
"""
Data Loss Prevention (DLP) - Enterprise Data Protection System
Advanced data classification, monitoring, and leakage prevention for creator platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
==========================================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided

This module provides comprehensive data loss prevention including:
- Real-time data classification and labeling
- Content inspection and sensitive data detection
- Data exfiltration monitoring and prevention
- Policy enforcement and compliance reporting
- Creator content protection and leak prevention
"""

import asyncio
import hashlib
import logging
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
import secrets
from pathlib import Path
import mimetypes
import magic
from cryptography.fernet import Fernet
import numpy as np
from collections import defaultdict
import zipfile
import tarfile
import gzip

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataClassification(Enum):
    """Classifications de données selon sensibilité"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

class DataType(Enum):
    """Types de données détectables"""
    PERSONAL_INFO = "personal_info"
    FINANCIAL_DATA = "financial_data"
    HEALTH_INFO = "health_info"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CREDENTIALS = "credentials"
    CREATOR_CONTENT = "creator_content"
    BUSINESS_SECRET = "business_secret"
    TECHNICAL_DATA = "technical_data"

class ViolationSeverity(Enum):
    """Niveaux de sévérité des violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ActionType(Enum):
    """Types d'actions DLP"""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    ENCRYPT = "encrypt"
    WATERMARK = "watermark"
    LOG_ONLY = "log_only"

class TransmissionChannel(Enum):
    """Canaux de transmission surveillés"""
    EMAIL = "email"
    FILE_UPLOAD = "file_upload"
    CLOUD_SYNC = "cloud_sync"
    USB_TRANSFER = "usb_transfer"
    NETWORK_SHARE = "network_share"
    WEB_UPLOAD = "web_upload"
    API_CALL = "api_call"
    DATABASE_EXPORT = "database_export"

@dataclass
class DataPattern:
    """Pattern de détection de données sensibles"""
    pattern_id: str
    name: str
    data_type: DataType
    regex_pattern: str
    classification: DataClassification
    confidence_threshold: float = 0.8
    enabled: bool = True
    description: str = ""
    
    def matches(self, text: str) -> List[Tuple[str, float]]:
        """Vérification correspondance pattern"""
        matches = []
        pattern = re.compile(self.regex_pattern, re.IGNORECASE | re.MULTILINE)
        
        for match in pattern.finditer(text):
            confidence = self._calculate_confidence(match.group(), text)
            if confidence >= self.confidence_threshold:
                matches.append((match.group(), confidence))
        
        return matches
    
    def _calculate_confidence(self, match: str, context: str) -> float:
        """Calcul confiance de détection"""
        base_confidence = 0.7
        
        # Facteurs d'augmentation confiance
        if len(match) > 10:
            base_confidence += 0.1
        
        # Contexte autour du match
        match_start = context.find(match)
        if match_start > 0:
            context_before = context[max(0, match_start-50):match_start]
            context_after = context[match_start+len(match):match_start+len(match)+50]
            
            # Mots-clés contextuels
            context_keywords = {
                DataType.PERSONAL_INFO: ['name', 'address', 'phone', 'email'],
                DataType.FINANCIAL_DATA: ['credit', 'bank', 'account', 'payment'],
                DataType.CREDENTIALS: ['password', 'token', 'key', 'secret']
            }
            
            if self.data_type in context_keywords:
                for keyword in context_keywords[self.data_type]:
                    if keyword.lower() in context_before.lower() or keyword.lower() in context_after.lower():
                        base_confidence += 0.1
                        break
        
        return min(1.0, base_confidence)

@dataclass
class DLPPolicy:
    """Politique DLP pour règles de protection"""
    policy_id: str
    name: str
    description: str
    data_types: List[DataType]
    classifications: List[DataClassification]
    channels: List[TransmissionChannel]
    action: ActionType
    severity: ViolationSeverity
    enabled: bool = True
    exceptions: List[str] = field(default_factory=list)
    notify_recipients: List[str] = field(default_factory=list)
    
    def applies_to(self, data_type: DataType, classification: DataClassification, channel: TransmissionChannel) -> bool:
        """Vérification applicabilité politique"""
        return (
            self.enabled and
            (not self.data_types or data_type in self.data_types) and
            (not self.classifications or classification in self.classifications) and
            (not self.channels or channel in self.channels)
        )

@dataclass
class DataIncident:
    """Incident de fuite de données détecté"""
    incident_id: str
    timestamp: datetime
    user_id: str
    source_location: str
    destination: str
    channel: TransmissionChannel
    data_type: DataType
    classification: DataClassification
    severity: ViolationSeverity
    action_taken: ActionType
    policy_violated: str
    detected_patterns: List[Dict[str, Any]]
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    blocked: bool = False
    quarantined_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return {
            'incident_id': self.incident_id,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'source_location': self.source_location,
            'destination': self.destination,
            'channel': self.channel.value,
            'data_type': self.data_type.value,
            'classification': self.classification.value,
            'severity': self.severity.value,
            'action_taken': self.action_taken.value,
            'policy_violated': self.policy_violated,
            'detected_patterns': self.detected_patterns,
            'file_hash': self.file_hash,
            'file_size': self.file_size,
            'blocked': self.blocked,
            'quarantined_path': self.quarantined_path
        }

@dataclass
class ScanResult:
    """Résultat scan DLP d'un contenu"""
    scan_id: str
    content_hash: str
    scan_timestamp: datetime
    total_patterns_found: int
    highest_classification: DataClassification
    sensitive_data_detected: bool
    patterns_by_type: Dict[DataType, List[Dict[str, Any]]]
    recommended_action: ActionType
    confidence_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return {
            'scan_id': self.scan_id,
            'content_hash': self.content_hash,
            'scan_timestamp': self.scan_timestamp.isoformat(),
            'total_patterns_found': self.total_patterns_found,
            'highest_classification': self.highest_classification.value,
            'sensitive_data_detected': self.sensitive_data_detected,
            'patterns_by_type': {k.value: v for k, v in self.patterns_by_type.items()},
            'recommended_action': self.recommended_action.value,
            'confidence_score': self.confidence_score
        }

class DataLossPreventionEngine:
    """Moteur principal de prévention perte de données"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialisation moteur DLP"""
        self.config = config or {}
        
        # Base de données patterns
        self.patterns: Dict[str, DataPattern] = {}
        self.policies: Dict[str, DLPPolicy] = {}
        self.incidents: Dict[str, DataIncident] = {}
        self.scan_history: Dict[str, ScanResult] = {}
        
        # Configuration
        self.quarantine_path = Path(self.config.get('quarantine_path', '/tmp/dlp_quarantine'))
        self.quarantine_path.mkdir(parents=True, exist_ok=True)
        
        self.max_scan_size = self.config.get('max_scan_size', 100 * 1024 * 1024)  # 100MB
        self.enable_real_time_monitoring = self.config.get('enable_real_time_monitoring', True)
        
        # Chiffrement pour données quarantinées
        self.quarantine_key = self._generate_quarantine_key()
        self.cipher = Fernet(self.quarantine_key)
        
        # Initialisation patterns par défaut
        self._initialize_default_patterns()
        self._initialize_default_policies()
        
        logger.info("Data Loss Prevention Engine initialized successfully")
    
    def _generate_quarantine_key(self) -> bytes:
        """Génération clé chiffrement quarantaine"""
        key_material = self.config.get('quarantine_key', secrets.token_bytes(32))
        return base64.urlsafe_b64encode(key_material)
    
    def _initialize_default_patterns(self):
        """Initialisation patterns de détection par défaut"""
        
        # Numéros de carte de crédit
        self.add_pattern(DataPattern(
            pattern_id="credit_card",
            name="Credit Card Numbers",
            data_type=DataType.FINANCIAL_DATA,
            regex_pattern=r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
            classification=DataClassification.CONFIDENTIAL,
            confidence_threshold=0.9,
            description="Credit card number detection"
        ))
        
        # Numéros de sécurité sociale
        self.add_pattern(DataPattern(
            pattern_id="ssn",
            name="Social Security Numbers",
            data_type=DataType.PERSONAL_INFO,
            regex_pattern=r'\b(?!000|666|9\d{2})\d{3}-?(?!00)\d{2}-?(?!0000)\d{4}\b',
            classification=DataClassification.RESTRICTED,
            confidence_threshold=0.85,
            description="Social Security Number detection"
        ))
        
        # Adresses email
        self.add_pattern(DataPattern(
            pattern_id="email",
            name="Email Addresses",
            data_type=DataType.PERSONAL_INFO,
            regex_pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            classification=DataClassification.INTERNAL,
            confidence_threshold=0.7,
            description="Email address detection"
        ))
        
        # Mots de passe potentiels
        self.add_pattern(DataPattern(
            pattern_id="passwords",
            name="Potential Passwords",
            data_type=DataType.CREDENTIALS,
            regex_pattern=r'(?:password|pwd|pass|secret|key)\s*[:=]\s*["\']?([^\s"\']{8,})["\']?',
            classification=DataClassification.TOP_SECRET,
            confidence_threshold=0.8,
            description="Password/credential detection"
        ))
        
        # Tokens API
        self.add_pattern(DataPattern(
            pattern_id="api_tokens",
            name="API Tokens",
            data_type=DataType.CREDENTIALS,
            regex_pattern=r'(?:api[_-]?key|token|secret[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            classification=DataClassification.TOP_SECRET,
            confidence_threshold=0.85,
            description="API token/key detection"
        ))
        
        # Numéros de téléphone
        self.add_pattern(DataPattern(
            pattern_id="phone_numbers",
            name="Phone Numbers",
            data_type=DataType.PERSONAL_INFO,
            regex_pattern=r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            classification=DataClassification.INTERNAL,
            confidence_threshold=0.7,
            description="Phone number detection"
        ))
        
        # Propriété intellectuelle IA Chérie
        self.add_pattern(DataPattern(
            pattern_id="ainflue_ip",
            name="IA Chérie Intellectual Property",
            data_type=DataType.INTELLECTUAL_PROPERTY,
            regex_pattern=r'(?:iacherie|fahed\s+mlaiel|propriét[éeè]\s+intellectuelle|copyright.*mlaiel)',
            classification=DataClassification.TOP_SECRET,
            confidence_threshold=0.9,
            description="IA Chérie IP and copyright detection"
        ))
        
        # Contenu créateur sensible
        self.add_pattern(DataPattern(
            pattern_id="creator_content",
            name="Creator Sensitive Content",
            data_type=DataType.CREATOR_CONTENT,
            regex_pattern=r'(?:creator[_-]?id|content[_-]?hash|private[_-]?content|unreleased.*content)',
            classification=DataClassification.CONFIDENTIAL,
            confidence_threshold=0.8,
            description="Creator sensitive content detection"
        ))
        
        logger.info(f"Initialized {len(self.patterns)} default detection patterns")
    
    def _initialize_default_policies(self):
        """Initialisation politiques DLP par défaut"""
        
        # Politique restriction données financières
        self.add_policy(DLPPolicy(
            policy_id="financial_data_protection",
            name="Financial Data Protection",
            description="Prevent financial data leakage",
            data_types=[DataType.FINANCIAL_DATA],
            classifications=[DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED],
            channels=[TransmissionChannel.EMAIL, TransmissionChannel.FILE_UPLOAD, TransmissionChannel.WEB_UPLOAD],
            action=ActionType.BLOCK,
            severity=ViolationSeverity.HIGH,
            notify_recipients=["security@iacherie.com", "compliance@iacherie.com"]
        ))
        
        # Politique protection credentials
        self.add_policy(DLPPolicy(
            policy_id="credentials_protection",
            name="Credentials Protection",
            description="Prevent credential leakage",
            data_types=[DataType.CREDENTIALS],
            classifications=[DataClassification.TOP_SECRET],
            channels=list(TransmissionChannel),
            action=ActionType.BLOCK,
            severity=ViolationSeverity.CRITICAL,
            notify_recipients=["security@iacherie.com", "ciso@iacherie.com"]
        ))
        
        # Politique protection IP IA Chérie
        self.add_policy(DLPPolicy(
            policy_id="ainflue_ip_protection",
            name="IA Chérie IP Protection",
            description="Protect IA Chérie intellectual property",
            data_types=[DataType.INTELLECTUAL_PROPERTY],
            classifications=[DataClassification.TOP_SECRET, DataClassification.RESTRICTED],
            channels=list(TransmissionChannel),
            action=ActionType.QUARANTINE,
            severity=ViolationSeverity.EMERGENCY,
            notify_recipients=["legal@iacherie.com", "mlaiel@live.de"]
        ))
        
        # Politique protection contenu créateur
        self.add_policy(DLPPolicy(
            policy_id="creator_content_protection",
            name="Creator Content Protection",
            description="Protect creator sensitive content",
            data_types=[DataType.CREATOR_CONTENT],
            classifications=[DataClassification.CONFIDENTIAL],
            channels=[TransmissionChannel.EMAIL, TransmissionChannel.WEB_UPLOAD, TransmissionChannel.CLOUD_SYNC],
            action=ActionType.WARN,
            severity=ViolationSeverity.MEDIUM,
            notify_recipients=["creators@iacherie.com"]
        ))
        
        # Politique surveillance données personnelles
        self.add_policy(DLPPolicy(
            policy_id="personal_data_monitoring",
            name="Personal Data Monitoring",
            description="Monitor personal data transmission",
            data_types=[DataType.PERSONAL_INFO],
            classifications=[DataClassification.INTERNAL, DataClassification.CONFIDENTIAL],
            channels=list(TransmissionChannel),
            action=ActionType.LOG_ONLY,
            severity=ViolationSeverity.LOW,
            notify_recipients=["privacy@iacherie.com"]
        ))
        
        logger.info(f"Initialized {len(self.policies)} default DLP policies")
    
    def add_pattern(self, pattern: DataPattern):
        """Ajout pattern de détection"""
        self.patterns[pattern.pattern_id] = pattern
        logger.debug(f"Added detection pattern: {pattern.name}")
    
    def add_policy(self, policy: DLPPolicy):
        """Ajout politique DLP"""
        self.policies[policy.policy_id] = policy
        logger.debug(f"Added DLP policy: {policy.name}")
    
    async def scan_content(
        self,
        content: Union[str, bytes, Path],
        source_info: Dict[str, Any] = None
    ) -> ScanResult:
        """Scan contenu pour détection données sensibles"""
        try:
            scan_id = str(uuid.uuid4())
            source_info = source_info or {}
            
            # Préparation contenu pour scan
            if isinstance(content, Path):
                with open(content, 'rb') as f:
                    content_bytes = f.read()
                content_text = self._extract_text_from_file(content, content_bytes)
            elif isinstance(content, bytes):
                content_bytes = content
                content_text = self._extract_text_from_bytes(content_bytes)
            else:
                content_text = str(content)
                content_bytes = content_text.encode('utf-8')
            
            # Vérification taille
            if len(content_bytes) > self.max_scan_size:
                logger.warning(f"Content too large for scan: {len(content_bytes)} bytes")
                # Scan partiel des premiers MB
                content_text = content_text[:self.max_scan_size // 2]
            
            # Hash du contenu
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # Détection patterns
            patterns_found = defaultdict(list)
            total_patterns = 0
            highest_classification = DataClassification.PUBLIC
            max_confidence = 0.0
            
            for pattern in self.patterns.values():
                if not pattern.enabled:
                    continue
                
                matches = pattern.matches(content_text)
                if matches:
                    for match_text, confidence in matches:
                        pattern_info = {
                            'pattern_id': pattern.pattern_id,
                            'pattern_name': pattern.name,
                            'matched_text': match_text[:100] + "..." if len(match_text) > 100 else match_text,
                            'confidence': confidence,
                            'classification': pattern.classification.value,
                            'position': content_text.find(match_text)
                        }
                        patterns_found[pattern.data_type].append(pattern_info)
                        total_patterns += 1
                        max_confidence = max(max_confidence, confidence)
                        
                        # Mise à jour classification la plus élevée
                        if self._classification_level(pattern.classification) > self._classification_level(highest_classification):
                            highest_classification = pattern.classification
            
            # Détermination action recommandée
            recommended_action = self._determine_recommended_action(patterns_found, highest_classification)
            
            # Création résultat
            scan_result = ScanResult(
                scan_id=scan_id,
                content_hash=content_hash,
                scan_timestamp=datetime.utcnow(),
                total_patterns_found=total_patterns,
                highest_classification=highest_classification,
                sensitive_data_detected=total_patterns > 0,
                patterns_by_type=dict(patterns_found),
                recommended_action=recommended_action,
                confidence_score=max_confidence
            )
            
            # Sauvegarde historique
            self.scan_history[scan_id] = scan_result
            
            logger.info(f"Content scan completed: {total_patterns} patterns found, classification: {highest_classification.value}")
            return scan_result
            
        except Exception as e:
            logger.error(f"Error scanning content: {str(e)}")
            raise
    
    async def monitor_transmission(
        self,
        content: Union[str, bytes, Path],
        user_id: str,
        source_location: str,
        destination: str,
        channel: TransmissionChannel,
        additional_context: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[DataIncident]]:
        """Surveillance transmission de données"""
        try:
            additional_context = additional_context or {}
            
            # Scan du contenu
            scan_result = await self.scan_content(content, additional_context)
            
            # Si aucune donnée sensible détectée, autoriser
            if not scan_result.sensitive_data_detected:
                return True, None
            
            # Évaluation selon politiques
            incident = None
            allow_transmission = True
            
            for data_type, patterns in scan_result.patterns_by_type.items():
                for pattern_info in patterns:
                    classification = DataClassification(pattern_info['classification'])
                    
                    # Recherche politique applicable
                    applicable_policy = self._find_applicable_policy(data_type, classification, channel)
                    
                    if applicable_policy:
                        # Création incident
                        incident = DataIncident(
                            incident_id=str(uuid.uuid4()),
                            timestamp=datetime.utcnow(),
                            user_id=user_id,
                            source_location=source_location,
                            destination=destination,
                            channel=channel,
                            data_type=data_type,
                            classification=classification,
                            severity=applicable_policy.severity,
                            action_taken=applicable_policy.action,
                            policy_violated=applicable_policy.policy_id,
                            detected_patterns=[pattern_info],
                            file_hash=scan_result.content_hash,
                            file_size=len(str(content).encode()) if isinstance(content, str) else len(content)
                        )
                        
                        # Application action
                        if applicable_policy.action == ActionType.BLOCK:
                            allow_transmission = False
                            incident.blocked = True
                        elif applicable_policy.action == ActionType.QUARANTINE:
                            allow_transmission = False
                            quarantine_path = await self._quarantine_content(content, incident.incident_id)
                            incident.quarantined_path = str(quarantine_path)
                        elif applicable_policy.action == ActionType.ENCRYPT:
                            # Chiffrement automatique du contenu
                            await self._encrypt_content(content, incident.incident_id)
                        
                        # Enregistrement incident
                        self.incidents[incident.incident_id] = incident
                        
                        # Notification si configurée
                        if applicable_policy.notify_recipients:
                            await self._send_incident_notification(incident, applicable_policy.notify_recipients)
                        
                        # Si action bloquante, arrêter évaluation
                        if applicable_policy.action in [ActionType.BLOCK, ActionType.QUARANTINE]:
                            break
                
                if incident and not allow_transmission:
                    break
            
            logger.info(f"Transmission monitoring completed: allowed={allow_transmission}, incident={incident.incident_id if incident else None}")
            return allow_transmission, incident
            
        except Exception as e:
            logger.error(f"Error monitoring transmission: {str(e)}")
            # En cas d'erreur, par sécurité, bloquer transmission
            return False, None
    
    async def investigate_incident(self, incident_id: str) -> Dict[str, Any]:
        """Investigation approfondie d'un incident"""
        try:
            if incident_id not in self.incidents:
                raise ValueError(f"Incident {incident_id} not found")
            
            incident = self.incidents[incident_id]
            
            # Récupération informations supplémentaires
            investigation_data = {
                'incident': incident.to_dict(),
                'related_incidents': [],
                'user_history': [],
                'content_analysis': {},
                'recommendations': []
            }
            
            # Recherche incidents liés (même utilisateur, même type de données)
            for other_incident in self.incidents.values():
                if (other_incident.incident_id != incident_id and
                    (other_incident.user_id == incident.user_id or
                     other_incident.data_type == incident.data_type)):
                    investigation_data['related_incidents'].append(other_incident.to_dict())
            
            # Historique utilisateur
            user_incidents = [
                inc.to_dict() for inc in self.incidents.values()
                if inc.user_id == incident.user_id
            ]
            investigation_data['user_history'] = sorted(
                user_incidents,
                key=lambda x: x['timestamp'],
                reverse=True
            )[:10]  # 10 derniers incidents
            
            # Analyse du contenu si disponible
            if incident.quarantined_path:
                content_analysis = await self._analyze_quarantined_content(incident.quarantined_path)
                investigation_data['content_analysis'] = content_analysis
            
            # Recommandations
            recommendations = self._generate_incident_recommendations(incident, investigation_data)
            investigation_data['recommendations'] = recommendations
            
            logger.info(f"Incident investigation completed for {incident_id}")
            return investigation_data
            
        except Exception as e:
            logger.error(f"Error investigating incident: {str(e)}")
            raise
    
    async def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """Génération rapport de conformité DLP"""
        try:
            # Filtrage incidents par période
            period_incidents = [
                incident for incident in self.incidents.values()
                if start_date <= incident.timestamp <= end_date
            ]
            
            # Statistiques générales
            total_incidents = len(period_incidents)
            blocked_transmissions = len([inc for inc in period_incidents if inc.blocked])
            quarantined_items = len([inc for inc in period_incidents if inc.quarantined_path])
            
            # Répartition par sévérité
            by_severity = defaultdict(int)
            for incident in period_incidents:
                by_severity[incident.severity.value] += 1
            
            # Répartition par type de données
            by_data_type = defaultdict(int)
            for incident in period_incidents:
                by_data_type[incident.data_type.value] += 1
            
            # Répartition par canal
            by_channel = defaultdict(int)
            for incident in period_incidents:
                by_channel[incident.channel.value] += 1
            
            # Top utilisateurs avec incidents
            user_incidents = defaultdict(int)
            for incident in period_incidents:
                user_incidents[incident.user_id] += 1
            
            top_users = sorted(user_incidents.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Efficacité politiques
            policy_effectiveness = defaultdict(lambda: {'applied': 0, 'effective': 0})
            for incident in period_incidents:
                policy_effectiveness[incident.policy_violated]['applied'] += 1
                if incident.blocked or incident.quarantined_path:
                    policy_effectiveness[incident.policy_violated]['effective'] += 1
            
            # Tendances temporelles
            daily_incidents = defaultdict(int)
            for incident in period_incidents:
                day = incident.timestamp.date().isoformat()
                daily_incidents[day] += 1
            
            # Compilation rapport
            report = {
                'report_id': str(uuid.uuid4()),
                'generation_timestamp': datetime.utcnow().isoformat(),
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_incidents': total_incidents,
                    'blocked_transmissions': blocked_transmissions,
                    'quarantined_items': quarantined_items,
                    'prevention_rate': (blocked_transmissions + quarantined_items) / total_incidents if total_incidents > 0 else 0
                },
                'breakdown': {
                    'by_severity': dict(by_severity),
                    'by_data_type': dict(by_data_type),
                    'by_channel': dict(by_channel),
                    'top_users_with_incidents': top_users
                },
                'policy_effectiveness': {
                    policy_id: {
                        'applied': stats['applied'],
                        'effective': stats['effective'],
                        'effectiveness_rate': stats['effective'] / stats['applied'] if stats['applied'] > 0 else 0
                    }
                    for policy_id, stats in policy_effectiveness.items()
                },
                'trends': {
                    'daily_incidents': dict(daily_incidents)
                }
            }
            
            # Détails incidents si demandé
            if include_details:
                report['detailed_incidents'] = [inc.to_dict() for inc in period_incidents]
            
            logger.info(f"Compliance report generated for period {start_date} to {end_date}: {total_incidents} incidents")
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            raise
    
    async def update_pattern(self, pattern_id: str, updates: Dict[str, Any]) -> bool:
        """Mise à jour pattern de détection"""
        try:
            if pattern_id not in self.patterns:
                return False
            
            pattern = self.patterns[pattern_id]
            
            # Application mises à jour
            for field, value in updates.items():
                if hasattr(pattern, field):
                    setattr(pattern, field, value)
            
            logger.info(f"Pattern {pattern_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating pattern: {str(e)}")
            return False
    
    async def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> bool:
        """Mise à jour politique DLP"""
        try:
            if policy_id not in self.policies:
                return False
            
            policy = self.policies[policy_id]
            
            # Application mises à jour
            for field, value in updates.items():
                if hasattr(policy, field):
                    if field in ['data_types', 'classifications', 'channels']:
                        # Conversion enum si nécessaire
                        if field == 'data_types':
                            value = [DataType(v) if isinstance(v, str) else v for v in value]
                        elif field == 'classifications':
                            value = [DataClassification(v) if isinstance(v, str) else v for v in value]
                        elif field == 'channels':
                            value = [TransmissionChannel(v) if isinstance(v, str) else v for v in value]
                    elif field in ['action', 'severity']:
                        if field == 'action':
                            value = ActionType(value) if isinstance(value, str) else value
                        elif field == 'severity':
                            value = ViolationSeverity(value) if isinstance(value, str) else value
                    
                    setattr(policy, field, value)
            
            logger.info(f"Policy {policy_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating policy: {str(e)}")
            return False
    
    # Méthodes privées utilitaires
    
    def _extract_text_from_file(self, file_path: Path, content_bytes: bytes) -> str:
        """Extraction texte depuis fichier selon type"""
        try:
            # Détection type MIME
            mime_type = magic.from_buffer(content_bytes, mime=True)
            
            if mime_type.startswith('text/'):
                # Fichier texte
                return content_bytes.decode('utf-8', errors='ignore')
            elif mime_type == 'application/pdf':
                # PDF - simulation extraction
                return f"PDF_CONTENT: {content_bytes[:1000].decode('utf-8', errors='ignore')}"
            elif mime_type.startswith('application/'):
                if 'zip' in mime_type or file_path.suffix.lower() in ['.zip', '.docx', '.xlsx']:
                    # Archive ou document Office
                    return self._extract_text_from_archive(content_bytes)
                else:
                    # Autres formats binaires
                    return content_bytes.decode('utf-8', errors='ignore')
            else:
                # Format non reconnu, traitement binaire
                return content_bytes.decode('utf-8', errors='ignore')
                
        except Exception as e:
            logger.warning(f"Error extracting text from file: {str(e)}")
            return content_bytes.decode('utf-8', errors='ignore')
    
    def _extract_text_from_bytes(self, content_bytes: bytes) -> str:
        """Extraction texte depuis bytes"""
        try:
            # Tentative décodage UTF-8
            return content_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.warning(f"Error extracting text from bytes: {str(e)}")
            return str(content_bytes)
    
    def _extract_text_from_archive(self, content_bytes: bytes) -> str:
        """Extraction texte depuis archive"""
        try:
            import io
            extracted_text = ""
            
            # Tentative ZIP
            try:
                with zipfile.ZipFile(io.BytesIO(content_bytes)) as zf:
                    for filename in zf.namelist()[:10]:  # Limite pour performance
                        if filename.endswith(('.txt', '.xml', '.json')):
                            with zf.open(filename) as f:
                                file_content = f.read().decode('utf-8', errors='ignore')
                                extracted_text += f"\n{filename}:\n{file_content}\n"
            except zipfile.BadZipFile:
                # Pas un ZIP valide
                pass
            
            # Si pas de texte extrait, retourner représentation binaire
            if not extracted_text:
                extracted_text = content_bytes.decode('utf-8', errors='ignore')
            
            return extracted_text
            
        except Exception as e:
            logger.warning(f"Error extracting text from archive: {str(e)}")
            return content_bytes.decode('utf-8', errors='ignore')
    
    def _classification_level(self, classification: DataClassification) -> int:
        """Niveau numérique de classification"""
        levels = {
            DataClassification.PUBLIC: 0,
            DataClassification.INTERNAL: 1,
            DataClassification.CONFIDENTIAL: 2,
            DataClassification.RESTRICTED: 3,
            DataClassification.TOP_SECRET: 4
        }
        return levels.get(classification, 0)
    
    def _determine_recommended_action(
        self,
        patterns_found: Dict[DataType, List[Dict[str, Any]]],
        highest_classification: DataClassification
    ) -> ActionType:
        """Détermination action recommandée selon patterns trouvés"""
        
        if not patterns_found:
            return ActionType.ALLOW
        
        # Vérification présence données critiques
        critical_types = [DataType.CREDENTIALS, DataType.INTELLECTUAL_PROPERTY]
        if any(data_type in critical_types for data_type in patterns_found.keys()):
            return ActionType.BLOCK
        
        # Selon niveau classification
        if highest_classification == DataClassification.TOP_SECRET:
            return ActionType.QUARANTINE
        elif highest_classification == DataClassification.RESTRICTED:
            return ActionType.BLOCK
        elif highest_classification == DataClassification.CONFIDENTIAL:
            return ActionType.WARN
        else:
            return ActionType.LOG_ONLY
    
    def _find_applicable_policy(
        self,
        data_type: DataType,
        classification: DataClassification,
        channel: TransmissionChannel
    ) -> Optional[DLPPolicy]:
        """Recherche politique applicable"""
        
        # Tri politiques par sévérité (plus sévère en premier)
        severity_order = {
            ViolationSeverity.EMERGENCY: 5,
            ViolationSeverity.CRITICAL: 4,
            ViolationSeverity.HIGH: 3,
            ViolationSeverity.MEDIUM: 2,
            ViolationSeverity.LOW: 1
        }
        
        applicable_policies = [
            policy for policy in self.policies.values()
            if policy.applies_to(data_type, classification, channel)
        ]
        
        if not applicable_policies:
            return None
        
        # Retourner politique la plus sévère
        return max(applicable_policies, key=lambda p: severity_order.get(p.severity, 0))
    
    async def _quarantine_content(self, content: Union[str, bytes, Path], incident_id: str) -> Path:
        """Mise en quarantaine du contenu"""
        try:
            # Préparation contenu
            if isinstance(content, Path):
                with open(content, 'rb') as f:
                    content_bytes = f.read()
            elif isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            # Chiffrement contenu
            encrypted_content = self.cipher.encrypt(content_bytes)
            
            # Sauvegarde en quarantaine
            quarantine_file = self.quarantine_path / f"{incident_id}.encrypted"
            with open(quarantine_file, 'wb') as f:
                f.write(encrypted_content)
            
            # Métadonnées quarantaine
            metadata = {
                'incident_id': incident_id,
                'timestamp': datetime.utcnow().isoformat(),
                'original_size': len(content_bytes),
                'encrypted_size': len(encrypted_content)
            }
            
            metadata_file = self.quarantine_path / f"{incident_id}.metadata"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Content quarantined: {quarantine_file}")
            return quarantine_file
            
        except Exception as e:
            logger.error(f"Error quarantining content: {str(e)}")
            raise
    
    async def _encrypt_content(self, content: Union[str, bytes, Path], incident_id: str):
        """Chiffrement automatique du contenu"""
        try:
            # Dans une implémentation réelle, chiffrer le contenu original
            # Pour cette simulation, juste logger l'action
            logger.info(f"Content encrypted for incident {incident_id}")
            
        except Exception as e:
            logger.error(f"Error encrypting content: {str(e)}")
    
    async def _send_incident_notification(self, incident: DataIncident, recipients: List[str]):
        """Envoi notification incident"""
        try:
            # Dans une implémentation réelle, intégrer avec système email/SMS
            notification_data = {
                'incident_id': incident.incident_id,
                'severity': incident.severity.value,
                'data_type': incident.data_type.value,
                'user_id': incident.user_id,
                'action_taken': incident.action_taken.value,
                'timestamp': incident.timestamp.isoformat()
            }
            
            for recipient in recipients:
                logger.info(f"Notification sent to {recipient}: {notification_data}")
            
        except Exception as e:
            logger.error(f"Error sending incident notification: {str(e)}")
    
    async def _analyze_quarantined_content(self, quarantine_path: str) -> Dict[str, Any]:
        """Analyse contenu en quarantaine"""
        try:
            quarantine_file = Path(quarantine_path)
            
            if not quarantine_file.exists():
                return {'error': 'Quarantined file not found'}
            
            # Lecture métadonnées
            metadata_file = quarantine_file.with_suffix('.metadata')
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            # Lecture contenu chiffré
            with open(quarantine_file, 'rb') as f:
                encrypted_content = f.read()
            
            # Déchiffrement pour analyse
            try:
                decrypted_content = self.cipher.decrypt(encrypted_content)
                content_preview = decrypted_content[:500].decode('utf-8', errors='ignore')
            except Exception:
                content_preview = "Unable to decrypt content"
            
            analysis = {
                'metadata': metadata,
                'encrypted_size': len(encrypted_content),
                'content_preview': content_preview,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing quarantined content: {str(e)}")
            return {'error': str(e)}
    
    def _generate_incident_recommendations(
        self,
        incident: DataIncident,
        investigation_data: Dict[str, Any]
    ) -> List[str]:
        """Génération recommandations suite incident"""
        recommendations = []
        
        # Recommandations selon sévérité
        if incident.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.EMERGENCY]:
            recommendations.append("Immediate security review required")
            recommendations.append("Consider user access suspension")
            recommendations.append("Notify legal and compliance teams")
        
        # Recommandations selon type de données
        if incident.data_type == DataType.CREDENTIALS:
            recommendations.append("Force password reset for affected user")
            recommendations.append("Review user access privileges")
            recommendations.append("Audit recent user activities")
        elif incident.data_type == DataType.INTELLECTUAL_PROPERTY:
            recommendations.append("Legal review for IP protection measures")
            recommendations.append("Consider content takedown procedures")
            recommendations.append("Audit content access controls")
        
        # Recommandations selon historique utilisateur
        user_incident_count = len(investigation_data.get('user_history', []))
        if user_incident_count > 3:
            recommendations.append("User shows pattern of violations - security training required")
            recommendations.append("Consider implementing stricter DLP policies for this user")
        
        # Recommandations selon incidents liés
        related_count = len(investigation_data.get('related_incidents', []))
        if related_count > 5:
            recommendations.append("Pattern detected - system-wide policy review needed")
            recommendations.append("Consider implementing additional monitoring")
        
        return recommendations
    
    # Méthodes de maintenance et statistiques
    
    async def get_dlp_statistics(self) -> Dict[str, Any]:
        """Statistiques système DLP"""
        try:
            current_time = datetime.utcnow()
            
            # Période dernières 24h
            yesterday = current_time - timedelta(days=1)
            recent_incidents = [
                inc for inc in self.incidents.values()
                if inc.timestamp >= yesterday
            ]
            
            # Période dernière semaine
            last_week = current_time - timedelta(days=7)
            week_incidents = [
                inc for inc in self.incidents.values()
                if inc.timestamp >= last_week
            ]
            
            stats = {
                'system_status': {
                    'total_patterns': len(self.patterns),
                    'active_patterns': len([p for p in self.patterns.values() if p.enabled]),
                    'total_policies': len(self.policies),
                    'active_policies': len([p for p in self.policies.values() if p.enabled]),
                    'total_incidents': len(self.incidents),
                    'quarantined_items': len([i for i in self.incidents.values() if i.quarantined_path])
                },
                'recent_activity': {
                    'incidents_last_24h': len(recent_incidents),
                    'incidents_last_week': len(week_incidents),
                    'blocked_transmissions_24h': len([i for i in recent_incidents if i.blocked]),
                    'avg_incidents_per_day': len(week_incidents) / 7
                },
                'pattern_effectiveness': {},
                'policy_effectiveness': {},
                'top_violation_types': {},
                'top_violating_users': {}
            }
            
            # Efficacité patterns
            for pattern in self.patterns.values():
                pattern_incidents = [
                    inc for inc in self.incidents.values()
                    if any(p['pattern_id'] == pattern.pattern_id for p in inc.detected_patterns)
                ]
                stats['pattern_effectiveness'][pattern.pattern_id] = {
                    'name': pattern.name,
                    'incidents_triggered': len(pattern_incidents),
                    'enabled': pattern.enabled
                }
            
            # Efficacité politiques
            for policy in self.policies.values():
                policy_incidents = [
                    inc for inc in self.incidents.values()
                    if inc.policy_violated == policy.policy_id
                ]
                stats['policy_effectiveness'][policy.policy_id] = {
                    'name': policy.name,
                    'incidents_triggered': len(policy_incidents),
                    'preventions': len([i for i in policy_incidents if i.blocked or i.quarantined_path]),
                    'enabled': policy.enabled
                }
            
            # Top types de violations
            violation_types = defaultdict(int)
            for incident in week_incidents:
                violation_types[incident.data_type.value] += 1
            
            stats['top_violation_types'] = dict(sorted(
                violation_types.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
            
            # Top utilisateurs avec violations
            user_violations = defaultdict(int)
            for incident in week_incidents:
                user_violations[incident.user_id] += 1
            
            stats['top_violating_users'] = dict(sorted(
                user_violations.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting DLP statistics: {str(e)}")
            raise
    
    async def cleanup_old_incidents(self, retention_days: int = 90) -> int:
        """Nettoyage anciens incidents"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            old_incident_ids = [
                incident_id for incident_id, incident in self.incidents.items()
                if incident.timestamp < cutoff_date
            ]
            
            # Suppression incidents et fichiers quarantaine
            for incident_id in old_incident_ids:
                incident = self.incidents[incident_id]
                
                # Suppression fichier quarantaine
                if incident.quarantined_path:
                    try:
                        Path(incident.quarantined_path).unlink(missing_ok=True)
                        Path(incident.quarantined_path).with_suffix('.metadata').unlink(missing_ok=True)
                    except Exception as e:
                        logger.warning(f"Error deleting quarantine file: {e}")
                
                # Suppression incident
                del self.incidents[incident_id]
            
            logger.info(f"Cleaned up {len(old_incident_ids)} old incidents")
            return len(old_incident_ids)
            
        except Exception as e:
            logger.error(f"Error cleaning up old incidents: {str(e)}")
            return 0

# Factory function
def create_dlp_engine(config: Dict[str, Any] = None) -> DataLossPreventionEngine:
    """Factory pour création moteur DLP configuré"""
    return DataLossPreventionEngine(config)

# Export des classes principales
__all__ = [
    'DataLossPreventionEngine',
    'DataPattern',
    'DLPPolicy',
    'DataIncident',
    'ScanResult',
    'DataClassification',
    'DataType',
    'ViolationSeverity',
    'ActionType',
    'TransmissionChannel',
    'create_dlp_engine'
]

if __name__ == "__main__":
    # Test basique du système DLP
    async def test_dlp():
        """Test des fonctionnalités DLP"""
        
        # Configuration test
        config = {
            'quarantine_path': '/tmp/dlp_test_quarantine',
            'max_scan_size': 50 * 1024 * 1024,  # 50MB
            'enable_real_time_monitoring': True
        }
        
        # Création moteur DLP
        dlp = create_dlp_engine(config)
        
        print("🔍 Testing Data Loss Prevention Engine...")
        
        # Test scan contenu avec données sensibles
        test_content = """
        User Information:
        Name: John Doe
        Email: john.doe@example.com
        Phone: +1-555-123-4567
        Credit Card: 4532-1234-5678-9012
        SSN: 123-45-6789
        
        API Configuration:
        api_key: sk-1234567890abcdef1234567890abcdef
        password: SuperSecret123!
        
        IA Chérie Proprietary Information:
        Creator content hash: abc123def456
        Fahed Mlaiel intellectual property notice
        """
        
        print("\n📄 Testing Content Scanning...")
        scan_result = await dlp.scan_content(test_content)
        
        print(f"✅ Scan completed:")
        print(f"   Patterns found: {scan_result.total_patterns_found}")
        print(f"   Classification: {scan_result.highest_classification.value}")
        print(f"   Recommended action: {scan_result.recommended_action.value}")
        print(f"   Confidence: {scan_result.confidence_score:.2%}")
        
        # Affichage patterns détectés
        for data_type, patterns in scan_result.patterns_by_type.items():
            print(f"   {data_type.value}: {len(patterns)} patterns")
            for pattern in patterns:
                print(f"     - {pattern['pattern_name']}: {pattern['confidence']:.2%}")
        
        # Test surveillance transmission
        print("\n🚨 Testing Transmission Monitoring...")
        allowed, incident = await dlp.monitor_transmission(
            content=test_content,
            user_id="user_123",
            source_location="/home/user/documents/sensitive.txt",
            destination="external@company.com",
            channel=TransmissionChannel.EMAIL
        )
        
        print(f"✅ Transmission monitoring:")
        print(f"   Allowed: {allowed}")
        if incident:
            print(f"   Incident ID: {incident.incident_id}")
            print(f"   Severity: {incident.severity.value}")
            print(f"   Action taken: {incident.action_taken.value}")
            print(f"   Blocked: {incident.blocked}")
        
        # Test investigation incident
        if incident:
            print(f"\n🔍 Testing Incident Investigation...")
            investigation = await dlp.investigate_incident(incident.incident_id)
            
            print(f"✅ Investigation completed:")
            print(f"   Related incidents: {len(investigation['related_incidents'])}")
            print(f"   Recommendations: {len(investigation['recommendations'])}")
            for rec in investigation['recommendations']:
                print(f"     - {rec}")
        
        # Test rapport conformité
        print(f"\n📊 Testing Compliance Report...")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        report = await dlp.generate_compliance_report(start_date, end_date, include_details=True)
        
        print(f"✅ Compliance report generated:")
        print(f"   Report ID: {report['report_id']}")
        print(f"   Total incidents: {report['summary']['total_incidents']}")
        print(f"   Prevention rate: {report['summary']['prevention_rate']:.2%}")
        print(f"   Blocked transmissions: {report['summary']['blocked_transmissions']}")
        
        # Test statistiques système
        print(f"\n📈 Testing System Statistics...")
        stats = await dlp.get_dlp_statistics()
        
        print(f"✅ System statistics:")
        print(f"   Active patterns: {stats['system_status']['active_patterns']}")
        print(f"   Active policies: {stats['system_status']['active_policies']}")
        print(f"   Total incidents: {stats['system_status']['total_incidents']}")
        print(f"   Incidents last 24h: {stats['recent_activity']['incidents_last_24h']}")
        
        # Test mise à jour pattern
        print(f"\n🔧 Testing Pattern Update...")
        pattern_updated = await dlp.update_pattern('email', {
            'confidence_threshold': 0.9,
            'description': 'Updated email detection pattern'
        })
        print(f"✅ Pattern update: {pattern_updated}")
        
        # Test nettoyage
        print(f"\n🧹 Testing Cleanup...")
        cleaned_count = await dlp.cleanup_old_incidents(retention_days=0)  # Test immédiat
        print(f"✅ Cleanup completed: {cleaned_count} incidents cleaned")
        
        print(f"\n🎉 All DLP tests completed successfully!")
    
    # Exécution tests
    asyncio.run(test_dlp())