"""Template Manager Service

Service layer for notification template management.
Integrates with the core notification infrastructure to provide 
a clean service interface for template operations.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import from core notification system
try:
    from notifications.templates import NotificationTemplateEngine, NotificationTemplate, PersonalizationContext
except ImportError:
    # Fallback for relative imports
    from ....notifications.templates import NotificationTemplateEngine, NotificationTemplate, PersonalizationContext

logger = logging.getLogger(__name__)


class TemplateManagerService:
    """
    Service layer for notification template management.
    
    Provides a clean interface for template operations
    with business logic integration and service-level orchestration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize template manager service.
        
        Args:
            config: Optional configuration for template service
        """
        self.config = config or {}
        self._template_engine = NotificationTemplateEngine(
            config=self.config
        )
        logger.info("TemplateManagerService initialized")
    
    async def create_template(
        self,
        template_id: str,
        template_type: str,
        subject_template: str,
        body_template: str,
        channel: str,
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new notification template.
        
        Args:
            template_id: Unique template identifier
            template_type: Type of template (email, sms, etc.)
            subject_template: Template for subject/title
            body_template: Template for message body
            channel: Target channel (email, sms, push, in_app)
            language: Template language code
            metadata: Optional template metadata
            
        Returns:
            Dict with creation result and metadata
        """
        try:
            template = NotificationTemplate(
                template_id=template_id,
                template_type=template_type,
                subject_template=subject_template,
                body_template=body_template,
                channel=channel,
                language=language,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            result = await self._template_engine.create_template(template)
            
            logger.info(f"Template created successfully: {template_id}")
            return {
                "success": True,
                "template_id": template_id,
                "template_type": template_type,
                "channel": channel,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create template {template_id}: {str(e)}")
            return {
                "success": False,
                "template_id": template_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def render_template(
        self,
        template_id: str,
        context: Dict[str, Any],
        user_id: Optional[str] = None,
        personalization_level: str = "basic"
    ) -> Dict[str, Any]:
        """
        Render a template with context data.
        
        Args:
            template_id: Template identifier
            context: Template rendering context
            user_id: Optional user ID for personalization
            personalization_level: Level of personalization
            
        Returns:
            Dict with rendered content and metadata
        """
        try:
            # Create personalization context
            personalization_context = PersonalizationContext(
                user_id=user_id,
                context_data=context,
                personalization_level=personalization_level,
                timestamp=datetime.utcnow()
            )
            
            # Render template
            rendered = await self._template_engine.render_template(
                template_id=template_id,
                context=personalization_context
            )
            
            logger.info(f"Template rendered successfully: {template_id}")
            return {
                "success": True,
                "template_id": template_id,
                "rendered_subject": rendered.get("subject", ""),
                "rendered_body": rendered.get("body", ""),
                "personalization_level": personalization_level,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to render template {template_id}: {str(e)}")
            return {
                "success": False,
                "template_id": template_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing template.
        
        Args:
            template_id: Template identifier
            updates: Dict with fields to update
            
        Returns:
            Dict with update result and metadata
        """
        try:
            result = await self._template_engine.update_template(
                template_id=template_id,
                updates=updates
            )
            
            logger.info(f"Template updated successfully: {template_id}")
            return {
                "success": True,
                "template_id": template_id,
                "updated_fields": list(updates.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {str(e)}")
            return {
                "success": False,
                "template_id": template_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def delete_template(
        self,
        template_id: str
    ) -> Dict[str, Any]:
        """
        Delete a template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Dict with deletion result
        """
        try:
            result = await self._template_engine.delete_template(template_id)
            
            logger.info(f"Template deleted successfully: {template_id}")
            return {
                "success": True,
                "template_id": template_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {str(e)}")
            return {
                "success": False,
                "template_id": template_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def list_templates(
        self,
        channel: Optional[str] = None,
        template_type: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List available templates.
        
        Args:
            channel: Optional channel filter
            template_type: Optional template type filter
            language: Optional language filter
            limit: Maximum number of templates to return
            offset: Offset for pagination
            
        Returns:
            Dict with templates list and metadata
        """
        try:
            filters = {}
            if channel:
                filters["channel"] = channel
            if template_type:
                filters["template_type"] = template_type
            if language:
                filters["language"] = language
            
            templates = await self._template_engine.list_templates(
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            return {
                "success": True,
                "templates": templates,
                "count": len(templates),
                "filters": filters,
                "has_more": len(templates) == limit,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to list templates: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_template(
        self,
        template_id: str
    ) -> Dict[str, Any]:
        """
        Get a specific template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Dict with template data
        """
        try:
            template = await self._template_engine.get_template(template_id)
            
            return {
                "success": True,
                "template": template,
                "template_id": template_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {str(e)}")
            return {
                "success": False,
                "template_id": template_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def create_business_templates(self) -> Dict[str, Any]:
        """
        Create default business templates for the platform.
        
        Returns:
            Dict with creation results
        """
        business_templates = [
            {
                "template_id": "content_protection_alert",
                "template_type": "security",
                "subject_template": "Content Protection Alert - {{content_title}}",
                "body_template": "Your content '{{content_title}}' protection status: {{protection_status}}. {{details}}",
                "channel": "email"
            },
            {
                "template_id": "collaboration_request",
                "template_type": "business",
                "subject_template": "Collaboration Request from {{requester_name}}",
                "body_template": "{{requester_name}} has sent you a collaboration request for {{project_type}}. {{message}}",
                "channel": "in_app"
            },
            {
                "template_id": "revenue_milestone",
                "template_type": "monetization",
                "subject_template": "Revenue Milestone Reached!",
                "body_template": "Congratulations! You've earned ${{amount}} in {{period}}. {{achievement_details}}",
                "channel": "push"
            },
            {
                "template_id": "viral_content_alert",
                "template_type": "engagement",
                "subject_template": "Your Content is Going Viral!",
                "body_template": "{{content_title}} has reached {{views}} views! {{performance_details}}",
                "channel": "sms"
            }
        ]
        
        results = []
        for template_data in business_templates:
            result = await self.create_template(**template_data)
            results.append(result)
        
        successful = len([r for r in results if r["success"]])
        
        return {
            "total_templates": len(business_templates),
            "successful": successful,
            "failed": len(business_templates) - successful,
            "results": results
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get template manager service status."""
        return {
            "service": "TemplateManagerService",
            "status": "active",
            "supported_channels": ["email", "sms", "push", "in_app"],
            "supported_languages": ["en", "fr", "es", "de"],
            "timestamp": datetime.utcnow().isoformat()
        }