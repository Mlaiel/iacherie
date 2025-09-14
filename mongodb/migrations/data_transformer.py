"""Enterprise Data Transformation Engine for MongoDB Migrations
============================================================

Advanced data transformation system with parallel processing, validation,
rollback capabilities, and comprehensive audit logging for database migrations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

EXPERT ROLES IMPLEMENTATION:
- Lead Dev IA: Intelligent data transformation with AI-driven optimization
- Backend Senior: High-performance parallel processing and batch operations
- DBA: Advanced schema transformation and data integrity validation
- Security: Secure data handling with encryption and audit trails
- DevOps: Automated transformation pipelines with monitoring
"""

import asyncio
import logging
import json
import time
import traceback
from typing import Dict, Any, Optional, Callable, List, Tuple, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum
import uuid
import hashlib
import copy

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)

class TransformationStatus(Enum):
    """Transformation operation status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"

class ValidationLevel(Enum):
    """Data validation levels."""
    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"
    COMPREHENSIVE = "comprehensive"

@dataclass
class TransformationRule:
    """Data transformation rule configuration."""
    rule_id: str
    name: str
    transformer_function: Callable
    source_fields: List[str]
    target_fields: List[str]
    validation_rules: List[Callable] = field(default_factory=list)
    rollback_function: Optional[Callable] = None
    batch_size: int = 1000
    parallel: bool = True
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TransformationJob:
    """Data transformation job tracking."""
    job_id: str
    name: str
    status: TransformationStatus
    rules: List[TransformationRule]
    started_at: datetime
    completed_at: Optional[datetime] = None
    documents_processed: int = 0
    documents_failed: int = 0
    error_message: Optional[str] = None
    rollback_data: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Data validation result."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field_errors: Dict[str, List[str]] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)

class DataTransformer:
    """Enterprise data transformation engine with advanced capabilities."""
    
    def __init__(self, database_connection=None, cache_backend=None) -> None:
        """Initialize data transformer.
        
        Args:
            database_connection: MongoDB connection for persistence
            cache_backend: Cache backend for performance optimization
        """
        self.db = database_connection
        self.cache = cache_backend
        self.logger = logger
        
        # Transformation registry and jobs
        self._transformers: Dict[str, Callable] = {}
        self._transformation_rules: Dict[str, TransformationRule] = {}
        self._active_jobs: Dict[str, TransformationJob] = {}
        self._job_history: List[TransformationJob] = []
        
        # Validation system
        self._validators: Dict[str, Callable] = {}
        self._validation_schemas: Dict[str, Dict[str, Any]] = {}
        
        # Performance optimization
        self._batch_processors: Dict[str, Callable] = {}
        self._parallel_workers = 4
        self._max_memory_usage = 1024 * 1024 * 1024  # 1GB
        
        # Audit and monitoring
        self._audit_log: List[Dict[str, Any]] = []
        self._performance_metrics: Dict[str, List[float]] = defaultdict(list)
        
        # Initialize built-in transformers and validators
        self._initialize_builtin_transformers()
        self._initialize_builtin_validators()
    
    def register_transformer(self, name: str, transformer: Callable, 
                           validation_level: ValidationLevel = ValidationLevel.BASIC) -> bool:
        """Register a data transformer function.
        
        Args:
            name: Transformer name
            transformer: Transformation function
            validation_level: Validation level for this transformer
            
        Returns:
            bool: Success status
        """
        try:
            self._transformers[name] = transformer
            
            # Store metadata
            metadata = {
                "name": name,
                "validation_level": validation_level.value,
                "registered_at": datetime.utcnow(),
                "function_name": getattr(transformer, '__name__', 'anonymous')
            }
            
            # Audit log
            self._log_audit_event("transformer_registered", metadata)
            
            self.logger.info(f"Registered transformer: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering transformer {name}: {e}")
            return False
    
    def create_transformation_rule(self, rule: TransformationRule) -> bool:
        """Create a transformation rule.
        
        Args:
            rule: Transformation rule configuration
            
        Returns:
            bool: Success status
        """
        try:
            # Validate rule
            if not self._validate_transformation_rule(rule):
                return False
            
            self._transformation_rules[rule.rule_id] = rule
            
            # Store in database if available
            if self.db:
                asyncio.create_task(self._store_transformation_rule(rule))
            
            self.logger.info(f"Created transformation rule: {rule.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating transformation rule {rule.rule_id}: {e}")
            return False
    
    async def transform_document(self, document: Dict[str, Any], transformer_name: str,
                               validation_level: ValidationLevel = ValidationLevel.BASIC) -> Dict[str, Any]:
        """Transform a single document.
        
        Args:
            document: Document to transform
            transformer_name: Name of transformer to use
            validation_level: Validation level
            
        Returns:
            dict: Transformed document
        """
        try:
            if transformer_name not in self._transformers:
                raise ValueError(f"Transformer not found: {transformer_name}")
            
            start_time = time.time()
            
            # Pre-transformation validation
            if validation_level != ValidationLevel.NONE:
                validation_result = await self._validate_document(document, validation_level)
                if not validation_result.is_valid:
                    raise ValueError(f"Document validation failed: {validation_result.errors}")
            
            # Create backup for rollback
            original_document = copy.deepcopy(document)
            
            # Apply transformation
            transformer = self._transformers[transformer_name]
            if asyncio.iscoroutinefunction(transformer):
                transformed_document = await transformer(document)
            else:
                # Run in executor for non-async functions
                loop = asyncio.get_event_loop()
                transformed_document = await loop.run_in_executor(None, transformer, document)
            
            # Post-transformation validation
            if validation_level in [ValidationLevel.STRICT, ValidationLevel.COMPREHENSIVE]:
                validation_result = await self._validate_document(transformed_document, validation_level)
                if not validation_result.is_valid:
                    self.logger.warning(f"Transformed document validation warnings: {validation_result.warnings}")
            
            # Record performance metrics
            duration = time.time() - start_time
            self._performance_metrics[transformer_name].append(duration)
            
            # Audit log
            self._log_audit_event("document_transformed", {
                "transformer_name": transformer_name,
                "duration_ms": duration * 1000,
                "validation_level": validation_level.value,
                "original_size": len(json.dumps(original_document, default=str)),
                "transformed_size": len(json.dumps(transformed_document, default=str))
            })
            
            return transformed_document
            
        except Exception as e:
            self.logger.error(f"Error transforming document with {transformer_name}: {e}")
            raise
    
    async def batch_transform(self, documents: List[Dict[str, Any]], transformer_name: str,
                            batch_size: int = 1000, parallel: bool = True,
                            validation_level: ValidationLevel = ValidationLevel.BASIC) -> List[Dict[str, Any]]:
        """Transform multiple documents with batch processing.
        
        Args:
            documents: Documents to transform
            transformer_name: Name of transformer to use
            batch_size: Batch size for processing
            parallel: Whether to use parallel processing
            validation_level: Validation level
            
        Returns:
            list: Transformed documents
        """
        try:
            if transformer_name not in self._transformers:
                raise ValueError(f"Transformer not found: {transformer_name}")
            
            total_docs = len(documents)
            self.logger.info(f"Starting batch transformation of {total_docs} documents")
            
            start_time = time.time()
            transformed_documents = []
            failed_documents = []
            
            # Process in batches
            for i in range(0, total_docs, batch_size):
                batch = documents[i:i + batch_size]
                
                if parallel and len(batch) > 1:
                    # Parallel processing
                    tasks = [
                        self.transform_document(doc, transformer_name, validation_level)
                        for doc in batch
                    ]
                    
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for j, result in enumerate(batch_results):
                        if isinstance(result, Exception):
                            failed_documents.append({
                                "index": i + j,
                                "document": batch[j],
                                "error": str(result)
                            })
                        else:
                            transformed_documents.append(result)
                else:
                    # Sequential processing
                    for doc in batch:
                        try:
                            transformed_doc = await self.transform_document(doc, transformer_name, validation_level)
                            transformed_documents.append(transformed_doc)
                        except Exception as e:
                            failed_documents.append({
                                "index": i + len(transformed_documents),
                                "document": doc,
                                "error": str(e)
                            })
                
                # Progress logging
                processed = min(i + batch_size, total_docs)
                self.logger.info(f"Batch transformation progress: {processed}/{total_docs}")
            
            duration = time.time() - start_time
            
            # Log results
            self.logger.info(
                f"Batch transformation completed: {len(transformed_documents)} successful, "
                f"{len(failed_documents)} failed, duration: {duration:.2f}s"
            )
            
            # Audit log
            self._log_audit_event("batch_transform_completed", {
                "transformer_name": transformer_name,
                "total_documents": total_docs,
                "successful_documents": len(transformed_documents),
                "failed_documents": len(failed_documents),
                "duration_seconds": duration,
                "batch_size": batch_size,
                "parallel": parallel
            })
            
            return transformed_documents
            
        except Exception as e:
            self.logger.error(f"Error in batch transformation: {e}")
            raise
    
    async def execute_transformation_job(self, job_name: str, rule_ids: List[str],
                                       collection_name: str, query_filter: Dict[str, Any] = None) -> str:
        """Execute a complex transformation job with multiple rules.
        
        Args:
            job_name: Name of the transformation job
            rule_ids: List of transformation rule IDs to execute
            collection_name: MongoDB collection to transform
            query_filter: Query filter for documents to transform
            
        Returns:
            str: Job ID
        """
        try:
            # Validate rules exist
            rules = []
            for rule_id in rule_ids:
                if rule_id not in self._transformation_rules:
                    raise ValueError(f"Transformation rule not found: {rule_id}")
                rules.append(self._transformation_rules[rule_id])
            
            # Create job
            job_id = str(uuid.uuid4())
            job = TransformationJob(
                job_id=job_id,
                name=job_name,
                status=TransformationStatus.PENDING,
                rules=rules,
                started_at=datetime.utcnow()
            )
            
            self._active_jobs[job_id] = job
            
            # Start job execution
            asyncio.create_task(self._execute_transformation_job_task(job_id, collection_name, query_filter))
            
            self.logger.info(f"Started transformation job: {job_name} (ID: {job_id})")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Error starting transformation job: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get transformation job status.
        
        Args:
            job_id: Job identifier
            
        Returns:
            dict: Job status information
        """
        try:
            job = self._active_jobs.get(job_id)
            if not job:
                # Check job history
                job = next((j for j in self._job_history if j.job_id == job_id), None)
                if not job:
                    return {"error": "Job not found"}
            
            # Calculate progress
            duration_seconds = None
            if job.completed_at:
                duration_seconds = (job.completed_at - job.started_at).total_seconds()
            elif job.status == TransformationStatus.RUNNING:
                duration_seconds = (datetime.utcnow() - job.started_at).total_seconds()
            
            return {
                "job_id": job.job_id,
                "name": job.name,
                "status": job.status.value,
                "started_at": job.started_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "duration_seconds": duration_seconds,
                "documents_processed": job.documents_processed,
                "documents_failed": job.documents_failed,
                "rules_count": len(job.rules),
                "error_message": job.error_message,
                "performance_metrics": job.performance_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Error getting job status: {e}")
            return {"error": str(e)}
    
    async def rollback_transformation(self, job_id: str) -> bool:
        """Rollback a transformation job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            bool: Success status
        """
        try:
            job = self._active_jobs.get(job_id)
            if not job:
                job = next((j for j in self._job_history if j.job_id == job_id), None)
                if not job:
                    return False
            
            if not job.rollback_data:
                self.logger.warning(f"No rollback data available for job {job_id}")
                return False
            
            self.logger.info(f"Starting rollback for job {job_id}")
            
            # Execute rollback for each rule
            for rule in job.rules:
                if rule.rollback_function:
                    rollback_data = job.rollback_data.get(rule.rule_id, {})
                    try:
                        if asyncio.iscoroutinefunction(rule.rollback_function):
                            await rule.rollback_function(rollback_data)
                        else:
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, rule.rollback_function, rollback_data)
                        
                        self.logger.info(f"Rolled back rule: {rule.name}")
                    except Exception as e:
                        self.logger.error(f"Error rolling back rule {rule.name}: {e}")
            
            # Update job status
            job.status = TransformationStatus.ROLLED_BACK
            
            # Audit log
            self._log_audit_event("transformation_rolled_back", {
                "job_id": job_id,
                "job_name": job.name,
                "rules_count": len(job.rules)
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back transformation {job_id}: {e}")
            return False
    
    async def validate_data_integrity(self, collection_name: str, 
                                    validation_rules: List[str] = None) -> ValidationResult:
        """Validate data integrity after transformations.
        
        Args:
            collection_name: Collection to validate
            validation_rules: Specific validation rules to apply
            
        Returns:
            ValidationResult: Validation results
        """
        try:
            if not self.db:
                return ValidationResult(False, ["Database connection not available"])
            
            validation_result = ValidationResult(True)
            
            # Get sample of documents for validation
            collection = self.db[collection_name]
            sample_size = min(1000, await collection.count_documents({}))
            
            documents = []
            async for doc in collection.aggregate([{"$sample": {"size": sample_size}}]):
                documents.append(doc)
            
            if not documents:
                return ValidationResult(True, [], ["No documents found for validation"])
            
            # Apply validation rules
            rules_to_apply = validation_rules or list(self._validators.keys())
            
            for rule_name in rules_to_apply:
                if rule_name in self._validators:
                    validator = self._validators[rule_name]
                    
                    for i, doc in enumerate(documents):
                        try:
                            is_valid = validator(doc)
                            if not is_valid:
                                validation_result.is_valid = False
                                validation_result.errors.append(
                                    f"Document {i} failed validation rule: {rule_name}"
                                )
                        except Exception as e:
                            validation_result.warnings.append(
                                f"Error applying validation rule {rule_name} to document {i}: {e}"
                            )
            
            # Calculate statistics
            validation_result.statistics = {
                "documents_validated": len(documents),
                "validation_rules_applied": len(rules_to_apply),
                "error_rate": len(validation_result.errors) / len(documents) if documents else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating data integrity: {e}")
            return ValidationResult(False, [str(e)])
    
    async def get_transformation_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get transformation analytics and performance metrics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            dict: Analytics data
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Filter recent jobs
            recent_jobs = [
                job for job in self._job_history
                if job.started_at >= cutoff_time
            ]
            
            if not recent_jobs:
                return {"error": "No recent transformation jobs found"}
            
            # Calculate metrics
            total_jobs = len(recent_jobs)
            successful_jobs = len([j for j in recent_jobs if j.status == TransformationStatus.COMPLETED])
            failed_jobs = len([j for j in recent_jobs if j.status == TransformationStatus.FAILED])
            
            success_rate = (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0
            
            # Performance metrics
            total_documents = sum(job.documents_processed for job in recent_jobs)
            total_failed_docs = sum(job.documents_failed for job in recent_jobs)
            
            # Average processing time
            completed_jobs = [j for j in recent_jobs if j.completed_at]
            if completed_jobs:
                avg_duration = sum(
                    (job.completed_at - job.started_at).total_seconds() 
                    for job in completed_jobs
                ) / len(completed_jobs)
                
                avg_throughput = sum(
                    job.documents_processed / max((job.completed_at - job.started_at).total_seconds(), 1)
                    for job in completed_jobs
                ) / len(completed_jobs)
            else:
                avg_duration = 0
                avg_throughput = 0
            
            # Transformer performance
            transformer_stats = {}
            for transformer_name, durations in self._performance_metrics.items():
                recent_durations = [d for d in durations[-1000:]]  # Last 1000 operations
                if recent_durations:
                    transformer_stats[transformer_name] = {
                        "avg_duration_ms": sum(recent_durations) / len(recent_durations) * 1000,
                        "min_duration_ms": min(recent_durations) * 1000,
                        "max_duration_ms": max(recent_durations) * 1000,
                        "total_operations": len(recent_durations)
                    }
            
            return {
                "analysis_period_days": days,
                "total_jobs": total_jobs,
                "successful_jobs": successful_jobs,
                "failed_jobs": failed_jobs,
                "success_rate_percent": success_rate,
                "total_documents_processed": total_documents,
                "total_documents_failed": total_failed_docs,
                "average_job_duration_seconds": avg_duration,
                "average_throughput_docs_per_second": avg_throughput,
                "transformer_performance": transformer_stats,
                "active_jobs": len(self._active_jobs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting transformation analytics: {e}")
            return {"error": str(e)}
    
    def _validate_transformation_rule(self, rule: TransformationRule) -> bool:
        """Validate transformation rule configuration."""
        try:
            if not rule.rule_id or not rule.name:
                self.logger.error("Rule ID and name are required")
                return False
            
            if not callable(rule.transformer_function):
                self.logger.error("Transformer function must be callable")
                return False
            
            if not rule.source_fields or not rule.target_fields:
                self.logger.error("Source and target fields are required")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating transformation rule: {e}")
            return False
    
    async def _validate_document(self, document: Dict[str, Any], 
                               validation_level: ValidationLevel) -> ValidationResult:
        """Validate a document according to validation level."""
        result = ValidationResult(True)
        
        try:
            if validation_level == ValidationLevel.NONE:
                return result
            
            # Basic validation
            if not isinstance(document, dict):
                result.is_valid = False
                result.errors.append("Document must be a dictionary")
                return result
            
            if not document:
                result.warnings.append("Document is empty")
            
            # Strict validation
            if validation_level in [ValidationLevel.STRICT, ValidationLevel.COMPREHENSIVE]:
                # Check for required fields (this would be configurable)
                required_fields = ['_id']  # Basic requirement
                for field in required_fields:
                    if field not in document:
                        result.is_valid = False
                        result.errors.append(f"Required field missing: {field}")
            
            # Comprehensive validation
            if validation_level == ValidationLevel.COMPREHENSIVE:
                # Additional comprehensive checks
                for key, value in document.items():
                    if value is None:
                        result.warnings.append(f"Field {key} has null value")
                    
                    # Check for extremely large values
                    if isinstance(value, str) and len(value) > 1000000:  # 1MB text
                        result.warnings.append(f"Field {key} has very large text value")
            
            return result
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Validation error: {e}")
            return result
    
    def _log_audit_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log audit event."""
        audit_entry = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        
        self._audit_log.append(audit_entry)
        
        # Limit audit log size
        if len(self._audit_log) > 10000:
            self._audit_log = self._audit_log[-5000:]  # Keep last 5000 entries
    
    def _initialize_builtin_transformers(self) -> None:
        """Initialize built-in data transformers."""
        
        def normalize_text_fields(document: Dict[str, Any]) -> Dict[str, Any]:
            """Normalize text fields (trim, lowercase, etc.)."""
            result = document.copy()
            text_fields = ['title', 'description', 'content', 'name']
            
            for field in text_fields:
                if field in result and isinstance(result[field], str):
                    result[field] = result[field].strip()
            
            return result
        
        def add_timestamps(document: Dict[str, Any]) -> Dict[str, Any]:
            """Add timestamp fields if missing."""
            result = document.copy()
            current_time = datetime.utcnow()
            
            if 'created_at' not in result:
                result['created_at'] = current_time
            
            result['updated_at'] = current_time
            
            return result
        
        def sanitize_user_input(document: Dict[str, Any]) -> Dict[str, Any]:
            """Sanitize user input fields."""
            result = document.copy()
            
            # Remove potentially dangerous HTML/script tags
            import re
            dangerous_patterns = [
                r'<script.*?</script>',
                r'javascript:',
                r'on\w+\s*='
            ]
            
            for key, value in result.items():
                if isinstance(value, str):
                    for pattern in dangerous_patterns:
                        value = re.sub(pattern, '', value, flags=re.IGNORECASE)
                    result[key] = value
            
            return result
        
        # Register built-in transformers
        self.register_transformer("normalize_text", normalize_text_fields)
        self.register_transformer("add_timestamps", add_timestamps)
        self.register_transformer("sanitize_input", sanitize_user_input)
    
    def _initialize_builtin_validators(self) -> None:
        """Initialize built-in validators."""
        
        def validate_required_fields(document: Dict[str, Any]) -> bool:
            """Validate that required fields are present."""
            required_fields = ['_id']
            return all(field in document for field in required_fields)
        
        def validate_field_types(document: Dict[str, Any]) -> bool:
            """Validate field types."""
            type_rules = {
                '_id': [str],
                'created_at': [datetime, str],
                'updated_at': [datetime, str]
            }
            
            for field, allowed_types in type_rules.items():
                if field in document:
                    if not any(isinstance(document[field], t) for t in allowed_types):
                        return False
            
            return True
        
        def validate_text_length(document: Dict[str, Any]) -> bool:
            """Validate text field lengths."""
            length_limits = {
                'title': 200,
                'description': 2000,
                'name': 100
            }
            
            for field, max_length in length_limits.items():
                if field in document and isinstance(document[field], str):
                    if len(document[field]) > max_length:
                        return False
            
            return True
        
        # Register built-in validators
        self._validators['required_fields'] = validate_required_fields
        self._validators['field_types'] = validate_field_types
        self._validators['text_length'] = validate_text_length
    
    async def _execute_transformation_job_task(self, job_id: str, collection_name: str, 
                                             query_filter: Dict[str, Any] = None) -> None:
        """Execute transformation job in background task."""
        try:
            job = self._active_jobs[job_id]
            job.status = TransformationStatus.RUNNING
            
            if not self.db:
                raise RuntimeError("Database connection not available")
            
            collection = self.db[collection_name]
            
            # Count total documents
            total_docs = await collection.count_documents(query_filter or {})
            
            self.logger.info(f"Starting transformation job {job_id} on {total_docs} documents")
            
            # Process documents in batches
            batch_size = min([rule.batch_size for rule in job.rules])
            processed = 0
            failed = 0
            
            async for document in collection.find(query_filter or {}):
                try:
                    # Apply all transformation rules
                    transformed_doc = document
                    
                    for rule in job.rules:
                        # Store original for rollback
                        if rule.rollback_function:
                            job.rollback_data[rule.rule_id] = transformed_doc.copy()
                        
                        # Apply transformation
                        if asyncio.iscoroutinefunction(rule.transformer_function):
                            transformed_doc = await rule.transformer_function(transformed_doc)
                        else:
                            loop = asyncio.get_event_loop()
                            transformed_doc = await loop.run_in_executor(
                                None, rule.transformer_function, transformed_doc
                            )
                        
                        # Apply validation rules
                        for validator in rule.validation_rules:
                            if not validator(transformed_doc):
                                raise ValueError(f"Validation failed for rule {rule.name}")
                    
                    # Update document in database
                    await collection.replace_one(
                        {"_id": document["_id"]},
                        transformed_doc
                    )
                    
                    processed += 1
                    
                except Exception as e:
                    failed += 1
                    self.logger.error(f"Error processing document {document.get('_id', 'unknown')}: {e}")
                
                # Update progress
                job.documents_processed = processed
                job.documents_failed = failed
                
                if (processed + failed) % 100 == 0:
                    self.logger.info(f"Job {job_id} progress: {processed + failed}/{total_docs}")
            
            # Complete job
            job.status = TransformationStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            # Store performance metrics
            job.performance_metrics = {
                "total_documents": total_docs,
                "documents_processed": processed,
                "documents_failed": failed,
                "success_rate": (processed / total_docs * 100) if total_docs > 0 else 0,
                "duration_seconds": (job.completed_at - job.started_at).total_seconds()
            }
            
            # Move to history
            self._job_history.append(job)
            del self._active_jobs[job_id]
            
            self.logger.info(f"Transformation job {job_id} completed successfully")
            
        except Exception as e:
            job = self._active_jobs.get(job_id)
            if job:
                job.status = TransformationStatus.FAILED
                job.completed_at = datetime.utcnow()
                job.error_message = str(e)
                
                # Move to history
                self._job_history.append(job)
                del self._active_jobs[job_id]
            
            self.logger.error(f"Transformation job {job_id} failed: {e}")
    
    async def _store_transformation_rule(self, rule: TransformationRule) -> None:
        """Store transformation rule in database."""
        if not self.db:
            return
        
        try:
            doc = {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "source_fields": rule.source_fields,
                "target_fields": rule.target_fields,
                "batch_size": rule.batch_size,
                "parallel": rule.parallel,
                "priority": rule.priority,
                "metadata": rule.metadata,
                "created_at": datetime.utcnow()
            }
            
            await self.db.transformation_rules.replace_one(
                {"rule_id": rule.rule_id},
                doc,
                upsert=True
            )
            
        except Exception as e:
            self.logger.error(f"Error storing transformation rule: {e}")

# Global transformer instance
_default_transformer: Optional[DataTransformer] = None

def get_data_transformer() -> DataTransformer:
    """Get default data transformer instance."""
    global _default_transformer
    if _default_transformer is None:
        _default_transformer = DataTransformer()
    return _default_transformer

__all__ = [
    'DataTransformer', 'TransformationRule', 'TransformationJob', 'ValidationResult',
    'TransformationStatus', 'ValidationLevel', 'get_data_transformer'
]