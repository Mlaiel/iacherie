"""
Response Processor

Advanced response processing and analysis system for DMCA takedown notices
with intelligent response interpretation and automated follow-up coordination.

Author: Fahed Mlaiel
Email: mlaiel@live.de

 COPYRIGHT WARNING 
Unauthorized copying or distribution prohibited. All rights reserved © 2025 Fahed Mlaiel
"""

import asyncio
import logging
import uuid
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from ...core.database import get_database
from ...core.exceptions import ContentProtectionError
from ...utils.nlp import NLPProcessor
from ...utils.sentiment import SentimentAnalyzer
from ..models import PlatformResponse, ResponseAnalysis

logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Types of platform responses"""
    ACKNOWLEDGMENT = "acknowledgment"
    COMPLIANCE = "compliance"
    PARTIAL_COMPLIANCE = "partial_compliance"
    REJECTION = "rejection"
    COUNTER_NOTICE = "counter_notice"
    REQUEST_MORE_INFO = "request_more_info"
    AUTOMATED_RESPONSE = "automated_response"
    ESCALATION_NOTICE = "escalation_notice"
    LEGAL_RESPONSE = "legal_response"


class ResponseStatus(Enum):
    """Response processing status"""
    PENDING = "pending"
    PROCESSED = "processed"
    REQUIRES_ACTION = "requires_action"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    DISPUTED = "disputed"


class SentimentType(Enum):
    """Response sentiment classification"""
    COOPERATIVE = "cooperative"
    NEUTRAL = "neutral"
    DEFENSIVE = "defensive"
    HOSTILE = "hostile"
    CONFUSED = "confused"


@dataclass
class ResponseClassification:
    """Response classification result"""
    response_type: ResponseType
    confidence_score: float
    sentiment: SentimentType
    urgency_level: int
    requires_human_review: bool
    key_phrases: List[str]
    identified_actions: List[str]
    legal_implications: List[str]


@dataclass
class ActionRecommendation:
    """Recommended action based on response"""
    action_type: str
    priority: int
    description: str
    timeline: timedelta
    resources_required: List[str]
    success_probability: float
    cost_estimate: Optional[float] = None


class ResponseProcessor:
    """
    Advanced response processing system for DMCA takedown responses
    
    Features:
    - Intelligent response classification
    - Sentiment analysis
    - Legal implication assessment
    - Automated action recommendations
    - Multi-language support
    - Pattern recognition
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize response processor"""
        self.config = config or {}
        self.db = get_database()
        self.nlp_processor = NLPProcessor(config)
        self.sentiment_analyzer = SentimentAnalyzer(config)
        self.logger = logger
        
        # Response patterns for classification
        self.response_patterns = {
            ResponseType.ACKNOWLEDGMENT: [
                r'received.*notice', r'acknowledgment', r'confirmed.*receipt',
                r'reviewing.*request', r'thank.*you.*for.*reporting'
            ],
            ResponseType.COMPLIANCE: [
                r'content.*removed', r'taken.*down', r'disabled.*access',
                r'complied.*with.*request', r'action.*has.*been.*taken'
            ],
            ResponseType.PARTIAL_COMPLIANCE: [
                r'some.*content.*removed', r'partially.*addressed',
                r'limited.*action.*taken', r'selective.*removal'
            ],
            ResponseType.REJECTION: [
                r'request.*denied', r'invalid.*claim', r'insufficient.*evidence',
                r'not.*infringing', r'legitimate.*use', r'fair.*use'
            ],
            ResponseType.COUNTER_NOTICE: [
                r'counter.*notification', r'disputes.*claim', r'dmca.*counter',
                r'believes.*use.*is.*authorized', r'good.*faith.*belief.*mistake'
            ],
            ResponseType.REQUEST_MORE_INFO: [
                r'need.*more.*information', r'additional.*details.*required',
                r'please.*provide', r'clarification.*needed', r'incomplete.*notice'
            ]
        }
        
        # Sentiment indicators
        self.sentiment_indicators = {
            SentimentType.COOPERATIVE: [
                'happy to help', 'working with you', 'appreciate your patience',
                'committed to resolving', 'take this seriously'
            ],
            SentimentType.NEUTRAL: [
                'standard procedure', 'following policy', 'in accordance with',
                'as per guidelines', 'normal process'
            ],
            SentimentType.DEFENSIVE: [
                'however', 'but we believe', 'dispute this claim',
                'not convinced', 'question the validity'
            ],
            SentimentType.HOSTILE: [
                'frivolous claim', 'bad faith', 'harassment',
                'abuse of process', 'will pursue legal action'
            ]
        }
        
        # Legal implication keywords
        self.legal_keywords = {
            'counter_claim_risk': ['counter-claim', 'sue', 'legal action', 'attorney'],
            'fair_use_defense': ['fair use', 'fair dealing', 'educational use', 'commentary'],
            'jurisdictional_issues': ['jurisdiction', 'applicable law', 'governing law'],
            'authenticity_challenge': ['prove ownership', 'evidence of copyright', 'registration'],
            'procedural_issues': ['improper notice', 'technical deficiency', 'format requirements']
        }
    
    async def process_platform_response(self, 
                                      response_data: Dict[str, Any],
                                      notice_id: str,
                                      platform_id: str) -> Dict[str, Any]:
        """
        Process and analyze platform response to DMCA notice
        
        Args:
            response_data: Raw response data from platform
            notice_id: ID of the original notice
            platform_id: Platform that sent the response
            
        Returns:
            Comprehensive response analysis result
        """



        try:
            self.logger.info(f"Processing platform response for notice: {notice_id}")
            
            # Extract response content
            response_content = await self._extract_response_content(response_data)
            
            # Classify response type
            classification = await self._classify_response(response_content, platform_id)
            
            # Analyze legal implications
            legal_analysis = await self._analyze_legal_implications(response_content, classification)
            
            # Generate action recommendations
            recommendations = await self._generate_action_recommendations(
                classification, legal_analysis, notice_id
            )
            
            # Calculate compliance metrics
            compliance_metrics = await self._calculate_compliance_metrics(
                classification, response_data
            )
            
            # Create response analysis record
            analysis = ResponseAnalysis(
                analysis_id=str(uuid.uuid4()),
                notice_id=notice_id,
                platform_id=platform_id,
                response_type=classification.response_type,
                classification=classification,
                legal_analysis=legal_analysis,
                recommendations=recommendations,
                compliance_metrics=compliance_metrics,
                processed_at=datetime.now(timezone.utc),
                metadata={
                    'raw_response': response_data,
                    'processing_version': '2.0',
                    'nlp_confidence': classification.confidence_score
                }
            )
            
            # Store analysis
            await self._store_response_analysis(analysis)
            
            # Trigger automated actions if applicable
            automated_actions = await self._trigger_automated_actions(analysis)
            
            return {
                'success': True,
                'analysis_id': analysis.analysis_id,
                'response_type': classification.response_type.value,
                'sentiment': classification.sentiment.value,
                'confidence_score': classification.confidence_score,
                'requires_human_review': classification.requires_human_review,
                'legal_implications': legal_analysis,
                'recommended_actions': recommendations,
                'compliance_status': compliance_metrics['compliance_status'],
                'automated_actions_triggered': len(automated_actions),
                'next_steps': await self._determine_next_steps(analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Response processing failed: {str(e)}")
            raise ContentProtectionError(f"Response processing failed: {str(e)}")
    
    async def analyze_response_patterns(self, 
                                      platform_id: str,
                                      time_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """
        Analyze response patterns from a specific platform
        
        Args:
            platform_id: Platform to analyze
            time_range: Optional time range for analysis
            
        Returns:
            Platform response pattern analysis
        """



        try:
            self.logger.info(f"Analyzing response patterns for platform: {platform_id}")
            
            # Set default time range
            if not time_range:
                time_range = {
                    'start': datetime.now(timezone.utc) - timedelta(days=90),
                    'end': datetime.now(timezone.utc)
                }
            
            # Query historical responses
            responses = await self._query_platform_responses(platform_id, time_range)
            
            # Analyze response types distribution
            type_distribution = await self._analyze_response_type_distribution(responses)
            
            # Analyze sentiment trends
            sentiment_trends = await self._analyze_sentiment_trends(responses)
            
            # Analyze response times
            timing_analysis = await self._analyze_response_timing(responses)
            
            # Identify common patterns
            common_patterns = await self._identify_common_patterns(responses)
            
            # Calculate platform cooperation score
            cooperation_score = await self._calculate_cooperation_score(
                type_distribution, sentiment_trends
            )
            
            # Generate platform-specific recommendations
            platform_recommendations = await self._generate_platform_recommendations(
                type_distribution, sentiment_trends, timing_analysis
            )
            
            return {
                'platform_id': platform_id,
                'analysis_period': {
                    'start': time_range['start'].isoformat(),
                    'end': time_range['end'].isoformat()
                },
                'total_responses_analyzed': len(responses),
                'response_type_distribution': type_distribution,
                'sentiment_trends': sentiment_trends,
                'timing_analysis': timing_analysis,
                'common_patterns': common_patterns,
                'cooperation_score': cooperation_score,
                'platform_recommendations': platform_recommendations,
                'predictive_insights': await self._generate_predictive_insights(responses)
            }
            
        except Exception as e:
            self.logger.error(f"Response pattern analysis failed: {str(e)}")
            raise ContentProtectionError(f"Pattern analysis failed: {str(e)}")
    
    async def handle_counter_notice(self, 
                                  counter_notice_data: Dict[str, Any],
                                  original_notice_id: str) -> Dict[str, Any]:
        """
        Handle DMCA counter-notice response
        
        Args:
            counter_notice_data: Counter-notice information
            original_notice_id: ID of the original takedown notice
            
        Returns:
            Counter-notice handling result
        """



        try:
            self.logger.info(f"Handling counter-notice for original notice: {original_notice_id}")
            
            # Validate counter-notice format
            validation_result = await self._validate_counter_notice(counter_notice_data)
            
            # Analyze counter-notice claims
            claims_analysis = await self._analyze_counter_claims(counter_notice_data)
            
            # Assess response strategy options
            strategy_options = await self._assess_counter_notice_strategies(
                claims_analysis, original_notice_id
            )
            
            # Generate legal assessment
            legal_assessment = await self._generate_counter_notice_legal_assessment(
                counter_notice_data, claims_analysis
            )
            
            # Calculate response timeline
            response_timeline = await self._calculate_counter_notice_timeline(validation_result)
            
            # Create counter-notice record
            counter_notice_id = str(uuid.uuid4())
            await self._store_counter_notice_record(
                counter_notice_id, counter_notice_data, original_notice_id,
                validation_result, claims_analysis
            )
            
            # Determine if legal counsel is required
            legal_counsel_required = await self._assess_legal_counsel_requirement(
                claims_analysis, legal_assessment
            )
            
            return {
                'success': True,
                'counter_notice_id': counter_notice_id,
                'original_notice_id': original_notice_id,
                'validation_result': validation_result,
                'claims_analysis': claims_analysis,
                'strategy_options': strategy_options,
                'legal_assessment': legal_assessment,
                'response_timeline': response_timeline,
                'legal_counsel_required': legal_counsel_required,
                'recommended_action': strategy_options[0] if strategy_options else None,
                'urgency_level': claims_analysis.get('urgency_level', 'medium')
            }
            
        except Exception as e:
            self.logger.error(f"Counter-notice handling failed: {str(e)}")
            raise ContentProtectionError(f"Counter-notice handling failed: {str(e)}")
    
    async def generate_response_summary(self, 
                                      notice_ids: List[str]) -> Dict[str, Any]:
        """
        Generate comprehensive response summary for multiple notices
        
        Args:
            notice_ids: List of notice IDs to summarize
            
        Returns:
            Comprehensive response summary
        """



        try:
            self.logger.info(f"Generating response summary for {len(notice_ids)} notices")
            
            # Retrieve response analyses
            analyses = await self._get_response_analyses(notice_ids)
            
            # Calculate overall metrics
            overall_metrics = await self._calculate_overall_metrics(analyses)
            
            # Analyze success patterns
            success_patterns = await self._analyze_success_patterns(analyses)
            
            # Identify problem areas
            problem_areas = await self._identify_problem_areas(analyses)
            
            # Generate improvement recommendations
            improvements = await self._generate_improvement_recommendations(
                overall_metrics, success_patterns, problem_areas
            )
            
            return {
                'summary_id': str(uuid.uuid4()),
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'notices_analyzed': len(notice_ids),
                'overall_metrics': overall_metrics,
                'success_patterns': success_patterns,
                'problem_areas': problem_areas,
                'improvement_recommendations': improvements,
                'performance_summary': {
                    'total_responses': len(analyses),
                    'compliance_rate': overall_metrics.get('compliance_rate', 0.0),
                    'avg_response_time': overall_metrics.get('avg_response_time', 0),
                    'cooperation_score': overall_metrics.get('cooperation_score', 0.0),
                    'escalation_rate': overall_metrics.get('escalation_rate', 0.0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Response summary generation failed: {str(e)}")
            raise ContentProtectionError(f"Summary generation failed: {str(e)}")
    
    # Private helper methods
    
    async def _extract_response_content(self, response_data: Dict[str, Any]) -> str:
        """Extract textual content from response data"""
        # Extract from various possible fields
        content_fields = ['message', 'body', 'content', 'text', 'response', 'reply']
        
        for field in content_fields:
            if field in response_data and response_data[field]:
                return str(response_data[field])
        
        # If no specific field, try to extract from the entire response
        if isinstance(response_data, dict):
            # Concatenate all string values
            text_parts = []
            for key, value in response_data.items():
                if isinstance(value, str) and len(value) > 10:  # Filter out short values
                    text_parts.append(value)
            return " ".join(text_parts)
        
        return str(response_data)
    
    async def _classify_response(self, 
                               content: str,
                               platform_id: str) -> ResponseClassification:
        """Classify response using pattern matching and NLP"""
        content_lower = content.lower()
        
        # Pattern-based classification
        pattern_scores = {}
        for response_type, patterns in self.response_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    score += 1
            pattern_scores[response_type] = score / len(patterns)
        
        # Find best match
        best_type = max(pattern_scores, key=pattern_scores.get)
        confidence = pattern_scores[best_type]
        
        # Enhance with NLP if confidence is low
        if confidence < 0.3:
            nlp_result = await self.nlp_processor.classify_text(content, {
                'categories': [rt.value for rt in ResponseType],
                'context': 'dmca_response'
            })
            best_type = ResponseType(nlp_result.get('category', best_type.value))
            confidence = max(confidence, nlp_result.get('confidence', 0.0))
        
        # Analyze sentiment
        sentiment = await self._analyze_response_sentiment(content)
        
        # Determine urgency and review requirements
        urgency_level = await self._calculate_urgency_level(content, best_type)
        requires_review = await self._requires_human_review(content, best_type, confidence)
        
        # Extract key phrases
        key_phrases = await self._extract_key_phrases(content)
        
        # Identify potential actions
        actions = await self._identify_mentioned_actions(content)
        
        # Assess legal implications
        legal_implications = await self._identify_legal_implications(content)
        
        return ResponseClassification(
            response_type=best_type,
            confidence_score=confidence,
            sentiment=sentiment,
            urgency_level=urgency_level,
            requires_human_review=requires_review,
            key_phrases=key_phrases,
            identified_actions=actions,
            legal_implications=legal_implications
        )
    
    async def _analyze_response_sentiment(self, content: str) -> SentimentType:
        """Analyze sentiment of response"""
        content_lower = content.lower()
        
        # Check for specific sentiment indicators
        for sentiment, indicators in self.sentiment_indicators.items():
            for indicator in indicators:
                if indicator in content_lower:
                    return sentiment
        
        # Use sentiment analyzer for more sophisticated analysis
        sentiment_result = await self.sentiment_analyzer.analyze(content)
        
        # Map sentiment score to our categories
        sentiment_score = sentiment_result.get('score', 0.0)
        if sentiment_score > 0.5:
            return SentimentType.COOPERATIVE
        elif sentiment_score > 0.1:
            return SentimentType.NEUTRAL
        elif sentiment_score > -0.3:
            return SentimentType.DEFENSIVE
        else:
            return SentimentType.HOSTILE
    
    async def _analyze_legal_implications(self, 
                                        content: str,
                                        classification: ResponseClassification) -> Dict[str, Any]:
        """Analyze legal implications of response"""
        content_lower = content.lower()
        implications = {}
        
        # Check for specific legal keywords
        for implication_type, keywords in self.legal_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    if implication_type not in implications:
                        implications[implication_type] = []
                    implications[implication_type].append(keyword)
        
        # Assess risk levels
        risk_assessment = {
            'overall_risk': 'low',
            'counter_claim_risk': 'low',
            'litigation_risk': 'low',
            'compliance_risk': 'low'
        }
        
        # Adjust risk based on response type and sentiment
        if classification.response_type == ResponseType.COUNTER_NOTICE:
            risk_assessment['counter_claim_risk'] = 'high'
            risk_assessment['overall_risk'] = 'medium'
        
        if classification.response_type == ResponseType.REJECTION:
            risk_assessment['compliance_risk'] = 'medium'
            
        if classification.sentiment == SentimentType.HOSTILE:
            risk_assessment['litigation_risk'] = 'medium'
            risk_assessment['overall_risk'] = 'medium'
        
        return {
            'identified_implications': implications,
            'risk_assessment': risk_assessment,
            'legal_review_required': len(implications) > 0 or classification.sentiment == SentimentType.HOSTILE,
            'potential_defenses': await self._identify_potential_defenses(content),
            'jurisdictional_issues': 'jurisdiction' in content_lower or 'governing law' in content_lower
        }
    
    async def _generate_action_recommendations(self, 
                                             classification: ResponseClassification,
                                             legal_analysis: Dict[str, Any],
                                             notice_id: str) -> List[ActionRecommendation]:
        """Generate action recommendations based on analysis"""
        recommendations = []
        
        if classification.response_type == ResponseType.ACKNOWLEDGMENT:
            recommendations.append(ActionRecommendation(
                action_type='monitor_compliance',
                priority=2,
                description='Monitor for compliance within expected timeframe',
                timeline=timedelta(days=7),
                resources_required=['automated_monitoring'],
                success_probability=0.8
            ))
            
        elif classification.response_type == ResponseType.COMPLIANCE:
            recommendations.append(ActionRecommendation(
                action_type='verify_removal',
                priority=1,
                description='Verify that infringing content has been removed',
                timeline=timedelta(hours=24),
                resources_required=['content_verification'],
                success_probability=0.95
            ))
            
        elif classification.response_type == ResponseType.REJECTION:
            if legal_analysis['risk_assessment']['overall_risk'] == 'low':
                recommendations.append(ActionRecommendation(
                    action_type='send_clarification',
                    priority=2,
                    description='Send clarification notice with additional evidence',
                    timeline=timedelta(days=3),
                    resources_required=['legal_review', 'evidence_gathering'],
                    success_probability=0.6,
                    cost_estimate=200.0
                ))
            else:
                recommendations.append(ActionRecommendation(
                    action_type='legal_consultation',
                    priority=1,
                    description='Consult with legal counsel before proceeding',
                    timeline=timedelta(days=1),
                    resources_required=['legal_counsel'],
                    success_probability=0.4,
                    cost_estimate=500.0
                ))
                
        elif classification.response_type == ResponseType.COUNTER_NOTICE:
            recommendations.append(ActionRecommendation(
                action_type='evaluate_counter_notice',
                priority=1,
                description='Evaluate counter-notice and determine response strategy',
                timeline=timedelta(days=7),
                resources_required=['legal_counsel', 'evidence_review'],
                success_probability=0.3,
                cost_estimate=1000.0
            ))
            
        elif classification.response_type == ResponseType.REQUEST_MORE_INFO:
            recommendations.append(ActionRecommendation(
                action_type='provide_additional_info',
                priority=1,
                description='Provide requested additional information',
                timeline=timedelta(days=2),
                resources_required=['documentation', 'evidence_gathering'],
                success_probability=0.85,
                cost_estimate=100.0
            ))
        
        # Add escalation recommendation if needed
        if classification.requires_human_review:
            recommendations.append(ActionRecommendation(
                action_type='human_review',
                priority=1,
                description='Requires human review due to complexity or risk factors',
                timeline=timedelta(hours=4),
                resources_required=['legal_expert', 'case_manager'],
                success_probability=0.9,
                cost_estimate=150.0
            ))
        
        return recommendations
    
    async def _calculate_compliance_metrics(self, 
                                          classification: ResponseClassification,
                                          response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate compliance-related metrics"""
        # Determine compliance status
        if classification.response_type == ResponseType.COMPLIANCE:
            compliance_status = 'compliant'
        elif classification.response_type == ResponseType.PARTIAL_COMPLIANCE:
            compliance_status = 'partially_compliant'
        elif classification.response_type in [ResponseType.REJECTION, ResponseType.COUNTER_NOTICE]:
            compliance_status = 'non_compliant'
        else:
            compliance_status = 'pending'
        
        # Calculate response time if available
        response_time = None
        if 'timestamp' in response_data and 'original_timestamp' in response_data:
            response_time = (
                datetime.fromisoformat(response_data['timestamp']) - 
                datetime.fromisoformat(response_data['original_timestamp'])
            ).total_seconds() / 3600  # Hours
        
        return {
            'compliance_status': compliance_status,
            'response_time_hours': response_time,
            'cooperation_score': self._calculate_response_cooperation_score(classification),
            'quality_score': classification.confidence_score,
            'escalation_required': classification.requires_human_review,
            'legal_risk_level': self._assess_legal_risk_level(classification)
        }
    
    def _calculate_response_cooperation_score(self, classification: ResponseClassification) -> float:
        """Calculate cooperation score based on response characteristics"""
        base_score = 0.5
        
        # Adjust based on response type
        type_adjustments = {
            ResponseType.COMPLIANCE: 0.4,
            ResponseType.ACKNOWLEDGMENT: 0.2,
            ResponseType.PARTIAL_COMPLIANCE: 0.1,
            ResponseType.REQUEST_MORE_INFO: 0.0,
            ResponseType.REJECTION: -0.2,
            ResponseType.COUNTER_NOTICE: -0.3
        }
        
        base_score += type_adjustments.get(classification.response_type, 0.0)
        
        # Adjust based on sentiment
        sentiment_adjustments = {
            SentimentType.COOPERATIVE: 0.2,
            SentimentType.NEUTRAL: 0.0,
            SentimentType.DEFENSIVE: -0.1,
            SentimentType.HOSTILE: -0.3
        }
        
        base_score += sentiment_adjustments.get(classification.sentiment, 0.0)
        
        return max(0.0, min(1.0, base_score))
    
    def _assess_legal_risk_level(self, classification: ResponseClassification) -> str:
        """Assess legal risk level based on response"""
        if classification.response_type == ResponseType.COUNTER_NOTICE:
            return 'high'
        elif classification.response_type == ResponseType.REJECTION and classification.sentiment == SentimentType.HOSTILE:
            return 'medium'
        elif 'legal action' in classification.key_phrases:
            return 'high'
        else:
            return 'low'
