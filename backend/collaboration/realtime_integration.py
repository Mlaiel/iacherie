"""Real-Time Collaboration Integration
Integration layer between real-time collaboration service and existing backend systems.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from ...services.realtime_collaboration_service import (
    RealtimeCollaborationService, 
    SessionType,
    AnnotationType
)
from ...services.virtual_daw_service import VirtualDAWService
from ...services.collaboration_engine import CollaborationEngine
from .ai_matcher import AICollaborationMatcher
from .project_manager import ProjectManager
from .contract_generator import ContractGenerator
from .revenue_splitter import RevenueSplitter

logger = logging.getLogger(__name__)


class RealtimeCollaborationIntegration:
    """Integration layer for real-time collaboration with existing systems"""
    
    def __init__(self):
        self.realtime_service = RealtimeCollaborationService()
        self.daw_service = VirtualDAWService()
        self.collaboration_engine = CollaborationEngine()
        self.ai_matcher = AICollaborationMatcher()
        self.project_manager = ProjectManager()
        self.contract_generator = ContractGenerator()
        self.revenue_splitter = RevenueSplitter()
        self.session_project_mapping: Dict[str, str] = {}  # session_id -> project_id
        
    async def initialize(self):
        """Initialize all services"""
        try:
            await self.realtime_service.initialize()
            
            # Set up event handlers
            self._setup_event_handlers()
            
            logger.info("Real-time collaboration integration initialized")
            
        except Exception as e:
            logger.error(f"Error initializing integration: {str(e)}")
            raise

    def _setup_event_handlers(self):
        """Set up event handlers for service integration"""
        # This would set up event listeners between services
        # In a real implementation, this would use an event bus or observer pattern
        pass

    async def create_collaborative_project(
        self,
        creator_id: str,
        project_data: Dict[str, Any],
        collaboration_type: str = "real_time"
    ) -> Dict[str, Any]:
        """Create new collaborative project with real-time capabilities"""
        try:
            # Create project in project manager
            project = await self.project_manager.create_project(
                creator_id, project_data
            )
            
            project_id = project.get("project_id")
            
            # Determine session type based on project
            session_type = self._determine_session_type(project_data)
            
            # Create real-time session
            realtime_session = await self.realtime_service.create_realtime_session(
                creator_id, session_type, project_id, {
                    "project_name": project_data.get("name", "Untitled Project"),
                    "collaboration_type": collaboration_type,
                    "max_participants": project_data.get("max_participants", 10)
                }
            )
            
            # Create DAW session if audio production
            daw_session = None
            if session_type == SessionType.AUDIO_PRODUCTION:
                daw_session = await self.daw_service.create_daw_session(
                    creator_id, project_data.get("daw_template")
                )
                
                # Link DAW session to realtime session
                realtime_session.session_state["daw_session_id"] = daw_session.session_id
            
            # Store mapping
            self.session_project_mapping[realtime_session.session_id] = project_id
            
            # Create collaboration proposal structure
            await self._setup_collaboration_framework(project_id, realtime_session.session_id)
            
            result = {
                "project_id": project_id,
                "realtime_session_id": realtime_session.session_id,
                "session_type": session_type.value,
                "webrtc_config": realtime_session.webrtc_config,
                "collaboration_url": f"/collaborate/{realtime_session.session_id}",
                "project_details": project
            }
            
            if daw_session:
                result["daw_session_id"] = daw_session.session_id
                result["daw_project"] = await self.daw_service.get_session_state(daw_session.session_id)
            
            logger.info(f"Created collaborative project {project_id} with real-time session {realtime_session.session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating collaborative project: {str(e)}")
            raise

    async def invite_collaborator(
        self,
        session_id: str,
        inviter_id: str,
        invitee_id: str,
        role: str = "collaborator",
        permissions: Optional[List[str]] = None
    ) -> bool:
        """Invite collaborator to real-time session"""
        try:
            project_id = self.session_project_mapping.get(session_id)
            if not project_id:
                return False
            
            # Create collaboration proposal
            proposal_data = {
                "type": "real_time_collaboration",
                "description": f"Real-time collaboration invitation for project {project_id}",
                "revenue_split": {inviter_id: 0.6, invitee_id: 0.4},  # Default split
                "timeline_days": 30,
                "requirements": permissions or ["basic_collaboration"],
                "metadata": {
                    "session_id": session_id,
                    "role": role,
                    "real_time_enabled": True
                }
            }
            
            proposal = await self.collaboration_engine.create_collaboration_proposal(
                inviter_id, invitee_id, proposal_data
            )
            
            # Store proposal mapping
            session = self.realtime_service.active_sessions.get(session_id)
            if session:
                if "collaboration_proposals" not in session.session_state:
                    session.session_state["collaboration_proposals"] = []
                session.session_state["collaboration_proposals"].append(proposal.id)
            
            logger.info(f"Invited {invitee_id} to collaborate on session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error inviting collaborator: {str(e)}")
            return False

    async def accept_collaboration_invitation(
        self,
        proposal_id: str,
        invitee_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Accept collaboration invitation and join real-time session"""
        try:
            # Accept collaboration proposal
            success = await self.collaboration_engine.respond_to_proposal(
                proposal_id, invitee_id, "accept"
            )
            
            if not success:
                return {"success": False, "error": "Failed to accept proposal"}
            
            # Generate collaboration contract
            contract = await self.contract_generator.generate_realtime_contract(
                proposal_id, session_id
            )
            
            # Set up revenue splitting
            await self.revenue_splitter.setup_realtime_revenue_split(
                session_id, proposal_id
            )
            
            # Add collaborator to project
            project_id = self.session_project_mapping.get(session_id)
            if project_id:
                await self.project_manager.add_collaborator(
                    project_id, invitee_id, "collaborator"
                )
            
            result = {
                "success": True,
                "proposal_id": proposal_id,
                "session_id": session_id,
                "contract": contract,
                "join_url": f"/collaborate/{session_id}",
                "collaboration_active": True
            }
            
            logger.info(f"Collaboration invitation accepted for session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error accepting collaboration invitation: {str(e)}")
            return {"success": False, "error": str(e)}

    async def find_collaboration_opportunities(
        self,
        creator_id: str,
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find real-time collaboration opportunities"""
        try:
            # Use AI matcher to find potential collaborators
            matches = await self.ai_matcher.find_realtime_matches(creator_id, criteria)
            
            # Filter for active real-time sessions
            opportunities = []
            
            for match in matches:
                collaborator_id = match.get("collaborator_id")
                
                # Check for active sessions by this collaborator
                for session_id, session in self.realtime_service.active_sessions.items():
                    if (session.creator_id == collaborator_id and 
                        len(session.participants) < session.session_state.get("max_participants", 10)):
                        
                        project_id = self.session_project_mapping.get(session_id)
                        project_details = await self.project_manager.get_project(project_id) if project_id else {}
                        
                        opportunity = {
                            "session_id": session_id,
                            "project_id": project_id,
                            "creator_id": collaborator_id,
                            "session_type": session.session_type.value,
                            "project_name": project_details.get("name", "Untitled"),
                            "participants_count": len(session.participants),
                            "max_participants": session.session_state.get("max_participants", 10),
                            "compatibility_score": match.get("compatibility_score", 0.0),
                            "collaboration_url": f"/collaborate/{session_id}",
                            "created_at": session.created_at.isoformat()
                        }
                        
                        opportunities.append(opportunity)
            
            # Sort by compatibility score
            opportunities.sort(key=lambda x: x["compatibility_score"], reverse=True)
            
            logger.info(f"Found {len(opportunities)} collaboration opportunities for {creator_id}")
            return opportunities[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error finding collaboration opportunities: {str(e)}")
            return []

    async def handle_session_completion(
        self,
        session_id: str,
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle completion of real-time collaboration session"""
        try:
            session = self.realtime_service.active_sessions.get(session_id)
            if not session:
                return {"error": "Session not found"}
            
            project_id = self.session_project_mapping.get(session_id)
            
            # Finalize project
            project_result = None
            if project_id:
                project_result = await self.project_manager.finalize_project(
                    project_id, completion_data
                )
            
            # Export DAW project if applicable
            daw_export = None
            if session.session_type == SessionType.AUDIO_PRODUCTION:
                daw_session_id = session.session_state.get("daw_session_id")
                if daw_session_id:
                    daw_export = await self.daw_service.export_project(
                        daw_session_id, 
                        completion_data.get("export_format", "wav"),
                        completion_data.get("quality", "high")
                    )
            
            # Calculate revenue distribution
            revenue_distribution = await self.revenue_splitter.calculate_final_distribution(
                session_id, completion_data
            )
            
            # Generate completion analytics
            analytics = await self.realtime_service.get_session_analytics(session_id)
            
            # Create completion record
            completion_record = {
                "session_id": session_id,
                "project_id": project_id,
                "completed_at": datetime.now().isoformat(),
                "participants": list(session.participants),
                "project_result": project_result,
                "analytics": analytics,
                "revenue_distribution": revenue_distribution,
                "completion_data": completion_data
            }
            
            if daw_export:
                completion_record["daw_export"] = {
                    "format": completion_data.get("export_format", "wav"),
                    "size_bytes": len(daw_export),
                    "exported_at": datetime.now().isoformat()
                }
            
            # Store completion record
            await self._store_completion_record(completion_record)
            
            # Clean up session
            await self._cleanup_completed_session(session_id)
            
            logger.info(f"Completed session {session_id}")
            return completion_record
            
        except Exception as e:
            logger.error(f"Error handling session completion: {str(e)}")
            return {"error": str(e)}

    async def get_collaboration_insights(
        self,
        creator_id: str,
        timeframe_days: int = 30
    ) -> Dict[str, Any]:
        """Get collaboration insights including real-time activities"""
        try:
            # Get base collaboration insights
            base_insights = await self.collaboration_engine.generate_collaboration_insights(creator_id)
            
            # Get real-time session insights
            realtime_insights = await self._get_realtime_insights(creator_id, timeframe_days)
            
            # Combine insights
            combined_insights = {
                **base_insights,
                "realtime_collaboration": realtime_insights,
                "integration_metrics": {
                    "active_realtime_sessions": len([
                        s for s in self.realtime_service.active_sessions.values()
                        if creator_id in s.participants
                    ]),
                    "total_daw_sessions": len([
                        s for s in self.daw_service.active_sessions.values()
                        if creator_id in s.active_users
                    ])
                }
            }
            
            return combined_insights
            
        except Exception as e:
            logger.error(f"Error getting collaboration insights: {str(e)}")
            return {}

    # Helper methods
    def _determine_session_type(self, project_data: Dict[str, Any]) -> SessionType:
        """Determine session type based on project data"""
        project_type = project_data.get("type", "general")
        
        if project_type == "music_production":
            return SessionType.AUDIO_PRODUCTION
        elif project_type == "video_collaboration":
            return SessionType.VIDEO_COLLABORATION
        elif project_type == "project_review":
            return SessionType.PROJECT_REVIEW
        elif project_type == "creative_brainstorm":
            return SessionType.CREATIVE_BRAINSTORM
        else:
            return SessionType.LIVE_ANNOTATION

    async def _setup_collaboration_framework(self, project_id: str, session_id: str):
        """Set up collaboration framework for project"""
        try:
            # Initialize collaboration settings
            collaboration_settings = {
                "revenue_model": "contribution_based",
                "ip_ownership": "shared",
                "decision_making": "consensus",
                "conflict_resolution": "automated_then_manual"
            }
            
            # Store in project
            await self.project_manager.update_project_settings(
                project_id, {"collaboration": collaboration_settings}
            )
            
        except Exception as e:
            logger.error(f"Error setting up collaboration framework: {str(e)}")

    async def _get_realtime_insights(
        self, 
        creator_id: str, 
        timeframe_days: int
    ) -> Dict[str, Any]:
        """Get real-time collaboration insights"""
        try:
            # Count active sessions
            active_sessions = [
                s for s in self.realtime_service.active_sessions.values()
                if creator_id in s.participants
            ]
            
            # Count sessions by type
            session_types = {}
            for session in active_sessions:
                session_type = session.session_type.value
                session_types[session_type] = session_types.get(session_type, 0) + 1
            
            # Calculate average session duration
            total_duration = sum([
                (datetime.now() - session.created_at).total_seconds()
                for session in active_sessions
            ])
            avg_duration = total_duration / len(active_sessions) if active_sessions else 0
            
            return {
                "active_sessions_count": len(active_sessions),
                "session_types_breakdown": session_types,
                "average_session_duration_seconds": avg_duration,
                "total_annotations_created": sum([
                    len(annotations) for annotations in self.realtime_service.media_annotations.values()
                ]),
                "realtime_collaboration_score": min(len(active_sessions) * 20, 100)
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time insights: {str(e)}")
            return {}

    async def _store_completion_record(self, completion_record: Dict[str, Any]):
        """Store session completion record"""
        try:
            # This would store in database
            # For now, just log the completion
            logger.info(f"Stored completion record for session {completion_record['session_id']}")
            
        except Exception as e:
            logger.error(f"Error storing completion record: {str(e)}")

    async def _cleanup_completed_session(self, session_id: str):
        """Clean up completed session resources"""
        try:
            # Remove from session mapping
            self.session_project_mapping.pop(session_id, None)
            
            # The services will handle their own cleanup
            logger.info(f"Cleaned up completed session {session_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up session: {str(e)}")


class RealtimeEventHandler:
    """Handles events between real-time collaboration and other systems"""
    
    def __init__(self, integration: RealtimeCollaborationIntegration):
        self.integration = integration
        
    async def handle_user_joined(self, session_id: str, user_id: str):
        """Handle user joining real-time session"""
        try:
            # Update project participation
            project_id = self.integration.session_project_mapping.get(session_id)
            if project_id:
                await self.integration.project_manager.add_participant(project_id, user_id)
            
            # Start revenue tracking
            await self.integration.revenue_splitter.start_user_participation(
                session_id, user_id
            )
            
        except Exception as e:
            logger.error(f"Error handling user joined event: {str(e)}")

    async def handle_user_left(self, session_id: str, user_id: str):
        """Handle user leaving real-time session"""
        try:
            # End revenue tracking
            await self.integration.revenue_splitter.end_user_participation(
                session_id, user_id
            )
            
        except Exception as e:
            logger.error(f"Error handling user left event: {str(e)}")

    async def handle_project_milestone(self, session_id: str, milestone_data: Dict[str, Any]):
        """Handle project milestone completion"""
        try:
            project_id = self.integration.session_project_mapping.get(session_id)
            if project_id:
                await self.integration.project_manager.complete_milestone(
                    project_id, milestone_data
                )
            
            # Trigger revenue distribution if configured
            if milestone_data.get("trigger_payment", False):
                await self.integration.revenue_splitter.distribute_milestone_payment(
                    session_id, milestone_data
                )
                
        except Exception as e:
            logger.error(f"Error handling project milestone: {str(e)}")