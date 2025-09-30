"""Ainflue Payment System Configuration
====================================

Payment system configurations for gateway integration, cryptocurrency support,
subscription management, billing, revenue sharing, and blockchain integration.

Enterprise payment configuration management for Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

# Payment system imports
from .payment_gateway_config import PaymentGatewayConfiguration
from .crypto_payment_config import CryptoPaymentConfiguration
from .subscription_management_config import SubscriptionManagementConfiguration

logger = logging.getLogger(__name__)

class PaymentConfigurationLevel(str, Enum):
    """Payment configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"

class PaymentSystemConfigurationManager:
    """Payment system configuration manager"""
    
    def __init__(self, level: PaymentConfigurationLevel = PaymentConfigurationLevel.ENTERPRISE):
        self.level = level
        self.configurations = {}
        self._initialize_payment_configs()
    
    def _initialize_payment_configs(self):
        """Initialize all payment configurations"""
        self.configurations = {
            "payment_gateway": PaymentGatewayConfiguration(level=self.level),
            "crypto_payments": CryptoPaymentConfiguration(level=self.level),
            "subscriptions": SubscriptionManagementConfiguration(level=self.level)
        }
        
        logger.info(f"💳 Payment configurations initialized - Level: {self.level.value}")
    
    def get_config(self, config_name: str) -> Optional[Any]:
        """Get specific payment configuration"""
        return self.configurations.get(config_name)
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all payment configurations"""
        return self.configurations.copy()
    
    def get_gateway_config(self) -> Optional[Any]:
        """Get payment gateway configuration"""
        return self.get_config("payment_gateway")
    
    def get_crypto_config(self) -> Optional[Any]:
        """Get cryptocurrency payment configuration"""
        return self.get_config("crypto_payments")
    
    def get_subscription_config(self) -> Optional[Any]:
        """Get subscription management configuration"""
        return self.get_config("subscriptions")
    
    def validate_payment_compliance(self) -> Dict[str, Any]:
        """Validate payment system compliance"""
        compliance_status = {
            "overall_compliance": True,
            "payment_methods": {},
            "missing_configurations": [],
            "compliance_warnings": []
        }
        
        required_configs = ["payment_gateway", "crypto_payments", "subscriptions"]
        
        for config_name in required_configs:
            if config_name in self.configurations:
                compliance_status["payment_methods"][config_name] = "ENABLED"
            else:
                compliance_status["missing_configurations"].append(config_name)
                compliance_status["overall_compliance"] = False
        
        if not compliance_status["overall_compliance"]:
            compliance_status["compliance_warnings"].append(
                "Missing critical payment configurations"
            )
        
        return compliance_status

# Global payment configuration manager
payment_config_manager = PaymentSystemConfigurationManager()

# Module exports
__all__ = [
    "PaymentGatewayConfiguration",
    "CryptoPaymentConfiguration",
    "SubscriptionManagementConfiguration",
    "PaymentSystemConfigurationManager",
    "PaymentConfigurationLevel",
    "payment_config_manager"
]

logger.info("💳 Ainflue Payment System Configuration Module loaded")
logger.info("⚠️ Protected by copyright - All Rights Reserved")
