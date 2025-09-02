"""Log Filtering Configuration for IA-Influencer Agent Platform
==========================================================

Advanced log filtering and sensitive data protection for multi-format
content processing, security compliance, and privacy preservation.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import re
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List, Union, Callable, Pattern, Set
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timezone

from cryptography.fernet import Fernet
import base64


class FilterAction(str, Enum):
    """
Actions to take when filter matches"""

    REDACT = "redact"           # Replace with [REDACTED]
    MASK = "mask"               # Replace with asterisks
    HASH = "hash"               # Replace with hash
    ENCRYPT = "encrypt"         # Encrypt the value
    DROP = "drop"               # Drop the entire log entry
    ALLOW = "allow"             # Allow the log entry
    TRANSFORM = "transform"     # Apply custom transformation


class FilterScope(str, Enum):
    """Scope of filtering application"""

    MESSAGE = "message"         # Filter only message field
    FIELD = "field"            # Filter specific field
    ALL_FIELDS = "all_fields"  # Filter all string fields
    RECORD = "record"          # Filter entire log record


class SensitiveDataType(str, Enum):
    """Types of sensitive data to detect"""

    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    EMAIL = "email"
    PHONE = "phone"
    IP_ADDRESS = "ip_address"
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    PERSONAL_NAME = "personal_name"
    BANK_ACCOUNT = "bank_account"
    CRYPTO_WALLET = "crypto_wallet"
    LICENSE_KEY = "license_key"
    DATABASE_URL = "database_url"
    AWS_KEY = "aws_key"
    JWT_TOKEN = "jwt_token"
    OAUTH_TOKEN = "oauth_token"


@dataclass
class FilterRule:
    """Individual filter rule configuration"""
    name: str
    pattern: Union[str, Pattern]
    action: FilterAction
    scope: FilterScope
    
    # Rule conditions
    log_level: Optional[str] = None
    logger_name: Optional[str] = None
    field_name: Optional[str] = None
    
    # Action parameters
    replacement_text: str = "[REDACTED]"
    mask_character: str = "*"
    mask_preserve_start: int = 0
    mask_preserve_end: int = 0
    hash_algorithm: str = "sha256"
    encryption_key: Optional[str] = None
    
    # Custom transformation function
    transform_func: Optional[Callable[[str], str]] = None
    
    # Rule metadata
    enabled: bool = True
    priority: int = 100  # Lower number = higher priority
    description: str = ""
    compliance_tags: List[str] = field(default_factory=list)
    
    # Performance settings
    case_sensitive: bool = False
    use_regex: bool = True
    cache_results: bool = True


@dataclass
class ComplianceConfig:
    """Compliance-specific filtering configuration"""
    gdpr_enabled: bool = True
    ccpa_enabled: bool = True
    hipaa_enabled: bool = False
    pci_dss_enabled: bool = True
    sox_enabled: bool = False
    
    # PII detection and protection
    detect_pii: bool = True
    protect_eu_citizens: bool = True
    protect_california_residents: bool = True
    
    # Data retention compliance
    apply_retention_filters: bool = True
    auto_purge_expired: bool = True
    
    # Audit requirements
    log_filter_actions: bool = True
    maintain_filter_audit: bool = True


class LogFilteringConfig:
    """
    Enterprise log filtering configuration for IA-Influencer platform.
    
    Provides comprehensive filtering, sensitive data protection, compliance
    enforcement, and privacy preservation for multi-format content processing logs.
    """
    
    def __init__(
        self,
        enabled: bool = True,
        rules: Optional[List[FilterRule]] = None,
        compliance_config: Optional[ComplianceConfig] = None,
        global_encryption_key: Optional[str] = None,
        enable_pattern_caching: bool = True,
        max_cache_size: int = 1000,
        enable_performance_monitoring: bool = True,
        custom_sensitive_patterns: Optional[Dict[str, str]] = None,
        whitelist_patterns: Optional[List[str]] = None,
        blacklist_patterns: Optional[List[str]] = None
    ):
        """
        Initialize log filtering configuration.
        
        Args:
            enabled: Enable log filtering
            rules: List of filtering rules
            compliance_config: Compliance configuration
            global_encryption_key: Global encryption key
            enable_pattern_caching: Enable regex pattern caching
            max_cache_size: Maximum cache size
            enable_performance_monitoring: Enable performance monitoring
            custom_sensitive_patterns: Custom sensitive data patterns
            whitelist_patterns: Patterns to always allow
            blacklist_patterns: Patterns to always block
        """
        self.enabled = enabled
        self.compliance_config = compliance_config or ComplianceConfig()
        self.enable_pattern_caching = enable_pattern_caching
        self.max_cache_size = max_cache_size
        self.enable_performance_monitoring = enable_performance_monitoring
        self.custom_sensitive_patterns = custom_sensitive_patterns or {}
        self.whitelist_patterns = whitelist_patterns or []
        self.blacklist_patterns = blacklist_patterns or []
        
        # Initialize encryption
        self._fernet = None
        if global_encryption_key:
            self._initialize_encryption(global_encryption_key)
        
        # Initialize rules
        self.rules = rules or self._create_default_rules()
        
        # Compile patterns and sort by priority
        self._compile_patterns()
        
        # Initialize caches
        self._pattern_cache: Dict[str, bool] = {}
        self._cache_lock = threading.RLock()
        
        # Performance monitoring
        self._filter_stats = {
            'total_processed': 0,
            'total_filtered': 0,
            'rules_matched': {},
            'processing_time': 0.0
        }
        self._stats_lock = threading.Lock()
    
    def _initialize_encryption(self, key: str) -> None:
        """
Initialize encryption for sensitive data"""
        try:
            if len(key) == 32:
                # Assume it's already a proper key
                key_bytes = base64.urlsafe_b64encode(key.encode()[:32])
            else:
                # Derive key from password
                key_hash = hashlib.sha256(key.encode()).digest()
                key_bytes = base64.urlsafe_b64encode(key_hash)
            
            self._fernet = Fernet(key_bytes)
        except Exception as e:
            logging.error(f"Failed to initialize filtering encryption: {e}")
            self._fernet = None
    
    def _create_default_rules(self) -> List[FilterRule]:
        try:
            logger.info(f"Executing _create_default_rules")
            
            # Implementation for _create_default_rules
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_create_default_rules completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_create_default_rules failed: {e}")
            raise
    def _compile_patterns(self) -> None:
        """Compile regex patterns and sort rules by priority"""
        # Sort rules by priority (lower number = higher priority)
        self.rules.sort(key=lambda r: r.priority)
        
        # Compile regex patterns
        for rule in self.rules:
            if rule.use_regex and isinstance(rule.pattern, str):
                flags = 0 if rule.case_sensitive else re.IGNORECASE
                try:
                    rule.pattern = re.compile(rule.pattern, flags)
                except re.error as e:
                    logging.error(f"Invalid regex pattern in rule {rule.name}: {e}")
                    rule.enabled = False
    
    def filter_log_record(self, record: logging.LogRecord) -> Optional[logging.LogRecord]:
        """
        Filter a log record according to configured rules.
        
        Args:
            record: Log record to filter
            
        Returns:
            Filtered log record or None if dropped
        """
        if not self.enabled:
            return record
        
        start_time = datetime.now()
        
        try:
            # Convert record to dictionary for easier processing
            record_dict = {
                'message': record.getMessage(),
                'level': record.levelname,
                'logger': record.name,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'timestamp': datetime.fromtimestamp(record.created).isoformat()
            }
            
            # Add any extra fields from record
            for key, value in record.__dict__.items():
                if key not in record_dict and not key.startswith('_'):
                    record_dict[key] = value
            
            # Apply whitelist check first
            if self._check_whitelist(record_dict):
                return record
            
            # Apply blacklist check
            if self._check_blacklist(record_dict):
                return None  # Drop the record
            
            # Apply filtering rules
            filtered_dict = self._apply_filter_rules(record_dict)
            
            if filtered_dict is None:
                # Record was dropped
                self._update_stats('dropped', None)
                return None
            
            # Update the original record with filtered data
            if 'message' in filtered_dict:
                record.msg = filtered_dict['message']
                record.args = ()
            
            # Update other fields
            for key, value in filtered_dict.items():
                if hasattr(record, key) and key != 'message':
                    setattr(record, key, value)
            
            self._update_stats('processed', None)
            return record
            
        except Exception as e:
            logging.error(f"Error filtering log record: {e}")
            return record
        finally:
            if self.enable_performance_monitoring:
                processing_time = (datetime.now() - start_time).total_seconds()
                with self._stats_lock:
                    self._filter_stats['processing_time'] += processing_time
    
    def filter_log_dict(self, log_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Filter a log dictionary according to configured rules.
        
        Args:
            log_dict: Log dictionary to filter
            
        Returns:
            Filtered log dictionary or None if dropped
        """
        if not self.enabled:
            return log_dict
        
        start_time = datetime.now()
        
        try:
            # Apply whitelist check first
            if self._check_whitelist(log_dict):
                return log_dict
            
            # Apply blacklist check
            if self._check_blacklist(log_dict):
                return None  # Drop the record
            
            # Apply filtering rules
            filtered_dict = self._apply_filter_rules(log_dict.copy())
            
            if filtered_dict is None:
                self._update_stats('dropped', None)
                return None
            
            self._update_stats('processed', None)
            return filtered_dict
            
        except Exception as e:
            logging.error(f"Error filtering log dictionary: {e}")
            return log_dict
        finally:
            if self.enable_performance_monitoring:
                processing_time = (datetime.now() - start_time).total_seconds()
                with self._stats_lock:
                    self._filter_stats['processing_time'] += processing_time
    
    def _check_whitelist(self, log_data: Dict[str, Any]) -> bool:
        """Check if log data matches whitelist patterns"""
        if not self.whitelist_patterns:
            return False
        
        log_text = json.dumps(log_data, default=str).lower()
        
        for pattern in self.whitelist_patterns:
            if isinstance(pattern, str):
                if pattern.lower() in log_text:
                    return True
            elif hasattr(pattern, 'search'):
                if pattern.search(log_text):
                    return True
        
        return False
    
    def _check_blacklist(self, log_data: Dict[str, Any]) -> bool:
        """
Check if log data matches blacklist patterns"""
        if not self.blacklist_patterns:
            return False
        
        log_text = json.dumps(log_data, default=str).lower()
        
        for pattern in self.blacklist_patterns:
            if isinstance(pattern, str):
                if pattern.lower() in log_text:
                    return True
            elif hasattr(pattern, 'search'):
                if pattern.search(log_text):
                    return True
        
        return False
    
    def _apply_filter_rules(self, log_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
Apply all filtering rules to log data"""
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Check if rule applies to this log entry
            if not self._rule_applies(rule, log_data):
                continue
            
            # Apply the rule
            try:
                result = self._apply_rule(rule, log_data)
                
                if result is None:
                    # Rule indicated to drop the entire record
                    self._update_stats('rule_matched', rule.name)
                    return None
                
                log_data = result
                self._update_stats('rule_matched', rule.name)
                
            except Exception as e:
                logging.error(f"Error applying rule {rule.name}: {e}")
                continue
        
        return log_data
    
    def _rule_applies(self, rule: FilterRule, log_data: Dict[str, Any]) -> bool:
        """Check if a rule applies to the given log data"""
        # Check log level
        if rule.log_level and log_data.get('level') != rule.log_level:
            return False
        
        # Check logger name
        if rule.logger_name and log_data.get('logger') != rule.logger_name:
            return False
        
        return True
    
    def _apply_rule(self, rule: FilterRule, log_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
Apply a single filtering rule to log data"""
        if rule.scope == FilterScope.MESSAGE:
            # Filter only the message field
            message = str(log_data.get('message', ''))
            filtered_message = self._apply_rule_to_text(rule, message)
            
            if filtered_message is None and rule.action == FilterAction.DROP:
                return None
            
            if filtered_message is not None:
                log_data['message'] = filtered_message
        
        elif rule.scope == FilterScope.FIELD:
            # Filter a specific field
            if rule.field_name and rule.field_name in log_data:
                field_value = str(log_data[rule.field_name])
                filtered_value = self._apply_rule_to_text(rule, field_value)
                
                if filtered_value is None and rule.action == FilterAction.DROP:
                    return None
                
                if filtered_value is not None:
                    log_data[rule.field_name] = filtered_value
        
        elif rule.scope == FilterScope.ALL_FIELDS:
            # Filter all string fields
            for key, value in log_data.items():
                if isinstance(value, str):
                    filtered_value = self._apply_rule_to_text(rule, value)
                    
                    if filtered_value is None and rule.action == FilterAction.DROP:
                        return None
                    
                    if filtered_value is not None:
                        log_data[key] = filtered_value
        
        elif rule.scope == FilterScope.RECORD:
            # Check entire record for pattern match
            record_text = json.dumps(log_data, default=str)
            if self._pattern_matches(rule.pattern, record_text):
                if rule.action == FilterAction.DROP:
                    return None
                # For record-level filters, we might transform the entire record
                # This could be implemented based on specific requirements
        
        return log_data
    
    def _apply_rule_to_text(self, rule: FilterRule, text: str) -> Optional[str]:
        """
Apply a filtering rule to a text string"""
        if not self._pattern_matches(rule.pattern, text):
            return text
        
        if rule.action == FilterAction.DROP:
            return None
        
        elif rule.action == FilterAction.ALLOW:
            return text
        
        elif rule.action == FilterAction.REDACT:
            return self._redact_matches(rule.pattern, text, rule.replacement_text)
        
        elif rule.action == FilterAction.MASK:
            return self._mask_matches(
                rule.pattern, text, rule.mask_character,
                rule.mask_preserve_start, rule.mask_preserve_end
            )
        
        elif rule.action == FilterAction.HASH:
            return self._hash_matches(rule.pattern, text, rule.hash_algorithm)
        
        elif rule.action == FilterAction.ENCRYPT:
            return self._encrypt_matches(rule.pattern, text, rule.encryption_key)
        
        elif rule.action == FilterAction.TRANSFORM and rule.transform_func:
            return rule.transform_func(text)
        
        return text
    
    def _pattern_matches(self, pattern: Union[str, Pattern], text: str) -> bool:
        """
Check if pattern matches text"""
        if self.enable_pattern_caching:
            cache_key = f"{hash(str(pattern))}_{hash(text)}"
            
            with self._cache_lock:
                if cache_key in self._pattern_cache:
                    return self._pattern_cache[cache_key]
        
        if isinstance(pattern, str):
            result = pattern.lower() in text.lower()
        else:
            result = bool(pattern.search(text))
        
        if self.enable_pattern_caching:
            with self._cache_lock:
                if len(self._pattern_cache) >= self.max_cache_size:
                    # Clear half of the cache
                    items_to_remove = list(self._pattern_cache.keys())[:self.max_cache_size // 2]
                    for key in items_to_remove:
                        del self._pattern_cache[key]
                
                self._pattern_cache[cache_key] = result
        
        return result
    
    def _redact_matches(self, pattern: Union[str, Pattern], text: str, replacement: str) -> str:
        """Replace pattern matches with replacement text"""
        if isinstance(pattern, str):
            return text.replace(pattern, replacement)
        else:
            return pattern.sub(replacement, text)
    
    def _mask_matches(
        self, pattern: Union[str, Pattern], text: str, mask_char: str,
        preserve_start: int, preserve_end: int
    ) -> str:
        """
Mask pattern matches with specified character"""
        def mask_function(match):
            matched_text = match.group(0)
            start_len = min(preserve_start, len(matched_text))
            end_len = min(preserve_end, len(matched_text) - start_len)
            middle_len = len(matched_text) - start_len - end_len
            
            return (
                matched_text[:start_len] +
                mask_char * middle_len +
                matched_text[-end_len:] if end_len > 0 else ''
            )
        
        if isinstance(pattern, str):
            # For string patterns, find all occurrences and mask them
            result = text
            while pattern in result:
                index = result.find(pattern)
                matched_text = result[index:index + len(pattern)]
                masked = mask_function(type('Match', (), {'group': lambda self, n: matched_text})())
                result = result[:index] + masked + result[index + len(pattern):]
            return result
        else:
            return pattern.sub(mask_function, text)
    
    def _hash_matches(self, pattern: Union[str, Pattern], text: str, algorithm: str) -> str:
        """
Replace pattern matches with hash values"""
        def hash_function(match):
            matched_text = match.group(0)
            
            if algorithm == "sha256":
                hash_obj = hashlib.sha256(matched_text.encode())
            elif algorithm == "md5":
                hash_obj = hashlib.md5(matched_text.encode())
            elif algorithm == "sha1":
                hash_obj = hashlib.sha1(matched_text.encode())
            else:
                hash_obj = hashlib.sha256(matched_text.encode())
            
            return f"[HASH:{hash_obj.hexdigest()[:16]}]"
        
        if isinstance(pattern, str):
            # For string patterns, find and hash all occurrences
            result = text
            while pattern in result:
                index = result.find(pattern)
                matched_text = result[index:index + len(pattern)]
                hashed = hash_function(type('Match', (), {'group': lambda self, n: matched_text})())
                result = result[:index] + hashed + result[index + len(pattern):]
            return result
        else:
            return pattern.sub(hash_function, text)
    
    def _encrypt_matches(self, pattern: Union[str, Pattern], text: str, encryption_key: Optional[str]) -> str:
        """Encrypt pattern matches"""
        if not self._fernet and not encryption_key:
            return self._redact_matches(pattern, text, "[ENCRYPT_FAILED]")
        
        fernet = self._fernet
        if encryption_key and encryption_key != "global":
            # Use rule-specific encryption key
            try:
                key_hash = hashlib.sha256(encryption_key.encode()).digest()
                key_bytes = base64.urlsafe_b64encode(key_hash)
                fernet = Fernet(key_bytes)
            except Exception:
                return self._redact_matches(pattern, text, "[ENCRYPT_FAILED]")
        
        def encrypt_function(match):
            try:
                matched_text = match.group(0)
                encrypted = fernet.encrypt(matched_text.encode())
                return f"[ENCRYPTED:{base64.b64encode(encrypted).decode()[:32]}...]"
            except Exception:
                return "[ENCRYPT_FAILED]"
        
        if isinstance(pattern, str):
            # For string patterns, find and encrypt all occurrences
            result = text
            while pattern in result:
                index = result.find(pattern)
                matched_text = result[index:index + len(pattern)]
                encrypted = encrypt_function(type('Match', (), {'group': lambda self, n: matched_text})())
                result = result[:index] + encrypted + result[index + len(pattern):]
            return result
        else:
            return pattern.sub(encrypt_function, text)
    
    def _update_stats(self, stat_type: str, rule_name: Optional[str]) -> None:
        """Update filtering statistics"""
        if not self.enable_performance_monitoring:
            return
        
        with self._stats_lock:
            if stat_type == 'processed':
                self._filter_stats['total_processed'] += 1
            elif stat_type == 'dropped':
                self._filter_stats['total_filtered'] += 1
            elif stat_type == 'rule_matched' and rule_name:
                if 'rules_matched' not in self._filter_stats:
                    self._filter_stats['rules_matched'] = {}
                self._filter_stats['rules_matched'][rule_name] = \
                    self._filter_stats['rules_matched'].get(rule_name, 0) + 1
    
    def add_rule(self, rule: FilterRule) -> None:
        """
Add a new filtering rule"""
        self.rules.append(rule)
        self._compile_patterns()
        logging.info(f"Added filtering rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a filtering rule"""
        rule = next((r for r in self.rules if r.name == rule_name), None)
        if rule:
            self.rules.remove(rule)
            logging.info(f"Removed filtering rule: {rule_name}")
            return True
        return False
    
    def update_rule(self, rule_name: str, **kwargs) -> bool:
        """Update an existing filtering rule"""
        rule = next((r for r in self.rules if r.name == rule_name), None)
        if rule:
            for key, value in kwargs.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            self._compile_patterns()
            logging.info(f"Updated filtering rule: {rule_name}")
            return True
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """Enable a filtering rule"""
        return self.update_rule(rule_name, enabled=True)
    
    def disable_rule(self, rule_name: str) -> bool:
        """
Disable a filtering rule"""
        return self.update_rule(rule_name, enabled=False)
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """
Get filtering statistics"""
        with self._stats_lock:
            return self._filter_stats.copy()
    
    def reset_stats(self) -> None:
        """
Reset filtering statistics"""
        with self._stats_lock:
            self._filter_stats = {
                'total_processed': 0,
                'total_filtered': 0,
                'rules_matched': {},
                'processing_time': 0.0
            }
    
    def clear_cache(self) -> None:
        """
Clear pattern matching cache"""
        with self._cache_lock:
            self._pattern_cache.clear()
    
    def get_config_status(self) -> Dict[str, Any]:
        """
Get current configuration status"""
        return {
            "enabled": self.enabled,
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules if r.enabled]),
            "compliance_config": asdict(self.compliance_config) if hasattr(self.compliance_config, '__dict__') else {},
            "cache_size": len(self._pattern_cache),
            "max_cache_size": self.max_cache_size,
            "performance_monitoring": self.enable_performance_monitoring,
            "pattern_caching": self.enable_pattern_caching,
            "encryption_enabled": self._fernet is not None,
            "whitelist_patterns": len(self.whitelist_patterns),
            "blacklist_patterns": len(self.blacklist_patterns),
            "custom_patterns": len(self.custom_sensitive_patterns)
        }


class SecurityLogFilter(logging.Filter):
    """Logging filter for security-related logs"""
    
    def __init__(self, filtering_config: LogFilteringConfig):
        super().__init__()
        self.filtering_config = filtering_config
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
Filter security log records"""
        # Only process security-related logs
        if not record.name.startswith('ia_influencer_security'):
            return True
        
        filtered_record = self.filtering_config.filter_log_record(record)
        return filtered_record is not None


class PerformanceLogFilter(logging.Filter):
    """
Logging filter for performance-related logs"""
    
    def __init__(self, filtering_config: LogFilteringConfig):
        super().__init__()
        self.filtering_config = filtering_config
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
Filter performance log records"""
        # Only process performance-related logs
        if not record.name.startswith('ia_influencer_performance'):
            return True
        
        filtered_record = self.filtering_config.filter_log_record(record)
        return filtered_record is not None


class AuditLogFilter(logging.Filter):
    """
Logging filter for audit-related logs"""
    
    def __init__(self, filtering_config: LogFilteringConfig):
        super().__init__()
        self.filtering_config = filtering_config
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
Filter audit log records"""
        # Only process audit-related logs
        if not record.name.startswith('ia_influencer_audit'):
            return True
        
        filtered_record = self.filtering_config.filter_log_record(record)
        return filtered_record is not None


# Global log filtering configuration instance
_filtering_config: Optional[LogFilteringConfig] = None
        try:
            logger.info(f"Executing encrypt_function")
            
            # Implementation for encrypt_function
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"encrypt_function completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"encrypt_function failed: {e}")
            raise
_filtering_config: Optional[LogFilteringConfig] = None


def initialize_log_filtering(
    config: Optional[LogFilteringConfig] = None
) -> LogFilteringConfig:
    """
    Initialize global log filtering configuration.
    
    Args:
        config: Custom LogFilteringConfig instance
        
    Returns:
        Initialized log filtering configuration
    """
    global _filtering_config
    
    if config:
        _filtering_config = config
    else:
        _filtering_config = LogFilteringConfig()
    
    return _filtering_config


def get_filtering_config() -> LogFilteringConfig:
    """
Get the global log filtering configuration"""
    if not _filtering_config:
        initialize_log_filtering()
    
    return _filtering_config


def filter_log_dict(log_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter a log dictionary using global configuration.
    
    Args:
        log_dict: Log dictionary to filter
        
    Returns:
        Filtered log dictionary or None if dropped
    """
    config = get_filtering_config()
    return config.filter_log_dict(log_dict)
