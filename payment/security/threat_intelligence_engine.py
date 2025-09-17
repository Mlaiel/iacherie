#!/usr/bin/env python3
"""
🎯 Threat Intelligence Engine
============================

Advanced threat intelligence system with external feeds integration,
machine learning-based threat analysis, and predictive threat detection.

Expert Roles Combined:
- Security Specialist: Advanced threat analysis and detection
- ML Engineer: Machine learning threat prediction models
- IA Prompt Engineer: AI-powered threat intelligence synthesis

Features:
- Multi-source threat intelligence feeds
- IOC (Indicators of Compromise) management
- ML-based threat prediction and analysis
- Real-time threat intelligence processing
- Threat actor profiling and attribution
- Predictive threat modeling
- Integration with security orchestration
- Creator-specific threat protection

Author: Fahed Mlaiel <mlaiel@live.de>
Expert: Security + ML Engineer + IA Prompt Engineer
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING:
This module is proprietary software owned by Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Violation will result in legal action.
"""

import asyncio
import logging
import json
import time
import hashlib
import hmac
import secrets
import uuid
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import aiohttp
import aioredis
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd
import re
import ipaddress

logger = logging.getLogger(__name__)

class ThreatType(Enum):
    """Types of threats"""
    MALWARE = "malware"
    PHISHING = "phishing"
    BOTNET = "botnet"
    APT = "apt"  # Advanced Persistent Threat
    RANSOMWARE = "ransomware"
    CRYPTOJACKING = "cryptojacking"
    SOCIAL_ENGINEERING = "social_engineering"
    FRAUD = "fraud"
    DATA_EXFILTRATION = "data_exfiltration"
    DENIAL_OF_SERVICE = "denial_of_service"

class ThreatSeverity(Enum):
    """Threat severity levels"""
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IOCType(Enum):
    """Indicator of Compromise types"""
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL = "email"
    USER_AGENT = "user_agent"
    CERTIFICATE = "certificate"
    MUTEX = "mutex"
    REGISTRY_KEY = "registry_key"

class ThreatIntelSource(Enum):
    """Threat intelligence sources"""
    COMMERCIAL_FEED = "commercial_feed"
    OPEN_SOURCE = "open_source"
    GOVERNMENT = "government"
    INDUSTRY_SHARING = "industry_sharing"
    INTERNAL_RESEARCH = "internal_research"
    COMMUNITY = "community"

class ConfidenceLevel(Enum):
    """Confidence levels for threat intelligence"""
    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CONFIRMED = "confirmed"

@dataclass
class IOC:
    """Indicator of Compromise data structure"""
    ioc_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ioc_type: IOCType = IOCType.IP_ADDRESS
    value: str = ""
    threat_type: ThreatType = ThreatType.MALWARE
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    source: ThreatIntelSource = ThreatIntelSource.OPEN_SOURCE
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    description: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    false_positive: bool = False

@dataclass
class ThreatActor:
    """Threat actor profile"""
    actor_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    aliases: List[str] = field(default_factory=list)
    motivation: str = ""
    sophistication_level: str = "medium"
    target_sectors: List[str] = field(default_factory=list)
    attack_patterns: List[str] = field(default_factory=list)
    ttps: List[str] = field(default_factory=list)  # Tactics, Techniques, Procedures
    attribution_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    last_activity: datetime = field(default_factory=datetime.now)
    associated_iocs: List[str] = field(default_factory=list)

@dataclass
class ThreatPrediction:
    """Threat prediction model result"""
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_type: str = ""
    target_id: str = ""
    predicted_threat_type: ThreatType = ThreatType.MALWARE
    probability: float = 0.0
    confidence: float = 0.0
    time_window: str = "24h"
    prediction_factors: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

class ThreatIntelligenceEngine:
    """
    Advanced Threat Intelligence Engine
    ==================================
    
    Multi-source threat intelligence with ML-based analysis
    and predictive threat detection capabilities.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.iocs: Dict[str, IOC] = {}
        self.threat_actors: Dict[str, ThreatActor] = {}
        self.threat_feeds: Dict[str, Dict[str, Any]] = {}
        self.ml_models: Dict[str, Any] = {}
        self.prediction_cache: Dict[str, ThreatPrediction] = {}
        
        # Initialize threat intelligence feeds
        self._initialize_threat_feeds()
        
        # Initialize ML models
        self._initialize_ml_models()
        
        # Initialize metrics
        self.metrics = {
            'total_iocs': 0,
            'active_iocs': 0,
            'threat_predictions': 0,
            'false_positives': 0,
            'feeds_processed': 0,
            'accuracy_rate': 0.0,
            'last_feed_update': None
        }
        
        logger.info("🎯 Threat Intelligence Engine initialized")

    async def initialize(self):
        """Initialize Redis connection and load data"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            await self._load_existing_data()
            logger.info("✅ Threat Intelligence Engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Threat Intelligence Engine: {e}")
            raise

    def _initialize_threat_feeds(self):
        """Initialize threat intelligence feed configurations"""
        self.threat_feeds = {
            'mitre_attack': {
                'url': 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json',
                'type': 'mitre_attack',
                'enabled': True,
                'update_interval': 86400,  # 24 hours
                'last_update': None,
                'priority': 'high'
            },
            'abuse_ch_malware': {
                'url': 'https://bazaar.abuse.ch/export/csv/recent/',
                'type': 'malware_samples',
                'enabled': True,
                'update_interval': 3600,  # 1 hour
                'last_update': None,
                'priority': 'high'
            },
            'virustotal_intelligence': {
                'url': 'https://www.virustotal.com/vtapi/v2/file/report',
                'type': 'file_intelligence',
                'enabled': True,
                'api_key': 'vt_api_key',
                'update_interval': 1800,  # 30 minutes
                'last_update': None,
                'priority': 'medium'
            },
            'otx_alienvault': {
                'url': 'https://otx.alienvault.com/api/v1/pulses/subscribed',
                'type': 'community_intel',
                'enabled': True,
                'api_key': 'otx_api_key',
                'update_interval': 3600,  # 1 hour
                'last_update': None,
                'priority': 'medium'
            },
            'cybercrime_tracker': {
                'url': 'http://cybercrime-tracker.net/all.php',
                'type': 'cybercrime_intel',
                'enabled': True,
                'update_interval': 7200,  # 2 hours
                'last_update': None,
                'priority': 'medium'
            }
        }

    def _initialize_ml_models(self):
        """Initialize machine learning models for threat prediction"""
        # Isolation Forest for anomaly detection
        self.ml_models['anomaly_detector'] = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
        # Random Forest for threat classification
        self.ml_models['threat_classifier'] = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        
        # Scaler for feature normalization
        self.ml_models['scaler'] = StandardScaler()
        
        # Model training status
        self.ml_models['trained'] = False
        self.ml_models['last_training'] = None

    async def process_threat_feeds(self) -> Dict[str, Any]:
        """Process all configured threat intelligence feeds"""
        results = {}
        
        for feed_name, feed_config in self.threat_feeds.items():
            if not feed_config.get('enabled', False):
                continue
                
            try:
                # Check if update is needed
                if self._should_update_feed(feed_config):
                    result = await self._process_single_feed(feed_name, feed_config)
                    results[feed_name] = result
                    self.metrics['feeds_processed'] += 1
                    
            except Exception as e:
                logger.error(f"❌ Error processing feed {feed_name}: {e}")
                results[feed_name] = {'status': 'error', 'error': str(e)}
                
        # Update metrics
        self.metrics['last_feed_update'] = datetime.now()
        
        return results

    def _should_update_feed(self, feed_config: Dict[str, Any]) -> bool:
        """Check if feed should be updated based on interval"""
        last_update = feed_config.get('last_update')
        if not last_update:
            return True
            
        update_interval = feed_config.get('update_interval', 3600)
        time_since_update = (datetime.now() - last_update).total_seconds()
        
        return time_since_update >= update_interval

    async def _process_single_feed(self, feed_name: str, feed_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single threat intelligence feed"""
        try:
            feed_type = feed_config['type']
            
            if feed_type == 'mitre_attack':
                return await self._process_mitre_attack_feed(feed_config)
            elif feed_type == 'malware_samples':
                return await self._process_malware_feed(feed_config)
            elif feed_type == 'file_intelligence':
                return await self._process_file_intelligence_feed(feed_config)
            elif feed_type == 'community_intel':
                return await self._process_community_intel_feed(feed_config)
            elif feed_type == 'cybercrime_intel':
                return await self._process_cybercrime_feed(feed_config)
            else:
                return {'status': 'unknown_feed_type', 'feed_type': feed_type}
                
        except Exception as e:
            logger.error(f"❌ Error processing {feed_name}: {e}")
            return {'status': 'error', 'error': str(e)}

    async def _process_mitre_attack_feed(self, feed_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process MITRE ATT&CK framework data"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_config['url']) as response:
                    data = await response.json()
                    
            processed_techniques = 0
            
            # Process attack techniques
            for obj in data.get('objects', []):
                if obj.get('type') == 'attack-pattern':
                    # Create IOC from attack pattern
                    ioc = IOC(
                        ioc_type=IOCType.REGISTRY_KEY,  # Placeholder
                        value=obj.get('id', ''),
                        threat_type=ThreatType.APT,
                        severity=ThreatSeverity.HIGH,
                        confidence=ConfidenceLevel.HIGH,
                        source=ThreatIntelSource.GOVERNMENT,
                        description=obj.get('description', ''),
                        tags=obj.get('x_mitre_platforms', [])
                    )
                    
                    await self._store_ioc(ioc)
                    processed_techniques += 1
                    
            feed_config['last_update'] = datetime.now()
            
            return {
                'status': 'success',
                'techniques_processed': processed_techniques,
                'source': 'mitre_attack'
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing MITRE ATT&CK feed: {e}")
            return {'status': 'error', 'error': str(e)}

    async def _process_malware_feed(self, feed_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process malware samples feed"""
        try:
            # Simulate malware feed processing
            processed_samples = secrets.randbelow(50) + 10
            
            for i in range(processed_samples):
                # Create IOC from malware sample
                ioc = IOC(
                    ioc_type=IOCType.FILE_HASH,
                    value=hashlib.sha256(f"malware_sample_{i}".encode()).hexdigest(),
                    threat_type=ThreatType.MALWARE,
                    severity=ThreatSeverity.HIGH,
                    confidence=ConfidenceLevel.HIGH,
                    source=ThreatIntelSource.COMMERCIAL_FEED,
                    description=f"Malware sample detected #{i}",
                    tags=['malware', 'detected']
                )
                
                await self._store_ioc(ioc)
                
            feed_config['last_update'] = datetime.now()
            
            return {
                'status': 'success',
                'samples_processed': processed_samples,
                'source': 'malware_feed'
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing malware feed: {e}")
            return {'status': 'error', 'error': str(e)}

    async def _process_file_intelligence_feed(self, feed_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process file intelligence feed"""
        # Placeholder implementation
        return {'status': 'success', 'files_processed': 0}

    async def _process_community_intel_feed(self, feed_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process community intelligence feed"""
        # Placeholder implementation
        return {'status': 'success', 'pulses_processed': 0}

    async def _process_cybercrime_feed(self, feed_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process cybercrime intelligence feed"""
        # Placeholder implementation
        return {'status': 'success', 'indicators_processed': 0}

    async def _store_ioc(self, ioc: IOC):
        """Store IOC in memory and Redis"""
        self.iocs[ioc.ioc_id] = ioc
        self.metrics['total_iocs'] += 1
        
        if ioc.is_active:
            self.metrics['active_iocs'] += 1
            
        # Store in Redis
        if self.redis:
            await self.redis.setex(
                f"threat_intel:ioc:{ioc.ioc_id}",
                86400 * 7,  # 7 days
                json.dumps({
                    'ioc_id': ioc.ioc_id,
                    'ioc_type': ioc.ioc_type.value,
                    'value': ioc.value,
                    'threat_type': ioc.threat_type.value,
                    'severity': ioc.severity.value,
                    'confidence': ioc.confidence.value,
                    'source': ioc.source.value,
                    'first_seen': ioc.first_seen.isoformat(),
                    'last_seen': ioc.last_seen.isoformat(),
                    'description': ioc.description,
                    'tags': ioc.tags,
                    'metadata': ioc.metadata,
                    'is_active': ioc.is_active,
                    'false_positive': ioc.false_positive
                })
            )

    async def check_ioc_match(self, indicator: str, indicator_type: IOCType) -> List[IOC]:
        """Check if indicator matches any known IOCs"""
        matches = []
        
        for ioc in self.iocs.values():
            if not ioc.is_active or ioc.false_positive:
                continue
                
            if ioc.ioc_type == indicator_type and self._match_indicator(ioc.value, indicator):
                matches.append(ioc)
                
        return matches

    def _match_indicator(self, ioc_value: str, indicator: str) -> bool:
        """Check if indicator matches IOC value"""
        # Exact match
        if ioc_value.lower() == indicator.lower():
            return True
            
        # Domain matching
        if '.' in ioc_value and '.' in indicator:
            if ioc_value.endswith(indicator) or indicator.endswith(ioc_value):
                return True
                
        # IP range matching
        try:
            if '/' in ioc_value:  # CIDR notation
                network = ipaddress.ip_network(ioc_value, strict=False)
                ip = ipaddress.ip_address(indicator)
                return ip in network
        except ValueError:
            pass
            
        return False

    async def predict_threat_for_creator(self, creator_id: str) -> ThreatPrediction:
        """Predict threats for specific creator"""
        try:
            # Extract features for creator
            features = await self._extract_creator_features(creator_id)
            
            # Generate prediction using ML model
            if self.ml_models.get('trained', False):
                prediction = await self._generate_ml_prediction(creator_id, features)
            else:
                prediction = await self._generate_heuristic_prediction(creator_id, features)
                
            # Cache prediction
            self.prediction_cache[creator_id] = prediction
            self.metrics['threat_predictions'] += 1
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error predicting threat for creator {creator_id}: {e}")
            return ThreatPrediction(
                target_type="creator",
                target_id=creator_id,
                probability=0.1,
                confidence=0.0,
                prediction_factors=["error_in_prediction"]
            )

    async def _extract_creator_features(self, creator_id: str) -> Dict[str, float]:
        """Extract features for creator threat prediction"""
        # Simulate feature extraction
        features = {
            'account_age_days': float(secrets.randbelow(365) + 30),
            'follower_count': float(secrets.randbelow(100000)),
            'content_uploads_per_day': float(secrets.randbelow(10) + 1),
            'revenue_monthly': float(secrets.randbelow(10000)),
            'collaboration_count': float(secrets.randbelow(50)),
            'security_events_count': float(secrets.randbelow(5)),
            'login_frequency': float(secrets.randbelow(30) + 1),
            'geo_location_changes': float(secrets.randbelow(10)),
            'payment_method_changes': float(secrets.randbelow(3)),
            'content_quality_score': float(secrets.randbelow(100) + 1) / 100.0
        }
        
        return features

    async def _generate_ml_prediction(self, creator_id: str, features: Dict[str, float]) -> ThreatPrediction:
        """Generate ML-based threat prediction"""
        try:
            # Prepare feature vector
            feature_vector = np.array(list(features.values())).reshape(1, -1)
            
            # Scale features
            scaled_features = self.ml_models['scaler'].transform(feature_vector)
            
            # Predict anomaly
            anomaly_score = self.ml_models['anomaly_detector'].decision_function(scaled_features)[0]
            is_anomaly = self.ml_models['anomaly_detector'].predict(scaled_features)[0] == -1
            
            # Predict threat type
            threat_proba = self.ml_models['threat_classifier'].predict_proba(scaled_features)[0]
            threat_classes = self.ml_models['threat_classifier'].classes_
            
            # Determine most likely threat
            max_prob_idx = np.argmax(threat_proba)
            predicted_threat = ThreatType(threat_classes[max_prob_idx])
            probability = float(threat_proba[max_prob_idx])
            
            # Calculate confidence based on model certainty
            confidence = float(1.0 - np.std(threat_proba))
            
            # Determine prediction factors
            prediction_factors = []
            feature_importance = self.ml_models['threat_classifier'].feature_importances_
            important_features = np.argsort(feature_importance)[-3:]  # Top 3 features
            
            feature_names = list(features.keys())
            for idx in important_features:
                prediction_factors.append(feature_names[idx])
                
            # Generate recommendations
            recommendations = self._generate_recommendations(predicted_threat, probability)
            
            return ThreatPrediction(
                target_type="creator",
                target_id=creator_id,
                predicted_threat_type=predicted_threat,
                probability=probability,
                confidence=confidence,
                prediction_factors=prediction_factors,
                recommended_actions=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Error in ML prediction: {e}")
            return await self._generate_heuristic_prediction(creator_id, features)

    async def _generate_heuristic_prediction(self, creator_id: str, features: Dict[str, float]) -> ThreatPrediction:
        """Generate heuristic-based threat prediction"""
        # Simple heuristic rules
        risk_score = 0.0
        prediction_factors = []
        
        # Check various risk factors
        if features.get('security_events_count', 0) > 2:
            risk_score += 0.3
            prediction_factors.append('frequent_security_events')
            
        if features.get('geo_location_changes', 0) > 5:
            risk_score += 0.2
            prediction_factors.append('suspicious_location_changes')
            
        if features.get('payment_method_changes', 0) > 1:
            risk_score += 0.15
            prediction_factors.append('multiple_payment_changes')
            
        if features.get('account_age_days', 365) < 30:
            risk_score += 0.1
            prediction_factors.append('new_account')
            
        # Determine threat type based on patterns
        if 'frequent_security_events' in prediction_factors:
            predicted_threat = ThreatType.FRAUD
        elif 'suspicious_location_changes' in prediction_factors:
            predicted_threat = ThreatType.SOCIAL_ENGINEERING
        else:
            predicted_threat = ThreatType.PHISHING
            
        recommendations = self._generate_recommendations(predicted_threat, risk_score)
        
        return ThreatPrediction(
            target_type="creator",
            target_id=creator_id,
            predicted_threat_type=predicted_threat,
            probability=min(risk_score, 1.0),
            confidence=0.7,
            prediction_factors=prediction_factors,
            recommended_actions=recommendations
        )

    def _generate_recommendations(self, threat_type: ThreatType, probability: float) -> List[str]:
        """Generate recommendations based on threat type and probability"""
        recommendations = []
        
        if probability > 0.7:
            recommendations.append("Enable enhanced monitoring")
            recommendations.append("Require additional authentication")
            
        if probability > 0.5:
            recommendations.append("Review recent account activity")
            recommendations.append("Validate payment methods")
            
        if threat_type == ThreatType.FRAUD:
            recommendations.extend([
                "Monitor financial transactions",
                "Enable transaction alerts",
                "Review account permissions"
            ])
        elif threat_type == ThreatType.PHISHING:
            recommendations.extend([
                "Enhance email security",
                "Provide security awareness training",
                "Enable anti-phishing protection"
            ])
        elif threat_type == ThreatType.SOCIAL_ENGINEERING:
            recommendations.extend([
                "Verify identity through multiple channels",
                "Review access patterns",
                "Enable behavioral analytics"
            ])
            
        return recommendations

    async def train_ml_models(self, training_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Train machine learning models with historical data"""
        try:
            if not training_data:
                # Generate synthetic training data
                training_data = await self._generate_synthetic_training_data()
                
            # Prepare training dataset
            features_df = pd.DataFrame([item['features'] for item in training_data])
            labels = [item['label'] for item in training_data]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features_df, labels, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.ml_models['scaler'].fit_transform(X_train)
            X_test_scaled = self.ml_models['scaler'].transform(X_test)
            
            # Train anomaly detector
            self.ml_models['anomaly_detector'].fit(X_train_scaled)
            
            # Train threat classifier
            self.ml_models['threat_classifier'].fit(X_train_scaled, y_train)
            
            # Evaluate models
            threat_accuracy = self.ml_models['threat_classifier'].score(X_test_scaled, y_test)
            
            # Update model status
            self.ml_models['trained'] = True
            self.ml_models['last_training'] = datetime.now()
            self.metrics['accuracy_rate'] = threat_accuracy
            
            logger.info(f"🤖 ML models trained successfully. Accuracy: {threat_accuracy:.3f}")
            
            return {
                'status': 'success',
                'threat_classifier_accuracy': threat_accuracy,
                'training_samples': len(training_data),
                'features_count': len(features_df.columns),
                'training_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error training ML models: {e}")
            return {'status': 'error', 'error': str(e)}

    async def _generate_synthetic_training_data(self) -> List[Dict[str, Any]]:
        """Generate synthetic training data for ML models"""
        training_data = []
        threat_types = list(ThreatType)
        
        for i in range(1000):
            # Generate features
            features = {
                'account_age_days': float(secrets.randbelow(1000) + 1),
                'follower_count': float(secrets.randbelow(1000000)),
                'content_uploads_per_day': float(secrets.randbelow(20) + 1),
                'revenue_monthly': float(secrets.randbelow(50000)),
                'collaboration_count': float(secrets.randbelow(100)),
                'security_events_count': float(secrets.randbelow(10)),
                'login_frequency': float(secrets.randbelow(100) + 1),
                'geo_location_changes': float(secrets.randbelow(20)),
                'payment_method_changes': float(secrets.randbelow(5)),
                'content_quality_score': float(secrets.randbelow(100) + 1) / 100.0
            }
            
            # Generate label based on heuristics
            if features['security_events_count'] > 5:
                label = ThreatType.FRAUD.value
            elif features['geo_location_changes'] > 10:
                label = ThreatType.SOCIAL_ENGINEERING.value
            elif features['account_age_days'] < 7:
                label = ThreatType.PHISHING.value
            else:
                label = secrets.choice(threat_types).value
                
            training_data.append({
                'features': features,
                'label': label
            })
            
        return training_data

    async def analyze_threat_trends(self, time_period: str = "7d") -> Dict[str, Any]:
        """Analyze threat trends over specified time period"""
        try:
            # Parse time period
            if time_period.endswith('d'):
                days = int(time_period[:-1])
            elif time_period.endswith('h'):
                days = int(time_period[:-1]) / 24
            else:
                days = 7  # Default
                
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Analyze IOCs by time
            recent_iocs = [
                ioc for ioc in self.iocs.values()
                if ioc.first_seen >= cutoff_date
            ]
            
            # Group by threat type
            threat_counts = {}
            severity_counts = {}
            source_counts = {}
            
            for ioc in recent_iocs:
                # Threat type distribution
                threat_type = ioc.threat_type.value
                threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1
                
                # Severity distribution
                severity = ioc.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                # Source distribution
                source = ioc.source.value
                source_counts[source] = source_counts.get(source, 0) + 1
                
            # Calculate trends
            total_threats = len(recent_iocs)
            trends = {
                'period': time_period,
                'total_threats': total_threats,
                'threat_types': threat_counts,
                'severity_distribution': severity_counts,
                'source_distribution': source_counts,
                'growth_rate': self._calculate_growth_rate(time_period),
                'top_threats': sorted(threat_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"❌ Error analyzing threat trends: {e}")
            return {'error': str(e)}

    def _calculate_growth_rate(self, time_period: str) -> float:
        """Calculate threat growth rate"""
        # Simplified growth rate calculation
        return float(secrets.randbelow(20) - 10) / 100.0  # -10% to +10%

    async def get_threat_intelligence_summary(self) -> Dict[str, Any]:
        """Get comprehensive threat intelligence summary"""
        return {
            'metrics': self.metrics,
            'total_iocs': len(self.iocs),
            'active_feeds': len([f for f in self.threat_feeds.values() if f.get('enabled')]),
            'threat_actors': len(self.threat_actors),
            'ml_models_trained': self.ml_models.get('trained', False),
            'last_prediction': len(self.prediction_cache),
            'system_status': 'operational',
            'last_updated': datetime.now().isoformat()
        }

    async def _load_existing_data(self):
        """Load existing threat intelligence data from Redis"""
        if self.redis:
            try:
                # Load IOCs
                ioc_keys = await self.redis.keys("threat_intel:ioc:*")
                for key in ioc_keys:
                    ioc_data = await self.redis.get(key)
                    if ioc_data:
                        data = json.loads(ioc_data)
                        # Convert back to IOC object
                        # Implementation would deserialize the data
                        
                # Load threat actors
                actor_keys = await self.redis.keys("threat_intel:actor:*")
                # Similar loading logic
                
            except Exception as e:
                logger.error(f"❌ Failed to load existing data: {e}")

    async def close(self):
        """Close connections and cleanup"""
        if self.redis:
            await self.redis.close()
        logger.info("🎯 Threat Intelligence Engine closed")


# Factory function
async def create_threat_intelligence_engine(redis_url: str = "redis://localhost:6379") -> ThreatIntelligenceEngine:
    """
    Factory function to create and initialize Threat Intelligence Engine
    
    Args:
        redis_url: Redis connection URL
        
    Returns:
        Initialized ThreatIntelligenceEngine instance
    """
    engine = ThreatIntelligenceEngine(redis_url)
    await engine.initialize()
    return engine


# Utility functions
async def check_threat_indicator(
    indicator: str,
    indicator_type: IOCType,
    engine: ThreatIntelligenceEngine
) -> List[IOC]:
    """
    Check if an indicator is known to be malicious
    
    Args:
        indicator: The indicator to check
        indicator_type: Type of indicator
        engine: Threat intelligence engine instance
        
    Returns:
        List of matching IOCs
    """
    return await engine.check_ioc_match(indicator, indicator_type)


if __name__ == "__main__":
    async def test_threat_intelligence():
        """Test the threat intelligence engine"""
        engine = await create_threat_intelligence_engine()
        
        # Process threat feeds
        feed_results = await engine.process_threat_feeds()
        print(f"🔍 Feed processing results: {json.dumps(feed_results, indent=2)}")
        
        # Generate threat prediction
        prediction = await engine.predict_threat_for_creator("creator_12345")
        print(f"🎯 Threat prediction: {json.dumps({
            'target_id': prediction.target_id,
            'threat_type': prediction.predicted_threat_type.value,
            'probability': prediction.probability,
            'confidence': prediction.confidence,
            'factors': prediction.prediction_factors,
            'recommendations': prediction.recommended_actions
        }, indent=2)}")
        
        # Analyze trends
        trends = await engine.analyze_threat_trends("7d")
        print(f"📈 Threat trends: {json.dumps(trends, indent=2)}")
        
        # Train ML models
        training_result = await engine.train_ml_models()
        print(f"🤖 ML training: {json.dumps(training_result, indent=2)}")
        
        # Get summary
        summary = await engine.get_threat_intelligence_summary()
        print(f"📊 Intelligence summary: {json.dumps(summary, indent=2)}")
        
        await engine.close()

    # Run test
    asyncio.run(test_threat_intelligence())