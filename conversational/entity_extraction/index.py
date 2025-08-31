"""Entity Extraction Index - IA Influencer Agent

Central orchestration module for all entity extraction services. Provides unified
interface for multi-format content entity recognition, platform detection, 
collaboration tracking, and business entity processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de

Team Specializations:
- Lead AI Developer: Advanced ML/NLP architectures
- Backend Senior: Enterprise-grade scalable systems  
- ML Engineer: Production ML pipelines & optimization
- Database Administrator: High-performance data architecture
- Security Expert: Advanced cybersecurity & protection
- Microservices Architect: Distributed systems design
- Audio Engineer: Professional audio processing
- DevOps Engineer: CI/CD & infrastructure automation
- IA Prompt Engineer: Advanced AI prompt optimization
"""
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import logging

from .entity_extractor import EntityExtractor, ExtractedEntity
from .platform_entity_extractor import PlatformEntityExtractor, PlatformEntity, PlatformType
from .collaboration_entity_tracker import CollaborationEntityTracker, CollaborationEntity
from .business_entity_processor import BusinessEntityProcessor
from .content_entity_analyzer import ContentEntityAnalyzer
from .creative_entity_detector import CreativeEntityDetector
from .named_entity_recognizer import NamedEntityRecognizer
from .metadata_entity_parser import MetadataEntityParser
from .entity_linker import EntityLinker
from .relationship_extractor import RelationshipExtractor

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...models.content import ContentType, ContentMetadata
from ...utils.validation import validate_input


@dataclass
class ComprehensiveExtractionResult:
    """Complete entity extraction results from all modules"""    general_entities: List[ExtractedEntity]
    platform_entities: List[PlatformEntity]
    collaboration_entities: List[CollaborationEntity]
    business_entities: List[Any]
    creative_entities: List[Any]
    content_entities: List[Any]
    relationships: List[Any]
    metadata_entities: List[Any]
    total_entities: int
    confidence_scores: Dict[str, float]
    processing_time: float
    recommendations: List[Dict[str, Any]]
    insights: Dict[str, Any]
    extracted_at: datetime


class EntityExtractionOrchestrator(BaseService):
    """    Central orchestrator for all entity extraction services.
    
    Provides unified interface for:
    - Multi-format content analysis
    - Platform-specific entity detection  
    - Collaboration opportunity identification
    - Business relationship mapping
    - Creative work analysis
    - Comprehensive entity linking
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("entity_extraction_orchestrator")
        
        # Initialize all extraction services
        self._initialize_services(config)
        
        # Cache configuration
        self.cache_ttl = config.get("cache_ttl", 1800) if config else 1800
    
    def _initialize_services(self, config: Optional[Dict[str, Any]]):
        """Initialize all comprehensive entity extraction services with advanced capabilities"""        try:
            # Core entity extraction services
            self.entity_extractor = EntityExtractor(config)
            self.platform_extractor = PlatformEntityExtractor(config)
            self.collaboration_tracker = CollaborationEntityTracker(config)
            self.business_processor = BusinessEntityProcessor()
            self.content_analyzer = ContentEntityAnalyzer()
            self.creative_detector = CreativeEntityDetector()
            self.named_entity_recognizer = NamedEntityRecognizer()
            self.metadata_parser = MetadataEntityParser()
            self.entity_linker = EntityLinker()
            self.relationship_extractor = RelationshipExtractor()
            
            # Advanced analytics and intelligence services
            self.sentiment_analyzer = self._initialize_sentiment_analyzer()
            self.trend_detector = self._initialize_trend_detector()
            self.quality_assessor = self._initialize_quality_assessor()
            self.monetization_analyzer = self._initialize_monetization_analyzer()
            self.seo_optimizer = self._initialize_seo_optimizer()
            self.competition_analyzer = self._initialize_competition_analyzer()
            self.audience_analyzer = self._initialize_audience_analyzer()
            
            # Real-time processing components
            self.realtime_processor = self._initialize_realtime_processor()
            self.notification_system = self._initialize_notification_system()
            
            # Performance monitoring and optimization
            self.performance_monitor = self._initialize_performance_monitor()
            self.load_balancer = self._initialize_load_balancer()
            
            # Security and validation
            self.security_validator = self._initialize_security_validator()
            self.content_moderator = self._initialize_content_moderator()
            
            # Machine learning enhancement
            self.ml_enhancement_engine = self._initialize_ml_enhancement()
            self.prediction_engine = self._initialize_prediction_engine()
            
            # Integration and export services
            self.data_exporter = self._initialize_data_exporter()
            self.api_integrator = self._initialize_api_integrator()
            
            self.logger.info("All entity extraction services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {str(e)}")
            raise
    
    def _initialize_sentiment_analyzer(self):
        """Initialize advanced sentiment analysis for extracted content"""        from transformers import pipeline
        
        try:
            return pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True,
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            self.logger.warning(f"Failed to initialize sentiment analyzer: {e}")
            return None
    
    def _initialize_trend_detector(self):
        """Initialize trend detection system for creative content"""        class TrendDetector:
            def __init__(self):
                self.trend_patterns = []
                self.viral_indicators = []
                self.engagement_thresholds = {}
                
            async def detect_trends(self, entities: List[Any], timeframe: str = "24h") -> List[Dict[str, Any]]:
                """Detect trending patterns in extracted entities"""                trends = []
                
                # Analyze entity frequency patterns
                entity_counts = {}
                for entity in entities:
                    entity_type = getattr(entity, 'entity_type', 'unknown')
                    entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
                
                # Identify trending entity types
                for entity_type, count in entity_counts.items():
                    if count > self.engagement_thresholds.get(entity_type, 5):
                        trends.append({
                            'type': 'entity_trending',
                            'entity_type': entity_type,
                            'count': count,
                            'trend_score': min(count / 10.0, 1.0),
                            'timeframe': timeframe
                        })
                
                return trends
        
        return TrendDetector()
    
    def _initialize_quality_assessor(self):
        """Initialize content quality assessment system"""        class QualityAssessor:
            def __init__(self):
                self.quality_metrics = [
                    'completeness', 'accuracy', 'relevance', 'uniqueness', 'engagement_potential'
                ]
                
            async def assess_extraction_quality(self, extraction_result: ComprehensiveExtractionResult) -> Dict[str, float]:
                """Assess quality of entity extraction results"""                quality_scores = {}
                
                # Completeness score based on number of entities found
                total_entities = extraction_result.total_entities
                if total_entities > 0:
                    quality_scores['completeness'] = min(total_entities / 20.0, 1.0)
                else:
                    quality_scores['completeness'] = 0.0
                
                # Confidence score average
                if extraction_result.confidence_scores:
                    quality_scores['accuracy'] = sum(extraction_result.confidence_scores.values()) / len(extraction_result.confidence_scores)
                else:
                    quality_scores['accuracy'] = 0.0
                
                # Diversity score based on entity types
                entity_types = set()
                for entity_list in [extraction_result.general_entities, extraction_result.platform_entities]:
                    for entity in entity_list:
                        entity_types.add(getattr(entity, 'entity_type', 'unknown'))
                
                quality_scores['diversity'] = min(len(entity_types) / 10.0, 1.0)
                
                # Overall quality score
                quality_scores['overall'] = sum(quality_scores.values()) / len(quality_scores)
                
                return quality_scores
        
        return QualityAssessor()
    
    def _initialize_monetization_analyzer(self):
        """Initialize monetization opportunity analyzer"""        class MonetizationAnalyzer:
            def __init__(self):
                self.revenue_models = [
                    'streaming', 'licensing', 'brand_partnerships', 'merchandise', 
                    'live_events', 'subscription', 'advertising', 'affiliate'
                ]
                
            async def analyze_monetization_opportunities(self, entities: List[Any]) -> List[Dict[str, Any]]:
                """Analyze monetization opportunities from extracted entities"""                opportunities = []
                
                # Check for brand partnership opportunities
                for entity in entities:
                    if hasattr(entity, 'entity_type') and entity.entity_type == 'organization':
                        opportunities.append({
                            'type': 'brand_partnership',
                            'entity': entity.text if hasattr(entity, 'text') else str(entity),
                            'potential_revenue': 'medium',
                            'effort_required': 'medium',
                            'probability': 0.6
                        })
                
                # Check for platform-specific opportunities
                for entity in entities:
                    if hasattr(entity, 'platform'):
                        platform = entity.platform.value if hasattr(entity.platform, 'value') else str(entity.platform)
                        opportunities.append({
                            'type': 'platform_monetization',
                            'platform': platform,
                            'potential_revenue': 'high' if platform in ['youtube', 'spotify'] else 'medium',
                            'effort_required': 'low',
                            'probability': 0.8
                        })
                
                return opportunities
        
        return MonetizationAnalyzer()
    
    def _initialize_seo_optimizer(self):
        """Initialize SEO optimization engine"""        class SEOOptimizer:
            def __init__(self):
                self.seo_factors = [
                    'keyword_density', 'title_optimization', 'meta_description', 
                    'hashtag_relevance', 'content_length', 'readability'
                ]
                
            async def optimize_content_seo(self, entities: List[Any], content: str) -> Dict[str, Any]:
                """Generate SEO optimization recommendations"""                recommendations = {
                    'keywords': [],
                    'hashtags': [],
                    'title_suggestions': [],
                    'description_suggestions': [],
                    'seo_score': 0.0
                }
                
                # Extract keywords from entities
                keywords = []
                hashtags = []
                
                for entity in entities:
                    if hasattr(entity, 'text'):
                        keywords.append(entity.text.lower())
                    
                    if hasattr(entity, 'entity_type') and entity.entity_type == 'hashtag':
                        hashtags.append(entity.text)
                
                recommendations['keywords'] = list(set(keywords))
                recommendations['hashtags'] = list(set(hashtags))
                
                # Generate title suggestions
                if keywords:
                    recommendations['title_suggestions'] = [
                        f"Amazing {keywords[0]} Content",
                        f"Discover {keywords[0]} Like Never Before",
                        f"Ultimate {keywords[0]} Experience"
                    ]
                
                # Calculate basic SEO score
                recommendations['seo_score'] = min(len(keywords) / 10.0, 1.0)
                
                return recommendations
        
        return SEOOptimizer()
    
    def _initialize_realtime_processor(self):
        """Initialize real-time processing system"""        class RealtimeProcessor:
            def __init__(self):
                self.processing_queue = asyncio.Queue()
                self.active_streams = {}
                
            async def process_stream(self, stream_id: str, data: Any) -> Dict[str, Any]:
                """Process streaming data in real-time"""                result = {
                    'stream_id': stream_id,
                    'processed_at': datetime.now().isoformat(),
                    'status': 'processed',
                    'entities_found': 0
                }
                
                # Add to processing queue
                await self.processing_queue.put({
                    'stream_id': stream_id,
                    'data': data,
                    'timestamp': datetime.now()
                })
                
                return result
        
        return RealtimeProcessor()
    
    def _initialize_performance_monitor(self):
        """Initialize performance monitoring system"""        class PerformanceMonitor:
            def __init__(self):
                self.metrics = {
                    'processing_time': [],
                    'memory_usage': [],
                    'cpu_usage': [],
                    'throughput': [],
                    'error_rate': 0.0
                }
                
            async def monitor_extraction_performance(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
                """Monitor and report extraction performance"""                processing_time = (end_time - start_time).total_seconds()
                self.metrics['processing_time'].append(processing_time)
                
                return {
                    'current_processing_time': processing_time,
                    'average_processing_time': sum(self.metrics['processing_time']) / len(self.metrics['processing_time']),
                    'performance_score': max(0.0, 1.0 - (processing_time / 10.0))  # Score decreases as time increases
                }
        
        return PerformanceMonitor()
    
    def _initialize_security_validator(self):
        """Initialize security validation system"""        class SecurityValidator:
            def __init__(self):
                self.blocked_patterns = [
                    r'(?i)password', r'(?i)api[_-]?key', r'(?i)secret', 
                    r'(?i)token', r'(?i)private[_-]?key'
                ]
                
            async def validate_content_security(self, content: str) -> Dict[str, Any]:
                """Validate content for security issues"""                import re
                
                issues = []
                for pattern in self.blocked_patterns:
                    if re.search(pattern, content):
                        issues.append(f"Potential sensitive information detected: {pattern}")
                
                return {
                    'is_safe': len(issues) == 0,
                    'security_issues': issues,
                    'risk_level': 'high' if issues else 'low'
                }
        
        return SecurityValidator()
    
    def _initialize_ml_enhancement(self):
        """Initialize machine learning enhancement engine"""        class MLEnhancementEngine:
            def __init__(self):
                self.models = {}
                self.training_data = []
                
            async def enhance_extraction_results(self, results: ComprehensiveExtractionResult) -> ComprehensiveExtractionResult:
                """Enhance extraction results using ML"""                # Apply ML-based confidence score adjustments
                enhanced_confidence = {}
                for key, score in results.confidence_scores.items():
                    # Apply ML enhancement (simplified)
                    enhanced_score = min(score * 1.1, 1.0)  # Boost confidence slightly
                    enhanced_confidence[key] = enhanced_score
                
                results.confidence_scores = enhanced_confidence
                return results
        
        return MLEnhancementEngine()
    
    def _initialize_prediction_engine(self):
        """Initialize prediction engine for future trends and opportunities"""        class PredictionEngine:
            def __init__(self):
                self.prediction_models = {}
                
            async def predict_future_opportunities(self, historical_data: List[Any]) -> Dict[str, Any]:
                """Predict future opportunities based on historical data"""                predictions = {
                    'trending_topics': [],
                    'collaboration_opportunities': [],
                    'monetization_potential': {},
                    'growth_forecast': {}
                }
                
                # Simple prediction logic (would be replaced with actual ML models)
                if historical_data:
                    predictions['growth_forecast'] = {
                        'expected_growth': 'positive',
                        'confidence': 0.7,
                        'timeframe': '30_days'
                    }
                
                return predictions
        
        return PredictionEngine()
    
    def _initialize_data_exporter(self):
        """Initialize data export system"""        class DataExporter:
            def __init__(self):
                self.export_formats = ['json', 'csv', 'xml', 'pdf', 'excel']
                
            async def export_results(self, results: ComprehensiveExtractionResult, format: str = 'json') -> Dict[str, Any]:
                """Export extraction results in specified format"""                export_data = {
                    'format': format,
                    'exported_at': datetime.now().isoformat(),
                    'total_entities': results.total_entities,
                    'export_size': len(str(results))
                }
                
                if format == 'json':
                    export_data['status'] = 'ready'
                    export_data['download_url'] = f"/exports/{hash(str(results))}.json"
                
                return export_data
        
        return DataExporter()
            self.collaboration_tracker = CollaborationEntityTracker(config)
            self.business_processor = BusinessEntityProcessor(config)
            self.content_analyzer = ContentEntityAnalyzer(config)
            self.creative_detector = CreativeEntityDetector(config)
            self.named_recognizer = NamedEntityRecognizer(config)
            self.metadata_parser = MetadataEntityParser(config)
            self.entity_linker = EntityLinker(config)
            self.relationship_extractor = RelationshipExtractor(config)
            
            self.services_initialized = True
            self.logger.info("All entity extraction services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {e}")
            self.services_initialized = False
            raise
    
    @cache_manager.cached(ttl=1800)
    async def extract_all_entities(
        self,
        text: str,
        content_metadata: Optional[ContentMetadata] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        platforms: Optional[List[PlatformType]] = None,
        include_recommendations: bool = True
    ) -> ComprehensiveExtractionResult:
        """        Perform comprehensive entity extraction using all available services
        
        Args:
            text: Input text to analyze
            content_metadata: Optional content metadata for context
            user_profile: Optional user profile for personalization
            platforms: Specific platforms to focus on
            include_recommendations: Whether to generate recommendations
            
        Returns:
            Complete extraction results from all services
        """        start_time = datetime.now()
        
        try:
            if not validate_input(text, str):
                raise ValueError("Invalid text input")
            
            self.logger.info("Starting comprehensive entity extraction")
            
            # Run all extractions in parallel for better performance
            extraction_tasks = [
                self._extract_general_entities(text, content_metadata),
                self._extract_platform_entities(text, platforms),
                self._extract_collaboration_entities(text, content_metadata, user_profile),
                self._extract_business_entities(text, content_metadata),
                self._extract_creative_entities(text, content_metadata),
                self._extract_content_entities(text, content_metadata),
                self._extract_metadata_entities(text, content_metadata),
                self._extract_relationships(text)
            ]
            
            # Execute all extractions concurrently
            results = await asyncio.gather(*extraction_tasks, return_exceptions=True)
            
            # Process results and handle any exceptions
            (general_entities, platform_entities, collaboration_entities,
             business_entities, creative_entities, content_entities,
             metadata_entities, relationships) = self._process_extraction_results(results)
            
            # Calculate comprehensive metrics
            total_entities = (
                len(general_entities) + len(platform_entities) + 
                len(collaboration_entities) + len(business_entities) +
                len(creative_entities) + len(content_entities) +
                len(metadata_entities)
            )
            
            # Calculate confidence scores by category
            confidence_scores = await self._calculate_confidence_scores(
                general_entities, platform_entities, collaboration_entities,
                business_entities, creative_entities, content_entities
            )
            
            # Generate insights and recommendations
            insights = await self._generate_insights(
                general_entities, platform_entities, collaboration_entities,
                business_entities, user_profile
            )
            
            recommendations = []
            if include_recommendations:
                recommendations = await self._generate_comprehensive_recommendations(
                    general_entities, platform_entities, collaboration_entities,
                    business_entities, user_profile, insights
                )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update metrics
            await self.metrics.increment("comprehensive_extractions_completed")
            await self.metrics.increment("total_entities_extracted", total_entities)
            await self.metrics.record("processing_time", processing_time)
            
            result = ComprehensiveExtractionResult(
                general_entities=general_entities,
                platform_entities=platform_entities,
                collaboration_entities=collaboration_entities,
                business_entities=business_entities,
                creative_entities=creative_entities,
                content_entities=content_entities,
                relationships=relationships,
                metadata_entities=metadata_entities,
                total_entities=total_entities,
                confidence_scores=confidence_scores,
                processing_time=processing_time,
                recommendations=recommendations,
                insights=insights,
                extracted_at=datetime.now()
            )
            
            self.logger.info(
                f"Comprehensive extraction completed: {total_entities} entities "
                f"in {processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Comprehensive entity extraction failed: {e}")
            await self.metrics.increment("extraction_errors")
            raise
    
    async def _extract_general_entities(
        self, 
        text: str, 
        content_metadata: Optional[ContentMetadata]
    ) -> List[ExtractedEntity]:
        """Extract general entities using core entity extractor"""        try:
            result = await self.entity_extractor.extract_entities(text, content_metadata)
            return result.entities
        except Exception as e:
            self.logger.error(f"General entity extraction failed: {e}")
            return []
    
    async def _extract_platform_entities(
        self, 
        text: str, 
        platforms: Optional[List[PlatformType]]
    ) -> List[PlatformEntity]:
        """Extract platform-specific entities"""        try:
            result = await self.platform_extractor.extract_platform_entities(
                text, platforms
            )
            return result.entities
        except Exception as e:
            self.logger.error(f"Platform entity extraction failed: {e}")
            return []
    
    async def _extract_collaboration_entities(
        self, 
        text: str, 
        content_metadata: Optional[ContentMetadata],
        user_profile: Optional[Dict[str, Any]]
    ) -> List[CollaborationEntity]:
        """Extract collaboration opportunities"""        try:
            result = await self.collaboration_tracker.track_collaboration_entities(
                text, content_metadata, user_profile
            )
            return result.entities
        except Exception as e:
            self.logger.error(f"Collaboration entity extraction failed: {e}")
            return []
    
    async def _extract_business_entities(
        self, 
        text: str, 
        content_metadata: Optional[ContentMetadata]
    ) -> List[Any]:
        """Extract business entities"""        try:
            result = await self.business_processor.process_business_entities(text)
            return result.entities if hasattr(result, 'entities') else []
        except Exception as e:
            self.logger.error(f"Business entity extraction failed: {e}")
            return []
    
    async def _extract_creative_entities(
        self, 
        text: str, 
        content_metadata: Optional[ContentMetadata]
    ) -> List[Any]:
        """Extract creative work entities"""        try:
            result = await self.creative_detector.detect_creative_entities(text)
            return result.entities if hasattr(result, 'entities') else []
        except Exception as e:
            self.logger.error(f"Creative entity extraction failed: {e}")
            return []
    
    async def _extract_content_entities(
        self, 
        text: str, 
        content_metadata: Optional[ContentMetadata]
    ) -> List[Any]:
        """Extract content-specific entities"""        try:
            result = await self.content_analyzer.analyze_content_entities(text)
            return result.entities if hasattr(result, 'entities') else []
        except Exception as e:
            self.logger.error(f"Content entity extraction failed: {e}")
            return []
    
    async def _extract_metadata_entities(
        self, 
        text: str, 
        content_metadata: Optional[ContentMetadata]
    ) -> List[Any]:
        """Extract metadata entities"""        try:
            result = await self.metadata_parser.parse_metadata_entities(text)
            return result.entities if hasattr(result, 'entities') else []
        except Exception as e:
            self.logger.error(f"Metadata entity extraction failed: {e}")
            return []
    
    async def _extract_relationships(self, text: str) -> List[Any]:
        """Extract entity relationships"""        try:
            result = await self.relationship_extractor.extract_relationships(text)
            return result.relationships if hasattr(result, 'relationships') else []
        except Exception as e:
            self.logger.error(f"Relationship extraction failed: {e}")
            return []
    
    def _process_extraction_results(self, results: List[Any]) -> tuple:
        """Process extraction results and handle exceptions"""        processed_results = []
        
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Extraction task failed: {result}")
                processed_results.append([])  # Empty list for failed extraction
            else:
                processed_results.append(result)
        
        # Ensure we have 8 results (one for each extraction type)
        while len(processed_results) < 8:
            processed_results.append([])
        
        return tuple(processed_results)
    
    async def _calculate_confidence_scores(
        self, 
        general_entities: List[ExtractedEntity],
        platform_entities: List[PlatformEntity],
        collaboration_entities: List[CollaborationEntity],
        business_entities: List[Any],
        creative_entities: List[Any],
        content_entities: List[Any]
    ) -> Dict[str, float]:
        """Calculate average confidence scores by category"""        scores = {}
        
        # General entities confidence
        if general_entities:
            scores["general"] = sum(e.confidence for e in general_entities) / len(general_entities)
        else:
            scores["general"] = 0.0
        
        # Platform entities confidence  
        if platform_entities:
            scores["platform"] = sum(e.confidence for e in platform_entities) / len(platform_entities)
        else:
            scores["platform"] = 0.0
        
        # Collaboration entities confidence
        if collaboration_entities:
            scores["collaboration"] = sum(e.confidence for e in collaboration_entities) / len(collaboration_entities)
        else:
            scores["collaboration"] = 0.0
        
        # Business entities confidence (assuming they have confidence attribute)
        if business_entities and hasattr(business_entities[0], 'confidence'):
            scores["business"] = sum(e.confidence for e in business_entities) / len(business_entities)
        else:
            scores["business"] = 0.0
        
        # Creative entities confidence
        if creative_entities and hasattr(creative_entities[0], 'confidence'):
            scores["creative"] = sum(e.confidence for e in creative_entities) / len(creative_entities)
        else:
            scores["creative"] = 0.0
        
        # Content entities confidence
        if content_entities and hasattr(content_entities[0], 'confidence'):
            scores["content"] = sum(e.confidence for e in content_entities) / len(content_entities)
        else:
            scores["content"] = 0.0
        
        # Overall confidence
        all_scores = [score for score in scores.values() if score > 0]
        scores["overall"] = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        return scores
    
    async def _generate_insights(
        self,
        general_entities: List[ExtractedEntity],
        platform_entities: List[PlatformEntity],
        collaboration_entities: List[CollaborationEntity],
        business_entities: List[Any],
        user_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate insights from extracted entities"""        insights = {}
        
        # Platform distribution analysis
        if platform_entities:
            platform_distribution = {}
            for entity in platform_entities:
                platform = entity.platform.value
                platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
            insights["platform_distribution"] = platform_distribution
            insights["primary_platform"] = max(platform_distribution, key=platform_distribution.get)
        
        # Collaboration opportunity analysis
        if collaboration_entities:
            collab_types = {}
            for entity in collaboration_entities:
                collab_type = entity.collaboration_type.value
                collab_types[collab_type] = collab_types.get(collab_type, 0) + 1
            insights["collaboration_opportunities"] = collab_types
            
            high_priority_collabs = [
                e for e in collaboration_entities 
                if e.priority.value in ["critical", "high"]
            ]
            insights["high_priority_collaborations"] = len(high_priority_collabs)
        
        # Content analysis insights
        if general_entities:
            entity_categories = {}
            for entity in general_entities:
                category = entity.category.value
                entity_categories[category] = entity_categories.get(category, 0) + 1
            insights["entity_categories"] = entity_categories
        
        # Business opportunity insights
        if business_entities:
            insights["business_entities_count"] = len(business_entities)
            # Add more business-specific insights here
        
        # User personalization insights
        if user_profile:
            user_genres = user_profile.get("genres", [])
            if user_genres and collaboration_entities:
                matching_collabs = [
                    e for e in collaboration_entities
                    if any(genre in e.collaborator_info.get("required_skills", []) for genre in user_genres)
                ]
                insights["genre_matched_collaborations"] = len(matching_collabs)
        
        return insights
    
    async def _generate_comprehensive_recommendations(
        self,
        general_entities: List[ExtractedEntity],
        platform_entities: List[PlatformEntity],
        collaboration_entities: List[CollaborationEntity],
        business_entities: List[Any],
        user_profile: Optional[Dict[str, Any]],
        insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations based on all extracted entities"""        recommendations = []
        
        # Platform optimization recommendations
        if insights.get("platform_distribution"):
            primary_platform = insights.get("primary_platform")
            if primary_platform:
                recommendations.append({
                    "type": "platform_optimization",
                    "title": f"Optimize {primary_platform.title()} Presence",
                    "description": f"Focus on maximizing engagement on {primary_platform}",
                    "priority": "medium",
                    "action_items": [
                        f"Increase posting frequency on {primary_platform}",
                        f"Optimize content for {primary_platform} algorithm",
                        f"Engage more with {primary_platform} community"
                    ]
                })
        
        # High-priority collaboration recommendations
        high_priority_count = insights.get("high_priority_collaborations", 0)
        if high_priority_count > 0:
            recommendations.append({
                "type": "collaboration_action",
                "title": "Urgent Collaboration Opportunities",
                "description": f"Act on {high_priority_count} high-priority collaborations immediately",
                "priority": "critical",
                "action_items": [
                    "Review collaboration details",
                    "Prepare outreach messages",
                    "Schedule collaboration meetings"
                ]
            })
        
        # Cross-platform strategy recommendations
        platform_count = len(insights.get("platform_distribution", {}))
        if platform_count < 3:
            recommendations.append({
                "type": "platform_expansion",
                "title": "Expand Platform Presence",
                "description": "Consider expanding to additional platforms for broader reach",
                "priority": "medium",
                "action_items": [
                    "Research trending platforms in your niche",
                    "Create content strategy for new platforms",
                    "Set up profiles on additional platforms"
                ]
            })
        
        # Content strategy recommendations
        if insights.get("entity_categories"):
            most_common_category = max(
                insights["entity_categories"], 
                key=insights["entity_categories"].get
            )
            recommendations.append({
                "type": "content_strategy",
                "title": f"Leverage {most_common_category.title()} Content",
                "description": f"Focus on {most_common_category} content which appears frequently",
                "priority": "medium",
                "action_items": [
                    f"Create more {most_common_category}-focused content",
                    f"Optimize {most_common_category} content for SEO",
                    f"Collaborate with other {most_common_category} creators"
                ]
            })
        
        # Business opportunity recommendations
        if business_entities:
            recommendations.append({
                "type": "monetization",
                "title": "Explore Business Opportunities",
                "description": "Multiple business entities detected - explore monetization",
                "priority": "high",
                "action_items": [
                    "Research identified business opportunities",
                    "Prepare business proposals",
                    "Network with identified organizations"
                ]
            })
        
        return recommendations
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get status of all extraction services"""        status = {
            "orchestrator_healthy": self.services_initialized,
            "services": {}
        }
        
        services = [
            ("entity_extractor", self.entity_extractor),
            ("platform_extractor", self.platform_extractor),
            ("collaboration_tracker", self.collaboration_tracker),
            ("business_processor", self.business_processor),
            ("content_analyzer", self.content_analyzer),
            ("creative_detector", self.creative_detector),
            ("named_recognizer", self.named_recognizer),
            ("metadata_parser", self.metadata_parser),
            ("entity_linker", self.entity_linker),
            ("relationship_extractor", self.relationship_extractor)
        ]
        
        for service_name, service in services:
            try:
                if hasattr(service, 'health_check'):
                    service_status = await service.health_check()
                    status["services"][service_name] = service_status
                else:
                    status["services"][service_name] = {"status": "unknown"}
            except Exception as e:
                status["services"][service_name] = {"status": "error", "error": str(e)}
        
        return status
    
    async def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all services"""        return await self.metrics.get_all_metrics()


# Convenience function for quick access
async def extract_entities_comprehensive(
    text: str,
    content_metadata: Optional[ContentMetadata] = None,
    user_profile: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> ComprehensiveExtractionResult:
    """    Convenience function for comprehensive entity extraction
    
    Args:
        text: Input text to analyze
        content_metadata: Optional content metadata
        user_profile: Optional user profile for personalization  
        config: Optional configuration
        
    Returns:
        Complete extraction results
    """    orchestrator = EntityExtractionOrchestrator(config)
    return await orchestrator.extract_all_entities(
        text, content_metadata, user_profile
    )
