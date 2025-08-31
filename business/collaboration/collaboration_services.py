"""Advanced Collaboration Services for IA Influencer Agent
Professional business logic services for collaboration management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass, field
import json
from enum import Enum
import uuid
from collections import defaultdict

from .collaboration_models import (
    CollaborationRequest, CollaborationMatch, CollaborationContract,
    CollaborationAnalytics, CollaborationNotification,
    CollaborationType, CollaborationStatus, SkillLevel
)
from .collaboration_processors import (
    CollaborationMatchingProcessor, CollaborationWorkflowProcessor,
    CollaborationContractProcessor, MatchingStrategy, ProcessingResult
)


logger = logging.getLogger(__name__)


class ServiceResponse:
    """Standardized service response"""
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


class CollaborationDiscoveryService:
    """Service for discovering and managing collaboration opportunities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.matching_processor = CollaborationMatchingProcessor(config)
        self.cache_duration = self.config.get('cache_duration_hours', 24)
        self._discovery_cache = {}
        
    async def discover_opportunities(
        self,
        creator_id: str,
        creator_profile: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> ServiceResponse:
        """Discover collaboration opportunities for a creator"""
        try:
            preferences = preferences or {}
            
            # Check cache first
            cache_key = f"discovery_{creator_id}_{hash(str(preferences))}"
            cached_result = self._get_cached_discovery(cache_key)
            if cached_result:
                return ServiceResponse(
                    success=True,
                    data=cached_result,
                    message="Opportunities retrieved from cache",
                    metadata={'source': 'cache', 'cached_at': cached_result.get('cached_at')}
                )
            
            # Get active collaboration requests
            active_requests = await self._get_active_requests(creator_id, preferences)
            
            if not active_requests:
                return ServiceResponse(
                    success=True,
                    data=[],
                    message="No collaboration opportunities found at this time"
                )
            
            # Find matches using different strategies
            all_opportunities = []
            
            for request in active_requests:
                matching_result = await self.matching_processor.find_matches(
                    request,
                    [creator_profile],
                    strategy=MatchingStrategy.HYBRID_INTELLIGENT
                )
                
                if matching_result.success and matching_result.data:
                    for match in matching_result.data:
                        opportunity = {
                            'collaboration_id': request.id,
                            'title': request.title,
                            'description': request.description,
                            'collaboration_type': request.collaboration_type.value,
                            'creator_id': request.creator_id,
                            'compatibility_score': match.compatibility_score,
                            'priority_score': match.priority_score,
                            'skill_matches': match.skill_matches,
                            'budget_range': request.budget_range,
                            'timeline': request.timeline,
                            'remote_allowed': request.remote_work_allowed,
                            'location_match': match.location_match,
                            'language_match': match.language_match,
                            'created_at': request.created_at.isoformat(),
                            'expires_at': request.expires_at.isoformat() if request.expires_at else None,
                            'match_quality': self._assess_match_quality(match),
                            'estimated_duration': self._estimate_collaboration_duration(request),
                            'complexity_level': self._assess_complexity_level(request)
                        }
                        all_opportunities.append(opportunity)
            
            # Sort by priority score and compatibility
            all_opportunities.sort(
                key=lambda x: (x['priority_score'], x['compatibility_score']), 
                reverse=True
            )
            
            # Limit results based on preferences
            max_results = preferences.get('max_results', 20)
            filtered_opportunities = all_opportunities[:max_results]
            
            # Apply additional filters
            if preferences.get('min_compatibility_score'):
                min_score = preferences['min_compatibility_score']
                filtered_opportunities = [
                    opp for opp in filtered_opportunities 
                    if opp['compatibility_score'] >= min_score
                ]
            
            # Cache results
            cache_data = {
                'opportunities': filtered_opportunities,
                'total_found': len(all_opportunities),
                'filtered_count': len(filtered_opportunities),
                'cached_at': datetime.utcnow().isoformat(),
                'preferences_applied': preferences
            }
            self._cache_discovery(cache_key, cache_data)
            
            return ServiceResponse(
                success=True,
                data=cache_data,
                message=f"Found {len(filtered_opportunities)} collaboration opportunities",
                metadata={
                    'total_requests_analyzed': len(active_requests),
                    'strategies_used': ['hybrid_intelligent'],
                    'cache_key': cache_key
                }
            )
            
        except Exception as e:
            logger.error(f"Discovery service failed for creator {creator_id}: {str(e)}")
            return ServiceResponse(
                success=False,
                message="Failed to discover collaboration opportunities",
                error_code="DISCOVERY_ERROR",
                metadata={'error_details': str(e)}
            )
    
    async def get_collaboration_recommendations(
        self,
        creator_id: str,
        collaboration_history: List[Dict[str, Any]],
        success_patterns: Dict[str, Any] = None
    ) -> ServiceResponse:
        """Get personalized collaboration recommendations based on history"""
        try:
            if not collaboration_history:
                return await self.discover_opportunities(creator_id, {})
            
            # Analyze success patterns
            patterns = success_patterns or self._analyze_success_patterns(collaboration_history)
            
            # Generate recommendations based on patterns
            recommendations = []
            
            # Recommend similar successful collaboration types
            successful_types = patterns.get('successful_types', [])
            for collab_type in successful_types:
                type_recommendations = await self._get_recommendations_by_type(
                    creator_id, collab_type, patterns
                )
                recommendations.extend(type_recommendations)
            
            # Recommend collaborations with similar creators
            successful_creator_profiles = patterns.get('successful_creator_profiles', [])
            for profile_pattern in successful_creator_profiles:
                similar_recommendations = await self._get_recommendations_by_creator_similarity(
                    creator_id, profile_pattern
                )
                recommendations.extend(similar_recommendations)
            
            # Remove duplicates and sort
            unique_recommendations = self._deduplicate_recommendations(recommendations)
            unique_recommendations.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
            
            return ServiceResponse(
                success=True,
                data={
                    'recommendations': unique_recommendations[:15],  # Top 15
                    'success_patterns': patterns,
                    'total_analyzed': len(collaboration_history),
                    'recommendation_basis': 'historical_success_patterns'
                },
                message=f"Generated {len(unique_recommendations)} personalized recommendations"
            )
            
        except Exception as e:
            logger.error(f"Recommendation service failed for creator {creator_id}: {str(e)}")
            return ServiceResponse(
                success=False,
                message="Failed to generate recommendations",
                error_code="RECOMMENDATION_ERROR"
            )
    
    def _analyze_success_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze collaboration history for success patterns"""
        successful_collaborations = [
            collab for collab in history 
            if collab.get('status') == 'completed' and 
               collab.get('satisfaction_score', 0) >= 0.7
        ]
        
        if not successful_collaborations:
            return {}
        
        # Analyze patterns
        type_counts = defaultdict(int)
        creator_profiles = []
        budget_ranges = []
        duration_patterns = []
        
        for collab in successful_collaborations:
            type_counts[collab.get('collaboration_type')] += 1
            
            if collab.get('partner_profile'):
                creator_profiles.append(collab['partner_profile'])
            
            if collab.get('budget_range'):
                budget_ranges.append(collab['budget_range'])
            
            if collab.get('duration_days'):
                duration_patterns.append(collab['duration_days'])
        
        # Calculate patterns
        most_successful_types = sorted(
            type_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        return {
            'successful_types': [t[0] for t in most_successful_types],
            'successful_creator_profiles': creator_profiles,
            'preferred_budget_ranges': budget_ranges,
            'optimal_durations': duration_patterns,
            'success_rate': len(successful_collaborations) / len(history),
            'analysis_date': datetime.utcnow().isoformat()
        }


class CollaborationMatchingService:
    """Service for advanced collaboration matching and pairing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.matching_processor = CollaborationMatchingProcessor(config)
        self.match_cache = {}
        
    async def find_collaboration_matches(
        self,
        request_id: str,
        request_data: Dict[str, Any],
        candidate_pool: List[Dict[str, Any]],
        matching_options: Dict[str, Any] = None
    ) -> ServiceResponse:
        """Find and rank collaboration matches"""
        try:
            matching_options = matching_options or {}
            
            # Create collaboration request object
            request = CollaborationRequest(**request_data)
            
            # Determine matching strategy
            strategy = MatchingStrategy(
                matching_options.get('strategy', 'hybrid_intelligent')
            )
            
            # Perform matching
            matching_result = await self.matching_processor.find_matches(
                request, candidate_pool, strategy
            )
            
            if not matching_result.success:
                return ServiceResponse(
                    success=False,
                    message="Matching process failed",
                    error_code="MATCHING_ERROR",
                    metadata={'error_details': matching_result.error_message}
                )
            
            matches = matching_result.data or []
            
            # Enhance matches with additional information
            enhanced_matches = []
            for match in matches:
                enhanced_match = await self._enhance_match_data(match, candidate_pool)
                enhanced_matches.append(enhanced_match)
            
            # Apply post-processing filters
            filtered_matches = self._apply_matching_filters(enhanced_matches, matching_options)
            
            # Generate matching insights
            insights = self._generate_matching_insights(request, filtered_matches)
            
            return ServiceResponse(
                success=True,
                data={
                    'matches': filtered_matches,
                    'total_candidates_analyzed': len(candidate_pool),
                    'qualified_matches': len(filtered_matches),
                    'matching_strategy': strategy.value,
                    'insights': insights,
                    'processing_time': matching_result.processing_time
                },
                message=f"Found {len(filtered_matches)} qualified matches"
            )
            
        except Exception as e:
            logger.error(f"Matching service failed for request {request_id}: {str(e)}")
            return ServiceResponse(
                success=False,
                message="Collaboration matching failed",
                error_code="MATCHING_SERVICE_ERROR"
            )
    
    async def validate_collaboration_feasibility(
        self,
        collaboration_data: Dict[str, Any],
        participants: List[Dict[str, Any]]
    ) -> ServiceResponse:
        """Validate if a collaboration is feasible"""
        try:
            feasibility_score = 0.0
            issues = []
            recommendations = []
            
            # Check skill compatibility
            skill_compatibility = self._check_skill_feasibility(
                collaboration_data, participants
            )
            feasibility_score += skill_compatibility['score'] * 0.3
            if skill_compatibility['issues']:
                issues.extend(skill_compatibility['issues'])
            if skill_compatibility['recommendations']:
                recommendations.extend(skill_compatibility['recommendations'])
            
            # Check timeline feasibility
            timeline_feasibility = self._check_timeline_feasibility(
                collaboration_data, participants
            )
            feasibility_score += timeline_feasibility['score'] * 0.2
            if timeline_feasibility['issues']:
                issues.extend(timeline_feasibility['issues'])
            
            # Check budget feasibility
            budget_feasibility = self._check_budget_feasibility(
                collaboration_data, participants
            )
            feasibility_score += budget_feasibility['score'] * 0.25
            if budget_feasibility['issues']:
                issues.extend(budget_feasibility['issues'])
            
            # Check resource availability
            resource_availability = self._check_resource_availability(
                collaboration_data, participants
            )
            feasibility_score += resource_availability['score'] * 0.15
            
            # Check communication compatibility
            communication_compatibility = self._check_communication_feasibility(
                participants
            )
            feasibility_score += communication_compatibility['score'] * 0.1
            
            # Determine overall feasibility
            feasibility_level = "high" if feasibility_score >= 0.8 else \
                              "medium" if feasibility_score >= 0.6 else "low"
            
            return ServiceResponse(
                success=True,
                data={
                    'feasibility_score': feasibility_score,
                    'feasibility_level': feasibility_level,
                    'is_feasible': feasibility_score >= 0.6,
                    'issues': issues,
                    'recommendations': recommendations,
                    'detailed_analysis': {
                        'skill_compatibility': skill_compatibility,
                        'timeline_feasibility': timeline_feasibility,
                        'budget_feasibility': budget_feasibility,
                        'resource_availability': resource_availability,
                        'communication_compatibility': communication_compatibility
                    }
                },
                message=f"Collaboration feasibility: {feasibility_level} ({feasibility_score:.2f})"
            )
            
        except Exception as e:
            logger.error(f"Feasibility validation failed: {str(e)}")
            return ServiceResponse(
                success=False,
                message="Feasibility validation failed",
                error_code="FEASIBILITY_ERROR"
            )


class CollaborationManagementService:
    """Service for managing active collaborations and contracts"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.workflow_processor = CollaborationWorkflowProcessor(config)
        self.contract_processor = CollaborationContractProcessor(config)
        
    async def create_collaboration(
        self,
        request_data: Dict[str, Any],
        selected_matches: List[str],
        contract_terms: Dict[str, Any]
    ) -> ServiceResponse:
        """Create a new collaboration from matches"""
        try:
            # Create collaboration request
            request = CollaborationRequest(**request_data)
            
            # Process the collaboration creation
            creation_result = await self.workflow_processor.process_collaboration_request(
                request, "submit"
            )
            
            if not creation_result.success:
                return ServiceResponse(
                    success=False,
                    message="Failed to create collaboration request",
                    error_code="REQUEST_CREATION_ERROR",
                    metadata={'error_details': creation_result.error_message}
                )
            
            # Create contract if matches are selected
            if selected_matches:
                contract_result = await self.contract_processor.create_contract(
                    request, selected_matches, contract_terms
                )
                
                if not contract_result.success:
                    return ServiceResponse(
                        success=False,
                        message="Failed to create collaboration contract",
                        error_code="CONTRACT_CREATION_ERROR",
                        metadata={'error_details': contract_result.error_message}
                    )
                
                contract = contract_result.data
                
                return ServiceResponse(
                    success=True,
                    data={
                        'collaboration_request': creation_result.data,
                        'contract': contract,
                        'next_steps': self._get_next_steps_for_new_collaboration(contract)
                    },
                    message="Collaboration and contract created successfully",
                    metadata={
                        'collaboration_id': request.id,
                        'contract_id': contract.id,
                        'participants_count': len(selected_matches)
                    }
                )
            else:
                return ServiceResponse(
                    success=True,
                    data={
                        'collaboration_request': creation_result.data,
                        'contract': None,
                        'next_steps': ['Find and select collaboration partners']
                    },
                    message="Collaboration request created, awaiting partner selection"
                )
                
        except Exception as e:
            logger.error(f"Collaboration creation failed: {str(e)}")
            return ServiceResponse(
                success=False,
                message="Collaboration creation failed",
                error_code="COLLABORATION_CREATION_ERROR"
            )
    
    async def update_collaboration_status(
        self,
        collaboration_id: str,
        new_status: str,
        update_data: Dict[str, Any] = None
    ) -> ServiceResponse:
        """Update collaboration status and related data"""
        try:
            update_data = update_data or {}
            
            # Get current collaboration (simulate database fetch)
            collaboration = await self._get_collaboration_by_id(collaboration_id)
            if not collaboration:
                return ServiceResponse(
                    success=False,
                    message="Collaboration not found",
                    error_code="COLLABORATION_NOT_FOUND"
                )
            
            # Validate status transition
            if not self._is_valid_status_transition(collaboration.status, new_status):
                return ServiceResponse(
                    success=False,
                    message=f"Invalid status transition from {collaboration.status.value} to {new_status}",
                    error_code="INVALID_STATUS_TRANSITION"
                )
            
            # Update status
            old_status = collaboration.status
            collaboration.status = CollaborationStatus(new_status)
            collaboration.updated_at = datetime.utcnow()
            
            # Process status-specific updates
            if new_status == CollaborationStatus.COMPLETED.value:
                completion_result = await self._process_collaboration_completion(
                    collaboration, update_data
                )
                if not completion_result.success:
                    return completion_result
            
            # Generate status update notifications
            notifications = await self._generate_status_update_notifications(
                collaboration, old_status, new_status
            )
            
            return ServiceResponse(
                success=True,
                data={
                    'collaboration': collaboration,
                    'old_status': old_status.value,
                    'new_status': new_status,
                    'notifications_generated': len(notifications)
                },
                message=f"Collaboration status updated to {new_status}",
                metadata={
                    'status_change_timestamp': collaboration.updated_at.isoformat(),
                    'notifications': [n.id for n in notifications]
                }
            )
            
        except Exception as e:
            logger.error(f"Status update failed for collaboration {collaboration_id}: {str(e)}")
            return ServiceResponse(
                success=False,
                message="Failed to update collaboration status",
                error_code="STATUS_UPDATE_ERROR"
            )
    
    async def manage_collaboration_milestones(
        self,
        collaboration_id: str,
        milestone_data: Dict[str, Any],
        action: str = "update"
    ) -> ServiceResponse:
        """Manage collaboration milestones and progress tracking"""
        try:
            # Get collaboration contract
            contract = await self._get_contract_by_collaboration_id(collaboration_id)
            if not contract:
                return ServiceResponse(
                    success=False,
                    message="Collaboration contract not found",
                    error_code="CONTRACT_NOT_FOUND"
                )
            
            if action == "add":
                result = await self._add_milestone(contract, milestone_data)
            elif action == "update":
                result = await self._update_milestone(contract, milestone_data)
            elif action == "complete":
                result = await self._complete_milestone(contract, milestone_data)
            elif action == "delete":
                result = await self._delete_milestone(contract, milestone_data)
            else:
                return ServiceResponse(
                    success=False,
                    message=f"Unknown milestone action: {action}",
                    error_code="INVALID_ACTION"
                )
            
            if result.success:
                # Update overall completion percentage
                completion_percentage = self._calculate_completion_percentage(contract)
                contract.completion_percentage = completion_percentage
                contract.updated_at = datetime.utcnow()
                
                return ServiceResponse(
                    success=True,
                    data={
                        'contract': contract,
                        'milestone_result': result.data,
                        'completion_percentage': completion_percentage,
                        'estimated_completion_date': contract.calculate_estimated_completion_date().isoformat()
                    },
                    message=f"Milestone {action} completed successfully"
                )
            else:
                return result
                
        except Exception as e:
            logger.error(f"Milestone management failed for collaboration {collaboration_id}: {str(e)}")
            return ServiceResponse(
                success=False,
                message="Milestone management failed",
                error_code="MILESTONE_ERROR"
            )


class CollaborationAnalyticsService:
    """Service for collaboration analytics and reporting"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
    async def generate_collaboration_analytics(
        self,
        collaboration_id: str,
        analytics_type: str = "comprehensive"
    ) -> ServiceResponse:
        """Generate comprehensive analytics for a collaboration"""
        try:
            # Get collaboration data
            collaboration_data = await self._get_collaboration_analytics_data(collaboration_id)
            
            if not collaboration_data:
                return ServiceResponse(
                    success=False,
                    message="Collaboration data not found for analytics",
                    error_code="DATA_NOT_FOUND"
                )
            
            if analytics_type == "performance":
                analytics = await self._generate_performance_analytics(collaboration_data)
            elif analytics_type == "financial":
                analytics = await self._generate_financial_analytics(collaboration_data)
            elif analytics_type == "engagement":
                analytics = await self._generate_engagement_analytics(collaboration_data)
            else:  # comprehensive
                analytics = await self._generate_comprehensive_analytics(collaboration_data)
            
            return ServiceResponse(
                success=True,
                data=analytics,
                message=f"{analytics_type.title()} analytics generated successfully",
                metadata={
                    'analytics_type': analytics_type,
                    'collaboration_id': collaboration_id,
                    'generated_at': datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Analytics generation failed for collaboration {collaboration_id}: {str(e)}")
            return ServiceResponse(
                success=False,
                message="Analytics generation failed",
                error_code="ANALYTICS_ERROR"
            )
    
    async def get_collaboration_insights(
        self,
        creator_id: str,
        time_period: Dict[str, datetime] = None
    ) -> ServiceResponse:
        """Get insights and trends for creator's collaborations"""
        try:
            time_period = time_period or {
                'start': datetime.utcnow() - timedelta(days=90),
                'end': datetime.utcnow()
            }
            
            # Get collaboration history
            collaborations = await self._get_creator_collaborations(creator_id, time_period)
            
            if not collaborations:
                return ServiceResponse(
                    success=True,
                    data={
                        'insights': [],
                        'trends': {},
                        'recommendations': ['Start collaborating to generate insights']
                    },
                    message="No collaboration data available for insights"
                )
            
            # Generate insights
            insights = {
                'collaboration_trends': self._analyze_collaboration_trends(collaborations),
                'performance_metrics': self._calculate_performance_metrics(collaborations),
                'success_factors': self._identify_success_factors(collaborations),
                'improvement_areas': self._identify_improvement_areas(collaborations),
                'partner_analysis': self._analyze_collaboration_partners(collaborations),
                'financial_insights': self._analyze_financial_performance(collaborations)
            }
            
            # Generate recommendations
            recommendations = self._generate_collaboration_recommendations(insights)
            
            return ServiceResponse(
                success=True,
                data={
                    'insights': insights,
                    'recommendations': recommendations,
                    'summary_statistics': {
                        'total_collaborations': len(collaborations),
                        'completion_rate': insights['performance_metrics']['completion_rate'],
                        'average_satisfaction': insights['performance_metrics']['average_satisfaction'],
                        'total_revenue': insights['financial_insights']['total_revenue']
                    },
                    'time_period': {
                        'start': time_period['start'].isoformat(),
                        'end': time_period['end'].isoformat()
                    }
                },
                message="Collaboration insights generated successfully"
            )
            
        except Exception as e:
            logger.error(f"Insights generation failed for creator {creator_id}: {str(e)}")
            return ServiceResponse(
                success=False,
                message="Insights generation failed",
                error_code="INSIGHTS_ERROR"
            )


# Export all services
__all__ = [
    'ServiceResponse',
    'CollaborationDiscoveryService',
    'CollaborationMatchingService', 
    'CollaborationManagementService',
    'CollaborationAnalyticsService'
]
