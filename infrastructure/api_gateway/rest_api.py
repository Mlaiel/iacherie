"""
REST API Manager - Enterprise REST API Management
© 2025 Fahed Mlaiel. All rights reserved.

Comprehensive REST API management for Ainflue creator platform.
Provides creator workflow APIs, platform integrations, and enterprise features.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class APIEndpointType(Enum):
    """API endpoint types"""
    CREATOR_WORKFLOW = "creator_workflow"
    PLATFORM_INTEGRATION = "platform_integration"
    AI_PROCESSING = "ai_processing"
    ANALYTICS = "analytics"
    ADMINISTRATION = "administration"
    COMPLIANCE = "compliance"


@dataclass
class APIEndpoint:
    """API endpoint definition"""
    endpoint_id: str
    path: str
    method: HTTPMethod
    endpoint_type: APIEndpointType
    description: str
    version: str
    authentication_required: bool
    rate_limit_tier: str
    request_schema: Optional[Dict[str, Any]]
    response_schema: Optional[Dict[str, Any]]
    creator_specific: bool
    platform_specific: bool


@dataclass
class APIRequest:
    """API request tracking"""
    request_id: str
    endpoint_id: str
    method: HTTPMethod
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Optional[Dict[str, Any]]
    user_id: Optional[str]
    creator_id: Optional[str]
    timestamp: datetime
    ip_address: str


@dataclass
class APIResponse:
    """API response tracking"""
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]]
    response_time_ms: float
    timestamp: datetime
    content_length: Optional[int]


class RESTAPIManager:
    """
    Enterprise REST API Management for Creator Platform
    
    Comprehensive API management capabilities:
    - Creator workflow APIs (upload, manage, distribute)
    - Platform integration APIs (65+ platforms)
    - AI processing APIs (53 AI agents)
    - Analytics and reporting APIs
    - Administration and compliance APIs
    - Multi-version API support
    - Rate limiting and authentication
    """
    
    def __init__(self):
        self.endpoints = {}
        self.api_requests = {}
        self.api_responses = {}
        
        # Initialize Ainflue-specific REST API endpoints
        self.ainflue_endpoints = self._initialize_ainflue_endpoints()
        
        # API metrics
        self.api_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'requests_by_endpoint': {},
            'requests_by_creator': {},
            'rate_limit_violations': 0
        }
        
        # API configuration
        self.api_config = {
            'base_url': 'https://api.ainflue.com',
            'supported_versions': ['v1', 'v2'],
            'default_version': 'v1',
            'enable_cors': True,
            'enable_compression': True,
            'max_request_size': 50 * 1024 * 1024,  # 50MB for creator content
            'request_timeout': 30,
            'enable_caching': True
        }
        
        logger.info("REST API manager initialized for creator platform")
    
    def _initialize_ainflue_endpoints(self) -> Dict[str, APIEndpoint]:
        """Initialize Ainflue creator platform REST API endpoints"""
        
        endpoints = {}
        
        # Creator Workflow APIs
        creator_endpoints = [
            {
                'endpoint_id': 'creator_content_upload',
                'path': '/api/v1/creators/content/upload',
                'method': HTTPMethod.POST,
                'description': 'Upload creator content (audio, video, image, documents)',
                'authentication_required': True,
                'rate_limit_tier': 'creator_tier',
                'creator_specific': True,
                'request_schema': {
                    'type': 'object',
                    'properties': {
                        'content_type': {'type': 'string', 'enum': ['audio', 'video', 'image', 'document']},
                        'title': {'type': 'string', 'maxLength': 255},
                        'description': {'type': 'string', 'maxLength': 2000},
                        'tags': {'type': 'array', 'items': {'type': 'string'}},
                        'privacy_settings': {'type': 'object'},
                        'content_data': {'type': 'string', 'format': 'base64'}
                    },
                    'required': ['content_type', 'title', 'content_data']
                }
            },
            {
                'endpoint_id': 'creator_profile_management',
                'path': '/api/v1/creators/profile',
                'method': HTTPMethod.PUT,
                'description': 'Update creator profile information',
                'authentication_required': True,
                'rate_limit_tier': 'creator_tier',
                'creator_specific': True,
                'request_schema': {
                    'type': 'object',
                    'properties': {
                        'display_name': {'type': 'string', 'maxLength': 100},
                        'bio': {'type': 'string', 'maxLength': 1000},
                        'avatar_url': {'type': 'string', 'format': 'uri'},
                        'social_links': {'type': 'object'},
                        'content_categories': {'type': 'array', 'items': {'type': 'string'}},
                        'privacy_preferences': {'type': 'object'}
                    }
                }
            },
            {
                'endpoint_id': 'creator_revenue_analytics',
                'path': '/api/v1/creators/revenue/analytics',
                'method': HTTPMethod.GET,
                'description': 'Get creator revenue analytics and insights',
                'authentication_required': True,
                'rate_limit_tier': 'creator_tier',
                'creator_specific': True,
                'response_schema': {
                    'type': 'object',
                    'properties': {
                        'total_revenue': {'type': 'number'},
                        'monthly_revenue': {'type': 'array'},
                        'platform_breakdown': {'type': 'object'},
                        'content_performance': {'type': 'array'},
                        'projected_earnings': {'type': 'object'}
                    }
                }
            },
            {
                'endpoint_id': 'creator_collaboration_requests',
                'path': '/api/v1/creators/collaborate',
                'method': HTTPMethod.POST,
                'description': 'Create or respond to collaboration requests',
                'authentication_required': True,
                'rate_limit_tier': 'creator_tier',
                'creator_specific': True,
                'request_schema': {
                    'type': 'object',
                    'properties': {
                        'collaboration_type': {'type': 'string', 'enum': ['content', 'project', 'event']},
                        'target_creator_id': {'type': 'string'},
                        'proposal': {'type': 'string', 'maxLength': 2000},
                        'compensation_model': {'type': 'object'},
                        'timeline': {'type': 'object'}
                    },
                    'required': ['collaboration_type', 'target_creator_id', 'proposal']
                }
            },
            {
                'endpoint_id': 'creator_content_distribution',
                'path': '/api/v1/creators/distribute',
                'method': HTTPMethod.POST,
                'description': 'Distribute content to multiple platforms (65+ platforms)',
                'authentication_required': True,
                'rate_limit_tier': 'creator_tier',
                'creator_specific': True,
                'request_schema': {
                    'type': 'object',
                    'properties': {
                        'content_id': {'type': 'string'},
                        'target_platforms': {'type': 'array', 'items': {'type': 'string'}},
                        'distribution_schedule': {'type': 'object'},
                        'platform_customizations': {'type': 'object'},
                        'seo_optimization': {'type': 'object'}
                    },
                    'required': ['content_id', 'target_platforms']
                }
            }
        ]
        
        # Platform Integration APIs
        platform_endpoints = [
            {
                'endpoint_id': 'platform_sync_status',
                'path': '/api/v1/platforms/sync/status',
                'method': HTTPMethod.GET,
                'description': 'Get platform synchronization status for 65+ platforms',
                'authentication_required': True,
                'rate_limit_tier': 'platform_integration',
                'platform_specific': True
            },
            {
                'endpoint_id': 'platform_oauth_callback',
                'path': '/api/v1/platforms/oauth/callback',
                'method': HTTPMethod.POST,
                'description': 'Handle OAuth callbacks from integrated platforms',
                'authentication_required': False,
                'rate_limit_tier': 'platform_integration',
                'platform_specific': True
            },
            {
                'endpoint_id': 'platform_content_status',
                'path': '/api/v1/platforms/content/status',
                'method': HTTPMethod.GET,
                'description': 'Get content publication status across platforms',
                'authentication_required': True,
                'rate_limit_tier': 'platform_integration',
                'platform_specific': True
            }
        ]
        
        # AI Processing APIs
        ai_endpoints = [
            {
                'endpoint_id': 'ai_content_enhancement',
                'path': '/api/v1/ai/enhance/content',
                'method': HTTPMethod.POST,
                'description': 'AI-powered content enhancement (53 AI agents)',
                'authentication_required': True,
                'rate_limit_tier': 'premium_tier',
                'request_schema': {
                    'type': 'object',
                    'properties': {
                        'content_id': {'type': 'string'},
                        'enhancement_type': {'type': 'string', 'enum': ['quality', 'seo', 'translation', 'optimization']},
                        'ai_agent_preferences': {'type': 'object'},
                        'target_languages': {'type': 'array', 'items': {'type': 'string'}}
                    },
                    'required': ['content_id', 'enhancement_type']
                }
            },
            {
                'endpoint_id': 'ai_content_analysis',
                'path': '/api/v1/ai/analyze/content',
                'method': HTTPMethod.POST,
                'description': 'AI content analysis and insights',
                'authentication_required': True,
                'rate_limit_tier': 'premium_tier',
                'request_schema': {
                    'type': 'object',
                    'properties': {
                        'content_id': {'type': 'string'},
                        'analysis_type': {'type': 'string', 'enum': ['sentiment', 'engagement', 'monetization', 'compliance']},
                        'target_audience': {'type': 'object'}
                    },
                    'required': ['content_id', 'analysis_type']
                }
            },
            {
                'endpoint_id': 'ai_recommendation_engine',
                'path': '/api/v1/ai/recommendations',
                'method': HTTPMethod.GET,
                'description': 'AI-powered content and collaboration recommendations',
                'authentication_required': True,
                'rate_limit_tier': 'creator_tier',
                'creator_specific': True
            }
        ]
        
        # Analytics APIs
        analytics_endpoints = [
            {
                'endpoint_id': 'analytics_content_performance',
                'path': '/api/v1/analytics/content/performance',
                'method': HTTPMethod.GET,
                'description': 'Content performance analytics across platforms',
                'authentication_required': True,
                'rate_limit_tier': 'creator_tier',
                'creator_specific': True
            },
            {
                'endpoint_id': 'analytics_audience_insights',
                'path': '/api/v1/analytics/audience/insights',
                'method': HTTPMethod.GET,
                'description': 'Audience analytics and demographic insights',
                'authentication_required': True,
                'rate_limit_tier': 'creator_tier',
                'creator_specific': True
            },
            {
                'endpoint_id': 'analytics_monetization_metrics',
                'path': '/api/v1/analytics/monetization',
                'method': HTTPMethod.GET,
                'description': 'Monetization analytics and revenue insights',
                'authentication_required': True,
                'rate_limit_tier': 'creator_tier',
                'creator_specific': True
            }
        ]
        
        # Administration APIs
        admin_endpoints = [
            {
                'endpoint_id': 'admin_user_management',
                'path': '/api/v1/admin/users',
                'method': HTTPMethod.GET,
                'description': 'User management and administration',
                'authentication_required': True,
                'rate_limit_tier': 'enterprise_tier',
                'creator_specific': False
            },
            {
                'endpoint_id': 'admin_platform_monitoring',
                'path': '/api/v1/admin/monitoring',
                'method': HTTPMethod.GET,
                'description': 'Platform monitoring and health status',
                'authentication_required': True,
                'rate_limit_tier': 'enterprise_tier',
                'creator_specific': False
            },
            {
                'endpoint_id': 'admin_compliance_reporting',
                'path': '/api/v1/admin/compliance/reports',
                'method': HTTPMethod.GET,
                'description': 'Compliance reporting and audit data',
                'authentication_required': True,
                'rate_limit_tier': 'enterprise_tier',
                'creator_specific': False
            }
        ]
        
        # Convert to APIEndpoint objects
        all_endpoint_defs = (
            creator_endpoints + platform_endpoints + ai_endpoints + 
            analytics_endpoints + admin_endpoints
        )
        
        for endpoint_def in all_endpoint_defs:
            endpoint = APIEndpoint(
                endpoint_id=endpoint_def['endpoint_id'],
                path=endpoint_def['path'],
                method=endpoint_def['method'],
                endpoint_type=self._determine_endpoint_type(endpoint_def['path']),
                description=endpoint_def['description'],
                version='v1',
                authentication_required=endpoint_def['authentication_required'],
                rate_limit_tier=endpoint_def['rate_limit_tier'],
                request_schema=endpoint_def.get('request_schema'),
                response_schema=endpoint_def.get('response_schema'),
                creator_specific=endpoint_def.get('creator_specific', False),
                platform_specific=endpoint_def.get('platform_specific', False)
            )
            
            endpoints[endpoint.endpoint_id] = endpoint
        
        return endpoints
    
    def _determine_endpoint_type(self, path: str) -> APIEndpointType:
        """Determine endpoint type from path"""
        
        if '/creators/' in path:
            return APIEndpointType.CREATOR_WORKFLOW
        elif '/platforms/' in path:
            return APIEndpointType.PLATFORM_INTEGRATION
        elif '/ai/' in path:
            return APIEndpointType.AI_PROCESSING
        elif '/analytics/' in path:
            return APIEndpointType.ANALYTICS
        elif '/admin/' in path:
            return APIEndpointType.ADMINISTRATION
        elif '/compliance/' in path:
            return APIEndpointType.COMPLIANCE
        else:
            return APIEndpointType.CREATOR_WORKFLOW
    
    async def register_endpoint(self, endpoint: APIEndpoint) -> bool:
        """Register new API endpoint"""
        
        try:
            # Validate endpoint
            if await self._validate_endpoint(endpoint):
                self.endpoints[endpoint.endpoint_id] = endpoint
                
                # Initialize metrics for endpoint
                self.api_metrics['requests_by_endpoint'][endpoint.endpoint_id] = 0
                
                logger.info(f"API endpoint registered: {endpoint.endpoint_id}")
                return True
            else:
                logger.warning(f"Invalid endpoint configuration: {endpoint.endpoint_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering endpoint {endpoint.endpoint_id}: {e}")
            return False
    
    async def _validate_endpoint(self, endpoint: APIEndpoint) -> bool:
        """Validate endpoint configuration"""
        
        # Check required fields
        if not all([endpoint.endpoint_id, endpoint.path, endpoint.method]):
            return False
        
        # Check path format
        if not endpoint.path.startswith('/api/'):
            return False
        
        # Check version format
        if not endpoint.version in self.api_config['supported_versions']:
            return False
        
        return True
    
    async def process_api_request(
        self, 
        path: str, 
        method: str, 
        headers: Dict[str, str],
        query_params: Dict[str, Any] = None,
        body: Dict[str, Any] = None,
        user_context: Dict[str, Any] = None
    ) -> APIResponse:
        """Process incoming API request"""
        
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Create request object
        api_request = APIRequest(
            request_id=request_id,
            endpoint_id='',
            method=HTTPMethod(method.upper()),
            path=path,
            headers=headers,
            query_params=query_params or {},
            body=body,
            user_id=user_context.get('user_id') if user_context else None,
            creator_id=user_context.get('creator_id') if user_context else None,
            timestamp=start_time,
            ip_address=headers.get('X-Forwarded-For', '0.0.0.0')
        )
        
        try:
            # Find matching endpoint
            endpoint = await self._find_endpoint(path, method)
            if not endpoint:
                return self._create_error_response(
                    request_id, 404, "Endpoint not found", start_time
                )
            
            api_request.endpoint_id = endpoint.endpoint_id
            
            # Validate authentication
            if endpoint.authentication_required:
                auth_valid = await self._validate_authentication(headers, user_context)
                if not auth_valid:
                    return self._create_error_response(
                        request_id, 401, "Authentication required", start_time
                    )
            
            # Check rate limits
            rate_limit_ok = await self._check_rate_limit(endpoint, user_context)
            if not rate_limit_ok:
                self.api_metrics['rate_limit_violations'] += 1
                return self._create_error_response(
                    request_id, 429, "Rate limit exceeded", start_time
                )
            
            # Validate request schema
            if endpoint.request_schema and body:
                schema_valid = await self._validate_request_schema(body, endpoint.request_schema)
                if not schema_valid:
                    return self._create_error_response(
                        request_id, 400, "Invalid request schema", start_time
                    )
            
            # Process the request
            response_data = await self._process_endpoint_request(endpoint, api_request)
            
            # Create success response
            response = APIResponse(
                request_id=request_id,
                status_code=200,
                headers={'Content-Type': 'application/json'},
                body=response_data,
                response_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                timestamp=datetime.utcnow(),
                content_length=len(json.dumps(response_data)) if response_data else 0
            )
            
            # Update metrics
            self.api_metrics['total_requests'] += 1
            self.api_metrics['successful_requests'] += 1
            self.api_metrics['requests_by_endpoint'][endpoint.endpoint_id] += 1
            
            if api_request.creator_id:
                if api_request.creator_id not in self.api_metrics['requests_by_creator']:
                    self.api_metrics['requests_by_creator'][api_request.creator_id] = 0
                self.api_metrics['requests_by_creator'][api_request.creator_id] += 1
            
            # Store request/response for analytics
            self.api_requests[request_id] = api_request
            self.api_responses[request_id] = response
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing API request {request_id}: {e}")
            self.api_metrics['failed_requests'] += 1
            
            return self._create_error_response(
                request_id, 500, f"Internal server error: {str(e)}", start_time
            )
    
    async def _find_endpoint(self, path: str, method: str) -> Optional[APIEndpoint]:
        """Find matching endpoint for path and method"""
        
        for endpoint in self.endpoints.values():
            if endpoint.path == path and endpoint.method.value == method.upper():
                return endpoint
        
        return None
    
    async def _validate_authentication(
        self, 
        headers: Dict[str, str], 
        user_context: Dict[str, Any]
    ) -> bool:
        """Validate request authentication"""
        
        # Check for Authorization header
        auth_header = headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            # JWT token validation
            return True  # Placeholder - would implement actual JWT validation
        elif auth_header.startswith('ApiKey '):
            # API key validation
            return True  # Placeholder - would implement actual API key validation
        elif user_context and user_context.get('user_id'):
            # Session-based authentication
            return True
        
        return False
    
    async def _check_rate_limit(
        self, 
        endpoint: APIEndpoint, 
        user_context: Dict[str, Any]
    ) -> bool:
        """Check rate limits for endpoint and user"""
        
        # Placeholder rate limiting logic
        # In real implementation, would use Redis or similar for distributed rate limiting
        rate_limits = {
            'creator_tier': 1000,  # requests per minute
            'premium_tier': 5000,
            'enterprise_tier': 10000,
            'platform_integration': 50000
        }
        
        limit = rate_limits.get(endpoint.rate_limit_tier, 1000)
        # Simplified check - in real implementation would track actual usage
        return True
    
    async def _validate_request_schema(
        self, 
        body: Dict[str, Any], 
        schema: Dict[str, Any]
    ) -> bool:
        """Validate request body against schema"""
        
        # Placeholder schema validation
        # In real implementation, would use jsonschema library
        return True
    
    async def _process_endpoint_request(
        self, 
        endpoint: APIEndpoint, 
        request: APIRequest
    ) -> Dict[str, Any]:
        """Process request for specific endpoint"""
        
        # Placeholder request processing
        # In real implementation, would route to appropriate service handlers
        
        response_data = {
            'success': True,
            'message': f"Processed {endpoint.endpoint_id}",
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': request.request_id
        }
        
        # Add endpoint-specific mock data
        if endpoint.endpoint_type == APIEndpointType.CREATOR_WORKFLOW:
            if 'upload' in endpoint.path:
                response_data.update({
                    'content_id': str(uuid.uuid4()),
                    'upload_status': 'processing',
                    'processing_queue_position': 3
                })
            elif 'analytics' in endpoint.path:
                response_data.update({
                    'total_revenue': 1250.75,
                    'monthly_growth': 15.2,
                    'top_platforms': ['youtube', 'spotify', 'instagram']
                })
        elif endpoint.endpoint_type == APIEndpointType.AI_PROCESSING:
            response_data.update({
                'ai_job_id': str(uuid.uuid4()),
                'estimated_completion': '2-5 minutes',
                'ai_agents_assigned': ['content_enhancer', 'seo_optimizer']
            })
        elif endpoint.endpoint_type == APIEndpointType.PLATFORM_INTEGRATION:
            response_data.update({
                'connected_platforms': 12,
                'sync_status': 'up_to_date',
                'last_sync': datetime.utcnow().isoformat()
            })
        
        return response_data
    
    def _create_error_response(
        self, 
        request_id: str, 
        status_code: int, 
        error_message: str, 
        start_time: datetime
    ) -> APIResponse:
        """Create error response"""
        
        return APIResponse(
            request_id=request_id,
            status_code=status_code,
            headers={'Content-Type': 'application/json'},
            body={
                'error': True,
                'message': error_message,
                'status_code': status_code,
                'timestamp': datetime.utcnow().isoformat(),
                'request_id': request_id
            },
            response_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
            timestamp=datetime.utcnow(),
            content_length=len(error_message)
        )
    
    async def get_api_documentation(self) -> Dict[str, Any]:
        """Generate API documentation"""
        
        documentation = {
            'api_info': {
                'title': 'Ainflue Creator Platform API',
                'version': '1.0.0',
                'description': 'Enterprise API for creator content management and platform distribution',
                'base_url': self.api_config['base_url'],
                'authentication': 'Bearer token, API key, or OAuth2'
            },
            'endpoints': {},
            'rate_limits': {
                'creator_tier': '1000 requests/minute',
                'premium_tier': '5000 requests/minute', 
                'enterprise_tier': '10000 requests/minute',
                'platform_integration': '50000 requests/minute'
            },
            'supported_formats': ['JSON'],
            'supported_languages': '644 languages for content localization'
        }
        
        # Group endpoints by type
        for endpoint in self.endpoints.values():
            endpoint_type = endpoint.endpoint_type.value
            
            if endpoint_type not in documentation['endpoints']:
                documentation['endpoints'][endpoint_type] = []
            
            endpoint_doc = {
                'endpoint_id': endpoint.endpoint_id,
                'path': endpoint.path,
                'method': endpoint.method.value,
                'description': endpoint.description,
                'authentication_required': endpoint.authentication_required,
                'rate_limit_tier': endpoint.rate_limit_tier,
                'creator_specific': endpoint.creator_specific,
                'platform_specific': endpoint.platform_specific
            }
            
            if endpoint.request_schema:
                endpoint_doc['request_schema'] = endpoint.request_schema
            
            if endpoint.response_schema:
                endpoint_doc['response_schema'] = endpoint.response_schema
            
            documentation['endpoints'][endpoint_type].append(endpoint_doc)
        
        return documentation
    
    async def get_api_metrics(self) -> Dict[str, Any]:
        """Get API usage metrics"""
        
        metrics = {
            'last_updated': datetime.utcnow().isoformat(),
            'overall_metrics': self.api_metrics.copy(),
            'endpoint_metrics': {},
            'creator_metrics': {},
            'platform_health': {
                'total_endpoints': len(self.endpoints),
                'active_endpoints': len([e for e in self.endpoints.values() if e.endpoint_id in self.api_metrics['requests_by_endpoint']]),
                'average_response_time': self.api_metrics['average_response_time'],
                'success_rate': (
                    self.api_metrics['successful_requests'] / 
                    max(self.api_metrics['total_requests'], 1)
                ) * 100
            }
        }
        
        # Endpoint-specific metrics
        for endpoint_id, request_count in self.api_metrics['requests_by_endpoint'].items():
            if endpoint_id in self.endpoints:
                endpoint = self.endpoints[endpoint_id]
                metrics['endpoint_metrics'][endpoint_id] = {
                    'path': endpoint.path,
                    'method': endpoint.method.value,
                    'total_requests': request_count,
                    'endpoint_type': endpoint.endpoint_type.value
                }
        
        # Creator-specific metrics
        metrics['creator_metrics'] = {
            'total_active_creators': len(self.api_metrics['requests_by_creator']),
            'top_creators_by_api_usage': sorted(
                self.api_metrics['requests_by_creator'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
        
        return metrics