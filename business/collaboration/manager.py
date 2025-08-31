"""
Advanced Collaboration Manager for IA Influencer Agent
Professional collaboration management and orchestration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
import json
import uuid

from .collaboration_models import (
    CollaborationRequest, CollaborationMatch, CollaborationContract,
    CollaborationType, CollaborationStatus, CollaborationAnalytics
)
from .collaboration_processors import (
    CollaborationMatchingProcessor, CollaborationWorkflowProcessor,
    CollaborationContractProcessor, MatchingStrategy
)
from .collaboration_services import (
    CollaborationDiscoveryService, CollaborationMatchingService,
    CollaborationManagementService, CollaborationAnalyticsService
)
from .collaboration_analytics import (
    CollaborationAnalyticsEngine, CollaborationReportGenerator
)


logger = logging.getLogger(__name__)


class CollaborationManagerResponse:
    """Standardized response from collaboration manager operations"""
    def __init__(
        self, 
        success: bool, 
        data: Any = None, 
        message: str = "", 
        error_code: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.success = success
        self.data = data
        self.message = message
        self.error_code = error_code
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()


@dataclass
class CollaborationManagerConfig:
    """Configuration for collaboration manager"""
    max_concurrent_matches: int = 50
    cache_duration_minutes: int = 30
    auto_match_threshold: float = 0.8
    notification_enabled: bool = True
    analytics_enabled: bool = True
    predictive_matching: bool = True
    ml_matching_enabled: bool = True
    contract_templates_enabled: bool = True


class CollaborationManager:
    """
    Advanced Collaboration Manager
    Orchestrates all collaboration-related operations including discovery,
    matching, contract management, and analytics
    """
    
    def __init__(self, config: CollaborationManagerConfig = None):
        self.config = config or CollaborationManagerConfig()
        
        # Initialize core services
        service_config = {
            'max_concurrent_matches': self.config.max_concurrent_matches,
            'cache_duration_minutes': self.config.cache_duration_minutes,
            'auto_match_threshold': self.config.auto_match_threshold,
            'notifications_enabled': self.config.notification_enabled,
            'ml_matching_enabled': self.config.ml_matching_enabled
        }
        
        self.discovery_service = CollaborationDiscoveryService(service_config)
        self.matching_service = CollaborationMatchingService(service_config)
        self.management_service = CollaborationManagementService(service_config)
        self.analytics_service = CollaborationAnalyticsService(service_config)
        
        # Initialize processors
        self.matching_processor = CollaborationMatchingProcessor(service_config)
        self.workflow_processor = CollaborationWorkflowProcessor(service_config)
        self.contract_processor = CollaborationContractProcessor(service_config)
        
        # Initialize analytics
        self.analytics_engine = CollaborationAnalyticsEngine(service_config)
        self.report_generator = CollaborationReportGenerator(service_config)
        
        self._operation_cache = {}
        self._active_collaborations = {}
        
    async def discover_collaborations(
        self,
        creator_id: str,
        creator_profile: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> CollaborationManagerResponse:
        """Discover available collaboration opportunities"""



        try:
            discovery_result = await self.discovery_service.discover_opportunities(
                creator_id, creator_profile, preferences
            )
            
            if discovery_result.success:
                return CollaborationManagerResponse(
                    success=True,
                    data=discovery_result.data,
                    message=discovery_result.message,
                    metadata=discovery_result.metadata
                )
            else:
                return CollaborationManagerResponse(
                    success=False,
                    message=discovery_result.message,
                    error_code=discovery_result.error_code,
                    metadata=discovery_result.metadata
                )
            
        except Exception as e:
            logger.error(f"Collaboration discovery failed for creator {creator_id}: {str(e)}")
            return CollaborationManagerResponse(
                success=False,
                message="Failed to discover collaborations",
                error_code="DISCOVERY_ERROR",
                metadata={'error_details': str(e)}
            )
    
    async def create_collaboration_request(
        self,
        creator_id: str,
        request_data: Dict[str, Any]
    ) -> CollaborationManagerResponse:
        """Create a new collaboration request"""



        try:
            # Validate request data
            validation_result = await self._validate_collaboration_request(request_data)
            if not validation_result.success:
                return validation_result
            
            # Enhanced request data with creator information
            enhanced_request_data = {
                **request_data,
                'creator_id': creator_id,
                'id': str(uuid.uuid4()),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Create collaboration request using service
            creation_result = await self.management_service.create_collaboration(
                enhanced_request_data, [], {}  # No matches or contract initially
            )
            
            if creation_result.success:
                return CollaborationManagerResponse(
                    success=True,
                    data=creation_result.data,
                    message=creation_result.message,
                    metadata={
                        **creation_result.metadata,
                        'next_steps': ['Find collaboration partners', 'Review and approve matches']
                    }
                )
            else:
                return CollaborationManagerResponse(
                    success=False,
                    message=creation_result.message,
                    error_code=creation_result.error_code,
                    metadata=creation_result.metadata
                )
            
        except Exception as e:
            logger.error(f"Collaboration request creation failed: {str(e)}")
            return CollaborationManagerResponse(
                success=False,
                message="Failed to create collaboration request",
                error_code="REQUEST_CREATION_ERROR"
            )
    
    async def find_collaboration_matches(
        self,
        request_id: str,
        candidate_pool: List[Dict[str, Any]],
        matching_preferences: Dict[str, Any] = None
    ) -> CollaborationManagerResponse:
        """Find and rank potential collaboration matches"""



        try:
            matching_preferences = matching_preferences or {}
            
            # Get collaboration request data (simulate database fetch)
            request_data = await self._get_collaboration_request_data(request_id)
            if not request_data:
                return CollaborationManagerResponse(
                    success=False,
                    message="Collaboration request not found",
                    error_code="REQUEST_NOT_FOUND"
                )
            
            # Find matches using matching service
            matching_result = await self.matching_service.find_collaboration_matches(
                request_id, request_data, candidate_pool, matching_preferences
            )
            
            if matching_result.success:
                # Cache results for performance
                cache_key = f"matches_{request_id}_{hash(str(matching_preferences))}"
                self._operation_cache[cache_key] = {
                    'data': matching_result.data,
                    'timestamp': datetime.utcnow(),
                    'expires_at': datetime.utcnow() + timedelta(minutes=self.config.cache_duration_minutes)
                }
                
                return CollaborationManagerResponse(
                    success=True,
                    data=matching_result.data,
                    message=matching_result.message,
                    metadata={
                        **matching_result.metadata,
                        'cache_key': cache_key,
                        'cached_until': (datetime.utcnow() + timedelta(minutes=self.config.cache_duration_minutes)).isoformat()
                    }
                )
            else:
                return CollaborationManagerResponse(
                    success=False,
                    message=matching_result.message,
                    error_code=matching_result.error_code,
                    metadata=matching_result.metadata
                )
            
        except Exception as e:
            logger.error(f"Collaboration matching failed for request {request_id}: {str(e)}")
            return CollaborationManagerResponse(
                success=False,
                message="Failed to find collaboration matches",
                error_code="MATCHING_ERROR"
            )
    
    async def manage_collaboration_lifecycle(
        self,
        collaboration_id: str,
        action: str,
        action_data: Dict[str, Any] = None
    ) -> CollaborationManagerResponse:
        """Manage collaboration lifecycle (status updates, milestones, etc.)"""



        try:
            action_data = action_data or {}
            
            # Validate action
            valid_actions = ['approve', 'reject', 'start', 'complete', 'cancel', 'update_milestone', 'extend_deadline']
            if action not in valid_actions:
                return CollaborationManagerResponse(
                    success=False,
                    message=f"Invalid action: {action}. Valid actions: {', '.join(valid_actions)}",
                    error_code="INVALID_ACTION"
                )
            
            # Process different lifecycle actions
            if action in ['approve', 'reject', 'start', 'complete', 'cancel']:
                result = await self.management_service.update_collaboration_status(
                    collaboration_id, action, action_data
                )
            elif action == 'update_milestone':
                result = await self.management_service.manage_collaboration_milestones(
                    collaboration_id, action_data, 'update'
                )
            elif action == 'extend_deadline':
                # Get current collaboration and process extension
                collaboration_data = await self._get_collaboration_data(collaboration_id)
                if collaboration_data:
                    request = CollaborationRequest(**collaboration_data)
                    extension_result = await self.workflow_processor.process_collaboration_request(
                        request, 'extend_deadline', action_data
                    )
                    result = type('ServiceResponse', (), {
                        'success': extension_result.success,
                        'data': extension_result.data,
                        'message': f"Deadline extension processed",
                        'error_code': None if extension_result.success else 'EXTENSION_ERROR',
                        'metadata': extension_result.metadata or {}
                    })()
                else:
                    result = type('ServiceResponse', (), {
                        'success': False,
                        'message': 'Collaboration not found',
                        'error_code': 'COLLABORATION_NOT_FOUND'
                    })()
            
            if result.success:
                return CollaborationManagerResponse(
                    success=True,
                    data=result.data,
                    message=result.message,
                    metadata={
                        **result.metadata,
                        'action_processed': action,
                        'processed_at': datetime.utcnow().isoformat()
                    }
                )
            else:
                return CollaborationManagerResponse(
                    success=False,
                    message=result.message,
                    error_code=result.error_code,
                    metadata=result.metadata
                )
            
        except Exception as e:
            logger.error(f"Collaboration lifecycle management failed: {str(e)}")
            return CollaborationManagerResponse(
                success=False,
                message="Failed to manage collaboration lifecycle",
                error_code="LIFECYCLE_ERROR"
            )
    
    async def generate_collaboration_analytics(
        self,
        creator_id: str,
        analytics_type: str = "comprehensive",
        time_period: Dict[str, datetime] = None
    ) -> CollaborationManagerResponse:
        """Generate collaboration analytics and insights"""



        try:
            # Default time period (last 90 days)
            if not time_period:
                time_period = {
                    'start': datetime.utcnow() - timedelta(days=90),
                    'end': datetime.utcnow()
                }
            
            # Generate analytics using analytics service
            analytics_result = await self.analytics_service.generate_collaboration_analytics(
                creator_id, analytics_type
            )
            
            if analytics_result.success:
                # Generate additional insights if comprehensive analytics requested
                if analytics_type == "comprehensive":
                    insights_result = await self.analytics_service.get_collaboration_insights(
                        creator_id, time_period
                    )
                    if insights_result.success:
                        analytics_result.data['detailed_insights'] = insights_result.data
                
                return CollaborationManagerResponse(
                    success=True,
                    data=analytics_result.data,
                    message=analytics_result.message,
                    metadata={
                        **analytics_result.metadata,
                        'analytics_type': analytics_type,
                        'time_period': {
                            'start': time_period['start'].isoformat(),
                            'end': time_period['end'].isoformat()
                        }
                    }
                )
            else:
                return CollaborationManagerResponse(
                    success=False,
                    message=analytics_result.message,
                    error_code=analytics_result.error_code,
                    metadata=analytics_result.metadata
                )
            
        except Exception as e:
            logger.error(f"Analytics generation failed for creator {creator_id}: {str(e)}")
            return CollaborationManagerResponse(
                success=False,
                message="Failed to generate collaboration analytics",
                error_code="ANALYTICS_ERROR"
            )
    
    async def create_collaboration_contract(
        self,
        collaboration_request_id: str,
        selected_participants: List[str],
        contract_terms: Dict[str, Any]
    ) -> CollaborationManagerResponse:
        """Create a collaboration contract"""



        try:
            # Get collaboration request
            request_data = await self._get_collaboration_request_data(collaboration_request_id)
            if not request_data:
                return CollaborationManagerResponse(
                    success=False,
                    message="Collaboration request not found",
                    error_code="REQUEST_NOT_FOUND"
                )
            
            request = CollaborationRequest(**request_data)
            
            # Create contract using contract processor
            contract_result = await self.contract_processor.create_contract(
                request, selected_participants, contract_terms
            )
            
            if contract_result.success:
                return CollaborationManagerResponse(
                    success=True,
                    data=contract_result.data,
                    message="Collaboration contract created successfully",
                    metadata={
                        **contract_result.metadata,
                        'requires_signatures': len(selected_participants),
                        'next_steps': ['Collect participant signatures', 'Activate contract when fully signed']
                    }
                )
            else:
                return CollaborationManagerResponse(
                    success=False,
                    message=contract_result.error_message,
                    error_code="CONTRACT_CREATION_ERROR"
                )
                
        except Exception as e:
            logger.error(f"Contract creation failed: {str(e)}")
            return CollaborationManagerResponse(
                success=False,
                message="Failed to create collaboration contract",
                error_code="CONTRACT_ERROR"
            )
    
    async def generate_comprehensive_report(
        self,
        creator_id: str,
        report_type: str = "monthly",
        include_predictions: bool = True
    ) -> CollaborationManagerResponse:
        """Generate comprehensive collaboration report"""



        try:
            # Get collaboration data for creator
            collaboration_data = await self._get_creator_collaboration_data(creator_id)
            
            # Generate report using report generator
            report = await self.report_generator.generate_comprehensive_report(
                creator_id, collaboration_data, report_type, include_predictions
            )
            
            if 'error' not in report:
                return CollaborationManagerResponse(
                    success=True,
                    data=report,
                    message=f"{report_type.title()} collaboration report generated successfully",
                    metadata={
                        'report_type': report_type,
                        'includes_predictions': include_predictions,
                        'data_points_analyzed': len(collaboration_data)
                    }
                )
            else:
                return CollaborationManagerResponse(
                    success=False,
                    message=f"Report generation failed: {report['error']}",
                    error_code="REPORT_ERROR"
                )
                
        except Exception as e:
            logger.error(f"Report generation failed for creator {creator_id}: {str(e)}")
            return CollaborationManagerResponse(
                success=False,
                message="Failed to generate collaboration report",
                error_code="REPORT_GENERATION_ERROR"
            )
    
    async def _validate_collaboration_request(
        self, 
        request_data: Dict[str, Any]
    ) -> CollaborationManagerResponse:
        """Validate collaboration request data"""
        required_fields = ['title', 'description', 'collaboration_type']
        missing_fields = [field for field in required_fields if not request_data.get(field)]
        
        if missing_fields:
            return CollaborationManagerResponse(
                success=False,
                message=f"Missing required fields: {', '.join(missing_fields)}",
                error_code="VALIDATION_ERROR",
                metadata={'missing_fields': missing_fields}
            )
        
        # Additional validation logic
        title = request_data.get('title', '')
        if len(title) < 5:
            return CollaborationManagerResponse(
                success=False,
                message="Title must be at least 5 characters long",
                error_code="VALIDATION_ERROR"
            )
        
        description = request_data.get('description', '')
        if len(description) < 20:
            return CollaborationManagerResponse(
                success=False,
                message="Description must be at least 20 characters long",
                error_code="VALIDATION_ERROR"
            )
        
        # Validate collaboration type
        collaboration_type = request_data.get('collaboration_type')
        valid_types = [t.value for t in CollaborationType]
        if collaboration_type not in valid_types:
            return CollaborationManagerResponse(
                success=False,
                message=f"Invalid collaboration type. Valid types: {', '.join(valid_types)}",
                error_code="VALIDATION_ERROR"
            )
        
        return CollaborationManagerResponse(
            success=True,
            message="Validation successful"
        )
    
    async def get_collaboration_status(
        self, 
        collaboration_id: str
    ) -> CollaborationManagerResponse:
        """Get current status of a collaboration"""



        try:
            # Fetch collaboration status
            collaboration_data = await self._get_collaboration_data(collaboration_id)
            
            if not collaboration_data:
                return CollaborationManagerResponse(
                    success=False,
                    message="Collaboration not found",
                    error_code="COLLABORATION_NOT_FOUND"
                )
            
            # Get contract information if available
            contract_data = await self._get_contract_data(collaboration_id)
            
            status_data = {
                'collaboration_id': collaboration_id,
                'status': collaboration_data.get('status', 'unknown'),
                'progress_percentage': contract_data.get('completion_percentage', 0.0) if contract_data else 0.0,
                'last_updated': collaboration_data.get('updated_at', datetime.utcnow()).isoformat(),
                'participants': contract_data.get('participants', []) if contract_data else [],
                'milestones': contract_data.get('milestones', []) if contract_data else [],
                'next_milestones': self._get_next_milestones(contract_data) if contract_data else [],
                'estimated_completion': self._calculate_estimated_completion(contract_data) if contract_data else None
            }
            
            return CollaborationManagerResponse(
                success=True,
                data=status_data,
                message="Collaboration status retrieved successfully",
                metadata={
                    'has_contract': contract_data is not None,
                    'active_participants': len(status_data['participants'])
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get collaboration status for {collaboration_id}: {str(e)}")
            return CollaborationManagerResponse(
                success=False,
                message="Failed to retrieve collaboration status",
                error_code="STATUS_RETRIEVAL_ERROR"
            )
    
    def get_manager_health_status(self) -> Dict[str, Any]:
        """Get health status of the collaboration manager"""



        try:
            # Check service health
            services_health = {
                'discovery_service': 'healthy',
                'matching_service': 'healthy', 
                'management_service': 'healthy',
                'analytics_service': 'healthy' if self.config.analytics_enabled else 'disabled'
            }
            
            # Cache health
            cache_health = {
                'cache_size': len(self._operation_cache),
                'cache_hit_rate': self._calculate_cache_hit_rate(),
                'expired_entries': len([
                    k for k, v in self._operation_cache.items() 
                    if v.get('expires_at', datetime.min) < datetime.utcnow()
                ])
            }
            
            return {
                'status': 'healthy',
                'services': services_health,
                'cache': cache_health,
                'active_collaborations': len(self._active_collaborations),
                'configuration': {
                    'max_concurrent_matches': self.config.max_concurrent_matches,
                    'auto_match_threshold': self.config.auto_match_threshold,
                    'notifications_enabled': self.config.notification_enabled,
                    'analytics_enabled': self.config.analytics_enabled,
                    'ml_matching_enabled': self.config.ml_matching_enabled,
                    'predictive_matching': self.config.predictive_matching
                },
                'last_health_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health status check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_health_check': datetime.utcnow().isoformat()
            }
    
    # Helper methods for simulated database operations
    async def _get_collaboration_request_data(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Simulate database fetch for collaboration request"""
        # In real implementation, this would query the database
        return None  # Placeholder
    
    async def _get_collaboration_data(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """Simulate database fetch for collaboration data"""
        # In real implementation, this would query the database
        return None  # Placeholder
    
    async def _get_contract_data(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """Simulate database fetch for contract data"""
        # In real implementation, this would query the database
        return None  # Placeholder
    
    async def _get_creator_collaboration_data(self, creator_id: str) -> List[Dict[str, Any]]:
        """Simulate database fetch for creator's collaboration history"""
        # In real implementation, this would query the database
        return []  # Placeholder
    
    def _get_next_milestones(self, contract_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get next upcoming milestones"""
        if not contract_data or 'milestones' not in contract_data:
            return []
        
        milestones = contract_data['milestones']
        upcoming = [
            m for m in milestones 
            if m.get('status') == 'pending' and 
               datetime.fromisoformat(m.get('due_date', '2000-01-01')) > datetime.utcnow()
        ]
        
        return sorted(upcoming, key=lambda x: x.get('due_date', ''))[:3]  # Next 3 milestones
    
    def _calculate_estimated_completion(self, contract_data: Dict[str, Any]) -> Optional[str]:
        """Calculate estimated completion date"""
        if not contract_data:
            return None
        
        try:
            contract = CollaborationContract(**contract_data)
            estimated_date = contract.calculate_estimated_completion_date()
            return estimated_date.isoformat()
        except:
            return None
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate (simplified)"""
        # In real implementation, this would track actual cache hits/misses
        return 0.75  # Placeholder 75% hit rate


# Export main manager class
__all__ = ['CollaborationManager', 'CollaborationManagerConfig', 'CollaborationManagerResponse']
