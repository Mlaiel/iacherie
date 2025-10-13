"""
Event Collector
Collects and tracks events from all modules for analytics
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
import json


class EventCollector:
    """Collect and track application events"""
    
    def __init__(self):
        self.enabled = os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
        
        # In production, use analytics service (e.g., Mixpanel, Amplitude)
        # or store in database/data warehouse
    
    async def track_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        module: Optional[str] = None
    ) -> bool:
        """
        Track an event
        
        Args:
            event_name: Name of the event
            user_id: Optional user ID
            properties: Event properties
            module: Module name (ia2good, guardian, eduverify, medcare)
            
        Returns:
            True if tracked successfully
        """
        if not self.enabled:
            return False
        
        event_data = {
            'event_name': event_name,
            'user_id': user_id,
            'properties': properties or {},
            'module': module,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # In production:
        # Send to analytics service or database
        # mixpanel.track(user_id, event_name, properties)
        
        print(f"[Analytics] Event: {event_name} | User: {user_id} | Module: {module}")
        return True
    
    async def track_page_view(
        self,
        page_path: str,
        user_id: Optional[str] = None,
        module: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track a page view
        
        Args:
            page_path: Page path/URL
            user_id: Optional user ID
            module: Module name
            properties: Additional properties
            
        Returns:
            True if tracked successfully
        """
        props = properties or {}
        props['page_path'] = page_path
        
        return await self.track_event('page_view', user_id, props, module)
    
    async def track_user_action(
        self,
        action: str,
        user_id: str,
        module: str,
        target: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track a user action
        
        Args:
            action: Action name (e.g., 'create_case', 'submit_form')
            user_id: User ID
            module: Module name
            target: Target object (e.g., case_id, form_id)
            metadata: Additional metadata
            
        Returns:
            True if tracked successfully
        """
        properties = metadata or {}
        properties['action'] = action
        properties['target'] = target
        
        return await self.track_event(f'user_action:{action}', user_id, properties, module)
    
    async def track_api_call(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Track an API call
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            response_time_ms: Response time in milliseconds
            user_id: Optional user ID
            
        Returns:
            True if tracked successfully
        """
        properties = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time_ms': response_time_ms
        }
        
        return await self.track_event('api_call', user_id, properties)
    
    async def track_error(
        self,
        error_type: str,
        error_message: str,
        module: str,
        user_id: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> bool:
        """
        Track an error
        
        Args:
            error_type: Type of error
            error_message: Error message
            module: Module name
            user_id: Optional user ID
            stack_trace: Optional stack trace
            
        Returns:
            True if tracked successfully
        """
        properties = {
            'error_type': error_type,
            'error_message': error_message,
            'stack_trace': stack_trace
        }
        
        return await self.track_event('error', user_id, properties, module)
    
    async def track_conversion(
        self,
        conversion_name: str,
        user_id: str,
        module: str,
        value: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track a conversion event
        
        Args:
            conversion_name: Name of conversion (e.g., 'signup', 'case_completed')
            user_id: User ID
            module: Module name
            value: Optional conversion value
            metadata: Additional metadata
            
        Returns:
            True if tracked successfully
        """
        properties = metadata or {}
        properties['conversion_name'] = conversion_name
        properties['value'] = value
        
        return await self.track_event(f'conversion:{conversion_name}', user_id, properties, module)
    
    async def set_user_properties(
        self,
        user_id: str,
        properties: Dict[str, Any]
    ) -> bool:
        """
        Set user properties for analytics
        
        Args:
            user_id: User ID
            properties: User properties to set
            
        Returns:
            True if set successfully
        """
        if not self.enabled:
            return False
        
        # In production:
        # mixpanel.people_set(user_id, properties)
        
        print(f"[Analytics] Set user properties for {user_id}: {list(properties.keys())}")
        return True
    
    async def identify_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Identify a user for analytics
        
        Args:
            user_id: User ID
            email: User email
            name: User name
            properties: Additional properties
            
        Returns:
            True if identified successfully
        """
        user_props = properties or {}
        if email:
            user_props['email'] = email
        if name:
            user_props['name'] = name
        
        return await self.set_user_properties(user_id, user_props)
