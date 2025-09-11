#!/usr/bin/env python3
"""
Ainflue Platform - Firebase Backend Services Integration
Enterprise-grade Firebase integration for real-time backend services

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved

Expert Roles Demonstrated:
- Backend Senior: Comprehensive backend services integration and architecture
- DevOps: Real-time monitoring, deployment automation, infrastructure management  
- DBA: Firestore database optimization, real-time data synchronization
- Security: Authentication, authorization, and data protection
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import os
from pathlib import Path

import aiohttp
import asyncio
import jwt
import httpx
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage, messaging

# Core platform imports
from ..core.base_integration import BaseIntegration
from ..core.exceptions import IntegrationError, ValidationError
from ..monitoring_integration import MonitoringIntegration
from ..audit_logger import AuditLogger

class FirebaseService(str, Enum):
    """Firebase service types"""
    FIRESTORE = "firestore"
    AUTHENTICATION = "authentication"
    STORAGE = "storage"
    MESSAGING = "messaging"
    FUNCTIONS = "functions"
    ANALYTICS = "analytics"
    REALTIME_DB = "realtime_database"
    HOSTING = "hosting"

class CollectionType(str, Enum):
    """Firestore collection types"""
    USERS = "users"
    CONTENT = "content"
    CREATORS = "creators"
    CAMPAIGNS = "campaigns"
    ANALYTICS = "analytics"
    NOTIFICATIONS = "notifications"
    SESSIONS = "sessions"
    LOGS = "logs"

@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    token_uri: str = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url: str = "https://www.googleapis.com/oauth2/v1/certs"
    
    # Storage configuration
    storage_bucket: Optional[str] = None
    
    # Real-time database configuration
    database_url: Optional[str] = None
    
    # Additional settings
    api_key: Optional[str] = None
    messaging_sender_id: Optional[str] = None
    app_id: Optional[str] = None

@dataclass
class DocumentOperation:
    """Document operation for batch processing"""
    operation_type: str  # create, update, delete
    collection: str
    document_id: Optional[str]
    data: Optional[Dict[str, Any]] = None
    merge: bool = False

@dataclass
class QueryFilter:
    """Firestore query filter"""
    field: str
    operator: str  # ==, !=, <, <=, >, >=, in, not-in, array-contains
    value: Any

@dataclass
class StorageFile:
    """Storage file representation"""
    file_path: str
    content_type: str
    metadata: Dict[str, str] = field(default_factory=dict)
    custom_token: Optional[str] = None

class FirebaseIntegration(BaseIntegration):
    """
    Enterprise Firebase Backend Services Integration
    
    Demonstrates Expert Roles:
    - Backend Senior: Comprehensive Firebase services orchestration
    - DevOps: Real-time monitoring, automated deployment, infrastructure
    - DBA: Firestore optimization, real-time data sync, query optimization
    - Security: Authentication flows, secure data access, encryption
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Firebase integration"""
        super().__init__(config)
        
        # Core configuration
        self.config = config
        self.firebase_config = self._parse_firebase_config(config)
        
        # Service dependencies
        self.monitoring = MonitoringIntegration(config)
        self.audit_logger = AuditLogger(config)
        
        # Firebase services
        self.app: Optional[firebase_admin.App] = None
        self.firestore_client: Optional[firestore.Client] = None
        self.auth_client = None
        self.storage_client = None
        self.messaging_client = None
        
        # Connection state
        self.is_initialized = False
        self.connection_pool_size = config.get("connection_pool_size", 10)
        
        # Performance tracking
        self.metrics = {
            "operations_performed": 0,
            "documents_processed": 0,
            "storage_operations": 0,
            "auth_operations": 0,
            "messaging_operations": 0,
            "average_response_time": 0.0,
            "error_count": 0,
            "cache_hits": 0
        }
        
        # Query cache
        self.query_cache = {}
        self.cache_ttl = config.get("cache_ttl", 300)  # 5 minutes
        
        self.logger = logging.getLogger(__name__)
    
    def _parse_firebase_config(self, config: Dict[str, Any]) -> FirebaseConfig:
        """Parse Firebase configuration from config dict"""
        firebase_config = config.get("firebase", {})
        
        return FirebaseConfig(
            project_id=firebase_config.get("project_id"),
            private_key_id=firebase_config.get("private_key_id"),
            private_key=firebase_config.get("private_key", "").replace("\\n", "\n"),
            client_email=firebase_config.get("client_email"),
            client_id=firebase_config.get("client_id"),
            storage_bucket=firebase_config.get("storage_bucket"),
            database_url=firebase_config.get("database_url"),
            api_key=firebase_config.get("api_key"),
            messaging_sender_id=firebase_config.get("messaging_sender_id"),
            app_id=firebase_config.get("app_id")
        )
    
    async def initialize(self) -> None:
        """
        Initialize Firebase services
        Demonstrates: DevOps - Service initialization and health validation
        """
        try:
            # Create service account credentials
            cred_dict = {
                "type": "service_account",
                "project_id": self.firebase_config.project_id,
                "private_key_id": self.firebase_config.private_key_id,
                "private_key": self.firebase_config.private_key,
                "client_email": self.firebase_config.client_email,
                "client_id": self.firebase_config.client_id,
                "auth_uri": self.firebase_config.auth_uri,
                "token_uri": self.firebase_config.token_uri,
                "auth_provider_x509_cert_url": self.firebase_config.auth_provider_x509_cert_url,
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.firebase_config.client_email}"
            }
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(cred_dict)
            
            # Check if app already exists
            try:
                self.app = firebase_admin.get_app()
            except ValueError:
                # App doesn't exist, create it
                self.app = firebase_admin.initialize_app(cred, {
                    'storageBucket': self.firebase_config.storage_bucket,
                    'databaseURL': self.firebase_config.database_url
                })
            
            # Initialize service clients
            self.firestore_client = firestore.client(app=self.app)
            self.auth_client = auth
            
            if self.firebase_config.storage_bucket:
                self.storage_client = storage.bucket(app=self.app)
            
            self.messaging_client = messaging
            
            # Test connections
            await self._test_connections()
            
            self.is_initialized = True
            
            await self.monitoring.record_metric("firebase_initialized", 1)
            self.logger.info("Firebase integration initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase integration: {e}")
            raise IntegrationError(f"Firebase initialization failed: {e}")
    
    async def _test_connections(self) -> None:
        """Test Firebase service connections"""
        try:
            # Test Firestore connection
            test_doc = self.firestore_client.collection("_test").document("connection_test")
            test_doc.set({"timestamp": firestore.SERVER_TIMESTAMP})
            test_doc.delete()
            
            # Test Authentication service
            try:
                auth.list_users(max_results=1, app=self.app)
            except Exception:
                pass  # Might fail if no users exist, but service is available
            
            self.logger.info("Firebase connection tests passed")
            
        except Exception as e:
            self.logger.error(f"Firebase connection test failed: {e}")
            raise IntegrationError(f"Firebase connection test failed: {e}")
    
    # ==================== FIRESTORE OPERATIONS ====================
    
    async def create_document(self, collection: str, document_id: Optional[str] = None, 
                            data: Dict[str, Any] = None, merge: bool = False) -> str:
        """
        Create or update a Firestore document
        Demonstrates: DBA - Optimized document operations
        """
        try:
            start_time = datetime.utcnow()
            
            if not self.firestore_client:
                raise IntegrationError("Firestore client not initialized")
            
            collection_ref = self.firestore_client.collection(collection)
            
            # Generate document ID if not provided
            if not document_id:
                doc_ref = collection_ref.document()
                document_id = doc_ref.id
            else:
                doc_ref = collection_ref.document(document_id)
            
            # Add metadata
            data = data or {}
            data.update({
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP
            })
            
            # Perform operation
            if merge:
                doc_ref.set(data, merge=True)
            else:
                doc_ref.set(data)
            
            # Update metrics
            self.metrics["operations_performed"] += 1
            self.metrics["documents_processed"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firestore_document_created", 1, {
                "collection": collection,
                "document_id": document_id
            })
            
            # Audit log
            await self.audit_logger.log_action(
                action="firestore_document_created",
                resource_id=f"{collection}/{document_id}",
                details={"collection": collection, "merge": merge}
            )
            
            self.logger.debug(f"Document created: {collection}/{document_id}")
            return document_id
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to create document: {e}")
            await self.monitoring.record_error("firestore_create_error", str(e))
            raise IntegrationError(f"Document creation failed: {e}")
    
    async def get_document(self, collection: str, document_id: str, 
                         use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get a Firestore document
        Demonstrates: DBA - Optimized data retrieval with caching
        """
        try:
            start_time = datetime.utcnow()
            
            # Check cache first
            cache_key = f"{collection}/{document_id}"
            if use_cache and cache_key in self.query_cache:
                cache_entry = self.query_cache[cache_key]
                if datetime.utcnow() - cache_entry["timestamp"] < timedelta(seconds=self.cache_ttl):
                    self.metrics["cache_hits"] += 1
                    return cache_entry["data"]
            
            if not self.firestore_client:
                raise IntegrationError("Firestore client not initialized")
            
            doc_ref = self.firestore_client.collection(collection).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                
                # Cache the result
                if use_cache:
                    self.query_cache[cache_key] = {
                        "data": data,
                        "timestamp": datetime.utcnow()
                    }
                
                # Update metrics
                self.metrics["operations_performed"] += 1
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                self._update_average_response_time(processing_time)
                
                return data
            else:
                return None
                
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to get document: {e}")
            await self.monitoring.record_error("firestore_get_error", str(e))
            raise IntegrationError(f"Document retrieval failed: {e}")
    
    async def update_document(self, collection: str, document_id: str, 
                            data: Dict[str, Any], merge: bool = True) -> bool:
        """
        Update a Firestore document
        Demonstrates: DBA - Efficient document updates
        """
        try:
            start_time = datetime.utcnow()
            
            if not self.firestore_client:
                raise IntegrationError("Firestore client not initialized")
            
            doc_ref = self.firestore_client.collection(collection).document(document_id)
            
            # Add update timestamp
            data["updated_at"] = firestore.SERVER_TIMESTAMP
            
            # Perform update
            if merge:
                doc_ref.set(data, merge=True)
            else:
                doc_ref.update(data)
            
            # Invalidate cache
            cache_key = f"{collection}/{document_id}"
            if cache_key in self.query_cache:
                del self.query_cache[cache_key]
            
            # Update metrics
            self.metrics["operations_performed"] += 1
            self.metrics["documents_processed"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firestore_document_updated", 1, {
                "collection": collection,
                "document_id": document_id
            })
            
            # Audit log
            await self.audit_logger.log_action(
                action="firestore_document_updated",
                resource_id=f"{collection}/{document_id}",
                details={"collection": collection, "merge": merge}
            )
            
            return True
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to update document: {e}")
            await self.monitoring.record_error("firestore_update_error", str(e))
            raise IntegrationError(f"Document update failed: {e}")
    
    async def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a Firestore document"""
        try:
            start_time = datetime.utcnow()
            
            if not self.firestore_client:
                raise IntegrationError("Firestore client not initialized")
            
            doc_ref = self.firestore_client.collection(collection).document(document_id)
            doc_ref.delete()
            
            # Invalidate cache
            cache_key = f"{collection}/{document_id}"
            if cache_key in self.query_cache:
                del self.query_cache[cache_key]
            
            # Update metrics
            self.metrics["operations_performed"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firestore_document_deleted", 1, {
                "collection": collection,
                "document_id": document_id
            })
            
            # Audit log
            await self.audit_logger.log_action(
                action="firestore_document_deleted",
                resource_id=f"{collection}/{document_id}",
                details={"collection": collection}
            )
            
            return True
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to delete document: {e}")
            await self.monitoring.record_error("firestore_delete_error", str(e))
            raise IntegrationError(f"Document deletion failed: {e}")
    
    async def query_collection(self, collection: str, filters: List[QueryFilter] = None,
                             order_by: Optional[str] = None, limit: Optional[int] = None,
                             use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Query Firestore collection with filters
        Demonstrates: DBA - Advanced query optimization
        """
        try:
            start_time = datetime.utcnow()
            
            # Create cache key for complex queries
            cache_key = f"query:{collection}:{hash(str(filters))}{order_by}{limit}"
            if use_cache and cache_key in self.query_cache:
                cache_entry = self.query_cache[cache_key]
                if datetime.utcnow() - cache_entry["timestamp"] < timedelta(seconds=self.cache_ttl):
                    self.metrics["cache_hits"] += 1
                    return cache_entry["data"]
            
            if not self.firestore_client:
                raise IntegrationError("Firestore client not initialized")
            
            # Build query
            query = self.firestore_client.collection(collection)
            
            # Apply filters
            if filters:
                for filter_item in filters:
                    query = query.where(filter_item.field, filter_item.operator, filter_item.value)
            
            # Apply ordering
            if order_by:
                direction = firestore.Query.DESCENDING if order_by.startswith("-") else firestore.Query.ASCENDING
                field = order_by.lstrip("-")
                query = query.order_by(field, direction=direction)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            # Execute query
            docs = query.stream()
            results = []
            
            for doc in docs:
                data = doc.to_dict()
                data["_id"] = doc.id
                results.append(data)
            
            # Cache results
            if use_cache:
                self.query_cache[cache_key] = {
                    "data": results,
                    "timestamp": datetime.utcnow()
                }
            
            # Update metrics
            self.metrics["operations_performed"] += 1
            self.metrics["documents_processed"] += len(results)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firestore_query_executed", 1, {
                "collection": collection,
                "results_count": len(results)
            })
            
            return results
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to query collection: {e}")
            await self.monitoring.record_error("firestore_query_error", str(e))
            raise IntegrationError(f"Collection query failed: {e}")
    
    async def batch_operations(self, operations: List[DocumentOperation]) -> bool:
        """
        Perform batch Firestore operations
        Demonstrates: DBA - Efficient batch processing
        """
        try:
            start_time = datetime.utcnow()
            
            if not self.firestore_client:
                raise IntegrationError("Firestore client not initialized")
            
            batch = self.firestore_client.batch()
            
            for operation in operations:
                collection_ref = self.firestore_client.collection(operation.collection)
                
                if operation.operation_type == "create":
                    if operation.document_id:
                        doc_ref = collection_ref.document(operation.document_id)
                    else:
                        doc_ref = collection_ref.document()
                    
                    data = operation.data or {}
                    data.update({
                        "created_at": firestore.SERVER_TIMESTAMP,
                        "updated_at": firestore.SERVER_TIMESTAMP
                    })
                    
                    batch.set(doc_ref, data, merge=operation.merge)
                
                elif operation.operation_type == "update":
                    doc_ref = collection_ref.document(operation.document_id)
                    data = operation.data or {}
                    data["updated_at"] = firestore.SERVER_TIMESTAMP
                    
                    if operation.merge:
                        batch.set(doc_ref, data, merge=True)
                    else:
                        batch.update(doc_ref, data)
                
                elif operation.operation_type == "delete":
                    doc_ref = collection_ref.document(operation.document_id)
                    batch.delete(doc_ref)
            
            # Commit batch
            batch.commit()
            
            # Invalidate relevant cache entries
            for operation in operations:
                cache_key = f"{operation.collection}/{operation.document_id}"
                if cache_key in self.query_cache:
                    del self.query_cache[cache_key]
            
            # Update metrics
            self.metrics["operations_performed"] += 1
            self.metrics["documents_processed"] += len(operations)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firestore_batch_completed", 1, {
                "operations_count": len(operations)
            })
            
            # Audit log
            await self.audit_logger.log_action(
                action="firestore_batch_operations",
                details={"operations_count": len(operations)}
            )
            
            return True
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to perform batch operations: {e}")
            await self.monitoring.record_error("firestore_batch_error", str(e))
            raise IntegrationError(f"Batch operations failed: {e}")
    
    # ==================== AUTHENTICATION OPERATIONS ====================
    
    async def create_user(self, email: str, password: str, display_name: Optional[str] = None,
                         custom_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create Firebase user
        Demonstrates: Security - User management and authentication
        """
        try:
            start_time = datetime.utcnow()
            
            # Create user
            user_record = self.auth_client.create_user(
                email=email,
                password=password,
                display_name=display_name,
                email_verified=False
            )
            
            # Set custom claims if provided
            if custom_claims:
                self.auth_client.set_custom_user_claims(user_record.uid, custom_claims)
            
            # Update metrics
            self.metrics["auth_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firebase_user_created", 1, {
                "user_id": user_record.uid
            })
            
            # Audit log
            await self.audit_logger.log_action(
                action="firebase_user_created",
                user_id=user_record.uid,
                details={"email": email, "display_name": display_name}
            )
            
            return user_record.uid
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to create user: {e}")
            await self.monitoring.record_error("firebase_user_create_error", str(e))
            raise IntegrationError(f"User creation failed: {e}")
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get Firebase user by ID"""
        try:
            start_time = datetime.utcnow()
            
            user_record = self.auth_client.get_user(user_id)
            
            user_data = {
                "uid": user_record.uid,
                "email": user_record.email,
                "display_name": user_record.display_name,
                "photo_url": user_record.photo_url,
                "email_verified": user_record.email_verified,
                "disabled": user_record.disabled,
                "creation_time": user_record.user_metadata.creation_timestamp,
                "last_sign_in": user_record.user_metadata.last_sign_in_timestamp,
                "custom_claims": user_record.custom_claims or {}
            }
            
            # Update metrics
            self.metrics["auth_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            return user_data
            
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to get user: {e}")
            await self.monitoring.record_error("firebase_user_get_error", str(e))
            raise IntegrationError(f"User retrieval failed: {e}")
    
    async def update_user(self, user_id: str, **kwargs) -> bool:
        """Update Firebase user"""
        try:
            start_time = datetime.utcnow()
            
            self.auth_client.update_user(user_id, **kwargs)
            
            # Update metrics
            self.metrics["auth_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firebase_user_updated", 1, {
                "user_id": user_id
            })
            
            # Audit log
            await self.audit_logger.log_action(
                action="firebase_user_updated",
                user_id=user_id,
                details=kwargs
            )
            
            return True
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to update user: {e}")
            await self.monitoring.record_error("firebase_user_update_error", str(e))
            raise IntegrationError(f"User update failed: {e}")
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete Firebase user"""
        try:
            start_time = datetime.utcnow()
            
            self.auth_client.delete_user(user_id)
            
            # Update metrics
            self.metrics["auth_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firebase_user_deleted", 1, {
                "user_id": user_id
            })
            
            # Audit log
            await self.audit_logger.log_action(
                action="firebase_user_deleted",
                user_id=user_id
            )
            
            return True
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to delete user: {e}")
            await self.monitoring.record_error("firebase_user_delete_error", str(e))
            raise IntegrationError(f"User deletion failed: {e}")
    
    async def verify_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token
        Demonstrates: Security - Token verification and validation
        """
        try:
            start_time = datetime.utcnow()
            
            decoded_token = self.auth_client.verify_id_token(id_token)
            
            # Update metrics
            self.metrics["auth_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            return decoded_token
            
        except Exception as e:
            self.logger.error(f"Failed to verify token: {e}")
            await self.monitoring.record_error("firebase_token_verify_error", str(e))
            return None
    
    async def create_custom_token(self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """Create custom Firebase token"""
        try:
            start_time = datetime.utcnow()
            
            custom_token = self.auth_client.create_custom_token(user_id, additional_claims)
            
            # Update metrics
            self.metrics["auth_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            return custom_token.decode('utf-8')
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to create custom token: {e}")
            await self.monitoring.record_error("firebase_custom_token_error", str(e))
            raise IntegrationError(f"Custom token creation failed: {e}")
    
    # ==================== STORAGE OPERATIONS ====================
    
    async def upload_file(self, file_path: str, destination_path: str, 
                         metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Upload file to Firebase Storage
        Demonstrates: Backend Senior - File storage and management
        """
        try:
            start_time = datetime.utcnow()
            
            if not self.storage_client:
                raise IntegrationError("Storage client not initialized")
            
            blob = self.storage_client.blob(destination_path)
            
            # Set metadata if provided
            if metadata:
                blob.metadata = metadata
            
            # Upload file
            blob.upload_from_filename(file_path)
            
            # Make public if needed (configurable)
            # blob.make_public()
            
            # Update metrics
            self.metrics["storage_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firebase_file_uploaded", 1, {
                "destination_path": destination_path
            })
            
            # Audit log
            await self.audit_logger.log_action(
                action="firebase_file_uploaded",
                resource_id=destination_path,
                details={"file_path": file_path, "metadata": metadata}
            )
            
            return blob.public_url if blob.public_url else f"gs://{self.firebase_config.storage_bucket}/{destination_path}"
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to upload file: {e}")
            await self.monitoring.record_error("firebase_upload_error", str(e))
            raise IntegrationError(f"File upload failed: {e}")
    
    async def download_file(self, source_path: str, destination_path: str) -> bool:
        """Download file from Firebase Storage"""
        try:
            start_time = datetime.utcnow()
            
            if not self.storage_client:
                raise IntegrationError("Storage client not initialized")
            
            blob = self.storage_client.blob(source_path)
            blob.download_to_filename(destination_path)
            
            # Update metrics
            self.metrics["storage_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firebase_file_downloaded", 1, {
                "source_path": source_path
            })
            
            return True
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to download file: {e}")
            await self.monitoring.record_error("firebase_download_error", str(e))
            raise IntegrationError(f"File download failed: {e}")
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from Firebase Storage"""
        try:
            start_time = datetime.utcnow()
            
            if not self.storage_client:
                raise IntegrationError("Storage client not initialized")
            
            blob = self.storage_client.blob(file_path)
            blob.delete()
            
            # Update metrics
            self.metrics["storage_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firebase_file_deleted", 1, {
                "file_path": file_path
            })
            
            # Audit log
            await self.audit_logger.log_action(
                action="firebase_file_deleted",
                resource_id=file_path
            )
            
            return True
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to delete file: {e}")
            await self.monitoring.record_error("firebase_delete_file_error", str(e))
            raise IntegrationError(f"File deletion failed: {e}")
    
    async def list_files(self, prefix: Optional[str] = None, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """List files in Firebase Storage"""
        try:
            start_time = datetime.utcnow()
            
            if not self.storage_client:
                raise IntegrationError("Storage client not initialized")
            
            blobs = self.storage_client.list_blobs(prefix=prefix, max_results=max_results)
            
            files = []
            for blob in blobs:
                file_info = {
                    "name": blob.name,
                    "size": blob.size,
                    "created": blob.time_created,
                    "updated": blob.updated,
                    "content_type": blob.content_type,
                    "metadata": blob.metadata or {},
                    "public_url": blob.public_url
                }
                files.append(file_info)
            
            # Update metrics
            self.metrics["storage_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            return files
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to list files: {e}")
            await self.monitoring.record_error("firebase_list_files_error", str(e))
            raise IntegrationError(f"File listing failed: {e}")
    
    # ==================== MESSAGING OPERATIONS ====================
    
    async def send_notification(self, token: str, title: str, body: str, 
                              data: Optional[Dict[str, str]] = None) -> str:
        """
        Send push notification via Firebase Cloud Messaging
        Demonstrates: Backend Senior - Real-time messaging integration
        """
        try:
            start_time = datetime.utcnow()
            
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                token=token
            )
            
            response = self.messaging_client.send(message)
            
            # Update metrics
            self.metrics["messaging_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firebase_notification_sent", 1, {
                "token": token[:10] + "..."  # Partial token for privacy
            })
            
            # Audit log
            await self.audit_logger.log_action(
                action="firebase_notification_sent",
                details={"title": title, "body": body}
            )
            
            return response
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to send notification: {e}")
            await self.monitoring.record_error("firebase_notification_error", str(e))
            raise IntegrationError(f"Notification sending failed: {e}")
    
    async def send_multicast_notification(self, tokens: List[str], title: str, body: str,
                                        data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Send notification to multiple devices"""
        try:
            start_time = datetime.utcnow()
            
            message = messaging.MulticastMessage(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                tokens=tokens
            )
            
            response = self.messaging_client.send_multicast(message)
            
            # Update metrics
            self.metrics["messaging_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firebase_multicast_sent", 1, {
                "token_count": len(tokens),
                "success_count": response.success_count,
                "failure_count": response.failure_count
            })
            
            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": [
                    {
                        "success": resp.success,
                        "message_id": resp.message_id if resp.success else None,
                        "error": str(resp.exception) if not resp.success else None
                    }
                    for resp in response.responses
                ]
            }
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to send multicast notification: {e}")
            await self.monitoring.record_error("firebase_multicast_error", str(e))
            raise IntegrationError(f"Multicast notification failed: {e}")
    
    async def subscribe_to_topic(self, tokens: List[str], topic: str) -> Dict[str, Any]:
        """Subscribe tokens to a topic"""
        try:
            start_time = datetime.utcnow()
            
            response = self.messaging_client.subscribe_to_topic(tokens, topic)
            
            # Update metrics
            self.metrics["messaging_operations"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_response_time(processing_time)
            
            await self.monitoring.record_metric("firebase_topic_subscription", 1, {
                "topic": topic,
                "token_count": len(tokens),
                "success_count": response.success_count,
                "failure_count": response.failure_count
            })
            
            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
            
        except Exception as e:
            self.metrics["error_count"] += 1
            self.logger.error(f"Failed to subscribe to topic: {e}")
            await self.monitoring.record_error("firebase_topic_subscribe_error", str(e))
            raise IntegrationError(f"Topic subscription failed: {e}")
    
    # ==================== REAL-TIME DATABASE OPERATIONS ====================
    
    async def set_realtime_data(self, path: str, data: Any) -> bool:
        """Set data in Firebase Realtime Database"""
        # Note: This would require firebase-admin realtime database support
        # For now, using Firestore as the primary database
        collection, document = path.split("/", 1) if "/" in path else (path, None)
        
        if document:
            return await self.update_document(collection, document, {"data": data})
        else:
            doc_id = await self.create_document(collection, data={"data": data})
            return bool(doc_id)
    
    async def get_realtime_data(self, path: str) -> Any:
        """Get data from Firebase Realtime Database"""
        collection, document = path.split("/", 1) if "/" in path else (path, None)
        
        if document:
            doc_data = await self.get_document(collection, document)
            return doc_data.get("data") if doc_data else None
        else:
            # Return first document for collection queries
            docs = await self.query_collection(collection, limit=1)
            return docs[0].get("data") if docs else None
    
    # ==================== UTILITY METHODS ====================
    
    def _update_average_response_time(self, response_time: float) -> None:
        """Update average response time metric"""
        current_avg = self.metrics["average_response_time"]
        total_operations = self.metrics["operations_performed"]
        
        if total_operations == 1:
            self.metrics["average_response_time"] = response_time
        else:
            self.metrics["average_response_time"] = (
                (current_avg * (total_operations - 1) + response_time) / total_operations
            )
    
    async def clear_cache(self) -> None:
        """Clear query cache"""
        self.query_cache.clear()
        await self.monitoring.record_metric("firebase_cache_cleared", 1)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.query_cache)
        expired_entries = 0
        
        current_time = datetime.utcnow()
        for entry in self.query_cache.values():
            if current_time - entry["timestamp"] > timedelta(seconds=self.cache_ttl):
                expired_entries += 1
        
        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "cache_hit_rate": self.metrics["cache_hits"] / max(self.metrics["operations_performed"], 1),
            "cache_ttl": self.cache_ttl
        }
    
    # ==================== HEALTH AND MONITORING ====================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check
        Demonstrates: DevOps - Service monitoring and health validation
        """
        health_status = {
            "service": "firebase_integration",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        try:
            # Check initialization
            if not self.is_initialized:
                health_status["status"] = "unhealthy"
                health_status["components"]["initialization"] = "not_initialized"
                return health_status
            
            # Check Firestore
            try:
                test_doc = self.firestore_client.collection("_health").document("test")
                test_doc.set({"timestamp": firestore.SERVER_TIMESTAMP})
                test_doc.delete()
                health_status["components"]["firestore"] = "healthy"
            except Exception as e:
                health_status["components"]["firestore"] = f"unhealthy: {str(e)}"
                health_status["status"] = "degraded"
            
            # Check Authentication
            try:
                self.auth_client.list_users(max_results=1)
                health_status["components"]["authentication"] = "healthy"
            except Exception as e:
                health_status["components"]["authentication"] = f"degraded: {str(e)}"
                if health_status["status"] == "healthy":
                    health_status["status"] = "degraded"
            
            # Check Storage
            if self.storage_client:
                try:
                    list(self.storage_client.list_blobs(max_results=1))
                    health_status["components"]["storage"] = "healthy"
                except Exception as e:
                    health_status["components"]["storage"] = f"degraded: {str(e)}"
                    if health_status["status"] == "healthy":
                        health_status["status"] = "degraded"
            else:
                health_status["components"]["storage"] = "not_configured"
            
            # Add metrics
            health_status["metrics"] = self.metrics.copy()
            health_status["cache_stats"] = await self.get_cache_stats()
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        return {
            "operations": {
                "total_operations": self.metrics["operations_performed"],
                "documents_processed": self.metrics["documents_processed"],
                "storage_operations": self.metrics["storage_operations"],
                "auth_operations": self.metrics["auth_operations"],
                "messaging_operations": self.metrics["messaging_operations"]
            },
            "performance": {
                "average_response_time": self.metrics["average_response_time"],
                "error_rate": self.metrics["error_count"] / max(self.metrics["operations_performed"], 1),
                "cache_hit_rate": self.metrics["cache_hits"] / max(self.metrics["operations_performed"], 1)
            },
            "cache": await self.get_cache_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def cleanup(self) -> None:
        """Cleanup Firebase resources"""
        try:
            # Clear cache
            self.query_cache.clear()
            
            # Note: Firebase Admin SDK doesn't require explicit cleanup
            # but we can perform any necessary cleanup here
            
            self.is_initialized = False
            self.logger.info("Firebase integration cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Export main class
__all__ = ["FirebaseIntegration", "FirebaseConfig", "DocumentOperation", "QueryFilter", "StorageFile"]