#!/usr/bin/env python3
"""
🔒 Password Policy Engine - Intelligent Security Management
============================================================

Enterprise password policy engine with ML-powered pattern detection,
adaptive strength requirements, and automated policy enforcement.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + ML + Backend + DevOps
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import hashlib
import re
import secrets
import string
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import logging
from pathlib import Path

# Security imports
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt

# ML imports for pattern detection
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split


class PasswordStrengthLevel(Enum):
    """Password strength classification levels"""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"
    ENTERPRISE = "enterprise"


class PolicyViolationType(Enum):
    """Types of policy violations"""
    LENGTH_TOO_SHORT = "length_too_short"
    MISSING_UPPERCASE = "missing_uppercase"
    MISSING_LOWERCASE = "missing_lowercase"
    MISSING_DIGITS = "missing_digits"
    MISSING_SPECIAL = "missing_special"
    COMMON_PATTERN = "common_pattern"
    DICTIONARY_WORD = "dictionary_word"
    REPEATED_CHARACTERS = "repeated_characters"
    SEQUENTIAL_CHARACTERS = "sequential_characters"
    PERSONAL_INFO = "personal_info"
    REUSED_PASSWORD = "reused_password"
    WEAK_ENTROPY = "weak_entropy"


@dataclass
class PasswordStrengthResult:
    """Password strength analysis result"""
    strength_level: PasswordStrengthLevel
    score: float  # 0.0 to 1.0
    violations: List[PolicyViolationType]
    suggestions: List[str]
    entropy: float
    estimated_crack_time: str
    is_compromised: bool


@dataclass
class PasswordPolicy:
    """Dynamic password policy configuration"""
    min_length: int = 12
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    min_special_chars: int = 2
    max_repeated_chars: int = 2
    min_entropy: float = 40.0
    rotation_days: int = 90
    history_count: int = 12
    check_compromised: bool = True
    allowed_special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"


class PasswordPolicyEngine:
    """
    🔒 Enterprise Password Policy Engine
    
    Intelligent password policy management with ML-powered analysis,
    adaptive strength requirements, and comprehensive security features.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize password policy engine"""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "security/config/password_policies.json"
        
        # Load configuration
        self.policies = self._load_policies()
        self.common_passwords = self._load_common_passwords()
        self.compromised_passwords = set()  # Could be loaded from breach databases
        
        # ML components for pattern detection
        self.pattern_detector = IsolationForest(contamination=0.1, random_state=42)
        self.vectorizer = TfidfVectorizer(
            analyzer='char', 
            ngram_range=(2, 4), 
            max_features=1000
        )
        
        # Password history storage
        self.password_history: Dict[str, List[str]] = {}
        
        # Initialize ML models
        self._initialize_ml_models()
    
    async def validate_password_strength(
        self, 
        password: str, 
        user_id: str,
        user_info: Optional[Dict[str, Any]] = None,
        policy_name: str = "default"
    ) -> PasswordStrengthResult:
        """
        Validate password strength against policy and ML analysis
        
        Args:
            password: Password to validate
            user_id: User identifier
            user_info: User personal information for context
            policy_name: Policy configuration to use
            
        Returns:
            PasswordStrengthResult with comprehensive analysis
        """
        try:
            policy = self.policies.get(policy_name, self.policies["default"])
            violations = []
            suggestions = []
            
            # Basic policy checks
            violations.extend(await self._check_basic_policy(password, policy))
            
            # Advanced pattern analysis
            pattern_violations = await self._analyze_patterns(password, user_info)
            violations.extend(pattern_violations)
            
            # Entropy calculation
            entropy = self._calculate_entropy(password)
            if entropy < policy.min_entropy:
                violations.append(PolicyViolationType.WEAK_ENTROPY)
                suggestions.append(f"Increase complexity for entropy > {policy.min_entropy}")
            
            # Check against compromised passwords
            is_compromised = await self._check_compromised(password)
            if is_compromised:
                violations.append(PolicyViolationType.REUSED_PASSWORD)
                suggestions.append("This password has been found in data breaches")
            
            # Check password history
            if await self._check_password_history(user_id, password):
                violations.append(PolicyViolationType.REUSED_PASSWORD)
                suggestions.append("Cannot reuse recent passwords")
            
            # Calculate strength score
            strength_level, score = self._calculate_strength_score(
                password, violations, entropy
            )
            
            # Generate suggestions
            if not suggestions:
                suggestions = self._generate_suggestions(violations, policy)
            
            # Estimate crack time
            crack_time = self._estimate_crack_time(password, entropy)
            
            return PasswordStrengthResult(
                strength_level=strength_level,
                score=score,
                violations=violations,
                suggestions=suggestions,
                entropy=entropy,
                estimated_crack_time=crack_time,
                is_compromised=is_compromised
            )
            
        except Exception as e:
            self.logger.error(f"Password validation error: {e}")
            raise
    
    async def generate_secure_password(
        self, 
        policy_name: str = "default",
        length: Optional[int] = None,
        include_words: bool = False
    ) -> str:
        """
        Generate cryptographically secure password
        
        Args:
            policy_name: Policy to follow
            length: Custom length (overrides policy)
            include_words: Include pronounceable words
            
        Returns:
            Generated secure password
        """
        try:
            policy = self.policies.get(policy_name, self.policies["default"])
            target_length = length or policy.min_length
            
            if include_words:
                return await self._generate_passphrase(target_length, policy)
            else:
                return await self._generate_random_password(target_length, policy)
                
        except Exception as e:
            self.logger.error(f"Password generation error: {e}")
            raise
    
    async def detect_weak_patterns(
        self, 
        password: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect weak patterns using ML analysis
        
        Args:
            password: Password to analyze
            context: Additional context for analysis
            
        Returns:
            List of detected weak patterns
        """
        try:
            patterns = []
            
            # Sequential patterns
            if self._has_sequential_chars(password):
                patterns.append({
                    "type": "sequential",
                    "description": "Contains sequential characters",
                    "risk_level": "medium",
                    "examples": ["123", "abc", "qwerty"]
                })
            
            # Repeated patterns
            repeated = self._find_repeated_patterns(password)
            if repeated:
                patterns.append({
                    "type": "repetition",
                    "description": f"Contains repeated patterns: {repeated}",
                    "risk_level": "high",
                    "patterns": repeated
                })
            
            # Dictionary words
            dict_words = await self._find_dictionary_words(password)
            if dict_words:
                patterns.append({
                    "type": "dictionary",
                    "description": f"Contains dictionary words: {dict_words}",
                    "risk_level": "high",
                    "words": dict_words
                })
            
            # Personal information patterns
            if context:
                personal_patterns = self._detect_personal_patterns(password, context)
                if personal_patterns:
                    patterns.append({
                        "type": "personal",
                        "description": "Contains personal information",
                        "risk_level": "critical",
                        "patterns": personal_patterns
                    })
            
            # ML-based anomaly detection
            ml_patterns = await self._ml_pattern_detection(password)
            patterns.extend(ml_patterns)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Pattern detection error: {e}")
            return []
    
    async def enforce_rotation_policy(
        self, 
        user_id: str,
        policy_name: str = "default"
    ) -> Dict[str, Any]:
        """
        Enforce password rotation policy
        
        Args:
            user_id: User identifier
            policy_name: Policy to enforce
            
        Returns:
            Rotation enforcement result
        """
        try:
            policy = self.policies.get(policy_name, self.policies["default"])
            
            # Get user's last password change
            last_change = await self._get_last_password_change(user_id)
            if not last_change:
                return {
                    "action_required": False,
                    "message": "No password history found"
                }
            
            # Calculate days since last change
            days_since_change = (datetime.utcnow() - last_change).days
            days_until_expiry = policy.rotation_days - days_since_change
            
            # Determine action required
            if days_until_expiry <= 0:
                action = "force_change"
                urgency = "critical"
                message = "Password has expired and must be changed immediately"
            elif days_until_expiry <= 7:
                action = "warn_expiry"
                urgency = "high"
                message = f"Password expires in {days_until_expiry} days"
            elif days_until_expiry <= 14:
                action = "notify_upcoming"
                urgency = "medium"
                message = f"Password expires in {days_until_expiry} days"
            else:
                action = "no_action"
                urgency = "low"
                message = f"Password expires in {days_until_expiry} days"
            
            return {
                "action_required": action != "no_action",
                "action": action,
                "urgency": urgency,
                "message": message,
                "days_until_expiry": days_until_expiry,
                "last_change": last_change.isoformat(),
                "policy": {
                    "rotation_days": policy.rotation_days,
                    "history_count": policy.history_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"Rotation policy enforcement error: {e}")
            raise
    
    # Private methods
    
    def _load_policies(self) -> Dict[str, PasswordPolicy]:
        """Load password policies from configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return {
                    name: PasswordPolicy(**policy_config)
                    for name, policy_config in config.items()
                }
            else:
                # Default policies
                return {
                    "default": PasswordPolicy(),
                    "admin": PasswordPolicy(
                        min_length=16,
                        min_entropy=50.0,
                        rotation_days=60
                    ),
                    "creator": PasswordPolicy(
                        min_length=14,
                        min_entropy=45.0,
                        rotation_days=90,
                        history_count=15
                    )
                }
        except Exception as e:
            self.logger.error(f"Policy loading error: {e}")
            return {"default": PasswordPolicy()}
    
    def _load_common_passwords(self) -> set:
        """Load common passwords list"""
        common_passwords = {
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "1234567890", "abc123",
            "password1", "123456789", "welcome123", "login", "guest"
        }
        # In production, load from comprehensive breach databases
        return common_passwords
    
    def _initialize_ml_models(self):
        """Initialize ML models for pattern detection"""
        try:
            # Generate training data for anomaly detection
            normal_patterns = [
                "ComplexPass123!", "SecureWord@456", "MyStrong#789",
                "Enterprise$2024", "SafeChoice&999", "PowerUser!2025"
            ]
            weak_patterns = [
                "password", "123456", "qwerty", "admin", "welcome",
                "letmein", "monkey", "abc123", "password123"
            ]
            
            # Combine and vectorize
            all_patterns = normal_patterns + weak_patterns
            if all_patterns:
                X = self.vectorizer.fit_transform(all_patterns)
                
                # Train anomaly detector on normal patterns
                normal_X = X[:len(normal_patterns)]
                self.pattern_detector.fit(normal_X.toarray())
                
        except Exception as e:
            self.logger.warning(f"ML model initialization failed: {e}")
    
    async def _check_basic_policy(
        self, 
        password: str, 
        policy: PasswordPolicy
    ) -> List[PolicyViolationType]:
        """Check basic policy requirements"""
        violations = []
        
        if len(password) < policy.min_length:
            violations.append(PolicyViolationType.LENGTH_TOO_SHORT)
        
        if policy.require_uppercase and not any(c.isupper() for c in password):
            violations.append(PolicyViolationType.MISSING_UPPERCASE)
        
        if policy.require_lowercase and not any(c.islower() for c in password):
            violations.append(PolicyViolationType.MISSING_LOWERCASE)
        
        if policy.require_digits and not any(c.isdigit() for c in password):
            violations.append(PolicyViolationType.MISSING_DIGITS)
        
        if policy.require_special:
            special_count = sum(1 for c in password if c in policy.allowed_special_chars)
            if special_count < policy.min_special_chars:
                violations.append(PolicyViolationType.MISSING_SPECIAL)
        
        # Check for repeated characters
        if self._has_excessive_repetition(password, policy.max_repeated_chars):
            violations.append(PolicyViolationType.REPEATED_CHARACTERS)
        
        return violations
    
    async def _analyze_patterns(
        self, 
        password: str, 
        user_info: Optional[Dict[str, Any]]
    ) -> List[PolicyViolationType]:
        """Analyze password for weak patterns"""
        violations = []
        
        # Check common passwords
        if password.lower() in self.common_passwords:
            violations.append(PolicyViolationType.COMMON_PATTERN)
        
        # Check sequential characters
        if self._has_sequential_chars(password):
            violations.append(PolicyViolationType.SEQUENTIAL_CHARACTERS)
        
        # Check personal information
        if user_info and self._contains_personal_info(password, user_info):
            violations.append(PolicyViolationType.PERSONAL_INFO)
        
        # Check dictionary words
        if await self._contains_dictionary_words(password):
            violations.append(PolicyViolationType.DICTIONARY_WORD)
        
        return violations
    
    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits"""
        charset_size = 0
        
        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            charset_size += 23
        
        if charset_size == 0:
            return 0.0
        
        # Entropy = log2(charset_size^length)
        import math
        return len(password) * math.log2(charset_size)
    
    async def _check_compromised(self, password: str) -> bool:
        """Check if password is in breach databases"""
        # Hash password for privacy
        password_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        
        # In production, check against HaveIBeenPwned API or local breach database
        # For now, check against our local compromised set
        return password.lower() in self.compromised_passwords
    
    async def _check_password_history(self, user_id: str, password: str) -> bool:
        """Check if password was used recently"""
        history = self.password_history.get(user_id, [])
        
        # Hash password for comparison
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        # Check against history
        for old_hash in history:
            if bcrypt.checkpw(password.encode(), old_hash.encode()):
                return True
        
        return False
    
    def _calculate_strength_score(
        self, 
        password: str, 
        violations: List[PolicyViolationType],
        entropy: float
    ) -> Tuple[PasswordStrengthLevel, float]:
        """Calculate overall password strength"""
        base_score = min(entropy / 60.0, 1.0)  # Normalize entropy to 0-1
        
        # Penalty for violations
        violation_penalty = len(violations) * 0.1
        score = max(0.0, base_score - violation_penalty)
        
        # Determine strength level
        if score >= 0.9:
            level = PasswordStrengthLevel.ENTERPRISE
        elif score >= 0.8:
            level = PasswordStrengthLevel.VERY_STRONG
        elif score >= 0.6:
            level = PasswordStrengthLevel.STRONG
        elif score >= 0.4:
            level = PasswordStrengthLevel.MEDIUM
        elif score >= 0.2:
            level = PasswordStrengthLevel.WEAK
        else:
            level = PasswordStrengthLevel.VERY_WEAK
        
        return level, score
    
    def _generate_suggestions(
        self, 
        violations: List[PolicyViolationType],
        policy: PasswordPolicy
    ) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        for violation in violations:
            if violation == PolicyViolationType.LENGTH_TOO_SHORT:
                suggestions.append(f"Use at least {policy.min_length} characters")
            elif violation == PolicyViolationType.MISSING_UPPERCASE:
                suggestions.append("Include uppercase letters (A-Z)")
            elif violation == PolicyViolationType.MISSING_LOWERCASE:
                suggestions.append("Include lowercase letters (a-z)")
            elif violation == PolicyViolationType.MISSING_DIGITS:
                suggestions.append("Include numbers (0-9)")
            elif violation == PolicyViolationType.MISSING_SPECIAL:
                suggestions.append(f"Include at least {policy.min_special_chars} special characters")
            elif violation == PolicyViolationType.COMMON_PATTERN:
                suggestions.append("Avoid common passwords and patterns")
            elif violation == PolicyViolationType.REPEATED_CHARACTERS:
                suggestions.append("Avoid excessive character repetition")
            elif violation == PolicyViolationType.SEQUENTIAL_CHARACTERS:
                suggestions.append("Avoid sequential characters (123, abc, qwerty)")
            elif violation == PolicyViolationType.PERSONAL_INFO:
                suggestions.append("Don't use personal information")
            elif violation == PolicyViolationType.WEAK_ENTROPY:
                suggestions.append("Increase password complexity and randomness")
        
        if not suggestions:
            suggestions.append("Password meets all requirements")
        
        return suggestions
    
    def _estimate_crack_time(self, password: str, entropy: float) -> str:
        """Estimate time to crack password"""
        # Assuming 10^9 guesses per second (modern GPU)
        guesses_per_second = 10**9
        total_combinations = 2**(entropy - 1)  # Average case
        seconds = total_combinations / guesses_per_second
        
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} hours"
        elif seconds < 31536000:
            return f"{seconds/86400:.1f} days"
        else:
            years = seconds / 31536000
            if years < 1000:
                return f"{years:.1f} years"
            elif years < 1000000:
                return f"{years/1000:.1f} thousand years"
            elif years < 1000000000:
                return f"{years/1000000:.1f} million years"
            else:
                return "billions of years"
    
    async def _generate_passphrase(
        self, 
        length: int, 
        policy: PasswordPolicy
    ) -> str:
        """Generate secure passphrase with words"""
        word_list = [
            "Secure", "Strong", "Complex", "Advanced", "Premium",
            "Elite", "Professional", "Enterprise", "Ultimate", "Superior"
        ]
        
        passphrase = ""
        while len(passphrase) < length:
            word = secrets.choice(word_list)
            number = secrets.randbelow(999)
            special = secrets.choice(policy.allowed_special_chars)
            
            segment = f"{word}{number}{special}"
            if len(passphrase + segment) <= length:
                passphrase += segment
            else:
                break
        
        # Ensure minimum length
        while len(passphrase) < length:
            passphrase += secrets.choice(policy.allowed_special_chars)
        
        return passphrase[:length]
    
    async def _generate_random_password(
        self, 
        length: int, 
        policy: PasswordPolicy
    ) -> str:
        """Generate cryptographically secure random password"""
        chars = ""
        if policy.require_lowercase:
            chars += string.ascii_lowercase
        if policy.require_uppercase:
            chars += string.ascii_uppercase
        if policy.require_digits:
            chars += string.digits
        if policy.require_special:
            chars += policy.allowed_special_chars
        
        # Ensure at least one of each required type
        password = []
        if policy.require_lowercase:
            password.append(secrets.choice(string.ascii_lowercase))
        if policy.require_uppercase:
            password.append(secrets.choice(string.ascii_uppercase))
        if policy.require_digits:
            password.append(secrets.choice(string.digits))
        if policy.require_special:
            for _ in range(policy.min_special_chars):
                password.append(secrets.choice(policy.allowed_special_chars))
        
        # Fill remaining length
        remaining_length = length - len(password)
        for _ in range(remaining_length):
            password.append(secrets.choice(chars))
        
        # Shuffle password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters"""
        sequences = [
            "abcdefghijklmnopqrstuvwxyz",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 
            "0123456789",
            "qwertyuiopasdfghjklzxcvbnm"
        ]
        
        for seq in sequences:
            for i in range(len(seq) - 2):
                if seq[i:i+3] in password.lower():
                    return True
        
        return False
    
    def _has_excessive_repetition(self, password: str, max_repeated: int) -> bool:
        """Check for excessive character repetition"""
        count = 1
        for i in range(1, len(password)):
            if password[i] == password[i-1]:
                count += 1
                if count > max_repeated:
                    return True
            else:
                count = 1
        return False
    
    def _find_repeated_patterns(self, password: str) -> List[str]:
        """Find repeated patterns in password"""
        patterns = []
        for length in range(2, len(password) // 2 + 1):
            for i in range(len(password) - length + 1):
                pattern = password[i:i+length]
                if password.count(pattern) > 1:
                    patterns.append(pattern)
        return list(set(patterns))
    
    async def _find_dictionary_words(self, password: str) -> List[str]:
        """Find dictionary words in password"""
        # Simple dictionary check
        common_words = {
            "password", "admin", "user", "login", "welcome",
            "hello", "world", "test", "demo", "sample"
        }
        
        found_words = []
        password_lower = password.lower()
        
        for word in common_words:
            if word in password_lower:
                found_words.append(word)
        
        return found_words
    
    def _detect_personal_patterns(
        self, 
        password: str, 
        user_info: Dict[str, Any]
    ) -> List[str]:
        """Detect personal information in password"""
        patterns = []
        password_lower = password.lower()
        
        # Check common personal fields
        for field in ["name", "email", "username", "birthdate", "phone"]:
            if field in user_info:
                value = str(user_info[field]).lower()
                if value in password_lower:
                    patterns.append(f"{field}: {value}")
        
        return patterns
    
    def _contains_personal_info(
        self, 
        password: str, 
        user_info: Dict[str, Any]
    ) -> bool:
        """Check if password contains personal information"""
        return len(self._detect_personal_patterns(password, user_info)) > 0
    
    async def _contains_dictionary_words(self, password: str) -> bool:
        """Check if password contains dictionary words"""
        words = await self._find_dictionary_words(password)
        return len(words) > 0
    
    async def _ml_pattern_detection(self, password: str) -> List[Dict[str, Any]]:
        """ML-based pattern detection"""
        patterns = []
        
        try:
            # Vectorize password
            X = self.vectorizer.transform([password])
            
            # Predict anomaly
            anomaly_score = self.pattern_detector.decision_function(X.toarray())[0]
            is_anomaly = self.pattern_detector.predict(X.toarray())[0] == -1
            
            if is_anomaly:
                patterns.append({
                    "type": "ml_anomaly",
                    "description": "ML model detected unusual pattern",
                    "risk_level": "medium",
                    "confidence": abs(anomaly_score)
                })
        
        except Exception as e:
            self.logger.warning(f"ML pattern detection failed: {e}")
        
        return patterns
    
    async def _get_last_password_change(self, user_id: str) -> Optional[datetime]:
        """Get last password change date for user"""
        # In production, query from user database
        # For now, return a mock date
        return datetime.utcnow() - timedelta(days=45)


# Export main class
__all__ = [
    "PasswordPolicyEngine",
    "PasswordStrengthLevel", 
    "PolicyViolationType",
    "PasswordStrengthResult",
    "PasswordPolicy"
]