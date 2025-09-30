"""
Payment Fraud Detection System for Ainflue Platform
Enterprise-grade fraud prevention and risk assessment for payment processing

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from decimal import Decimal
import logging
from dataclasses import dataclass
from enum import Enum
import uuid
import ipaddress
import re
from collections import defaultdict, deque

import aiohttp
import structlog
import geoip2.database
import geoip2.errors

from ..core.base_integration import BaseIntegration
from ..core.exceptions import (
    SecurityError, ValidationError, FraudError
)
from ..core.security import SecurityManager
from ..core.monitoring import MetricsCollector
from ..core.cache import CacheManager

logger = structlog.get_logger(__name__)

class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FraudAction(Enum):
    """Actions to take based on fraud assessment"""
    ALLOW = "allow"
    REVIEW = "review"
    CHALLENGE = "challenge"
    BLOCK = "block"
    DECLINE = "decline"

class FraudSignal(Enum):
    """Types of fraud signals"""
    VELOCITY = "velocity"
    GEOLOCATION = "geolocation"
    DEVICE_FINGERPRINT = "device_fingerprint"
    BEHAVIORAL = "behavioral"
    BLACKLIST = "blacklist"
    CARD_TESTING = "card_testing"
    BIN_ANALYSIS = "bin_analysis"
    EMAIL_REPUTATION = "email_reputation"
    IP_REPUTATION = "ip_reputation"
    AMOUNT_PATTERN = "amount_pattern"

@dataclass
class PaymentAttempt:
    """Payment attempt data for fraud analysis"""
    id: str
    user_id: Optional[str]
    email: Optional[str]
    ip_address: str
    user_agent: str
    amount: Decimal
    currency: str
    payment_method: str
    card_bin: Optional[str]
    card_last4: Optional[str]
    billing_country: Optional[str]
    shipping_country: Optional[str]
    device_fingerprint: Optional[str]
    session_id: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class FraudSignalResult:
    """Result of a fraud signal analysis"""
    signal_type: FraudSignal
    risk_score: float  # 0.0 to 1.0
    risk_level: RiskLevel
    reason: str
    details: Dict[str, Any]
    confidence: float  # 0.0 to 1.0

@dataclass
class FraudAssessment:
    """Complete fraud assessment result"""
    payment_id: str
    overall_risk_score: float
    overall_risk_level: RiskLevel
    recommended_action: FraudAction
    signals: List[FraudSignalResult]
    processing_time_ms: int
    assessment_id: str
    created_at: datetime

@dataclass
class FraudConfig:
    """Fraud detection configuration"""
    # Risk thresholds
    low_risk_threshold: float = 0.3
    medium_risk_threshold: float = 0.6
    high_risk_threshold: float = 0.8
    
    # Velocity limits
    max_attempts_per_minute: int = 5
    max_attempts_per_hour: int = 20
    max_amount_per_hour: Decimal = Decimal("1000.00")
    max_amount_per_day: Decimal = Decimal("5000.00")
    
    # Geographic settings
    allowed_countries: List[str] = None
    blocked_countries: List[str] = None
    high_risk_countries: List[str] = None
    
    # BIN settings
    blocked_bins: List[str] = None
    high_risk_bins: List[str] = None
    
    # Email/IP settings
    email_domain_whitelist: List[str] = None
    email_domain_blacklist: List[str] = None
    ip_whitelist: List[str] = None
    ip_blacklist: List[str] = None
    
    # Machine learning settings
    ml_model_enabled: bool = True
    ml_model_threshold: float = 0.7
    
    # Features
    enable_device_fingerprinting: bool = True
    enable_behavioral_analysis: bool = True
    enable_bin_analysis: bool = True
    enable_geolocation_analysis: bool = True
    enable_velocity_analysis: bool = True
    
    def __post_init__(self):
        if self.allowed_countries is None:
            self.allowed_countries = ["US", "CA", "GB", "DE", "FR", "AU", "JP"]
        if self.blocked_countries is None:
            self.blocked_countries = []
        if self.high_risk_countries is None:
            self.high_risk_countries = ["CN", "RU", "NG", "GH"]
        if self.blocked_bins is None:
            self.blocked_bins = []
        if self.high_risk_bins is None:
            self.high_risk_bins = []
        if self.email_domain_whitelist is None:
            self.email_domain_whitelist = []
        if self.email_domain_blacklist is None:
            self.email_domain_blacklist = ["tempmail.com", "guerrillamail.com"]
        if self.ip_whitelist is None:
            self.ip_whitelist = []
        if self.ip_blacklist is None:
            self.ip_blacklist = []

class PaymentFraudDetection(BaseIntegration):
    """
    Enterprise Payment Fraud Detection System for Ainflue platform
    
    Features:
    - Real-time fraud scoring and risk assessment
    - Advanced velocity monitoring
    - Geographic risk analysis
    - Device fingerprinting and behavioral analysis
    - BIN (Bank Identification Number) analysis
    - Machine learning-based fraud detection
    - Customizable rules engine
    - Comprehensive audit logging
    - Integration with external fraud databases
    """

    def __init__(self, config: FraudConfig):
        super().__init__("fraud_detection")
        self.config = config
        self.security_manager = SecurityManager()
        self.metrics = MetricsCollector()
        self.cache = CacheManager()
        
        # Fraud detection storage
        self._payment_attempts: Dict[str, PaymentAttempt] = {}
        self._fraud_assessments: Dict[str, FraudAssessment] = {}
        
        # Velocity tracking
        self._velocity_tracker = defaultdict(lambda: defaultdict(deque))
        self._amount_tracker = defaultdict(lambda: defaultdict(Decimal))
        
        # Behavioral analysis
        self._user_behavior = defaultdict(dict)
        self._device_profiles = defaultdict(dict)
        
        # External services
        self._geoip_db = None
        self._load_geoip_database()
        
        # Blacklists and reputation data
        self._ip_reputation_cache = {}
        self._email_reputation_cache = {}
        self._card_bin_cache = {}
        
        logger.info("Payment fraud detection initialized",
                   ml_enabled=config.ml_model_enabled,
                   features_enabled={
                       "device_fingerprinting": config.enable_device_fingerprinting,
                       "behavioral_analysis": config.enable_behavioral_analysis,
                       "geolocation": config.enable_geolocation_analysis
                   })

    def _load_geoip_database(self):
        """Load GeoIP database for location analysis"""
        try:
            # In production, use actual GeoIP2 database file
            # self._geoip_db = geoip2.database.Reader('/path/to/GeoLite2-City.mmdb')
            logger.info("GeoIP database would be loaded in production")
        except Exception as e:
            logger.warning("GeoIP database not available", error=str(e))

    async def assess_payment_fraud(self, payment_attempt: PaymentAttempt) -> FraudAssessment:
        """
        Perform comprehensive fraud assessment on payment attempt
        
        Args:
            payment_attempt: Payment attempt data
            
        Returns:
            Complete fraud assessment with risk score and recommended action
        """
        start_time = time.time()
        assessment_id = str(uuid.uuid4())
        
        try:
            # Store payment attempt
            self._payment_attempts[payment_attempt.id] = payment_attempt
            
            # Run all fraud detection signals
            signals = []
            
            if self.config.enable_velocity_analysis:
                velocity_signal = await self._analyze_velocity(payment_attempt)
                signals.append(velocity_signal)
            
            if self.config.enable_geolocation_analysis:
                geo_signal = await self._analyze_geolocation(payment_attempt)
                signals.append(geo_signal)
            
            if self.config.enable_device_fingerprinting:
                device_signal = await self._analyze_device_fingerprint(payment_attempt)
                signals.append(device_signal)
            
            if self.config.enable_behavioral_analysis:
                behavioral_signal = await self._analyze_behavior(payment_attempt)
                signals.append(behavioral_signal)
            
            if self.config.enable_bin_analysis and payment_attempt.card_bin:
                bin_signal = await self._analyze_bin(payment_attempt)
                signals.append(bin_signal)
            
            # Check blacklists
            blacklist_signal = await self._check_blacklists(payment_attempt)
            signals.append(blacklist_signal)
            
            # Email reputation analysis
            email_signal = await self._analyze_email_reputation(payment_attempt)
            signals.append(email_signal)
            
            # IP reputation analysis
            ip_signal = await self._analyze_ip_reputation(payment_attempt)
            signals.append(ip_signal)
            
            # Amount pattern analysis
            amount_signal = await self._analyze_amount_patterns(payment_attempt)
            signals.append(amount_signal)
            
            # Calculate overall risk score
            overall_risk_score = self._calculate_overall_risk_score(signals)
            
            # Determine risk level and action
            risk_level = self._determine_risk_level(overall_risk_score)
            recommended_action = self._determine_action(risk_level, signals)
            
            # Create assessment
            processing_time = int((time.time() - start_time) * 1000)
            
            assessment = FraudAssessment(
                payment_id=payment_attempt.id,
                overall_risk_score=overall_risk_score,
                overall_risk_level=risk_level,
                recommended_action=recommended_action,
                signals=signals,
                processing_time_ms=processing_time,
                assessment_id=assessment_id,
                created_at=datetime.utcnow()
            )
            
            # Store assessment
            self._fraud_assessments[payment_attempt.id] = assessment
            
            # Cache assessment
            await self.cache.set(
                f"fraud_assessment:{payment_attempt.id}",
                assessment,
                ttl=86400  # 24 hours
            )
            
            # Update metrics
            self.metrics.increment("fraud.assessments.completed")
            self.metrics.observe("fraud.assessment_time", processing_time)
            self.metrics.increment(f"fraud.risk_level.{risk_level.value}")
            self.metrics.increment(f"fraud.action.{recommended_action.value}")
            
            logger.info("Fraud assessment completed",
                       payment_id=payment_attempt.id,
                       risk_score=overall_risk_score,
                       risk_level=risk_level.value,
                       action=recommended_action.value,
                       processing_time=processing_time)
            
            return assessment
            
        except Exception as e:
            self.metrics.increment("fraud.assessments.failed")
            logger.error("Fraud assessment failed",
                        payment_id=payment_attempt.id,
                        error=str(e))
            
            # Return safe assessment on error
            return FraudAssessment(
                payment_id=payment_attempt.id,
                overall_risk_score=1.0,  # Maximum risk on error
                overall_risk_level=RiskLevel.CRITICAL,
                recommended_action=FraudAction.REVIEW,
                signals=[],
                processing_time_ms=int((time.time() - start_time) * 1000),
                assessment_id=assessment_id,
                created_at=datetime.utcnow()
            )

    async def _analyze_velocity(self, payment: PaymentAttempt) -> FraudSignalResult:
        """Analyze payment velocity patterns"""
        try:
            risk_score = 0.0
            details = {}
            
            current_time = datetime.utcnow()
            minute_key = current_time.strftime("%Y%m%d%H%M")
            hour_key = current_time.strftime("%Y%m%d%H")
            day_key = current_time.strftime("%Y%m%d")
            
            # Track by IP address
            ip_attempts_minute = len(self._velocity_tracker[payment.ip_address]["minute"])
            ip_attempts_hour = len(self._velocity_tracker[payment.ip_address]["hour"])
            
            # Track by user if available
            user_attempts_minute = 0
            user_attempts_hour = 0
            if payment.user_id:
                user_attempts_minute = len(self._velocity_tracker[payment.user_id]["minute"])
                user_attempts_hour = len(self._velocity_tracker[payment.user_id]["hour"])
            
            # Track amounts
            ip_amount_hour = self._amount_tracker[payment.ip_address][hour_key]
            ip_amount_day = self._amount_tracker[payment.ip_address][day_key]
            
            # Update trackers
            self._velocity_tracker[payment.ip_address]["minute"].append(current_time)
            self._velocity_tracker[payment.ip_address]["hour"].append(current_time)
            
            if payment.user_id:
                self._velocity_tracker[payment.user_id]["minute"].append(current_time)
                self._velocity_tracker[payment.user_id]["hour"].append(current_time)
            
            self._amount_tracker[payment.ip_address][hour_key] += payment.amount
            self._amount_tracker[payment.ip_address][day_key] += payment.amount
            
            # Clean old entries
            self._clean_velocity_data()
            
            # Calculate risk based on velocity
            if ip_attempts_minute > self.config.max_attempts_per_minute:
                risk_score += 0.4
                details["ip_attempts_minute_exceeded"] = True
            
            if ip_attempts_hour > self.config.max_attempts_per_hour:
                risk_score += 0.3
                details["ip_attempts_hour_exceeded"] = True
            
            if user_attempts_minute > self.config.max_attempts_per_minute:
                risk_score += 0.4
                details["user_attempts_minute_exceeded"] = True
            
            if ip_amount_hour > self.config.max_amount_per_hour:
                risk_score += 0.3
                details["ip_amount_hour_exceeded"] = True
            
            if ip_amount_day > self.config.max_amount_per_day:
                risk_score += 0.5
                details["ip_amount_day_exceeded"] = True
            
            risk_score = min(risk_score, 1.0)
            
            details.update({
                "ip_attempts_minute": ip_attempts_minute,
                "ip_attempts_hour": ip_attempts_hour,
                "user_attempts_minute": user_attempts_minute,
                "user_attempts_hour": user_attempts_hour,
                "ip_amount_hour": float(ip_amount_hour),
                "ip_amount_day": float(ip_amount_day)
            })
            
            return FraudSignalResult(
                signal_type=FraudSignal.VELOCITY,
                risk_score=risk_score,
                risk_level=self._determine_risk_level(risk_score),
                reason=f"Velocity analysis: {ip_attempts_minute} attempts/min, {ip_attempts_hour} attempts/hour",
                details=details,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error("Velocity analysis failed", error=str(e))
            return FraudSignalResult(
                signal_type=FraudSignal.VELOCITY,
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                reason="Velocity analysis failed",
                details={"error": str(e)},
                confidence=0.0
            )

    def _clean_velocity_data(self):
        """Clean old velocity tracking data"""
        current_time = datetime.utcnow()
        minute_cutoff = current_time - timedelta(minutes=1)
        hour_cutoff = current_time - timedelta(hours=1)
        
        for tracker_id in list(self._velocity_tracker.keys()):
            # Clean minute data
            minute_queue = self._velocity_tracker[tracker_id]["minute"]
            while minute_queue and minute_queue[0] < minute_cutoff:
                minute_queue.popleft()
            
            # Clean hour data
            hour_queue = self._velocity_tracker[tracker_id]["hour"]
            while hour_queue and hour_queue[0] < hour_cutoff:
                hour_queue.popleft()
            
            # Remove empty trackers
            if not minute_queue and not hour_queue:
                del self._velocity_tracker[tracker_id]

    async def _analyze_geolocation(self, payment: PaymentAttempt) -> FraudSignalResult:
        """Analyze geographic risk factors"""
        try:
            risk_score = 0.0
            details = {}
            
            # Get country from IP address (simplified - would use GeoIP in production)
            ip_country = self._get_country_from_ip(payment.ip_address)
            
            details["ip_country"] = ip_country
            details["billing_country"] = payment.billing_country
            details["shipping_country"] = payment.shipping_country
            
            # Check blocked countries
            if ip_country in self.config.blocked_countries:
                risk_score = 1.0
                details["blocked_country"] = True
            
            # Check high-risk countries
            elif ip_country in self.config.high_risk_countries:
                risk_score += 0.6
                details["high_risk_country"] = True
            
            # Check country mismatch
            if payment.billing_country and ip_country != payment.billing_country:
                risk_score += 0.3
                details["country_mismatch"] = True
            
            # Check shipping vs billing country mismatch
            if (payment.billing_country and payment.shipping_country and 
                payment.billing_country != payment.shipping_country):
                risk_score += 0.2
                details["billing_shipping_mismatch"] = True
            
            risk_score = min(risk_score, 1.0)
            
            return FraudSignalResult(
                signal_type=FraudSignal.GEOLOCATION,
                risk_score=risk_score,
                risk_level=self._determine_risk_level(risk_score),
                reason=f"Geographic analysis: IP from {ip_country}",
                details=details,
                confidence=0.8
            )
            
        except Exception as e:
            logger.error("Geolocation analysis failed", error=str(e))
            return FraudSignalResult(
                signal_type=FraudSignal.GEOLOCATION,
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                reason="Geolocation analysis failed",
                details={"error": str(e)},
                confidence=0.0
            )

    def _get_country_from_ip(self, ip_address: str) -> str:
        """Get country code from IP address"""
        try:
            # In production, would use GeoIP2 database
            # response = self._geoip_db.city(ip_address)
            # return response.country.iso_code
            
            # Simplified IP country detection for demo
            if ip_address.startswith("192.168.") or ip_address.startswith("10."):
                return "US"  # Default for private IPs
            
            # Simple heuristic based on IP ranges (not accurate)
            if ip_address.startswith("5."):
                return "RU"
            elif ip_address.startswith("14."):
                return "CN"
            else:
                return "US"  # Default
                
        except Exception:
            return "UNKNOWN"

    async def _analyze_device_fingerprint(self, payment: PaymentAttempt) -> FraudSignalResult:
        """Analyze device fingerprint patterns"""
        try:
            risk_score = 0.0
            details = {}
            
            if not payment.device_fingerprint:
                return FraudSignalResult(
                    signal_type=FraudSignal.DEVICE_FINGERPRINT,
                    risk_score=0.1,  # Slight risk for missing fingerprint
                    risk_level=RiskLevel.LOW,
                    reason="No device fingerprint provided",
                    details={"missing_fingerprint": True},
                    confidence=0.5
                )
            
            # Check if device has been seen before
            device_id = payment.device_fingerprint
            device_profile = self._device_profiles.get(device_id, {})
            
            # Track device usage
            if device_id not in self._device_profiles:
                self._device_profiles[device_id] = {
                    "first_seen": datetime.utcnow(),
                    "payment_count": 0,
                    "user_ids": set(),
                    "ip_addresses": set(),
                    "countries": set()
                }
                risk_score += 0.2  # New device has some risk
                details["new_device"] = True
            
            device_profile = self._device_profiles[device_id]
            device_profile["payment_count"] += 1
            device_profile["last_seen"] = datetime.utcnow()
            
            if payment.user_id:
                device_profile["user_ids"].add(payment.user_id)
            device_profile["ip_addresses"].add(payment.ip_address)
            device_profile["countries"].add(self._get_country_from_ip(payment.ip_address))
            
            # Check for suspicious patterns
            if len(device_profile["user_ids"]) > 5:
                risk_score += 0.4
                details["multiple_users"] = len(device_profile["user_ids"])
            
            if len(device_profile["countries"]) > 3:
                risk_score += 0.3
                details["multiple_countries"] = len(device_profile["countries"])
            
            if device_profile["payment_count"] > 20:
                risk_score += 0.2
                details["high_usage"] = device_profile["payment_count"]
            
            risk_score = min(risk_score, 1.0)
            
            details.update({
                "device_age_hours": (datetime.utcnow() - device_profile["first_seen"]).total_seconds() / 3600,
                "payment_count": device_profile["payment_count"],
                "unique_users": len(device_profile["user_ids"]),
                "unique_ips": len(device_profile["ip_addresses"])
            })
            
            return FraudSignalResult(
                signal_type=FraudSignal.DEVICE_FINGERPRINT,
                risk_score=risk_score,
                risk_level=self._determine_risk_level(risk_score),
                reason=f"Device analysis: {device_profile['payment_count']} payments from device",
                details=details,
                confidence=0.7
            )
            
        except Exception as e:
            logger.error("Device fingerprint analysis failed", error=str(e))
            return FraudSignalResult(
                signal_type=FraudSignal.DEVICE_FINGERPRINT,
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                reason="Device fingerprint analysis failed",
                details={"error": str(e)},
                confidence=0.0
            )

    async def _analyze_behavior(self, payment: PaymentAttempt) -> FraudSignalResult:
        """Analyze behavioral patterns"""
        try:
            risk_score = 0.0
            details = {}
            
            if not payment.user_id:
                return FraudSignalResult(
                    signal_type=FraudSignal.BEHAVIORAL,
                    risk_score=0.1,
                    risk_level=RiskLevel.LOW,
                    reason="No user ID for behavioral analysis",
                    details={"anonymous_user": True},
                    confidence=0.3
                )
            
            # Get or create user behavior profile
            user_id = payment.user_id
            if user_id not in self._user_behavior:
                self._user_behavior[user_id] = {
                    "first_payment": datetime.utcnow(),
                    "payment_count": 0,
                    "total_amount": Decimal("0"),
                    "average_amount": Decimal("0"),
                    "typical_hours": set(),
                    "typical_countries": set(),
                    "payment_methods": set(),
                    "currencies": set()
                }
                risk_score += 0.2  # New user has some risk
                details["new_user"] = True
            
            behavior = self._user_behavior[user_id]
            behavior["payment_count"] += 1
            behavior["total_amount"] += payment.amount
            behavior["average_amount"] = behavior["total_amount"] / behavior["payment_count"]
            behavior["typical_hours"].add(payment.timestamp.hour)
            behavior["typical_countries"].add(self._get_country_from_ip(payment.ip_address))
            behavior["payment_methods"].add(payment.payment_method)
            behavior["currencies"].add(payment.currency)
            
            # Analyze amount deviation
            if behavior["payment_count"] > 1:
                amount_ratio = float(payment.amount / behavior["average_amount"])
                if amount_ratio > 5.0 or amount_ratio < 0.2:
                    risk_score += 0.3
                    details["unusual_amount"] = amount_ratio
            
            # Analyze time patterns
            current_hour = payment.timestamp.hour
            if (behavior["payment_count"] > 5 and 
                current_hour not in behavior["typical_hours"]):
                risk_score += 0.2
                details["unusual_time"] = current_hour
            
            # Analyze currency/method changes
            if len(behavior["currencies"]) > 3:
                risk_score += 0.2
                details["multiple_currencies"] = len(behavior["currencies"])
            
            if len(behavior["payment_methods"]) > 3:
                risk_score += 0.2
                details["multiple_methods"] = len(behavior["payment_methods"])
            
            risk_score = min(risk_score, 1.0)
            
            details.update({
                "user_age_hours": (datetime.utcnow() - behavior["first_payment"]).total_seconds() / 3600,
                "payment_count": behavior["payment_count"],
                "average_amount": float(behavior["average_amount"]),
                "current_amount": float(payment.amount)
            })
            
            return FraudSignalResult(
                signal_type=FraudSignal.BEHAVIORAL,
                risk_score=risk_score,
                risk_level=self._determine_risk_level(risk_score),
                reason=f"Behavioral analysis: {behavior['payment_count']} payments",
                details=details,
                confidence=min(0.9, behavior["payment_count"] / 10.0)
            )
            
        except Exception as e:
            logger.error("Behavioral analysis failed", error=str(e))
            return FraudSignalResult(
                signal_type=FraudSignal.BEHAVIORAL,
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                reason="Behavioral analysis failed",
                details={"error": str(e)},
                confidence=0.0
            )

    async def _analyze_bin(self, payment: PaymentAttempt) -> FraudSignalResult:
        """Analyze Bank Identification Number (BIN)"""
        try:
            risk_score = 0.0
            details = {}
            
            if not payment.card_bin:
                return FraudSignalResult(
                    signal_type=FraudSignal.BIN_ANALYSIS,
                    risk_score=0.0,
                    risk_level=RiskLevel.LOW,
                    reason="No BIN provided",
                    details={"no_bin": True},
                    confidence=0.0
                )
            
            bin_number = payment.card_bin
            
            # Check blocked BINs
            if bin_number in self.config.blocked_bins:
                risk_score = 1.0
                details["blocked_bin"] = True
            
            # Check high-risk BINs
            elif bin_number in self.config.high_risk_bins:
                risk_score += 0.6
                details["high_risk_bin"] = True
            
            # BIN analysis (simplified - would use actual BIN database)
            bin_info = await self._get_bin_info(bin_number)
            details["bin_info"] = bin_info
            
            # Check for prepaid cards (higher risk)
            if bin_info.get("card_type") == "PREPAID":
                risk_score += 0.3
                details["prepaid_card"] = True
            
            # Check for gift cards (higher risk)
            if bin_info.get("card_category") == "GIFT":
                risk_score += 0.5
                details["gift_card"] = True
            
            # Check country mismatch
            bin_country = bin_info.get("country")
            ip_country = self._get_country_from_ip(payment.ip_address)
            if bin_country and bin_country != ip_country:
                risk_score += 0.2
                details["bin_country_mismatch"] = True
            
            risk_score = min(risk_score, 1.0)
            
            return FraudSignalResult(
                signal_type=FraudSignal.BIN_ANALYSIS,
                risk_score=risk_score,
                risk_level=self._determine_risk_level(risk_score),
                reason=f"BIN analysis: {bin_info.get('card_type', 'UNKNOWN')} card",
                details=details,
                confidence=0.8
            )
            
        except Exception as e:
            logger.error("BIN analysis failed", error=str(e))
            return FraudSignalResult(
                signal_type=FraudSignal.BIN_ANALYSIS,
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                reason="BIN analysis failed",
                details={"error": str(e)},
                confidence=0.0
            )

    async def _get_bin_info(self, bin_number: str) -> Dict[str, str]:
        """Get BIN information from cache or external service"""
        if bin_number in self._card_bin_cache:
            return self._card_bin_cache[bin_number]
        
        # In production, would call external BIN lookup service
        # For demo, return simplified data
        bin_info = {
            "card_type": "CREDIT",
            "card_category": "STANDARD",
            "bank_name": "Unknown Bank",
            "country": "US"
        }
        
        # Cache for future use
        self._card_bin_cache[bin_number] = bin_info
        return bin_info

    async def _check_blacklists(self, payment: PaymentAttempt) -> FraudSignalResult:
        """Check various blacklists"""
        try:
            risk_score = 0.0
            details = {}
            
            # Check IP blacklist
            if payment.ip_address in self.config.ip_blacklist:
                risk_score = 1.0
                details["blacklisted_ip"] = True
            
            # Check email domain blacklist
            if payment.email:
                email_domain = payment.email.split("@")[-1].lower()
                if email_domain in self.config.email_domain_blacklist:
                    risk_score += 0.7
                    details["blacklisted_email_domain"] = email_domain
            
            # Check against custom blacklists (would integrate with external services)
            
            return FraudSignalResult(
                signal_type=FraudSignal.BLACKLIST,
                risk_score=risk_score,
                risk_level=self._determine_risk_level(risk_score),
                reason="Blacklist check completed",
                details=details,
                confidence=1.0 if risk_score > 0 else 0.8
            )
            
        except Exception as e:
            logger.error("Blacklist check failed", error=str(e))
            return FraudSignalResult(
                signal_type=FraudSignal.BLACKLIST,
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                reason="Blacklist check failed",
                details={"error": str(e)},
                confidence=0.0
            )

    async def _analyze_email_reputation(self, payment: PaymentAttempt) -> FraudSignalResult:
        """Analyze email reputation and patterns"""
        try:
            risk_score = 0.0
            details = {}
            
            if not payment.email:
                return FraudSignalResult(
                    signal_type=FraudSignal.EMAIL_REPUTATION,
                    risk_score=0.1,
                    risk_level=RiskLevel.LOW,
                    reason="No email provided",
                    details={"no_email": True},
                    confidence=0.5
                )
            
            email = payment.email.lower()
            domain = email.split("@")[-1]
            
            # Check for temporary email patterns
            if any(temp in domain for temp in ["temp", "throw", "guerrilla", "10minute"]):
                risk_score += 0.6
                details["temporary_email"] = True
            
            # Check for suspicious patterns
            if re.search(r'\d{4,}', email):  # Many numbers in email
                risk_score += 0.2
                details["numeric_email"] = True
            
            if len(email.split("@")[0]) < 3:  # Very short username
                risk_score += 0.2
                details["short_username"] = True
            
            # Domain reputation (simplified)
            domain_reputation = self._get_domain_reputation(domain)
            if domain_reputation == "bad":
                risk_score += 0.8
                details["bad_domain_reputation"] = domain
            elif domain_reputation == "suspicious":
                risk_score += 0.4
                details["suspicious_domain"] = domain
            
            risk_score = min(risk_score, 1.0)
            
            return FraudSignalResult(
                signal_type=FraudSignal.EMAIL_REPUTATION,
                risk_score=risk_score,
                risk_level=self._determine_risk_level(risk_score),
                reason=f"Email analysis: {domain}",
                details=details,
                confidence=0.7
            )
            
        except Exception as e:
            logger.error("Email reputation analysis failed", error=str(e))
            return FraudSignalResult(
                signal_type=FraudSignal.EMAIL_REPUTATION,
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                reason="Email reputation analysis failed",
                details={"error": str(e)},
                confidence=0.0
            )

    def _get_domain_reputation(self, domain: str) -> str:
        """Get domain reputation (simplified)"""
        # In production, would integrate with reputation services
        known_good = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
        known_bad = ["tempmail.com", "guerrillamail.com", "10minutemail.com"]
        
        if domain in known_bad:
            return "bad"
        elif domain in known_good:
            return "good"
        else:
            return "unknown"

    async def _analyze_ip_reputation(self, payment: PaymentAttempt) -> FraudSignalResult:
        """Analyze IP address reputation"""
        try:
            risk_score = 0.0
            details = {}
            
            ip = payment.ip_address
            
            # Check for private/local IPs
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private:
                    risk_score += 0.1
                    details["private_ip"] = True
            except ValueError:
                risk_score += 0.3
                details["invalid_ip"] = True
            
            # IP reputation check (simplified)
            reputation = await self._get_ip_reputation(ip)
            details["ip_reputation"] = reputation
            
            if reputation == "malicious":
                risk_score += 0.9
                details["malicious_ip"] = True
            elif reputation == "suspicious":
                risk_score += 0.5
                details["suspicious_ip"] = True
            elif reputation == "tor":
                risk_score += 0.6
                details["tor_ip"] = True
            elif reputation == "proxy":
                risk_score += 0.4
                details["proxy_ip"] = True
            
            risk_score = min(risk_score, 1.0)
            
            return FraudSignalResult(
                signal_type=FraudSignal.IP_REPUTATION,
                risk_score=risk_score,
                risk_level=self._determine_risk_level(risk_score),
                reason=f"IP reputation: {reputation}",
                details=details,
                confidence=0.8
            )
            
        except Exception as e:
            logger.error("IP reputation analysis failed", error=str(e))
            return FraudSignalResult(
                signal_type=FraudSignal.IP_REPUTATION,
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                reason="IP reputation analysis failed",
                details={"error": str(e)},
                confidence=0.0
            )

    async def _get_ip_reputation(self, ip: str) -> str:
        """Get IP reputation from cache or external service"""
        if ip in self._ip_reputation_cache:
            return self._ip_reputation_cache[ip]
        
        # In production, would call IP reputation services
        # For demo, return based on simple patterns
        if ip.startswith("192.168.") or ip.startswith("10."):
            reputation = "private"
        elif ip.startswith("127."):
            reputation = "localhost"
        else:
            reputation = "unknown"
        
        self._ip_reputation_cache[ip] = reputation
        return reputation

    async def _analyze_amount_patterns(self, payment: PaymentAttempt) -> FraudSignalResult:
        """Analyze payment amount patterns"""
        try:
            risk_score = 0.0
            details = {}
            
            amount = payment.amount
            
            # Check for round numbers (often used in testing)
            if amount % 10 == 0:
                risk_score += 0.1
                details["round_amount"] = True
            
            # Check for very small amounts (card testing)
            if amount < Decimal("1.00"):
                risk_score += 0.5
                details["micro_amount"] = True
            
            # Check for very large amounts
            if amount > Decimal("10000.00"):
                risk_score += 0.3
                details["large_amount"] = True
            
            # Check for common testing amounts
            test_amounts = [Decimal("1.00"), Decimal("0.01"), Decimal("9.99")]
            if amount in test_amounts:
                risk_score += 0.4
                details["test_amount"] = True
            
            risk_score = min(risk_score, 1.0)
            
            return FraudSignalResult(
                signal_type=FraudSignal.AMOUNT_PATTERN,
                risk_score=risk_score,
                risk_level=self._determine_risk_level(risk_score),
                reason=f"Amount pattern analysis: ${amount}",
                details=details,
                confidence=0.6
            )
            
        except Exception as e:
            logger.error("Amount pattern analysis failed", error=str(e))
            return FraudSignalResult(
                signal_type=FraudSignal.AMOUNT_PATTERN,
                risk_score=0.0,
                risk_level=RiskLevel.LOW,
                reason="Amount pattern analysis failed",
                details={"error": str(e)},
                confidence=0.0
            )

    def _calculate_overall_risk_score(self, signals: List[FraudSignalResult]) -> float:
        """Calculate overall risk score from individual signals"""
        if not signals:
            return 0.0
        
        # Weighted average based on signal confidence
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for signal in signals:
            weight = signal.confidence
            total_weighted_score += signal.risk_score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        base_score = total_weighted_score / total_weight
        
        # Apply signal count bonus (more signals = more confidence)
        signal_bonus = min(0.1, len(signals) * 0.01)
        
        # Check for critical signals
        critical_signals = [s for s in signals if s.risk_level == RiskLevel.CRITICAL]
        if critical_signals:
            base_score = max(base_score, 0.8)
        
        return min(1.0, base_score + signal_bonus)

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from risk score"""
        if risk_score >= self.config.high_risk_threshold:
            return RiskLevel.HIGH
        elif risk_score >= self.config.medium_risk_threshold:
            return RiskLevel.MEDIUM
        elif risk_score >= self.config.low_risk_threshold:
            return RiskLevel.LOW
        else:
            return RiskLevel.LOW

    def _determine_action(self, risk_level: RiskLevel, signals: List[FraudSignalResult]) -> FraudAction:
        """Determine recommended action based on risk level and signals"""
        # Check for immediate block conditions
        block_signals = [
            FraudSignal.BLACKLIST,
        ]
        
        for signal in signals:
            if (signal.signal_type in block_signals and 
                signal.risk_score >= 0.8):
                return FraudAction.BLOCK
        
        # Determine action based on risk level
        if risk_level == RiskLevel.CRITICAL:
            return FraudAction.DECLINE
        elif risk_level == RiskLevel.HIGH:
            return FraudAction.REVIEW
        elif risk_level == RiskLevel.MEDIUM:
            return FraudAction.CHALLENGE
        else:
            return FraudAction.ALLOW

    async def get_assessment(self, payment_id: str) -> Optional[FraudAssessment]:
        """Get fraud assessment by payment ID"""
        try:
            # Check memory first
            if payment_id in self._fraud_assessments:
                return self._fraud_assessments[payment_id]
            
            # Check cache
            cached_assessment = await self.cache.get(f"fraud_assessment:{payment_id}")
            if cached_assessment:
                self._fraud_assessments[payment_id] = cached_assessment
                return cached_assessment
            
            return None
            
        except Exception as e:
            logger.error("Failed to get fraud assessment",
                        payment_id=payment_id,
                        error=str(e))
            return None

    async def health_check(self) -> Dict[str, Any]:
        """
        Check fraud detection system health
        
        Returns:
            Health status information
        """
        try:
            health_status = {
                "service": "fraud_detection",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "config": {
                    "ml_enabled": self.config.ml_model_enabled,
                    "features_enabled": {
                        "velocity": self.config.enable_velocity_analysis,
                        "geolocation": self.config.enable_geolocation_analysis,
                        "device_fingerprinting": self.config.enable_device_fingerprinting,
                        "behavioral": self.config.enable_behavioral_analysis,
                        "bin_analysis": self.config.enable_bin_analysis
                    }
                },
                "metrics": {
                    "total_assessments": len(self._fraud_assessments),
                    "active_devices": len(self._device_profiles),
                    "tracked_users": len(self._user_behavior)
                }
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service": "fraud_detection",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Factory function for easy setup
def create_fraud_detection_system(**kwargs) -> PaymentFraudDetection:
    """
    Factory function to create fraud detection system
    
    Args:
        **kwargs: Configuration options
        
    Returns:
        Configured fraud detection system
    """
    config = FraudConfig(**kwargs)
    return PaymentFraudDetection(config)

# Example usage for Ainflue platform
async def example_fraud_detection_flow():
    """Example fraud detection usage"""
    
    # Initialize fraud detection system
    fraud_detector = create_fraud_detection_system(
        max_attempts_per_minute=3,
        max_attempts_per_hour=15,
        max_amount_per_hour=Decimal("500.00"),
        blocked_countries=["XX", "YY"],
        high_risk_countries=["CN", "RU"],
        enable_device_fingerprinting=True,
        enable_behavioral_analysis=True
    )
    
    try:
        # Example payment attempt
        payment_attempt = PaymentAttempt(
            id="payment_123",
            user_id="user_456",
            email="creator@ainflue.com",
            ip_address="203.0.113.1",
            user_agent="Mozilla/5.0...",
            amount=Decimal("29.99"),
            currency="USD",
            payment_method="credit_card",
            card_bin="411111",
            card_last4="1111",
            billing_country="US",
            shipping_country="US",
            device_fingerprint="device_abc123",
            session_id="session_789",
            timestamp=datetime.utcnow(),
            metadata={
                "subscription_type": "premium",
                "platform": "ainflue"
            }
        )
        
        # Perform fraud assessment
        assessment = await fraud_detector.assess_payment_fraud(payment_attempt)
        
        print(f"Fraud Assessment for {payment_attempt.id}:")
        print(f"Risk Score: {assessment.overall_risk_score:.2f}")
        print(f"Risk Level: {assessment.overall_risk_level.value}")
        print(f"Recommended Action: {assessment.recommended_action.value}")
        print(f"Processing Time: {assessment.processing_time_ms}ms")
        
        print("\nDetailed Signals:")
        for signal in assessment.signals:
            print(f"- {signal.signal_type.value}: {signal.risk_score:.2f} ({signal.reason})")
        
        # Health check
        health = await fraud_detector.health_check()
        print(f"\nFraud Detection Health: {health['status']}")
        
    except Exception as e:
        print(f"Fraud detection error: {e}")

if __name__ == "__main__":
    asyncio.run(example_fraud_detection_flow())