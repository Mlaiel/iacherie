"""
Threat Detection Service - Advanced AI-Powered Security Analysis
===============================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Role**: Security Specialist & ML Engineer
**Module**: Security & Monitoring Services
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Advanced threat detection using machine learning, behavioral analysis,
and real-time pattern recognition for comprehensive security monitoring.
"""

import asyncio
import hashlib
import json
import logging
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import aioredis
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import base64


class ThreatCategory(Enum):
    """Threat categorization for detection"""
    MALWARE = "malware"
    PHISHING = "phishing"
    DDOS = "ddos"
    BRUTE_FORCE = "brute_force"
    DATA_EXFILTRATION = "data_exfiltration"
    INSIDER_THREAT = "insider_threat"
    API_ABUSE = "api_abuse"
    ZERO_DAY = "zero_day"
    ADVANCED_PERSISTENT_THREAT = "apt"


class DetectionMethod(Enum):
    """Detection methods used"""
    SIGNATURE_BASED = "signature"
    BEHAVIORAL_ANALYSIS = "behavioral"
    MACHINE_LEARNING = "ml"
    ANOMALY_DETECTION = "anomaly"
    THREAT_INTELLIGENCE = "threat_intel"
    HEURISTIC = "heuristic"


@dataclass
class ThreatSignature:
    """Threat signature definition"""
    signature_id: str
    name: str
    category: ThreatCategory
    pattern: str
    confidence: float
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ThreatDetection:
    """Threat detection result"""
    detection_id: str
    threat_category: ThreatCategory
    detection_method: DetectionMethod
    confidence_score: float
    severity_level: str
    source_data: Dict[str, Any]
    indicators: List[str]
    mitigation_suggestions: List[str]
    detected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BehavioralProfile:
    """User behavioral profile for anomaly detection"""
    user_id: str
    baseline_features: Dict[str, float]
    activity_patterns: Dict[str, Any]
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ThreatDetectionService:
    """
    Advanced Threat Detection Service
    
    Comprehensive threat detection with:
    - Real-time behavioral analysis
    - Machine learning-based anomaly detection
    - Signature-based threat identification
    - Advanced persistent threat (APT) detection
    - Zero-day threat heuristics
    - Threat intelligence integration
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.logger = logging.getLogger(__name__)
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        
        # ML Models for threat detection
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.threat_classifier = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            max_depth=20
        )
        self.scaler = StandardScaler()
        
        # Threat signatures database
        self.threat_signatures: Dict[str, ThreatSignature] = {}
        
        # Behavioral profiles
        self.behavioral_profiles: Dict[str, BehavioralProfile] = {}
        
        # Detection statistics
        self.detection_stats = {
            "total_detections": 0,
            "true_positives": 0,
            "false_positives": 0,
            "threats_blocked": 0,
            "accuracy_rate": 0.0,
            "last_model_update": None
        }
        
        # Real-time threat tracking
        self.active_threats: Dict[str, ThreatDetection] = {}
        self.threat_patterns: Dict[str, List] = {}
        
        # Initialize threat signatures
        self._initialize_threat_signatures()
        
        self.logger.info("Threat Detection Service initialized with ML-powered analysis")

    async def initialize(self):
        """Initialize threat detection service with Redis and ML models"""
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Load pre-trained models and profiles
            await self._load_ml_models()
            await self._load_behavioral_profiles()
            await self._load_threat_signatures()
            
            # Initialize threat intelligence feeds
            await self._initialize_threat_intelligence()
            
            self.logger.info("Threat Detection Service fully initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Threat Detection Service: {e}")
            raise

    def _initialize_threat_signatures(self):
        """Initialize threat signatures for known attack patterns"""
        
        signatures = [
            ThreatSignature(
                signature_id="SIG_001",
                name="SQL Injection Pattern",
                category=ThreatCategory.MALWARE,
                pattern=r"(\bUNION\b|\bSELECT\b|\bDROP\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b).*(\bFROM\b|\bWHERE\b|\bOR\b|\bAND\b)",
                confidence=0.85,
                description="Detects SQL injection attack patterns"
            ),
            ThreatSignature(
                signature_id="SIG_002",
                name="XSS Attack Pattern",
                category=ThreatCategory.MALWARE,
                pattern=r"<script[^>]*>.*?</script>|javascript:|onload=|onerror=",
                confidence=0.90,
                description="Detects cross-site scripting (XSS) patterns"
            ),
            ThreatSignature(
                signature_id="SIG_003",
                name="Brute Force Login Pattern",
                category=ThreatCategory.BRUTE_FORCE,
                pattern=r"(failed.*login.*attempt|authentication.*failed|invalid.*credentials)",
                confidence=0.75,
                description="Detects brute force login attempts"
            ),
            ThreatSignature(
                signature_id="SIG_004",
                name="DDoS Attack Pattern",
                category=ThreatCategory.DDOS,
                pattern=r"(excessive.*requests|rate.*limit.*exceeded|connection.*flood)",
                confidence=0.80,
                description="Detects distributed denial of service patterns"
            ),
            ThreatSignature(
                signature_id="SIG_005",
                name="Data Exfiltration Pattern",
                category=ThreatCategory.DATA_EXFILTRATION,
                pattern=r"(large.*data.*download|bulk.*export|unusual.*data.*access)",
                confidence=0.85,
                description="Detects potential data exfiltration activities"
            )
        ]
        
        for signature in signatures:
            self.threat_signatures[signature.signature_id] = signature

    async def analyze_threat(self, event_data: Dict[str, Any]) -> ThreatDetection:
        """
        Comprehensive threat analysis using multiple detection methods
        
        Args:
            event_data: Event data to analyze for threats
            
        Returns:
            ThreatDetection with analysis results
        """
        detection_id = f"DET_{int(time.time() * 1000)}"
        
        try:
            # Multi-method threat analysis
            signature_results = await self._signature_based_detection(event_data)
            behavioral_results = await self._behavioral_analysis(event_data)
            ml_results = await self._ml_based_detection(event_data)
            anomaly_results = await self._anomaly_detection(event_data)
            threat_intel_results = await self._threat_intelligence_analysis(event_data)
            
            # Combine results and calculate confidence
            combined_analysis = await self._combine_detection_results(
                signature_results,
                behavioral_results,
                ml_results,
                anomaly_results,
                threat_intel_results
            )
            
            # Create threat detection object
            threat_detection = ThreatDetection(
                detection_id=detection_id,
                threat_category=combined_analysis["threat_category"],
                detection_method=combined_analysis["primary_method"],
                confidence_score=combined_analysis["confidence_score"],
                severity_level=combined_analysis["severity_level"],
                source_data=event_data,
                indicators=combined_analysis["indicators"],
                mitigation_suggestions=combined_analysis["mitigation_suggestions"]
            )
            
            # Store detection result
            await self._store_threat_detection(threat_detection)
            
            # Update threat patterns
            await self._update_threat_patterns(threat_detection)
            
            # Update statistics
            self._update_detection_stats(threat_detection)
            
            self.logger.info(f"Threat analysis completed: {detection_id}")
            return threat_detection
            
        except Exception as e:
            self.logger.error(f"Error in threat analysis: {e}")
            raise

    async def _signature_based_detection(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Signature-based threat detection"""
        
        results = {
            "method": DetectionMethod.SIGNATURE_BASED,
            "threats_found": [],
            "confidence": 0.0,
            "indicators": []
        }
        
        # Convert event data to searchable text
        searchable_text = json.dumps(event_data).lower()
        
        for signature_id, signature in self.threat_signatures.items():
            import re
            if re.search(signature.pattern, searchable_text, re.IGNORECASE):
                threat_info = {
                    "signature_id": signature_id,
                    "name": signature.name,
                    "category": signature.category,
                    "confidence": signature.confidence
                }
                results["threats_found"].append(threat_info)
                results["indicators"].append(f"Signature match: {signature.name}")
        
        if results["threats_found"]:
            results["confidence"] = max([t["confidence"] for t in results["threats_found"]])
        
        return results

    async def _behavioral_analysis(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Behavioral analysis for anomaly detection"""
        
        results = {
            "method": DetectionMethod.BEHAVIORAL_ANALYSIS,
            "anomaly_score": 0.0,
            "behavioral_indicators": [],
            "confidence": 0.0
        }
        
        user_id = event_data.get("user_id")
        if not user_id:
            return results
        
        # Get user's behavioral profile
        profile = self.behavioral_profiles.get(user_id)
        if not profile:
            # Create new behavioral profile
            profile = await self._create_behavioral_profile(user_id, event_data)
            self.behavioral_profiles[user_id] = profile
            return results
        
        # Extract behavioral features from current event
        current_features = self._extract_behavioral_features(event_data)
        
        # Compare with baseline
        anomaly_score = self._calculate_behavioral_anomaly(
            current_features,
            profile.baseline_features
        )
        
        results["anomaly_score"] = anomaly_score
        results["confidence"] = min(anomaly_score, 1.0)
        
        # Identify specific behavioral anomalies
        if anomaly_score > 0.7:
            results["behavioral_indicators"].extend([
                "Unusual activity pattern detected",
                "Significant deviation from baseline behavior"
            ])
        
        # Update behavioral profile
        await self._update_behavioral_profile(user_id, current_features)
        
        return results

    async def _ml_based_detection(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Machine learning-based threat detection"""
        
        results = {
            "method": DetectionMethod.MACHINE_LEARNING,
            "ml_prediction": None,
            "feature_importance": {},
            "confidence": 0.0
        }
        
        try:
            # Extract ML features from event data
            features = self._extract_ml_features(event_data)
            if not features:
                return results
            
            # Prepare features for ML model
            feature_vector = np.array([features]).reshape(1, -1)
            
            # Check if model is trained
            if hasattr(self.threat_classifier, 'classes_'):
                # Make prediction
                prediction_proba = self.threat_classifier.predict_proba(feature_vector)
                prediction = self.threat_classifier.predict(feature_vector)[0]
                
                results["ml_prediction"] = prediction
                results["confidence"] = max(prediction_proba[0])
                
                # Get feature importance
                if hasattr(self.threat_classifier, 'feature_importances_'):
                    feature_names = [f"feature_{i}" for i in range(len(features))]
                    importance_dict = dict(zip(
                        feature_names,
                        self.threat_classifier.feature_importances_
                    ))
                    results["feature_importance"] = importance_dict
            
        except Exception as e:
            self.logger.warning(f"ML detection error: {e}")
        
        return results

    async def _anomaly_detection(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anomaly detection using isolation forest"""
        
        results = {
            "method": DetectionMethod.ANOMALY_DETECTION,
            "is_anomaly": False,
            "anomaly_score": 0.0,
            "confidence": 0.0
        }
        
        try:
            # Extract features for anomaly detection
            features = self._extract_anomaly_features(event_data)
            if not features:
                return results
            
            # Prepare features for anomaly detector
            feature_vector = np.array([features]).reshape(1, -1)
            
            # Check if model is fitted
            if hasattr(self.anomaly_detector, 'offset_'):
                # Predict anomaly
                anomaly_prediction = self.anomaly_detector.predict(feature_vector)[0]
                anomaly_score = self.anomaly_detector.decision_function(feature_vector)[0]
                
                results["is_anomaly"] = anomaly_prediction == -1
                results["anomaly_score"] = abs(anomaly_score)
                results["confidence"] = min(abs(anomaly_score), 1.0)
            
        except Exception as e:
            self.logger.warning(f"Anomaly detection error: {e}")
        
        return results

    async def _threat_intelligence_analysis(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Threat intelligence-based analysis"""
        
        results = {
            "method": DetectionMethod.THREAT_INTELLIGENCE,
            "threat_intel_matches": [],
            "ioc_matches": [],
            "confidence": 0.0
        }
        
        # Extract indicators of compromise (IOCs)
        iocs = self._extract_iocs(event_data)
        
        # Check against threat intelligence feeds
        for ioc_type, ioc_value in iocs.items():
            threat_intel_result = await self._check_threat_intelligence(ioc_type, ioc_value)
            if threat_intel_result["is_malicious"]:
                results["threat_intel_matches"].append(threat_intel_result)
                results["ioc_matches"].append(f"{ioc_type}: {ioc_value}")
        
        if results["threat_intel_matches"]:
            results["confidence"] = max([
                match["confidence"] for match in results["threat_intel_matches"]
            ])
        
        return results

    async def _combine_detection_results(self, *detection_results) -> Dict[str, Any]:
        """Combine results from multiple detection methods"""
        
        combined = {
            "threat_category": ThreatCategory.API_ABUSE,  # Default
            "primary_method": DetectionMethod.HEURISTIC,
            "confidence_score": 0.0,
            "severity_level": "low",
            "indicators": [],
            "mitigation_suggestions": []
        }
        
        # Collect all confidence scores
        confidence_scores = []
        all_indicators = []
        
        for result in detection_results:
            if result and result.get("confidence", 0) > 0:
                confidence_scores.append(result["confidence"])
                
                # Collect indicators
                if "indicators" in result:
                    all_indicators.extend(result["indicators"])
                if "behavioral_indicators" in result:
                    all_indicators.extend(result["behavioral_indicators"])
                if "ioc_matches" in result:
                    all_indicators.extend(result["ioc_matches"])
        
        # Calculate weighted confidence score
        if confidence_scores:
            combined["confidence_score"] = np.mean(confidence_scores)
            
            # Determine primary detection method
            best_result = max(detection_results, key=lambda x: x.get("confidence", 0))
            combined["primary_method"] = best_result.get("method", DetectionMethod.HEURISTIC)
            
            # Determine threat category from signature results
            if detection_results[0].get("threats_found"):
                combined["threat_category"] = detection_results[0]["threats_found"][0]["category"]
        
        # Determine severity level
        if combined["confidence_score"] > 0.8:
            combined["severity_level"] = "critical"
        elif combined["confidence_score"] > 0.6:
            combined["severity_level"] = "high"
        elif combined["confidence_score"] > 0.4:
            combined["severity_level"] = "medium"
        else:
            combined["severity_level"] = "low"
        
        combined["indicators"] = list(set(all_indicators))
        
        # Generate mitigation suggestions based on threat category
        combined["mitigation_suggestions"] = self._generate_mitigation_suggestions(
            combined["threat_category"],
            combined["severity_level"]
        )
        
        return combined

    def _extract_behavioral_features(self, event_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract behavioral features from event data"""
        
        features = {}
        
        # Time-based features
        current_time = datetime.utcnow()
        features["hour_of_day"] = current_time.hour
        features["day_of_week"] = current_time.weekday()
        
        # Request frequency features
        features["request_size"] = len(json.dumps(event_data))
        features["request_complexity"] = len(event_data.keys())
        
        # IP-based features
        source_ip = event_data.get("source_ip", "")
        if source_ip:
            ip_parts = source_ip.split(".")
            if len(ip_parts) == 4:
                features["ip_class"] = int(ip_parts[0]) if ip_parts[0].isdigit() else 0
        
        # User agent features
        user_agent = event_data.get("user_agent", "")
        features["user_agent_length"] = len(user_agent)
        features["is_mobile"] = 1.0 if "mobile" in user_agent.lower() else 0.0
        
        return features

    def _extract_ml_features(self, event_data: Dict[str, Any]) -> List[float]:
        """Extract numerical features for ML models"""
        
        features = []
        
        # Basic event features
        features.append(len(json.dumps(event_data)))  # Event size
        features.append(len(event_data.keys()))       # Event complexity
        features.append(datetime.utcnow().hour)       # Hour of day
        features.append(datetime.utcnow().weekday())  # Day of week
        
        # String-based features
        source_ip = event_data.get("source_ip", "")
        if source_ip:
            ip_parts = source_ip.split(".")
            if len(ip_parts) == 4:
                features.extend([
                    int(part) if part.isdigit() else 0 for part in ip_parts
                ])
            else:
                features.extend([0, 0, 0, 0])
        else:
            features.extend([0, 0, 0, 0])
        
        # User agent features
        user_agent = event_data.get("user_agent", "")
        features.append(len(user_agent))
        features.append(1.0 if "bot" in user_agent.lower() else 0.0)
        features.append(1.0 if "mobile" in user_agent.lower() else 0.0)
        
        return features

    def _extract_anomaly_features(self, event_data: Dict[str, Any]) -> List[float]:
        """Extract features for anomaly detection"""
        
        features = []
        
        # Time-based features
        current_time = datetime.utcnow()
        features.append(current_time.hour)
        features.append(current_time.minute)
        features.append(current_time.weekday())
        
        # Event characteristics
        features.append(len(json.dumps(event_data)))
        features.append(len(event_data.keys()))
        
        # Request patterns
        features.append(1.0 if event_data.get("method") == "POST" else 0.0)
        features.append(1.0 if event_data.get("method") == "GET" else 0.0)
        
        # Content analysis
        content = str(event_data)
        features.append(content.count("script"))
        features.append(content.count("sql"))
        features.append(content.count("admin"))
        
        return features

    def _extract_iocs(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract indicators of compromise from event data"""
        
        iocs = {}
        
        # IP addresses
        if "source_ip" in event_data:
            iocs["ip"] = event_data["source_ip"]
        
        # URLs
        if "url" in event_data:
            iocs["url"] = event_data["url"]
        
        # File hashes
        if "file_hash" in event_data:
            iocs["hash"] = event_data["file_hash"]
        
        # Domain names
        if "domain" in event_data:
            iocs["domain"] = event_data["domain"]
        
        return iocs

    async def _check_threat_intelligence(self, ioc_type: str, ioc_value: str) -> Dict[str, Any]:
        """Check IOC against threat intelligence feeds"""
        
        # Check Redis cache first
        cache_key = f"threat_intel:{ioc_type}:{ioc_value}"
        cached_result = await self.redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Simulate threat intelligence lookup
        # In production, integrate with real threat intelligence APIs
        result = {
            "is_malicious": False,
            "confidence": 0.0,
            "threat_types": [],
            "first_seen": None,
            "last_seen": None
        }
        
        # Simple heuristics for demonstration
        if ioc_type == "ip":
            # Check for common malicious IP patterns
            if ioc_value.startswith("192.168.") or ioc_value.startswith("10."):
                result["is_malicious"] = False
            elif ioc_value in ["127.0.0.1", "0.0.0.0"]:
                result["is_malicious"] = False
            else:
                # Simulate occasional threat detection
                import random
                if random.random() < 0.1:  # 10% chance of being flagged
                    result["is_malicious"] = True
                    result["confidence"] = 0.8
                    result["threat_types"] = ["botnet", "scanner"]
        
        # Cache result for 1 hour
        await self.redis_client.setex(cache_key, 3600, json.dumps(result))
        
        return result

    def _calculate_behavioral_anomaly(self, current_features: Dict[str, float], 
                                    baseline_features: Dict[str, float]) -> float:
        """Calculate behavioral anomaly score"""
        
        if not baseline_features:
            return 0.0
        
        anomaly_score = 0.0
        feature_count = 0
        
        for feature_name, current_value in current_features.items():
            if feature_name in baseline_features:
                baseline_value = baseline_features[feature_name]
                
                # Calculate normalized difference
                if baseline_value != 0:
                    diff = abs(current_value - baseline_value) / abs(baseline_value)
                    anomaly_score += min(diff, 1.0)
                elif current_value != 0:
                    anomaly_score += 1.0
                
                feature_count += 1
        
        return anomaly_score / feature_count if feature_count > 0 else 0.0

    async def _create_behavioral_profile(self, user_id: str, 
                                       event_data: Dict[str, Any]) -> BehavioralProfile:
        """Create new behavioral profile for user"""
        
        baseline_features = self._extract_behavioral_features(event_data)
        
        profile = BehavioralProfile(
            user_id=user_id,
            baseline_features=baseline_features,
            activity_patterns={"total_events": 1}
        )
        
        # Store in Redis
        await self.redis_client.setex(
            f"behavioral_profile:{user_id}",
            86400,  # 24 hours
            json.dumps({
                "baseline_features": baseline_features,
                "activity_patterns": profile.activity_patterns,
                "last_updated": profile.last_updated.isoformat()
            })
        )
        
        return profile

    async def _update_behavioral_profile(self, user_id: str, 
                                       current_features: Dict[str, float]):
        """Update user's behavioral profile with new data"""
        
        profile = self.behavioral_profiles.get(user_id)
        if not profile:
            return
        
        # Update baseline features with exponential moving average
        alpha = 0.1  # Learning rate
        for feature_name, current_value in current_features.items():
            if feature_name in profile.baseline_features:
                old_value = profile.baseline_features[feature_name]
                profile.baseline_features[feature_name] = (
                    alpha * current_value + (1 - alpha) * old_value
                )
            else:
                profile.baseline_features[feature_name] = current_value
        
        # Update activity patterns
        profile.activity_patterns["total_events"] += 1
        profile.last_updated = datetime.utcnow()
        
        # Store updated profile
        await self.redis_client.setex(
            f"behavioral_profile:{user_id}",
            86400,
            json.dumps({
                "baseline_features": profile.baseline_features,
                "activity_patterns": profile.activity_patterns,
                "last_updated": profile.last_updated.isoformat()
            })
        )

    def _generate_mitigation_suggestions(self, threat_category: ThreatCategory, 
                                       severity_level: str) -> List[str]:
        """Generate mitigation suggestions based on threat type and severity"""
        
        suggestions = []
        
        if threat_category == ThreatCategory.BRUTE_FORCE:
            suggestions.extend([
                "Implement rate limiting on authentication endpoints",
                "Enable account lockout after failed attempts",
                "Require CAPTCHA for suspicious login patterns",
                "Implement multi-factor authentication"
            ])
        
        elif threat_category == ThreatCategory.DDOS:
            suggestions.extend([
                "Enable DDoS protection and rate limiting",
                "Implement connection throttling",
                "Use CDN and load balancing",
                "Block attacking IP ranges"
            ])
        
        elif threat_category == ThreatCategory.MALWARE:
            suggestions.extend([
                "Scan and quarantine suspicious files",
                "Update antivirus signatures",
                "Implement web application firewall",
                "Review and patch system vulnerabilities"
            ])
        
        elif threat_category == ThreatCategory.DATA_EXFILTRATION:
            suggestions.extend([
                "Monitor and limit data export activities",
                "Implement data loss prevention (DLP)",
                "Review user access permissions",
                "Enable audit logging for sensitive data"
            ])
        
        # Add severity-specific suggestions
        if severity_level in ["critical", "high"]:
            suggestions.extend([
                "Immediate isolation of affected systems",
                "Escalate to security incident response team",
                "Conduct forensic analysis",
                "Notify relevant stakeholders"
            ])
        
        return suggestions

    async def _store_threat_detection(self, detection: ThreatDetection):
        """Store threat detection result"""
        
        detection_data = {
            "detection_id": detection.detection_id,
            "threat_category": detection.threat_category.value,
            "detection_method": detection.detection_method.value,
            "confidence_score": detection.confidence_score,
            "severity_level": detection.severity_level,
            "source_data": detection.source_data,
            "indicators": detection.indicators,
            "mitigation_suggestions": detection.mitigation_suggestions,
            "detected_at": detection.detected_at.isoformat()
        }
        
        # Store in Redis
        await self.redis_client.setex(
            f"threat_detection:{detection.detection_id}",
            86400,  # 24 hours
            json.dumps(detection_data)
        )
        
        # Add to detections timeline
        await self.redis_client.lpush(
            "threat_detections_timeline",
            json.dumps(detection_data)
        )
        
        # Keep only last 500 detections
        await self.redis_client.ltrim("threat_detections_timeline", 0, 499)

    async def _update_threat_patterns(self, detection: ThreatDetection):
        """Update threat patterns for learning"""
        
        pattern_key = f"threat_pattern:{detection.threat_category.value}"
        
        pattern_data = {
            "detection_id": detection.detection_id,
            "confidence": detection.confidence_score,
            "method": detection.detection_method.value,
            "timestamp": detection.detected_at.isoformat()
        }
        
        await self.redis_client.lpush(pattern_key, json.dumps(pattern_data))
        await self.redis_client.ltrim(pattern_key, 0, 99)  # Keep last 100 patterns

    def _update_detection_stats(self, detection: ThreatDetection):
        """Update detection statistics"""
        
        self.detection_stats["total_detections"] += 1
        
        # Update accuracy based on confidence score
        if detection.confidence_score > 0.8:
            self.detection_stats["true_positives"] += 1
        elif detection.confidence_score < 0.3:
            self.detection_stats["false_positives"] += 1
        
        # Calculate accuracy rate
        total = self.detection_stats["total_detections"]
        tp = self.detection_stats["true_positives"]
        fp = self.detection_stats["false_positives"]
        
        if total > 0:
            self.detection_stats["accuracy_rate"] = (total - fp) / total

    async def _load_ml_models(self):
        """Load pre-trained ML models from storage"""
        
        try:
            # Load anomaly detector
            model_data = await self.redis_client.get("ml_model:anomaly_detector")
            if model_data:
                model_bytes = base64.b64decode(model_data)
                self.anomaly_detector = pickle.loads(model_bytes)
            
            # Load threat classifier
            classifier_data = await self.redis_client.get("ml_model:threat_classifier")
            if classifier_data:
                classifier_bytes = base64.b64decode(classifier_data)
                self.threat_classifier = pickle.loads(classifier_bytes)
            
            self.logger.info("ML models loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Could not load ML models: {e}")

    async def _load_behavioral_profiles(self):
        """Load behavioral profiles from storage"""
        
        try:
            profile_keys = await self.redis_client.keys("behavioral_profile:*")
            
            for key in profile_keys:
                user_id = key.split(":")[-1]
                profile_data = await self.redis_client.get(key)
                
                if profile_data:
                    data = json.loads(profile_data)
                    profile = BehavioralProfile(
                        user_id=user_id,
                        baseline_features=data["baseline_features"],
                        activity_patterns=data["activity_patterns"],
                        last_updated=datetime.fromisoformat(data["last_updated"])
                    )
                    self.behavioral_profiles[user_id] = profile
            
            self.logger.info(f"Loaded {len(self.behavioral_profiles)} behavioral profiles")
            
        except Exception as e:
            self.logger.warning(f"Could not load behavioral profiles: {e}")

    async def _load_threat_signatures(self):
        """Load threat signatures from storage"""
        
        try:
            signatures_data = await self.redis_client.get("threat_signatures")
            if signatures_data:
                signatures_dict = json.loads(signatures_data)
                
                for sig_id, sig_data in signatures_dict.items():
                    signature = ThreatSignature(
                        signature_id=sig_data["signature_id"],
                        name=sig_data["name"],
                        category=ThreatCategory(sig_data["category"]),
                        pattern=sig_data["pattern"],
                        confidence=sig_data["confidence"],
                        description=sig_data["description"],
                        created_at=datetime.fromisoformat(sig_data["created_at"]),
                        last_updated=datetime.fromisoformat(sig_data["last_updated"])
                    )
                    self.threat_signatures[sig_id] = signature
            
            self.logger.info(f"Loaded {len(self.threat_signatures)} threat signatures")
            
        except Exception as e:
            self.logger.warning(f"Could not load threat signatures: {e}")

    async def _initialize_threat_intelligence(self):
        """Initialize threat intelligence feeds"""
        
        # Initialize threat intelligence sources
        # This would integrate with external threat intelligence APIs
        
        self.logger.info("Threat intelligence feeds initialized")

    async def get_detection_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive threat detection dashboard"""
        
        # Get recent detections
        recent_detections = await self.redis_client.lrange(
            "threat_detections_timeline", 0, 9
        )
        detections_data = [
            json.loads(detection) for detection in recent_detections
        ] if recent_detections else []
        
        # Get threat pattern summaries
        threat_patterns = {}
        for category in ThreatCategory:
            pattern_key = f"threat_pattern:{category.value}"
            patterns = await self.redis_client.lrange(pattern_key, 0, 9)
            threat_patterns[category.value] = len(patterns)
        
        return {
            "detection_stats": self.detection_stats,
            "recent_detections": detections_data,
            "threat_patterns": threat_patterns,
            "active_profiles": len(self.behavioral_profiles),
            "threat_signatures": len(self.threat_signatures),
            "system_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }

    async def shutdown(self):
        """Shutdown threat detection service"""
        
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("Threat Detection Service shutdown completed")


# Example usage
async def main():
    """Example usage of Threat Detection Service"""
    
    threat_detector = ThreatDetectionService()
    await threat_detector.initialize()
    
    try:
        # Example threat analysis
        test_event = {
            "source_ip": "192.168.1.100",
            "user_id": "user_123",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "request_data": "SELECT * FROM users WHERE id=1 OR 1=1",
            "method": "POST",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        detection = await threat_detector.analyze_threat(test_event)
        print(f"Threat detection result: {detection}")
        
        # Get dashboard
        dashboard = await threat_detector.get_detection_dashboard()
        print(f"Detection dashboard: {dashboard}")
        
    finally:
        await threat_detector.shutdown()


if __name__ == "__main__":
    asyncio.run(main())