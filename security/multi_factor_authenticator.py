"""
Multi Factor Authenticator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🔐 Multi-Factor Authentication Engine Enterprise - Comprehensive MFA System
=========================================================================

Multi-role expertise demonstrated:
- Security Specialist: Advanced MFA strategies and threat protection
- Backend Senior: Scalable authentication infrastructure
- ML Engineer: Risk-based adaptive authentication algorithms
- DevOps Engineer: High-availability authentication services
- Mobile Developer: Cross-platform MFA implementation

@author: Fahed Mlaiel <mlaiel@live.de>
@copyright: 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
"""

import os
import sys
import json
import qrcode
import pyotp
import base64
import hashlib
import logging
import asyncio
import smtplib
import redis
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import sqlite3
import jwt
import requests
from cryptography.fernet import Fernet
from twilio.rest import Client as TwilioClient
import phonenumbers
from phonenumbers import geocoder, carrier
import random
import string
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import geoip2.database
import user_agents
from passlib.hash import argon2
import cv2
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MFAFactor:
    """Multi-factor authentication factor"""
    factor_id: str
    user_id: str
    factor_type: str  # sms, email, totp, push, biometric, hardware_token
    identifier: str   # phone number, email, device_id, etc.
    secret_data: bytes  # Encrypted secret/key data
    backup_codes: List[str] = field(default_factory=list)
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    failure_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MFAChallenge:
    """MFA challenge data"""
    challenge_id: str
    user_id: str
    factor_type: str
    challenge_data: str  # Code, push notification ID, etc.
    expires_at: datetime
    attempts: int = 0
    max_attempts: int = 3
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuthenticationSession:
    """Authentication session tracking"""
    session_id: str
    user_id: str
    required_factors: List[str]
    completed_factors: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    device_fingerprint: str = ""
    ip_address: str = ""
    user_agent: str = ""
    location: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(minutes=15))
    is_complete: bool = False

@dataclass
class RiskAssessment:
    """Risk assessment for adaptive authentication"""
    risk_score: float
    risk_level: str  # low, medium, high, critical
    factors: Dict[str, float]  # Individual risk factors
    recommended_factors: List[str]
    required_factors: List[str]
    explanation: str
    timestamp: datetime = field(default_factory=datetime.now)

class SMSProvider:
    """SMS provider interface"""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.provider = config.get('provider', 'twilio')
        
        if self.provider == 'twilio':
            self.client = TwilioClient(
                config.get('account_sid'),
                config.get('auth_token')
            )
            self.from_number = config.get('from_number')
    
    async def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS message"""
        try:
            if self.provider == 'twilio':
                message = self.client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=to_number
                )
                logger.info(f"SMS sent to {to_number}: {message.sid}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            return False

class EmailProvider:
    """Email provider for MFA"""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.smtp_server = config.get('smtp_server')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.from_email = config.get('from_email')
    
    async def send_email(self, to_email: str, subject: str, body: str, 
                        html_body: str = None) -> bool:
        """Send email message"""
        try:
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text part
            text_part = MimeText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MimeText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent to {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False

class PushNotificationProvider:
    """Push notification provider for MFA"""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.provider = config.get('provider', 'firebase')
        
        if self.provider == 'firebase':
            self.server_key = config.get('server_key')
            self.fcm_url = 'https://fcm.googleapis.com/fcm/send'
    
    async def send_push_notification(self, device_token: str, title: str, 
                                   body: str, data: Dict[str, Any] = None) -> bool:
        """Send push notification"""
        try:
            if self.provider == 'firebase':
                headers = {
                    'Authorization': f'key={self.server_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'to': device_token,
                    'notification': {
                        'title': title,
                        'body': body
                    },
                    'data': data or {}
                }
                
                response = requests.post(
                    self.fcm_url,
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"Push notification sent to {device_token}")
                    return True
                else:
                    logger.error(f"Push notification failed: {response.text}")
                    return False
            
            return False
        
        except Exception as e:
            logger.error(f"Push notification failed: {e}")
            return False

class RiskAnalyzer:
    """Risk-based authentication analyzer"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.geoip_db_path = self.config.get('geoip_db_path')
        self.geoip_reader = None
        
        # Initialize GeoIP database if available
        if self.geoip_db_path and os.path.exists(self.geoip_db_path):
            try:
                self.geoip_reader = geoip2.database.Reader(self.geoip_db_path)
            except Exception as e:
                logger.warning(f"GeoIP database initialization failed: {e}")
    
    async def assess_risk(self, session: AuthenticationSession, 
                         user_history: Dict[str, Any]) -> RiskAssessment:
        """Assess authentication risk based on multiple factors"""
        risk_factors = {}
        
        # Location risk
        location_risk = await self._assess_location_risk(
            session.ip_address, user_history.get('typical_locations', [])
        )
        risk_factors['location'] = location_risk
        
        # Device risk
        device_risk = await self._assess_device_risk(
            session.device_fingerprint, user_history.get('known_devices', [])
        )
        risk_factors['device'] = device_risk
        
        # Time-based risk
        time_risk = await self._assess_time_risk(
            session.started_at, user_history.get('typical_hours', [])
        )
        risk_factors['time'] = time_risk
        
        # Behavioral risk
        behavioral_risk = await self._assess_behavioral_risk(
            session, user_history.get('behavior_patterns', {})
        )
        risk_factors['behavior'] = behavioral_risk
        
        # Velocity risk (multiple attempts)
        velocity_risk = await self._assess_velocity_risk(
            session.user_id, session.ip_address
        )
        risk_factors['velocity'] = velocity_risk
        
        # Calculate overall risk score
        weights = {
            'location': 0.25,
            'device': 0.25,
            'time': 0.15,
            'behavior': 0.20,
            'velocity': 0.15
        }
        
        overall_risk = sum(
            risk_factors[factor] * weights[factor] 
            for factor in risk_factors
        )
        
        # Determine risk level
        if overall_risk < 0.3:
            risk_level = 'low'
        elif overall_risk < 0.6:
            risk_level = 'medium'
        elif overall_risk < 0.8:
            risk_level = 'high'
        else:
            risk_level = 'critical'
        
        # Determine required factors based on risk
        required_factors = self._determine_required_factors(risk_level, overall_risk)
        recommended_factors = self._determine_recommended_factors(risk_level, risk_factors)
        
        explanation = self._generate_risk_explanation(risk_factors, risk_level)
        
        return RiskAssessment(
            risk_score=overall_risk,
            risk_level=risk_level,
            factors=risk_factors,
            recommended_factors=recommended_factors,
            required_factors=required_factors,
            explanation=explanation
        )
    
    async def _assess_location_risk(self, ip_address: str, 
                                  typical_locations: List[Dict[str, Any]]) -> float:
        """Assess location-based risk"""
        if not self.geoip_reader:
            return 0.0
        
        try:
            response = self.geoip_reader.city(ip_address)
            current_location = {
                'country': response.country.iso_code,
                'city': response.city.name,
                'latitude': float(response.location.latitude or 0),
                'longitude': float(response.location.longitude or 0)
            }
            
            if not typical_locations:
                return 0.5  # Unknown location pattern
            
            # Check if current location matches typical locations
            for location in typical_locations:
                if (location['country'] == current_location['country'] and
                    location['city'] == current_location['city']):
                    return 0.1  # Low risk - known location
                
                # Calculate distance
                distance = self._calculate_distance(
                    current_location['latitude'], current_location['longitude'],
                    location['latitude'], location['longitude']
                )
                
                if distance < 50:  # Within 50km
                    return 0.2
                elif distance < 200:  # Within 200km
                    return 0.4
            
            return 0.8  # High risk - unknown location
        
        except Exception as e:
            logger.error(f"Location risk assessment failed: {e}")
            return 0.5
    
    async def _assess_device_risk(self, device_fingerprint: str, 
                                known_devices: List[str]) -> float:
        """Assess device-based risk"""
        if not device_fingerprint:
            return 0.7  # Unknown device
        
        if device_fingerprint in known_devices:
            return 0.1  # Known device
        
        # Check for similar device fingerprints
        for known_device in known_devices:
            similarity = self._calculate_string_similarity(device_fingerprint, known_device)
            if similarity > 0.8:
                return 0.3  # Similar device
        
        return 0.8  # Unknown device
    
    async def _assess_time_risk(self, current_time: datetime, 
                              typical_hours: List[int]) -> float:
        """Assess time-based risk"""
        if not typical_hours:
            return 0.3  # No pattern established
        
        current_hour = current_time.hour
        
        if current_hour in typical_hours:
            return 0.1  # Typical time
        
        # Check adjacent hours
        for hour in typical_hours:
            if abs(current_hour - hour) <= 1:
                return 0.3  # Close to typical time
        
        return 0.7  # Unusual time
    
    async def _assess_behavioral_risk(self, session: AuthenticationSession, 
                                    behavior_patterns: Dict[str, Any]) -> float:
        """Assess behavioral risk"""
        risk_score = 0.0
        
        # User agent analysis
        if behavior_patterns.get('typical_user_agents'):
            ua_risk = self._analyze_user_agent_risk(
                session.user_agent, behavior_patterns['typical_user_agents']
            )
            risk_score += ua_risk * 0.5
        
        # Login frequency analysis
        if behavior_patterns.get('login_frequency'):
            freq_risk = self._analyze_frequency_risk(behavior_patterns['login_frequency'])
            risk_score += freq_risk * 0.3
        
        # Session duration patterns
        if behavior_patterns.get('session_durations'):
            duration_risk = self._analyze_duration_risk(behavior_patterns['session_durations'])
            risk_score += duration_risk * 0.2
        
        return min(1.0, risk_score)
    
    async def _assess_velocity_risk(self, user_id: str, ip_address: str) -> float:
        """Assess velocity-based risk (multiple attempts)"""
        # This would typically check recent authentication attempts
        # For now, return a placeholder
        return 0.2
    
    def _determine_required_factors(self, risk_level: str, risk_score: float) -> List[str]:
        """Determine required MFA factors based on risk"""
        if risk_level == 'low':
            return ['password']
        elif risk_level == 'medium':
            return ['password', 'sms']
        elif risk_level == 'high':
            return ['password', 'totp', 'sms']
        else:  # critical
            return ['password', 'totp', 'biometric', 'email']
    
    def _determine_recommended_factors(self, risk_level: str, 
                                     risk_factors: Dict[str, float]) -> List[str]:
        """Determine recommended additional factors"""
        recommended = []
        
        if risk_factors.get('location', 0) > 0.6:
            recommended.append('email')
        
        if risk_factors.get('device', 0) > 0.6:
            recommended.append('push')
        
        if risk_factors.get('velocity', 0) > 0.6:
            recommended.append('biometric')
        
        return recommended
    
    def _generate_risk_explanation(self, risk_factors: Dict[str, float], 
                                 risk_level: str) -> str:
        """Generate human-readable risk explanation"""
        explanations = []
        
        if risk_factors.get('location', 0) > 0.6:
            explanations.append("login from unusual location")
        
        if risk_factors.get('device', 0) > 0.6:
            explanations.append("unrecognized device")
        
        if risk_factors.get('time', 0) > 0.6:
            explanations.append("unusual login time")
        
        if risk_factors.get('velocity', 0) > 0.6:
            explanations.append("multiple recent attempts")
        
        if not explanations:
            return f"Authentication risk is {risk_level}"
        
        return f"Authentication risk is {risk_level} due to: {', '.join(explanations)}"
    
    def _calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using Levenshtein distance"""
        if len(str1) == 0 or len(str2) == 0:
            return 0.0
        
        # Simple Levenshtein distance implementation
        matrix = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]
        
        for i in range(len(str1) + 1):
            matrix[i][0] = i
        for j in range(len(str2) + 1):
            matrix[0][j] = j
        
        for i in range(1, len(str1) + 1):
            for j in range(1, len(str2) + 1):
                if str1[i-1] == str2[j-1]:
                    matrix[i][j] = matrix[i-1][j-1]
                else:
                    matrix[i][j] = min(
                        matrix[i-1][j] + 1,      # deletion
                        matrix[i][j-1] + 1,      # insertion
                        matrix[i-1][j-1] + 1     # substitution
                    )
        
        max_len = max(len(str1), len(str2))
        distance = matrix[len(str1)][len(str2)]
        
        return 1 - (distance / max_len)
    
    def _analyze_user_agent_risk(self, current_ua: str, typical_uas: List[str]) -> float:
        """Analyze user agent risk"""
        if current_ua in typical_uas:
            return 0.0
        
        # Parse user agent
        try:
            current_parsed = user_agents.parse(current_ua)
            
            for typical_ua in typical_uas:
                typical_parsed = user_agents.parse(typical_ua)
                
                # Check if same browser family and OS family
                if (current_parsed.browser.family == typical_parsed.browser.family and
                    current_parsed.os.family == typical_parsed.os.family):
                    return 0.2
            
            return 0.8  # Different browser/OS
        
        except Exception:
            return 0.5
    
    def _analyze_frequency_risk(self, login_frequency: Dict[str, Any]) -> float:
        """Analyze login frequency risk"""
        # Simplified frequency analysis
        return 0.2
    
    def _analyze_duration_risk(self, session_durations: List[int]) -> float:
        """Analyze session duration risk"""
        # Simplified duration analysis
        return 0.2

class MultiFactorAuthenticator:
    """
    Enterprise Multi-Factor Authentication Engine
    Comprehensive MFA system with adaptive security
    """
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        """Initialize MFA engine"""
        self.config = config or {}
        self.database_path = self.config.get('database_path', 'mfa.db')
        self.redis_client = None
        self.encryption_key = None
        
        # Initialize providers
        self.sms_provider = None
        self.email_provider = None
        self.push_provider = None
        
        if self.config.get('sms'):
            self.sms_provider = SMSProvider(self.config['sms'])
        if self.config.get('email'):
            self.email_provider = EmailProvider(self.config['email'])
        if self.config.get('push'):
            self.push_provider = PushNotificationProvider(self.config['push'])
        
        # Initialize risk analyzer
        self.risk_analyzer = RiskAnalyzer(self.config.get('risk_analysis', {}))
        
        # Initialize database
        self._initialize_database()
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Initialize Redis
        self._initialize_redis()
        
        # Active sessions and challenges
        self.active_sessions = {}
        self.active_challenges = {}
        
        # Metrics
        self.metrics = {
            'challenges_sent': 0,
            'challenges_verified': 0,
            'challenges_failed': 0,
            'sessions_created': 0,
            'sessions_completed': 0,
            'high_risk_attempts': 0
        }
    
    def _initialize_database(self) -> None:
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # MFA factors table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mfa_factors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    factor_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    factor_type TEXT NOT NULL,
                    identifier TEXT NOT NULL,
                    secret_data BLOB NOT NULL,
                    backup_codes TEXT,
                    is_active INTEGER DEFAULT 1,
                    is_verified INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    last_used TEXT,
                    failure_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            ''')
            
            # MFA sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mfa_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    required_factors TEXT NOT NULL,
                    completed_factors TEXT,
                    risk_score REAL NOT NULL,
                    device_fingerprint TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    location TEXT,
                    started_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    is_complete INTEGER DEFAULT 0
                )
            ''')
            
            # Authentication logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mfa_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    factor_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    risk_score REAL,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TEXT NOT NULL,
                    details TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("MFA database initialized successfully")
        
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _initialize_encryption(self) -> None:
        """Initialize encryption for sensitive data"""
        try:
            key = self.config.get('encryption_key')
            if key:
                self.encryption_key = Fernet(key.encode() if isinstance(key, str) else key)
            else:
                # Generate a new key
                key = Fernet.generate_key()
                self.encryption_key = Fernet(key)
                logger.warning("Generated new encryption key - store this securely!")
            
            logger.info("Encryption initialized successfully")
        
        except Exception as e:
            logger.error(f"Encryption initialization failed: {e}")
            raise
    
    def _initialize_redis(self) -> None:
        """Initialize Redis for session management"""
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            
            logger.info("Redis connection initialized successfully")
        
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
            self.redis_client = None
    
    async def register_factor(self, user_id: str, factor_type: str, 
                            identifier: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register a new MFA factor for a user
        
        Args:
            user_id: User identifier
            factor_type: Type of factor (sms, email, totp, etc.)
            identifier: Factor identifier (phone, email, etc.)
            metadata: Additional metadata
            
        Returns:
            Dictionary with registration results
        """
        try:
            factor_id = self._generate_factor_id()
            
            # Generate secret data based on factor type
            secret_data = self._generate_secret_data(factor_type)
            
            # Generate backup codes
            backup_codes = self._generate_backup_codes() if factor_type != 'backup' else []
            
            # Create MFA factor
            factor = MFAFactor(
                factor_id=factor_id,
                user_id=user_id,
                factor_type=factor_type,
                identifier=identifier,
                secret_data=self.encryption_key.encrypt(secret_data),
                backup_codes=backup_codes,
                metadata=metadata or {}
            )
            
            # Store factor
            await self._store_factor(factor)
            
            # Prepare response
            response = {
                'factor_id': factor_id,
                'factor_type': factor_type,
                'identifier': identifier,
                'backup_codes': backup_codes if factor_type != 'backup' else None,
                'qr_code': None
            }
            
            # Generate QR code for TOTP
            if factor_type == 'totp':
                totp_secret = secret_data.decode('utf-8')
                provisioning_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
                    name=identifier,
                    issuer_name=self.config.get('issuer_name', 'Ainflue')
                )
                
                # Generate QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(provisioning_uri)
                qr.make(fit=True)
                
                # Convert to base64 for web display
                import io
                from PIL import Image
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                qr_code_data = base64.b64encode(buffer.getvalue()).decode()
                
                response['qr_code'] = f"data:image/png;base64,{qr_code_data}"
                response['secret'] = totp_secret  # For manual entry
            
            self.metrics['challenges_sent'] += 1
            
            return response
        
        except Exception as e:
            logger.error(f"Factor registration failed: {e}")
            raise
    
    async def start_authentication(self, user_id: str, device_fingerprint: str = "",
                                 ip_address: str = "", user_agent: str = "",
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Start multi-factor authentication session
        
        Args:
            user_id: User identifier
            device_fingerprint: Device fingerprint
            ip_address: Client IP address
            user_agent: Client user agent
            context: Additional context
            
        Returns:
            Dictionary with session information
        """
        try:
            session_id = self._generate_session_id()
            
            # Get user's registered factors
            user_factors = await self._get_user_factors(user_id)
            if not user_factors:
                raise ValueError("No MFA factors registered for user")
            
            # Create authentication session
            session = AuthenticationSession(
                session_id=session_id,
                user_id=user_id,
                required_factors=[],
                device_fingerprint=device_fingerprint,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Assess risk and determine required factors
            user_history = await self._get_user_history(user_id)
            risk_assessment = await self.risk_analyzer.assess_risk(session, user_history)
            
            session.risk_score = risk_assessment.risk_score
            session.required_factors = risk_assessment.required_factors
            
            # Store session
            await self._store_session(session)
            self.active_sessions[session_id] = session
            
            # Log session start
            await self._log_authentication(
                user_id, 'session', 'start', True, risk_assessment.risk_score,
                ip_address, user_agent, {'risk_level': risk_assessment.risk_level}
            )
            
            self.metrics['sessions_created'] += 1
            if risk_assessment.risk_level in ['high', 'critical']:
                self.metrics['high_risk_attempts'] += 1
            
            return {
                'session_id': session_id,
                'required_factors': session.required_factors,
                'risk_assessment': {
                    'risk_score': risk_assessment.risk_score,
                    'risk_level': risk_assessment.risk_level,
                    'explanation': risk_assessment.explanation
                },
                'available_factors': [f.factor_type for f in user_factors if f.is_active]
            }
        
        except Exception as e:
            logger.error(f"Authentication start failed: {e}")
            raise
    
    async def send_challenge(self, session_id: str, factor_type: str) -> Dict[str, Any]:
        """
        Send MFA challenge to user
        
        Args:
            session_id: Authentication session ID
            factor_type: Type of factor to challenge
            
        Returns:
            Dictionary with challenge information
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError("Invalid or expired session")
            
            if factor_type in session.completed_factors:
                raise ValueError("Factor already completed")
            
            # Get user factor
            factor = await self._get_user_factor(session.user_id, factor_type)
            if not factor or not factor.is_active:
                raise ValueError("Factor not available")
            
            challenge_id = self._generate_challenge_id()
            
            # Generate challenge based on factor type
            if factor_type == 'sms':
                code = self._generate_code()
                message = f"Your Ainflue verification code is: {code}"
                
                if self.sms_provider:
                    success = await self.sms_provider.send_sms(factor.identifier, message)
                    if not success:
                        raise ValueError("Failed to send SMS")
                else:
                    raise ValueError("SMS provider not configured")
                
                challenge = MFAChallenge(
                    challenge_id=challenge_id,
                    user_id=session.user_id,
                    factor_type=factor_type,
                    challenge_data=code,
                    expires_at=datetime.now() + timedelta(minutes=5)
                )
            
            elif factor_type == 'email':
                code = self._generate_code()
                subject = "Ainflue Security Code"
                body = f"Your verification code is: {code}\n\nThis code will expire in 5 minutes."
                
                if self.email_provider:
                    success = await self.email_provider.send_email(
                        factor.identifier, subject, body
                    )
                    if not success:
                        raise ValueError("Failed to send email")
                else:
                    raise ValueError("Email provider not configured")
                
                challenge = MFAChallenge(
                    challenge_id=challenge_id,
                    user_id=session.user_id,
                    factor_type=factor_type,
                    challenge_data=code,
                    expires_at=datetime.now() + timedelta(minutes=5)
                )
            
            elif factor_type == 'push':
                if self.push_provider:
                    success = await self.push_provider.send_push_notification(
                        factor.identifier,
                        "Ainflue Login Verification",
                        "Tap to approve your login attempt",
                        {'challenge_id': challenge_id, 'action': 'approve_login'}
                    )
                    if not success:
                        raise ValueError("Failed to send push notification")
                else:
                    raise ValueError("Push provider not configured")
                
                challenge = MFAChallenge(
                    challenge_id=challenge_id,
                    user_id=session.user_id,
                    factor_type=factor_type,
                    challenge_data="push_sent",
                    expires_at=datetime.now() + timedelta(minutes=2)
                )
            
            elif factor_type == 'totp':
                # TOTP doesn't require sending a challenge
                challenge = MFAChallenge(
                    challenge_id=challenge_id,
                    user_id=session.user_id,
                    factor_type=factor_type,
                    challenge_data="totp_ready",
                    expires_at=datetime.now() + timedelta(minutes=5)
                )
            
            else:
                raise ValueError(f"Unsupported factor type: {factor_type}")
            
            # Store challenge
            self.active_challenges[challenge_id] = challenge
            
            # Cache in Redis if available
            if self.redis_client:
                self.redis_client.setex(
                    f"mfa_challenge:{challenge_id}",
                    300,  # 5 minutes
                    json.dumps({
                        'user_id': session.user_id,
                        'factor_type': factor_type,
                        'challenge_data': challenge.challenge_data,
                        'expires_at': challenge.expires_at.isoformat()
                    })
                )
            
            self.metrics['challenges_sent'] += 1
            
            return {
                'challenge_id': challenge_id,
                'factor_type': factor_type,
                'expires_at': challenge.expires_at.isoformat(),
                'message': f"Challenge sent via {factor_type}"
            }
        
        except Exception as e:
            logger.error(f"Challenge sending failed: {e}")
            raise
    
    async def verify_challenge(self, challenge_id: str, response: str) -> Dict[str, Any]:
        """
        Verify MFA challenge response
        
        Args:
            challenge_id: Challenge identifier
            response: User's response to challenge
            
        Returns:
            Dictionary with verification results
        """
        try:
            challenge = self.active_challenges.get(challenge_id)
            if not challenge:
                # Try to load from Redis
                if self.redis_client:
                    cached_data = self.redis_client.get(f"mfa_challenge:{challenge_id}")
                    if cached_data:
                        data = json.loads(cached_data)
                        challenge = MFAChallenge(
                            challenge_id=challenge_id,
                            user_id=data['user_id'],
                            factor_type=data['factor_type'],
                            challenge_data=data['challenge_data'],
                            expires_at=datetime.fromisoformat(data['expires_at'])
                        )
                
                if not challenge:
                    raise ValueError("Invalid or expired challenge")
            
            # Check if challenge has expired
            if datetime.now() > challenge.expires_at:
                self.active_challenges.pop(challenge_id, None)
                if self.redis_client:
                    self.redis_client.delete(f"mfa_challenge:{challenge_id}")
                raise ValueError("Challenge has expired")
            
            # Check attempt limit
            challenge.attempts += 1
            if challenge.attempts > challenge.max_attempts:
                self.active_challenges.pop(challenge_id, None)
                if self.redis_client:
                    self.redis_client.delete(f"mfa_challenge:{challenge_id}")
                raise ValueError("Maximum attempts exceeded")
            
            # Verify response based on factor type
            is_valid = False
            
            if challenge.factor_type in ['sms', 'email']:
                is_valid = response.strip() == challenge.challenge_data
            
            elif challenge.factor_type == 'totp':
                # Get user factor for TOTP secret
                factor = await self._get_user_factor(challenge.user_id, 'totp')
                if factor:
                    secret_data = self.encryption_key.decrypt(factor.secret_data)
                    totp_secret = secret_data.decode('utf-8')
                    totp = pyotp.TOTP(totp_secret)
                    is_valid = totp.verify(response.strip())
            
            elif challenge.factor_type == 'push':
                # For push notifications, response should be 'approved'
                is_valid = response.strip().lower() == 'approved'
            
            elif challenge.factor_type == 'backup':
                # Verify backup code
                factor = await self._get_user_factor(challenge.user_id, 'backup')
                if factor and response.strip() in factor.backup_codes:
                    # Remove used backup code
                    factor.backup_codes.remove(response.strip())
                    await self._update_factor(factor)
                    is_valid = True
            
            if is_valid:
                challenge.is_verified = True
                
                # Update session
                session = None
                for sess in self.active_sessions.values():
                    if sess.user_id == challenge.user_id:
                        session = sess
                        break
                
                if session:
                    if challenge.factor_type not in session.completed_factors:
                        session.completed_factors.append(challenge.factor_type)
                    
                    # Check if all required factors are completed
                    if all(factor in session.completed_factors for factor in session.required_factors):
                        session.is_complete = True
                        self.metrics['sessions_completed'] += 1
                
                # Update factor usage
                factor = await self._get_user_factor(challenge.user_id, challenge.factor_type)
                if factor:
                    factor.last_used = datetime.now()
                    factor.failure_count = 0
                    await self._update_factor(factor)
                
                # Clean up challenge
                self.active_challenges.pop(challenge_id, None)
                if self.redis_client:
                    self.redis_client.delete(f"mfa_challenge:{challenge_id}")
                
                # Log successful verification
                await self._log_authentication(
                    challenge.user_id, challenge.factor_type, 'verify', True,
                    session.risk_score if session else 0.0,
                    session.ip_address if session else "",
                    session.user_agent if session else "",
                    {'challenge_id': challenge_id}
                )
                
                self.metrics['challenges_verified'] += 1
                
                return {
                    'verified': True,
                    'factor_type': challenge.factor_type,
                    'session_complete': session.is_complete if session else False,
                    'message': 'Challenge verified successfully'
                }
            
            else:
                # Update factor failure count
                factor = await self._get_user_factor(challenge.user_id, challenge.factor_type)
                if factor:
                    factor.failure_count += 1
                    await self._update_factor(factor)
                
                # Log failed verification
                await self._log_authentication(
                    challenge.user_id, challenge.factor_type, 'verify', False,
                    0.0, "", "", {'challenge_id': challenge_id}
                )
                
                self.metrics['challenges_failed'] += 1
                
                return {
                    'verified': False,
                    'factor_type': challenge.factor_type,
                    'attempts_remaining': challenge.max_attempts - challenge.attempts,
                    'message': 'Invalid response'
                }
        
        except Exception as e:
            logger.error(f"Challenge verification failed: {e}")
            raise
    
    # Helper methods for data generation and management
    
    def _generate_factor_id(self) -> str:
        """Generate unique factor ID"""
        return f"factor_{int(time.time())}_{random.randint(1000, 9999)}"
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{int(time.time())}_{random.randint(10000, 99999)}"
    
    def _generate_challenge_id(self) -> str:
        """Generate unique challenge ID"""
        return f"challenge_{int(time.time())}_{random.randint(10000, 99999)}"
    
    def _generate_secret_data(self, factor_type: str) -> bytes:
        """Generate secret data for factor type"""
        if factor_type == 'totp':
            return pyotp.random_base32().encode('utf-8')
        else:
            return os.urandom(32)
    
    def _generate_code(self, length: int = 6) -> str:
        """Generate random numeric code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def _generate_backup_codes(self, count: int = 10, length: int = 8) -> List[str]:
        """Generate backup codes"""
        codes = []
        for _ in range(count):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            codes.append(code)
        return codes
    
    # Database operations
    
    async def _store_factor(self, factor -> None: MFAFactor) -> None:
        """Store MFA factor in database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO mfa_factors
                (factor_id, user_id, factor_type, identifier, secret_data, backup_codes,
                 is_active, is_verified, created_at, last_used, failure_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                factor.factor_id, factor.user_id, factor.factor_type, factor.identifier,
                factor.secret_data, json.dumps(factor.backup_codes),
                1 if factor.is_active else 0, 1 if factor.is_verified else 0,
                factor.created_at.isoformat(),
                factor.last_used.isoformat() if factor.last_used else None,
                factor.failure_count, json.dumps(factor.metadata)
            ))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"Factor storage failed: {e}")
            raise
    
    async def _get_user_factors(self, user_id: str) -> List[MFAFactor]:
        """Get all MFA factors for a user"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT factor_id, factor_type, identifier, secret_data, backup_codes,
                       is_active, is_verified, created_at, last_used, failure_count, metadata
                FROM mfa_factors
                WHERE user_id = ?
            ''', (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            factors = []
            for row in rows:
                factors.append(MFAFactor(
                    factor_id=row[0],
                    user_id=user_id,
                    factor_type=row[1],
                    identifier=row[2],
                    secret_data=row[3],
                    backup_codes=json.loads(row[4]) if row[4] else [],
                    is_active=bool(row[5]),
                    is_verified=bool(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    last_used=datetime.fromisoformat(row[8]) if row[8] else None,
                    failure_count=row[9],
                    metadata=json.loads(row[10]) if row[10] else {}
                ))
            
            return factors
        
        except Exception as e:
            logger.error(f"Factor retrieval failed: {e}")
            return []
    
    async def _get_user_factor(self, user_id: str, factor_type: str) -> Optional[MFAFactor]:
        """Get specific MFA factor for a user"""
        factors = await self._get_user_factors(user_id)
        for factor in factors:
            if factor.factor_type == factor_type and factor.is_active:
                return factor
        return None
    
    async def _update_factor(self, factor -> None: MFAFactor) -> None:
        """Update MFA factor in database"""
        await self._store_factor(factor)
    
    async def _store_session(self, session -> None: AuthenticationSession) -> None:
        """Store authentication session"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO mfa_sessions
                (session_id, user_id, required_factors, completed_factors, risk_score,
                 device_fingerprint, ip_address, user_agent, location, started_at,
                 expires_at, is_complete)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id, session.user_id, 
                json.dumps(session.required_factors),
                json.dumps(session.completed_factors),
                session.risk_score, session.device_fingerprint, session.ip_address,
                session.user_agent, json.dumps(session.location),
                session.started_at.isoformat(), session.expires_at.isoformat(),
                1 if session.is_complete else 0
            ))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"Session storage failed: {e}")
            raise
    
    async def _get_user_history(self, user_id: str) -> Dict[str, Any]:
        """Get user authentication history for risk assessment"""
        # This would typically analyze historical data
        # For now, return empty history
        return {
            'typical_locations': [],
            'known_devices': [],
            'typical_hours': list(range(8, 18)),  # Business hours
            'behavior_patterns': {}
        }
    
    async def _log_authentication(self, user_id -> None: str, factor_type -> None: str, action -> None: str,
                                success -> None: bool, risk_score -> None: float, ip_address -> None: str,
                                user_agent -> None: str, details -> None: Dict[str, Any]) -> None:
        """Log authentication event"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO mfa_logs
                (user_id, factor_type, action, success, risk_score, ip_address,
                 user_agent, timestamp, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, factor_type, action, 1 if success else 0, risk_score,
                ip_address, user_agent, datetime.now().isoformat(),
                json.dumps(details)
            ))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"Authentication logging failed: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get MFA system metrics"""
        return self.metrics.copy()

# CLI interface for testing
async def main() -> None:
    """Main function for command-line testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Factor Authentication Engine')
    parser.add_argument('action', choices=['register', 'start', 'challenge', 'verify'])
    parser.add_argument('--user-id', required=True, help='User ID')
    parser.add_argument('--factor-type', help='Factor type')
    parser.add_argument('--identifier', help='Factor identifier')
    parser.add_argument('--session-id', help='Session ID')
    parser.add_argument('--challenge-id', help='Challenge ID')
    parser.add_argument('--response', help='Challenge response')
    parser.add_argument('--config', help='Configuration file')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Initialize MFA engine
    mfa = MultiFactorAuthenticator(config)
    
    try:
        if args.action == 'register':
            if not args.factor_type or not args.identifier:
                print("Error: --factor-type and --identifier required")
                return
            
            result = await mfa.register_factor(args.user_id, args.factor_type, args.identifier)
            print(json.dumps(result, indent=2))
        
        elif args.action == 'start':
            result = await mfa.start_authentication(args.user_id)
            print(json.dumps(result, indent=2))
        
        elif args.action == 'challenge':
            if not args.session_id or not args.factor_type:
                print("Error: --session-id and --factor-type required")
                return
            
            result = await mfa.send_challenge(args.session_id, args.factor_type)
            print(json.dumps(result, indent=2))
        
        elif args.action == 'verify':
            if not args.challenge_id or not args.response:
                print("Error: --challenge-id and --response required")
                return
            
            result = await mfa.verify_challenge(args.challenge_id, args.response)
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())