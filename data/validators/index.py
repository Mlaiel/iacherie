"""
Validator Index - Central validation system orchestrator
========================================================

Main validation engine and registry system for coordinating all validators
in the IA Influencer Agent Platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Type, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class ValidationMode(Enum):
    """Validation execution modes."""
    SYNC = "sync"
    ASYNC = "async"
    PARALLEL = "parallel"
    STREAMING = "streaming"


class ValidationPriority(Enum):
    """Validation priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ValidationConfig:
    """Global validation configuration."""
    strict_mode: bool = True
    cache_enabled: bool = True
    parallel_processing: bool = True
    max_workers: int = 4
    timeout: int = 30
    log_level: str = "INFO"
    
    # Performance settings
    cache_ttl: int = 3600
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    chunk_size: int = 1024 * 1024  # 1MB
    
    # Security settings
    antivirus_enabled: bool = True
    content_scanning: bool = True
    input_sanitization: bool = True
    
    # Quality settings
    min_quality_score: float = 60.0
    enable_ai_analysis: bool = True
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""



        return {
            "strict_mode": self.strict_mode,
            "cache_enabled": self.cache_enabled,
            "parallel_processing": self.parallel_processing,
            "max_workers": self.max_workers,
            "timeout": self.timeout,
            "log_level": self.log_level,
            "cache_ttl": self.cache_ttl,
            "max_file_size": self.max_file_size,
            "chunk_size": self.chunk_size,
            "antivirus_enabled": self.antivirus_enabled,
            "content_scanning": self.content_scanning,
            "input_sanitization": self.input_sanitization,
            "min_quality_score": self.min_quality_score,
            "enable_ai_analysis": self.enable_ai_analysis
        }


@dataclass
class ValidatorInfo:
    """Validator registration information."""
    name: str
    validator_class: Type
    description: str
    version: str
    capabilities: List[str]
    dependencies: List[str] = field(default_factory=list)
    priority: ValidationPriority = ValidationPriority.NORMAL
    enabled: bool = True


@dataclass
class ValidationRequest:
    """Validation request structure."""
    request_id: str
    validator_name: str
    data: Any
    options: Dict[str, Any] = field(default_factory=dict)
    priority: ValidationPriority = ValidationPriority.NORMAL
    timeout: Optional[int] = None
    callback: Optional[Callable] = None


@dataclass
class ValidationResponse:
    """Validation response structure."""
    request_id: str
    validator_name: str
    result: Any
    success: bool
    duration: float
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ValidatorRegistry:
    """
    Central registry for all validators.
    
    Manages validator registration, discovery, and lifecycle.
    """
    
    def __init__(self):
        """Initialize validator registry."""
        self._validators: Dict[str, ValidatorInfo] = {}
        self._instances: Dict[str, Any] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        
        # Auto-register built-in validators
        self._register_builtin_validators()
        
        logger.info("ValidatorRegistry initialized")
    
    def register_validator(
        self,
        name: str,
        validator_class: Type,
        description: str = "",
        version: str = "1.0.0",
        capabilities: List[str] = None,
        dependencies: List[str] = None,
        priority: ValidationPriority = ValidationPriority.NORMAL,
        enabled: bool = True
    ) -> None:
        """
        Register a validator.
        
        Args:
            name: Validator name
            validator_class: Validator class
            description: Validator description
            version: Validator version
            capabilities: List of capabilities
            dependencies: List of dependencies
            priority: Validation priority
            enabled: Whether validator is enabled
        """



        try:
            info = ValidatorInfo(
                name=name,
                validator_class=validator_class,
                description=description,
                version=version,
                capabilities=capabilities or [],
                dependencies=dependencies or [],
                priority=priority,
                enabled=enabled
            )
            
            self._validators[name] = info
            self._locks[name] = asyncio.Lock()
            
            logger.info(f"Registered validator: {name}")
            
        except Exception as e:
            logger.error(f"Failed to register validator {name}: {str(e)}")
            raise
    
    def unregister_validator(self, name: str) -> None:
        """
        Unregister a validator.
        
        Args:
            name: Validator name
        """



        try:
            if name in self._validators:
                del self._validators[name]
                
                if name in self._instances:
                    del self._instances[name]
                
                if name in self._locks:
                    del self._locks[name]
                
                logger.info(f"Unregistered validator: {name}")
            
        except Exception as e:
            logger.error(f"Failed to unregister validator {name}: {str(e)}")
    
    async def get_validator(self, name: str, config: Optional[ValidationConfig] = None) -> Any:
        """
        Get validator instance.
        
        Args:
            name: Validator name
            config: Validation configuration
            
        Returns:
            Validator instance
        """



        try:
            if name not in self._validators:
                raise ValueError(f"Validator '{name}' not registered")
            
            validator_info = self._validators[name]
            
            if not validator_info.enabled:
                raise ValueError(f"Validator '{name}' is disabled")
            
            # Use lock to ensure thread-safe instance creation
            async with self._locks[name]:
                if name not in self._instances:
                    # Create new instance
                    validator_class = validator_info.validator_class
                    
                    # Pass config if constructor accepts it
                    try:
                        if config:
                            instance = validator_class(config=config.dict())
                        else:
                            instance = validator_class()
                    except TypeError:
                        # Fallback for constructors without config parameter
                        instance = validator_class()
                    
                    self._instances[name] = instance
                    logger.debug(f"Created validator instance: {name}")
                
                return self._instances[name]
            
        except Exception as e:
            logger.error(f"Failed to get validator {name}: {str(e)}")
            raise
    
    def get_available_validators(self) -> List[str]:
        """
        Get list of available validators.
        
        Returns:
            List of validator names
        """



        return [name for name, info in self._validators.items() if info.enabled]
    
    def get_validator_info(self, name: str) -> Optional[ValidatorInfo]:
        """
        Get validator information.
        
        Args:
            name: Validator name
            
        Returns:
            Validator information or None
        """



        return self._validators.get(name)
    
    def get_validators_by_capability(self, capability: str) -> List[str]:
        """
        Get validators by capability.
        
        Args:
            capability: Required capability
            
        Returns:
            List of validator names
        """



        return [
            name for name, info in self._validators.items()
            if info.enabled and capability in info.capabilities
        ]
    
    def enable_validator(self, name: str) -> None:
        """Enable a validator."""
        if name in self._validators:
            self._validators[name].enabled = True
            logger.info(f"Enabled validator: {name}")
    
    def disable_validator(self, name: str) -> None:
        """Disable a validator."""
        if name in self._validators:
            self._validators[name].enabled = False
            logger.info(f"Disabled validator: {name}")
    
    def _register_builtin_validators(self) -> None:
        """Register built-in validators."""



        try:
            # Import validator classes
            from .content_validator import ContentValidator
            from .schema_validator import SchemaValidator
            from .security_validator import SecurityValidator
            from .business_validator import BusinessValidator
            from .file_validator import FileValidator
            from .metadata_validator import MetadataValidator
            from .quality_validator import QualityValidator
            from .compliance_validator import ComplianceValidator
            from .performance_validator import PerformanceValidator
            from .chain_validator import ChainValidator
            
            # Register each validator
            self.register_validator(
                name="content",
                validator_class=ContentValidator,
                description="Multi-format content validation",
                capabilities=["content", "audio", "video", "image", "text"],
                priority=ValidationPriority.HIGH
            )
            
            self.register_validator(
                name="schema",
                validator_class=SchemaValidator,
                description="Schema and structure validation",
                capabilities=["schema", "json", "pydantic", "structure"],
                priority=ValidationPriority.HIGH
            )
            
            self.register_validator(
                name="security",
                validator_class=SecurityValidator,
                description="Security and safety validation",
                capabilities=["security", "malware", "injection", "sanitization"],
                priority=ValidationPriority.CRITICAL
            )
            
            self.register_validator(
                name="business",
                validator_class=BusinessValidator,
                description="Business rules validation",
                capabilities=["business", "rules", "licensing", "monetization"],
                priority=ValidationPriority.NORMAL
            )
            
            self.register_validator(
                name="file",
                validator_class=FileValidator,
                description="File integrity validation",
                capabilities=["file", "integrity", "checksum", "signature"],
                priority=ValidationPriority.HIGH
            )
            
            self.register_validator(
                name="metadata",
                validator_class=MetadataValidator,
                description="Metadata validation",
                capabilities=["metadata", "id3", "exif", "xmp"],
                priority=ValidationPriority.NORMAL
            )
            
            self.register_validator(
                name="quality",
                validator_class=QualityValidator,
                description="Content quality assessment",
                capabilities=["quality", "assessment", "scoring", "analysis"],
                priority=ValidationPriority.NORMAL
            )
            
            self.register_validator(
                name="compliance",
                validator_class=ComplianceValidator,
                description="Platform compliance validation",
                capabilities=["compliance", "platform", "legal", "gdpr"],
                priority=ValidationPriority.HIGH
            )
            
            self.register_validator(
                name="performance",
                validator_class=PerformanceValidator,
                description="Performance metrics validation",
                capabilities=["performance", "metrics", "benchmark", "optimization"],
                priority=ValidationPriority.LOW
            )
            
            self.register_validator(
                name="chain",
                validator_class=ChainValidator,
                description="Validation chain orchestrator",
                capabilities=["chain", "pipeline", "orchestration", "workflow"],
                priority=ValidationPriority.NORMAL
            )
            
        except ImportError as e:
            logger.warning(f"Some validators could not be imported: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to register built-in validators: {str(e)}")


class ValidationManager:
    """
    Manages validation execution and coordination.
    
    Handles request queuing, execution, and result management.
    """
    
    def __init__(self, config: ValidationConfig, registry: ValidatorRegistry):
        """
        Initialize validation manager.
        
        Args:
            config: Validation configuration
            registry: Validator registry
        """
        self.config = config
        self.registry = registry
        
        # Execution management
        self._request_queue = asyncio.Queue()
        self._active_requests: Dict[str, ValidationRequest] = {}
        self._results_cache: Dict[str, ValidationResponse] = {}
        
        # Threading
        self._executor = ThreadPoolExecutor(max_workers=config.max_workers)
        
        # Statistics
        self._stats = {
            "total_requests": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "cache_hits": 0,
            "average_duration": 0.0
        }
        
        logger.info("ValidationManager initialized")
    
    async def validate(
        self,
        validator_name: str,
        data: Any,
        options: Dict[str, Any] = None,
        priority: ValidationPriority = ValidationPriority.NORMAL,
        timeout: Optional[int] = None
    ) -> ValidationResponse:
        """
        Execute validation.
        
        Args:
            validator_name: Name of validator to use
            data: Data to validate
            options: Validation options
            priority: Request priority
            timeout: Request timeout
            
        Returns:
            Validation response
        """
        request_id = f"req_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            # Create validation request
            request = ValidationRequest(
                request_id=request_id,
                validator_name=validator_name,
                data=data,
                options=options or {},
                priority=priority,
                timeout=timeout or self.config.timeout
            )
            
            # Check cache first
            if self.config.cache_enabled:
                cache_key = self._generate_cache_key(request)
                if cache_key in self._results_cache:
                    self._stats["cache_hits"] += 1
                    return self._results_cache[cache_key]
            
            # Get validator instance
            validator = await self.registry.get_validator(validator_name, self.config)
            
            # Execute validation
            result = await self._execute_validation(validator, request)
            
            # Create response
            duration = time.time() - start_time
            response = ValidationResponse(
                request_id=request_id,
                validator_name=validator_name,
                result=result,
                success=True,
                duration=duration
            )
            
            # Cache result
            if self.config.cache_enabled:
                cache_key = self._generate_cache_key(request)
                self._results_cache[cache_key] = response
            
            # Update statistics
            self._update_stats(True, duration)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Validation failed for {validator_name}: {str(e)}")
            
            response = ValidationResponse(
                request_id=request_id,
                validator_name=validator_name,
                result=None,
                success=False,
                duration=duration,
                error=str(e)
            )
            
            self._update_stats(False, duration)
            return response
    
    async def validate_batch(
        self,
        requests: List[Dict[str, Any]],
        mode: ValidationMode = ValidationMode.PARALLEL
    ) -> List[ValidationResponse]:
        """
        Execute batch validation.
        
        Args:
            requests: List of validation requests
            mode: Execution mode
            
        Returns:
            List of validation responses
        """



        try:
            if mode == ValidationMode.PARALLEL:
                # Execute in parallel
                tasks = [
                    self.validate(
                        validator_name=req["validator"],
                        data=req["data"],
                        options=req.get("options", {}),
                        priority=ValidationPriority(req.get("priority", "normal")),
                        timeout=req.get("timeout")
                    )
                    for req in requests
                ]
                
                return await asyncio.gather(*tasks, return_exceptions=False)
            
            else:
                # Execute sequentially
                results = []
                for req in requests:
                    result = await self.validate(
                        validator_name=req["validator"],
                        data=req["data"],
                        options=req.get("options", {}),
                        priority=ValidationPriority(req.get("priority", "normal")),
                        timeout=req.get("timeout")
                    )
                    results.append(result)
                
                return results
            
        except Exception as e:
            logger.error(f"Batch validation failed: {str(e)}")
            # Return error responses for all requests
            return [
                ValidationResponse(
                    request_id=f"batch_error_{i}",
                    validator_name=req.get("validator", "unknown"),
                    result=None,
                    success=False,
                    duration=0.0,
                    error=str(e)
                )
                for i, req in enumerate(requests)
            ]
    
    async def validate_chain(
        self,
        validators: List[Dict[str, Any]],
        data: Any,
        stop_on_error: bool = True
    ) -> List[ValidationResponse]:
        """
        Execute validation chain.
        
        Args:
            validators: List of validators to execute
            data: Data to validate
            stop_on_error: Whether to stop on first error
            
        Returns:
            List of validation responses
        """
        results = []
        current_data = data
        
        try:
            for validator_config in validators:
                validator_name = validator_config["name"]
                options = validator_config.get("options", {})
                
                # Execute validation
                result = await self.validate(
                    validator_name=validator_name,
                    data=current_data,
                    options=options
                )
                
                results.append(result)
                
                # Check for errors
                if not result.success and stop_on_error:
                    logger.warning(f"Validation chain stopped at {validator_name} due to error")
                    break
                
                # Update data for next validator if result provides new data
                if hasattr(result.result, 'processed_data'):
                    current_data = result.result.processed_data
            
            return results
            
        except Exception as e:
            logger.error(f"Validation chain failed: {str(e)}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get validation statistics.
        
        Returns:
            Statistics dictionary
        """



        return self._stats.copy()
    
    def clear_cache(self) -> None:
        """Clear validation cache."""
        self._results_cache.clear()
        logger.info("Validation cache cleared")
    
    async def _execute_validation(self, validator: Any, request: ValidationRequest) -> Any:
        """Execute validation with timeout."""



        try:
            # Determine validation method
            if hasattr(validator, 'validate_async'):
                # Async validation
                result = await asyncio.wait_for(
                    validator.validate_async(request.data, **request.options),
                    timeout=request.timeout
                )
            elif hasattr(validator, 'validate'):
                # Sync validation (run in executor)
                result = await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    lambda: validator.validate(request.data, **request.options)
                )
            else:
                raise ValueError(f"Validator has no validate method")
            
            return result
            
        except asyncio.TimeoutError:
            raise Exception(f"Validation timeout after {request.timeout} seconds")
        except Exception as e:
            raise Exception(f"Validation execution failed: {str(e)}")
    
    def _generate_cache_key(self, request: ValidationRequest) -> str:
        """Generate cache key for request."""



        try:
            # Create deterministic key from request data
            key_data = {
                "validator": request.validator_name,
                "data_hash": hash(str(request.data)),
                "options": request.options
            }
            return f"cache_{hash(json.dumps(key_data, sort_keys=True))}"
        except Exception:
            # Fallback to simple key
            return f"cache_{request.validator_name}_{int(time.time())}"
    
    def _update_stats(self, success: bool, duration: float) -> None:
        """Update validation statistics."""
        self._stats["total_requests"] += 1
        
        if success:
            self._stats["successful_validations"] += 1
        else:
            self._stats["failed_validations"] += 1
        
        # Update average duration
        total_validations = self._stats["total_requests"]
        current_avg = self._stats["average_duration"]
        self._stats["average_duration"] = (
            (current_avg * (total_validations - 1) + duration) / total_validations
        )


class ValidationEngine:
    """
    Main validation engine for the IA Influencer Agent Platform.
    
    Provides unified interface for all validation operations.
    """
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        """
        Initialize validation engine.
        
        Args:
            config: Validation configuration
        """
        self.config = config or ValidationConfig()
        self.registry = ValidatorRegistry()
        self.manager = ValidationManager(self.config, self.registry)
        
        # Configure logging
        logging.basicConfig(level=getattr(logging, self.config.log_level))
        
        logger.info("ValidationEngine initialized")
    
    async def validate_content(
        self,
        file_path: Optional[str] = None,
        file_data: Optional[bytes] = None,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        validation_level: str = "standard"
    ) -> ValidationResponse:
        """
        Validate content using content validator.
        
        Args:
            file_path: Path to content file
            file_data: Content data bytes
            filename: Original filename
            content_type: Content type hint
            validation_level: Validation level
            
        Returns:
            Validation response
        """



        return await self.manager.validate(
            validator_name="content",
            data={
                "file_path": file_path,
                "file_data": file_data,
                "filename": filename,
                "content_type": content_type
            },
            options={"validation_level": validation_level}
        )
    
    async def validate_schema(
        self,
        data: Any,
        schema_type: str = "json_schema",
        schema: Optional[Dict[str, Any]] = None
    ) -> ValidationResponse:
        """
        Validate data schema.
        
        Args:
            data: Data to validate
            schema_type: Type of schema validation
            schema: Schema definition
            
        Returns:
            Validation response
        """



        return await self.manager.validate(
            validator_name="schema",
            data=data,
            options={
                "schema_type": schema_type,
                "schema": schema
            }
        )
    
    async def validate_security(
        self,
        data: Any,
        scan_malware: bool = True,
        check_injections: bool = True
    ) -> ValidationResponse:
        """
        Validate security aspects.
        
        Args:
            data: Data to validate
            scan_malware: Enable malware scanning
            check_injections: Enable injection detection
            
        Returns:
            Validation response
        """



        return await self.manager.validate(
            validator_name="security",
            data=data,
            options={
                "scan_malware": scan_malware,
                "check_injections": check_injections
            }
        )
    
    async def validate_chain(
        self,
        validators: List[tuple],
        data: Any
    ) -> List[ValidationResponse]:
        """
        Execute validation chain.
        
        Args:
            validators: List of (validator_name, options) tuples
            data: Data to validate
            
        Returns:
            List of validation responses
        """
        validator_configs = [
            {"name": name, "options": options}
            for name, options in validators
        ]
        
        return await self.manager.validate_chain(validator_configs, data)
    
    async def validate_batch(
        self,
        items: List[Dict[str, Any]],
        parallel: bool = True
    ) -> List[ValidationResponse]:
        """
        Validate multiple items.
        
        Args:
            items: List of validation items
            parallel: Execute in parallel
            
        Returns:
            List of validation responses
        """
        mode = ValidationMode.PARALLEL if parallel else ValidationMode.SYNC
        return await self.manager.validate_batch(items, mode)
    
    def register_custom_validator(
        self,
        name: str,
        validator_class: Type,
        **kwargs
    ) -> None:
        """
        Register custom validator.
        
        Args:
            name: Validator name
            validator_class: Validator class
            **kwargs: Additional registration options
        """
        self.registry.register_validator(name, validator_class, **kwargs)
    
    def get_available_validators(self) -> List[str]:
        """Get list of available validators."""



        return self.registry.get_available_validators()
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update configuration.
        
        Args:
            config: Configuration updates
        """
        for key, value in config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        logger.info("ValidationEngine configuration updated")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get validation statistics."""



        return self.manager.get_statistics()
    
    def clear_cache(self) -> None:
        """Clear validation cache."""
        self.manager.clear_cache()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on validation system.
        
        Returns:
            Health check results
        """



        try:
            health = {
                "status": "healthy",
                "validators": len(self.registry.get_available_validators()),
                "config": self.config.dict(),
                "statistics": self.get_statistics(),
                "timestamp": time.time()
            }
            
            # Test a simple validation
            test_result = await self.validate_schema(
                data={"test": "data"},
                schema_type="json_schema"
            )
            
            if not test_result.success:
                health["status"] = "degraded"
                health["issues"] = ["Schema validation test failed"]
            
            return health
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
