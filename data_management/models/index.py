"""
🗄️ Data Models Index - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/data_management/models/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Data Models Index and Registry - Ultra Production-Ready
Responsibility: Central index for all data models with utilities and factory methods
==================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Type, Any, Optional, Union
from datetime import datetime, timezone
import importlib
import inspect

# Import all models
from . import (
    ContentModel, CreatorModel, AnalyticsModel, FingerPrintModel,
    ProtectionModel, MonetizationModel, CollaborationModel,
    PlatformModel, AuditModel, GovernanceModel
)

class ModelRegistry:
    """Central registry for all data models with factory methods and utilities"""
    
    def __init__(self):
        self._models: Dict[str, Type] = {}
        self._register_default_models()
    
    def _register_default_models(self):
        """Register all default models"""
        self._models.update({
            'content': ContentModel,
            'creator': CreatorModel,
            'analytics': AnalyticsModel,
            'fingerprint': FingerPrintModel,
            'protection': ProtectionModel,
            'monetization': MonetizationModel,
            'collaboration': CollaborationModel,
            'platform': PlatformModel,
            'audit': AuditModel,
            'governance': GovernanceModel
        })
    
    def register_model(self, name: str, model_class: Type) -> None:
        """Register a new model class"""
        if not inspect.isclass(model_class):
            raise ValueError(f"Expected class, got {type(model_class)}")
        
        self._models[name.lower()] = model_class
    
    def get_model(self, name: str) -> Optional[Type]:
        """Get model class by name"""
        return self._models.get(name.lower())
    
    def list_models(self) -> List[str]:
        """List all registered model names"""
        return list(self._models.keys())
    
    def create_instance(self, model_name: str, **kwargs) -> Any:
        """Create model instance with provided kwargs"""
        model_class = self.get_model(model_name)
        if not model_class:
            raise ValueError(f"Model '{model_name}' not found")
        
        return model_class(**kwargs)
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get comprehensive information about a model"""
        model_class = self.get_model(model_name)
        if not model_class:
            return {}
        
        # Get model fields/attributes
        fields = []
        if hasattr(model_class, '__dataclass_fields__'):
            fields = list(model_class.__dataclass_fields__.keys())
        elif hasattr(model_class, '__annotations__'):
            fields = list(model_class.__annotations__.keys())
        
        return {
            'name': model_name,
            'class_name': model_class.__name__,
            'module': model_class.__module__,
            'doc': model_class.__doc__,
            'fields': fields,
            'methods': [method for method in dir(model_class) 
                       if not method.startswith('_') and callable(getattr(model_class, method))]
        }
    
    def validate_model_data(self, model_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against model schema"""
        model_class = self.get_model(model_name)
        if not model_class:
            raise ValueError(f"Model '{model_name}' not found")
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Basic validation - check if required fields are present
        if hasattr(model_class, '__dataclass_fields__'):
            fields = model_class.__dataclass_fields__
            
            for field_name, field_info in fields.items():
                if field_info.default == inspect.Parameter.empty and field_name not in data:
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"Required field '{field_name}' is missing")
        
        return validation_result


class ModelFactory:
    """Factory for creating and managing model instances"""
    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
    
    def create_content(self, creator_id: str, tenant_id: str, **kwargs) -> ContentModel:
        """Create a new content model instance"""
        return self.registry.create_instance('content', 
                                            creator_id=creator_id, 
                                            tenant_id=tenant_id, 
                                            **kwargs)
    
    def create_creator(self, user_id: str, tenant_id: str, email: str, **kwargs) -> CreatorModel:
        """Create a new creator model instance"""
        return self.registry.create_instance('creator',
                                            user_id=user_id,
                                            tenant_id=tenant_id,
                                            email=email,
                                            **kwargs)
    
    def create_monetization(self, creator_id: str, tenant_id: str, **kwargs) -> MonetizationModel:
        """Create a new monetization model instance"""
        return self.registry.create_instance('monetization',
                                            creator_id=creator_id,
                                            tenant_id=tenant_id,
                                            **kwargs)
    
    def batch_create(self, model_configs: List[Dict[str, Any]]) -> List[Any]:
        """Create multiple model instances from configurations"""
        instances = []
        
        for config in model_configs:
            model_type = config.pop('model_type')
            instance = self.registry.create_instance(model_type, **config)
            instances.append(instance)
        
        return instances


class ModelSerializer:
    """Utility for serializing and deserializing models"""
    
    @staticmethod
    def serialize_model(model_instance) -> Dict[str, Any]:
        """Serialize model instance to dictionary"""
        if hasattr(model_instance, 'to_dict'):
            return model_instance.to_dict()
        
        # Fallback for models without to_dict method
        result = {}
        for attr_name in dir(model_instance):
            if not attr_name.startswith('_') and not callable(getattr(model_instance, attr_name)):
                attr_value = getattr(model_instance, attr_name)
                
                # Handle datetime objects
                if isinstance(attr_value, datetime):
                    result[attr_name] = attr_value.isoformat()
                # Handle other serializable types
                elif isinstance(attr_value, (str, int, float, bool, list, dict)):
                    result[attr_name] = attr_value
                else:
                    result[attr_name] = str(attr_value)
        
        return result
    
    @staticmethod
    def deserialize_model(model_class: Type, data: Dict[str, Any]) -> Any:
        """Deserialize dictionary to model instance"""
        if hasattr(model_class, 'from_dict'):
            return model_class.from_dict(data)
        
        # Fallback - try to create instance directly
        try:
            return model_class(**data)
        except Exception as e:
            raise ValueError(f"Failed to deserialize {model_class.__name__}: {e}")


class ModelValidator:
    """Advanced validation utilities for models"""
    
    @staticmethod
    def validate_content_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content model data"""
        result = {'valid': True, 'errors': []}
        
        # Required fields validation
        required_fields = ['creator_id', 'tenant_id']
        for field in required_fields:
            if field not in data:
                result['valid'] = False
                result['errors'].append(f"Missing required field: {field}")
        
        # Content type validation
        if 'content_type' in data:
            valid_types = ['audio', 'video', 'image', 'document', 'mixed']
            if data['content_type'] not in valid_types:
                result['valid'] = False
                result['errors'].append(f"Invalid content_type. Must be one of: {valid_types}")
        
        return result
    
    @staticmethod
    def validate_creator_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate creator model data"""
        result = {'valid': True, 'errors': []}
        
        # Required fields validation
        required_fields = ['user_id', 'tenant_id', 'email']
        for field in required_fields:
            if field not in data:
                result['valid'] = False
                result['errors'].append(f"Missing required field: {field}")
        
        # Email validation
        if 'email' in data:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                result['valid'] = False
                result['errors'].append("Invalid email format")
        
        return result


# Global instances
model_registry = ModelRegistry()
model_factory = ModelFactory(model_registry)
model_serializer = ModelSerializer()
model_validator = ModelValidator()

# Utility functions
def get_all_models() -> Dict[str, Type]:
    """Get all registered models"""
    return model_registry._models.copy()

def create_model_instance(model_name: str, **kwargs) -> Any:
    """Quick utility to create model instance"""
    return model_factory.registry.create_instance(model_name, **kwargs)

def serialize_models(models: List[Any]) -> List[Dict[str, Any]]:
    """Serialize multiple model instances"""
    return [model_serializer.serialize_model(model) for model in models]

def get_model_schema(model_name: str) -> Dict[str, Any]:
    """Get model schema information"""
    return model_registry.get_model_info(model_name)

# Export public interface
__all__ = [
    'ModelRegistry', 'ModelFactory', 'ModelSerializer', 'ModelValidator',
    'model_registry', 'model_factory', 'model_serializer', 'model_validator',
    'get_all_models', 'create_model_instance', 'serialize_models', 'get_model_schema'
]
