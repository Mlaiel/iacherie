"""
Regulatory Monitor - Advanced Regulatory Compliance Monitoring System

Real-time monitoring of regulatory changes, policy updates, and compliance requirements
across multiple jurisdictions and frameworks.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code and intellectual property belong exclusively to Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple, Union
import json
import re
from pathlib import Path

import aiofiles
import httpx
import feedparser
import redis
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup

from ...core.config import settings
from ...core.database import get_db_session
from ...core.exceptions import ComplianceError, ValidationError
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...integrations.legal_apis import LegalAPIClient

logger = logging.getLogger(__name__)

class PolicyUpdateType(Enum):
    """Types of policy updates"""
    NEW_REGULATION = "new_regulation"
    AMENDMENT = "amendment"
    ENFORCEMENT_CHANGE = "enforcement_change"
    GUIDANCE_UPDATE = "guidance_update"
    DEADLINE_CHANGE = "deadline_change"
    REVOCATION = "revocation"

class PolicyPriority(Enum):
    """Priority levels for policy updates"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class JurisdictionScope(Enum):
    """Jurisdictional scope of regulations"""
    GLOBAL = "global"
    REGIONAL = "regional"
    NATIONAL = "national"
    STATE = "state"
    LOCAL = "local"

@dataclass
class RegulatorySource:
    """Regulatory information source configuration"""
    id: str
    name: str
    url: str
    source_type: str  # rss, api, scraper, webhook
    jurisdiction: JurisdictionScope
    frameworks: List[str]
    update_frequency: int  # minutes
    last_check: Optional[datetime] = None
    is_active: bool = True
    credentials: Optional[Dict[str, str]] = None
    parser_config: Optional[Dict[str, Any]] = None

@dataclass
class PolicyUpdate:
    """Regulatory policy update record"""
    id: str
    source_id: str
    title: str
    description: str
    update_type: PolicyUpdateType
    priority: PolicyPriority
    jurisdiction: JurisdictionScope
    affected_frameworks: List[str]
    effective_date: Optional[datetime]
    compliance_deadline: Optional[datetime]
    published_date: datetime
    source_url: str
    full_text: Optional[str] = None
    impact_analysis: Optional[Dict[str, Any]] = None
    action_required: bool = False
    stakeholders_notified: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ComplianceAlert:
    """Compliance alert for policy changes"""
    id: str
    policy_update_id: str
    alert_type: str
    severity: PolicyPriority
    message: str
    affected_entities: List[str]
    required_actions: List[str]
    deadline: Optional[datetime]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

class RegulatoryMonitor:
    """
    Advanced regulatory monitoring system for compliance automation
    
    Monitors regulatory sources, tracks policy changes, analyzes impact,
    and generates compliance alerts for proactive compliance management.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize regulatory monitor with comprehensive source management"""
        self.config = config or {}
        self.encryption = ContentEncryption()
        self.performance_monitor = PerformanceMonitor()
        self.legal_api_client = LegalAPIClient()
        
        # Core components
        self.sources: Dict[str, RegulatorySource] = {}
        self.policy_updates: Dict[str, PolicyUpdate] = {}
        self.compliance_alerts: Dict[str, ComplianceAlert] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Redis for caching and real-time updates
        try:
            self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
        
        # HTTP client for API requests
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={'User-Agent': 'IA-Influencer-Agent-ComplianceBot/2.0'}
        )
        
        # Initialize regulatory sources
        asyncio.create_task(self.initialize_regulatory_sources())
        
        logger.info("RegulatoryMonitor initialized successfully")
    
    async def initialize_regulatory_sources(self):
        """Initialize comprehensive regulatory monitoring sources"""
        try:
            # GDPR Sources
            gdpr_sources = [
                RegulatorySource(
                    id="eu_gdpr_official",
                    name="EU GDPR Official Updates",
                    url="https://edpb.europa.eu/news_en",
                    source_type="rss",
                    jurisdiction=JurisdictionScope.REGIONAL,
                    frameworks=["gdpr"],
                    update_frequency=60,  # Check hourly
                    parser_config={"content_selector": ".news-item"}
                ),
                RegulatorySource(
                    id="gdpr_info_portal",
                    name="GDPR.eu Information Portal",
                    url="https://gdpr.eu/news/",
                    source_type="scraper",
                    jurisdiction=JurisdictionScope.REGIONAL,
                    frameworks=["gdpr"],
                    update_frequency=360,  # Check every 6 hours
                    parser_config={"article_selector": ".news-article"}
                )
            ]
            
            # DMCA Sources
            dmca_sources = [
                RegulatorySource(
                    id="us_copyright_office",
                    name="US Copyright Office",
                    url="https://www.copyright.gov/newsnet/",
                    source_type="rss",
                    jurisdiction=JurisdictionScope.NATIONAL,
                    frameworks=["dmca"],
                    update_frequency=720,  # Check twice daily
                    parser_config={"feed_format": "rss2"}
                )
            ]
            
            # Platform Policy Sources
            platform_sources = [
                RegulatorySource(
                    id="youtube_policy_updates",
                    name="YouTube Creator Policy Updates",
                    url="https://support.google.com/youtube/community",
                    source_type="api",
                    jurisdiction=JurisdictionScope.GLOBAL,
                    frameworks=["youtube_policy"],
                    update_frequency=1440,  # Daily check
                    parser_config={"api_endpoint": "/policy-updates"}
                ),
                RegulatorySource(
                    id="spotify_developer_policy",
                    name="Spotify Developer Policy",
                    url="https://developer.spotify.com/policy/",
                    source_type="scraper",
                    jurisdiction=JurisdictionScope.GLOBAL,
                    frameworks=["spotify_policy"],
                    update_frequency=1440,  # Daily check
                    parser_config={"policy_selector": ".policy-content"}
                )
            ]
            
            # Data Protection Authorities
            dpa_sources = [
                RegulatorySource(
                    id="ico_uk_updates",
                    name="UK ICO Regulatory Updates",
                    url="https://ico.org.uk/about-the-ico/news-and-events/news-and-blogs/",
                    source_type="rss",
                    jurisdiction=JurisdictionScope.NATIONAL,
                    frameworks=["gdpr", "uk_dpa"],
                    update_frequency=720,  # Twice daily
                    parser_config={"category_filter": "regulatory-action"}
                ),
                RegulatorySource(
                    id="cnil_france_updates", 
                    name="CNIL France Updates",
                    url="https://www.cnil.fr/fr/actualites",
                    source_type="scraper",
                    jurisdiction=JurisdictionScope.NATIONAL,
                    frameworks=["gdpr"],
                    update_frequency=720,
                    parser_config={"language": "fr", "auto_translate": True}
                )
            ]
            
            # Industry-Specific Sources
            industry_sources = [
                RegulatorySource(
                    id="music_industry_compliance",
                    name="Music Industry Compliance Updates",
                    url="https://www.riaa.com/news/",
                    source_type="rss",
                    jurisdiction=JurisdictionScope.GLOBAL,
                    frameworks=["dmca", "music_licensing"],
                    update_frequency=1440,
                    parser_config={"category_filter": "policy"}
                ),
                RegulatorySource(
                    id="social_media_policy_tracker",
                    name="Social Media Policy Tracker",
                    url="https://www.socialmediapolicytracker.com/feed/",
                    source_type="rss",
                    jurisdiction=JurisdictionScope.GLOBAL,
                    frameworks=["platform_policies"],
                    update_frequency=720,
                    parser_config={"multi_platform": True}
                )
            ]
            
            # Register all sources
            all_sources = gdpr_sources + dmca_sources + platform_sources + dpa_sources + industry_sources
            
            for source in all_sources:
                self.sources[source.id] = source
                # Start monitoring task for active sources
                if source.is_active:
                    task = asyncio.create_task(self._monitor_source(source))
                    self.monitoring_tasks[source.id] = task
            
            logger.info(f"Initialized {len(all_sources)} regulatory sources")
            
        except Exception as e:
            logger.error(f"Failed to initialize regulatory sources: {e}")
            raise ComplianceError(f"Source initialization failed: {e}")
    
    async def _monitor_source(self, source: RegulatorySource):
        """Continuously monitor a regulatory source for updates"""
        while source.is_active:
            try:
                logger.debug(f"Checking regulatory source: {source.name}")
                
                updates = await self._fetch_source_updates(source)
                
                for update in updates:
                    await self._process_policy_update(update)
                
                # Update last check time
                source.last_check = datetime.now(timezone.utc)
                
                # Cache source status
                if self.redis_client:
                    await self._cache_source_status(source)
                
                # Wait for next check interval
                await asyncio.sleep(source.update_frequency * 60)
                
            except Exception as e:
                logger.error(f"Error monitoring source {source.id}: {e}")
                # Wait before retry to avoid spam
                await asyncio.sleep(300)  # 5 minute retry delay
    
    async def _fetch_source_updates(self, source: RegulatorySource) -> List[PolicyUpdate]:
        """Fetch updates from a regulatory source"""
        try:
            updates = []
            
            if source.source_type == "rss":
                updates = await self._fetch_rss_updates(source)
            elif source.source_type == "api":
                updates = await self._fetch_api_updates(source)
            elif source.source_type == "scraper":
                updates = await self._fetch_scraper_updates(source)
            elif source.source_type == "webhook":
                # Webhook updates are handled separately
                updates = await self._get_webhook_updates(source)
            
            # Filter for new updates only
            new_updates = []
            for update in updates:
                if not await self._is_duplicate_update(update):
                    new_updates.append(update)
            
            return new_updates
            
        except Exception as e:
            logger.error(f"Failed to fetch updates from {source.id}: {e}")
            return []
    
    async def _fetch_rss_updates(self, source: RegulatorySource) -> List[PolicyUpdate]:
        """Fetch updates from RSS feeds"""
        try:
            response = await self.http_client.get(source.url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            updates = []
            
            for entry in feed.entries[:10]:  # Limit to latest 10 entries
                # Parse entry data
                title = entry.get('title', 'Unknown Title')
                description = entry.get('summary', entry.get('description', ''))
                link = entry.get('link', source.url)
                published_str = entry.get('published', entry.get('updated', ''))
                
                # Parse publication date
                try:
                    if published_str:
                        published_date = datetime.fromtimestamp(
                            time.mktime(entry.published_parsed), timezone.utc
                        )
                    else:
                        published_date = datetime.now(timezone.utc)
                except:
                    published_date = datetime.now(timezone.utc)
                
                # Skip old entries (older than 30 days)
                if (datetime.now(timezone.utc) - published_date).days > 30:
                    continue
                
                # Analyze update content
                update_analysis = await self._analyze_update_content(title, description)
                
                update = PolicyUpdate(
                    id=str(uuid.uuid4()),
                    source_id=source.id,
                    title=title,
                    description=description,
                    update_type=update_analysis['update_type'],
                    priority=update_analysis['priority'],
                    jurisdiction=source.jurisdiction,
                    affected_frameworks=source.frameworks,
                    published_date=published_date,
                    source_url=link,
                    effective_date=update_analysis.get('effective_date'),
                    compliance_deadline=update_analysis.get('compliance_deadline'),
                    impact_analysis=update_analysis,
                    action_required=update_analysis.get('action_required', False)
                )
                
                updates.append(update)
            
            return updates
            
        except Exception as e:
            logger.error(f"RSS fetch error for {source.id}: {e}")
            return []
    
    async def _fetch_api_updates(self, source: RegulatorySource) -> List[PolicyUpdate]:
        """Fetch updates from API endpoints"""
        try:
            headers = {}
            if source.credentials:
                # Add authentication headers
                if 'api_key' in source.credentials:
                    headers['X-API-Key'] = source.credentials['api_key']
                elif 'bearer_token' in source.credentials:
                    headers['Authorization'] = f"Bearer {source.credentials['bearer_token']}"
            
            response = await self.http_client.get(source.url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            updates = []
            
            # Process API response based on source configuration
            items = data.get('items', data.get('updates', data.get('results', [])))
            
            for item in items[:10]:  # Limit to latest 10
                title = item.get('title', item.get('name', 'API Update'))
                description = item.get('description', item.get('summary', ''))
                published_str = item.get('published_at', item.get('created_at', ''))
                
                # Parse dates
                try:
                    published_date = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                except:
                    published_date = datetime.now(timezone.utc)
                
                # Skip old updates
                if (datetime.now(timezone.utc) - published_date).days > 30:
                    continue
                
                update_analysis = await self._analyze_update_content(title, description)
                
                update = PolicyUpdate(
                    id=str(uuid.uuid4()),
                    source_id=source.id,
                    title=title,
                    description=description,
                    update_type=update_analysis['update_type'],
                    priority=update_analysis['priority'],
                    jurisdiction=source.jurisdiction,
                    affected_frameworks=source.frameworks,
                    published_date=published_date,
                    source_url=item.get('url', source.url),
                    full_text=item.get('content', item.get('full_text')),
                    impact_analysis=update_analysis,
                    action_required=update_analysis.get('action_required', False)
                )
                
                updates.append(update)
            
            return updates
            
        except Exception as e:
            logger.error(f"API fetch error for {source.id}: {e}")
            return []
    
    async def _fetch_scraper_updates(self, source: RegulatorySource) -> List[PolicyUpdate]:
        """Fetch updates by scraping web pages"""
        try:
            response = await self.http_client.get(source.url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            updates = []
            
            # Use parser configuration for scraping
            config = source.parser_config or {}
            selector = config.get('content_selector', '.news-item')
            
            items = soup.select(selector)[:10]  # Limit to 10 items
            
            for item in items:
                # Extract title
                title_elem = item.find(['h1', 'h2', 'h3', 'h4']) or item.find('a')
                title = title_elem.get_text(strip=True) if title_elem else 'Scraped Update'
                
                # Extract description
                desc_elem = item.find('p') or item
                description = desc_elem.get_text(strip=True)[:500] if desc_elem else ''
                
                # Extract link
                link_elem = item.find('a')
                link = link_elem.get('href', source.url) if link_elem else source.url
                if link.startswith('/'):
                    from urllib.parse import urljoin
                    link = urljoin(source.url, link)
                
                # Try to extract date
                date_elem = item.find(['time', '.date', '.published'])
                published_date = datetime.now(timezone.utc)
                if date_elem:
                    date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                    try:
                        published_date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                    except:
                        pass
                
                # Skip old content
                if (datetime.now(timezone.utc) - published_date).days > 30:
                    continue
                
                update_analysis = await self._analyze_update_content(title, description)
                
                update = PolicyUpdate(
                    id=str(uuid.uuid4()),
                    source_id=source.id,
                    title=title,
                    description=description,
                    update_type=update_analysis['update_type'],
                    priority=update_analysis['priority'],
                    jurisdiction=source.jurisdiction,
                    affected_frameworks=source.frameworks,
                    published_date=published_date,
                    source_url=link,
                    impact_analysis=update_analysis,
                    action_required=update_analysis.get('action_required', False)
                )
                
                updates.append(update)
            
            return updates
            
        except Exception as e:
            logger.error(f"Scraper error for {source.id}: {e}")
            return []
    
    async def _analyze_update_content(self, title: str, description: str) -> Dict[str, Any]:
        """Analyze policy update content to determine type, priority, and impact"""
        content = (title + " " + description).lower()
        
        analysis = {
            'update_type': PolicyUpdateType.GUIDANCE_UPDATE,
            'priority': PolicyPriority.LOW,
            'action_required': False,
            'keywords_found': [],
            'effective_date': None,
            'compliance_deadline': None
        }
        
        # Critical keywords that indicate high priority
        critical_keywords = [
            'emergency', 'urgent', 'immediate', 'critical', 'mandatory',
            'violation', 'penalty', 'fine', 'enforcement action',
            'cease and desist', 'takedown', 'suspension'
        ]
        
        high_priority_keywords = [
            'new regulation', 'amendment', 'deadline', 'compliance',
            'required', 'must', 'shall', 'obligatory',
            'data breach', 'security incident', 'privacy violation'
        ]
        
        medium_priority_keywords = [
            'guidance', 'recommendation', 'best practice', 'update',
            'clarification', 'interpretation', 'policy change'
        ]
        
        # Update type indicators
        type_indicators = {
            PolicyUpdateType.NEW_REGULATION: ['new regulation', 'new law', 'new rule', 'introduces'],
            PolicyUpdateType.AMENDMENT: ['amendment', 'amends', 'modifies', 'changes to'],
            PolicyUpdateType.ENFORCEMENT_CHANGE: ['enforcement', 'penalty', 'fine', 'sanctions'],
            PolicyUpdateType.DEADLINE_CHANGE: ['deadline', 'extended', 'postponed', 'due date'],
            PolicyUpdateType.REVOCATION: ['revokes', 'cancels', 'withdraws', 'repeals']
        }
        
        # Analyze priority
        found_keywords = []
        
        for keyword in critical_keywords:
            if keyword in content:
                analysis['priority'] = PolicyPriority.CRITICAL
                analysis['action_required'] = True
                found_keywords.append(keyword)
        
        if analysis['priority'] != PolicyPriority.CRITICAL:
            for keyword in high_priority_keywords:
                if keyword in content:
                    analysis['priority'] = PolicyPriority.HIGH
                    analysis['action_required'] = True
                    found_keywords.append(keyword)
                    break
        
        if analysis['priority'] not in [PolicyPriority.CRITICAL, PolicyPriority.HIGH]:
            for keyword in medium_priority_keywords:
                if keyword in content:
                    analysis['priority'] = PolicyPriority.MEDIUM
                    found_keywords.append(keyword)
                    break
        
        # Analyze update type
        for update_type, indicators in type_indicators.items():
            for indicator in indicators:
                if indicator in content:
                    analysis['update_type'] = update_type
                    break
        
        # Try to extract dates
        date_patterns = [
            r'effective (?:date |on |from )?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'deadline (?:of |is |on )?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'by (\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2} (?:january|february|march|april|may|june|july|august|september|october|november|december) \d{4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    # Simple date parsing (would need more robust parsing in production)
                    date_str = matches[0]
                    if 'effective' in pattern:
                        analysis['effective_date'] = datetime.now(timezone.utc) + timedelta(days=30)
                    elif 'deadline' in pattern or 'by' in pattern:
                        analysis['compliance_deadline'] = datetime.now(timezone.utc) + timedelta(days=60)
                except:
                    pass
        
        analysis['keywords_found'] = found_keywords
        return analysis
    
    async def _process_policy_update(self, update: PolicyUpdate):
        """Process and store a policy update"""
        try:
            # Store the update
            self.policy_updates[update.id] = update
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_policy_update(update)
            
            # Generate compliance alert if action required
            if update.action_required or update.priority in [PolicyPriority.HIGH, PolicyPriority.CRITICAL]:
                alert = await self._generate_compliance_alert(update)
                self.compliance_alerts[alert.id] = alert
                
                # Send notifications
                await self._send_policy_alert_notifications(alert)
            
            # Log the policy update
            logger.info(f"Processed policy update: {update.title} (Priority: {update.priority.value})")
            
        except Exception as e:
            logger.error(f"Error processing policy update {update.id}: {e}")
    
    async def _generate_compliance_alert(self, update: PolicyUpdate) -> ComplianceAlert:
        """Generate compliance alert for policy update"""
        alert_id = str(uuid.uuid4())
        
        # Determine affected entities (this would be more sophisticated in production)
        affected_entities = []
        if 'gdpr' in update.affected_frameworks:
            affected_entities.extend(['user_data', 'privacy_policies', 'consent_management'])
        if 'dmca' in update.affected_frameworks:
            affected_entities.extend(['content_management', 'takedown_processes'])
        if any('policy' in framework for framework in update.affected_frameworks):
            affected_entities.extend(['content_moderation', 'platform_compliance'])
        
        # Generate required actions based on update type and priority
        required_actions = []
        
        if update.update_type == PolicyUpdateType.NEW_REGULATION:
            required_actions.extend([
                "Review new regulation requirements",
                "Assess impact on current processes",
                "Update compliance procedures",
                "Train relevant teams"
            ])
        elif update.update_type == PolicyUpdateType.AMENDMENT:
            required_actions.extend([
                "Review amendment details", 
                "Update existing procedures",
                "Communicate changes to stakeholders"
            ])
        elif update.update_type == PolicyUpdateType.ENFORCEMENT_CHANGE:
            required_actions.extend([
                "Review enforcement changes",
                "Update violation handling procedures",
                "Assess penalty implications"
            ])
        
        # Set deadline based on priority and effective date
        deadline = update.compliance_deadline
        if not deadline:
            if update.priority == PolicyPriority.CRITICAL:
                deadline = datetime.now(timezone.utc) + timedelta(days=7)
            elif update.priority == PolicyPriority.HIGH:
                deadline = datetime.now(timezone.utc) + timedelta(days=30)
            else:
                deadline = datetime.now(timezone.utc) + timedelta(days=60)
        
        alert = ComplianceAlert(
            id=alert_id,
            policy_update_id=update.id,
            alert_type=f"{update.priority.value}_policy_update",
            severity=update.priority,
            message=f"Policy Update Alert: {update.title}",
            affected_entities=affected_entities,
            required_actions=required_actions,
            deadline=deadline
        )
        
        return alert
    
    async def _is_duplicate_update(self, update: PolicyUpdate) -> bool:
        """Check if update is a duplicate"""
        # Simple duplicate detection based on title similarity
        for existing_id, existing_update in self.policy_updates.items():
            if existing_update.source_id == update.source_id:
                # Check title similarity
                title_similarity = self._calculate_similarity(
                    update.title.lower(), existing_update.title.lower()
                )
                if title_similarity > 0.8:  # 80% similarity threshold
                    return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simple implementation)"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _cache_source_status(self, source: RegulatorySource):
        """Cache source status in Redis"""
        if not self.redis_client:
            return
        
        try:
            cache_data = {
                'id': source.id,
                'name': source.name,
                'last_check': source.last_check.isoformat() if source.last_check else None,
                'is_active': source.is_active,
                'update_frequency': source.update_frequency
            }
            
            key = f"regulatory_source:{source.id}"
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.setex, key, 3600, json.dumps(cache_data)
            )
        except Exception as e:
            logger.warning(f"Failed to cache source status: {e}")
    
    async def _cache_policy_update(self, update: PolicyUpdate):
        """Cache policy update in Redis"""
        if not self.redis_client:
            return
        
        try:
            cache_data = {
                'id': update.id,
                'title': update.title,
                'priority': update.priority.value,
                'frameworks': update.affected_frameworks,
                'published_date': update.published_date.isoformat(),
                'action_required': update.action_required
            }
            
            key = f"policy_update:{update.id}"
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.setex, key, 86400, json.dumps(cache_data)  # 24 hours
            )
        except Exception as e:
            logger.warning(f"Failed to cache policy update: {e}")
    
    async def _send_policy_alert_notifications(self, alert: ComplianceAlert):
        """Send notifications for compliance alerts"""
        try:
            # This would integrate with notification systems (email, Slack, Teams, etc.)
            logger.info(f"Sending policy alert notifications for: {alert.message}")
            
            # Example notification logic (would be implemented with actual services)
            notification_data = {
                'alert_id': alert.id,
                'severity': alert.severity.value,
                'message': alert.message,
                'affected_entities': alert.affected_entities,
                'deadline': alert.deadline.isoformat() if alert.deadline else None
            }
            
            # Cache notification for external services to pick up
            if self.redis_client:
                key = f"policy_alert_notification:{alert.id}"
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.setex, key, 3600, json.dumps(notification_data)
                )
            
        except Exception as e:
            logger.error(f"Failed to send policy alert notifications: {e}")
    
    async def get_recent_updates(self, frameworks: Optional[List[str]] = None,
                               priority: Optional[PolicyPriority] = None,
                               days: int = 7) -> List[PolicyUpdate]:
        """Get recent policy updates with optional filtering"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            filtered_updates = []
            
            for update in self.policy_updates.values():
                # Filter by date
                if update.published_date < cutoff_date:
                    continue
                
                # Filter by frameworks
                if frameworks:
                    if not any(fw in update.affected_frameworks for fw in frameworks):
                        continue
                
                # Filter by priority
                if priority and update.priority != priority:
                    continue
                
                filtered_updates.append(update)
            
            # Sort by priority and date
            priority_order = {
                PolicyPriority.EMERGENCY: 0,
                PolicyPriority.CRITICAL: 1,
                PolicyPriority.HIGH: 2,
                PolicyPriority.MEDIUM: 3,
                PolicyPriority.LOW: 4
            }
            
            filtered_updates.sort(
                key=lambda u: (priority_order.get(u.priority, 5), u.published_date),
                reverse=True
            )
            
            return filtered_updates
            
        except Exception as e:
            logger.error(f"Error getting recent updates: {e}")
            return []
    
    async def get_active_alerts(self, acknowledged: bool = False) -> List[ComplianceAlert]:
        """Get active compliance alerts"""
        try:
            active_alerts = []
            
            for alert in self.compliance_alerts.values():
                if alert.acknowledged == acknowledged:
                    active_alerts.append(alert)
            
            # Sort by severity and creation date
            severity_order = {
                PolicyPriority.EMERGENCY: 0,
                PolicyPriority.CRITICAL: 1,
                PolicyPriority.HIGH: 2,
                PolicyPriority.MEDIUM: 3,
                PolicyPriority.LOW: 4
            }
            
            active_alerts.sort(
                key=lambda a: (severity_order.get(a.severity, 5), a.created_at),
                reverse=True
            )
            
            return active_alerts
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge a compliance alert"""
        try:
            alert = self.compliance_alerts.get(alert_id)
            if not alert:
                return False
            
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now(timezone.utc)
            
            # Update cache
            if self.redis_client:
                cache_data = {
                    'acknowledged': True,
                    'acknowledged_by': acknowledged_by,
                    'acknowledged_at': alert.acknowledged_at.isoformat()
                }
                key = f"compliance_alert:{alert_id}"
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.hset, key, 'acknowledgment', json.dumps(cache_data)
                )
            
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False
    
    async def add_custom_source(self, source: RegulatorySource) -> bool:
        """Add a custom regulatory source"""
        try:
            self.sources[source.id] = source
            
            # Start monitoring if active
            if source.is_active:
                task = asyncio.create_task(self._monitor_source(source))
                self.monitoring_tasks[source.id] = task
            
            logger.info(f"Added custom regulatory source: {source.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding custom source: {e}")
            return False
    
    async def stop_monitoring(self):
        """Stop all monitoring tasks"""
        for task_id, task in self.monitoring_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.monitoring_tasks.clear()
        await self.http_client.aclose()
        
        logger.info("Regulatory monitoring stopped")


class PolicyTracker:
    """
    Advanced policy change tracking and analysis system
    """
    
    def __init__(self, regulatory_monitor: RegulatoryMonitor):
        self.monitor = regulatory_monitor
        self.policy_history: Dict[str, List[PolicyUpdate]] = {}
        self.trend_analysis_cache: Dict[str, Any] = {}
    
    async def track_policy_changes(self, framework: str, lookback_days: int = 90) -> Dict[str, Any]:
        """Track and analyze policy changes for a specific framework"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)
            
            # Get relevant updates
            updates = []
            for update in self.monitor.policy_updates.values():
                if framework in update.affected_frameworks and update.published_date >= cutoff_date:
                    updates.append(update)
            
            # Analyze trends
            analysis = {
                'total_updates': len(updates),
                'update_frequency': len(updates) / (lookback_days / 30),  # Updates per month
                'priority_breakdown': {},
                'update_types': {},
                'compliance_impact': 'low',
                'trend_direction': 'stable',
                'recommendations': []
            }
            
            # Analyze by priority
            for update in updates:
                priority = update.priority.value
                analysis['priority_breakdown'][priority] = analysis['priority_breakdown'].get(priority, 0) + 1
                
                update_type = update.update_type.value
                analysis['update_types'][update_type] = analysis['update_types'].get(update_type, 0) + 1
            
            # Determine compliance impact
            high_priority_count = analysis['priority_breakdown'].get('high', 0) + \
                                analysis['priority_breakdown'].get('critical', 0) + \
                                analysis['priority_breakdown'].get('emergency', 0)
            
            if high_priority_count > 3:
                analysis['compliance_impact'] = 'high'
            elif high_priority_count > 1:
                analysis['compliance_impact'] = 'medium'
            
            # Generate recommendations
            if analysis['update_frequency'] > 2:
                analysis['recommendations'].append(
                    "High frequency of policy changes detected - consider dedicated monitoring"
                )
            
            if high_priority_count > 0:
                analysis['recommendations'].append(
                    "Critical policy updates require immediate attention and review"
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error tracking policy changes for {framework}: {e}")
            return {'error': str(e)}
