"""
AI Content Analyzer - Advanced Multi-Provider AI Content Analysis
================================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Role**: Lead Dev IA & IA Prompt Engineer
**Module**: AI & Machine Learning Services
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Advanced AI content analysis with multi-provider orchestration,
intelligent prompt engineering, and comprehensive content insights.
"""

import asyncio
import json
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import aioredis
import aiohttp
import openai
from anthropic import AsyncAnthropic
import base64
import tiktoken


class ContentType(Enum):
    """Types of content to analyze"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    CODE = "code"
    MIXED = "mixed"


class AnalysisType(Enum):
    """Types of analysis to perform"""
    SENTIMENT = "sentiment"
    TOXICITY = "toxicity"
    TOPICS = "topics"
    ENTITIES = "entities"
    KEYWORDS = "keywords"
    QUALITY = "quality"
    ORIGINALITY = "originality"
    READABILITY = "readability"
    SEO_OPTIMIZATION = "seo"
    ENGAGEMENT_POTENTIAL = "engagement"
    MONETIZATION_SCORE = "monetization"
    COMPLIANCE = "compliance"


class AIProvider(Enum):
    """AI providers for content analysis"""
    OPENAI_GPT4 = "openai_gpt4"
    OPENAI_GPT35 = "openai_gpt35"
    ANTHROPIC_CLAUDE = "anthropic_claude"
    CUSTOM_MODEL = "custom_model"
    ENSEMBLE = "ensemble"


@dataclass
class ContentInput:
    """Content input structure"""
    content_id: str
    content_type: ContentType
    content_data: Union[str, bytes, Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    analysis_types: List[AnalysisType] = field(default_factory=list)
    ai_provider: AIProvider = AIProvider.OPENAI_GPT4
    custom_prompts: Dict[str, str] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Analysis result structure"""
    content_id: str
    analysis_type: AnalysisType
    ai_provider: AIProvider
    score: float
    confidence: float
    details: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentAnalysisReport:
    """Comprehensive content analysis report"""
    content_id: str
    content_type: ContentType
    overall_score: float
    analysis_results: List[AnalysisResult]
    summary: Dict[str, Any]
    actionable_insights: List[str]
    optimization_suggestions: List[str]
    compliance_status: bool
    monetization_potential: float
    created_at: datetime = field(default_factory=datetime.utcnow)


class AIContentAnalyzer:
    """
    Advanced AI Content Analyzer Service
    
    Multi-provider AI content analysis with:
    - Advanced prompt engineering and optimization
    - Multi-provider AI orchestration (OpenAI, Anthropic, Custom)
    - Comprehensive content quality assessment
    - SEO and monetization analysis
    - Compliance and safety checking
    - Real-time performance optimization
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.logger = logging.getLogger(__name__)
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        
        # AI Provider configurations
        self.ai_providers = {}
        self.prompt_templates = {}
        
        # Analysis cache and optimization
        self.analysis_cache: Dict[str, ContentAnalysisReport] = {}
        self.performance_metrics = {
            "total_analyses": 0,
            "avg_processing_time": 0.0,
            "provider_performance": {},
            "cache_hit_rate": 0.0
        }
        
        # Content quality thresholds
        self.quality_thresholds = {
            "minimum_quality": 0.6,
            "high_quality": 0.8,
            "exceptional_quality": 0.9,
            "toxicity_threshold": 0.3,
            "originality_threshold": 0.7
        }
        
        # Initialize AI providers and prompts
        self._initialize_ai_providers()
        self._initialize_prompt_templates()
        
        self.logger.info("AI Content Analyzer initialized with multi-provider support")

    async def initialize(self):
        """Initialize AI content analyzer"""
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Load cached prompts and configurations
            await self._load_prompt_configurations()
            
            # Initialize provider connections
            await self._initialize_provider_connections()
            
            self.logger.info("AI Content Analyzer initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Content Analyzer: {e}")
            raise

    def _initialize_ai_providers(self):
        """Initialize AI provider configurations"""
        
        # OpenAI configuration
        self.ai_providers[AIProvider.OPENAI_GPT4] = {
            "model": "gpt-4-turbo-preview",
            "max_tokens": 4000,
            "temperature": 0.3,
            "timeout": 30
        }
        
        self.ai_providers[AIProvider.OPENAI_GPT35] = {
            "model": "gpt-3.5-turbo",
            "max_tokens": 2000,
            "temperature": 0.3,
            "timeout": 20
        }
        
        # Anthropic configuration
        self.ai_providers[AIProvider.ANTHROPIC_CLAUDE] = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 3000,
            "timeout": 25
        }

    def _initialize_prompt_templates(self):
        """Initialize advanced prompt templates for different analysis types"""
        
        # Sentiment Analysis Prompt
        self.prompt_templates[AnalysisType.SENTIMENT] = {
            "system": """You are an expert sentiment analysis AI. Analyze the emotional tone and sentiment of content with high precision.""",
            "user": """Analyze the sentiment of the following content:

Content: {content}

Provide analysis in JSON format with:
- sentiment: positive/negative/neutral
- intensity: 0-1 scale
- emotional_components: list of detected emotions
- confidence: 0-1 scale
- reasoning: brief explanation

Be thorough and consider context, sarcasm, and nuanced expressions."""
        }
        
        # Content Quality Prompt
        self.prompt_templates[AnalysisType.QUALITY] = {
            "system": """You are a content quality expert. Evaluate content across multiple dimensions with professional standards.""",
            "user": """Evaluate the quality of this content:

Content: {content}

Analyze and rate (0-1 scale) these aspects:
- clarity: how clear and understandable
- coherence: logical flow and structure
- engagement: potential to capture audience attention
- uniqueness: originality and distinctiveness
- value: usefulness and informativeness
- technical_quality: grammar, style, formatting

Provide JSON response with scores, overall_quality (0-1), and detailed feedback."""
        }
        
        # SEO Optimization Prompt
        self.prompt_templates[AnalysisType.SEO_OPTIMIZATION] = {
            "system": """You are an SEO expert analyzing content for search engine optimization potential.""",
            "user": """Analyze this content for SEO optimization:

Content: {content}

Evaluate:
- keyword_density: natural keyword usage
- title_optimization: effectiveness of headlines
- readability_seo: SEO-friendly readability
- meta_potential: meta description quality
- search_intent_match: alignment with user queries
- content_structure: SEO-friendly formatting

Provide JSON with scores (0-1), seo_score, and optimization_recommendations."""
        }
        
        # Toxicity Detection Prompt
        self.prompt_templates[AnalysisType.TOXICITY] = {
            "system": """You are a content safety expert. Detect potentially harmful, toxic, or inappropriate content.""",
            "user": """Analyze this content for toxicity and safety concerns:

Content: {content}

Check for:
- hate_speech: discriminatory language
- harassment: bullying or threatening content
- violence: graphic or violent content
- adult_content: inappropriate sexual content
- misinformation: potentially false information
- spam: promotional or spam content

Provide JSON with boolean flags, toxicity_score (0-1), risk_level, and specific_concerns."""
        }
        
        # Monetization Potential Prompt
        self.prompt_templates[AnalysisType.MONETIZATION_SCORE] = {
            "system": """You are a digital marketing and monetization expert. Assess content's commercial potential.""",
            "user": """Evaluate the monetization potential of this content:

Content: {content}

Analyze:
- commercial_appeal: attractiveness to advertisers
- audience_engagement: potential for user interaction
- shareability: viral and sharing potential
- conversion_potential: ability to drive actions
- brand_safety: suitability for brand partnerships
- niche_value: value in specific market segments

Provide JSON with scores (0-1), monetization_score, revenue_strategies, and market_insights."""
        }

    async def _initialize_provider_connections(self):
        """Initialize connections to AI providers"""
        
        try:
            # Initialize OpenAI client
            openai.api_key = "your-openai-api-key"  # In production, use environment variables
            
            # Initialize Anthropic client
            self.anthropic_client = AsyncAnthropic(
                api_key="your-anthropic-api-key"  # In production, use environment variables
            )
            
            self.logger.info("AI provider connections initialized")
            
        except Exception as e:
            self.logger.warning(f"Could not initialize all AI providers: {e}")

    async def analyze_content(self, content_input: ContentInput) -> ContentAnalysisReport:
        """
        Comprehensive content analysis using multiple AI providers
        
        Args:
            content_input: Content to analyze with configuration
            
        Returns:
            ContentAnalysisReport with comprehensive analysis
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(content_input)
            cached_result = await self._get_cached_analysis(cache_key)
            
            if cached_result:
                self.performance_metrics["cache_hit_rate"] = (
                    self.performance_metrics.get("cache_hit_rate", 0) * 0.9 + 0.1
                )
                return cached_result
            
            # Perform analysis
            analysis_results = []
            
            # Run analysis for each requested type
            for analysis_type in content_input.analysis_types:
                result = await self._perform_single_analysis(
                    content_input,
                    analysis_type
                )
                analysis_results.append(result)
            
            # Generate comprehensive report
            report = await self._generate_analysis_report(
                content_input,
                analysis_results
            )
            
            # Cache result
            await self._cache_analysis_result(cache_key, report)
            
            # Update performance metrics
            processing_time = time.time() - start_time
            await self._update_performance_metrics(processing_time, content_input.ai_provider)
            
            self.logger.info(f"Content analysis completed for {content_input.content_id}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error analyzing content {content_input.content_id}: {e}")
            raise

    async def _perform_single_analysis(self, content_input: ContentInput,
                                     analysis_type: AnalysisType) -> AnalysisResult:
        """Perform single type of analysis using specified AI provider"""
        
        start_time = time.time()
        
        try:
            # Get optimized prompt
            prompt = await self._get_optimized_prompt(analysis_type, content_input)
            
            # Choose AI provider based on analysis type and performance
            provider = await self._select_optimal_provider(analysis_type, content_input.ai_provider)
            
            # Perform AI analysis
            ai_response = await self._call_ai_provider(provider, prompt, content_input)
            
            # Parse and validate response
            parsed_result = await self._parse_ai_response(ai_response, analysis_type)
            
            # Create analysis result
            result = AnalysisResult(
                content_id=content_input.content_id,
                analysis_type=analysis_type,
                ai_provider=provider,
                score=parsed_result.get("score", 0.0),
                confidence=parsed_result.get("confidence", 0.0),
                details=parsed_result.get("details", {}),
                insights=parsed_result.get("insights", []),
                recommendations=parsed_result.get("recommendations", []),
                processing_time=time.time() - start_time
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in single analysis {analysis_type.value}: {e}")
            raise

    async def _get_optimized_prompt(self, analysis_type: AnalysisType, 
                                  content_input: ContentInput) -> Dict[str, str]:
        """Get optimized prompt for specific analysis type"""
        
        # Get base template
        template = self.prompt_templates.get(analysis_type)
        if not template:
            raise ValueError(f"No prompt template for analysis type: {analysis_type.value}")
        
        # Use custom prompt if provided
        if analysis_type.value in content_input.custom_prompts:
            template["user"] = content_input.custom_prompts[analysis_type.value]
        
        # Format prompt with content
        content_text = await self._extract_text_content(content_input)
        
        formatted_prompt = {
            "system": template["system"],
            "user": template["user"].format(content=content_text[:4000])  # Limit content length
        }
        
        return formatted_prompt

    async def _extract_text_content(self, content_input: ContentInput) -> str:
        """Extract text content from various content types"""
        
        if content_input.content_type == ContentType.TEXT:
            return str(content_input.content_data)
        
        elif content_input.content_type == ContentType.DOCUMENT:
            # Handle document content extraction
            if isinstance(content_input.content_data, dict):
                return content_input.content_data.get("text", "")
            return str(content_input.content_data)
        
        elif content_input.content_type == ContentType.CODE:
            return str(content_input.content_data)
        
        elif content_input.content_type in [ContentType.IMAGE, ContentType.AUDIO, ContentType.VIDEO]:
            # For media content, use metadata or description
            return content_input.metadata.get("description", "Media content")
        
        else:
            return str(content_input.content_data)

    async def _select_optimal_provider(self, analysis_type: AnalysisType, 
                                     preferred_provider: AIProvider) -> AIProvider:
        """Select optimal AI provider based on analysis type and performance"""
        
        # Provider performance mapping
        provider_strengths = {
            AnalysisType.SENTIMENT: [AIProvider.OPENAI_GPT4, AIProvider.ANTHROPIC_CLAUDE],
            AnalysisType.TOXICITY: [AIProvider.OPENAI_GPT4, AIProvider.ANTHROPIC_CLAUDE],
            AnalysisType.QUALITY: [AIProvider.OPENAI_GPT4, AIProvider.ANTHROPIC_CLAUDE],
            AnalysisType.SEO_OPTIMIZATION: [AIProvider.OPENAI_GPT4, AIProvider.OPENAI_GPT35],
            AnalysisType.MONETIZATION_SCORE: [AIProvider.OPENAI_GPT4, AIProvider.ANTHROPIC_CLAUDE]
        }
        
        # Check if preferred provider is suitable
        suitable_providers = provider_strengths.get(analysis_type, [preferred_provider])
        
        if preferred_provider in suitable_providers:
            return preferred_provider
        
        # Select best performing provider for this analysis type
        performance_scores = self.performance_metrics.get("provider_performance", {})
        
        best_provider = preferred_provider
        best_score = 0.0
        
        for provider in suitable_providers:
            provider_key = f"{provider.value}_{analysis_type.value}"
            score = performance_scores.get(provider_key, 0.5)
            
            if score > best_score:
                best_score = score
                best_provider = provider
        
        return best_provider

    async def _call_ai_provider(self, provider: AIProvider, prompt: Dict[str, str],
                              content_input: ContentInput) -> Dict[str, Any]:
        """Call specific AI provider with optimized parameters"""
        
        try:
            if provider in [AIProvider.OPENAI_GPT4, AIProvider.OPENAI_GPT35]:
                return await self._call_openai(provider, prompt)
            
            elif provider == AIProvider.ANTHROPIC_CLAUDE:
                return await self._call_anthropic(prompt)
            
            else:
                raise ValueError(f"Unsupported AI provider: {provider.value}")
        
        except Exception as e:
            self.logger.error(f"Error calling AI provider {provider.value}: {e}")
            raise

    async def _call_openai(self, provider: AIProvider, prompt: Dict[str, str]) -> Dict[str, Any]:
        """Call OpenAI API with optimized parameters"""
        
        config = self.ai_providers[provider]
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=config["model"],
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
                timeout=config["timeout"]
            )
            
            return {
                "response": response.choices[0].message.content,
                "usage": response.usage,
                "model": config["model"]
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise

    async def _call_anthropic(self, prompt: Dict[str, str]) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        
        config = self.ai_providers[AIProvider.ANTHROPIC_CLAUDE]
        
        try:
            response = await self.anthropic_client.messages.create(
                model=config["model"],
                max_tokens=config["max_tokens"],
                messages=[
                    {"role": "user", "content": f"{prompt['system']}\n\n{prompt['user']}"}
                ]
            )
            
            return {
                "response": response.content[0].text,
                "usage": {"total_tokens": len(response.content[0].text.split())},
                "model": config["model"]
            }
            
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            raise

    async def _parse_ai_response(self, ai_response: Dict[str, Any], 
                               analysis_type: AnalysisType) -> Dict[str, Any]:
        """Parse and validate AI response"""
        
        response_text = ai_response.get("response", "")
        
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith("{"):
                parsed = json.loads(response_text)
                return self._validate_parsed_response(parsed, analysis_type)
            
            # Fallback: extract structured data from text
            return await self._extract_structured_data(response_text, analysis_type)
            
        except json.JSONDecodeError:
            # Fallback: create structured response from text
            return await self._create_fallback_response(response_text, analysis_type)

    def _validate_parsed_response(self, parsed_data: Dict[str, Any], 
                                analysis_type: AnalysisType) -> Dict[str, Any]:
        """Validate and normalize parsed response"""
        
        validated = {
            "score": float(parsed_data.get("score", 0.0)),
            "confidence": float(parsed_data.get("confidence", 0.5)),
            "details": parsed_data.get("details", {}),
            "insights": parsed_data.get("insights", []),
            "recommendations": parsed_data.get("recommendations", [])
        }
        
        # Ensure score is in valid range
        validated["score"] = max(0.0, min(1.0, validated["score"]))
        validated["confidence"] = max(0.0, min(1.0, validated["confidence"]))
        
        # Analysis-specific validation
        if analysis_type == AnalysisType.SENTIMENT:
            sentiment = parsed_data.get("sentiment", "neutral")
            validated["details"]["sentiment"] = sentiment
            validated["details"]["emotional_components"] = parsed_data.get("emotional_components", [])
        
        elif analysis_type == AnalysisType.TOXICITY:
            validated["details"]["risk_level"] = parsed_data.get("risk_level", "low")
            validated["details"]["specific_concerns"] = parsed_data.get("specific_concerns", [])
        
        return validated

    async def _extract_structured_data(self, response_text: str, 
                                     analysis_type: AnalysisType) -> Dict[str, Any]:
        """Extract structured data from unstructured AI response"""
        
        # Use simple pattern matching for common structures
        import re
        
        # Extract score
        score_match = re.search(r'score[:\s]*([0-9.]+)', response_text, re.IGNORECASE)
        score = float(score_match.group(1)) if score_match else 0.5
        
        # Extract confidence
        conf_match = re.search(r'confidence[:\s]*([0-9.]+)', response_text, re.IGNORECASE)
        confidence = float(conf_match.group(1)) if conf_match else 0.5
        
        return {
            "score": max(0.0, min(1.0, score)),
            "confidence": max(0.0, min(1.0, confidence)),
            "details": {"raw_response": response_text},
            "insights": [response_text[:200]],  # First 200 chars as insight
            "recommendations": []
        }

    async def _create_fallback_response(self, response_text: str, 
                                      analysis_type: AnalysisType) -> Dict[str, Any]:
        """Create fallback response when parsing fails"""
        
        return {
            "score": 0.5,  # Neutral score
            "confidence": 0.3,  # Low confidence due to parsing failure
            "details": {
                "raw_response": response_text,
                "parsing_error": True
            },
            "insights": ["AI response could not be parsed structured"],
            "recommendations": ["Retry analysis with different prompt"]
        }

    async def _generate_analysis_report(self, content_input: ContentInput,
                                      analysis_results: List[AnalysisResult]) -> ContentAnalysisReport:
        """Generate comprehensive analysis report"""
        
        # Calculate overall score (weighted average)
        weights = {
            AnalysisType.QUALITY: 0.25,
            AnalysisType.SENTIMENT: 0.15,
            AnalysisType.TOXICITY: 0.20,  # Negative contribution
            AnalysisType.SEO_OPTIMIZATION: 0.15,
            AnalysisType.MONETIZATION_SCORE: 0.15,
            AnalysisType.ENGAGEMENT_POTENTIAL: 0.10
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        result_dict = {result.analysis_type: result for result in analysis_results}
        
        for analysis_type, weight in weights.items():
            if analysis_type in result_dict:
                result = result_dict[analysis_type]
                
                # Toxicity contributes negatively
                if analysis_type == AnalysisType.TOXICITY:
                    score_contribution = (1.0 - result.score) * weight
                else:
                    score_contribution = result.score * weight
                
                total_score += score_contribution
                total_weight += weight
        
        overall_score = total_score / total_weight if total_weight > 0 else 0.5
        
        # Generate summary
        summary = await self._generate_content_summary(analysis_results)
        
        # Generate actionable insights
        insights = await self._generate_actionable_insights(analysis_results)
        
        # Generate optimization suggestions
        optimizations = await self._generate_optimization_suggestions(analysis_results)
        
        # Check compliance
        compliance_status = await self._check_compliance_status(analysis_results)
        
        # Calculate monetization potential
        monetization_potential = await self._calculate_monetization_potential(analysis_results)
        
        report = ContentAnalysisReport(
            content_id=content_input.content_id,
            content_type=content_input.content_type,
            overall_score=overall_score,
            analysis_results=analysis_results,
            summary=summary,
            actionable_insights=insights,
            optimization_suggestions=optimizations,
            compliance_status=compliance_status,
            monetization_potential=monetization_potential
        )
        
        return report

    async def _generate_content_summary(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Generate content summary from analysis results"""
        
        summary = {
            "quality_assessment": "Unknown",
            "content_safety": "Unknown",
            "commercial_viability": "Unknown",
            "key_strengths": [],
            "areas_for_improvement": []
        }
        
        for result in results:
            if result.analysis_type == AnalysisType.QUALITY:
                if result.score >= 0.8:
                    summary["quality_assessment"] = "High Quality"
                elif result.score >= 0.6:
                    summary["quality_assessment"] = "Good Quality"
                else:
                    summary["quality_assessment"] = "Needs Improvement"
            
            elif result.analysis_type == AnalysisType.TOXICITY:
                if result.score <= 0.2:
                    summary["content_safety"] = "Safe"
                elif result.score <= 0.5:
                    summary["content_safety"] = "Moderate Risk"
                else:
                    summary["content_safety"] = "High Risk"
            
            elif result.analysis_type == AnalysisType.MONETIZATION_SCORE:
                if result.score >= 0.7:
                    summary["commercial_viability"] = "High Potential"
                elif result.score >= 0.5:
                    summary["commercial_viability"] = "Moderate Potential"
                else:
                    summary["commercial_viability"] = "Low Potential"
            
            # Add insights as strengths or improvements
            if result.score >= 0.7:
                summary["key_strengths"].extend(result.insights[:2])
            else:
                summary["areas_for_improvement"].extend(result.recommendations[:2])
        
        return summary

    async def _generate_actionable_insights(self, results: List[AnalysisResult]) -> List[str]:
        """Generate actionable insights from analysis results"""
        
        insights = []
        
        for result in results:
            if result.insights:
                insights.extend(result.insights[:2])  # Top 2 insights per analysis
        
        # Add cross-analysis insights
        quality_result = next((r for r in results if r.analysis_type == AnalysisType.QUALITY), None)
        seo_result = next((r for r in results if r.analysis_type == AnalysisType.SEO_OPTIMIZATION), None)
        
        if quality_result and seo_result:
            if quality_result.score > 0.8 and seo_result.score < 0.6:
                insights.append("High-quality content with SEO optimization potential")
            elif quality_result.score < 0.6 and seo_result.score > 0.7:
                insights.append("SEO-optimized content needs quality improvements")
        
        return list(set(insights))  # Remove duplicates

    async def _generate_optimization_suggestions(self, results: List[AnalysisResult]) -> List[str]:
        """Generate optimization suggestions"""
        
        suggestions = []
        
        for result in results:
            if result.score < 0.7 and result.recommendations:
                suggestions.extend(result.recommendations[:2])
        
        # Add prioritized suggestions based on impact
        priority_suggestions = []
        
        toxicity_result = next((r for r in results if r.analysis_type == AnalysisType.TOXICITY), None)
        if toxicity_result and toxicity_result.score > 0.3:
            priority_suggestions.append("URGENT: Address content safety concerns before publication")
        
        quality_result = next((r for r in results if r.analysis_type == AnalysisType.QUALITY), None)
        if quality_result and quality_result.score < 0.6:
            priority_suggestions.append("Improve content quality for better audience engagement")
        
        return priority_suggestions + list(set(suggestions))

    async def _check_compliance_status(self, results: List[AnalysisResult]) -> bool:
        """Check if content meets compliance requirements"""
        
        # Check toxicity threshold
        toxicity_result = next((r for r in results if r.analysis_type == AnalysisType.TOXICITY), None)
        if toxicity_result and toxicity_result.score > self.quality_thresholds["toxicity_threshold"]:
            return False
        
        # Check minimum quality threshold
        quality_result = next((r for r in results if r.analysis_type == AnalysisType.QUALITY), None)
        if quality_result and quality_result.score < self.quality_thresholds["minimum_quality"]:
            return False
        
        return True

    async def _calculate_monetization_potential(self, results: List[AnalysisResult]) -> float:
        """Calculate overall monetization potential"""
        
        monetization_factors = {}
        
        for result in results:
            if result.analysis_type == AnalysisType.MONETIZATION_SCORE:
                monetization_factors["commercial_appeal"] = result.score
            elif result.analysis_type == AnalysisType.QUALITY:
                monetization_factors["content_quality"] = result.score
            elif result.analysis_type == AnalysisType.SEO_OPTIMIZATION:
                monetization_factors["discoverability"] = result.score
            elif result.analysis_type == AnalysisType.ENGAGEMENT_POTENTIAL:
                monetization_factors["engagement"] = result.score
        
        # Weighted calculation
        weights = {
            "commercial_appeal": 0.4,
            "content_quality": 0.3,
            "discoverability": 0.2,
            "engagement": 0.1
        }
        
        total_potential = 0.0
        total_weight = 0.0
        
        for factor, score in monetization_factors.items():
            weight = weights.get(factor, 0.1)
            total_potential += score * weight
            total_weight += weight
        
        return total_potential / total_weight if total_weight > 0 else 0.0

    def _generate_cache_key(self, content_input: ContentInput) -> str:
        """Generate cache key for content analysis"""
        
        # Create hash of content and analysis configuration
        content_str = str(content_input.content_data)[:1000]  # First 1000 chars
        analysis_config = f"{content_input.content_type.value}_{sorted(content_input.analysis_types)}"
        
        cache_content = f"{content_str}_{analysis_config}_{content_input.ai_provider.value}"
        return hashlib.md5(cache_content.encode()).hexdigest()

    async def _get_cached_analysis(self, cache_key: str) -> Optional[ContentAnalysisReport]:
        """Get cached analysis result"""
        
        try:
            cached_data = await self.redis_client.get(f"content_analysis:{cache_key}")
            if cached_data:
                data = json.loads(cached_data)
                # Reconstruct ContentAnalysisReport from cached data
                return self._deserialize_analysis_report(data)
        except Exception as e:
            self.logger.warning(f"Error reading cache: {e}")
        
        return None

    async def _cache_analysis_result(self, cache_key: str, report: ContentAnalysisReport):
        """Cache analysis result"""
        
        try:
            # Serialize report
            serialized = self._serialize_analysis_report(report)
            
            # Cache for 24 hours
            await self.redis_client.setex(
                f"content_analysis:{cache_key}",
                86400,
                json.dumps(serialized)
            )
        except Exception as e:
            self.logger.warning(f"Error caching result: {e}")

    def _serialize_analysis_report(self, report: ContentAnalysisReport) -> Dict[str, Any]:
        """Serialize analysis report for caching"""
        
        return {
            "content_id": report.content_id,
            "content_type": report.content_type.value,
            "overall_score": report.overall_score,
            "analysis_results": [
                {
                    "content_id": r.content_id,
                    "analysis_type": r.analysis_type.value,
                    "ai_provider": r.ai_provider.value,
                    "score": r.score,
                    "confidence": r.confidence,
                    "details": r.details,
                    "insights": r.insights,
                    "recommendations": r.recommendations,
                    "processing_time": r.processing_time,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in report.analysis_results
            ],
            "summary": report.summary,
            "actionable_insights": report.actionable_insights,
            "optimization_suggestions": report.optimization_suggestions,
            "compliance_status": report.compliance_status,
            "monetization_potential": report.monetization_potential,
            "created_at": report.created_at.isoformat()
        }

    def _deserialize_analysis_report(self, data: Dict[str, Any]) -> ContentAnalysisReport:
        """Deserialize analysis report from cache"""
        
        analysis_results = []
        for r_data in data["analysis_results"]:
            result = AnalysisResult(
                content_id=r_data["content_id"],
                analysis_type=AnalysisType(r_data["analysis_type"]),
                ai_provider=AIProvider(r_data["ai_provider"]),
                score=r_data["score"],
                confidence=r_data["confidence"],
                details=r_data["details"],
                insights=r_data["insights"],
                recommendations=r_data["recommendations"],
                processing_time=r_data["processing_time"],
                timestamp=datetime.fromisoformat(r_data["timestamp"])
            )
            analysis_results.append(result)
        
        return ContentAnalysisReport(
            content_id=data["content_id"],
            content_type=ContentType(data["content_type"]),
            overall_score=data["overall_score"],
            analysis_results=analysis_results,
            summary=data["summary"],
            actionable_insights=data["actionable_insights"],
            optimization_suggestions=data["optimization_suggestions"],
            compliance_status=data["compliance_status"],
            monetization_potential=data["monetization_potential"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

    async def _update_performance_metrics(self, processing_time: float, provider: AIProvider):
        """Update performance metrics"""
        
        self.performance_metrics["total_analyses"] += 1
        
        # Update average processing time
        current_avg = self.performance_metrics["avg_processing_time"]
        total_analyses = self.performance_metrics["total_analyses"]
        
        self.performance_metrics["avg_processing_time"] = (
            (current_avg * (total_analyses - 1) + processing_time) / total_analyses
        )
        
        # Update provider performance
        provider_key = provider.value
        if "provider_performance" not in self.performance_metrics:
            self.performance_metrics["provider_performance"] = {}
        
        current_perf = self.performance_metrics["provider_performance"].get(provider_key, 0.5)
        
        # Score based on processing time (lower is better)
        time_score = max(0.1, min(1.0, 1.0 - (processing_time / 30.0)))
        
        # Exponential moving average
        self.performance_metrics["provider_performance"][provider_key] = (
            current_perf * 0.8 + time_score * 0.2
        )

    async def _load_prompt_configurations(self):
        """Load custom prompt configurations from cache"""
        
        try:
            prompts_data = await self.redis_client.get("ai_content_prompts")
            if prompts_data:
                custom_prompts = json.loads(prompts_data)
                self.prompt_templates.update(custom_prompts)
                
                self.logger.info("Loaded custom prompt configurations")
        except Exception as e:
            self.logger.warning(f"Could not load prompt configurations: {e}")

    async def get_analysis_dashboard(self) -> Dict[str, Any]:
        """Get AI content analysis dashboard"""
        
        return {
            "performance_metrics": self.performance_metrics,
            "quality_thresholds": self.quality_thresholds,
            "available_providers": list(self.ai_providers.keys()),
            "supported_analysis_types": [t.value for t in AnalysisType],
            "cache_size": len(self.analysis_cache),
            "system_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }

    async def shutdown(self):
        """Shutdown AI content analyzer"""
        
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("AI Content Analyzer shutdown completed")


# Example usage
async def main():
    """Example usage of AI Content Analyzer"""
    
    analyzer = AIContentAnalyzer()
    await analyzer.initialize()
    
    try:
        # Example content analysis
        content_input = ContentInput(
            content_id="test_content_001",
            content_type=ContentType.TEXT,
            content_data="This is a sample blog post about artificial intelligence and its applications in modern business. AI is transforming how we work and live.",
            analysis_types=[
                AnalysisType.QUALITY,
                AnalysisType.SENTIMENT,
                AnalysisType.SEO_OPTIMIZATION,
                AnalysisType.MONETIZATION_SCORE
            ],
            ai_provider=AIProvider.OPENAI_GPT4
        )
        
        report = await analyzer.analyze_content(content_input)
        print(f"Analysis report: {report}")
        
        # Get dashboard
        dashboard = await analyzer.get_analysis_dashboard()
        print(f"Analysis dashboard: {dashboard}")
        
    finally:
        await analyzer.shutdown()


if __name__ == "__main__":
    asyncio.run(main())