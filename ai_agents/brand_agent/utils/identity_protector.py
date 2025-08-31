"""Identity Protector - Advanced Brand Identity & Trademark Protection System

Comprehensive identity protection including trademark monitoring, domain protection,
and anti-counterfeiting measures for content creators and brands.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
import hashlib
import whois
import dns.resolver
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import json
import tldextract

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
from ...utils.legal_database import TrademarkDatabase, LegalDocumentGenerator
from ...utils.domain_monitor import DomainMonitor, WhoisChecker
from ...utils.image_analysis import LogoAnalyzer, VisualIdentityChecker
from ...utils.notification_service import NotificationService
from ...security.encryption import ContentEncryption

logger = logging.getLogger(__name__)

class ProtectionLevel(Enum):
    """Levels of identity protection"""    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ULTIMATE = "ultimate"

class ThreatType(Enum):
    """Types of identity threats"""    TRADEMARK_INFRINGEMENT = "trademark_infringement"
    DOMAIN_SQUATTING = "domain_squatting"
    TYPOSQUATTING = "typosquatting"
    COUNTERFEITING = "counterfeiting"
    IMPERSONATION = "impersonation"
    LOGO_MISUSE = "logo_misuse"
    BRAND_CONFUSION = "brand_confusion"
    CYBERSQUATTING = "cybersquatting"
    SOCIAL_MEDIA_HIJACKING = "social_media_hijacking"
    DEEP_FAKE_ABUSE = "deep_fake_abuse"
    AI_GENERATED_COUNTERFEITS = "ai_generated_counterfeits"

class LegalJurisdiction(Enum):
    """Legal jurisdictions for protection"""    USPTO = "uspto"  # United States
    EUIPO = "euipo"  # European Union
    WIPO = "wipo"    # World Intellectual Property Organization
    JPO = "jpo"      # Japan Patent Office
    CNIPA = "cnipa"  # China National IP Administration
    CIPO = "cipo"    # Canadian IP Office
    IPO_UK = "ipo_uk"  # UK Intellectual Property Office
    INPI_FRANCE = "inpi_france"  # France
    DPMA = "dpma"    # Germany
    MULTIPLE = "multiple"

class ProtectionStatus(Enum):
    """Status of protection measures"""    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    REJECTED = "rejected"
    DISPUTED = "disputed"
    RENEWAL_REQUIRED = "renewal_required"
    ENFORCEMENT_NEEDED = "enforcement_needed"

@dataclass
class TrademarkProtection:
    """Trademark protection registration"""    trademark_id: str
    brand_name: str
    trademark_text: str
    jurisdiction: LegalJurisdiction
    registration_number: Optional[str] = None
    filing_date: Optional[datetime] = None
    registration_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    status: ProtectionStatus = ProtectionStatus.PENDING
    classes: List[str] = field(default_factory=list)
    description: str = ""
    attorney_info: Dict[str, str] = field(default_factory=dict)
    renewal_alerts: List[datetime] = field(default_factory=list)
    enforcement_history: List[Dict[str, Any]] = field(default_factory=list)
    maintenance_costs: float = 0.0

@dataclass
class DomainProtection:
    """Domain protection and monitoring"""    domain_id: str
    primary_domain: str
    protected_variations: List[str] = field(default_factory=list)
    registered_domains: List[str] = field(default_factory=list)
    monitored_extensions: List[str] = field(default_factory=list)
    threat_domains: List[Dict[str, Any]] = field(default_factory=list)
    whois_monitoring: bool = True
    auto_renewal: bool = True
    dns_monitoring: bool = True
    ssl_monitoring: bool = True
    last_scan: Optional[datetime] = None
    protection_score: float = 0.0

@dataclass
class IdentityThreat:
    """Detected identity threat with details"""    threat_id: str
    threat_type: ThreatType
    severity_level: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    source_url: Optional[str] = None
    infringing_entity: Optional[str] = None
    similarity_score: float = 0.0
    evidence: Dict[str, Any] = field(default_factory=dict)
    legal_risk_assessment: Dict[str, Any] = field(default_factory=dict)
    recommended_actions: List[str] = field(default_factory=list)
    estimated_damages: float = 0.0
    jurisdiction: Optional[LegalJurisdiction] = None
    status: str = "detected"
    action_deadline: Optional[datetime] = None 
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class ThreatType(Enum):
    """Types of identity threats"""    TRADEMARK_INFRINGEMENT = "trademark_infringement"
    DOMAIN_SQUATTING = "domain_squatting"
    LOGO_THEFT = "logo_theft"
    BRAND_IMPERSONATION = "brand_impersonation"
    COUNTERFEITING = "counterfeiting"
    SOCIAL_MEDIA_IMPERSONATION = "social_media_impersonation"
    CYBERSQUATTING = "cybersquatting"
    TYPOSQUATTING = "typosquatting"

class ProtectionStatus(Enum):
    """Status of protection measures"""    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    VIOLATED = "violated"
    SUSPENDED = "suspended"

@dataclass
class TrademarkProtection:
    """Trademark protection record"""    protection_id: str
    brand_id: str
    trademark_name: str
    registration_number: Optional[str]
    jurisdiction: str
    protection_class: str
    status: ProtectionStatus
    registration_date: Optional[datetime]
    expiry_date: Optional[datetime]
    renewal_date: Optional[datetime]
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DomainProtection:
    """Domain protection record"""    protection_id: str
    brand_id: str
    domain_name: str
    registrar: Optional[str]
    registration_date: Optional[datetime]
    expiry_date: Optional[datetime]
    status: ProtectionStatus
    protection_type: str  # defensive, primary, monitored
    monitoring_enabled: bool = True
    auto_renewal: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    whois_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IdentityThreat:
    """Identity threat detection result"""    threat_id: str
    brand_id: str
    threat_type: ThreatType
    severity: str  # low, medium, high, critical
    confidence: float
    detected_at: datetime
    source_url: Optional[str] = None
    infringing_content: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    legal_risk: float = 0.0
    recommended_actions: List[str] = field(default_factory=list)
    status: str = "detected"  # detected, investigating, action_taken, resolved
    assigned_to: Optional[str] = None

@dataclass
class ProtectionReport:
    """Comprehensive protection status report"""    report_id: str
    brand_id: str
    protection_summary: Dict[str, Any]
    active_threats: List[IdentityThreat]
    protection_gaps: List[str]
    recommendations: List[str]
    legal_actions_needed: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)
    report_period: str = "30d"

class IdentityProtector:
    """    Advanced Brand Identity & Trademark Protection System
    
    Provides comprehensive identity protection including:
    - Trademark monitoring and protection
    - Domain name protection and monitoring
    - Logo and visual identity protection
    - Anti-counterfeiting measures
    - Legal document generation
    - Automated threat response
    """
    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        self.protection_level = ProtectionLevel.STANDARD
        
        # Initialize protection services
        self.trademark_db = TrademarkDatabase()
        self.domain_monitor = DomainMonitor()
        self.whois_checker = WhoisChecker()
        self.logo_analyzer = LogoAnalyzer()
        self.legal_generator = LegalDocumentGenerator()
        self.notification_service = NotificationService()
        self.encryption = ContentEncryption()
        
        # Protection records
        self.trademark_protections: Dict[str, TrademarkProtection] = {}
        self.domain_protections: Dict[str, DomainProtection] = {}
        self.detected_threats: List[IdentityThreat] = []
        
        # Monitoring tasks
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.monitoring_active = False
        
        logger.info(f"Identity protector initialized for brand: {brand_id}")

    async def configure_protection(self, config: Dict[str, Any]) -> None:
        """Configure identity protection parameters"""        try:
            self.protection_level = ProtectionLevel(config.get("protection_level", "standard"))
            
            # Configure trademark protections
            trademarks = config.get("trademarks", [])
            for tm_config in trademarks:
                await self._register_trademark_protection(tm_config)
            
            # Configure domain protections
            domains = config.get("domains", [])
            for domain_config in domains:
                await self._register_domain_protection(domain_config)
            
            logger.info(f"Identity protection configured: {len(trademarks)} trademarks, {len(domains)} domains")
            
        except Exception as e:
            logger.error(f"Protection configuration failed: {str(e)}")
            raise

    async def _register_trademark_protection(self, config: Dict[str, Any]) -> TrademarkProtection:
        """Register trademark for protection"""        try:
            protection_id = f"tm_{hashlib.md5(f'{self.brand_id}_{config.get(\"name\")}_{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:12]}"
            
            protection = TrademarkProtection(
                protection_id=protection_id,
                brand_id=self.brand_id,
                trademark_name=config.get("name"),
                registration_number=config.get("registration_number"),
                jurisdiction=config.get("jurisdiction", "US"),
                protection_class=config.get("protection_class", "general"),
                status=ProtectionStatus.ACTIVE,
                registration_date=config.get("registration_date"),
                expiry_date=config.get("expiry_date"),
                metadata=config.get("metadata", {})
            )
            
            self.trademark_protections[protection_id] = protection
            
            # Start monitoring if not already active
            await self._start_trademark_monitoring(protection)
            
            logger.info(f"Trademark protection registered: {config.get('name')}")
            return protection
            
        except Exception as e:
            logger.error(f"Trademark protection registration failed: {str(e)}")
            raise

    async def _register_domain_protection(self, config: Dict[str, Any]) -> DomainProtection:
        """Register domain for protection"""        try:
            domain_name = config.get("domain")
            protection_id = f"dom_{hashlib.md5(f'{self.brand_id}_{domain_name}_{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:12]}"
            
            # Get domain information
            domain_info = await self._get_domain_info(domain_name)
            
            protection = DomainProtection(
                protection_id=protection_id,
                brand_id=self.brand_id,
                domain_name=domain_name,
                registrar=domain_info.get("registrar"),
                registration_date=domain_info.get("registration_date"),
                expiry_date=domain_info.get("expiry_date"),
                status=ProtectionStatus.ACTIVE,
                protection_type=config.get("type", "primary"),
                monitoring_enabled=config.get("monitoring_enabled", True),
                auto_renewal=config.get("auto_renewal", False),
                whois_data=domain_info
            )
            
            self.domain_protections[protection_id] = protection
            
            # Start domain monitoring
            if protection.monitoring_enabled:
                await self._start_domain_monitoring(protection)
            
            logger.info(f"Domain protection registered: {domain_name}")
            return protection
            
        except Exception as e:
            logger.error(f"Domain protection registration failed: {str(e)}")
            raise

    async def _get_domain_info(self, domain_name: str) -> Dict[str, Any]:
        """Get comprehensive domain information"""        try:
            # Use whois to get domain information
            domain_info = await self.whois_checker.get_domain_info(domain_name)
            return domain_info
        except Exception as e:
            logger.error(f"Domain info retrieval failed for {domain_name}: {str(e)}")
            return {}

    async def start_monitoring(self) -> None:
        """Start comprehensive identity monitoring"""        try:
            if self.monitoring_active:
                logger.warning("Identity monitoring already active")
                return
            
            self.monitoring_active = True
            
            # Start trademark monitoring
            self.monitoring_tasks["trademark_monitor"] = asyncio.create_task(
                self._comprehensive_trademark_monitoring()
            )
            
            # Start domain monitoring
            self.monitoring_tasks["domain_monitor"] = asyncio.create_task(
                self._comprehensive_domain_monitoring()
            )
            
            # Start visual identity monitoring
            self.monitoring_tasks["visual_monitor"] = asyncio.create_task(
                self._visual_identity_monitoring()
            )
            
            # Start threat analysis
            self.monitoring_tasks["threat_analysis"] = asyncio.create_task(
                self._continuous_threat_analysis()
            )
            
            logger.info("Identity monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Identity monitoring startup failed: {str(e)}")
            self.monitoring_active = False
            raise

    async def stop_monitoring(self) -> None:
        """Stop identity monitoring"""        try:
            self.monitoring_active = False
            
            for task_name, task in self.monitoring_tasks.items():
                task.cancel()
                logger.info(f"Cancelled identity monitoring task: {task_name}")
            
            self.monitoring_tasks.clear()
            logger.info("Identity monitoring stopped")
            
        except Exception as e:
            logger.error(f"Identity monitoring stop failed: {str(e)}")

    async def _comprehensive_trademark_monitoring(self) -> None:
        """Comprehensive trademark monitoring across multiple databases"""        try:
            while self.monitoring_active:
                try:
                    for protection_id, protection in self.trademark_protections.items():
                        await self._monitor_trademark_violations(protection)
                    
                    await asyncio.sleep(3600)  # Check every hour
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Trademark monitoring cycle error: {str(e)}")
                    await asyncio.sleep(300)
                    
        except Exception as e:
            logger.error(f"Comprehensive trademark monitoring failed: {str(e)}")

    async def _monitor_trademark_violations(self, protection: TrademarkProtection) -> None:
        """Monitor for specific trademark violations"""        try:
            trademark_name = protection.trademark_name
            
            # Search trademark databases
            database_threats = await self._search_trademark_databases(trademark_name)
            
            # Search web for unauthorized usage
            web_threats = await self._search_web_trademark_usage(trademark_name)
            
            # Search marketplaces for counterfeits
            marketplace_threats = await self._search_marketplace_counterfeits(trademark_name)
            
            # Search social media for impersonation
            social_threats = await self._search_social_impersonation(trademark_name)
            
            # Process detected threats
            all_threats = database_threats + web_threats + marketplace_threats + social_threats
            for threat in all_threats:
                await self._process_identity_threat(threat)
                
        except Exception as e:
            logger.error(f"Trademark violation monitoring failed: {str(e)}")

    async def _search_trademark_databases(self, trademark_name: str) -> List[IdentityThreat]:
        """Search official trademark databases for conflicts"""        threats = []
        
        try:
            # Search USPTO database
            uspto_results = await self.trademark_db.search_uspto(trademark_name)
            
            for result in uspto_results:
                if self._is_trademark_conflict(trademark_name, result):
                    threat = IdentityThreat(
                        threat_id=f"tm_db_{hashlib.md5(result.get('serial_number', '').encode()).hexdigest()[:12]}",
                        brand_id=self.brand_id,
                        threat_type=ThreatType.TRADEMARK_INFRINGEMENT,
                        severity="high",
                        confidence=0.8,
                        detected_at=datetime.utcnow(),
                        evidence={
                            "database": "USPTO",
                            "serial_number": result.get("serial_number"),
                            "application_date": result.get("application_date"),
                            "status": result.get("status"),
                            "similarity_score": self._calculate_trademark_similarity(trademark_name, result.get("mark"))
                        }
                    )
                    threats.append(threat)
            
            # Search EUIPO database
            euipo_results = await self.trademark_db.search_euipo(trademark_name)
            
            for result in euipo_results:
                if self._is_trademark_conflict(trademark_name, result):
                    threat = IdentityThreat(
                        threat_id=f"tm_eu_{hashlib.md5(result.get('application_number', '').encode()).hexdigest()[:12]}",
                        brand_id=self.brand_id,
                        threat_type=ThreatType.TRADEMARK_INFRINGEMENT,
                        severity="medium",
                        confidence=0.7,
                        detected_at=datetime.utcnow(),
                        evidence={
                            "database": "EUIPO",
                            "application_number": result.get("application_number"),
                            "filing_date": result.get("filing_date"),
                            "status": result.get("status")
                        }
                    )
                    threats.append(threat)
                    
        except Exception as e:
            logger.error(f"Trademark database search failed: {str(e)}")
            
        return threats

    async def _search_web_trademark_usage(self, trademark_name: str) -> List[IdentityThreat]:
        """Search web for unauthorized trademark usage"""        threats = []
        
        try:
            # Search engines for trademark usage
            search_queries = [
                f'"{trademark_name}"',
                f'{trademark_name} trademark',
                f'{trademark_name} brand',
                f'{trademark_name} logo'
            ]
            
            for query in search_queries:
                search_results = await self._perform_web_search(query)
                
                for result in search_results:
                    threat_level = await self._analyze_trademark_usage(result, trademark_name)
                    
                    if threat_level > 0.6:  # Significant threat threshold
                        threat = IdentityThreat(
                            threat_id=f"web_{hashlib.md5(result.get('url', '').encode()).hexdigest()[:12]}",
                            brand_id=self.brand_id,
                            threat_type=ThreatType.TRADEMARK_INFRINGEMENT,
                            severity=self._threat_level_to_severity(threat_level),
                            confidence=threat_level,
                            detected_at=datetime.utcnow(),
                            source_url=result.get("url"),
                            evidence={
                                "title": result.get("title"),
                                "description": result.get("description"),
                                "usage_context": await self._analyze_usage_context(result)
                            }
                        )
                        threats.append(threat)
                        
        except Exception as e:
            logger.error(f"Web trademark search failed: {str(e)}")
            
        return threats

    async def _search_marketplace_counterfeits(self, trademark_name: str) -> List[IdentityThreat]:
        """Search online marketplaces for counterfeit products"""        threats = []
        
        try:
            marketplaces = ["amazon", "ebay", "alibaba", "etsy", "facebook_marketplace"]
            
            for marketplace in marketplaces:
                marketplace_results = await self._search_marketplace(marketplace, trademark_name)
                
                for product in marketplace_results:
                    counterfeit_score = await self._analyze_counterfeit_risk(product, trademark_name)
                    
                    if counterfeit_score > 0.7:
                        threat = IdentityThreat(
                            threat_id=f"market_{marketplace}_{hashlib.md5(product.get('id', '').encode()).hexdigest()[:12]}",
                            brand_id=self.brand_id,
                            threat_type=ThreatType.COUNTERFEITING,
                            severity=self._threat_level_to_severity(counterfeit_score),
                            confidence=counterfeit_score,
                            detected_at=datetime.utcnow(),
                            source_url=product.get("url"),
                            evidence={
                                "marketplace": marketplace,
                                "product_title": product.get("title"),
                                "seller": product.get("seller"),
                                "price": product.get("price"),
                                "counterfeit_indicators": product.get("counterfeit_indicators", [])
                            }
                        )
                        threats.append(threat)
                        
        except Exception as e:
            logger.error(f"Marketplace counterfeit search failed: {str(e)}")
            
        return threats

    async def _search_social_impersonation(self, trademark_name: str) -> List[IdentityThreat]:
        """Search social media for brand impersonation"""        threats = []
        
        try:
            platforms = ["instagram", "facebook", "twitter", "linkedin", "tiktok", "youtube"]
            
            for platform in platforms:
                impersonation_accounts = await self._search_platform_impersonation(platform, trademark_name)
                
                for account in impersonation_accounts:
                    impersonation_score = await self._analyze_impersonation_risk(account, trademark_name)
                    
                    if impersonation_score > 0.6:
                        threat = IdentityThreat(
                            threat_id=f"social_{platform}_{hashlib.md5(account.get('username', '').encode()).hexdigest()[:12]}",
                            brand_id=self.brand_id,
                            threat_type=ThreatType.SOCIAL_MEDIA_IMPERSONATION,
                            severity=self._threat_level_to_severity(impersonation_score),
                            confidence=impersonation_score,
                            detected_at=datetime.utcnow(),
                            source_url=account.get("profile_url"),
                            evidence={
                                "platform": platform,
                                "username": account.get("username"),
                                "display_name": account.get("display_name"),
                                "bio": account.get("bio"),
                                "follower_count": account.get("followers", 0),
                                "verification_status": account.get("verified", False),
                                "profile_image_similarity": account.get("profile_image_similarity", 0.0)
                            }
                        )
                        threats.append(threat)
                        
        except Exception as e:
            logger.error(f"Social media impersonation search failed: {str(e)}")
            
        return threats

    def _is_trademark_conflict(self, protected_mark: str, search_result: Dict[str, Any]) -> bool:
        """Determine if search result represents a trademark conflict"""        try:
            result_mark = search_result.get("mark", "")
            
            # Calculate similarity
            similarity = self._calculate_trademark_similarity(protected_mark, result_mark)
            
            # Check if it's a conflict (high similarity and same/related class)
            return similarity > 0.7 and search_result.get("status") != "ABANDONED"
            
        except Exception:
            return False

    def _calculate_trademark_similarity(self, mark1: str, mark2: str) -> float:
        """Calculate similarity between two trademarks"""        try:
            if not mark1 or not mark2:
                return 0.0
            
            # Normalize marks
            mark1_norm = mark1.lower().strip()
            mark2_norm = mark2.lower().strip()
            
            # Exact match
            if mark1_norm == mark2_norm:
                return 1.0
            
            # Calculate Levenshtein distance-based similarity
            from difflib import SequenceMatcher
            return SequenceMatcher(None, mark1_norm, mark2_norm).ratio()
            
        except Exception:
            return 0.0

    async def _perform_web_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform web search for trademark usage"""        # This would integrate with search APIs like Google Custom Search
        # For now, return placeholder results
        return [
            {
                "url": f"https://example.com/result-{i}",
                "title": f"Search result {i} for {query}",
                "description": f"Description mentioning {query}",
                "content": f"Content containing {query}"
            }
            for i in range(10)
        ]

    async def _analyze_trademark_usage(self, result: Dict[str, Any], trademark: str) -> float:
        """Analyze potential trademark usage for threat level"""        try:
            threat_score = 0.0
            
            title = result.get("title", "").lower()
            description = result.get("description", "").lower()
            content = result.get("content", "").lower()
            
            # Check for commercial usage indicators
            commercial_keywords = ["buy", "sell", "shop", "store", "price", "sale", "discount"]
            commercial_score = sum(1 for keyword in commercial_keywords 
                                 if keyword in title or keyword in description) / len(commercial_keywords)
            
            # Check trademark prominence
            trademark_prominence = 0.0
            if trademark.lower() in title:
                trademark_prominence += 0.5
            if trademark.lower() in description[:100]:  # First 100 chars
                trademark_prominence += 0.3
            
            # Check for disclaimers or proper attribution
            disclaimer_keywords = ["trademark", "©", "®", "™", "official", "authorized"]
            has_disclaimer = any(keyword in content for keyword in disclaimer_keywords)
            
            # Calculate overall threat
            threat_score = (commercial_score * 0.4 + trademark_prominence * 0.6)
            
            # Reduce score if proper disclaimers present
            if has_disclaimer:
                threat_score *= 0.5
                
            return min(threat_score, 1.0)
            
        except Exception as e:
            logger.error(f"Trademark usage analysis failed: {str(e)}")
            return 0.0

    async def _analyze_usage_context(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the context of trademark usage"""        try:
            context = {
                "usage_type": "unknown",
                "commercial_intent": False,
                "proper_attribution": False,
                "competitive_usage": False
            }
            
            content = result.get("content", "").lower()
            title = result.get("title", "").lower()
            
            # Determine usage type
            if any(word in content for word in ["review", "opinion", "analysis"]):
                context["usage_type"] = "editorial"
            elif any(word in content for word in ["buy", "shop", "purchase"]):
                context["usage_type"] = "commercial"
            elif any(word in content for word in ["news", "report", "announcement"]):
                context["usage_type"] = "news"
            
            # Check commercial intent
            context["commercial_intent"] = any(word in content for word in 
                                             ["sale", "discount", "buy now", "shop", "store"])
            
            # Check for proper attribution
            context["proper_attribution"] = any(word in content for word in 
                                              ["trademark", "®", "™", "©", "official"])
            
            # Check competitive usage
            competitive_keywords = ["vs", "versus", "alternative", "competitor", "compare"]
            context["competitive_usage"] = any(word in content for word in competitive_keywords)
            
            return context
            
        except Exception as e:
            logger.error(f"Usage context analysis failed: {str(e)}")
            return {}

    async def _search_marketplace(self, marketplace: str, trademark: str) -> List[Dict[str, Any]]:
        """Search marketplace for products using trademark"""        # This would integrate with marketplace APIs
        # For now, return placeholder results
        return [
            {
                "id": f"{marketplace}_product_{i}",
                "title": f"Product {i} mentioning {trademark}",
                "seller": f"Seller{i}",
                "price": f"${10 + i * 5}",
                "url": f"https://{marketplace}.com/product/{i}",
                "counterfeit_indicators": ["suspicious_price", "unknown_seller"]
            }
            for i in range(5)
        ]

    async def _analyze_counterfeit_risk(self, product: Dict[str, Any], trademark: str) -> float:
        """Analyze product for counterfeit risk"""        try:
            risk_score = 0.0
            
            # Price analysis
            price_str = product.get("price", "0")
            try:
                price = float(re.sub(r'[^\d.]', '', price_str))
                if price < 10:  # Suspiciously low price
                    risk_score += 0.3
            except ValueError:
                pass
            
            # Seller analysis
            seller = product.get("seller", "").lower()
            if len(seller) < 5 or seller.startswith("seller"):
                risk_score += 0.2
            
            # Title analysis
            title = product.get("title", "").lower()
            suspicious_phrases = ["replica", "inspired by", "style", "like", "similar"]
            if any(phrase in title for phrase in suspicious_phrases):
                risk_score += 0.4
            
            # Trademark prominence in title
            if trademark.lower() in title:
                risk_score += 0.3
            
            # Counterfeit indicators
            indicators = product.get("counterfeit_indicators", [])
            risk_score += len(indicators) * 0.1
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Counterfeit risk analysis failed: {str(e)}")
            return 0.0

    async def _search_platform_impersonation(self, platform: str, trademark: str) -> List[Dict[str, Any]]:
        """Search platform for impersonation accounts"""        # This would integrate with social media APIs
        # For now, return placeholder results
        variations = [
            trademark.lower(),
            trademark.lower().replace(" ", ""),
            f"official{trademark.lower()}",
            f"{trademark.lower()}official",
            f"real{trademark.lower()}"
        ]
        
        return [
            {
                "username": variation,
                "display_name": f"Official {trademark}",
                "bio": f"Official account of {trademark}",
                "followers": 1000 + i * 500,
                "verified": False,
                "profile_url": f"https://{platform}.com/{variation}",
                "profile_image_similarity": 0.8
            }
            for i, variation in enumerate(variations)
        ]

    async def _analyze_impersonation_risk(self, account: Dict[str, Any], trademark: str) -> float:
        """Analyze account for impersonation risk"""        try:
            risk_score = 0.0
            
            username = account.get("username", "").lower()
            display_name = account.get("display_name", "").lower()
            bio = account.get("bio", "").lower()
            
            # Username similarity
            if trademark.lower() in username:
                risk_score += 0.4
            
            # Display name analysis
            if "official" in display_name and trademark.lower() in display_name:
                risk_score += 0.3
            
            # Bio analysis
            official_claims = ["official", "authorized", "verified", "real"]
            if any(claim in bio for claim in official_claims):
                risk_score += 0.2
            
            # Verification status (lack of verification is suspicious for official claims)
            if not account.get("verified", False) and "official" in display_name:
                risk_score += 0.2
            
            # Profile image similarity
            profile_similarity = account.get("profile_image_similarity", 0.0)
            risk_score += profile_similarity * 0.3
            
            # Follower analysis (suspiciously high followers for new fake account)
            followers = account.get("followers", 0)
            if followers > 10000 and not account.get("verified", False):
                risk_score += 0.1
                
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Impersonation risk analysis failed: {str(e)}")
            return 0.0

    def _threat_level_to_severity(self, threat_level: float) -> str:
        """Convert threat level score to severity category"""        if threat_level >= 0.8:
            return "critical"
        elif threat_level >= 0.6:
            return "high"
        elif threat_level >= 0.4:
            return "medium"
        else:
            return "low"

    async def _process_identity_threat(self, threat: IdentityThreat) -> None:
        """Process detected identity threat"""        try:
            # Store threat
            self.detected_threats.append(threat)
            
            # Calculate legal risk
            threat.legal_risk = await self._calculate_legal_risk(threat)
            
            # Generate recommended actions
            threat.recommended_actions = await self._generate_threat_actions(threat)
            
            # Send alerts for high-severity threats
            if threat.severity in ["high", "critical"]:
                await self._send_threat_alert(threat)
            
            # Auto-initiate actions for critical threats
            if threat.severity == "critical" and self.protection_level in [ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE]:
                await self._auto_respond_to_threat(threat)
                
            logger.info(f"Identity threat processed: {threat.threat_id} ({threat.severity})")
            
        except Exception as e:
            logger.error(f"Threat processing failed: {str(e)}")

    async def _calculate_legal_risk(self, threat: IdentityThreat) -> float:
        """Calculate legal risk score for threat"""        try:
            base_risk = threat.confidence * 0.6
            
            # Threat type risk multipliers
            type_multipliers = {
                ThreatType.TRADEMARK_INFRINGEMENT: 1.0,
                ThreatType.COUNTERFEITING: 1.2,
                ThreatType.BRAND_IMPERSONATION: 0.8,
                ThreatType.DOMAIN_SQUATTING: 0.9,
                ThreatType.LOGO_THEFT: 1.1,
                ThreatType.SOCIAL_MEDIA_IMPERSONATION: 0.7,
                ThreatType.CYBERSQUATTING: 0.9,
                ThreatType.TYPOSQUATTING: 0.6
            }
            
            multiplier = type_multipliers.get(threat.threat_type, 1.0)
            
            # Commercial usage increases legal risk
            evidence = threat.evidence
            if evidence.get("commercial_intent", False):
                multiplier *= 1.3
            
            # Scale factor increases risk
            if evidence.get("follower_count", 0) > 50000:
                multiplier *= 1.2
                
            return min(base_risk * multiplier, 1.0)
            
        except Exception as e:
            logger.error(f"Legal risk calculation failed: {str(e)}")
            return threat.confidence * 0.5

    async def _generate_threat_actions(self, threat: IdentityThreat) -> List[str]:
        """Generate recommended actions for threat"""        actions = []
        
        try:
            threat_type = threat.threat_type
            severity = threat.severity
            
            if threat_type == ThreatType.TRADEMARK_INFRINGEMENT:
                if severity == "critical":
                    actions.extend([
                        "Immediate cease and desist letter",
                        "Legal consultation for injunctive relief",
                        "Document all evidence thoroughly",
                        "Consider expedited trademark opposition"
                    ])
                elif severity == "high":
                    actions.extend([
                        "Send formal cease and desist notice",
                        "Contact legal counsel",
                        "Monitor for compliance",
                        "Prepare for potential litigation"
                    ])
                else:
                    actions.extend([
                        "Send warning notice",
                        "Request voluntary cessation",
                        "Monitor situation closely"
                    ])
                    
            elif threat_type == ThreatType.COUNTERFEITING:
                actions.extend([
                    "Report to marketplace for immediate removal",
                    "Contact law enforcement if criminal activity suspected",
                    "Send takedown notice to hosting provider",
                    "Document counterfeit products as evidence"
                ])
                
            elif threat_type == ThreatType.SOCIAL_MEDIA_IMPERSONATION:
                actions.extend([
                    "Report impersonation to platform",
                    "Request immediate account suspension",
                    "Contact platform's brand protection team",
                    "Monitor for account migration"
                ])
                
            elif threat_type == ThreatType.DOMAIN_SQUATTING:
                actions.extend([
                    "Initiate UDRP proceedings",
                    "Send cease and desist to domain owner",
                    "Consider domain acquisition negotiation",
                    "File complaint with registrar"
                ])
                
        except Exception as e:
            logger.error(f"Threat action generation failed: {str(e)}")
            
        return actions

    async def _send_threat_alert(self, threat: IdentityThreat) -> None:
        """Send alert for detected threat"""        try:
            await self.notification_service.send_alert(
                alert_level=threat.severity,
                message=f"Identity threat detected: {threat.threat_type.value}",
                threat_data=threat.__dict__
            )
            
            logger.info(f"Threat alert sent: {threat.threat_id}")
            
        except Exception as e:
            logger.error(f"Threat alert sending failed: {str(e)}")

    async def _auto_respond_to_threat(self, threat: IdentityThreat) -> None:
        """Automatically respond to critical threats"""        try:
            if threat.threat_type == ThreatType.SOCIAL_MEDIA_IMPERSONATION:
                await self._auto_report_social_impersonation(threat)
            elif threat.threat_type == ThreatType.COUNTERFEITING:
                await self._auto_report_counterfeit(threat)
            elif threat.threat_type == ThreatType.TRADEMARK_INFRINGEMENT:
                await self._auto_send_cease_desist(threat)
                
            threat.status = "action_taken"
            logger.info(f"Automatic response initiated for threat: {threat.threat_id}")
            
        except Exception as e:
            logger.error(f"Auto threat response failed: {str(e)}")

    async def _comprehensive_domain_monitoring(self) -> None:
        """Comprehensive domain monitoring for protection"""        try:
            while self.monitoring_active:
                try:
                    for protection_id, protection in self.domain_protections.items():
                        await self._monitor_domain_threats(protection)
                    
                    await asyncio.sleep(7200)  # Check every 2 hours
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Domain monitoring cycle error: {str(e)}")
                    await asyncio.sleep(300)
                    
        except Exception as e:
            logger.error(f"Comprehensive domain monitoring failed: {str(e)}")

    async def _monitor_domain_threats(self, protection: DomainProtection) -> None:
        """Monitor for domain-related threats"""        try:
            domain_name = protection.domain_name
            
            # Check for typosquatting domains
            typosquatting_threats = await self._detect_typosquatting(domain_name)
            
            # Check for cybersquatting
            cybersquatting_threats = await self._detect_cybersquatting(domain_name)
            
            # Monitor domain expiry
            expiry_threats = await self._check_domain_expiry_risks(protection)
            
            # Process detected threats
            all_threats = typosquatting_threats + cybersquatting_threats + expiry_threats
            for threat in all_threats:
                await self._process_identity_threat(threat)
                
        except Exception as e:
            logger.error(f"Domain threat monitoring failed: {str(e)}")

    async def _detect_typosquatting(self, domain_name: str) -> List[IdentityThreat]:
        """Detect typosquatting domain registrations"""        threats = []
        
        try:
            # Generate typo variations
            typo_domains = self._generate_typo_domains(domain_name)
            
            # Check if typo domains are registered
            for typo_domain in typo_domains:
                try:
                    domain_info = await self._get_domain_info(typo_domain)
                    
                    if domain_info and domain_info.get("registered", False):
                        threat = IdentityThreat(
                            threat_id=f"typo_{hashlib.md5(typo_domain.encode()).hexdigest()[:12]}",
                            brand_id=self.brand_id,
                            threat_type=ThreatType.TYPOSQUATTING,
                            severity="medium",
                            confidence=0.8,
                            detected_at=datetime.utcnow(),
                            source_url=f"http://{typo_domain}",
                            evidence={
                                "typo_domain": typo_domain,
                                "original_domain": domain_name,
                                "registration_date": domain_info.get("registration_date"),
                                "registrar": domain_info.get("registrar")
                            }
                        )
                        threats.append(threat)
                        
                except Exception:
                    continue  # Domain not registered or error checking
                    
        except Exception as e:
            logger.error(f"Typosquatting detection failed: {str(e)}")
            
        return threats

    def _generate_typo_domains(self, domain: str) -> List[str]:
        """Generate common typosquatting variations"""        variations = []
        
        try:
            # Extract domain parts
            extracted = tldextract.extract(domain)
            domain_name = extracted.domain
            tld = extracted.suffix or "com"
            
            # Character substitution variations
            for i, char in enumerate(domain_name):
                # Adjacent key typos (simplified)
                adjacent_keys = {
                    'a': ['s', 'q', 'w'], 'b': ['v', 'g', 'h', 'n'],
                    'c': ['x', 'd', 'f', 'v'], 'd': ['s', 'e', 'r', 'f', 'c', 'x'],
                    'e': ['w', 'r', 't', 'd', 's'], 'f': ['d', 'r', 't', 'g', 'c', 'v'],
                    # Add more as needed
                }
                
                if char in adjacent_keys:
                    for replacement in adjacent_keys[char]:
                        typo_name = domain_name[:i] + replacement + domain_name[i+1:]
                        variations.append(f"{typo_name}.{tld}")
            
            # Character omission
            for i in range(len(domain_name)):
                if i > 0:  # Don't create single-character domains
                    omission_name = domain_name[:i] + domain_name[i+1:]
                    variations.append(f"{omission_name}.{tld}")
            
            # Character duplication
            for i in range(len(domain_name)):
                duplication_name = domain_name[:i] + domain_name[i] + domain_name[i:]
                variations.append(f"{duplication_name}.{tld}")
            
            # Common TLD variations
            common_tlds = ["com", "net", "org", "info", "biz"]
            if tld not in common_tlds:
                for alt_tld in common_tlds:
                    variations.append(f"{domain_name}.{alt_tld}")
                    
        except Exception as e:
            logger.error(f"Typo domain generation failed: {str(e)}")
        
        return list(set(variations))  # Remove duplicates

    async def _visual_identity_monitoring(self) -> None:
        """Monitor for visual identity theft (logos, designs)"""        try:
            while self.monitoring_active:
                try:
                    # Search for logo usage across web
                    await self._monitor_logo_usage()
                    
                    # Monitor visual style copying
                    await self._monitor_visual_style_copying()
                    
                    await asyncio.sleep(1800)  # Check every 30 minutes
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Visual identity monitoring error: {str(e)}")
                    await asyncio.sleep(300)
                    
        except Exception as e:
            logger.error(f"Visual identity monitoring failed: {str(e)}")

    async def generate_protection_report(self, time_period: str = "30d") -> ProtectionReport:
        """Generate comprehensive identity protection report"""        try:
            report_id = f"protection_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Calculate time cutoff
            cutoff_time = datetime.utcnow() - timedelta(days=30 if time_period == "30d" else 7)
            
            # Get active threats in time period
            active_threats = [
                threat for threat in self.detected_threats
                if threat.detected_at >= cutoff_time and threat.status != "resolved"
            ]
            
            # Generate protection summary
            protection_summary = {
                "total_trademark_protections": len(self.trademark_protections),
                "total_domain_protections": len(self.domain_protections),
                "active_threats": len(active_threats),
                "critical_threats": len([t for t in active_threats if t.severity == "critical"]),
                "high_threats": len([t for t in active_threats if t.severity == "high"]),
                "threat_types": self._get_threat_type_distribution(active_threats)
            }
            
            # Identify protection gaps
            protection_gaps = await self._identify_protection_gaps()
            
            # Generate recommendations
            recommendations = await self._generate_protection_recommendations(active_threats, protection_gaps)
            
            # Identify legal actions needed
            legal_actions = await self._identify_legal_actions_needed(active_threats)
            
            return ProtectionReport(
                report_id=report_id,
                brand_id=self.brand_id,
                protection_summary=protection_summary,
                active_threats=active_threats,
                protection_gaps=protection_gaps,
                recommendations=recommendations,
                legal_actions_needed=legal_actions,
                report_period=time_period
            )
            
        except Exception as e:
            logger.error(f"Protection report generation failed: {str(e)}")
            return ProtectionReport(
                report_id="error",
                brand_id=self.brand_id,
                protection_summary={},
                active_threats=[],
                protection_gaps=[],
                recommendations=[],
                legal_actions_needed=[]
            )

    def _get_threat_type_distribution(self, threats: List[IdentityThreat]) -> Dict[str, int]:
        """Get distribution of threat types"""        distribution = {}
        for threat in threats:
            threat_type = threat.threat_type.value
            distribution[threat_type] = distribution.get(threat_type, 0) + 1
        return distribution

    async def _identify_protection_gaps(self) -> List[str]:
        """Identify gaps in current protection coverage"""        gaps = []
        
        try:
            # Check trademark coverage
            if not self.trademark_protections:
                gaps.append("No trademark protections registered")
            
            # Check domain coverage
            if not self.domain_protections:
                gaps.append("No domain protections active")
            
            # Check for expired protections
            now = datetime.utcnow()
            for protection in self.trademark_protections.values():
                if protection.expiry_date and protection.expiry_date < now:
                    gaps.append(f"Expired trademark protection: {protection.trademark_name}")
            
            for protection in self.domain_protections.values():
                if protection.expiry_date and protection.expiry_date < now + timedelta(days=90):
                    gaps.append(f"Domain protection expiring soon: {protection.domain_name}")
            
            # Check protection level adequacy
            critical_threats = len([t for t in self.detected_threats if t.severity == "critical"])
            if critical_threats > 0 and self.protection_level == ProtectionLevel.BASIC:
                gaps.append("Protection level insufficient for threat landscape")
                
        except Exception as e:
            logger.error(f"Protection gap identification failed: {str(e)}")
        
        return gaps


class TrademarkGuardian:
    """    Specialized Trademark Protection & Legal Action Coordinator
    
    Handles complex trademark protection scenarios and coordinates legal responses.
    """
    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        self.legal_generator = LegalDocumentGenerator()
        self.pending_actions: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Trademark guardian initialized for brand: {brand_id}")

    async def initiate_legal_action(self, threat: IdentityThreat, action_type: str) -> Dict[str, Any]:
        """Initiate legal action for identity threat"""        try:
            action_id = f"legal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{threat.threat_id[:8]}"
            
            if action_type == "cease_desist":
                result = await self._generate_cease_desist_letter(threat, action_id)
            elif action_type == "takedown_notice":
                result = await self._generate_takedown_notice(threat, action_id)
            elif action_type == "udrp_complaint":
                result = await self._prepare_udrp_complaint(threat, action_id)
            elif action_type == "trademark_opposition":
                result = await self._prepare_trademark_opposition(threat, action_id)
            else:
                raise ValueError(f"Unknown legal action type: {action_type}")
            
            # Track the legal action
            self.pending_actions[action_id] = {
                "threat_id": threat.threat_id,
                "action_type": action_type,
                "status": "initiated",
                "created_at": datetime.utcnow(),
                "documents": result.get("documents", []),
                "next_steps": result.get("next_steps", [])
            }
            
            logger.info(f"Legal action initiated: {action_id} ({action_type})")
            return {"success": True, "action_id": action_id, "result": result}
            
        except Exception as e:
            logger.error(f"Legal action initiation failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _generate_cease_desist_letter(self, threat: IdentityThreat, action_id: str) -> Dict[str, Any]:
        """Generate cease and desist letter"""        try:
            letter_content = await self.legal_generator.generate_cease_desist(
                brand_id=self.brand_id,
                threat_details=threat.__dict__,
                urgency=threat.severity
            )
            
            return {
                "documents": [
                    {
                        "type": "cease_desist_letter",
                        "content": letter_content,
                        "filename": f"cease_desist_{action_id}.pdf"
                    }
                ],
                "next_steps": [
                    "Review and customize letter content",
                    "Send via certified mail and email",
                    "Set follow-up reminder for 14 days",
                    "Prepare for escalation if no response"
                ]
            }
            
        except Exception as e:
            logger.error(f"Cease desist generation failed: {str(e)}")
            raise

    async def _generate_takedown_notice(self, threat: IdentityThreat, action_id: str) -> Dict[str, Any]:
        """Generate DMCA/platform takedown notice"""        try:
            notice_content = await self.legal_generator.generate_takedown_notice(
                brand_id=self.brand_id,
                threat_details=threat.__dict__,
                platform=threat.evidence.get("platform", "unknown")
            )
            
            return {
                "documents": [
                    {
                        "type": "takedown_notice",
                        "content": notice_content,
                        "filename": f"takedown_notice_{action_id}.pdf"
                    }
                ],
                "next_steps": [
                    "Submit notice to platform/host",
                    "Monitor for compliance",
                    "Follow up if not removed within 24-48 hours",
                    "Document response for record"
                ]
            }
            
        except Exception as e:
            logger.error(f"Takedown notice generation failed: {str(e)}")
            raise

    async def track_legal_action_status(self, action_id: str, status_update: str) -> None:
        """Track status of legal action"""        try:
            if action_id in self.pending_actions:
                self.pending_actions[action_id]["status"] = status_update
                self.pending_actions[action_id]["last_updated"] = datetime.utcnow()
                
                logger.info(f"Legal action status updated: {action_id} -> {status_update}")
                
        except Exception as e:
            logger.error(f"Legal action tracking failed: {str(e)}")

    def get_pending_actions(self) -> Dict[str, Dict[str, Any]]:
        """Get all pending legal actions"""        return self.pending_actions.copy()
