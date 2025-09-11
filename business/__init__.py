"""
Business Logic Module for Ainflue Platform
===========================================

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue - AI-Powered Content Protection and Monetization Platform
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module contains core business logic and models for the Ainflue platform.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Business Models and Rules
class BusinessRule:
    """Base class for business rules"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def apply(self, data: Dict[str, Any]) -> bool:
        """Apply business rule to data"""
        return True

class MonetizationRule(BusinessRule):
    """Business rules for monetization"""
    def __init__(self):
        super().__init__("monetization", "Core monetization business rules")
    
    def apply(self, transaction_data: Dict[str, Any]) -> bool:
        """Apply monetization rules"""
        try:
            # Basic validation
            required_fields = ['amount', 'currency', 'creator_id']
            for field in required_fields:
                if field not in transaction_data:
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Amount validation
            amount = transaction_data.get('amount', 0)
            if not isinstance(amount, (int, float)) or amount <= 0:
                logger.warning(f"Invalid amount: {amount}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error applying monetization rule: {e}")
            return False

class CreatorBusinessLogic:
    """Business logic for creator operations"""
    
    @staticmethod
    def validate_creator_profile(profile_data: Dict[str, Any]) -> bool:
        """Validate creator profile data"""
        try:
            required_fields = ['name', 'email', 'content_type']
            for field in required_fields:
                if field not in profile_data:
                    return False
            
            # Email validation
            email = profile_data.get('email', '')
            if '@' not in email or '.' not in email:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating creator profile: {e}")
            return False
    
    @staticmethod
    def calculate_revenue_share(total_amount: float, creator_percentage: float = 0.7) -> Dict[str, float]:
        """Calculate revenue sharing between creator and platform"""
        try:
            creator_share = total_amount * creator_percentage
            platform_share = total_amount * (1 - creator_percentage)
            
            return {
                'creator_share': round(creator_share, 2),
                'platform_share': round(platform_share, 2),
                'total_amount': total_amount
            }
        except Exception as e:
            logger.error(f"Error calculating revenue share: {e}")
            return {'creator_share': 0.0, 'platform_share': 0.0, 'total_amount': 0.0}

class ContentBusinessLogic:
    """Business logic for content operations"""
    
    @staticmethod
    def validate_content_metadata(metadata: Dict[str, Any]) -> bool:
        """Validate content metadata"""
        try:
            required_fields = ['title', 'content_type', 'creator_id']
            for field in required_fields:
                if field not in metadata:
                    return False
            
            # Content type validation
            valid_types = ['audio', 'video', 'image', 'text', 'podcast', 'music']
            if metadata.get('content_type') not in valid_types:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating content metadata: {e}")
            return False

# Business Services
class BusinessService:
    """Main business service coordinator"""
    
    def __init__(self):
        self.monetization_rule = MonetizationRule()
        self.creator_logic = CreatorBusinessLogic()
        self.content_logic = ContentBusinessLogic()
        
        logger.info("Business service initialized successfully")
    
    def process_monetization_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process monetization request with business rules"""
        try:
            # Apply business rules
            if not self.monetization_rule.apply(request_data):
                return {
                    'success': False,
                    'error': 'Monetization rules validation failed',
                    'data': None
                }
            
            # Calculate revenue sharing if applicable
            amount = request_data.get('amount', 0)
            revenue_share = self.creator_logic.calculate_revenue_share(amount)
            
            return {
                'success': True,
                'data': {
                    'original_request': request_data,
                    'revenue_breakdown': revenue_share,
                    'approved': True
                }
            }
        except Exception as e:
            logger.error(f"Error processing monetization request: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }

# Global business service instance
business_service = BusinessService()

# Export main components
__all__ = [
    'BusinessRule',
    'MonetizationRule', 
    'CreatorBusinessLogic',
    'ContentBusinessLogic',
    'BusinessService',
    'business_service'
]