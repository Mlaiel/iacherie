"""IA Influencer Agent - Schema Evolution Registry
Schema Evolution and Compatibility Management for Ainflue Event Streaming

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. This is proprietary technology.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import hashlib
from uuid import uuid4
from collections import defaultdict

logger = logging.getLogger(__name__)


class CompatibilityType(Enum):
    """Schema compatibility types"""
    BACKWARD = "backward"
    FORWARD = "forward"
    FULL = "full"
    NONE = "none"
    TRANSITIVE = "transitive"


class SchemaType(Enum):
    """Schema format types"""
    JSON_SCHEMA = "json_schema"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    THRIFT = "thrift"
    CUSTOM = "custom"


class EvolutionType(Enum):
    """Types of schema evolution"""
    FIELD_ADDITION = "field_addition"
    FIELD_REMOVAL = "field_removal"
    FIELD_RENAME = "field_rename"
    TYPE_CHANGE = "type_change"
    DEFAULT_VALUE_CHANGE = "default_value_change"
    CONSTRAINT_CHANGE = "constraint_change"
    METADATA_CHANGE = "metadata_change"


@dataclass
class SchemaVersion:
    """Schema version information"""
    
    schema_id: str
    version: int
    schema_content: Dict[str, Any]
    schema_type: SchemaType
    compatibility_type: CompatibilityType
    created_at: datetime
    created_by: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    checksum: Optional[str] = None
    
    def __post_init__(self) -> None:
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate schema content checksum"""
        content_str = json.dumps(self.schema_content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()


@dataclass
class MigrationRule:
    """Rule for migrating between schema versions"""
    
    rule_id: str
    from_version: int
    to_version: int
    rule_type: EvolutionType
    field_path: str
    transformation: Dict[str, Any]
    condition: Optional[str] = None
    description: Optional[str] = None
    
    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply migration rule to data"""
        try:
            if self.rule_type == EvolutionType.FIELD_ADDITION:
                return self._apply_field_addition(data)
            elif self.rule_type == EvolutionType.FIELD_REMOVAL:
                return self._apply_field_removal(data)
            elif self.rule_type == EvolutionType.FIELD_RENAME:
                return self._apply_field_rename(data)
            elif self.rule_type == EvolutionType.TYPE_CHANGE:
                return self._apply_type_change(data)
            elif self.rule_type == EvolutionType.DEFAULT_VALUE_CHANGE:
                return self._apply_default_value_change(data)
            else:
                logger.warning(f"Unsupported migration rule type: {self.rule_type}")
                return data
                
        except Exception as e:
            logger.error(f"Error applying migration rule {self.rule_id}: {e}")
            return data
    
    def _apply_field_addition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply field addition migration"""
        default_value = self.transformation.get("default_value")
        self._set_nested_field(data, self.field_path, default_value)
        return data
    
    def _apply_field_removal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply field removal migration"""
        self._remove_nested_field(data, self.field_path)
        return data
    
    def _apply_field_rename(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply field rename migration"""
        old_name = self.transformation.get("old_name")
        new_name = self.transformation.get("new_name")
        
        if old_name and new_name:
            value = self._get_nested_field(data, old_name)
            if value is not None:
                self._set_nested_field(data, new_name, value)
                self._remove_nested_field(data, old_name)
        
        return data
    
    def _apply_type_change(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply type change migration"""
        converter = self.transformation.get("converter")
        
        if converter:
            value = self._get_nested_field(data, self.field_path)
            if value is not None:
                try:
                    if converter == "string_to_int":
                        converted_value = int(str(value))
                    elif converter == "int_to_string":
                        converted_value = str(value)
                    elif converter == "string_to_float":
                        converted_value = float(str(value))
                    elif converter == "timestamp_to_iso":
                        if isinstance(value, (int, float)):
                            converted_value = datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
                        else:
                            converted_value = value
                    else:
                        converted_value = value
                    
                    self._set_nested_field(data, self.field_path, converted_value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Type conversion failed for field {self.field_path}: {e}")
        
        return data
    
    def _apply_default_value_change(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default value change migration"""
        current_value = self._get_nested_field(data, self.field_path)
        old_default = self.transformation.get("old_default")
        new_default = self.transformation.get("new_default")
        
        if current_value == old_default:
            self._set_nested_field(data, self.field_path, new_default)
        
        return data
    
    def _get_nested_field(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested field path"""
        try:
            current = data
            for part in field_path.split('.'):
                current = current.get(part)
                if current is None:
                    return None
            return current
        except Exception:
            return None
    
    def _set_nested_field(self, data -> None: Dict[str, Any], field_path -> None: str, value -> None: Any) -> None:
        """Set value for nested field path"""
        try:
            parts = field_path.split('.')
            current = data
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = value
        except Exception as e:
            logger.error(f"Error setting nested field {field_path}: {e}")
    
    def _remove_nested_field(self, data -> None: Dict[str, Any], field_path -> None: str) -> None:
        """Remove nested field"""
        try:
            parts = field_path.split('.')
            current = data
            
            for part in parts[:-1]:
                current = current.get(part, {})
                if not isinstance(current, dict):
                    return
            
            if isinstance(current, dict) and parts[-1] in current:
                del current[parts[-1]]
        except Exception as e:
            logger.error(f"Error removing nested field {field_path}: {e}")


@dataclass
class CompatibilityCheck:
    """Result of schema compatibility check"""
    
    is_compatible: bool
    compatibility_type: CompatibilityType
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    required_migrations: List[MigrationRule] = field(default_factory=list)


class AinflueBusinesSchemas:
    """Predefined schema templates for Ainflue business events"""
    
    CONTENT_UPLOAD_SCHEMA = {
        "type": "object",
        "properties": {
            "event_id": {"type": "string"},
            "event_type": {"type": "string", "enum": ["content_upload_started", "content_upload_completed"]},
            "timestamp": {"type": "string", "format": "date-time"},
            "creator_id": {"type": "string"},
            "content_id": {"type": "string"},
            "content_type": {"type": "string", "enum": ["audio", "video", "image", "blog", "podcast"]},
            "content_size": {"type": "integer", "minimum": 0},
            "metadata": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "duration": {"type": "number", "minimum": 0}
                }
            }
        },
        "required": ["event_id", "event_type", "timestamp", "creator_id", "content_type"]
    }
    
    REVENUE_EVENT_SCHEMA = {
        "type": "object",
        "properties": {
            "event_id": {"type": "string"},
            "event_type": {"type": "string", "enum": ["revenue_generated", "payment_processed", "commission_calculated"]},
            "timestamp": {"type": "string", "format": "date-time"},
            "creator_id": {"type": "string"},
            "amount": {"type": "number", "minimum": 0},
            "currency": {"type": "string", "default": "USD"},
            "revenue_type": {"type": "string", "enum": ["subscription", "tip", "collaboration", "platform_share"]},
            "transaction_id": {"type": "string"},
            "platform_fee": {"type": "number", "minimum": 0}
        },
        "required": ["event_id", "event_type", "timestamp", "creator_id", "amount", "revenue_type"]
    }
    
    COLLABORATION_EVENT_SCHEMA = {
        "type": "object",
        "properties": {
            "event_id": {"type": "string"},
            "event_type": {"type": "string", "enum": ["collaboration_request_sent", "collaboration_accepted", "collaboration_completed"]},
            "timestamp": {"type": "string", "format": "date-time"},
            "requester_id": {"type": "string"},
            "target_creator_id": {"type": "string"},
            "collaboration_type": {"type": "string", "enum": ["content_creation", "cross_promotion", "revenue_share"]},
            "collaboration_id": {"type": "string"},
            "terms": {
                "type": "object",
                "properties": {
                    "duration": {"type": "string"},
                    "revenue_split": {"type": "number", "minimum": 0, "maximum": 1},
                    "deliverables": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "required": ["event_id", "event_type", "timestamp", "requester_id", "collaboration_type"]
    }


class SchemaValidator:
    """Validates data against schemas"""
    
    def __init__(self) -> None:
        # In a real implementation, would use jsonschema or similar library
        pass
    
    def validate(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate data against schema"""
        try:
            errors = []
            
            # Basic validation implementation
            if schema.get("type") == "object":
                if not isinstance(data, dict):
                    errors.append("Data must be an object")
                    return False, errors
                
                # Check required fields
                required_fields = schema.get("required", [])
                for field in required_fields:
                    if field not in data:
                        errors.append(f"Missing required field: {field}")
                
                # Check properties
                properties = schema.get("properties", {})
                for field_name, field_schema in properties.items():
                    if field_name in data:
                        field_valid, field_errors = self._validate_field(data[field_name], field_schema, field_name)
                        if not field_valid:
                            errors.extend(field_errors)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Error validating schema: {e}")
            return False, [str(e)]
    
    def _validate_field(self, value: Any, field_schema: Dict[str, Any], field_name: str) -> Tuple[bool, List[str]]:
        """Validate individual field"""
        errors = []
        
        try:
            field_type = field_schema.get("type")
            
            if field_type == "string" and not isinstance(value, str):
                errors.append(f"Field {field_name} must be a string")
            elif field_type == "integer" and not isinstance(value, int):
                errors.append(f"Field {field_name} must be an integer")
            elif field_type == "number" and not isinstance(value, (int, float)):
                errors.append(f"Field {field_name} must be a number")
            elif field_type == "boolean" and not isinstance(value, bool):
                errors.append(f"Field {field_name} must be a boolean")
            elif field_type == "array" and not isinstance(value, list):
                errors.append(f"Field {field_name} must be an array")
            elif field_type == "object" and not isinstance(value, dict):
                errors.append(f"Field {field_name} must be an object")
            
            # Check enum constraints
            if "enum" in field_schema and value not in field_schema["enum"]:
                errors.append(f"Field {field_name} value '{value}' not in allowed values: {field_schema['enum']}")
            
            # Check minimum/maximum for numbers
            if field_type in ["integer", "number"]:
                if "minimum" in field_schema and value < field_schema["minimum"]:
                    errors.append(f"Field {field_name} value {value} is below minimum {field_schema['minimum']}")
                if "maximum" in field_schema and value > field_schema["maximum"]:
                    errors.append(f"Field {field_name} value {value} is above maximum {field_schema['maximum']}")
            
        except Exception as e:
            errors.append(f"Error validating field {field_name}: {e}")
        
        return len(errors) == 0, errors


class CompatibilityChecker:
    """Checks compatibility between schema versions"""
    
    def check_compatibility(self, 
                          old_schema: SchemaVersion, 
                          new_schema: SchemaVersion,
                          compatibility_type: CompatibilityType) -> CompatibilityCheck:
        """Check compatibility between two schema versions"""
        try:
            if compatibility_type == CompatibilityType.BACKWARD:
                return self._check_backward_compatibility(old_schema, new_schema)
            elif compatibility_type == CompatibilityType.FORWARD:
                return self._check_forward_compatibility(old_schema, new_schema)
            elif compatibility_type == CompatibilityType.FULL:
                return self._check_full_compatibility(old_schema, new_schema)
            else:
                return CompatibilityCheck(
                    is_compatible=True,
                    compatibility_type=compatibility_type,
                    warnings=["No compatibility checking performed"]
                )
                
        except Exception as e:
            logger.error(f"Error checking compatibility: {e}")
            return CompatibilityCheck(
                is_compatible=False,
                compatibility_type=compatibility_type,
                issues=[str(e)]
            )
    
    def _check_backward_compatibility(self, old_schema: SchemaVersion, new_schema: SchemaVersion) -> CompatibilityCheck:
        """Check backward compatibility (new schema can read old data)"""
        issues = []
        warnings = []
        required_migrations = []
        
        old_props = old_schema.schema_content.get("properties", {})
        new_props = new_schema.schema_content.get("properties", {})
        old_required = set(old_schema.schema_content.get("required", []))
        new_required = set(new_schema.schema_content.get("required", []))
        
        # Check for removed fields
        removed_fields = set(old_props.keys()) - set(new_props.keys())
        if removed_fields:
            issues.extend([f"Field removed: {field}" for field in removed_fields])
            required_migrations.extend([
                MigrationRule(
                    rule_id=str(uuid4()),
                    from_version=old_schema.version,
                    to_version=new_schema.version,
                    rule_type=EvolutionType.FIELD_REMOVAL,
                    field_path=field,
                    transformation={}
                ) for field in removed_fields
            ])
        
        # Check for new required fields (breaks backward compatibility)
        new_required_fields = new_required - old_required
        if new_required_fields:
            issues.extend([f"New required field: {field}" for field in new_required_fields])
        
        # Check for type changes
        for field_name in old_props.keys() & new_props.keys():
            old_type = old_props[field_name].get("type")
            new_type = new_props[field_name].get("type")
            
            if old_type != new_type:
                if self._is_compatible_type_change(old_type, new_type):
                    warnings.append(f"Type change for field {field_name}: {old_type} -> {new_type}")
                    required_migrations.append(
                        MigrationRule(
                            rule_id=str(uuid4()),
                            from_version=old_schema.version,
                            to_version=new_schema.version,
                            rule_type=EvolutionType.TYPE_CHANGE,
                            field_path=field_name,
                            transformation={"converter": f"{old_type}_to_{new_type}"}
                        )
                    )
                else:
                    issues.append(f"Incompatible type change for field {field_name}: {old_type} -> {new_type}")
        
        is_compatible = len(issues) == 0
        
        return CompatibilityCheck(
            is_compatible=is_compatible,
            compatibility_type=CompatibilityType.BACKWARD,
            issues=issues,
            warnings=warnings,
            required_migrations=required_migrations
        )
    
    def _check_forward_compatibility(self, old_schema: SchemaVersion, new_schema: SchemaVersion) -> CompatibilityCheck:
        """Check forward compatibility (old schema can read new data)"""
        issues = []
        warnings = []
        
        old_props = old_schema.schema_content.get("properties", {})
        new_props = new_schema.schema_content.get("properties", {})
        
        # Check for new fields without defaults
        new_fields = set(new_props.keys()) - set(old_props.keys())
        for field in new_fields:
            if "default" not in new_props[field]:
                issues.append(f"New field without default: {field}")
            else:
                warnings.append(f"New field with default: {field}")
        
        is_compatible = len(issues) == 0
        
        return CompatibilityCheck(
            is_compatible=is_compatible,
            compatibility_type=CompatibilityType.FORWARD,
            issues=issues,
            warnings=warnings
        )
    
    def _check_full_compatibility(self, old_schema: SchemaVersion, new_schema: SchemaVersion) -> CompatibilityCheck:
        """Check full compatibility (both directions)"""
        backward_check = self._check_backward_compatibility(old_schema, new_schema)
        forward_check = self._check_forward_compatibility(old_schema, new_schema)
        
        return CompatibilityCheck(
            is_compatible=backward_check.is_compatible and forward_check.is_compatible,
            compatibility_type=CompatibilityType.FULL,
            issues=backward_check.issues + forward_check.issues,
            warnings=backward_check.warnings + forward_check.warnings,
            required_migrations=backward_check.required_migrations
        )
    
    def _is_compatible_type_change(self, old_type: str, new_type: str) -> bool:
        """Check if type change is compatible"""
        compatible_changes = {
            ("integer", "number"),
            ("integer", "string"),
            ("number", "string"),
        }
        
        return (old_type, new_type) in compatible_changes


class SchemaEvolutionRegistry:
    """Main registry for managing schema evolution in Ainflue platform"""
    
    def __init__(self, metrics_collector=None) -> None:
        self.metrics_collector = metrics_collector
        self.schemas: Dict[str, List[SchemaVersion]] = defaultdict(list)
        self.migration_rules: Dict[str, List[MigrationRule]] = defaultdict(list)
        self.validator = SchemaValidator()
        self.compatibility_checker = CompatibilityChecker()
        
        # Initialize with Ainflue business schemas
        self._initialize_business_schemas()
    
    def _initialize_business_schemas(self) -> None:
        """Initialize with predefined Ainflue business schemas"""
        try:
            # Content upload schema
            content_schema = SchemaVersion(
                schema_id="ainflue.content.upload",
                version=1,
                schema_content=AinflueBusinesSchemas.CONTENT_UPLOAD_SCHEMA,
                schema_type=SchemaType.JSON_SCHEMA,
                compatibility_type=CompatibilityType.BACKWARD,
                created_at=datetime.now(timezone.utc),
                created_by="system",
                description="Schema for content upload events",
                tags=["content", "upload", "core"]
            )
            self.schemas["ainflue.content.upload"].append(content_schema)
            
            # Revenue event schema
            revenue_schema = SchemaVersion(
                schema_id="ainflue.revenue.event",
                version=1,
                schema_content=AinflueBusinesSchemas.REVENUE_EVENT_SCHEMA,
                schema_type=SchemaType.JSON_SCHEMA,
                compatibility_type=CompatibilityType.BACKWARD,
                created_at=datetime.now(timezone.utc),
                created_by="system",
                description="Schema for revenue and payment events",
                tags=["revenue", "payment", "finance"]
            )
            self.schemas["ainflue.revenue.event"].append(revenue_schema)
            
            # Collaboration event schema
            collaboration_schema = SchemaVersion(
                schema_id="ainflue.collaboration.event",
                version=1,
                schema_content=AinflueBusinesSchemas.COLLABORATION_EVENT_SCHEMA,
                schema_type=SchemaType.JSON_SCHEMA,
                compatibility_type=CompatibilityType.BACKWARD,
                created_at=datetime.now(timezone.utc),
                created_by="system",
                description="Schema for collaboration events",
                tags=["collaboration", "creator", "matching"]
            )
            self.schemas["ainflue.collaboration.event"].append(collaboration_schema)
            
            logger.info("Initialized Ainflue business schemas")
            
        except Exception as e:
            logger.error(f"Error initializing business schemas: {e}")
    
    def register_schema(self, schema_version: SchemaVersion) -> bool:
        """Register a new schema version"""
        try:
            schema_id = schema_version.schema_id
            
            # Check if this is a new schema or evolution
            existing_versions = self.schemas[schema_id]
            
            if existing_versions:
                # This is an evolution - check compatibility
                latest_version = max(existing_versions, key=lambda s: s.version)
                compatibility_check = self.compatibility_checker.check_compatibility(
                    latest_version, schema_version, schema_version.compatibility_type
                )
                
                if not compatibility_check.is_compatible:
                    logger.error(f"Schema {schema_id} v{schema_version.version} is not compatible: {compatibility_check.issues}")
                    return False
                
                # Store migration rules if any
                if compatibility_check.required_migrations:
                    self.migration_rules[schema_id].extend(compatibility_check.required_migrations)
                
                # Log warnings
                for warning in compatibility_check.warnings:
                    logger.warning(f"Schema {schema_id} v{schema_version.version}: {warning}")
            
            # Register the schema
            self.schemas[schema_id].append(schema_version)
            
            # Sort versions
            self.schemas[schema_id].sort(key=lambda s: s.version)
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("schema_versions_registered")
            
            logger.info(f"Registered schema {schema_id} version {schema_version.version}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering schema: {e}")
            return False
    
    def get_schema(self, schema_id: str, version: Optional[int] = None) -> Optional[SchemaVersion]:
        """Get schema by ID and version (latest if version not specified)"""
        try:
            versions = self.schemas.get(schema_id, [])
            
            if not versions:
                return None
            
            if version is None:
                # Return latest version
                return max(versions, key=lambda s: s.version)
            else:
                # Return specific version
                for schema_version in versions:
                    if schema_version.version == version:
                        return schema_version
                return None
                
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            return None
    
    def validate_data(self, data: Dict[str, Any], schema_id: str, version: Optional[int] = None) -> Tuple[bool, List[str]]:
        """Validate data against schema"""
        try:
            schema_version = self.get_schema(schema_id, version)
            
            if not schema_version:
                return False, [f"Schema {schema_id} not found"]
            
            is_valid, errors = self.validator.validate(data, schema_version.schema_content)
            
            if self.metrics_collector:
                if is_valid:
                    self.metrics_collector.increment_counter("schema_validations_successful")
                else:
                    self.metrics_collector.increment_counter("schema_validations_failed")
            
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return False, [str(e)]
    
    def migrate_data(self, data: Dict[str, Any], schema_id: str, from_version: int, to_version: int) -> Dict[str, Any]:
        """Migrate data between schema versions"""
        try:
            if from_version == to_version:
                return data
            
            # Get migration path
            migration_path = self._get_migration_path(schema_id, from_version, to_version)
            
            if not migration_path:
                logger.warning(f"No migration path found from version {from_version} to {to_version}")
                return data
            
            # Apply migrations in sequence
            migrated_data = data.copy()
            
            for rule in migration_path:
                migrated_data = rule.apply(migrated_data)
                logger.debug(f"Applied migration rule {rule.rule_id}")
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("schema_migrations_performed")
            
            logger.info(f"Migrated data from schema {schema_id} v{from_version} to v{to_version}")
            return migrated_data
            
        except Exception as e:
            logger.error(f"Error migrating data: {e}")
            return data
    
    def _get_migration_path(self, schema_id: str, from_version: int, to_version: int) -> List[MigrationRule]:
        """Get ordered list of migration rules to transform from one version to another"""
        try:
            rules = self.migration_rules.get(schema_id, [])
            
            if from_version < to_version:
                # Forward migration
                applicable_rules = [
                    rule for rule in rules
                    if from_version <= rule.from_version < to_version
                ]
                return sorted(applicable_rules, key=lambda r: r.from_version)
            
            elif from_version > to_version:
                # Backward migration (reverse rules)
                applicable_rules = [
                    rule for rule in rules
                    if to_version <= rule.to_version < from_version
                ]
                # Would need reverse migration rules for proper backward migration
                logger.warning("Backward migration not fully supported")
                return []
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting migration path: {e}")
            return []
    
    def get_registry_metrics(self) -> Dict[str, Any]:
        """Get comprehensive registry metrics"""
        try:
            total_schemas = len(self.schemas)
            total_versions = sum(len(versions) for versions in self.schemas.values())
            total_migration_rules = sum(len(rules) for rules in self.migration_rules.values())
            
            schema_details = {}
            for schema_id, versions in self.schemas.items():
                latest_version = max(versions, key=lambda s: s.version) if versions else None
                schema_details[schema_id] = {
                    "total_versions": len(versions),
                    "latest_version": latest_version.version if latest_version else 0,
                    "schema_type": latest_version.schema_type.value if latest_version else "unknown",
                    "compatibility_type": latest_version.compatibility_type.value if latest_version else "unknown"
                }
            
            return {
                "total_schemas": total_schemas,
                "total_versions": total_versions,
                "total_migration_rules": total_migration_rules,
                "schema_details": schema_details,
                "registry_health": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Error getting registry metrics: {e}")
            return {"error": str(e)}


# Export public API
__all__ = [
    "SchemaEvolutionRegistry", "SchemaVersion", "MigrationRule", "CompatibilityCheck",
    "SchemaValidator", "CompatibilityChecker", "AinflueBusinesSchemas",
    "CompatibilityType", "SchemaType", "EvolutionType"
]