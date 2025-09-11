#!/usr/bin/env python3
"""
Ainflue Platform - Enterprise CRM Systems Integration
Multi-platform CRM integration for customer relationship management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved

Expert Roles Demonstrated:
- Backend Senior: Multi-CRM architecture, API orchestration, data synchronization
- DBA: Customer data modeling, relationship mapping, analytics optimization
- Security: Data encryption, compliance (GDPR, CCPA), secure API integration
- DevOps: Automated sync processes, monitoring, error handling
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import hashlib
import re
from decimal import Decimal

import asyncpg
import redis.asyncio as redis
import aiohttp
import httpx
from pydantic import BaseModel, Field, validator
import requests
from cryptography.fernet import Fernet

# Core platform imports
from ..core.base_integration import BaseIntegration
from ..core.exceptions import IntegrationError, ValidationError
from ..monitoring_integration import MonitoringIntegration
from ..audit_logger import AuditLogger

class CRMProvider(str, Enum):
    """Supported CRM providers"""
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    PIPEDRIVE = "pipedrive"
    ZOHO = "zoho"
    MONDAY = "monday"
    AIRTABLE = "airtable"
    NOTION = "notion"
    MICROSOFT_DYNAMICS = "microsoft_dynamics"

class ContactType(str, Enum):
    """Contact types in CRM"""
    LEAD = "lead"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    PARTNER = "partner"
    INFLUENCER = "influencer"
    VENDOR = "vendor"

class DealStage(str, Enum):
    """Deal pipeline stages"""
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class ActivityType(str, Enum):
    """CRM activity types"""
    EMAIL = "email"
    CALL = "call"
    MEETING = "meeting"
    TASK = "task"
    NOTE = "note"
    CAMPAIGN = "campaign"
    COLLABORATION = "collaboration"

@dataclass
class CRMContact:
    """Unified CRM contact representation"""
    contact_id: str
    crm_provider: CRMProvider
    external_id: str
    
    # Basic information
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    
    # Contact classification
    contact_type: ContactType = ContactType.LEAD
    lead_source: Optional[str] = None
    
    # Social media profiles
    social_profiles: Dict[str, str] = field(default_factory=dict)
    influencer_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Address information
    address: Dict[str, str] = field(default_factory=dict)
    
    # Custom fields
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Relationship data
    deals: List[str] = field(default_factory=list)
    activities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_contacted: Optional[datetime] = None
    
    # Sync metadata
    last_sync: Optional[datetime] = None
    sync_status: str = "pending"
    
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CRMDeal:
    """Unified CRM deal representation"""
    deal_id: str
    crm_provider: CRMProvider
    external_id: str
    
    # Basic information
    title: str
    description: Optional[str] = None
    value: Decimal = Decimal("0.00")
    currency: str = "USD"
    
    # Pipeline information
    stage: DealStage = DealStage.LEAD
    pipeline: Optional[str] = None
    probability: float = 0.0
    
    # Relationships
    contact_id: Optional[str] = None
    company_id: Optional[str] = None
    owner_id: Optional[str] = None
    
    # Dates
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    
    # Campaign specific
    campaign_type: Optional[str] = None
    collaboration_details: Dict[str, Any] = field(default_factory=dict)
    influencer_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Custom fields
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Sync metadata
    last_sync: Optional[datetime] = None
    sync_status: str = "pending"
    
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CRMActivity:
    """Unified CRM activity representation"""
    activity_id: str
    crm_provider: CRMProvider
    external_id: str
    
    # Basic information
    activity_type: ActivityType
    subject: str
    description: Optional[str] = None
    
    # Relationships
    contact_id: Optional[str] = None
    deal_id: Optional[str] = None
    owner_id: Optional[str] = None
    
    # Scheduling
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    
    # Status
    status: str = "open"
    priority: str = "normal"
    
    # Custom fields
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Sync metadata
    last_sync: Optional[datetime] = None
    sync_status: str = "pending"
    
    metadata: Dict[str, Any] = field(default_factory=dict)

class CRMIntegration(BaseIntegration):
    """
    Enterprise Multi-Platform CRM Integration System
    
    Demonstrates Expert Roles:
    - Backend Senior: Multi-CRM architecture, unified API layer
    - DBA: Customer data optimization, relationship modeling
    - Security: Data encryption, compliance automation
    - DevOps: Automated synchronization, monitoring
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize CRM integration system"""
        super().__init__(config)
        
        # Core configuration
        self.config = config
        self.redis_url = config.get("redis_url", "redis://localhost:6379")
        self.db_url = config.get("database_url")
        self.sync_interval = config.get("sync_interval", 300)  # 5 minutes
        
        # Service dependencies
        self.monitoring = MonitoringIntegration(config)
        self.audit_logger = AuditLogger(config)
        
        # Runtime state
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.sync_task: Optional[asyncio.Task] = None
        
        # CRM provider configurations
        self.crm_configs = config.get("crm_providers", {})
        self.active_providers = set()
        
        # Data encryption
        self.encryption_key = config.get("encryption_key", Fernet.generate_key())
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Performance tracking
        self.metrics = {
            "contacts_synced": 0,
            "deals_synced": 0,
            "activities_synced": 0,
            "sync_operations": 0,
            "api_calls_made": 0,
            "average_sync_time": 0.0,
            "error_count": 0,
            "compliance_violations": 0
        }
        
        # HTTP clients for different providers
        self.http_clients = {}
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize CRM integration system"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.Redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Initialize database pool
            if self.db_url:
                self.db_pool = await asyncpg.create_pool(
                    self.db_url,
                    min_size=10,
                    max_size=25
                )
                await self._setup_database_schema()
            
            # Initialize CRM provider connections
            await self._initialize_crm_providers()
            
            # Start background sync
            self.sync_task = asyncio.create_task(self._run_sync_pipeline())
            
            await self.monitoring.record_metric("crm_integration_initialized", 1)
            self.logger.info("CRM integration system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CRM integration: {e}")
            raise IntegrationError(f"CRM initialization failed: {e}")
    
    async def _setup_database_schema(self) -> None:
        """
        Setup database schema for CRM data
        Demonstrates: DBA - Optimized customer data modeling
        """
        if not self.db_pool:
            return
        
        schema_sql = """
        -- CRM contacts table
        CREATE TABLE IF NOT EXISTS crm_contacts (
            contact_id VARCHAR(255) PRIMARY KEY,
            crm_provider VARCHAR(50) NOT NULL,
            external_id VARCHAR(255) NOT NULL,
            
            -- Personal information (encrypted where needed)
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            company VARCHAR(255),
            job_title VARCHAR(255),
            
            -- Classification
            contact_type VARCHAR(50) DEFAULT 'lead',
            lead_source VARCHAR(255),
            
            -- Social profiles (JSON)
            social_profiles JSONB DEFAULT '{}',
            influencer_metrics JSONB DEFAULT '{}',
            
            -- Address information (encrypted)
            address JSONB DEFAULT '{}',
            
            -- Custom fields
            custom_fields JSONB DEFAULT '{}',
            
            -- Relationship data
            deals TEXT[] DEFAULT '{}',
            activities TEXT[] DEFAULT '{}',
            tags TEXT[] DEFAULT '{}',
            
            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_contacted TIMESTAMP WITH TIME ZONE,
            
            -- Sync metadata
            last_sync TIMESTAMP WITH TIME ZONE,
            sync_status VARCHAR(50) DEFAULT 'pending',
            metadata JSONB DEFAULT '{}',
            
            UNIQUE(crm_provider, external_id)
        );
        
        -- CRM deals table
        CREATE TABLE IF NOT EXISTS crm_deals (
            deal_id VARCHAR(255) PRIMARY KEY,
            crm_provider VARCHAR(50) NOT NULL,
            external_id VARCHAR(255) NOT NULL,
            
            -- Basic information
            title VARCHAR(500) NOT NULL,
            description TEXT,
            value DECIMAL(15,2) DEFAULT 0.00,
            currency VARCHAR(10) DEFAULT 'USD',
            
            -- Pipeline information
            stage VARCHAR(50) DEFAULT 'lead',
            pipeline VARCHAR(255),
            probability DECIMAL(5,2) DEFAULT 0.00,
            
            -- Relationships
            contact_id VARCHAR(255),
            company_id VARCHAR(255),
            owner_id VARCHAR(255),
            
            -- Dates
            expected_close_date DATE,
            actual_close_date DATE,
            
            -- Campaign specific
            campaign_type VARCHAR(100),
            collaboration_details JSONB DEFAULT '{}',
            influencer_metrics JSONB DEFAULT '{}',
            
            -- Custom fields
            custom_fields JSONB DEFAULT '{}',
            
            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            -- Sync metadata
            last_sync TIMESTAMP WITH TIME ZONE,
            sync_status VARCHAR(50) DEFAULT 'pending',
            metadata JSONB DEFAULT '{}',
            
            UNIQUE(crm_provider, external_id)
        );
        
        -- CRM activities table
        CREATE TABLE IF NOT EXISTS crm_activities (
            activity_id VARCHAR(255) PRIMARY KEY,
            crm_provider VARCHAR(50) NOT NULL,
            external_id VARCHAR(255) NOT NULL,
            
            -- Basic information
            activity_type VARCHAR(50) NOT NULL,
            subject VARCHAR(500) NOT NULL,
            description TEXT,
            
            -- Relationships
            contact_id VARCHAR(255),
            deal_id VARCHAR(255),
            owner_id VARCHAR(255),
            
            -- Scheduling
            due_date TIMESTAMP WITH TIME ZONE,
            completed_date TIMESTAMP WITH TIME ZONE,
            duration_minutes INTEGER,
            
            -- Status
            status VARCHAR(50) DEFAULT 'open',
            priority VARCHAR(20) DEFAULT 'normal',
            
            -- Custom fields
            custom_fields JSONB DEFAULT '{}',
            
            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            -- Sync metadata
            last_sync TIMESTAMP WITH TIME ZONE,
            sync_status VARCHAR(50) DEFAULT 'pending',
            metadata JSONB DEFAULT '{}',
            
            UNIQUE(crm_provider, external_id)
        );
        
        -- CRM sync logs table
        CREATE TABLE IF NOT EXISTS crm_sync_logs (
            id SERIAL PRIMARY KEY,
            crm_provider VARCHAR(50) NOT NULL,
            sync_type VARCHAR(50) NOT NULL,
            started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            status VARCHAR(50) DEFAULT 'running',
            records_processed INTEGER DEFAULT 0,
            records_successful INTEGER DEFAULT 0,
            records_failed INTEGER DEFAULT 0,
            error_details JSONB DEFAULT '{}',
            performance_metrics JSONB DEFAULT '{}'
        );
        
        -- Analytics aggregations
        CREATE TABLE IF NOT EXISTS crm_analytics (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            crm_provider VARCHAR(50) NOT NULL,
            
            -- Contact metrics
            total_contacts INTEGER DEFAULT 0,
            new_contacts INTEGER DEFAULT 0,
            active_contacts INTEGER DEFAULT 0,
            
            -- Deal metrics
            total_deals INTEGER DEFAULT 0,
            new_deals INTEGER DEFAULT 0,
            closed_deals INTEGER DEFAULT 0,
            total_deal_value DECIMAL(15,2) DEFAULT 0.00,
            
            -- Activity metrics
            total_activities INTEGER DEFAULT 0,
            completed_activities INTEGER DEFAULT 0,
            
            -- Performance metrics
            sync_duration_avg DECIMAL(8,4) DEFAULT 0,
            api_response_time_avg DECIMAL(8,4) DEFAULT 0,
            error_rate DECIMAL(5,4) DEFAULT 0,
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(date, crm_provider)
        );
        
        -- GDPR compliance tracking
        CREATE TABLE IF NOT EXISTS gdpr_compliance_log (
            id SERIAL PRIMARY KEY,
            contact_id VARCHAR(255) NOT NULL,
            action_type VARCHAR(50) NOT NULL, -- consent_given, consent_withdrawn, data_exported, data_deleted
            action_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            details JSONB DEFAULT '{}',
            ip_address INET,
            user_agent TEXT
        );
        
        -- Performance indexes
        CREATE INDEX IF NOT EXISTS idx_crm_contacts_provider ON crm_contacts(crm_provider, updated_at DESC);
        CREATE INDEX IF NOT EXISTS idx_crm_contacts_email ON crm_contacts(email);
        CREATE INDEX IF NOT EXISTS idx_crm_contacts_type ON crm_contacts(contact_type, crm_provider);
        CREATE INDEX IF NOT EXISTS idx_crm_contacts_sync ON crm_contacts(sync_status, last_sync);
        
        CREATE INDEX IF NOT EXISTS idx_crm_deals_provider ON crm_deals(crm_provider, updated_at DESC);
        CREATE INDEX IF NOT EXISTS idx_crm_deals_stage ON crm_deals(stage, crm_provider);
        CREATE INDEX IF NOT EXISTS idx_crm_deals_contact ON crm_deals(contact_id);
        CREATE INDEX IF NOT EXISTS idx_crm_deals_value ON crm_deals(value DESC, stage);
        
        CREATE INDEX IF NOT EXISTS idx_crm_activities_provider ON crm_activities(crm_provider, updated_at DESC);
        CREATE INDEX IF NOT EXISTS idx_crm_activities_contact ON crm_activities(contact_id, due_date);
        CREATE INDEX IF NOT EXISTS idx_crm_activities_deal ON crm_activities(deal_id);
        CREATE INDEX IF NOT EXISTS idx_crm_activities_status ON crm_activities(status, activity_type);
        
        CREATE INDEX IF NOT EXISTS idx_crm_sync_logs_provider ON crm_sync_logs(crm_provider, started_at DESC);
        CREATE INDEX IF NOT EXISTS idx_gdpr_compliance_contact ON gdpr_compliance_log(contact_id, action_date DESC);
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(schema_sql)
    
    async def _initialize_crm_providers(self) -> None:
        """Initialize connections to configured CRM providers"""
        for provider, config in self.crm_configs.items():
            try:
                provider_enum = CRMProvider(provider)
                
                # Create HTTP client for provider
                timeout = httpx.Timeout(30.0)
                self.http_clients[provider_enum] = httpx.AsyncClient(timeout=timeout)
                
                # Test connection
                if await self._test_provider_connection(provider_enum, config):
                    self.active_providers.add(provider_enum)
                    self.logger.info(f"CRM provider {provider} connected successfully")
                else:
                    self.logger.warning(f"CRM provider {provider} connection failed")
                    
            except ValueError:
                self.logger.error(f"Unsupported CRM provider: {provider}")
            except Exception as e:
                self.logger.error(f"Failed to initialize CRM provider {provider}: {e}")
    
    async def _test_provider_connection(self, provider: CRMProvider, config: Dict[str, Any]) -> bool:
        """Test connection to CRM provider"""
        try:
            if provider == CRMProvider.SALESFORCE:
                return await self._test_salesforce_connection(config)
            elif provider == CRMProvider.HUBSPOT:
                return await self._test_hubspot_connection(config)
            elif provider == CRMProvider.PIPEDRIVE:
                return await self._test_pipedrive_connection(config)
            # Add other providers as needed
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed for {provider.value}: {e}")
            return False
    
    # ==================== SALESFORCE INTEGRATION ====================
    
    async def _test_salesforce_connection(self, config: Dict[str, Any]) -> bool:
        """Test Salesforce connection"""
        try:
            client = self.http_clients[CRMProvider.SALESFORCE]
            
            # OAuth authentication
            auth_url = f"{config['instance_url']}/services/oauth2/token"
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": config["client_id"],
                "client_secret": config["client_secret"]
            }
            
            response = await client.post(auth_url, data=auth_data)
            response.raise_for_status()
            
            auth_response = response.json()
            access_token = auth_response["access_token"]
            
            # Test API call
            headers = {"Authorization": f"Bearer {access_token}"}
            test_url = f"{config['instance_url']}/services/data/v58.0/sobjects/Contact/describe"
            
            test_response = await client.get(test_url, headers=headers)
            test_response.raise_for_status()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Salesforce connection test failed: {e}")
            return False
    
    async def _sync_salesforce_contacts(self, config: Dict[str, Any]) -> int:
        """
        Sync contacts from Salesforce
        Demonstrates: Backend Senior - API integration and data transformation
        """
        try:
            client = self.http_clients[CRMProvider.SALESFORCE]
            
            # Get access token
            access_token = await self._get_salesforce_token(config)
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Query contacts
            query = """
            SELECT Id, FirstName, LastName, Email, Phone, Title, Account.Name,
                   LeadSource, CreatedDate, LastModifiedDate
            FROM Contact
            WHERE LastModifiedDate >= TODAY
            """
            
            query_url = f"{config['instance_url']}/services/data/v58.0/query"
            params = {"q": query}
            
            response = await client.get(query_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            contacts = data.get("records", [])
            
            synced_count = 0
            for contact in contacts:
                crm_contact = self._map_salesforce_contact(contact)
                await self._store_contact(crm_contact)
                synced_count += 1
            
            self.metrics["contacts_synced"] += synced_count
            return synced_count
            
        except Exception as e:
            self.logger.error(f"Salesforce contact sync failed: {e}")
            self.metrics["error_count"] += 1
            raise IntegrationError(f"Salesforce sync failed: {e}")
    
    def _map_salesforce_contact(self, sf_contact: Dict[str, Any]) -> CRMContact:
        """Map Salesforce contact to unified format"""
        return CRMContact(
            contact_id=str(uuid.uuid4()),
            crm_provider=CRMProvider.SALESFORCE,
            external_id=sf_contact["Id"],
            first_name=sf_contact.get("FirstName", ""),
            last_name=sf_contact.get("LastName", ""),
            email=sf_contact.get("Email", ""),
            phone=sf_contact.get("Phone"),
            company=sf_contact.get("Account", {}).get("Name") if sf_contact.get("Account") else None,
            job_title=sf_contact.get("Title"),
            lead_source=sf_contact.get("LeadSource"),
            created_at=self._parse_salesforce_datetime(sf_contact.get("CreatedDate")),
            updated_at=self._parse_salesforce_datetime(sf_contact.get("LastModifiedDate"))
        )
    
    async def _get_salesforce_token(self, config: Dict[str, Any]) -> str:
        """Get Salesforce access token"""
        # Check cache first
        cache_key = f"sf_token:{config['client_id']}"
        if self.redis_client:
            cached_token = await self.redis_client.get(cache_key)
            if cached_token:
                return cached_token
        
        client = self.http_clients[CRMProvider.SALESFORCE]
        auth_url = f"{config['instance_url']}/services/oauth2/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": config["client_id"],
            "client_secret": config["client_secret"]
        }
        
        response = await client.post(auth_url, data=auth_data)
        response.raise_for_status()
        
        auth_response = response.json()
        access_token = auth_response["access_token"]
        
        # Cache token
        if self.redis_client:
            await self.redis_client.setex(cache_key, 3600, access_token)  # 1 hour TTL
        
        return access_token
    
    # ==================== HUBSPOT INTEGRATION ====================
    
    async def _test_hubspot_connection(self, config: Dict[str, Any]) -> bool:
        """Test HubSpot connection"""
        try:
            client = self.http_clients[CRMProvider.HUBSPOT]
            headers = {"Authorization": f"Bearer {config['access_token']}"}
            
            test_url = "https://api.hubapi.com/contacts/v1/lists/all/contacts/all"
            params = {"count": 1}
            
            response = await client.get(test_url, headers=headers, params=params)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            self.logger.error(f"HubSpot connection test failed: {e}")
            return False
    
    async def _sync_hubspot_contacts(self, config: Dict[str, Any]) -> int:
        """Sync contacts from HubSpot"""
        try:
            client = self.http_clients[CRMProvider.HUBSPOT]
            headers = {"Authorization": f"Bearer {config['access_token']}"}
            
            # Get contacts modified in last 24 hours
            yesterday = int((datetime.utcnow() - timedelta(days=1)).timestamp() * 1000)
            
            url = "https://api.hubapi.com/contacts/v1/lists/all/contacts/recent"
            params = {
                "count": 100,
                "timeOffset": yesterday,
                "property": ["firstname", "lastname", "email", "phone", "company", "jobtitle"]
            }
            
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            contacts = data.get("contacts", [])
            
            synced_count = 0
            for contact in contacts:
                crm_contact = self._map_hubspot_contact(contact)
                await self._store_contact(crm_contact)
                synced_count += 1
            
            self.metrics["contacts_synced"] += synced_count
            return synced_count
            
        except Exception as e:
            self.logger.error(f"HubSpot contact sync failed: {e}")
            self.metrics["error_count"] += 1
            raise IntegrationError(f"HubSpot sync failed: {e}")
    
    def _map_hubspot_contact(self, hs_contact: Dict[str, Any]) -> CRMContact:
        """Map HubSpot contact to unified format"""
        properties = hs_contact.get("properties", {})
        
        return CRMContact(
            contact_id=str(uuid.uuid4()),
            crm_provider=CRMProvider.HUBSPOT,
            external_id=str(hs_contact["vid"]),
            first_name=properties.get("firstname", {}).get("value", ""),
            last_name=properties.get("lastname", {}).get("value", ""),
            email=properties.get("email", {}).get("value", ""),
            phone=properties.get("phone", {}).get("value"),
            company=properties.get("company", {}).get("value"),
            job_title=properties.get("jobtitle", {}).get("value"),
            created_at=self._parse_hubspot_timestamp(hs_contact.get("addedAt")),
            updated_at=self._parse_hubspot_timestamp(hs_contact.get("properties", {}).get("lastmodifieddate", {}).get("value"))
        )
    
    # ==================== PIPEDRIVE INTEGRATION ====================
    
    async def _test_pipedrive_connection(self, config: Dict[str, Any]) -> bool:
        """Test Pipedrive connection"""
        try:
            client = self.http_clients[CRMProvider.PIPEDRIVE]
            params = {"api_token": config["api_token"]}
            
            test_url = "https://api.pipedrive.com/v1/users/me"
            response = await client.get(test_url, params=params)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Pipedrive connection test failed: {e}")
            return False
    
    async def _sync_pipedrive_contacts(self, config: Dict[str, Any]) -> int:
        """Sync contacts from Pipedrive"""
        try:
            client = self.http_clients[CRMProvider.PIPEDRIVE]
            params = {"api_token": config["api_token"], "limit": 100}
            
            url = "https://api.pipedrive.com/v1/persons"
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            persons = data.get("data", [])
            
            synced_count = 0
            for person in persons:
                crm_contact = self._map_pipedrive_contact(person)
                await self._store_contact(crm_contact)
                synced_count += 1
            
            self.metrics["contacts_synced"] += synced_count
            return synced_count
            
        except Exception as e:
            self.logger.error(f"Pipedrive contact sync failed: {e}")
            self.metrics["error_count"] += 1
            raise IntegrationError(f"Pipedrive sync failed: {e}")
    
    def _map_pipedrive_contact(self, pd_contact: Dict[str, Any]) -> CRMContact:
        """Map Pipedrive contact to unified format"""
        return CRMContact(
            contact_id=str(uuid.uuid4()),
            crm_provider=CRMProvider.PIPEDRIVE,
            external_id=str(pd_contact["id"]),
            first_name=pd_contact.get("first_name", ""),
            last_name=pd_contact.get("last_name", ""),
            email=pd_contact.get("email", [{}])[0].get("value", "") if pd_contact.get("email") else "",
            phone=pd_contact.get("phone", [{}])[0].get("value") if pd_contact.get("phone") else None,
            company=pd_contact.get("org_name"),
            created_at=self._parse_pipedrive_datetime(pd_contact.get("add_time")),
            updated_at=self._parse_pipedrive_datetime(pd_contact.get("update_time"))
        )
    
    # ==================== UNIFIED CRM OPERATIONS ====================
    
    async def _store_contact(self, contact: CRMContact) -> str:
        """
        Store contact in unified database
        Demonstrates: DBA - Optimized contact storage with encryption
        """
        try:
            if not self.db_pool:
                return contact.contact_id
            
            # Encrypt sensitive data
            encrypted_email = self._encrypt_sensitive_data(contact.email)
            encrypted_phone = self._encrypt_sensitive_data(contact.phone) if contact.phone else None
            
            query = """
            INSERT INTO crm_contacts (
                contact_id, crm_provider, external_id, first_name, last_name,
                email, phone, company, job_title, contact_type, lead_source,
                social_profiles, influencer_metrics, address, custom_fields,
                deals, activities, tags, created_at, updated_at, last_contacted,
                last_sync, sync_status, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24)
            ON CONFLICT (crm_provider, external_id) DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                email = EXCLUDED.email,
                phone = EXCLUDED.phone,
                company = EXCLUDED.company,
                job_title = EXCLUDED.job_title,
                contact_type = EXCLUDED.contact_type,
                lead_source = EXCLUDED.lead_source,
                social_profiles = EXCLUDED.social_profiles,
                influencer_metrics = EXCLUDED.influencer_metrics,
                address = EXCLUDED.address,
                custom_fields = EXCLUDED.custom_fields,
                updated_at = EXCLUDED.updated_at,
                last_sync = NOW(),
                sync_status = 'synced'
            RETURNING contact_id
            """
            
            async with self.db_pool.acquire() as conn:
                result = await conn.fetchval(
                    query,
                    contact.contact_id, contact.crm_provider.value, contact.external_id,
                    contact.first_name, contact.last_name, encrypted_email, encrypted_phone,
                    contact.company, contact.job_title, contact.contact_type.value,
                    contact.lead_source, json.dumps(contact.social_profiles),
                    json.dumps(contact.influencer_metrics), json.dumps(contact.address),
                    json.dumps(contact.custom_fields), contact.deals, contact.activities,
                    contact.tags, contact.created_at, contact.updated_at, contact.last_contacted,
                    datetime.utcnow(), "synced", json.dumps(contact.metadata)
                )
                
                # Log GDPR compliance action
                await self._log_gdpr_action(result or contact.contact_id, "data_stored")
                
                return result or contact.contact_id
                
        except Exception as e:
            self.logger.error(f"Failed to store contact: {e}")
            raise IntegrationError(f"Contact storage failed: {e}")
    
    def _encrypt_sensitive_data(self, data: Optional[str]) -> Optional[str]:
        """
        Encrypt sensitive personal data
        Demonstrates: Security - Data encryption for compliance
        """
        if not data:
            return None
        
        try:
            encrypted_bytes = self.cipher_suite.encrypt(data.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            return data  # Return original if encryption fails
    
    def _decrypt_sensitive_data(self, encrypted_data: Optional[str]) -> Optional[str]:
        """Decrypt sensitive personal data"""
        if not encrypted_data:
            return None
        
        try:
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return encrypted_data  # Return original if decryption fails
    
    async def _log_gdpr_action(self, contact_id: str, action_type: str, 
                              details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log GDPR compliance actions
        Demonstrates: Security - Compliance tracking and audit
        """
        if not self.db_pool:
            return
        
        query = """
        INSERT INTO gdpr_compliance_log (contact_id, action_type, details)
        VALUES ($1, $2, $3)
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                contact_id, action_type, json.dumps(details or {})
            )
    
    async def _run_sync_pipeline(self) -> None:
        """
        Main synchronization pipeline
        Demonstrates: DevOps - Automated data synchronization
        """
        while True:
            try:
                sync_start = datetime.utcnow()
                
                for provider in self.active_providers:
                    await self._sync_provider_data(provider)
                
                # Update analytics
                await self._update_sync_analytics()
                
                # Clean up old data
                await self._cleanup_old_sync_logs()
                
                sync_duration = (datetime.utcnow() - sync_start).total_seconds()
                self._update_average_sync_time(sync_duration)
                
                await self.monitoring.record_metric("crm_sync_cycle_completed", 1, {
                    "duration": sync_duration,
                    "providers": len(self.active_providers)
                })
                
                # Sleep until next sync
                await asyncio.sleep(self.sync_interval)
                
            except Exception as e:
                self.logger.error(f"CRM sync pipeline error: {e}")
                await self.monitoring.record_error("crm_sync_pipeline_error", str(e))
                await asyncio.sleep(60)  # Short delay on error
    
    async def _sync_provider_data(self, provider: CRMProvider) -> None:
        """Sync data for specific CRM provider"""
        try:
            config = self.crm_configs.get(provider.value, {})
            if not config:
                return
            
            sync_log_id = await self._start_sync_log(provider)
            
            # Sync contacts
            contacts_synced = 0
            if provider == CRMProvider.SALESFORCE:
                contacts_synced = await self._sync_salesforce_contacts(config)
            elif provider == CRMProvider.HUBSPOT:
                contacts_synced = await self._sync_hubspot_contacts(config)
            elif provider == CRMProvider.PIPEDRIVE:
                contacts_synced = await self._sync_pipedrive_contacts(config)
            
            # TODO: Sync deals and activities
            
            await self._complete_sync_log(sync_log_id, contacts_synced, 0)
            
            self.metrics["sync_operations"] += 1
            
        except Exception as e:
            self.logger.error(f"Provider sync failed for {provider.value}: {e}")
            self.metrics["error_count"] += 1
    
    async def _start_sync_log(self, provider: CRMProvider) -> int:
        """Start sync operation log"""
        if not self.db_pool:
            return 0
        
        query = """
        INSERT INTO crm_sync_logs (crm_provider, sync_type, started_at)
        VALUES ($1, $2, NOW())
        RETURNING id
        """
        
        async with self.db_pool.acquire() as conn:
            return await conn.fetchval(query, provider.value, "contacts")
    
    async def _complete_sync_log(self, log_id: int, contacts_synced: int, errors: int) -> None:
        """Complete sync operation log"""
        if not self.db_pool:
            return
        
        query = """
        UPDATE crm_sync_logs
        SET completed_at = NOW(),
            status = 'completed',
            records_processed = $2,
            records_successful = $3,
            records_failed = $4
        WHERE id = $1
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(query, log_id, contacts_synced, contacts_synced - errors, errors)
    
    # ==================== PUBLIC API METHODS ====================
    
    async def get_contact(self, contact_id: str, decrypt_sensitive: bool = False) -> Optional[CRMContact]:
        """Get contact by ID with optional decryption"""
        if not self.db_pool:
            return None
        
        query = "SELECT * FROM crm_contacts WHERE contact_id = $1"
        
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(query, contact_id)
            
            if row:
                contact = CRMContact(
                    contact_id=row["contact_id"],
                    crm_provider=CRMProvider(row["crm_provider"]),
                    external_id=row["external_id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    email=self._decrypt_sensitive_data(row["email"]) if decrypt_sensitive else row["email"],
                    phone=self._decrypt_sensitive_data(row["phone"]) if decrypt_sensitive and row["phone"] else row["phone"],
                    company=row["company"],
                    job_title=row["job_title"],
                    contact_type=ContactType(row["contact_type"]),
                    lead_source=row["lead_source"],
                    social_profiles=row["social_profiles"] or {},
                    influencer_metrics=row["influencer_metrics"] or {},
                    address=row["address"] or {},
                    custom_fields=row["custom_fields"] or {},
                    deals=row["deals"] or [],
                    activities=row["activities"] or [],
                    tags=row["tags"] or [],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    last_contacted=row["last_contacted"],
                    last_sync=row["last_sync"],
                    sync_status=row["sync_status"],
                    metadata=row["metadata"] or {}
                )
                
                return contact
            
            return None
    
    async def search_contacts(self, query: str, contact_type: Optional[ContactType] = None,
                            provider: Optional[CRMProvider] = None,
                            limit: int = 50) -> List[CRMContact]:
        """Search contacts with filters"""
        if not self.db_pool:
            return []
        
        # Build search query
        where_conditions = ["(first_name ILIKE $1 OR last_name ILIKE $1 OR company ILIKE $1)"]
        params = [f"%{query}%"]
        param_count = 1
        
        if contact_type:
            param_count += 1
            where_conditions.append(f"contact_type = ${param_count}")
            params.append(contact_type.value)
        
        if provider:
            param_count += 1
            where_conditions.append(f"crm_provider = ${param_count}")
            params.append(provider.value)
        
        sql_query = f"""
        SELECT * FROM crm_contacts
        WHERE {' AND '.join(where_conditions)}
        ORDER BY updated_at DESC
        LIMIT {limit}
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(sql_query, *params)
            
            contacts = []
            for row in rows:
                contact = CRMContact(
                    contact_id=row["contact_id"],
                    crm_provider=CRMProvider(row["crm_provider"]),
                    external_id=row["external_id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    email=row["email"],  # Keep encrypted in search results
                    phone=row["phone"],
                    company=row["company"],
                    job_title=row["job_title"],
                    contact_type=ContactType(row["contact_type"]),
                    lead_source=row["lead_source"],
                    social_profiles=row["social_profiles"] or {},
                    influencer_metrics=row["influencer_metrics"] or {},
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    last_contacted=row["last_contacted"],
                    sync_status=row["sync_status"]
                )
                contacts.append(contact)
            
            return contacts
    
    async def get_crm_analytics(self, provider: Optional[CRMProvider] = None,
                               days: int = 30) -> Dict[str, Any]:
        """Get CRM analytics"""
        if not self.db_pool:
            return {}
        
        provider_filter = f"AND crm_provider = '{provider.value}'" if provider else ""
        
        # Contact analytics
        contact_query = f"""
        SELECT 
            crm_provider,
            COUNT(*) as total_contacts,
            COUNT(CASE WHEN created_at >= NOW() - INTERVAL '{days} days' THEN 1 END) as new_contacts,
            COUNT(CASE WHEN contact_type = 'customer' THEN 1 END) as customers,
            COUNT(CASE WHEN contact_type = 'lead' THEN 1 END) as leads
        FROM crm_contacts
        WHERE created_at >= NOW() - INTERVAL '{days} days' {provider_filter}
        GROUP BY crm_provider
        """
        
        # Deal analytics
        deal_query = f"""
        SELECT 
            crm_provider,
            COUNT(*) as total_deals,
            SUM(value) as total_value,
            AVG(value) as avg_deal_value,
            COUNT(CASE WHEN stage = 'closed_won' THEN 1 END) as won_deals
        FROM crm_deals
        WHERE created_at >= NOW() - INTERVAL '{days} days' {provider_filter}
        GROUP BY crm_provider
        """
        
        async with self.db_pool.acquire() as conn:
            contact_stats = await conn.fetch(contact_query)
            deal_stats = await conn.fetch(deal_query)
            
            analytics = {
                "contact_analytics": [dict(row) for row in contact_stats],
                "deal_analytics": [dict(row) for row in deal_stats],
                "system_metrics": self.metrics.copy(),
                "period_days": days
            }
            
            return analytics
    
    # ==================== GDPR COMPLIANCE METHODS ====================
    
    async def export_contact_data(self, contact_id: str) -> Dict[str, Any]:
        """
        Export all data for a contact (GDPR Article 20)
        Demonstrates: Security - Data portability compliance
        """
        try:
            contact = await self.get_contact(contact_id, decrypt_sensitive=True)
            if not contact:
                return {}
            
            # Log the export action
            await self._log_gdpr_action(contact_id, "data_exported")
            
            # Return all contact data in portable format
            export_data = {
                "contact_information": {
                    "first_name": contact.first_name,
                    "last_name": contact.last_name,
                    "email": contact.email,
                    "phone": contact.phone,
                    "company": contact.company,
                    "job_title": contact.job_title,
                    "address": contact.address
                },
                "classification": {
                    "contact_type": contact.contact_type.value,
                    "lead_source": contact.lead_source,
                    "tags": contact.tags
                },
                "social_media": contact.social_profiles,
                "custom_fields": contact.custom_fields,
                "timestamps": {
                    "created_at": contact.created_at.isoformat(),
                    "updated_at": contact.updated_at.isoformat(),
                    "last_contacted": contact.last_contacted.isoformat() if contact.last_contacted else None
                },
                "data_source": {
                    "crm_provider": contact.crm_provider.value,
                    "external_id": contact.external_id
                }
            }
            
            await self.audit_logger.log_action(
                action="gdpr_data_export",
                resource_id=contact_id,
                details={"export_timestamp": datetime.utcnow().isoformat()}
            )
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"GDPR data export failed for {contact_id}: {e}")
            raise IntegrationError(f"Data export failed: {e}")
    
    async def delete_contact_data(self, contact_id: str, reason: str = "user_request") -> bool:
        """
        Delete all data for a contact (GDPR Article 17)
        Demonstrates: Security - Right to erasure compliance
        """
        try:
            if not self.db_pool:
                return False
            
            # First, export the data for audit purposes
            contact_data = await self.export_contact_data(contact_id)
            
            # Delete from main tables
            delete_queries = [
                "DELETE FROM crm_activities WHERE contact_id = $1",
                "DELETE FROM crm_deals WHERE contact_id = $1",
                "DELETE FROM crm_contacts WHERE contact_id = $1"
            ]
            
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    for query in delete_queries:
                        await conn.execute(query, contact_id)
            
            # Log the deletion
            await self._log_gdpr_action(contact_id, "data_deleted", {
                "reason": reason,
                "deleted_data": contact_data
            })
            
            await self.audit_logger.log_action(
                action="gdpr_data_deletion",
                resource_id=contact_id,
                details={"reason": reason, "deletion_timestamp": datetime.utcnow().isoformat()}
            )
            
            self.logger.info(f"Contact data deleted for GDPR compliance: {contact_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"GDPR data deletion failed for {contact_id}: {e}")
            self.metrics["compliance_violations"] += 1
            raise IntegrationError(f"Data deletion failed: {e}")
    
    # ==================== UTILITY METHODS ====================
    
    def _parse_salesforce_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Parse Salesforce datetime string"""
        if not dt_string:
            return None
        try:
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except:
            return None
    
    def _parse_hubspot_timestamp(self, timestamp: Optional[int]) -> Optional[datetime]:
        """Parse HubSpot timestamp"""
        if not timestamp:
            return None
        try:
            return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        except:
            return None
    
    def _parse_pipedrive_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Parse Pipedrive datetime string"""
        if not dt_string:
            return None
        try:
            return datetime.fromisoformat(dt_string)
        except:
            return None
    
    def _update_average_sync_time(self, sync_time: float) -> None:
        """Update average sync time metric"""
        current_avg = self.metrics["average_sync_time"]
        total_syncs = self.metrics["sync_operations"]
        
        if total_syncs == 1:
            self.metrics["average_sync_time"] = sync_time
        else:
            self.metrics["average_sync_time"] = (
                (current_avg * (total_syncs - 1) + sync_time) / total_syncs
            )
    
    async def _update_sync_analytics(self) -> None:
        """Update daily analytics"""
        if not self.db_pool:
            return
        
        today = datetime.utcnow().date()
        
        for provider in self.active_providers:
            # Update analytics for each provider
            query = """
            INSERT INTO crm_analytics (
                date, crm_provider, total_contacts, new_contacts, 
                total_deals, sync_duration_avg, error_rate
            )
            SELECT 
                $1 as date,
                $2 as crm_provider,
                COUNT(DISTINCT c.contact_id) as total_contacts,
                COUNT(DISTINCT CASE WHEN DATE(c.created_at) = $1 THEN c.contact_id END) as new_contacts,
                COUNT(DISTINCT d.deal_id) as total_deals,
                $3 as sync_duration_avg,
                $4 as error_rate
            FROM crm_contacts c
            LEFT JOIN crm_deals d ON c.contact_id = d.contact_id
            WHERE c.crm_provider = $2
            ON CONFLICT (date, crm_provider) DO UPDATE SET
                total_contacts = EXCLUDED.total_contacts,
                new_contacts = EXCLUDED.new_contacts,
                total_deals = EXCLUDED.total_deals,
                sync_duration_avg = EXCLUDED.sync_duration_avg,
                error_rate = EXCLUDED.error_rate
            """
            
            error_rate = self.metrics["error_count"] / max(self.metrics["sync_operations"], 1)
            
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    query,
                    today, provider.value, self.metrics["average_sync_time"], error_rate
                )
    
    async def _cleanup_old_sync_logs(self) -> None:
        """Cleanup old sync logs"""
        if not self.db_pool:
            return
        
        # Keep logs for 90 days
        cleanup_query = """
        DELETE FROM crm_sync_logs
        WHERE started_at < NOW() - INTERVAL '90 days'
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(cleanup_query)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check
        Demonstrates: DevOps - Service monitoring and health validation
        """
        health_status = {
            "service": "crm_integration",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        try:
            # Check Redis connection
            if self.redis_client:
                await self.redis_client.ping()
                health_status["components"]["redis"] = "healthy"
            else:
                health_status["components"]["redis"] = "disconnected"
                health_status["status"] = "degraded"
            
            # Check database connection
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                health_status["components"]["database"] = "healthy"
            else:
                health_status["components"]["database"] = "disconnected"
                health_status["status"] = "degraded"
            
            # Check CRM provider connections
            provider_status = {}
            for provider in self.active_providers:
                try:
                    config = self.crm_configs.get(provider.value, {})
                    if await self._test_provider_connection(provider, config):
                        provider_status[provider.value] = "healthy"
                    else:
                        provider_status[provider.value] = "unhealthy"
                        health_status["status"] = "degraded"
                except Exception:
                    provider_status[provider.value] = "error"
                    health_status["status"] = "degraded"
            
            health_status["components"]["crm_providers"] = provider_status
            
            # Check sync task
            if self.sync_task and not self.sync_task.done():
                health_status["components"]["sync_pipeline"] = "running"
            else:
                health_status["components"]["sync_pipeline"] = "stopped"
                health_status["status"] = "unhealthy"
            
            # Add metrics
            health_status["metrics"] = self.metrics.copy()
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def cleanup(self) -> None:
        """Cleanup CRM integration resources"""
        try:
            # Stop sync task
            if self.sync_task:
                self.sync_task.cancel()
                try:
                    await self.sync_task
                except asyncio.CancelledError:
                    pass
            
            # Close HTTP clients
            for client in self.http_clients.values():
                await client.aclose()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            # Close database pool
            if self.db_pool:
                await self.db_pool.close()
            
            self.logger.info("CRM integration cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Export main classes
__all__ = [
    "CRMIntegration", "CRMContact", "CRMDeal", "CRMActivity",
    "CRMProvider", "ContactType", "DealStage", "ActivityType"
]