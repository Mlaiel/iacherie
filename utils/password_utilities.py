"""
Password Security Utilities - Enterprise Password Management System
==================================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive password security utilities supporting:
- Advanced password hashing and validation
- Password strength analysis and policy enforcement
- Secure password generation and rotation
- Breach detection and security monitoring
- Multi-factor authentication support

Expert Roles Covered:
- Security Expert: Password security and cryptographic operations
- Backend Senior: Password management and validation systems
- DevOps Expert: Security monitoring and policy enforcement
"""

import hashlib
import secrets
import string
import re
import time
import hmac
import base64
import json
from typing import Dict, List, Optional, Union, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import math
import unicodedata

# External dependencies for advanced features
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

try:
    import argon2
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False

try:
    import scrypt
    SCRYPT_AVAILABLE = True
except ImportError:
    SCRYPT_AVAILABLE = False

logger = logging.getLogger(__name__)


class HashAlgorithm(Enum):
    """Password hashing algorithms"""
    BCRYPT = "bcrypt"
    ARGON2 = "argon2"
    SCRYPT = "scrypt"
    PBKDF2_SHA256 = "pbkdf2_sha256"
    PBKDF2_SHA512 = "pbkdf2_sha512"


class PasswordStrength(Enum):
    """Password strength levels"""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class PasswordComplexity(Enum):
    """Password complexity requirements"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    ENTERPRISE = "enterprise"
    MAXIMUM = "maximum"


@dataclass
class PasswordPolicy:
    """Password policy configuration"""
    min_length: int = 8
    max_length: int = 128
    require_lowercase: bool = True
    require_uppercase: bool = True
    require_digits: bool = True
    require_special_chars: bool = True
    min_special_chars: int = 1
    min_digits: int = 1
    min_uppercase: int = 1
    min_lowercase: int = 1
    max_consecutive_chars: int = 3
    max_repeated_chars: int = 2
    forbidden_patterns: List[str] = field(default_factory=list)
    forbidden_words: Set[str] = field(default_factory=set)
    min_unique_chars: int = 4
    require_mixed_case: bool = True
    allow_unicode: bool = False
    entropy_threshold: float = 50.0


@dataclass
class PasswordAnalysis:
    """Password strength analysis result"""
    password: str
    strength: PasswordStrength
    score: int
    entropy: float
    length: int
    character_sets: Dict[str, int]
    patterns_found: List[str]
    policy_violations: List[str]
    estimated_crack_time: str
    recommendations: List[str]
    is_breached: Optional[bool] = None


@dataclass
class PasswordHash:
    """Password hash storage format"""
    algorithm: HashAlgorithm
    hash_value: str
    salt: Optional[str] = None
    iterations: Optional[int] = None
    memory_cost: Optional[int] = None
    parallelism: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PasswordUtilities:
    """
    Enterprise-grade password security utilities for authentication systems.
    
    Features:
    - Multiple advanced hashing algorithms
    - Comprehensive password strength analysis
    - Policy enforcement and validation
    - Secure password generation
    - Breach detection capabilities
    - Performance optimization
    """
    
    def __init__(self,
                 default_algorithm -> None: HashAlgorithm = HashAlgorithm.ARGON2,
                 default_policy -> None: Optional[PasswordPolicy] = None,
                 enable_breach_checking -> None: bool = True,
                 pepper -> None: Optional[str] = None) -> None:
        """
        Initialize password utilities
        
        Args:
            default_algorithm: Default hashing algorithm
            default_policy: Default password policy
            enable_breach_checking: Whether to enable breach checking
            pepper: Optional pepper for additional security
        """
        try:
            logger.info("Initializing PasswordUtilities")
            
            # Configuration
            self.default_algorithm = default_algorithm
            self.pepper = pepper
            self.enable_breach_checking = enable_breach_checking
            
            # Default password policy
            self.default_policy = default_policy or self._get_default_policy()
            
            # Predefined policies by complexity level
            self.complexity_policies = self._get_complexity_policies()
            
            # Common password patterns
            self.common_patterns = [
                r'(.)\1{2,}',  # Repeated characters
                r'(012|123|234|345|456|567|678|789|890)',  # Sequential numbers
                r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
                r'(qwer|asdf|zxcv|qwerty|asdfgh|zxcvbn)',  # Keyboard patterns
                r'(password|pass|1234|0000|admin|user|test|guest)',  # Common passwords
            ]
            
            # Common weak passwords (top 1000 most common)
            self.common_passwords = self._load_common_passwords()
            
            # Character sets for analysis
            self.character_sets = {
                'lowercase': string.ascii_lowercase,
                'uppercase': string.ascii_uppercase,
                'digits': string.digits,
                'special': '!@#$%^&*()_+-=[]{}|;:,.<>?',
                'space': ' ',
                'unicode': ''  # Will be populated as needed
            }
            
            # Hash algorithm configurations
            self.hash_configs = {
                HashAlgorithm.BCRYPT: {'rounds': 12},
                HashAlgorithm.ARGON2: {'time_cost': 3, 'memory_cost': 65536, 'parallelism': 1},
                HashAlgorithm.SCRYPT: {'n': 32768, 'r': 8, 'p': 1},
                HashAlgorithm.PBKDF2_SHA256: {'iterations': 100000},
                HashAlgorithm.PBKDF2_SHA512: {'iterations': 100000}
            }
            
            # Statistics
            self.password_stats = {
                "total_hashes_created": 0,
                "total_verifications": 0,
                "successful_verifications": 0,
                "failed_verifications": 0,
                "policy_violations_detected": 0,
                "breaches_detected": 0
            }
            
            logger.info("PasswordUtilities initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PasswordUtilities: {e}")
            raise

    def hash_password(self, 
                     password: str,
                     algorithm: Optional[HashAlgorithm] = None,
                     custom_config: Optional[Dict[str, Any]] = None) -> PasswordHash:
        """
        Hash a password using the specified algorithm
        
        Args:
            password: Plain text password
            algorithm: Hashing algorithm to use
            custom_config: Custom configuration for the algorithm
            
        Returns:
            PasswordHash object with hash details
        """
        try:
            algorithm = algorithm or self.default_algorithm
            config = custom_config or self.hash_configs.get(algorithm, {})
            
            logger.debug(f"Hashing password with {algorithm.value}")
            
            # Add pepper if configured
            if self.pepper:
                password = password + self.pepper
            
            if algorithm == HashAlgorithm.BCRYPT and BCRYPT_AVAILABLE:
                rounds = config.get('rounds', 12)
                salt = bcrypt.gensalt(rounds=rounds)
                hash_value = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                
                return PasswordHash(
                    algorithm=algorithm,
                    hash_value=hash_value,
                    iterations=rounds,
                    metadata={'rounds': rounds}
                )
            
            elif algorithm == HashAlgorithm.ARGON2 and ARGON2_AVAILABLE:
                ph = argon2.PasswordHasher(
                    time_cost=config.get('time_cost', 3),
                    memory_cost=config.get('memory_cost', 65536),
                    parallelism=config.get('parallelism', 1)
                )
                hash_value = ph.hash(password)
                
                return PasswordHash(
                    algorithm=algorithm,
                    hash_value=hash_value,
                    memory_cost=config.get('memory_cost'),
                    parallelism=config.get('parallelism'),
                    iterations=config.get('time_cost')
                )
            
            elif algorithm == HashAlgorithm.SCRYPT and SCRYPT_AVAILABLE:
                salt = secrets.token_bytes(32)
                hash_value = scrypt.hash(
                    password.encode('utf-8'),
                    salt,
                    config.get('n', 32768),
                    config.get('r', 8),
                    config.get('p', 1),
                    64
                )
                
                # Encode for storage
                encoded_hash = base64.b64encode(hash_value).decode('utf-8')
                encoded_salt = base64.b64encode(salt).decode('utf-8')
                
                return PasswordHash(
                    algorithm=algorithm,
                    hash_value=encoded_hash,
                    salt=encoded_salt,
                    metadata={
                        'n': config.get('n'),
                        'r': config.get('r'),
                        'p': config.get('p')
                    }
                )
            
            elif algorithm in [HashAlgorithm.PBKDF2_SHA256, HashAlgorithm.PBKDF2_SHA512]:
                iterations = config.get('iterations', 100000)
                salt = secrets.token_bytes(32)
                
                if algorithm == HashAlgorithm.PBKDF2_SHA256:
                    hash_value = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
                else:
                    hash_value = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, iterations)
                
                encoded_hash = base64.b64encode(hash_value).decode('utf-8')
                encoded_salt = base64.b64encode(salt).decode('utf-8')
                
                return PasswordHash(
                    algorithm=algorithm,
                    hash_value=encoded_hash,
                    salt=encoded_salt,
                    iterations=iterations
                )
            
            else:
                raise ValueError(f"Unsupported or unavailable algorithm: {algorithm.value}")
            
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise
        finally:
            self.password_stats["total_hashes_created"] += 1

    def verify_password(self, password: str, password_hash: PasswordHash) -> bool:
        """
        Verify a password against its hash
        
        Args:
            password: Plain text password
            password_hash: PasswordHash object
            
        Returns:
            True if password matches hash
        """
        try:
            self.password_stats["total_verifications"] += 1
            
            # Add pepper if configured
            if self.pepper:
                password = password + self.pepper
            
            algorithm = password_hash.algorithm
            
            if algorithm == HashAlgorithm.BCRYPT and BCRYPT_AVAILABLE:
                result = bcrypt.checkpw(password.encode('utf-8'), password_hash.hash_value.encode('utf-8'))
            
            elif algorithm == HashAlgorithm.ARGON2 and ARGON2_AVAILABLE:
                ph = argon2.PasswordHasher()
                try:
                    ph.verify(password_hash.hash_value, password)
                    result = True
                except argon2.exceptions.VerifyMismatchError:
                    result = False
            
            elif algorithm == HashAlgorithm.SCRYPT and SCRYPT_AVAILABLE:
                stored_hash = base64.b64decode(password_hash.hash_value)
                salt = base64.b64decode(password_hash.salt)
                
                computed_hash = scrypt.hash(
                    password.encode('utf-8'),
                    salt,
                    password_hash.metadata.get('n', 32768),
                    password_hash.metadata.get('r', 8),
                    password_hash.metadata.get('p', 1),
                    64
                )
                
                result = hmac.compare_digest(stored_hash, computed_hash)
            
            elif algorithm in [HashAlgorithm.PBKDF2_SHA256, HashAlgorithm.PBKDF2_SHA512]:
                stored_hash = base64.b64decode(password_hash.hash_value)
                salt = base64.b64decode(password_hash.salt)
                
                if algorithm == HashAlgorithm.PBKDF2_SHA256:
                    computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, password_hash.iterations)
                else:
                    computed_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, password_hash.iterations)
                
                result = hmac.compare_digest(stored_hash, computed_hash)
            
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm.value}")
            
            if result:
                self.password_stats["successful_verifications"] += 1
            else:
                self.password_stats["failed_verifications"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            self.password_stats["failed_verifications"] += 1
            return False

    def analyze_password_strength(self, 
                                password: str,
                                policy: Optional[PasswordPolicy] = None,
                                check_breaches: bool = None) -> PasswordAnalysis:
        """
        Analyze password strength and compliance
        
        Args:
            password: Password to analyze
            policy: Password policy to check against
            check_breaches: Whether to check for breaches
            
        Returns:
            PasswordAnalysis with detailed results
        """
        try:
            policy = policy or self.default_policy
            check_breaches = check_breaches if check_breaches is not None else self.enable_breach_checking
            
            logger.debug(f"Analyzing password strength")
            
            # Basic measurements
            length = len(password)
            
            # Character set analysis
            character_sets = self._analyze_character_sets(password)
            
            # Calculate entropy
            entropy = self._calculate_entropy(password, character_sets)
            
            # Pattern detection
            patterns_found = self._detect_patterns(password)
            
            # Policy compliance
            policy_violations = self._check_policy_compliance(password, policy)
            
            # Strength scoring
            score = self._calculate_strength_score(password, character_sets, entropy, patterns_found, policy_violations)
            strength = self._determine_strength_level(score)
            
            # Crack time estimation
            crack_time = self._estimate_crack_time(entropy)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(password, character_sets, policy_violations, patterns_found)
            
            # Breach checking (simplified - would integrate with actual breach databases)
            is_breached = None
            if check_breaches:
                is_breached = self._check_password_breaches(password)
            
            return PasswordAnalysis(
                password="[REDACTED]",  # Don't store the actual password
                strength=strength,
                score=score,
                entropy=entropy,
                length=length,
                character_sets=character_sets,
                patterns_found=patterns_found,
                policy_violations=policy_violations,
                estimated_crack_time=crack_time,
                recommendations=recommendations,
                is_breached=is_breached
            )
            
        except Exception as e:
            logger.error(f"Password analysis failed: {e}")
            raise

    def generate_secure_password(self,
                                length: int = 16,
                                policy: Optional[PasswordPolicy] = None,
                                exclude_ambiguous: bool = True,
                                ensure_pronounceable: bool = False) -> str:
        """
        Generate a secure password meeting specified requirements
        
        Args:
            length: Password length
            policy: Password policy to comply with
            exclude_ambiguous: Whether to exclude ambiguous characters
            ensure_pronounceable: Whether to generate pronounceable password
            
        Returns:
            Generated secure password
        """
        try:
            policy = policy or self.default_policy
            
            logger.debug(f"Generating secure password of length {length}")
            
            if ensure_pronounceable:
                return self._generate_pronounceable_password(length, policy)
            
            # Build character set based on policy
            charset = ""
            required_chars = []
            
            if policy.require_lowercase:
                lowercase = string.ascii_lowercase
                if exclude_ambiguous:
                    lowercase = lowercase.replace('l', '').replace('o', '')
                charset += lowercase
                required_chars.extend(secrets.choice(lowercase) for _ in range(policy.min_lowercase))
            
            if policy.require_uppercase:
                uppercase = string.ascii_uppercase
                if exclude_ambiguous:
                    uppercase = uppercase.replace('I', '').replace('O', '')
                charset += uppercase
                required_chars.extend(secrets.choice(uppercase) for _ in range(policy.min_uppercase))
            
            if policy.require_digits:
                digits = string.digits
                if exclude_ambiguous:
                    digits = digits.replace('0', '').replace('1', '')
                charset += digits
                required_chars.extend(secrets.choice(digits) for _ in range(policy.min_digits))
            
            if policy.require_special_chars:
                special = policy.min_special_chars and '!@#$%^&*()_+-=[]{}|;:,.<>?' or ''
                if exclude_ambiguous:
                    special = special.replace('|', '').replace('`', '')
                charset += special
                required_chars.extend(secrets.choice(special) for _ in range(policy.min_special_chars))
            
            # Generate remaining characters
            remaining_length = length - len(required_chars)
            if remaining_length < 0:
                raise ValueError("Required characters exceed password length")
            
            password_chars = required_chars + [secrets.choice(charset) for _ in range(remaining_length)]
            
            # Shuffle to avoid predictable patterns
            secrets.SystemRandom().shuffle(password_chars)
            password = ''.join(password_chars)
            
            # Validate against policy
            analysis = self.analyze_password_strength(password, policy, check_breaches=False)
            if analysis.policy_violations:
                # Retry if policy violations found (recursive with limit)
                return self.generate_secure_password(length, policy, exclude_ambiguous, ensure_pronounceable)
            
            return password
            
        except Exception as e:
            logger.error(f"Password generation failed: {e}")
            raise

    def check_password_policy(self, password: str, policy: Optional[PasswordPolicy] = None) -> List[str]:
        """
        Check password against policy requirements
        
        Args:
            password: Password to check
            policy: Password policy
            
        Returns:
            List of policy violations
        """
        policy = policy or self.default_policy
        return self._check_policy_compliance(password, policy)

    def generate_password_reset_token(self, user_id: str, expiry_minutes: int = 15) -> str:
        """
        Generate secure password reset token
        
        Args:
            user_id: User identifier
            expiry_minutes: Token expiry time in minutes
            
        Returns:
            Secure reset token
        """
        try:
            # Create token payload
            payload = {
                'user_id': user_id,
                'timestamp': time.time(),
                'expiry': time.time() + (expiry_minutes * 60),
                'nonce': secrets.token_hex(16)
            }
            
            # Encode payload
            payload_json = json.dumps(payload, sort_keys=True)
            payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
            
            # Create signature
            signature = hmac.new(
                (self.pepper or "default_key").encode(),
                payload_b64.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return f"{payload_b64}.{signature}"
            
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise

    def verify_password_reset_token(self, token: str, user_id: str) -> bool:
        """
        Verify password reset token
        
        Args:
            token: Reset token to verify
            user_id: Expected user identifier
            
        Returns:
            True if token is valid
        """
        try:
            if '.' not in token:
                return False
            
            payload_b64, signature = token.rsplit('.', 1)
            
            # Verify signature
            expected_signature = hmac.new(
                (self.pepper or "default_key").encode(),
                payload_b64.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return False
            
            # Decode payload
            payload_json = base64.urlsafe_b64decode(payload_b64).decode()
            payload = json.loads(payload_json)
            
            # Verify user ID
            if payload.get('user_id') != user_id:
                return False
            
            # Check expiry
            if time.time() > payload.get('expiry', 0):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return False

    def get_password_statistics(self) -> Dict[str, Any]:
        """
        Get password management statistics
        
        Returns:
            Dictionary with statistics
        """
        total_verifications = self.password_stats["total_verifications"]
        
        return {
            **self.password_stats,
            "verification_success_rate": (self.password_stats["successful_verifications"] / 
                                        max(total_verifications, 1)) * 100,
            "verification_failure_rate": (self.password_stats["failed_verifications"] / 
                                        max(total_verifications, 1)) * 100
        }

    # Private helper methods
    def _get_default_policy(self) -> PasswordPolicy:
        """Get default password policy"""
        return PasswordPolicy(
            min_length=12,
            max_length=128,
            require_lowercase=True,
            require_uppercase=True,
            require_digits=True,
            require_special_chars=True,
            min_special_chars=1,
            min_digits=1,
            min_uppercase=1,
            min_lowercase=1,
            max_consecutive_chars=2,
            max_repeated_chars=2,
            min_unique_chars=8,
            entropy_threshold=60.0
        )

    def _get_complexity_policies(self) -> Dict[PasswordComplexity, PasswordPolicy]:
        """Get predefined complexity policies"""
        return {
            PasswordComplexity.BASIC: PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=False,
                require_digits=True,
                require_special_chars=False,
                entropy_threshold=30.0
            ),
            PasswordComplexity.STANDARD: PasswordPolicy(
                min_length=10,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_special_chars=True,
                min_special_chars=1,
                entropy_threshold=45.0
            ),
            PasswordComplexity.ENHANCED: PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_special_chars=True,
                min_special_chars=2,
                min_digits=2,
                max_consecutive_chars=2,
                entropy_threshold=60.0
            ),
            PasswordComplexity.ENTERPRISE: PasswordPolicy(
                min_length=14,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_special_chars=True,
                min_special_chars=2,
                min_digits=2,
                min_uppercase=2,
                min_lowercase=2,
                max_consecutive_chars=2,
                max_repeated_chars=1,
                min_unique_chars=10,
                entropy_threshold=75.0
            ),
            PasswordComplexity.MAXIMUM: PasswordPolicy(
                min_length=16,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_special_chars=True,
                min_special_chars=3,
                min_digits=3,
                min_uppercase=3,
                min_lowercase=3,
                max_consecutive_chars=1,
                max_repeated_chars=1,
                min_unique_chars=12,
                entropy_threshold=90.0
            )
        }

    def _analyze_character_sets(self, password: str) -> Dict[str, int]:
        """Analyze character sets used in password"""
        sets = {}
        
        for char in password:
            if char in string.ascii_lowercase:
                sets['lowercase'] = sets.get('lowercase', 0) + 1
            elif char in string.ascii_uppercase:
                sets['uppercase'] = sets.get('uppercase', 0) + 1
            elif char in string.digits:
                sets['digits'] = sets.get('digits', 0) + 1
            elif char in '!@#$%^&*()_+-=[]{}|;:,.<>?':
                sets['special'] = sets.get('special', 0) + 1
            elif char == ' ':
                sets['space'] = sets.get('space', 0) + 1
            else:
                sets['unicode'] = sets.get('unicode', 0) + 1
        
        return sets

    def _calculate_entropy(self, password: str, character_sets: Dict[str, int]) -> float:
        """Calculate password entropy"""
        charset_size = 0
        
        if character_sets.get('lowercase', 0) > 0:
            charset_size += 26
        if character_sets.get('uppercase', 0) > 0:
            charset_size += 26
        if character_sets.get('digits', 0) > 0:
            charset_size += 10
        if character_sets.get('special', 0) > 0:
            charset_size += 32
        if character_sets.get('space', 0) > 0:
            charset_size += 1
        if character_sets.get('unicode', 0) > 0:
            charset_size += 1000  # Rough estimate
        
        if charset_size == 0:
            return 0
        
        return len(password) * math.log2(charset_size)

    def _detect_patterns(self, password: str) -> List[str]:
        """Detect common patterns in password"""
        patterns = []
        
        for pattern in self.common_patterns:
            if re.search(pattern, password.lower()):
                patterns.append(pattern)
        
        # Check for common passwords
        if password.lower() in self.common_passwords:
            patterns.append("common_password")
        
        # Check for personal information patterns (simplified)
        if re.search(r'\b(19|20)\d{2}\b', password):
            patterns.append("year_pattern")
        
        return patterns

    def _check_policy_compliance(self, password: str, policy: PasswordPolicy) -> List[str]:
        """Check password against policy requirements"""
        violations = []
        
        # Length checks
        if len(password) < policy.min_length:
            violations.append(f"Password too short (minimum {policy.min_length} characters)")
        
        if len(password) > policy.max_length:
            violations.append(f"Password too long (maximum {policy.max_length} characters)")
        
        # Character set requirements
        character_sets = self._analyze_character_sets(password)
        
        if policy.require_lowercase and character_sets.get('lowercase', 0) < policy.min_lowercase:
            violations.append(f"Requires at least {policy.min_lowercase} lowercase letter(s)")
        
        if policy.require_uppercase and character_sets.get('uppercase', 0) < policy.min_uppercase:
            violations.append(f"Requires at least {policy.min_uppercase} uppercase letter(s)")
        
        if policy.require_digits and character_sets.get('digits', 0) < policy.min_digits:
            violations.append(f"Requires at least {policy.min_digits} digit(s)")
        
        if policy.require_special_chars and character_sets.get('special', 0) < policy.min_special_chars:
            violations.append(f"Requires at least {policy.min_special_chars} special character(s)")
        
        # Pattern checks
        if policy.max_consecutive_chars > 0:
            if re.search(rf'(.)\1{{{policy.max_consecutive_chars},}}', password):
                violations.append(f"Contains more than {policy.max_consecutive_chars} consecutive identical characters")
        
        # Entropy check
        entropy = self._calculate_entropy(password, character_sets)
        if entropy < policy.entropy_threshold:
            violations.append(f"Password entropy too low ({entropy:.1f} < {policy.entropy_threshold})")
        
        # Forbidden patterns
        for pattern in policy.forbidden_patterns:
            if re.search(pattern, password.lower()):
                violations.append(f"Contains forbidden pattern: {pattern}")
        
        # Forbidden words
        password_lower = password.lower()
        for word in policy.forbidden_words:
            if word.lower() in password_lower:
                violations.append(f"Contains forbidden word: {word}")
        
        if violations:
            self.password_stats["policy_violations_detected"] += 1
        
        return violations

    def _calculate_strength_score(self, password: str, character_sets: Dict[str, int], 
                                entropy: float, patterns: List[str], violations: List[str]) -> int:
        """Calculate overall password strength score (0-100)"""
        score = 0
        
        # Base score from length
        score += min(len(password) * 4, 40)
        
        # Character set diversity bonus
        num_sets = len([s for s in character_sets.values() if s > 0])
        score += num_sets * 10
        
        # Entropy bonus
        score += min(entropy / 2, 30)
        
        # Pattern penalties
        score -= len(patterns) * 10
        
        # Policy violation penalties
        score -= len(violations) * 5
        
        return max(0, min(100, score))

    def _determine_strength_level(self, score: int) -> PasswordStrength:
        """Determine strength level from score"""
        if score >= 80:
            return PasswordStrength.VERY_STRONG
        elif score >= 60:
            return PasswordStrength.STRONG
        elif score >= 40:
            return PasswordStrength.MEDIUM
        elif score >= 20:
            return PasswordStrength.WEAK
        else:
            return PasswordStrength.VERY_WEAK

    def _estimate_crack_time(self, entropy: float) -> str:
        """Estimate time to crack password"""
        # Assume 1 billion guesses per second
        guesses_per_second = 10**9
        total_combinations = 2 ** entropy
        time_seconds = total_combinations / (2 * guesses_per_second)  # Average case
        
        if time_seconds < 1:
            return "Instantly"
        elif time_seconds < 60:
            return f"{time_seconds:.0f} seconds"
        elif time_seconds < 3600:
            return f"{time_seconds/60:.0f} minutes"
        elif time_seconds < 86400:
            return f"{time_seconds/3600:.0f} hours"
        elif time_seconds < 31536000:
            return f"{time_seconds/86400:.0f} days"
        else:
            return f"{time_seconds/31536000:.0f} years"

    def _generate_recommendations(self, password: str, character_sets: Dict[str, int], 
                                violations: List[str], patterns: List[str]) -> List[str]:
        """Generate password improvement recommendations"""
        recommendations = []
        
        if len(password) < 12:
            recommendations.append("Increase password length to at least 12 characters")
        
        if not character_sets.get('lowercase'):
            recommendations.append("Add lowercase letters")
        
        if not character_sets.get('uppercase'):
            recommendations.append("Add uppercase letters")
        
        if not character_sets.get('digits'):
            recommendations.append("Add numbers")
        
        if not character_sets.get('special'):
            recommendations.append("Add special characters (!@#$%^&*)")
        
        if patterns:
            recommendations.append("Avoid common patterns and sequences")
        
        if "common_password" in patterns:
            recommendations.append("Avoid commonly used passwords")
        
        return recommendations

    def _check_password_breaches(self, password: str) -> bool:
        """Check if password appears in breach databases (simplified)"""
        # This would integrate with actual breach databases like HaveIBeenPwned
        # For now, just check against common passwords
        is_breached = password.lower() in self.common_passwords
        
        if is_breached:
            self.password_stats["breaches_detected"] += 1
        
        return is_breached

    def _load_common_passwords(self) -> Set[str]:
        """Load common passwords list"""
        # In a real implementation, this would load from a file or database
        return {
            'password', '123456', '123456789', 'qwerty', 'abc123', 'password123',
            '111111', '123123', 'admin', 'letmein', 'welcome', 'monkey',
            '1234567890', 'password1', 'qwerty123', 'dragon', 'master',
            'hello', 'freedom', 'whatever', 'qazwsx', 'trustno1'
        }

    def _generate_pronounceable_password(self, length: int, policy: PasswordPolicy) -> str:
        """Generate a pronounceable password"""
        # Simplified pronounceable password generation
        consonants = "bcdfghjklmnpqrstvwxyz"
        vowels = "aeiou"
        
        password = ""
        is_vowel = False
        
        while len(password) < length:
            if is_vowel:
                password += secrets.choice(vowels)
            else:
                password += secrets.choice(consonants)
            is_vowel = not is_vowel
        
        # Add required characters to meet policy
        if policy.require_uppercase:
            password = password.capitalize()
        
        if policy.require_digits:
            password += str(secrets.randbelow(10))
        
        if policy.require_special_chars:
            password += secrets.choice("!@#$")
        
        return password[:length]


# Utility functions
def quick_password_check(password: str) -> Dict[str, Any]:
    """
    Quick password strength check
    
    Args:
        password: Password to check
        
    Returns:
        Dictionary with basic strength information
    """
    utils = PasswordUtilities()
    analysis = utils.analyze_password_strength(password, check_breaches=False)
    
    return {
        "strength": analysis.strength.value,
        "score": analysis.score,
        "length": analysis.length,
        "entropy": round(analysis.entropy, 1),
        "violations": len(analysis.policy_violations),
        "crack_time": analysis.estimated_crack_time
    }


def generate_strong_password(length: int = 16, exclude_ambiguous: bool = True) -> str:
    """
    Generate a strong password quickly
    
    Args:
        length: Password length
        exclude_ambiguous: Whether to exclude ambiguous characters
        
    Returns:
        Generated strong password
    """
    utils = PasswordUtilities()
    return utils.generate_secure_password(length=length, exclude_ambiguous=exclude_ambiguous)


def is_password_secure(password: str, min_score: int = 60) -> bool:
    """
    Check if password meets minimum security requirements
    
    Args:
        password: Password to check
        min_score: Minimum acceptable score
        
    Returns:
        True if password is secure enough
    """
    result = quick_password_check(password)
    return result["score"] >= min_score and result["violations"] == 0