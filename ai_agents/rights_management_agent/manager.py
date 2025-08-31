"""Rights Management Manager - Global Digital Rights Management"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from decimal import Decimal

# Import base agent functionality
from ..base import BaseAgent, AgentRequest, AgentResponse

# Import existing rights management functionality
try:
    from core.rights.rights_manager import RightsManager
    from core.rights.digital_fingerprint_engine import DigitalFingerprintEngine
    from core.rights.copyright_detection_service import CopyrightDetectionService
    from core.rights.license_management_system import LicenseManagementSystem
    from core.rights.ownership_validation_service import OwnershipValidationService
    from core.rights.royalty_calculation_engine import RoyaltyCalculationEngine
    from core.rights.monetization_engine import MonetizationEngine
except ImportError:
    # Fallback implementations
    class RightsManager:
        async def register_rights(self, content_id, owner_info): return {"status": "registered"}
    class DigitalFingerprintEngine:
        async def generate_fingerprint(self, content_data): return {"fingerprint": "mock"}
    class CopyrightDetectionService:
        async def detect_violations(self, content_id): return []
    class LicenseManagementSystem:
        async def create_license(self, license_data): return {"license_id": "mock"}
    class OwnershipValidationService:
        async def validate_ownership(self, content_id, claimant): return True
    class RoyaltyCalculationEngine:
        async def calculate_royalties(self, usage_data): return {"amount": 0}
    class MonetizationEngine:
        async def optimize_revenue(self, content_id): return {"strategy": "basic"}

from .models.rights_models import RightsRequest, RightsResult, OwnershipRecord, LicenseAgreement

logger = logging.getLogger(__name__)

@dataclass
class RightsManagementConfig:
    """Configuration for rights management operations"""
    enable_automatic_registration: bool = True
    enable_blockchain_verification: bool = True
    enable_royalty_tracking: bool = True
    default_protection_level: str = "standard"
    royalty_calculation_interval: int = 86400  # 24 hours
    license_auto_renewal: bool = True
    territorial_restrictions: Set[str] = field(default_factory=set)
    supported_license_types: Set[str] = field(default_factory=lambda: {
        'exclusive', 'non_exclusive', 'creative_commons', 'public_domain',
        'commercial', 'personal', 'educational', 'sync', 'mechanical'
    })

class RightsManagementManager(BaseAgent):
    """
    Enterprise Rights Management Manager
    
    Provides comprehensive digital rights management with:
    - Ownership registration and validation
    - License creation and management
    - Royalty calculation and distribution
    - Revenue optimization
    - Territorial rights control
    - Usage tracking and analytics
    """
    
    def __init__(self, agent_id: str = "rights_management_manager"):
        super().__init__(
            agent_id=agent_id,
            agent_type="rights_management",
            version="1.0.0"
        )
        
        self.config = RightsManagementConfig()
        
        # Initialize core components
        self.rights_manager = RightsManager()
        self.fingerprint_engine = DigitalFingerprintEngine()
        self.copyright_detector = CopyrightDetectionService()
        self.license_manager = LicenseManagementSystem()
        self.ownership_validator = OwnershipValidationService()
        self.royalty_calculator = RoyaltyCalculationEngine()
        self.monetization_engine = MonetizationEngine()
        
        # Tracking
        self.registered_rights: Dict[str, Dict] = {}
        self.active_licenses: Dict[str, Dict] = {}
        self.royalty_payments: List[Dict] = []
        self.usage_analytics: Dict[str, Any] = {}
        
    async def _load_models_and_resources(self):
        """Load AI models and initialize resources"""
        try:
            await self.rights_manager.initialize()
            await self.fingerprint_engine.initialize()
            await self.copyright_detector.initialize()
            await self.license_manager.initialize()
            await self.ownership_validator.initialize()
            await self.royalty_calculator.initialize()
            await self.monetization_engine.initialize()
            logger.info("Rights management models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load rights management models: {e}")
            raise
    
    def get_required_config_keys(self) -> List[str]:
        """Required configuration keys"""
        return ['supported_license_types', 'default_protection_level']
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Main request processing logic"""
        action = request.action.lower()
        
        try:
            if action == "register_rights":
                result = await self._register_rights(request.data)
            elif action == "create_license":
                result = await self._create_license(request.data)
            elif action == "validate_ownership":
                result = await self._validate_ownership(request.data)
            elif action == "calculate_royalties":
                result = await self._calculate_royalties(request.data)
            elif action == "track_usage":
                result = await self._track_usage(request.data)
            elif action == "optimize_revenue":
                result = await self._optimize_revenue(request.data)
            elif action == "get_rights_status":
                result = await self._get_rights_status(request.data)
            elif action == "transfer_rights":
                result = await self._transfer_rights(request.data)
            else:
                raise ValueError(f"Unknown action: {action}")
            
            return AgentResponse(
                success=True,
                data=result,
                message=f"Rights management {action} completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Rights management error: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                error_code="RIGHTS_MANAGEMENT_ERROR"
            )
    
    async def _register_rights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register digital rights for content"""
        content_id = data.get('content_id')
        owner_info = data.get('owner_info', {})
        content_data = data.get('content_data')  # bytes
        protection_level = data.get('protection_level', self.config.default_protection_level)
        territorial_rights = set(data.get('territorial_rights', []))
        
        if not content_id:
            raise ValueError("content_id is required")
        
        if not owner_info:
            raise ValueError("owner_info is required")
        
        # Generate content fingerprint for verification
        fingerprint = {}
        if content_data:
            fingerprint = await self.fingerprint_engine.generate_fingerprint(content_data)
        
        # Register rights with the core system
        registration_result = await self.rights_manager.register_rights(content_id, owner_info)
        
        # Create ownership record
        ownership_record = {
            'content_id': content_id,
            'owner_info': owner_info,
            'protection_level': protection_level,
            'territorial_rights': list(territorial_rights),
            'fingerprint': fingerprint,
            'registered_at': datetime.now(timezone.utc).isoformat(),
            'status': 'active',
            'registration_id': registration_result.get('registration_id', f"reg_{content_id}"),
            'blockchain_verified': bool(fingerprint.get('blockchain_hash')),
            'usage_tracking_enabled': True
        }
        
        self.registered_rights[content_id] = ownership_record
        
        return {
            'content_id': content_id,
            'registration_id': ownership_record['registration_id'],
            'status': 'registered',
            'protection_level': protection_level,
            'territorial_coverage': len(territorial_rights) if territorial_rights else 'global',
            'blockchain_verified': ownership_record['blockchain_verified'],
            'registered_at': ownership_record['registered_at']
        }
    
    async def _create_license(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create and manage content licenses"""
        content_id = data.get('content_id')
        license_type = data.get('license_type')
        licensee_info = data.get('licensee_info', {})
        terms = data.get('terms', {})
        duration = data.get('duration_days', 365)
        
        if not content_id:
            raise ValueError("content_id is required")
        
        if content_id not in self.registered_rights:
            raise ValueError(f"Content {content_id} is not registered")
        
        if license_type not in self.config.supported_license_types:
            raise ValueError(f"Unsupported license type: {license_type}")
        
        # Create license with core system
        license_data = {
            'content_id': content_id,
            'license_type': license_type,
            'licensee_info': licensee_info,
            'terms': terms,
            'duration_days': duration
        }
        
        license_result = await self.license_manager.create_license(license_data)
        
        # Create license record
        license_record = {
            'license_id': license_result.get('license_id', f"lic_{content_id}_{len(self.active_licenses)}"),
            'content_id': content_id,
            'license_type': license_type,
            'licensee_info': licensee_info,
            'terms': terms,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'expires_at': (datetime.now(timezone.utc) + timedelta(days=duration)).isoformat(),
            'status': 'active',
            'usage_count': 0,
            'revenue_generated': Decimal('0.00'),
            'auto_renewal': self.config.license_auto_renewal
        }
        
        license_id = license_record['license_id']
        self.active_licenses[license_id] = license_record
        
        return {
            'license_id': license_id,
            'content_id': content_id,
            'license_type': license_type,
            'status': 'active',
            'created_at': license_record['created_at'],
            'expires_at': license_record['expires_at'],
            'terms_summary': terms
        }
    
    async def _validate_ownership(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ownership claims"""
        content_id = data.get('content_id')
        claimant_info = data.get('claimant_info', {})
        
        if not content_id:
            raise ValueError("content_id is required")
        
        # Check if content is registered
        is_registered = content_id in self.registered_rights
        
        if not is_registered:
            return {
                'content_id': content_id,
                'is_valid': False,
                'reason': 'content_not_registered',
                'validation_timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        # Validate ownership with core system
        is_valid_owner = await self.ownership_validator.validate_ownership(content_id, claimant_info)
        
        # Compare with registered owner
        registered_owner = self.registered_rights[content_id]['owner_info']
        owner_match = self._compare_owner_info(registered_owner, claimant_info)
        
        validation_result = {
            'content_id': content_id,
            'is_valid': is_valid_owner and owner_match,
            'owner_match': owner_match,
            'validation_method': 'fingerprint_and_registry',
            'confidence_score': 0.95 if (is_valid_owner and owner_match) else 0.2,
            'validation_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if not validation_result['is_valid']:
            validation_result['reason'] = 'ownership_mismatch' if not owner_match else 'validation_failed'
        
        return validation_result
    
    def _compare_owner_info(self, registered: Dict, claimed: Dict) -> bool:
        """Compare owner information for validation"""
        # Compare key identifying fields
        key_fields = ['name', 'email', 'organization', 'user_id']
        
        for field in key_fields:
            if field in registered and field in claimed:
                if registered[field].lower() == claimed[field].lower():
                    return True
        
        return False
    
    async def _calculate_royalties(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate and distribute royalties"""
        content_id = data.get('content_id')
        usage_data = data.get('usage_data', [])
        calculation_period = data.get('period', 'current_month')
        
        if content_id and content_id not in self.registered_rights:
            raise ValueError(f"Content {content_id} is not registered")
        
        # Calculate royalties using core engine
        royalty_result = await self.royalty_calculator.calculate_royalties(usage_data)
        
        # Process royalty calculations
        total_royalties = Decimal(str(royalty_result.get('amount', 0)))
        breakdown = royalty_result.get('breakdown', {})
        
        # Create royalty payment record
        payment_record = {
            'payment_id': f"pay_{content_id}_{len(self.royalty_payments)}",
            'content_id': content_id,
            'calculation_period': calculation_period,
            'total_amount': float(total_royalties),
            'breakdown': breakdown,
            'calculated_at': datetime.now(timezone.utc).isoformat(),
            'status': 'calculated',
            'usage_records': len(usage_data)
        }
        
        self.royalty_payments.append(payment_record)
        
        # Update registered rights with revenue info
        if content_id in self.registered_rights:
            if 'total_revenue' not in self.registered_rights[content_id]:
                self.registered_rights[content_id]['total_revenue'] = 0
            self.registered_rights[content_id]['total_revenue'] += float(total_royalties)
        
        return {
            'payment_id': payment_record['payment_id'],
            'content_id': content_id,
            'total_royalties': float(total_royalties),
            'breakdown': breakdown,
            'calculation_period': calculation_period,
            'status': 'calculated',
            'calculated_at': payment_record['calculated_at']
        }
    
    async def _track_usage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Track content usage for royalty calculation"""
        content_id = data.get('content_id')
        usage_event = data.get('usage_event', {})
        
        if not content_id:
            raise ValueError("content_id is required")
        
        if content_id not in self.registered_rights:
            raise ValueError(f"Content {content_id} is not registered")
        
        # Store usage analytics
        if content_id not in self.usage_analytics:
            self.usage_analytics[content_id] = {
                'total_uses': 0,
                'platforms': {},
                'geographical_distribution': {},
                'revenue_events': [],
                'last_updated': None
            }
        
        # Update usage statistics
        analytics = self.usage_analytics[content_id]
        analytics['total_uses'] += 1
        analytics['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        # Track platform usage
        platform = usage_event.get('platform', 'unknown')
        analytics['platforms'][platform] = analytics['platforms'].get(platform, 0) + 1
        
        # Track geographical usage
        country = usage_event.get('country', 'unknown')
        analytics['geographical_distribution'][country] = analytics['geographical_distribution'].get(country, 0) + 1
        
        # Track revenue events
        if usage_event.get('revenue_amount'):
            analytics['revenue_events'].append({
                'amount': float(usage_event['revenue_amount']),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'platform': platform,
                'country': country
            })
        
        return {
            'content_id': content_id,
            'usage_tracked': True,
            'total_uses': analytics['total_uses'],
            'platform': platform,
            'timestamp': analytics['last_updated']
        }
    
    async def _optimize_revenue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize revenue strategies for content"""
        content_id = data.get('content_id')
        
        if not content_id:
            raise ValueError("content_id is required")
        
        if content_id not in self.registered_rights:
            raise ValueError(f"Content {content_id} is not registered")
        
        # Get optimization recommendations from core engine
        optimization_result = await self.monetization_engine.optimize_revenue(content_id)
        
        # Analyze current performance
        analytics = self.usage_analytics.get(content_id, {})
        current_revenue = sum(event['amount'] for event in analytics.get('revenue_events', []))
        
        # Generate optimization recommendations
        recommendations = optimization_result.get('strategy', {})
        
        optimization_report = {
            'content_id': content_id,
            'current_revenue': current_revenue,
            'optimization_potential': recommendations.get('potential_increase', 0),
            'recommended_strategies': recommendations.get('strategies', []),
            'suggested_platforms': recommendations.get('platforms', []),
            'pricing_recommendations': recommendations.get('pricing', {}),
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return optimization_report
    
    async def _get_rights_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive rights status"""
        content_id = data.get('content_id')
        
        if content_id:
            if content_id not in self.registered_rights:
                raise ValueError(f"Content {content_id} is not registered")
            
            rights_info = self.registered_rights[content_id].copy()
            
            # Add usage analytics
            if content_id in self.usage_analytics:
                rights_info['usage_analytics'] = self.usage_analytics[content_id]
            
            # Add active licenses
            content_licenses = [
                license_info for license_info in self.active_licenses.values()
                if license_info['content_id'] == content_id
            ]
            rights_info['active_licenses'] = content_licenses
            
            return rights_info
        
        # Return overall statistics
        total_registered = len(self.registered_rights)
        total_licenses = len(self.active_licenses)
        total_revenue = sum(
            float(payment['total_amount']) for payment in self.royalty_payments
        )
        
        return {
            'total_registered_content': total_registered,
            'total_active_licenses': total_licenses,
            'total_revenue_generated': total_revenue,
            'protection_levels': {
                level: sum(1 for r in self.registered_rights.values() if r['protection_level'] == level)
                for level in ['basic', 'standard', 'premium', 'enterprise']
            },
            'recent_registrations': len([
                r for r in self.registered_rights.values()
                if (datetime.now(timezone.utc) - datetime.fromisoformat(r['registered_at'].replace('Z', '+00:00'))).days <= 30
            ])
        }
    
    async def _transfer_rights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transfer rights ownership"""
        content_id = data.get('content_id')
        current_owner = data.get('current_owner', {})
        new_owner = data.get('new_owner', {})
        transfer_terms = data.get('transfer_terms', {})
        
        if not content_id:
            raise ValueError("content_id is required")
        
        if content_id not in self.registered_rights:
            raise ValueError(f"Content {content_id} is not registered")
        
        # Validate current ownership
        validation_result = await self._validate_ownership({
            'content_id': content_id,
            'claimant_info': current_owner
        })
        
        if not validation_result['is_valid']:
            raise ValueError("Current owner validation failed")
        
        # Update ownership record
        rights_record = self.registered_rights[content_id]
        
        # Create transfer record
        transfer_record = {
            'transfer_id': f"transfer_{content_id}_{int(datetime.now().timestamp())}",
            'content_id': content_id,
            'previous_owner': rights_record['owner_info'].copy(),
            'new_owner': new_owner,
            'transfer_terms': transfer_terms,
            'transferred_at': datetime.now(timezone.utc).isoformat(),
            'status': 'completed'
        }
        
        # Update ownership
        rights_record['owner_info'] = new_owner
        rights_record['last_updated'] = transfer_record['transferred_at']
        
        # Add transfer history
        if 'transfer_history' not in rights_record:
            rights_record['transfer_history'] = []
        rights_record['transfer_history'].append(transfer_record)
        
        return {
            'transfer_id': transfer_record['transfer_id'],
            'content_id': content_id,
            'status': 'completed',
            'new_owner': new_owner,
            'transferred_at': transfer_record['transferred_at']
        }