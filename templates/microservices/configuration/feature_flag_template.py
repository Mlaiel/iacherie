#!/usr/bin/env python3
"""
🚩 FEATURE FLAG TEMPLATE - DYNAMIC FEATURE MANAGEMENT
=====================================================

Feature flag management for gradual rollouts, A/B testing,
and runtime feature toggling without deployments.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class FeatureStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    BETA = "beta"
    ROLLOUT = "rollout"

@dataclass
class FeatureFlag:
    """Feature flag definition"""
    name: str
    status: FeatureStatus
    rollout_percentage: int = 0
    target_users: list = None
    description: str = ""

class FeatureFlagTemplate:
    """
    🚀 ENTERPRISE FEATURE FLAG TEMPLATE
    
    Dynamic feature management with rollout control and targeting.
    """
    
    def __init__(self):
        """Initialize feature flag manager"""
        self.flags: Dict[str, FeatureFlag] = {}
        self._load_default_flags()
    
    def _load_default_flags(self):
        """Load default feature flags"""
        default_flags = [
            FeatureFlag("new_ui", FeatureStatus.BETA, rollout_percentage=25),
            FeatureFlag("enhanced_search", FeatureStatus.ENABLED),
            FeatureFlag("premium_features", FeatureStatus.ROLLOUT, rollout_percentage=50)
        ]
        
        for flag in default_flags:
            self.flags[flag.name] = flag
    
    def is_feature_enabled(self, feature_name: str, user_id: str = None) -> bool:
        """Check if feature is enabled for user"""
        flag = self.flags.get(feature_name)
        
        if not flag:
            return False
        
        if flag.status == FeatureStatus.DISABLED:
            return False
        elif flag.status == FeatureStatus.ENABLED:
            return True
        elif flag.status in [FeatureStatus.BETA, FeatureStatus.ROLLOUT]:
            # Simple rollout logic based on user ID hash
            if user_id:
                user_hash = hash(user_id) % 100
                return user_hash < flag.rollout_percentage
            return False
        
        return False
    
    def add_feature_flag(self, flag: FeatureFlag):
        """Add new feature flag"""
        self.flags[flag.name] = flag
    
    def update_rollout_percentage(self, feature_name: str, percentage: int):
        """Update rollout percentage for feature"""
        if feature_name in self.flags:
            self.flags[feature_name].rollout_percentage = percentage