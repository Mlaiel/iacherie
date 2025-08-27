"""
Business Intent Analysis for Creative Industry

Specialized intent analysis for business operations, monetization strategies,
and commercial workflows in the creative industry ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import re
import json

from .config import IntentRecognitionConfig
from .exceptions import BusinessAnalysisError

logger = logging.getLogger(__name__)


class BusinessIntentCategory(Enum):
    """Business intent categories for creative professionals"""
    MONETIZATION = "monetization"
    REVENUE_TRACKING = "revenue_tracking"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    CONTENT_LICENSING = "content_licensing"
    SUBSCRIPTION_MANAGEMENT = "subscription_management"
    PAYMENT_PROCESSING = "payment_processing"
    TAX_REPORTING = "tax_reporting"
    CONTRACT_MANAGEMENT = "contract_management"
    COLLABORATION_BUSINESS = "collaboration_business"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    AUDIENCE_MONETIZATION = "audience_monetization"
    INTELLECTUAL_PROPERTY = "intellectual_property"


class RevenueStreamType(Enum):
    """Types of revenue streams for creators"""
    STREAMING_ROYALTIES = "streaming_royalties"
    BRAND_SPONSORSHIPS = "brand_sponsorships"
    MERCHANDISE_SALES = "merchandise_sales"
    LIVE_PERFORMANCES = "live_performances"
    DIGITAL_PRODUCTS = "digital_products"
    SUBSCRIPTION_REVENUE = "subscription_revenue"
    AFFILIATE_MARKETING = "affiliate_marketing"
    LICENSING_FEES = "licensing_fees"
    DONATION_REVENUE = "donation_revenue"
    COURSE_SALES = "course_sales"
    NFT_SALES = "nft_sales"
    CONSULTING_FEES = "consulting_fees"


class BusinessPriority(Enum):
    """Business priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPPORTUNITY = "opportunity"


@dataclass
class BusinessIntentAnalysis:
    """Business intent analysis result"""
    
    # Primary business intent
    business_category: BusinessIntentCategory
    revenue_stream_type: Optional[RevenueStreamType] = None
    priority_level: BusinessPriority = BusinessPriority.MEDIUM
    
    # Financial implications
    potential_revenue_impact: float = 0.0
    cost_implications: float = 0.0
    roi_estimate: float = 0.0
    
    # Timeline and urgency
    estimated_timeline: timedelta = field(default_factory=lambda: timedelta(days=7))
    urgency_score: float = 0.5
    deadline_pressure: bool = False
    
    # Market context
    market_opportunity_score: float = 0.0
    competitive_analysis: Dict[str, Any] = field(default_factory=dict)
    seasonal_relevance: float = 0.0
    
    # Risk assessment
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)
    
    # Recommendations
    business_recommendations: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=list)


@dataclass
class MonetizationOpportunity:
    """Monetization opportunity identification"""
    
    opportunity_type: RevenueStreamType
    potential_revenue: float
    implementation_effort: str  # low, medium, high
    time_to_market: timedelta
    
    # Market analysis
    market_demand: float = 0.0
    competition_level: str = "medium"
    unique_advantages: List[str] = field(default_factory=list)
    
    # Requirements
    prerequisites: List[str] = field(default_factory=list)
    investment_required: float = 0.0
    skills_needed: List[str] = field(default_factory=list)
    
    # Success metrics
    success_indicators: List[str] = field(default_factory=list)
    measurement_methods: List[str] = field(default_factory=list)


class BusinessIntentAnalyzer:
    """
    Specialized analyzer for business and monetization intents
    
    Provides deep analysis of business-related intentions including:
    - Revenue stream optimization
    - Monetization strategy analysis
    - Partnership opportunity identification
    - Financial planning assistance
    - Compliance and legal considerations
    """
    
    def __init__(self, config: IntentRecognitionConfig):
        self.config = config
        self.business_patterns = self._initialize_business_patterns()
        self.revenue_stream_keywords = self._initialize_revenue_keywords()
        self.priority_indicators = self._initialize_priority_indicators()
        self.market_data = self._load_market_data()
    
    def _initialize_business_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize business-related pattern matching"""
        return {
            "monetization": re.compile(
                r'\b(monetize|revenue|income|earnings|profit|money|financial|payment)\b',
                re.IGNORECASE
            ),
            "partnerships": re.compile(
                r'\b(partnership|collaboration|sponsor|brand|deal|contract|agreement)\b',
                re.IGNORECASE
            ),
            "licensing": re.compile(
                r'\b(license|licensing|rights|copyright|royalty|usage|permission)\b',
                re.IGNORECASE
            ),
            "subscriptions": re.compile(
                r'\b(subscription|subscriber|recurring|monthly|premium|tier|membership)\b',
                re.IGNORECASE
            ),
            "marketplace": re.compile(
                r'\b(sell|selling|marketplace|store|shop|commerce|purchase|buy)\b',
                re.IGNORECASE
            ),
            "analytics": re.compile(
                r'\b(analytics|metrics|performance|roi|conversion|tracking|dashboard)\b',
                re.IGNORECASE
            ),
            "tax_legal": re.compile(
                r'\b(tax|taxes|legal|compliance|regulation|filing|deduction|invoice)\b',
                re.IGNORECASE
            ),
            "urgency": re.compile(
                r'\b(urgent|asap|deadline|immediately|quickly|rush|priority|critical)\b',
                re.IGNORECASE
            )
        }
    
    def _initialize_revenue_keywords(self) -> Dict[RevenueStreamType, List[str]]:
        """Initialize revenue stream specific keywords"""
        return {
            RevenueStreamType.STREAMING_ROYALTIES: [
                "spotify", "streaming", "royalties", "streams", "plays", "listens"
            ],
            RevenueStreamType.BRAND_SPONSORSHIPS: [
                "sponsor", "sponsorship", "brand", "endorsement", "campaign", "ambassador"
            ],
            RevenueStreamType.MERCHANDISE_SALES: [
                "merch", "merchandise", "t-shirt", "products", "store", "shop"
            ],
            RevenueStreamType.LIVE_PERFORMANCES: [
                "concert", "performance", "gig", "show", "tour", "live", "venue"
            ],
            RevenueStreamType.DIGITAL_PRODUCTS: [
                "digital", "download", "ebook", "course", "template", "preset"
            ],
            RevenueStreamType.SUBSCRIPTION_REVENUE: [
                "subscription", "patreon", "recurring", "monthly", "premium", "tier"
            ],
            RevenueStreamType.AFFILIATE_MARKETING: [
                "affiliate", "commission", "referral", "partnership", "link"
            ],
            RevenueStreamType.LICENSING_FEES: [
                "license", "licensing", "sync", "usage", "rights", "permission"
            ]
        }
    
    def _initialize_priority_indicators(self) -> Dict[BusinessPriority, List[str]]:
        """Initialize priority level indicators"""
        return {
            BusinessPriority.CRITICAL: [
                "urgent", "critical", "emergency", "immediately", "asap", "deadline"
            ],
            BusinessPriority.HIGH: [
                "important", "priority", "soon", "quickly", "high", "significant"
            ],
            BusinessPriority.MEDIUM: [
                "moderate", "standard", "normal", "regular", "medium"
            ],
            BusinessPriority.LOW: [
                "low", "later", "eventually", "when possible", "minor"
            ],
            BusinessPriority.OPPORTUNITY: [
                "opportunity", "potential", "explore", "consider", "possibility"
            ]
        }
    
    def _load_market_data(self) -> Dict[str, Any]:
        """Load market data and trends (simplified for demo)"""
        return {
            "creator_economy_size": 104_000_000_000,  # $104B
            "average_creator_income": {
                "musician": 35000,
                "influencer": 42000,
                "photographer": 28000,
                "blogger": 31000
            },
            "platform_revenue_shares": {
                "spotify": 0.003,  # per stream
                "youtube": 0.55,   # revenue share
                "instagram": 0.45, # brand partnership
                "tiktok": 0.02     # creator fund
            },
            "trending_revenue_streams": [
                "nft_sales", "course_sales", "subscription_revenue", "brand_partnerships"
            ]
        }
    
    def analyze_business_intent(
        self,
        message_text: str,
        user_profile: Dict[str, Any],
        conversation_context: Dict[str, Any],
        current_business_state: Optional[Dict[str, Any]] = None
    ) -> BusinessIntentAnalysis:
        """
        Analyze business-related intent with comprehensive context
        
        Args:
            message_text: User's message
            user_profile: User profile information
            conversation_context: Conversation context
            current_business_state: Current business metrics and state
            
        Returns:
            BusinessIntentAnalysis: Comprehensive business intent analysis
        """
        try:
            # Identify primary business category
            business_category = self._identify_business_category(message_text)
            
            # Identify revenue stream type
            revenue_stream_type = self._identify_revenue_stream(message_text, user_profile)
            
            # Assess priority level
            priority_level = self._assess_priority_level(message_text, conversation_context)
            
            # Calculate financial implications
            financial_analysis = self._analyze_financial_implications(
                business_category, revenue_stream_type, user_profile, current_business_state
            )
            
            # Assess timeline and urgency
            timeline_analysis = self._analyze_timeline_urgency(message_text, business_category)
            
            # Market context analysis
            market_analysis = self._analyze_market_context(
                business_category, revenue_stream_type, user_profile
            )
            
            # Risk assessment
            risk_analysis = self._assess_business_risks(
                business_category, revenue_stream_type, current_business_state
            )
            
            # Generate recommendations
            recommendations = self._generate_business_recommendations(
                business_category, revenue_stream_type, financial_analysis, 
                market_analysis, user_profile
            )
            
            return BusinessIntentAnalysis(
                business_category=business_category,
                revenue_stream_type=revenue_stream_type,
                priority_level=priority_level,
                potential_revenue_impact=financial_analysis["revenue_impact"],
                cost_implications=financial_analysis["cost_implications"],
                roi_estimate=financial_analysis["roi_estimate"],
                estimated_timeline=timeline_analysis["timeline"],
                urgency_score=timeline_analysis["urgency_score"],
                deadline_pressure=timeline_analysis["deadline_pressure"],
                market_opportunity_score=market_analysis["opportunity_score"],
                competitive_analysis=market_analysis["competitive_analysis"],
                seasonal_relevance=market_analysis["seasonal_relevance"],
                risk_factors=risk_analysis["risk_factors"],
                mitigation_strategies=risk_analysis["mitigation_strategies"],
                compliance_requirements=risk_analysis["compliance_requirements"],
                business_recommendations=recommendations["recommendations"],
                next_steps=recommendations["next_steps"],
                required_resources=recommendations["required_resources"]
            )
            
        except Exception as e:
            logger.error(f"Business intent analysis failed: {e}")
            raise BusinessAnalysisError(f"Analysis failed: {e}")
    
    def _identify_business_category(self, message_text: str) -> BusinessIntentCategory:
        """Identify the primary business category from message"""
        text_lower = message_text.lower()
        
        # Check for specific business patterns
        if self.business_patterns["monetization"].search(text_lower):
            if "subscription" in text_lower or "recurring" in text_lower:
                return BusinessIntentCategory.SUBSCRIPTION_MANAGEMENT
            elif "track" in text_lower or "analytics" in text_lower:
                return BusinessIntentCategory.REVENUE_TRACKING
            else:
                return BusinessIntentCategory.MONETIZATION
        
        elif self.business_patterns["partnerships"].search(text_lower):
            return BusinessIntentCategory.BRAND_PARTNERSHIPS
        
        elif self.business_patterns["licensing"].search(text_lower):
            if "rights" in text_lower or "copyright" in text_lower:
                return BusinessIntentCategory.INTELLECTUAL_PROPERTY
            else:
                return BusinessIntentCategory.CONTENT_LICENSING
        
        elif self.business_patterns["subscriptions"].search(text_lower):
            return BusinessIntentCategory.SUBSCRIPTION_MANAGEMENT
        
        elif self.business_patterns["analytics"].search(text_lower):
            return BusinessIntentCategory.REVENUE_TRACKING
        
        elif self.business_patterns["tax_legal"].search(text_lower):
            if "contract" in text_lower:
                return BusinessIntentCategory.CONTRACT_MANAGEMENT
            else:
                return BusinessIntentCategory.TAX_REPORTING
        
        else:
            # Default categorization
            return BusinessIntentCategory.MONETIZATION
    
    def _identify_revenue_stream(
        self, 
        message_text: str, 
        user_profile: Dict[str, Any]
    ) -> Optional[RevenueStreamType]:
        """Identify the specific revenue stream type"""
        text_lower = message_text.lower()
        
        # Check each revenue stream type
        for stream_type, keywords in self.revenue_stream_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return stream_type
        
        # Fallback based on user profile
        creator_type = user_profile.get("creator_type", "")
        if creator_type == "musician":
            return RevenueStreamType.STREAMING_ROYALTIES
        elif creator_type == "influencer":
            return RevenueStreamType.BRAND_SPONSORSHIPS
        elif creator_type == "photographer":
            return RevenueStreamType.LICENSING_FEES
        
        return None
    
    def _assess_priority_level(
        self, 
        message_text: str, 
        conversation_context: Dict[str, Any]
    ) -> BusinessPriority:
        """Assess the priority level of the business intent"""
        text_lower = message_text.lower()
        
        # Check for priority indicators
        for priority, indicators in self.priority_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    return priority
        
        # Consider conversation context
        urgency_indicators = conversation_context.get("urgency_indicators", 0)
        if urgency_indicators > 2:
            return BusinessPriority.HIGH
        elif urgency_indicators > 0:
            return BusinessPriority.MEDIUM
        
        return BusinessPriority.MEDIUM
    
    def _analyze_financial_implications(
        self,
        business_category: BusinessIntentCategory,
        revenue_stream_type: Optional[RevenueStreamType],
        user_profile: Dict[str, Any],
        current_business_state: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Analyze financial implications of the business intent"""
        
        creator_type = user_profile.get("creator_type", "unknown")
        follower_count = user_profile.get("total_followers", 1000)
        
        # Base revenue potential calculation
        base_revenue = self.market_data["average_creator_income"].get(creator_type, 30000)
        
        # Revenue impact estimation
        revenue_impact = 0.0
        if revenue_stream_type:
            stream_multipliers = {
                RevenueStreamType.BRAND_SPONSORSHIPS: 0.3,
                RevenueStreamType.SUBSCRIPTION_REVENUE: 0.25,
                RevenueStreamType.LICENSING_FEES: 0.2,
                RevenueStreamType.MERCHANDISE_SALES: 0.15,
                RevenueStreamType.STREAMING_ROYALTIES: 0.1
            }
            
            multiplier = stream_multipliers.get(revenue_stream_type, 0.1)
            revenue_impact = base_revenue * multiplier * (follower_count / 10000)
        
        # Cost implications
        cost_implications = revenue_impact * 0.2  # Assume 20% cost
        
        # ROI estimation
        roi_estimate = (revenue_impact - cost_implications) / max(cost_implications, 1)
        
        return {
            "revenue_impact": revenue_impact,
            "cost_implications": cost_implications,
            "roi_estimate": roi_estimate
        }
    
    def _analyze_timeline_urgency(
        self, 
        message_text: str, 
        business_category: BusinessIntentCategory
    ) -> Dict[str, Any]:
        """Analyze timeline and urgency factors"""
        
        # Default timelines by category
        category_timelines = {
            BusinessIntentCategory.PAYMENT_PROCESSING: timedelta(days=1),
            BusinessIntentCategory.TAX_REPORTING: timedelta(days=30),
            BusinessIntentCategory.BRAND_PARTNERSHIPS: timedelta(days=14),
            BusinessIntentCategory.CONTENT_LICENSING: timedelta(days=7),
            BusinessIntentCategory.SUBSCRIPTION_MANAGEMENT: timedelta(days=3),
            BusinessIntentCategory.REVENUE_TRACKING: timedelta(days=1),
            BusinessIntentCategory.MONETIZATION: timedelta(days=7)
        }
        
        timeline = category_timelines.get(business_category, timedelta(days=7))
        
        # Urgency scoring
        urgency_score = 0.5
        deadline_pressure = False
        
        if self.business_patterns["urgency"].search(message_text.lower()):
            urgency_score = 0.9
            deadline_pressure = True
            timeline = timeline / 2  # Halve the timeline for urgent requests
        
        return {
            "timeline": timeline,
            "urgency_score": urgency_score,
            "deadline_pressure": deadline_pressure
        }
    
    def _analyze_market_context(
        self,
        business_category: BusinessIntentCategory,
        revenue_stream_type: Optional[RevenueStreamType],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze market context and opportunities"""
        
        # Market opportunity scoring
        opportunity_score = 0.5
        
        if revenue_stream_type and revenue_stream_type.value in self.market_data["trending_revenue_streams"]:
            opportunity_score += 0.3
        
        # Seasonal relevance (simplified)
        current_month = datetime.now().month
        seasonal_relevance = 0.5
        
        # Holiday seasons are good for merchandise
        if revenue_stream_type == RevenueStreamType.MERCHANDISE_SALES and current_month in [11, 12]:
            seasonal_relevance = 0.9
        
        # Competition analysis (simplified)
        creator_type = user_profile.get("creator_type", "")
        competitive_analysis = {
            "market_saturation": "medium",
            "barriers_to_entry": "low",
            "competitive_advantages": []
        }
        
        return {
            "opportunity_score": opportunity_score,
            "competitive_analysis": competitive_analysis,
            "seasonal_relevance": seasonal_relevance
        }
    
    def _assess_business_risks(
        self,
        business_category: BusinessIntentCategory,
        revenue_stream_type: Optional[RevenueStreamType],
        current_business_state: Optional[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Assess business risks and compliance requirements"""
        
        risk_factors = []
        mitigation_strategies = []
        compliance_requirements = []
        
        # Category-specific risks
        if business_category == BusinessIntentCategory.BRAND_PARTNERSHIPS:
            risk_factors.extend([
                "Brand alignment mismatch",
                "Contract disputes",
                "Payment delays"
            ])
            mitigation_strategies.extend([
                "Thorough brand vetting process",
                "Clear contract terms",
                "Payment milestone structure"
            ])
            compliance_requirements.extend([
                "FTC disclosure requirements",
                "Tax reporting obligations"
            ])
        
        elif business_category == BusinessIntentCategory.CONTENT_LICENSING:
            risk_factors.extend([
                "Copyright infringement claims",
                "Unauthorized usage",
                "Licensing term violations"
            ])
            mitigation_strategies.extend([
                "Comprehensive licensing agreements",
                "Regular usage monitoring",
                "Legal review of terms"
            ])
            compliance_requirements.extend([
                "Copyright registration",
                "DMCA compliance"
            ])
        
        # Revenue stream specific risks
        if revenue_stream_type == RevenueStreamType.SUBSCRIPTION_REVENUE:
            risk_factors.append("Subscription churn")
            mitigation_strategies.append("Regular content quality maintenance")
            compliance_requirements.append("Recurring payment regulations")
        
        return {
            "risk_factors": risk_factors,
            "mitigation_strategies": mitigation_strategies,
            "compliance_requirements": compliance_requirements
        }
    
    def _generate_business_recommendations(
        self,
        business_category: BusinessIntentCategory,
        revenue_stream_type: Optional[RevenueStreamType],
        financial_analysis: Dict[str, float],
        market_analysis: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate business recommendations and next steps"""
        
        recommendations = []
        next_steps = []
        required_resources = []
        
        # Category-specific recommendations
        if business_category == BusinessIntentCategory.MONETIZATION:
            if financial_analysis["roi_estimate"] > 2.0:
                recommendations.append("High ROI opportunity - prioritize implementation")
                next_steps.append("Develop detailed implementation plan")
            else:
                recommendations.append("Consider optimization strategies before implementation")
                next_steps.append("Analyze cost reduction opportunities")
        
        elif business_category == BusinessIntentCategory.BRAND_PARTNERSHIPS:
            recommendations.extend([
                "Build comprehensive brand partnership portfolio",
                "Focus on brand alignment and audience match"
            ])
            next_steps.extend([
                "Create brand partnership pitch deck",
                "Research potential brand partners"
            ])
            required_resources.extend([
                "Media kit preparation",
                "Analytics dashboard access"
            ])
        
        # Revenue stream specific recommendations
        if revenue_stream_type == RevenueStreamType.SUBSCRIPTION_REVENUE:
            recommendations.append("Develop tiered subscription model")
            next_steps.append("Survey audience for subscription preferences")
            required_resources.append("Subscription platform integration")
        
        # Market-based recommendations
        if market_analysis["opportunity_score"] > 0.7:
            recommendations.append("Strong market opportunity - fast-track implementation")
            next_steps.append("Allocate additional resources for quick market entry")
        
        return {
            "recommendations": recommendations,
            "next_steps": next_steps,
            "required_resources": required_resources
        }
    
    def identify_monetization_opportunities(
        self,
        user_profile: Dict[str, Any],
        current_revenue_streams: List[str],
        audience_metrics: Dict[str, Any]
    ) -> List[MonetizationOpportunity]:
        """Identify potential monetization opportunities"""
        
        opportunities = []
        creator_type = user_profile.get("creator_type", "")
        follower_count = audience_metrics.get("total_followers", 0)
        engagement_rate = audience_metrics.get("engagement_rate", 0.03)
        
        # Subscription opportunity
        if "subscription_revenue" not in current_revenue_streams and follower_count > 1000:
            potential_revenue = follower_count * 0.05 * 10  # 5% conversion at $10/month
            
            opportunities.append(MonetizationOpportunity(
                opportunity_type=RevenueStreamType.SUBSCRIPTION_REVENUE,
                potential_revenue=potential_revenue * 12,  # Annual
                implementation_effort="medium",
                time_to_market=timedelta(days=30),
                market_demand=0.8,
                competition_level="high",
                prerequisites=["Content strategy", "Platform integration"],
                investment_required=1000,
                skills_needed=["Content planning", "Community management"],
                success_indicators=["Subscriber growth", "Retention rate"]
            ))
        
        # Brand partnership opportunity
        if engagement_rate > 0.03 and follower_count > 5000:
            potential_revenue = follower_count * 0.01 * 12  # $0.01 per follower per campaign
            
            opportunities.append(MonetizationOpportunity(
                opportunity_type=RevenueStreamType.BRAND_SPONSORSHIPS,
                potential_revenue=potential_revenue,
                implementation_effort="low",
                time_to_market=timedelta(days=14),
                market_demand=0.9,
                competition_level="high",
                prerequisites=["Media kit", "Portfolio"],
                investment_required=0,
                skills_needed=["Negotiation", "Content creation"],
                success_indicators=["Partnership count", "Campaign performance"]
            ))
        
        # Merchandise opportunity for established creators
        if follower_count > 10000 and engagement_rate > 0.05:
            potential_revenue = follower_count * 0.02 * 25  # 2% conversion at $25 average
            
            opportunities.append(MonetizationOpportunity(
                opportunity_type=RevenueStreamType.MERCHANDISE_SALES,
                potential_revenue=potential_revenue,
                implementation_effort="high",
                time_to_market=timedelta(days=60),
                market_demand=0.6,
                competition_level="medium",
                prerequisites=["Design resources", "E-commerce platform"],
                investment_required=5000,
                skills_needed=["Product design", "Inventory management"],
                success_indicators=["Sales volume", "Profit margins"]
            ))
        
        return sorted(opportunities, key=lambda x: x.potential_revenue, reverse=True)
    
    def calculate_revenue_projections(
        self,
        revenue_stream_type: RevenueStreamType,
        user_metrics: Dict[str, Any],
        market_conditions: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate revenue projections for specific revenue streams"""
        
        projections = {
            "conservative": 0.0,
            "realistic": 0.0,
            "optimistic": 0.0,
            "confidence_interval": 0.0
        }
        
        followers = user_metrics.get("followers", 1000)
        engagement_rate = user_metrics.get("engagement_rate", 0.03)
        
        if revenue_stream_type == RevenueStreamType.BRAND_SPONSORSHIPS:
            base_rate = followers * 0.005  # $0.005 per follower base rate
            
            projections["conservative"] = base_rate * 0.7 * 6  # 6 campaigns/year
            projections["realistic"] = base_rate * 1.0 * 12    # 12 campaigns/year
            projections["optimistic"] = base_rate * 1.5 * 24   # 24 campaigns/year
            projections["confidence_interval"] = 0.7
        
        elif revenue_stream_type == RevenueStreamType.SUBSCRIPTION_REVENUE:
            conversion_rate = min(0.1, engagement_rate * 2)  # Up to 10% conversion
            monthly_price = 10
            
            projections["conservative"] = followers * conversion_rate * 0.5 * monthly_price * 12
            projections["realistic"] = followers * conversion_rate * monthly_price * 12
            projections["optimistic"] = followers * conversion_rate * 1.5 * monthly_price * 12
            projections["confidence_interval"] = 0.6
        
        return projections
