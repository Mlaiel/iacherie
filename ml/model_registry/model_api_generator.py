"""
Model Api Generator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
import logging

🚀 **Model API Generator - Enterprise ML API Automation**

**Author:** Fahed Mlaiel (mlaiel@live.de) - Lead Dev IA  
**Copyright:** © 2025 Fahed Mlaiel. All rights reserved.  
**Version:** 1.0.0  
**Created:** January 2025

**⚠️ WARNING:** This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly prohibited.

---

## 🎯 **ROLE: LEAD DEV IA - API ORCHESTRATION MASTERY**

Enterprise-grade automatic API generation for ML models with OpenAPI specifications,
versioning, authentication, and creator-specific optimization strategies.
"""

import os
import yaml
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

import mlflow
import mlflow.tracking
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
import uvicorn
from jinja2 import Environment, FileSystemLoader

class ModelType(Enum):
    """Model type classification for API generation"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"  
    CLUSTERING = "clustering"
    NLP = "natural_language_processing"
    COMPUTER_VISION = "computer_vision"
    AUDIO_PROCESSING = "audio_processing"
    RECOMMENDER = "recommender_system"
    GENERATIVE = "generative_model"

class CreatorType(Enum):
    """Creator specialization for model APIs"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERIC = "generic"

@dataclass
class APIEndpointConfig:
    """Configuration for generated API endpoints"""
    endpoint_name: str
    method: str
    path: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    authentication_required: bool = True
    rate_limit: int = 1000  # requests per hour
    timeout: int = 30  # seconds
    creator_specific: bool = False

@dataclass
class ModelAPISpec:
    """Complete model API specification"""
    model_id: str
    model_name: str
    model_version: str
    model_type: ModelType
    creator_type: CreatorType
    endpoints: List[APIEndpointConfig]
    base_url: str
    authentication: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ModelAPIGenerator:
    """
    🚀 **Enterprise Model API Generator**
    
    **Lead Dev IA Role:** Automated API generation with enterprise standards
    - OpenAPI 3.0 specification generation
    - Authentication and authorization integration
    - Creator-specific API optimization
    - Versioning and deployment automation
    - Performance monitoring integration
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.mlflow_client = mlflow.tracking.MlflowClient()
        self.template_env = Environment(
            loader=FileSystemLoader(config.get('template_dir', 'templates'))
        )
        self.output_dir = Path(config.get('output_dir', 'generated_apis'))
        self.output_dir.mkdir(exist_ok=True)
        
        # Security configuration
        self.security = HTTPBearer()
        
        # Creator-specific configurations
        self.creator_configs = {
            CreatorType.MUSICIAN: {
                'max_audio_size': '100MB',
                'supported_formats': ['mp3', 'wav', 'flac'],
                'processing_timeout': 60
            },
            CreatorType.PHOTOGRAPHER: {
                'max_image_size': '50MB',
                'supported_formats': ['jpg', 'png', 'tiff', 'raw'],
                'processing_timeout': 30
            },
            CreatorType.BLOGGER: {
                'max_text_length': 50000,
                'supported_languages': ['en', 'fr', 'de', 'es'],
                'processing_timeout': 15
            }
        }
    
    async def generate_api_for_model(
        self, 
        model_id: str,
        creator_type: CreatorType = CreatorType.GENERIC,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> ModelAPISpec:
        """
        Generate complete API specification for a model
        
        **Lead Dev IA Expertise:**
        - Model introspection and schema generation
        - Creator-specific optimization
        - Enterprise security integration
        """
        # Get model metadata from MLflow
        model_info = await self._get_model_info(model_id)
        
        # Determine model type
        model_type = await self._classify_model(model_info)
        
        # Generate endpoints based on model type and creator
        endpoints = await self._generate_endpoints(
            model_info, model_type, creator_type
        )
        
        # Create API specification
        api_spec = ModelAPISpec(
            model_id=model_id,
            model_name=model_info.get('name', f'model_{model_id}'),
            model_version=model_info.get('version', '1.0.0'),
            model_type=model_type,
            creator_type=creator_type,
            endpoints=endpoints,
            base_url=f"{self.config.get('base_url', 'http://localhost:8000')}/api/v1",
            authentication=self._generate_auth_config(),
            metadata={
                'generated_at': datetime.utcnow().isoformat(),
                'generator_version': '1.0.0',
                'model_framework': model_info.get('framework', 'unknown'),
                'creator_optimized': creator_type != CreatorType.GENERIC
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return api_spec
    
    async def _get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Retrieve model information from MLflow registry"""
        try:
            model_version = self.mlflow_client.get_latest_versions(
                model_id, stages=["Production", "Staging"]
            )[0]
            
            return {
                'name': model_version.name,
                'version': model_version.version,
                'stage': model_version.current_stage,
                'description': model_version.description,
                'tags': model_version.tags,
                'run_id': model_version.run_id
            }
        except Exception as e:
            raise HTTPException(
                status_code=404, 
                detail=f"Model {model_id} not found: {str(e)}"
            )
    
    async def _classify_model(self, model_info: Dict[str, Any]) -> ModelType:
        """Classify model type based on metadata and tags"""
        tags = model_info.get('tags', {})
        
        # Check for explicit model type tag
        if 'model_type' in tags:
            try:
                return ModelType(tags['model_type'])
            except ValueError:
                pass
        
        # Infer from model name or description
        name_desc = f"{model_info.get('name', '')} {model_info.get('description', '')}".lower()
        
        if any(word in name_desc for word in ['classifier', 'classification']):
            return ModelType.CLASSIFICATION
        elif any(word in name_desc for word in ['regression', 'predict']):
            return ModelType.REGRESSION
        elif any(word in name_desc for word in ['cluster', 'segmentation']):
            return ModelType.CLUSTERING
        elif any(word in name_desc for word in ['nlp', 'text', 'language']):
            return ModelType.NLP
        elif any(word in name_desc for word in ['vision', 'image', 'cv']):
            return ModelType.COMPUTER_VISION
        elif any(word in name_desc for word in ['audio', 'sound', 'music']):
            return ModelType.AUDIO_PROCESSING
        elif any(word in name_desc for word in ['recommend', 'suggest']):
            return ModelType.RECOMMENDER
        elif any(word in name_desc for word in ['generate', 'create', 'gan']):
            return ModelType.GENERATIVE
        
        return ModelType.CLASSIFICATION  # Default
    
    async def _generate_endpoints(
        self,
        model_info: Dict[str, Any],
        model_type: ModelType,
        creator_type: CreatorType
    ) -> List[APIEndpointConfig]:
        """Generate API endpoints based on model and creator type"""
        endpoints = []
        
        # Standard prediction endpoint
        predict_endpoint = APIEndpointConfig(
            endpoint_name="predict",
            method="POST",
            path="/predict",
            description=f"Make predictions using {model_info.get('name', 'model')}",
            input_schema=self._generate_input_schema(model_type, creator_type),
            output_schema=self._generate_output_schema(model_type),
            rate_limit=self.creator_configs.get(creator_type, {}).get('rate_limit', 1000)
        )
        endpoints.append(predict_endpoint)
        
        # Batch prediction endpoint
        batch_endpoint = APIEndpointConfig(
            endpoint_name="batch_predict",
            method="POST", 
            path="/batch-predict",
            description="Batch predictions for multiple inputs",
            input_schema=self._generate_batch_input_schema(model_type, creator_type),
            output_schema=self._generate_batch_output_schema(model_type),
            rate_limit=100  # Lower rate limit for batch operations
        )
        endpoints.append(batch_endpoint)
        
        # Model info endpoint
        info_endpoint = APIEndpointConfig(
            endpoint_name="model_info",
            method="GET",
            path="/info",
            description="Get model information and metadata",
            input_schema={},
            output_schema=self._generate_info_schema(),
            authentication_required=False
        )
        endpoints.append(info_endpoint)
        
        # Health check endpoint
        health_endpoint = APIEndpointConfig(
            endpoint_name="health",
            method="GET",
            path="/health",
            description="Check model service health",
            input_schema={},
            output_schema={"type": "object", "properties": {"status": {"type": "string"}}},
            authentication_required=False
        )
        endpoints.append(health_endpoint)
        
        # Creator-specific endpoints
        if creator_type == CreatorType.MUSICIAN:
            endpoints.extend(self._generate_musician_endpoints())
        elif creator_type == CreatorType.PHOTOGRAPHER:
            endpoints.extend(self._generate_photographer_endpoints())
        elif creator_type == CreatorType.BLOGGER:
            endpoints.extend(self._generate_blogger_endpoints())
        
        return endpoints
    
    def _generate_input_schema(self, model_type: ModelType, creator_type: CreatorType) -> Dict[str, Any]:
        """Generate input schema based on model and creator type"""
        base_schema = {
            "type": "object",
            "required": ["data"],
            "properties": {
                "data": {"type": "object"},
                "options": {
                    "type": "object",
                    "properties": {
                        "confidence_threshold": {"type": "number", "minimum": 0, "maximum": 1},
                        "return_probabilities": {"type": "boolean", "default": False}
                    }
                }
            }
        }
        
        # Customize based on model type
        if model_type == ModelType.AUDIO_PROCESSING:
            base_schema["properties"]["data"] = {
                "type": "object",
                "required": ["audio_data"],
                "properties": {
                    "audio_data": {"type": "string", "format": "base64"},
                    "sample_rate": {"type": "integer", "default": 44100},
                    "format": {"type": "string", "enum": ["mp3", "wav", "flac"]}
                }
            }
        elif model_type == ModelType.COMPUTER_VISION:
            base_schema["properties"]["data"] = {
                "type": "object", 
                "required": ["image_data"],
                "properties": {
                    "image_data": {"type": "string", "format": "base64"},
                    "format": {"type": "string", "enum": ["jpg", "png", "tiff"]}
                }
            }
        elif model_type == ModelType.NLP:
            base_schema["properties"]["data"] = {
                "type": "object",
                "required": ["text"],
                "properties": {
                    "text": {"type": "string", "maxLength": 10000},
                    "language": {"type": "string", "default": "en"}
                }
            }
        
        return base_schema
    
    def _generate_output_schema(self, model_type: ModelType) -> Dict[str, Any]:
        """Generate output schema based on model type"""
        base_schema = {
            "type": "object",
            "properties": {
                "prediction": {"type": "object"},
                "confidence": {"type": "number"},
                "model_version": {"type": "string"},
                "processing_time_ms": {"type": "number"}
            }
        }
        
        if model_type == ModelType.CLASSIFICATION:
            base_schema["properties"]["prediction"] = {
                "type": "object",
                "properties": {
                    "class": {"type": "string"},
                    "probabilities": {"type": "object"}
                }
            }
        elif model_type == ModelType.REGRESSION:
            base_schema["properties"]["prediction"] = {
                "type": "object", 
                "properties": {
                    "value": {"type": "number"},
                    "confidence_interval": {"type": "array", "items": {"type": "number"}}
                }
            }
        
        return base_schema
    
    def _generate_batch_input_schema(self, model_type: ModelType, creator_type: CreatorType) -> Dict[str, Any]:
        """Generate batch input schema"""
        single_schema = self._generate_input_schema(model_type, creator_type)
        return {
            "type": "object",
            "required": ["batch_data"],
            "properties": {
                "batch_data": {
                    "type": "array",
                    "items": single_schema["properties"]["data"],
                    "maxItems": 100
                },
                "options": single_schema["properties"]["options"]
            }
        }
    
    def _generate_batch_output_schema(self, model_type: ModelType) -> Dict[str, Any]:
        """Generate batch output schema"""
        single_schema = self._generate_output_schema(model_type)
        return {
            "type": "object",
            "properties": {
                "predictions": {
                    "type": "array",
                    "items": single_schema
                },
                "batch_id": {"type": "string"},
                "total_processing_time_ms": {"type": "number"}
            }
        }
    
    def _generate_info_schema(self) -> Dict[str, Any]:
        """Generate model info schema"""
        return {
            "type": "object",
            "properties": {
                "model_id": {"type": "string"},
                "model_name": {"type": "string"},
                "model_version": {"type": "string"},
                "model_type": {"type": "string"},
                "creator_type": {"type": "string"},
                "description": {"type": "string"},
                "input_features": {"type": "array", "items": {"type": "string"}},
                "output_classes": {"type": "array", "items": {"type": "string"}},
                "performance_metrics": {"type": "object"},
                "deployment_info": {"type": "object"}
            }
        }
    
    def _generate_musician_endpoints(self) -> List[APIEndpointConfig]:
        """Generate musician-specific endpoints"""
        return [
            APIEndpointConfig(
                endpoint_name="analyze_audio",
                method="POST",
                path="/analyze-audio",
                description="Analyze audio content for musicians",
                input_schema={
                    "type": "object",
                    "required": ["audio_data"],
                    "properties": {
                        "audio_data": {"type": "string", "format": "base64"},
                        "analysis_type": {
                            "type": "string",
                            "enum": ["tempo", "key", "genre", "mood", "energy"]
                        }
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "tempo": {"type": "number"},
                        "key": {"type": "string"},
                        "genre": {"type": "string"},
                        "mood": {"type": "string"},
                        "energy_level": {"type": "number"}
                    }
                },
                creator_specific=True
            )
        ]
    
    def _generate_photographer_endpoints(self) -> List[APIEndpointConfig]:
        """Generate photographer-specific endpoints"""
        return [
            APIEndpointConfig(
                endpoint_name="aesthetic_analysis",
                method="POST",
                path="/aesthetic-analysis",
                description="Analyze image aesthetics for photographers",
                input_schema={
                    "type": "object",
                    "required": ["image_data"],
                    "properties": {
                        "image_data": {"type": "string", "format": "base64"},
                        "analysis_aspects": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["composition", "lighting", "color", "style"]}
                        }
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "aesthetic_score": {"type": "number"},
                        "composition_rating": {"type": "number"},
                        "lighting_quality": {"type": "number"},
                        "color_harmony": {"type": "number"},
                        "style_classification": {"type": "string"}
                    }
                },
                creator_specific=True
            )
        ]
    
    def _generate_blogger_endpoints(self) -> List[APIEndpointConfig]:
        """Generate blogger-specific endpoints"""
        return [
            APIEndpointConfig(
                endpoint_name="content_optimization",
                method="POST",
                path="/content-optimization",
                description="Optimize content for bloggers",
                input_schema={
                    "type": "object",
                    "required": ["content"],
                    "properties": {
                        "content": {"type": "string", "maxLength": 50000},
                        "target_audience": {"type": "string"},
                        "seo_focus": {"type": "string"},
                        "optimization_goals": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["readability", "seo", "engagement", "conversion"]}
                        }
                    }
                },
                output_schema={
                    "type": "object", 
                    "properties": {
                        "readability_score": {"type": "number"},
                        "seo_score": {"type": "number"},
                        "engagement_prediction": {"type": "number"},
                        "optimization_suggestions": {"type": "array", "items": {"type": "string"}},
                        "keyword_recommendations": {"type": "array", "items": {"type": "string"}}
                    }
                },
                creator_specific=True
            )
        ]
    
    def _generate_auth_config(self) -> Dict[str, Any]:
        """Generate authentication configuration"""
        return {
            "type": "bearer",
            "scheme": "JWT",
            "bearer_format": "JWT",
            "description": "Enterprise JWT authentication with role-based access control",
            "scopes": {
                "read": "Read model information",
                "predict": "Make predictions",
                "admin": "Administrative access"
            }
        }
    
    async def generate_openapi_spec(self, api_spec: ModelAPISpec) -> Dict[str, Any]:
        """
        Generate OpenAPI 3.0 specification
        
        **Lead Dev IA Mastery:** Complete API documentation generation
        """
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{api_spec.model_name} API",
                "description": f"Auto-generated API for {api_spec.model_name} ({api_spec.model_type.value})",
                "version": api_spec.model_version,
                "contact": {
                    "name": "Fahed Mlaiel",
                    "email": "mlaiel@live.de"
                },
                "license": {
                    "name": "Proprietary",
                    "url": "https://ainflue.com/license"
                }
            },
            "servers": [
                {
                    "url": api_spec.base_url,
                    "description": "Production server"
                }
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                },
                "schemas": {}
            },
            "security": [{"bearerAuth": []}]
        }
        
        # Add paths for each endpoint
        for endpoint in api_spec.endpoints:
            path_item = {
                endpoint.method.lower(): {
                    "summary": endpoint.description,
                    "operationId": endpoint.endpoint_name,
                    "tags": [api_spec.creator_type.value],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": endpoint.input_schema
                            }
                        }
                    } if endpoint.method == "POST" else None,
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": endpoint.output_schema
                                }
                            }
                        },
                        "400": {"description": "Bad Request"},
                        "401": {"description": "Unauthorized"},
                        "429": {"description": "Rate Limit Exceeded"},
                        "500": {"description": "Internal Server Error"}
                    }
                }
            }
            
            # Remove requestBody for GET requests
            if endpoint.method == "GET":
                path_item[endpoint.method.lower()].pop("requestBody", None)
            
            # Add security requirement if needed
            if endpoint.authentication_required:
                path_item[endpoint.method.lower()]["security"] = [{"bearerAuth": []}]
            else:
                path_item[endpoint.method.lower()]["security"] = []
            
            openapi_spec["paths"][endpoint.path] = path_item
        
        return openapi_spec
    
    async def generate_fastapi_code(self, api_spec: ModelAPISpec) -> str:
        """
        Generate FastAPI application code
        
        **Lead Dev IA Excellence:** Complete FastAPI app generation
        """
        template = self.template_env.get_template('fastapi_template.py.j2')
        
        return template.render(
            api_spec=api_spec,
            model_type=api_spec.model_type.value,
            creator_type=api_spec.creator_type.value,
            generated_at=datetime.utcnow().isoformat()
        )
    
    async def save_generated_api(
        self, 
        api_spec: ModelAPISpec, 
        include_code: bool = True,
        include_openapi: bool = True
    ) -> Dict[str, Path]:
        """Save generated API artifacts"""
        output_paths = {}
        
        model_dir = self.output_dir / api_spec.model_id
        model_dir.mkdir(exist_ok=True)
        
        # Save API specification
        spec_path = model_dir / 'api_spec.json'
        with open(spec_path, 'w') as f:
            json.dump(asdict(api_spec), f, indent=2, default=str)
        output_paths['spec'] = spec_path
        
        # Save OpenAPI specification
        if include_openapi:
            openapi_spec = await self.generate_openapi_spec(api_spec)
            openapi_path = model_dir / 'openapi.yaml'
            with open(openapi_path, 'w') as f:
                yaml.dump(openapi_spec, f, default_flow_style=False)
            output_paths['openapi'] = openapi_path
        
        # Save FastAPI code
        if include_code:
            fastapi_code = await self.generate_fastapi_code(api_spec)
            code_path = model_dir / 'app.py'
            with open(code_path, 'w') as f:
                f.write(fastapi_code)
            output_paths['code'] = code_path
        
        return output_paths

# Usage example
async def main() -> None:
    """Example usage of ModelAPIGenerator"""
    config = {
        'base_url': 'https://api.ainflue.com',
        'output_dir': 'generated_apis',
        'template_dir': 'templates'
    }
    
    generator = ModelAPIGenerator(config)
    
    # Generate API for a musician's audio model
    api_spec = await generator.generate_api_for_model(
        model_id="musician_audio_classifier",
        creator_type=CreatorType.MUSICIAN
    )
    
    # Save generated artifacts
    output_paths = await generator.save_generated_api(api_spec)
    print(f"API generated successfully: {output_paths}")

if __name__ == "__main__":
    asyncio.run(main())