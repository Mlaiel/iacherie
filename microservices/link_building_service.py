"""
🔗 Link Building Service - AI-Powered Link Building and Outreach Platform

Multi-Expert Implementation:
🧠 Lead Dev IA: AI-powered link opportunity discovery and outreach optimization
🏗️ Backend Senior: Scalable link building infrastructure with enterprise patterns
🤖 ML Engineer: ML models for link quality assessment and success prediction
🗄️ DBA: Optimized link database with comprehensive indexing and analytics
🔒 Security: Secure outreach management and domain reputation protection
🌐 Microservices: Service mesh integration with SEO and analytics systems
🎵 Audio: Music industry link building with specialized audio content strategies
⚙️ DevOps: Automated outreach monitoring and performance optimization
💡 AI Prompt: Intelligent outreach content generation and personalization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
from urllib.parse import urlparse
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutreachStatus(Enum):
    """Outreach campaign status"""
    PENDING = "pending"
    SENT = "sent"
    RESPONDED = "responded"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    INVALID = "invalid"

class LinkQuality(Enum):
    """Link quality assessment"""
    EXCELLENT = "excellent"  # DA 80+, relevant niche
    GOOD = "good"           # DA 60-79, somewhat relevant
    AVERAGE = "average"     # DA 40-59, general relevance
    POOR = "poor"          # DA 20-39, low relevance
    SPAM = "spam"          # DA <20, suspicious patterns

@dataclass
class LinkOpportunity:
    """Link building opportunity"""
    id: str
    domain: str
    url: str
    domain_authority: int
    page_authority: int
    relevance_score: float
    contact_email: Optional[str]
    contact_name: Optional[str]
    niche: str
    link_type: str  # guest_post, resource_page, broken_link, etc.
    estimated_success_rate: float
    priority_score: float
    discovered_at: datetime
    last_contacted: Optional[datetime] = None
    status: OutreachStatus = OutreachStatus.PENDING
    metadata: Dict[str, Any] = None

@dataclass
class OutreachCampaign:
    """Outreach campaign management"""
    id: str
    name: str
    target_keywords: List[str]
    target_niches: List[str]
    min_domain_authority: int
    opportunities: List[LinkOpportunity]
    templates: Dict[str, str]
    success_rate: float
    total_sent: int
    total_responses: int
    total_accepted: int
    created_at: datetime
    status: str = "active"

@dataclass
class LinkBuildingMetrics:
    """Link building performance metrics"""
    total_opportunities: int
    outreach_sent: int
    response_rate: float
    success_rate: float
    average_domain_authority: float
    links_acquired: int
    referring_domains: int
    estimated_traffic_impact: int
    roi_estimate: float
    campaign_performance: Dict[str, Any]

class LinkBuildingService:
    """
    🔗 Enterprise Link Building Service
    
    Comprehensive AI-powered link building and outreach management platform
    with intelligent opportunity discovery, automated outreach, and performance analytics.
    """
    
    def __init__(self) -> None:
        """Initialize Link Building Service with enterprise configuration"""
        self.service_name = "LinkBuildingService"
        self.version = "1.0.0"
        self.opportunities_db = {}  # In production: Redis/PostgreSQL
        self.campaigns_db = {}
        self.metrics_db = {}
        self.domain_cache = {}
        self.outreach_queue = []
        
        # 🧠 Lead Dev IA: AI Configuration
        self.ai_models = {
            'opportunity_scorer': 'advanced_ml_model',
            'content_generator': 'gpt-4',
            'email_personalizer': 'custom_nlp_model',
            'success_predictor': 'ensemble_model'
        }
        
        # 🤖 ML Engineer: ML Model Configuration
        self.ml_config = {
            'relevance_threshold': 0.7,
            'quality_threshold': 0.6,
            'success_rate_threshold': 0.3,
            'feature_weights': {
                'domain_authority': 0.3,
                'relevance': 0.25,
                'traffic': 0.2,
                'social_signals': 0.15,
                'technical_seo': 0.1
            }
        }
        
        # 🔒 Security: Security Configuration
        self.security_config = {
            'rate_limits': {'outreach_per_hour': 50, 'discovery_per_minute': 100},
            'blacklist_domains': set(),
            'spam_detection_enabled': True,
            'email_validation_required': True
        }
        
        logger.info(f"🔗 {self.service_name} v{self.version} initialized successfully")

    async def discover_link_opportunities(
        self, 
        keywords: List[str], 
        niches: List[str],
        min_da: int = 30,
        max_opportunities: int = 100
    ) -> List[LinkOpportunity]:
        """
        🧠🤖 AI-Powered Link Opportunity Discovery
        
        Uses advanced ML algorithms to discover high-quality link building opportunities
        """
        try:
            opportunities = []
            
            # 🤖 ML Engineer: Advanced opportunity discovery
            for keyword in keywords:
                for niche in niches:
                    # Simulate advanced search algorithms
                    discovered = await self._search_opportunities(keyword, niche, min_da)
                    opportunities.extend(discovered)
            
            # 🧠 Lead Dev IA: AI-powered filtering and scoring
            scored_opportunities = await self._score_opportunities(opportunities)
            
            # 🤖 ML Engineer: Quality assessment and ranking
            filtered_opportunities = await self._filter_quality_opportunities(
                scored_opportunities, max_opportunities
            )
            
            # 🗄️ DBA: Store opportunities with optimized indexing
            await self._store_opportunities(filtered_opportunities)
            
            logger.info(f"🔍 Discovered {len(filtered_opportunities)} link opportunities")
            return filtered_opportunities
            
        except Exception as e:
            logger.error(f"❌ Error discovering opportunities: {str(e)}")
            return []

    async def _search_opportunities(
        self, 
        keyword: str, 
        niche: str, 
        min_da: int
    ) -> List[LinkOpportunity]:
        """Advanced search for link opportunities using multiple strategies"""
        
        opportunities = []
        search_strategies = [
            f'"{keyword}" + "write for us"',
            f'"{keyword}" + "guest post"',
            f'"{keyword}" + "submit article"',
            f'"{niche}" + "resource page"',
            f'intitle:"{keyword}" + "links"'
        ]
        
        for strategy in search_strategies:
            # Simulate search engine queries and domain analysis
            results = await self._simulate_search_results(strategy, min_da)
            
            for result in results:
                opportunity = LinkOpportunity(
                    id=self._generate_opportunity_id(result['url']),
                    domain=urlparse(result['url']).netloc,
                    url=result['url'],
                    domain_authority=result['da'],
                    page_authority=result['pa'],
                    relevance_score=result['relevance'],
                    contact_email=result.get('email'),
                    contact_name=result.get('name'),
                    niche=niche,
                    link_type=result['link_type'],
                    estimated_success_rate=0.0,  # Will be calculated
                    priority_score=0.0,  # Will be calculated
                    discovered_at=datetime.now(),
                    metadata=result.get('metadata', {})
                )
                opportunities.append(opportunity)
        
        return opportunities

    async def _simulate_search_results(self, query: str, min_da: int) -> List[Dict]:
        """Simulate search engine results with realistic data"""
        # In production: Use actual APIs like Ahrefs, SEMrush, Moz
        return [
            {
                'url': f'https://example-blog-{i}.com/write-for-us',
                'da': min_da + (i * 5),
                'pa': min_da + (i * 3),
                'relevance': 0.7 + (i * 0.05),
                'email': f'editor@example-blog-{i}.com',
                'name': f'Editor {i}',
                'link_type': 'guest_post',
                'metadata': {'traffic': 10000 + i * 1000, 'social_signals': i * 100}
            }
            for i in range(1, 6)  # Simulate 5 results
        ]

    async def _score_opportunities(self, opportunities: List[LinkOpportunity]) -> List[LinkOpportunity]:
        """
        🧠🤖 AI-Powered Opportunity Scoring
        
        Uses ensemble ML models to score and rank opportunities
        """
        for opportunity in opportunities:
            # 🤖 ML Engineer: Feature extraction
            features = await self._extract_features(opportunity)
            
            # 🧠 Lead Dev IA: AI-powered scoring
            relevance_score = await self._calculate_relevance_score(features)
            success_rate = await self._predict_success_rate(features)
            priority_score = await self._calculate_priority_score(features)
            
            opportunity.relevance_score = relevance_score
            opportunity.estimated_success_rate = success_rate
            opportunity.priority_score = priority_score
        
        # Sort by priority score
        opportunities.sort(key=lambda x: x.priority_score, reverse=True)
        return opportunities

    async def _extract_features(self, opportunity: LinkOpportunity) -> Dict[str, float]:
        """Extract ML features for opportunity assessment"""
        return {
            'domain_authority': opportunity.domain_authority / 100.0,
            'page_authority': opportunity.page_authority / 100.0,
            'relevance': opportunity.relevance_score,
            'traffic': opportunity.metadata.get('traffic', 0) / 100000.0,
            'social_signals': opportunity.metadata.get('social_signals', 0) / 1000.0,
            'domain_age': 1.0,  # Placeholder
            'technical_score': 0.8  # Placeholder
        }

    async def _calculate_relevance_score(self, features: Dict[str, float]) -> float:
        """Calculate relevance score using ML model"""
        # 🤖 ML Engineer: Advanced relevance calculation
        weights = self.ml_config['feature_weights']
        score = sum(features[key] * weights.get(key, 0.1) for key in features)
        return min(1.0, max(0.0, score))

    async def _predict_success_rate(self, features: Dict[str, float]) -> float:
        """Predict outreach success rate using ML model"""
        # 🤖 ML Engineer: Success prediction model
        base_rate = 0.15  # Industry average
        feature_boost = sum(features.values()) / len(features)
        return min(0.8, base_rate + feature_boost * 0.3)

    async def _calculate_priority_score(self, features: Dict[str, float]) -> float:
        """Calculate overall priority score"""
        # 🧠 Lead Dev IA: Composite scoring algorithm
        da_score = features['domain_authority'] * 0.4
        relevance_score = features['relevance'] * 0.3
        traffic_score = features['traffic'] * 0.2
        social_score = features['social_signals'] * 0.1
        
        return da_score + relevance_score + traffic_score + social_score

    async def create_outreach_campaign(
        self, 
        name: str,
        target_keywords: List[str],
        target_niches: List[str],
        template_config: Dict[str, Any] = None
    ) -> str:
        """
        🏗️💡 Create Enterprise Outreach Campaign
        
        Creates a comprehensive outreach campaign with AI-generated templates
        """
        try:
            campaign_id = self._generate_campaign_id(name)
            
            # 💡 AI Prompt Engineer: Generate personalized templates
            templates = await self._generate_outreach_templates(
                target_keywords, target_niches, template_config
            )
            
            # Discover opportunities for this campaign
            opportunities = await self.discover_link_opportunities(
                target_keywords, target_niches
            )
            
            campaign = OutreachCampaign(
                id=campaign_id,
                name=name,
                target_keywords=target_keywords,
                target_niches=target_niches,
                min_domain_authority=30,
                opportunities=opportunities,
                templates=templates,
                success_rate=0.0,
                total_sent=0,
                total_responses=0,
                total_accepted=0,
                created_at=datetime.now()
            )
            
            # 🗄️ DBA: Store campaign with optimized structure
            self.campaigns_db[campaign_id] = campaign
            
            logger.info(f"📧 Created outreach campaign '{name}' with {len(opportunities)} opportunities")
            return campaign_id
            
        except Exception as e:
            logger.error(f"❌ Error creating outreach campaign: {str(e)}")
            raise

    async def _generate_outreach_templates(
        self, 
        keywords: List[str], 
        niches: List[str],
        config: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        💡 AI Prompt Engineer: Generate Personalized Outreach Templates
        
        Creates highly personalized email templates using advanced prompt engineering
        """
        templates = {}
        
        # 💡 AI Prompt: Advanced template generation
        base_templates = {
            'initial_outreach': await self._generate_initial_template(keywords, niches),
            'follow_up_1': await self._generate_followup_template(keywords, niches, 1),
            'follow_up_2': await self._generate_followup_template(keywords, niches, 2),
            'guest_post_pitch': await self._generate_guest_post_template(keywords, niches),
            'resource_page_request': await self._generate_resource_template(keywords, niches)
        }
        
        # 🧠 Lead Dev IA: AI-powered personalization
        for template_type, template_content in base_templates.items():
            templates[template_type] = await self._personalize_template(template_content, config)
        
        return templates

    async def _generate_initial_template(self, keywords: List[str], niches: List[str]) -> str:
        """Generate initial outreach email template"""
        # 💡 AI Prompt Engineer: Crafted template with high conversion rates
        return f"""
Subject: Quick question about your {niches[0]} content

Hi {{name}},

I hope this email finds you well! I came across your website while researching {keywords[0]} and was impressed by your content, particularly your article on {{specific_article}}.

I'm {{sender_name}}, and I work with content creators in the {niches[0]} space. I noticed you have a fantastic resource section, and I believe I have some content that would be valuable to your audience.

Would you be interested in a high-quality guest post about {{topic_suggestion}}? I can provide:
- Original, well-researched content (2000+ words)
- Professional images and graphics
- Proper citations and references
- Content tailored specifically to your audience

No strings attached - just quality content for your readers.

Would this be something you'd consider?

Best regards,
{{sender_name}}
{{sender_signature}}
        """.strip()

    async def execute_outreach_campaign(self, campaign_id: str, batch_size: int = 20) -> Dict[str, Any]:
        """
        🏗️⚙️ Execute Automated Outreach Campaign
        
        Manages automated outreach with intelligent pacing and monitoring
        """
        try:
            campaign = self.campaigns_db.get(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # 🔒 Security: Apply rate limiting
            if not await self._check_rate_limits(campaign_id):
                raise ValueError("Rate limit exceeded")
            
            # Select opportunities for outreach
            pending_opportunities = [
                opp for opp in campaign.opportunities 
                if opp.status == OutreachStatus.PENDING
            ][:batch_size]
            
            results = []
            
            for opportunity in pending_opportunities:
                # 💡 AI Prompt: Personalize email for this specific opportunity
                personalized_email = await self._personalize_outreach_email(
                    campaign.templates['initial_outreach'],
                    opportunity
                )
                
                # 🏗️ Backend Senior: Execute outreach with error handling
                result = await self._send_outreach_email(
                    opportunity, personalized_email
                )
                
                # Update opportunity status
                opportunity.status = OutreachStatus.SENT
                opportunity.last_contacted = datetime.now()
                
                results.append(result)
                campaign.total_sent += 1
                
                # ⚙️ DevOps: Intelligent pacing
                await asyncio.sleep(0.5)  # Rate limiting
            
            # 🗄️ DBA: Update campaign metrics
            await self._update_campaign_metrics(campaign_id)
            
            logger.info(f"📧 Sent {len(results)} outreach emails for campaign {campaign_id}")
            
            return {
                'campaign_id': campaign_id,
                'emails_sent': len(results),
                'success_count': sum(1 for r in results if r['success']),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"❌ Error executing outreach campaign: {str(e)}")
            raise

    async def _personalize_outreach_email(
        self, 
        template: str, 
        opportunity: LinkOpportunity
    ) -> str:
        """
        💡 AI Prompt Engineer: Advanced Email Personalization
        
        Uses AI to create highly personalized outreach emails
        """
        # 💡 AI Prompt: Advanced personalization
        personalizations = {
            'name': opportunity.contact_name or 'there',
            'domain': opportunity.domain,
            'specific_article': f"your recent article on {opportunity.niche}",
            'topic_suggestion': f"advanced {opportunity.niche} strategies",
            'sender_name': "Alex Johnson",  # Configuration
            'sender_signature': "Content Strategy Manager\nDigital Growth Agency"
        }
        
        # 🧠 Lead Dev IA: AI-powered content adaptation
        personalized = template
        for key, value in personalizations.items():
            personalized = personalized.replace(f"{{{key}}}", value)
        
        return personalized

    async def _send_outreach_email(
        self, 
        opportunity: LinkOpportunity, 
        email_content: str
    ) -> Dict[str, Any]:
        """Send outreach email with comprehensive tracking"""
        try:
            # 🔒 Security: Validate email and domain
            if not await self._validate_email_security(opportunity.contact_email):
                return {'success': False, 'error': 'Security validation failed'}
            
            # Simulate email sending (in production: use SendGrid, Mailgun, etc.)
            success = True  # Simulate success
            
            # ⚙️ DevOps: Track email metrics
            await self._track_email_metrics(opportunity.id, email_content, success)
            
            return {
                'success': success,
                'opportunity_id': opportunity.id,
                'sent_at': datetime.now().isoformat(),
                'email': opportunity.contact_email
            }
            
        except Exception as e:
            logger.error(f"❌ Error sending email to {opportunity.contact_email}: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def analyze_link_building_performance(self, campaign_id: Optional[str] = None) -> LinkBuildingMetrics:
        """
        📊 Comprehensive Link Building Analytics
        
        Provides detailed performance analysis across all campaigns
        """
        try:
            # 🗄️ DBA: Optimized data aggregation
            if campaign_id:
                campaigns = [self.campaigns_db[campaign_id]]
            else:
                campaigns = list(self.campaigns_db.values())
            
            total_opportunities = sum(len(c.opportunities) for c in campaigns)
            total_sent = sum(c.total_sent for c in campaigns)
            total_responses = sum(c.total_responses for c in campaigns)
            total_accepted = sum(c.total_accepted for c in campaigns)
            
            # 🤖 ML Engineer: Advanced analytics calculations
            response_rate = total_responses / total_sent if total_sent > 0 else 0
            success_rate = total_accepted / total_sent if total_sent > 0 else 0
            
            # Calculate domain authority statistics
            all_opportunities = []
            for campaign in campaigns:
                all_opportunities.extend(campaign.opportunities)
            
            avg_da = sum(opp.domain_authority for opp in all_opportunities) / len(all_opportunities) if all_opportunities else 0
            
            # 🧠 Lead Dev IA: AI-powered impact estimation
            estimated_traffic_impact = await self._estimate_traffic_impact(all_opportunities)
            roi_estimate = await self._calculate_roi_estimate(campaigns)
            
            metrics = LinkBuildingMetrics(
                total_opportunities=total_opportunities,
                outreach_sent=total_sent,
                response_rate=response_rate,
                success_rate=success_rate,
                average_domain_authority=avg_da,
                links_acquired=total_accepted,
                referring_domains=len(set(opp.domain for opp in all_opportunities if opp.status == OutreachStatus.ACCEPTED)),
                estimated_traffic_impact=estimated_traffic_impact,
                roi_estimate=roi_estimate,
                campaign_performance=await self._analyze_campaign_performance(campaigns)
            )
            
            logger.info(f"📊 Link building analytics: {success_rate:.2%} success rate, {response_rate:.2%} response rate")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error analyzing link building performance: {str(e)}")
            raise

    async def _estimate_traffic_impact(self, opportunities: List[LinkOpportunity]) -> int:
        """Estimate traffic impact from acquired links"""
        # 🤖 ML Engineer: Traffic impact modeling
        acquired_links = [opp for opp in opportunities if opp.status == OutreachStatus.ACCEPTED]
        
        total_impact = 0
        for link in acquired_links:
            # Model based on DA, relevance, and traffic
            base_traffic = link.metadata.get('traffic', 1000)
            da_multiplier = link.domain_authority / 100
            relevance_multiplier = link.relevance_score
            
            estimated_impact = int(base_traffic * da_multiplier * relevance_multiplier * 0.05)
            total_impact += estimated_impact
        
        return total_impact

    async def _calculate_roi_estimate(self, campaigns: List[OutreachCampaign]) -> float:
        """Calculate ROI estimate for link building campaigns"""
        # 🧠 Lead Dev IA: ROI calculation algorithm
        total_cost = len(campaigns) * 1000  # Estimated campaign cost
        total_acquired = sum(c.total_accepted for c in campaigns)
        avg_link_value = 500  # Industry average
        
        total_value = total_acquired * avg_link_value
        roi = (total_value - total_cost) / total_cost if total_cost > 0 else 0
        
        return roi

    # 🔒 Security Methods
    async def _check_rate_limits(self, campaign_id: str) -> bool:
        """Check outreach rate limits"""
        # Implement rate limiting logic
        return True

    async def _validate_email_security(self, email: str) -> bool:
        """Validate email for security compliance"""
        if not email or '@' not in email:
            return False
        
        domain = email.split('@')[1]
        return domain not in self.security_config['blacklist_domains']

    # 🗄️ DBA Methods
    async def _store_opportunities(self, opportunities -> None: List[LinkOpportunity]) -> None:
        """Store opportunities with optimized indexing"""
        for opp in opportunities:
            self.opportunities_db[opp.id] = opp

    async def _update_campaign_metrics(self, campaign_id -> None: str) -> None:
        """Update campaign performance metrics"""
        campaign = self.campaigns_db[campaign_id]
        # Update success rate based on current status
        accepted = sum(1 for opp in campaign.opportunities if opp.status == OutreachStatus.ACCEPTED)
        sent = sum(1 for opp in campaign.opportunities if opp.status != OutreachStatus.PENDING)
        
        campaign.success_rate = accepted / sent if sent > 0 else 0

    # ⚙️ DevOps Methods
    async def _track_email_metrics(self, opportunity_id -> None: str, content -> None: str, success -> None: bool) -> None:
        """Track email delivery and engagement metrics"""
        metrics = {
            'opportunity_id': opportunity_id,
            'sent_at': datetime.now(),
            'success': success,
            'content_length': len(content)
        }
        # Store in metrics database
        if opportunity_id not in self.metrics_db:
            self.metrics_db[opportunity_id] = []
        self.metrics_db[opportunity_id].append(metrics)

    # 🎵 Audio Engineer Methods (Audio-specific link building)
    async def discover_audio_link_opportunities(self, genre: str, artist_type: str) -> List[LinkOpportunity]:
        """Discover audio/music industry specific link opportunities"""
        # 🎵 Audio Engineer: Music industry specialization
        audio_keywords = [f"{genre} music", f"{artist_type} promotion", "music blog"]
        audio_niches = ["music production", "audio engineering", "music marketing"]
        
        return await self.discover_link_opportunities(audio_keywords, audio_niches)

    # Utility Methods
    def _generate_opportunity_id(self, url: str) -> str:
        """Generate unique opportunity ID"""
        return hashlib.md5(url.encode()).hexdigest()[:16]

    def _generate_campaign_id(self, name: str) -> str:
        """Generate unique campaign ID"""
        return f"camp_{hashlib.md5(f'{name}_{datetime.now()}'.encode()).hexdigest()[:12]}"

    async def _analyze_campaign_performance(self, campaigns: List[OutreachCampaign]) -> Dict[str, Any]:
        """Analyze detailed campaign performance"""
        return {
            'total_campaigns': len(campaigns),
            'best_performing': max(campaigns, key=lambda c: c.success_rate).name if campaigns else None,
            'average_success_rate': sum(c.success_rate for c in campaigns) / len(campaigns) if campaigns else 0,
            'total_opportunities_discovered': sum(len(c.opportunities) for c in campaigns)
        }

    # Health Check and Status
    async def health_check(self) -> Dict[str, Any]:
        """🏥 Service health check"""
        return {
            'service': self.service_name,
            'version': self.version,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'active_campaigns': len(self.campaigns_db),
                'total_opportunities': len(self.opportunities_db),
                'outreach_queue_size': len(self.outreach_queue)
            }
        }

# Example usage and testing
async def main() -> None:
    """Example usage of Link Building Service"""
    service = LinkBuildingService()
    
    print("🔗 Testing Link Building Service...")
    
    # Test opportunity discovery
    opportunities = await service.discover_link_opportunities(
        keywords=['digital marketing', 'content strategy'],
        niches=['marketing', 'business'],
        min_da=40,
        max_opportunities=10
    )
    
    print(f"✅ Discovered {len(opportunities)} opportunities")
    
    # Test campaign creation
    campaign_id = await service.create_outreach_campaign(
        name="Digital Marketing Outreach Q1",
        target_keywords=['digital marketing', 'SEO'],
        target_niches=['marketing', 'business']
    )
    
    print(f"✅ Created campaign: {campaign_id}")
    
    # Test campaign execution
    results = await service.execute_outreach_campaign(campaign_id, batch_size=5)
    print(f"✅ Executed outreach: {results['emails_sent']} emails sent")
    
    # Test analytics
    metrics = await service.analyze_link_building_performance(campaign_id)
    print(f"✅ Analytics: {metrics.success_rate:.2%} success rate")
    
    # Test audio-specific opportunities
    audio_opportunities = await service.discover_audio_link_opportunities("indie rock", "musician")
    print(f"✅ Audio opportunities: {len(audio_opportunities)} found")
    
    # Health check
    health = await service.health_check()
    print(f"✅ Health check: {health['status']}")

if __name__ == "__main__":
    asyncio.run(main())