"""
Enterprise Key Lifecycle Automator
Created by: Senior Engineering Team (DevOps + DBA + Security + ML + Microservices + IA Prompt Engineer)
Date: 2024
Purpose: Fully automated key lifecycle management with Creator Economy optimizations

Features:
- Fully automated key lifecycle management (create, rotate, retire, destroy)
- Creator-aware lifecycle policies with intelligent automation
- Machine learning-driven optimization and predictive maintenance
- Compliance-integrated automation with regulatory awareness
- Performance-based adaptive policies
- Creator Economy specific automation workflows
"""

import asyncio
import hashlib
import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any, Callable, Union
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import sqlite3
import redis
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class KeyLifecycleStage(Enum):
    """Key lifecycle stages"""
    PENDING_CREATION = "pending_creation"
    ACTIVE = "active"
    ROTATION_DUE = "rotation_due"
    ROTATION_IN_PROGRESS = "rotation_in_progress"
    DEPRECATED = "deprecated"
    PENDING_DESTRUCTION = "pending_destruction"
    DESTROYED = "destroyed"
    EMERGENCY_REVOKED = "emergency_revoked"


class AutomationTrigger(Enum):
    """Automation trigger types"""
    TIME_BASED = "time_based"
    USAGE_BASED = "usage_based"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_REQUIREMENT = "compliance_requirement"
    PERFORMANCE_THRESHOLD = "performance_threshold"
    CREATOR_REQUEST = "creator_request"
    ML_PREDICTION = "ml_prediction"
    ANOMALY_DETECTION = "anomaly_detection"


class CreatorTier(Enum):
    """Creator tier levels for lifecycle policies"""
    EMERGING = "emerging"        # New creators, basic policies
    STANDARD = "standard"        # Regular creators, standard policies
    PREMIUM = "premium"          # High-value creators, enhanced policies
    ENTERPRISE = "enterprise"    # Enterprise creators, custom policies
    VIP = "vip"                 # Top-tier creators, priority treatment


@dataclass
class KeyMetrics:
    """Key usage and performance metrics"""
    key_id: str
    creation_time: datetime
    last_used: datetime
    usage_count: int
    error_count: int
    performance_ms: float
    size_bytes: int
    encryption_operations: int
    decryption_operations: int
    creator_id: Optional[str] = None
    content_type: Optional[str] = None
    
    def to_ml_features(self) -> List[float]:
        """Convert metrics to ML features"""
        now = datetime.now()
        age_hours = (now - self.creation_time).total_seconds() / 3600
        last_used_hours = (now - self.last_used).total_seconds() / 3600
        error_rate = self.error_count / max(self.usage_count, 1)
        
        return [
            age_hours,
            last_used_hours,
            self.usage_count,
            error_rate,
            self.performance_ms,
            self.size_bytes,
            self.encryption_operations,
            self.decryption_operations
        ]


@dataclass
class LifecyclePolicy:
    """Automated lifecycle policy configuration"""
    policy_id: str
    name: str
    creator_tiers: List[CreatorTier]
    content_types: List[str]
    
    # Lifecycle rules
    max_age_days: int
    max_usage_count: int
    rotation_frequency_days: int
    performance_threshold_ms: float
    error_rate_threshold: float
    
    # Automation settings
    auto_rotation: bool = True
    auto_cleanup: bool = True
    auto_monitoring: bool = True
    emergency_revocation: bool = True
    
    # Creator-specific settings
    creator_notification: bool = True
    creator_approval_required: bool = False
    graceful_transition: bool = True
    
    # Compliance settings
    compliance_requirements: List[str] = field(default_factory=list)
    audit_logging: bool = True
    retention_period_days: int = 90
    
    def applies_to_creator(self, creator_metadata: Dict[str, Any]) -> bool:
        """Check if policy applies to creator"""
        creator_tier = CreatorTier(creator_metadata.get('tier', 'standard'))
        content_types = creator_metadata.get('content_types', [])
        
        # Check tier match
        if self.creator_tiers and creator_tier not in self.creator_tiers:
            return False
        
        # Check content type match
        if self.content_types:
            if not any(ct in content_types for ct in self.content_types):
                return False
        
        return True


@dataclass
class AutomationAction:
    """Automated action specification"""
    action_id: str
    action_type: str  # rotate, revoke, notify, cleanup
    key_id: str
    trigger: AutomationTrigger
    scheduled_time: datetime
    creator_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    execution_time: Optional[datetime] = None
    result: Optional[str] = None
    error_message: Optional[str] = None


class MLOptimizationEngine:
    """Machine learning engine for lifecycle optimization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # ML models
        self.rotation_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
        # Model training data
        self.training_data = []
        self.is_trained = False
        
        # Prediction cache
        self.prediction_cache = {}
        self.cache_timeout = timedelta(hours=1)
    
    def add_training_data(self, metrics: KeyMetrics, actual_rotation_days: int):
        """Add training data for ML models"""
        features = metrics.to_ml_features()
        self.training_data.append((features, actual_rotation_days))
    
    def train_models(self):
        """Train ML models with collected data"""
        try:
            if len(self.training_data) < 100:  # Need minimum data
                self.logger.warning("Insufficient training data for ML models")
                return False
            
            # Prepare data
            X = np.array([data[0] for data in self.training_data])
            y = np.array([data[1] for data in self.training_data])
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train rotation predictor
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
            self.rotation_predictor.fit(X_train, y_train)
            
            # Train anomaly detector
            self.anomaly_detector.fit(X_scaled)
            
            # Evaluate models
            train_score = self.rotation_predictor.score(X_train, y_train)
            test_score = self.rotation_predictor.score(X_test, y_test)
            
            self.logger.info(f"ML models trained - Train score: {train_score:.3f}, Test score: {test_score:.3f}")
            self.is_trained = True
            return True
            
        except Exception as e:
            self.logger.error(f"ML model training failed: {e}")
            return False
    
    def predict_optimal_rotation_time(self, metrics: KeyMetrics) -> int:
        """Predict optimal rotation time in days"""
        try:
            if not self.is_trained:
                return 30  # Default fallback
            
            # Check cache
# SECURITY: cache_key = f"rotation_{metrics.key_id}" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
            if cache_key in self.prediction_cache:
                cached_time, cached_result = self.prediction_cache[cache_key]
                if datetime.now() - cached_time < self.cache_timeout:
                    return cached_result
            
            # Make prediction
            features = np.array([metrics.to_ml_features()])
            features_scaled = self.scaler.transform(features)
            prediction = self.rotation_predictor.predict(features_scaled)[0]
            
            # Clamp to reasonable range
            result = max(1, min(365, int(prediction)))
            
            # Cache result
            self.prediction_cache[cache_key] = (datetime.now(), result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Rotation prediction failed: {e}")
            return 30  # Default fallback
    
    def detect_anomalies(self, metrics_list: List[KeyMetrics]) -> List[str]:
        """Detect anomalous keys that may need attention"""
        try:
            if not self.is_trained or not metrics_list:
                return []
            
            # Prepare features
            features = np.array([metrics.to_ml_features() for metrics in metrics_list])
            features_scaled = self.scaler.transform(features)
            
            # Detect anomalies
            anomaly_scores = self.anomaly_detector.decision_function(features_scaled)
            outliers = self.anomaly_detector.predict(features_scaled)
            
            # Return anomalous key IDs
            anomalous_keys = []
            for i, (metrics, is_outlier) in enumerate(zip(metrics_list, outliers)):
                if is_outlier == -1:  # Anomaly
                    anomalous_keys.append(metrics.key_id)
            
            return anomalous_keys
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def optimize_policy_parameters(self, 
                                 policy: LifecyclePolicy,
                                 historical_metrics: List[KeyMetrics]) -> Dict[str, Any]:
        """Optimize policy parameters based on historical data"""
        try:
            if not historical_metrics:
                return {}
            
            # Analyze historical patterns
            ages = [(datetime.now() - m.creation_time).days for m in historical_metrics]
            usage_counts = [m.usage_count for m in historical_metrics]
            performance_times = [m.performance_ms for m in historical_metrics]
            error_rates = [m.error_count / max(m.usage_count, 1) for m in historical_metrics]
            
            # Calculate optimized parameters
            optimizations = {}
            
            # Optimize rotation frequency based on usage patterns
            if usage_counts:
                avg_usage = np.mean(usage_counts)
                if avg_usage > 1000:  # High usage
                    optimizations['rotation_frequency_days'] = max(7, policy.rotation_frequency_days // 2)
                elif avg_usage < 100:  # Low usage
                    optimizations['rotation_frequency_days'] = min(90, policy.rotation_frequency_days * 2)
            
            # Optimize performance threshold based on observed performance
            if performance_times:
                p95_performance = np.percentile(performance_times, 95)
                optimizations['performance_threshold_ms'] = p95_performance * 1.2
            
            # Optimize error rate threshold
            if error_rates:
                p95_error_rate = np.percentile(error_rates, 95)
                optimizations['error_rate_threshold'] = max(0.01, p95_error_rate * 1.5)
            
            return optimizations
            
        except Exception as e:
            self.logger.error(f"Policy optimization failed: {e}")
            return {}


class ComplianceEngine:
    """Compliance automation engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compliance_rules = {}
        self._initialize_compliance_rules()
    
    def _initialize_compliance_rules(self):
        """Initialize compliance rules"""
        self.compliance_rules = {
            'GDPR': {
                'max_retention_days': 365,
                'encryption_required': True,
                'audit_logging': True,
                'right_to_erasure': True,
                'data_portability': True
            },
            'CCPA': {
                'max_retention_days': 365,
                'encryption_required': True,
                'audit_logging': True,
                'right_to_deletion': True,
                'opt_out_rights': True
            },
            'SOX': {
                'audit_logging': True,
                'access_controls': True,
                'financial_data_protection': True,
                'retention_period_days': 2555  # 7 years
            },
            'HIPAA': {
                'encryption_required': True,
                'access_controls': True,
                'audit_logging': True,
                'minimum_necessary': True,
                'breach_notification': True
            },
            'PCI_DSS': {
                'encryption_required': True,
                'access_controls': True,
                'regular_testing': True,
                'secure_key_management': True
            }
        }
    
    def validate_policy_compliance(self, 
                                 policy: LifecyclePolicy,
                                 creator_metadata: Dict[str, Any]) -> List[str]:
        """Validate policy compliance"""
        violations = []
        
        try:
            applicable_regulations = creator_metadata.get('applicable_regulations', [])
            
            for regulation in applicable_regulations:
                if regulation not in self.compliance_rules:
                    continue
                
                rules = self.compliance_rules[regulation]
                
                # Check retention period
                if 'max_retention_days' in rules:
                    if policy.retention_period_days > rules['max_retention_days']:
                        violations.append(f"{regulation}: Retention period exceeds limit")
                
                # Check audit logging
                if rules.get('audit_logging') and not policy.audit_logging:
                    violations.append(f"{regulation}: Audit logging required")
                
                # Check encryption requirement
                if rules.get('encryption_required'):
                    # This would check if encryption is properly configured
                    pass
                
                # Regulation-specific checks
                if regulation == 'SOX' and rules.get('retention_period_days'):
                    if policy.retention_period_days < rules['retention_period_days']:
                        violations.append(f"SOX: Minimum retention period not met")
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Compliance validation failed: {e}")
            return [f"Compliance validation error: {e}"]
    
    def get_required_retention_period(self, creator_metadata: Dict[str, Any]) -> int:
        """Get minimum required retention period"""
        applicable_regulations = creator_metadata.get('applicable_regulations', [])
        
        min_retention = 30  # Default minimum
        for regulation in applicable_regulations:
            if regulation in self.compliance_rules:
                rules = self.compliance_rules[regulation]
                if 'retention_period_days' in rules:
                    min_retention = max(min_retention, rules['retention_period_days'])
                elif 'max_retention_days' in rules:
                    min_retention = max(min_retention, rules['max_retention_days'])
        
        return min_retention
    
    def should_apply_right_to_erasure(self, 
                                    creator_metadata: Dict[str, Any],
                                    erasure_request: Dict[str, Any]) -> bool:
        """Check if right to erasure should be applied"""
        applicable_regulations = creator_metadata.get('applicable_regulations', [])
        
        # GDPR right to erasure
        if 'GDPR' in applicable_regulations:
            return True
        
        # CCPA right to deletion
        if 'CCPA' in applicable_regulations:
            return True
        
        return False


class MetricsCollector:
    """Collects and stores key metrics for analysis"""
    
    def __init__(self, db_path: str = "/tmp/key_metrics.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database for metrics storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS key_metrics (
                    key_id TEXT PRIMARY KEY,
                    creation_time TEXT,
                    last_used TEXT,
                    usage_count INTEGER,
                    error_count INTEGER,
                    performance_ms REAL,
                    size_bytes INTEGER,
                    encryption_operations INTEGER,
                    decryption_operations INTEGER,
                    creator_id TEXT,
                    content_type TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
    
    def update_metrics(self, metrics: KeyMetrics):
        """Update key metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO key_metrics 
                (key_id, creation_time, last_used, usage_count, error_count, 
                 performance_ms, size_bytes, encryption_operations, decryption_operations,
                 creator_id, content_type, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.key_id,
                metrics.creation_time.isoformat(),
                metrics.last_used.isoformat(),
                metrics.usage_count,
                metrics.error_count,
                metrics.performance_ms,
                metrics.size_bytes,
                metrics.encryption_operations,
                metrics.decryption_operations,
                metrics.creator_id,
                metrics.content_type,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Metrics update failed: {e}")
    
    def get_metrics(self, key_id: str) -> Optional[KeyMetrics]:
        """Get metrics for a specific key"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM key_metrics WHERE key_id = ?', (key_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return KeyMetrics(
                    key_id=row[0],
                    creation_time=datetime.fromisoformat(row[1]),
                    last_used=datetime.fromisoformat(row[2]),
                    usage_count=row[3],
                    error_count=row[4],
                    performance_ms=row[5],
                    size_bytes=row[6],
                    encryption_operations=row[7],
                    decryption_operations=row[8],
                    creator_id=row[9],
                    content_type=row[10]
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Metrics retrieval failed: {e}")
            return None
    
    def get_all_metrics(self) -> List[KeyMetrics]:
        """Get all key metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM key_metrics')
            rows = cursor.fetchall()
            conn.close()
            
            metrics_list = []
            for row in rows:
                metrics = KeyMetrics(
                    key_id=row[0],
                    creation_time=datetime.fromisoformat(row[1]),
                    last_used=datetime.fromisoformat(row[2]),
                    usage_count=row[3],
                    error_count=row[4],
                    performance_ms=row[5],
                    size_bytes=row[6],
                    encryption_operations=row[7],
                    decryption_operations=row[8],
                    creator_id=row[9],
                    content_type=row[10]
                )
                metrics_list.append(metrics)
            
            return metrics_list
            
        except Exception as e:
            self.logger.error(f"All metrics retrieval failed: {e}")
            return []


class KeyLifecycleAutomator:
    """Main automated key lifecycle management system"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.logger = logging.getLogger(__name__)
        
        # Components
        self.ml_engine = MLOptimizationEngine()
        self.compliance_engine = ComplianceEngine()
        self.metrics_collector = MetricsCollector()
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        
        # State management
        self.lifecycle_policies = {}
        self.creator_profiles = {}
        self.automation_queue = []
        self.active_keys = {}
        
        # Automation control
        self.automation_enabled = True
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.running = False
        
        # Metrics
        self.automation_metrics = {
            'keys_created': 0,
            'keys_rotated': 0,
            'keys_revoked': 0,
            'keys_destroyed': 0,
            'automation_actions': 0,
            'ml_predictions': 0,
            'compliance_violations': 0
        }
        
        # Initialize default policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default lifecycle policies"""
        
        # VIP Creator Policy
        vip_policy = LifecyclePolicy(
            policy_id="vip_creator_policy",
            name="VIP Creator Lifecycle Policy",
            creator_tiers=[CreatorTier.VIP],
            content_types=["audio", "video", "image"],
            max_age_days=180,
            max_usage_count=1000000,
            rotation_frequency_days=7,  # Weekly rotation for VIPs
            performance_threshold_ms=50.0,
            error_rate_threshold=0.001,
            auto_rotation=True,
            auto_cleanup=True,
            auto_monitoring=True,
            creator_notification=True,
            creator_approval_required=False,
            graceful_transition=True,
            audit_logging=True,
            retention_period_days=365
        )
        
        # Premium Creator Policy
        premium_policy = LifecyclePolicy(
            policy_id="premium_creator_policy",
            name="Premium Creator Lifecycle Policy",
            creator_tiers=[CreatorTier.PREMIUM],
            content_types=["audio", "video", "image"],
            max_age_days=365,
            max_usage_count=500000,
            rotation_frequency_days=14,  # Bi-weekly rotation
            performance_threshold_ms=100.0,
            error_rate_threshold=0.005,
            auto_rotation=True,
            auto_cleanup=True,
            auto_monitoring=True,
            creator_notification=True,
            creator_approval_required=False,
            graceful_transition=True,
            audit_logging=True,
            retention_period_days=180
        )
        
        # Standard Creator Policy
        standard_policy = LifecyclePolicy(
            policy_id="standard_creator_policy",
            name="Standard Creator Lifecycle Policy",
            creator_tiers=[CreatorTier.STANDARD],
            content_types=["audio", "video", "image", "text"],
            max_age_days=365,
            max_usage_count=100000,
            rotation_frequency_days=30,  # Monthly rotation
            performance_threshold_ms=200.0,
            error_rate_threshold=0.01,
            auto_rotation=True,
            auto_cleanup=True,
            auto_monitoring=True,
            creator_notification=True,
            creator_approval_required=False,
            graceful_transition=True,
            audit_logging=True,
            retention_period_days=90
        )
        
        # Emerging Creator Policy
        emerging_policy = LifecyclePolicy(
            policy_id="emerging_creator_policy",
            name="Emerging Creator Lifecycle Policy",
            creator_tiers=[CreatorTier.EMERGING],
            content_types=["text", "image"],
            max_age_days=365,
            max_usage_count=10000,
            rotation_frequency_days=60,  # Bi-monthly rotation
            performance_threshold_ms=500.0,
            error_rate_threshold=0.02,
            auto_rotation=True,
            auto_cleanup=True,
            auto_monitoring=True,
            creator_notification=True,
            creator_approval_required=True,  # Require approval for emerging creators
            graceful_transition=True,
            audit_logging=True,
            retention_period_days=30
        )
        
        # Register policies
        self.register_lifecycle_policy(vip_policy)
        self.register_lifecycle_policy(premium_policy)
        self.register_lifecycle_policy(standard_policy)
        self.register_lifecycle_policy(emerging_policy)
    
    def register_lifecycle_policy(self, policy: LifecyclePolicy):
        """Register a lifecycle policy"""
        self.lifecycle_policies[policy.policy_id] = policy
        self.logger.info(f"Registered lifecycle policy: {policy.name}")
    
    def register_creator(self, creator_id: str, creator_metadata: Dict[str, Any]):
        """Register creator profile"""
        self.creator_profiles[creator_id] = creator_metadata
        self.logger.info(f"Registered creator: {creator_id}")
    
    async def create_key_automated(self, 
                                 key_id: str,
                                 creator_id: str,
                                 content_type: str,
                                 key_data: Dict[str, Any]) -> bool:
        """Create key with automated lifecycle management"""
        try:
            # Get creator profile
            creator_metadata = self.creator_profiles.get(creator_id, {})
            
            # Find applicable policy
            policy = self._find_applicable_policy(creator_metadata)
            if not policy:
                self.logger.error(f"No applicable policy found for creator {creator_id}")
                return False
            
            # Validate compliance
            violations = self.compliance_engine.validate_policy_compliance(policy, creator_metadata)
            if violations:
                self.logger.warning(f"Compliance violations for {creator_id}: {violations}")
                self.automation_metrics['compliance_violations'] += len(violations)
            
            # Create key metrics
            metrics = KeyMetrics(
                key_id=key_id,
                creation_time=datetime.now(),
                last_used=datetime.now(),
                usage_count=0,
                error_count=0,
                performance_ms=0.0,
                size_bytes=len(str(key_data)),
                encryption_operations=0,
                decryption_operations=0,
                creator_id=creator_id,
                content_type=content_type
            )
            
            # Store metrics
            self.metrics_collector.update_metrics(metrics)
            
            # Register key
            self.active_keys[key_id] = {
                'stage': KeyLifecycleStage.ACTIVE,
                'policy_id': policy.policy_id,
                'creator_id': creator_id,
                'created_at': datetime.now(),
                'key_data': key_data
            }
            
            # Schedule automated actions
            await self._schedule_lifecycle_actions(key_id, policy, creator_metadata)
            
            self.automation_metrics['keys_created'] += 1
            self.logger.info(f"Created key {key_id} with automated lifecycle")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Automated key creation failed: {e}")
            return False
    
    def _find_applicable_policy(self, creator_metadata: Dict[str, Any]) -> Optional[LifecyclePolicy]:
        """Find applicable lifecycle policy for creator"""
        for policy in self.lifecycle_policies.values():
            if policy.applies_to_creator(creator_metadata):
                return policy
        return None
    
    async def _schedule_lifecycle_actions(self, 
                                        key_id: str,
                                        policy: LifecyclePolicy,
                                        creator_metadata: Dict[str, Any]):
        """Schedule automated lifecycle actions"""
        try:
            now = datetime.now()
            
            # Schedule rotation
            if policy.auto_rotation:
                rotation_days = policy.rotation_frequency_days
                
                # Use ML prediction if available
                if self.ml_engine.is_trained:
                    metrics = self.metrics_collector.get_metrics(key_id)
                    if metrics:
                        predicted_days = self.ml_engine.predict_optimal_rotation_time(metrics)
                        rotation_days = min(rotation_days, predicted_days)
                        self.automation_metrics['ml_predictions'] += 1
                
                rotation_time = now + timedelta(days=rotation_days)
                rotation_action = AutomationAction(
                    action_id=str(uuid.uuid4()),
                    action_type="rotate",
                    key_id=key_id,
                    trigger=AutomationTrigger.TIME_BASED,
                    scheduled_time=rotation_time,
                    creator_id=creator_metadata.get('creator_id'),
                    parameters={'policy_id': policy.policy_id}
                )
                self.automation_queue.append(rotation_action)
            
            # Schedule cleanup based on max age
            cleanup_time = now + timedelta(days=policy.max_age_days)
            cleanup_action = AutomationAction(
                action_id=str(uuid.uuid4()),
                action_type="cleanup",
                key_id=key_id,
                trigger=AutomationTrigger.TIME_BASED,
                scheduled_time=cleanup_time,
                creator_id=creator_metadata.get('creator_id'),
                parameters={'policy_id': policy.policy_id}
            )
            self.automation_queue.append(cleanup_action)
            
            # Schedule compliance-based actions
            retention_period = self.compliance_engine.get_required_retention_period(creator_metadata)
            if retention_period > policy.retention_period_days:
                # Update retention based on compliance
                extended_cleanup_time = now + timedelta(days=retention_period)
                compliance_action = AutomationAction(
                    action_id=str(uuid.uuid4()),
                    action_type="compliance_cleanup",
                    key_id=key_id,
                    trigger=AutomationTrigger.COMPLIANCE_REQUIREMENT,
                    scheduled_time=extended_cleanup_time,
                    creator_id=creator_metadata.get('creator_id'),
                    parameters={'retention_period': retention_period}
                )
                self.automation_queue.append(compliance_action)
            
        except Exception as e:
            self.logger.error(f"Action scheduling failed: {e}")
    
    async def start_automation(self):
        """Start automated lifecycle management"""
        try:
            self.running = True
            self.logger.info("Starting key lifecycle automation")
            
            # Start background tasks
            await asyncio.gather(
                self._automation_loop(),
                self._monitoring_loop(),
                self._ml_training_loop(),
                self._anomaly_detection_loop()
            )
            
        except Exception as e:
            self.logger.error(f"Automation startup failed: {e}")
    
    async def _automation_loop(self):
        """Main automation execution loop"""
        while self.running:
            try:
                if not self.automation_enabled:
                    await asyncio.sleep(60)
                    continue
                
                # Process pending actions
                current_time = datetime.now()
                pending_actions = [action for action in self.automation_queue 
                                 if action.status == "pending" and action.scheduled_time <= current_time]
                
                for action in pending_actions:
                    await self._execute_automation_action(action)
                
                # Clean up completed actions
                self.automation_queue = [action for action in self.automation_queue 
                                       if action.status == "pending"]
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Automation loop error: {e}")
                await asyncio.sleep(5)
    
    async def _execute_automation_action(self, action: AutomationAction):
        """Execute an automation action"""
        try:
            action.status = "executing"
            action.execution_time = datetime.now()
            
            self.logger.info(f"Executing {action.action_type} for key {action.key_id}")
            
            if action.action_type == "rotate":
                success = await self._execute_key_rotation(action)
            elif action.action_type == "cleanup":
                success = await self._execute_key_cleanup(action)
            elif action.action_type == "compliance_cleanup":
                success = await self._execute_compliance_cleanup(action)
            elif action.action_type == "revoke":
                success = await self._execute_key_revocation(action)
            elif action.action_type == "notify":
                success = await self._execute_creator_notification(action)
            else:
                self.logger.warning(f"Unknown action type: {action.action_type}")
                success = False
            
            action.status = "completed" if success else "failed"
            if success:
                self.automation_metrics['automation_actions'] += 1
            
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            self.logger.error(f"Action execution failed: {e}")
    
    async def _execute_key_rotation(self, action: AutomationAction) -> bool:
        """Execute key rotation"""
        try:
            key_id = action.key_id
            creator_id = action.creator_id
            
            # Check if creator approval is required
            if creator_id:
                creator_metadata = self.creator_profiles.get(creator_id, {})
                policy = self._find_applicable_policy(creator_metadata)
                
                if policy and policy.creator_approval_required:
                    # Request creator approval
                    approval = await self._request_creator_approval(creator_id, "rotation", key_id)
                    if not approval:
                        self.logger.info(f"Creator {creator_id} denied rotation for key {key_id}")
                        return False
            
            # Update key stage
            if key_id in self.active_keys:
                self.active_keys[key_id]['stage'] = KeyLifecycleStage.ROTATION_IN_PROGRESS
            
            # Perform rotation (simulated)
            await asyncio.sleep(0.1)  # Simulate rotation work
            
            # Generate new key data
            new_key_data = {'rotated_at': datetime.now().isoformat(), 'rotation_count': 1}
            
            # Update key
            if key_id in self.active_keys:
                self.active_keys[key_id]['key_data'] = new_key_data
                self.active_keys[key_id]['stage'] = KeyLifecycleStage.ACTIVE
                self.active_keys[key_id]['last_rotated'] = datetime.now()
            
            # Update metrics
            metrics = self.metrics_collector.get_metrics(key_id)
            if metrics:
                # Reset some metrics after rotation
                metrics.usage_count = 0
                metrics.error_count = 0
                metrics.last_used = datetime.now()
                self.metrics_collector.update_metrics(metrics)
            
            # Schedule next rotation
            if creator_id:
                creator_metadata = self.creator_profiles.get(creator_id, {})
                policy = self._find_applicable_policy(creator_metadata)
                if policy and policy.auto_rotation:
                    next_rotation = datetime.now() + timedelta(days=policy.rotation_frequency_days)
                    next_action = AutomationAction(
                        action_id=str(uuid.uuid4()),
                        action_type="rotate",
                        key_id=key_id,
                        trigger=AutomationTrigger.TIME_BASED,
                        scheduled_time=next_rotation,
                        creator_id=creator_id,
                        parameters={'policy_id': policy.policy_id}
                    )
                    self.automation_queue.append(next_action)
            
            self.automation_metrics['keys_rotated'] += 1
            self.logger.info(f"Successfully rotated key {key_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {e}")
            return False
    
    async def _execute_key_cleanup(self, action: AutomationAction) -> bool:
        """Execute key cleanup/destruction"""
        try:
            key_id = action.key_id
            
            # Update key stage
            if key_id in self.active_keys:
                self.active_keys[key_id]['stage'] = KeyLifecycleStage.PENDING_DESTRUCTION
            
            # Check if key is still in use
            metrics = self.metrics_collector.get_metrics(key_id)
            if metrics:
                time_since_last_use = datetime.now() - metrics.last_used
                if time_since_last_use < timedelta(hours=24):
                    # Key was used recently, defer cleanup
                    action.scheduled_time = datetime.now() + timedelta(days=7)
                    action.status = "pending"
                    self.logger.info(f"Deferred cleanup for recently used key {key_id}")
                    return True
            
            # Perform cleanup
            await asyncio.sleep(0.05)  # Simulate cleanup work
            
            # Mark as destroyed
            if key_id in self.active_keys:
                self.active_keys[key_id]['stage'] = KeyLifecycleStage.DESTROYED
                self.active_keys[key_id]['destroyed_at'] = datetime.now()
            
            self.automation_metrics['keys_destroyed'] += 1
            self.logger.info(f"Successfully cleaned up key {key_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Key cleanup failed: {e}")
            return False
    
    async def _execute_compliance_cleanup(self, action: AutomationAction) -> bool:
        """Execute compliance-based cleanup"""
        try:
            # Similar to regular cleanup but with compliance considerations
            return await self._execute_key_cleanup(action)
            
        except Exception as e:
            self.logger.error(f"Compliance cleanup failed: {e}")
            return False
    
    async def _execute_key_revocation(self, action: AutomationAction) -> bool:
        """Execute key revocation"""
        try:
            key_id = action.key_id
            
            # Update key stage
            if key_id in self.active_keys:
                self.active_keys[key_id]['stage'] = KeyLifecycleStage.EMERGENCY_REVOKED
                self.active_keys[key_id]['revoked_at'] = datetime.now()
            
            self.automation_metrics['keys_revoked'] += 1
            self.logger.info(f"Successfully revoked key {key_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Key revocation failed: {e}")
            return False
    
    async def _execute_creator_notification(self, action: AutomationAction) -> bool:
        """Execute creator notification"""
        try:
            creator_id = action.creator_id
            message = action.parameters.get('message', 'Key lifecycle notification')
            
            # Simulate sending notification
            self.logger.info(f"Notification sent to creator {creator_id}: {message}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Creator notification failed: {e}")
            return False
    
    async def _request_creator_approval(self, 
                                      creator_id: str, 
                                      action_type: str, 
                                      key_id: str) -> bool:
        """Request creator approval for action"""
        # Simulate approval request
        # In real implementation, this would integrate with notification system
        return True  # Auto-approve for demo
    
    async def _monitoring_loop(self):
        """Monitor key usage and performance"""
        while self.running:
            try:
                # Collect metrics for all active keys
                for key_id, key_info in self.active_keys.items():
                    if key_info['stage'] in [KeyLifecycleStage.ACTIVE, KeyLifecycleStage.ROTATION_DUE]:
                        await self._collect_key_metrics(key_id, key_info)
                
                # Check for performance issues
                await self._check_performance_thresholds()
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_key_metrics(self, key_id: str, key_info: Dict[str, Any]):
        """Collect metrics for a specific key"""
        try:
            # Simulate metric collection
            metrics = self.metrics_collector.get_metrics(key_id)
            if metrics:
                # Update metrics with simulated data
                metrics.usage_count += np.random.poisson(10)
                metrics.error_count += np.random.poisson(0.1)
                metrics.performance_ms = np.random.gamma(2, 10)
                metrics.encryption_operations += np.random.poisson(5)
                metrics.decryption_operations += np.random.poisson(5)
                metrics.last_used = datetime.now()
                
                self.metrics_collector.update_metrics(metrics)
            
        except Exception as e:
            self.logger.error(f"Metric collection failed for {key_id}: {e}")
    
    async def _check_performance_thresholds(self):
        """Check for performance threshold violations"""
        try:
            all_metrics = self.metrics_collector.get_all_metrics()
            
            for metrics in all_metrics:
                if metrics.creator_id:
                    creator_metadata = self.creator_profiles.get(metrics.creator_id, {})
                    policy = self._find_applicable_policy(creator_metadata)
                    
                    if policy:
                        # Check error rate threshold
                        error_rate = metrics.error_count / max(metrics.usage_count, 1)
                        if error_rate > policy.error_rate_threshold:
                            await self._trigger_emergency_action(
                                metrics.key_id, 
                                "high_error_rate",
                                f"Error rate {error_rate:.3f} exceeds threshold {policy.error_rate_threshold}"
                            )
                        
                        # Check performance threshold
                        if metrics.performance_ms > policy.performance_threshold_ms:
                            await self._trigger_emergency_action(
                                metrics.key_id,
                                "poor_performance", 
                                f"Performance {metrics.performance_ms:.1f}ms exceeds threshold {policy.performance_threshold_ms}ms"
                            )
            
        except Exception as e:
            self.logger.error(f"Performance threshold check failed: {e}")
    
    async def _trigger_emergency_action(self, key_id: str, reason: str, details: str):
        """Trigger emergency action for key"""
        self.logger.warning(f"Emergency action triggered for {key_id}: {reason} - {details}")
        
        # Create emergency rotation action
        emergency_action = AutomationAction(
            action_id=str(uuid.uuid4()),
            action_type="rotate",
            key_id=key_id,
            trigger=AutomationTrigger.SECURITY_EVENT,
            scheduled_time=datetime.now(),
            parameters={'reason': reason, 'details': details, 'emergency': True}
        )
        
        self.automation_queue.append(emergency_action)
    
    async def _ml_training_loop(self):
        """Periodically train ML models"""
        while self.running:
            try:
                # Collect training data
                all_metrics = self.metrics_collector.get_all_metrics()
                
                # Add training data (simulate actual rotation times)
                for metrics in all_metrics:
                    if metrics.key_id in self.active_keys:
                        key_info = self.active_keys[metrics.key_id]
                        if 'last_rotated' in key_info:
                            days_since_rotation = (datetime.now() - key_info['last_rotated']).days
                            if days_since_rotation > 0:
                                self.ml_engine.add_training_data(metrics, days_since_rotation)
                
                # Train models if enough data
                if len(self.ml_engine.training_data) >= 100:
                    success = self.ml_engine.train_models()
                    if success:
                        self.logger.info("ML models retrained successfully")
                
                await asyncio.sleep(3600)  # Train every hour
                
            except Exception as e:
                self.logger.error(f"ML training loop error: {e}")
                await asyncio.sleep(300)
    
    async def _anomaly_detection_loop(self):
        """Detect anomalous key behavior"""
        while self.running:
            try:
                if self.ml_engine.is_trained:
                    all_metrics = self.metrics_collector.get_all_metrics()
                    anomalous_keys = self.ml_engine.detect_anomalies(all_metrics)
                    
                    for key_id in anomalous_keys:
                        await self._investigate_anomaly(key_id)
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Anomaly detection loop error: {e}")
                await asyncio.sleep(300)
    
    async def _investigate_anomaly(self, key_id: str):
        """Investigate anomalous key behavior"""
        self.logger.warning(f"Anomaly detected for key {key_id}")
        
        # Create investigation notification
        investigation_action = AutomationAction(
            action_id=str(uuid.uuid4()),
            action_type="notify",
            key_id=key_id,
            trigger=AutomationTrigger.ANOMALY_DETECTION,
            scheduled_time=datetime.now(),
            parameters={'message': f'Anomaly detected for key {key_id}', 'priority': 'high'}
        )
        
        self.automation_queue.append(investigation_action)
    
    def get_key_status(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a key"""
        if key_id not in self.active_keys:
            return None
        
        key_info = self.active_keys[key_id]
        metrics = self.metrics_collector.get_metrics(key_id)
        
        # Get pending actions
        pending_actions = [action for action in self.automation_queue 
                         if action.key_id == key_id and action.status == "pending"]
        
        return {
            'key_id': key_id,
            'stage': key_info['stage'].value,
            'created_at': key_info['created_at'].isoformat(),
            'creator_id': key_info.get('creator_id'),
            'policy_id': key_info.get('policy_id'),
            'last_rotated': key_info.get('last_rotated').isoformat() if key_info.get('last_rotated') else None,
            'metrics': asdict(metrics) if metrics else None,
            'pending_actions': len(pending_actions),
            'next_rotation': min([action.scheduled_time for action in pending_actions 
                                if action.action_type == "rotate"], default=None)
        }
    
    def get_automation_metrics(self) -> Dict[str, Any]:
        """Get automation system metrics"""
        return {
            'automation_metrics': self.automation_metrics.copy(),
            'active_keys': len(self.active_keys),
            'pending_actions': len([action for action in self.automation_queue if action.status == "pending"]),
            'registered_creators': len(self.creator_profiles),
            'lifecycle_policies': len(self.lifecycle_policies),
            'ml_model_trained': self.ml_engine.is_trained,
            'automation_enabled': self.automation_enabled
        }
    
    async def stop_automation(self):
        """Stop automated lifecycle management"""
        self.running = False
        self.executor.shutdown(wait=True)
        self.logger.info("Key lifecycle automation stopped")


# Example usage
async def demo_lifecycle_automator():
    """Demonstrate automated key lifecycle management"""
    
    # Initialize automator
    automator = KeyLifecycleAutomator()
    
    # Register creators
    creators = [
        {
            'creator_id': 'vip_musician_001',
            'tier': 'vip',
            'creator_type': 'musician',
            'content_types': ['audio', 'video'],
            'applicable_regulations': ['GDPR', 'CCPA']
        },
        {
            'creator_id': 'premium_photographer_001', 
            'tier': 'premium',
            'creator_type': 'photographer',
            'content_types': ['image'],
            'applicable_regulations': ['GDPR']
        }
    ]
    
    for creator in creators:
        automator.register_creator(creator['creator_id'], creator)
    
    # Create keys with automated lifecycle
    keys_created = []
    for i, creator in enumerate(creators):
        key_id = f"auto_key_{i+1:03d}"
        key_data = {'algorithm': 'AES-256-GCM', 'purpose': 'content_encryption'}
        
        success = await automator.create_key_automated(
            key_id=key_id,
            creator_id=creator['creator_id'],
            content_type=creator['content_types'][0],
            key_data=key_data
        )
        
        if success:
            keys_created.append(key_id)
            print(f"Created automated key: {key_id}")
    
    # Start automation (run for a short time for demo)
    automation_task = asyncio.create_task(automator.start_automation())
    
    # Let automation run for a few seconds
    await asyncio.sleep(5)
    
    # Check key statuses
    for key_id in keys_created:
        status = automator.get_key_status(key_id)
        if status:
            print(f"Key {key_id} status: {json.dumps(status, indent=2, default=str)}")
    
    # Get automation metrics
    metrics = automator.get_automation_metrics()
    print(f"Automation metrics: {json.dumps(metrics, indent=2)}")
    
    # Stop automation
    await automator.stop_automation()
    automation_task.cancel()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demo
    asyncio.run(demo_lifecycle_automator())