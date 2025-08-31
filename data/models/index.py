"""Data Models Index
================

Central index file for IA Influencer Agent data models.
Provides easy access to all models, utilities, and helper functions.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, List, Type, Any, Optional
from datetime import datetime
import importlib
import inspect

# Import all models and enums
from . import (
    # Models
    ContentModel, UserModel, FingerprintModel, RevenueModel, 
    AnalyticsModel, ProtectionModel, LicensingModel,
    
    # Enums
    ContentType, ContentStatus, ContentVisibility,
    UserType, UserStatus, SubscriptionTier,
    FingerprintType, FingerprintAlgorithm, FingerprintStatus, MatchConfidenceLevel,
    RevenueSource, RevenueStatus, PaymentMethod, RevenuePeriod,
    AnalyticsType, MetricType, TimeGranularity,
    ProtectionType, ViolationType, SeverityLevel, ProtectionStatus, EnforcementAction,
    LicenseType, LicenseCategory, UsageType, LicenseStatus, PaymentStructure,
    
    # Utilities
    MODEL_REGISTRY, RELATIONSHIP_MAPPINGS,
    get_model_by_table_name, get_all_models, get_model_relationships
)

# SQLAlchemy imports for database operations
try:
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.ext.declarative import declarative_base
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


class ModelManager:
    """
    Central manager for all data models.
    Provides utilities for model operations, validation, and introspection.
    """
    
    def __init__(self):
        self.models = MODEL_REGISTRY
        self.relationships = RELATIONSHIP_MAPPINGS
        self._session = None
        self._engine = None
    
    def get_model(self, name: str) -> Optional[Type]:
        """Get model class by name"""
        return self.models.get(name)
    
    def get_all_model_names(self) -> List[str]:
        """Get all registered model names"""
        return list(self.models.keys())
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a model"""
        model_class = self.get_model(model_name)
        if not model_class:
            return {}
        
        # Get model attributes
        attributes = {}
        for attr_name in dir(model_class):
            if not attr_name.startswith('_'):
                attr = getattr(model_class, attr_name)
                if hasattr(attr, 'type'):  # SQLAlchemy column
                    attributes[attr_name] = {
                        'type': str(attr.type),
                        'nullable': getattr(attr, 'nullable', True),
                        'primary_key': getattr(attr, 'primary_key', False),
                        'unique': getattr(attr, 'unique', False)
                    }
        
        return {
            'name': model_name,
            'class': model_class.__name__,
            'table_name': getattr(model_class, '__tablename__', None),
            'attributes': attributes,
            'relationships': [rel for rel in self.relationships.keys() 
                            if model_name in rel],
            'docstring': model_class.__doc__
        }
    
    def validate_model_data(self, model_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against model schema"""
        model_class = self.get_model(model_name)
        if not model_class:
            return {'valid': False, 'errors': [f'Model {model_name} not found']}
        
        errors = []
        warnings = []
        
        # Get model columns
        if hasattr(model_class, '__table__'):
            table = model_class.__table__
            
            # Check required fields
            for column in table.columns:
                if not column.nullable and column.name not in data:
                    if not column.default and not column.server_default:
                        errors.append(f'Required field {column.name} is missing')
            
            # Check data types and constraints
            for field_name, value in data.items():
                if hasattr(table.columns, field_name):
                    column = getattr(table.columns, field_name)
                    
                    # Basic type checking
                    if value is not None:
                        try:
                            # This is a simplified validation
                            column.type.python_type
                        except (AttributeError, NotImplementedError):
                            pass  # Skip complex types
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def create_model_instance(self, model_name: str, **kwargs) -> Optional[Any]:
        """Create an instance of a model with provided data"""
        model_class = self.get_model(model_name)
        if not model_class:
            raise ValueError(f'Model {model_name} not found')
        
        validation_result = self.validate_model_data(model_name, kwargs)
        if not validation_result['valid']:
            raise ValueError(f'Validation errors: {validation_result["errors"]}')
        
        return model_class(**kwargs)
    
    def get_model_relationships_info(self, model_name: str) -> Dict[str, Any]:
        """Get relationship information for a specific model"""
        model_class = self.get_model(model_name)
        if not model_class:
            return {}
        
        relationships = {}
        
        if hasattr(model_class, '__mapper__'):
            mapper = model_class.__mapper__
            
            for relationship_name, relationship in mapper.relationships.items():
                relationships[relationship_name] = {
                    'target_model': relationship.mapper.class_.__name__,
                    'direction': str(relationship.direction),
                    'cascade': str(relationship.cascade),
                    'back_populates': getattr(relationship, 'back_populates', None)
                }
        
        return relationships
    
    def get_enum_values(self, enum_class_name: str) -> List[str]:
        """Get all possible values for an enum"""
        enum_mapping = {
            'ContentType': ContentType,
            'ContentStatus': ContentStatus,
            'ContentVisibility': ContentVisibility,
            'UserType': UserType,
            'UserStatus': UserStatus,
            'SubscriptionTier': SubscriptionTier,
            'FingerprintType': FingerprintType,
            'FingerprintAlgorithm': FingerprintAlgorithm,
            'FingerprintStatus': FingerprintStatus,
            'MatchConfidenceLevel': MatchConfidenceLevel,
            'RevenueSource': RevenueSource,
            'RevenueStatus': RevenueStatus,
            'PaymentMethod': PaymentMethod,
            'RevenuePeriod': RevenuePeriod,
            'AnalyticsType': AnalyticsType,
            'MetricType': MetricType,
            'TimeGranularity': TimeGranularity,
            'ProtectionType': ProtectionType,
            'ViolationType': ViolationType,
            'SeverityLevel': SeverityLevel,
            'ProtectionStatus': ProtectionStatus,
            'EnforcementAction': EnforcementAction,
            'LicenseType': LicenseType,
            'LicenseCategory': LicenseCategory,
            'UsageType': UsageType,
            'LicenseStatus': LicenseStatus,
            'PaymentStructure': PaymentStructure
        }
        
        enum_class = enum_mapping.get(enum_class_name)
        if enum_class:
            return [item.value for item in enum_class]
        return []
    
    def setup_database(self, database_url: str, **kwargs):
        """Setup database connection and session"""
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required for database operations")
        
        self._engine = create_engine(database_url, **kwargs)
        Session = sessionmaker(bind=self._engine)
        self._session = Session()
        
        return self._engine, self._session
    
    def create_all_tables(self):
        """Create all model tables in the database"""
        if not self._engine:
            raise RuntimeError("Database engine not configured. Call setup_database first.")
        
        # Import declarative base from models
        from .content_model import Base
        Base.metadata.create_all(self._engine)
    
    def get_session(self) -> Optional[Session]:
        """Get current database session"""
        return self._session
    
    def close_session(self):
        """Close current database session"""
        if self._session:
            self._session.close()
            self._session = None


class ModelQueryBuilder:
    """
    Helper class for building queries across models.
    Provides common query patterns and utilities.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.manager = ModelManager()
    
    def get_user_content_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's content across all types"""
        if not self.session:
            raise RuntimeError("Database session not available")
        
        content_query = self.session.query(ContentModel).filter(
            ContentModel.user_id == user_id,
            ContentModel.is_deleted == False
        )
        
        summary = {
            'total_content': content_query.count(),
            'by_type': {},
            'by_status': {},
            'total_views': 0,
            'total_revenue': 0
        }
        
        for content in content_query.all():
            # Count by type
            content_type = content.content_type
            summary['by_type'][content_type] = summary['by_type'].get(content_type, 0) + 1
            
            # Count by status
            status = content.status
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
            
            # Sum metrics
            summary['total_views'] += content.view_count or 0
            summary['total_revenue'] += float(content.revenue_total or 0)
        
        return summary
    
    def get_user_analytics_overview(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user analytics overview for specified period"""
        from datetime import timedelta
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        analytics_query = self.session.query(AnalyticsModel).filter(
            AnalyticsModel.user_id == user_id,
            AnalyticsModel.measurement_date >= start_date,
            AnalyticsModel.measurement_date <= end_date,
            AnalyticsModel.is_deleted == False
        )
        
        overview = {
            'period_days': days,
            'total_records': analytics_query.count(),
            'metrics_summary': {},
            'top_performing_content': [],
            'growth_trends': {}
        }
        
        # Aggregate metrics
        for analytics in analytics_query.all():
            metric_type = analytics.metric_type
            if metric_type not in overview['metrics_summary']:
                overview['metrics_summary'][metric_type] = {
                    'total_value': 0,
                    'average_value': 0,
                    'count': 0
                }
            
            overview['metrics_summary'][metric_type]['total_value'] += float(analytics.value or 0)
            overview['metrics_summary'][metric_type]['count'] += 1
        
        # Calculate averages
        for metric_data in overview['metrics_summary'].values():
            if metric_data['count'] > 0:
                metric_data['average_value'] = metric_data['total_value'] / metric_data['count']
        
        return overview
    
    def get_protection_alerts(self, user_id: str, severity_levels: List[str] = None) -> List[Dict[str, Any]]:
        """Get active protection alerts for user"""
        query = self.session.query(ProtectionModel).filter(
            ProtectionModel.user_id == user_id,
            ProtectionModel.is_deleted == False,
            ProtectionModel.status.in_([
                ProtectionStatus.DETECTED.value,
                ProtectionStatus.INVESTIGATING.value,
                ProtectionStatus.CONFIRMED.value
            ])
        )
        
        if severity_levels:
            query = query.filter(ProtectionModel.severity_level.in_(severity_levels))
        
        alerts = []
        for protection in query.order_by(ProtectionModel.detected_at.desc()).all():
            alerts.append({
                'id': protection.id,
                'protection_type': protection.protection_type,
                'severity_level': protection.severity_level,
                'detected_url': protection.detected_url,
                'detected_platform': protection.detected_platform,
                'detected_at': protection.detected_at.isoformat() if protection.detected_at else None,
                'similarity_score': protection.similarity_score,
                'status': protection.status
            })
        
        return alerts


# Global model manager instance
model_manager = ModelManager()

# Convenience functions
def get_model(name: str):
    """Get model class by name"""
    return model_manager.get_model(name)

def create_instance(model_name: str, **kwargs):
    """Create model instance with validation"""
    return model_manager.create_model_instance(model_name, **kwargs)

def get_enum_values(enum_name: str):
    """Get enum values"""
    return model_manager.get_enum_values(enum_name)

def setup_database(database_url: str, **kwargs):
    """Setup database connection"""
    return model_manager.setup_database(database_url, **kwargs)

# Export all for easy access
__all__ = [
    # Models
    'ContentModel', 'UserModel', 'FingerprintModel', 'RevenueModel',
    'AnalyticsModel', 'ProtectionModel', 'LicensingModel',
    
    # Enums
    'ContentType', 'ContentStatus', 'ContentVisibility',
    'UserType', 'UserStatus', 'SubscriptionTier',
    'FingerprintType', 'FingerprintAlgorithm', 'FingerprintStatus', 'MatchConfidenceLevel',
    'RevenueSource', 'RevenueStatus', 'PaymentMethod', 'RevenuePeriod',
    'AnalyticsType', 'MetricType', 'TimeGranularity',
    'ProtectionType', 'ViolationType', 'SeverityLevel', 'ProtectionStatus', 'EnforcementAction',
    'LicenseType', 'LicenseCategory', 'UsageType', 'LicenseStatus', 'PaymentStructure',
    
    # Utilities
    'ModelManager', 'ModelQueryBuilder', 'model_manager',
    'get_model', 'create_instance', 'get_enum_values', 'setup_database',
    'MODEL_REGISTRY', 'RELATIONSHIP_MAPPINGS'
]
