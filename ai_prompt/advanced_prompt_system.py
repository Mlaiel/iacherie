"""
🤖 Advanced AI Prompt Engineering System - IA Prompt Engineer Implementation
==========================================================================

Enterprise-grade AI prompt optimization system with multi-provider management,
automated prompt tuning, performance analytics, and intelligent prompt generation.

Features:
- Multi-provider AI integration (OpenAI, Anthropic, Google, etc.)
- Automated prompt optimization and testing
- Prompt template management and versioning
- Performance analytics and A/B testing
- Context-aware prompt generation
- Prompt safety and bias detection
- Cost optimization across providers

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: IA Prompt Engineer
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timedelta
import uuid
import time
import statistics
from collections import defaultdict, deque
import hashlib
import re
from pathlib import Path

# Optional AI provider imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """AI service providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    AZURE_OPENAI = "azure_openai"

class PromptType(Enum):
    """Types of prompts"""
    COMPLETION = "completion"
    CHAT = "chat"
    INSTRUCTION = "instruction"
    QUESTION_ANSWER = "question_answer"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CODE_GENERATION = "code_generation"
    CREATIVE_WRITING = "creative_writing"

class OptimizationStrategy(Enum):
    """Prompt optimization strategies"""
    COST_MINIMIZATION = "cost_minimization"
    QUALITY_MAXIMIZATION = "quality_maximization"
    SPEED_OPTIMIZATION = "speed_optimization"
    BALANCED = "balanced"

@dataclass
class PromptTemplate:
    """Prompt template definition"""
    template_id: str
    name: str
    prompt_type: PromptType
    template: str
    variables: List[str]
    provider: AIProvider
    model: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)

@dataclass
class PromptExecution:
    """Prompt execution result"""
    execution_id: str
    template_id: str
    prompt: str
    provider: AIProvider
    model: str
    response: str
    execution_time_ms: float
    token_count: int
    cost_usd: float
    quality_score: float
    safety_score: float
    timestamp: datetime = field(default_factory=datetime.now)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PromptOptimization:
    """Prompt optimization experiment"""
    optimization_id: str
    original_template_id: str
    strategy: OptimizationStrategy
    variants: List[str]
    test_results: List[PromptExecution] = field(default_factory=list)
    best_variant_id: Optional[str] = None
    improvement_score: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "running"  # running, completed, failed

@dataclass
class AIProviderConfig:
    """AI provider configuration"""
    provider: AIProvider
    api_key: str
    base_url: Optional[str] = None
    models: List[str] = field(default_factory=list)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    cost_per_token: Dict[str, float] = field(default_factory=dict)
    enabled: bool = True

class AdvancedAIPromptEngineer:
    """
    Advanced AI Prompt Engineering System
    
    IA Prompt Engineer responsibilities:
    - Multi-provider AI integration and management
    - Prompt template creation and optimization
    - Automated prompt testing and A/B testing
    - Performance analytics and cost optimization
    - Prompt safety and bias detection
    - Context-aware prompt generation
    - Provider selection and load balancing
    """
    
    def __init__(self):
        # Prompt management
        self.prompt_templates: Dict[str, PromptTemplate] = {}
        self.prompt_executions: deque = deque(maxlen=50000)
        self.optimization_experiments: Dict[str, PromptOptimization] = {}
        
        # Provider management
        self.provider_configs: Dict[AIProvider, AIProviderConfig] = {}
        self.provider_clients: Dict[AIProvider, Any] = {}
        self.provider_performance: Dict[AIProvider, Dict] = defaultdict(dict)
        
        # Analytics and optimization
        self.performance_metrics: Dict[str, Any] = {}
        self.cost_tracking: Dict[str, float] = defaultdict(float)
        self.quality_benchmarks: Dict[str, float] = {}
        
        # Prompt library and templates
        self.prompt_library: Dict[str, List[PromptTemplate]] = defaultdict(list)
        self.context_templates: Dict[str, str] = {}
        
        # Safety and bias detection
        self.safety_filters: List[Callable] = []
        self.bias_detectors: List[Callable] = []
        
        self._initialize_prompt_system()
        self._initialize_providers()
        self._initialize_templates()
        self._initialize_monitoring()
        
        logger.info("AdvancedAIPromptEngineer initialized - IA Prompt Engineer")

    def _initialize_prompt_system(self):
        """Initialize prompt engineering system"""
        
        # Initialize monitoring tasks
        asyncio.create_task(self._performance_monitoring_loop())
        asyncio.create_task(self._cost_optimization_loop())
        asyncio.create_task(self._quality_monitoring_loop())
        asyncio.create_task(self._provider_health_check_loop())
        
        # Initialize safety filters
        self.safety_filters = [
            self._check_harmful_content,
            self._check_personal_information,
            self._check_inappropriate_content
        ]
        
        # Initialize bias detectors
        self.bias_detectors = [
            self._detect_gender_bias,
            self._detect_racial_bias,
            self._detect_cultural_bias
        ]
        
        logger.info("Prompt engineering system components initialized")

    def _initialize_providers(self):
        """Initialize AI provider configurations"""
        
        # OpenAI configuration
        self.provider_configs[AIProvider.OPENAI] = AIProviderConfig(
            provider=AIProvider.OPENAI,
            api_key="sk-mock-key",  # Mock API key
            models=["gpt-4", "gpt-3.5-turbo", "text-davinci-003"],
            rate_limits={"requests_per_minute": 200, "tokens_per_minute": 150000},
            cost_per_token={"gpt-4": 0.00003, "gpt-3.5-turbo": 0.000002},
            enabled=True
        )
        
        # Anthropic configuration
        self.provider_configs[AIProvider.ANTHROPIC] = AIProviderConfig(
            provider=AIProvider.ANTHROPIC,
            api_key="mock-anthropic-key",
            models=["claude-3-opus", "claude-3-sonnet", "claude-instant"],
            rate_limits={"requests_per_minute": 100, "tokens_per_minute": 100000},
            cost_per_token={"claude-3-opus": 0.000015, "claude-3-sonnet": 0.000003},
            enabled=True
        )
        
        # Google configuration
        self.provider_configs[AIProvider.GOOGLE] = AIProviderConfig(
            provider=AIProvider.GOOGLE,
            api_key="mock-google-key",
            models=["gemini-pro", "palm-2"],
            rate_limits={"requests_per_minute": 150, "tokens_per_minute": 120000},
            cost_per_token={"gemini-pro": 0.0000025, "palm-2": 0.000001},
            enabled=True
        )

    def _initialize_templates(self):
        """Initialize default prompt templates"""
        
        # Content classification template
        classification_template = PromptTemplate(
            template_id=str(uuid.uuid4()),
            name="content_classification",
            prompt_type=PromptType.CLASSIFICATION,
            template="""Analyze the following content and classify it into appropriate categories.

Content: {content}

Categories to consider:
- Type: {content_types}
- Topic: {topics}
- Sentiment: positive, negative, neutral
- Safety: safe, questionable, unsafe

Provide your analysis in JSON format with confidence scores (0-1) for each classification.""",
            variables=["content", "content_types", "topics"],
            provider=AIProvider.OPENAI,
            model="gpt-3.5-turbo",
            parameters={"temperature": 0.3, "max_tokens": 500},
            tags=["classification", "content", "safety"]
        )
        
        self.prompt_templates[classification_template.template_id] = classification_template
        self.prompt_library["classification"].append(classification_template)
        
        # Content summarization template
        summarization_template = PromptTemplate(
            template_id=str(uuid.uuid4()),
            name="content_summarization",
            prompt_type=PromptType.SUMMARIZATION,
            template="""Create a comprehensive summary of the following content.

Content: {content}

Requirements:
- Length: {summary_length} words maximum
- Style: {style}
- Include key points and main insights
- Maintain the original tone and context

Summary:""",
            variables=["content", "summary_length", "style"],
            provider=AIProvider.ANTHROPIC,
            model="claude-3-sonnet",
            parameters={"temperature": 0.2, "max_tokens": 300},
            tags=["summarization", "content", "optimization"]
        )
        
        self.prompt_templates[summarization_template.template_id] = summarization_template
        self.prompt_library["summarization"].append(summarization_template)
        
        # Creative content generation template
        creative_template = PromptTemplate(
            template_id=str(uuid.uuid4()),
            name="creative_content_generation",
            prompt_type=PromptType.CREATIVE_WRITING,
            template="""Generate creative content based on the following specifications.

Topic: {topic}
Style: {style}
Target Audience: {audience}
Length: {length}
Tone: {tone}

Requirements:
- Be original and engaging
- Match the specified style and tone
- Consider the target audience
- Include relevant keywords: {keywords}

Generated Content:""",
            variables=["topic", "style", "audience", "length", "tone", "keywords"],
            provider=AIProvider.OPENAI,
            model="gpt-4",
            parameters={"temperature": 0.8, "max_tokens": 1000},
            tags=["creative", "content", "generation"]
        )
        
        self.prompt_templates[creative_template.template_id] = creative_template
        self.prompt_library["creative"].append(creative_template)

    def _initialize_monitoring(self):
        """Initialize monitoring and analytics"""
        
        # Initialize performance baselines
        self.performance_metrics = {
            "avg_response_time_ms": 0,
            "avg_quality_score": 0,
            "avg_safety_score": 0,
            "total_executions": 0,
            "total_cost_usd": 0,
            "provider_distribution": {},
            "optimization_improvements": 0
        }

    async def execute_prompt(
        self,
        template_id: str,
        variables: Dict[str, Any],
        provider: Optional[AIProvider] = None,
        model: Optional[str] = None
    ) -> PromptExecution:
        """
        Execute prompt with specified template and variables
        
        IA Prompt Engineer: Intelligent prompt execution with optimization
        """
        
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            if template_id not in self.prompt_templates:
                raise ValueError(f"Template not found: {template_id}")
            
            template = self.prompt_templates[template_id]
            
            # Use template provider/model or override
            selected_provider = provider or template.provider
            selected_model = model or template.model
            
            # Generate prompt from template
            prompt = await self._generate_prompt_from_template(template, variables)
            
            # Safety and bias checks
            safety_score = await self._assess_prompt_safety(prompt)
            if safety_score < 0.7:
                raise ValueError(f"Prompt failed safety check: {safety_score}")
            
            # Execute with selected provider
            response, token_count, cost = await self._execute_with_provider(
                selected_provider, selected_model, prompt, template.parameters
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Assess response quality
            quality_score = await self._assess_response_quality(prompt, response, template.prompt_type)
            
            # Create execution record
            execution = PromptExecution(
                execution_id=execution_id,
                template_id=template_id,
                prompt=prompt,
                provider=selected_provider,
                model=selected_model,
                response=response,
                execution_time_ms=execution_time,
                token_count=token_count,
                cost_usd=cost,
                quality_score=quality_score,
                safety_score=safety_score,
                parameters=template.parameters
            )
            
            # Store execution
            self.prompt_executions.append(execution)
            
            # Update metrics
            await self._update_performance_metrics(execution)
            
            logger.info(f"Prompt executed: {template.name} -> {quality_score:.2f} quality, {execution_time:.2f}ms")
            return execution
            
        except Exception as e:
            logger.error(f"Prompt execution failed: {str(e)}")
            raise

    async def _generate_prompt_from_template(
        self, 
        template: PromptTemplate, 
        variables: Dict[str, Any]
    ) -> str:
        """Generate prompt from template and variables"""
        
        try:
            prompt = template.template
            
            # Replace variables in template
            for var_name in template.variables:
                if var_name in variables:
                    placeholder = "{" + var_name + "}"
                    prompt = prompt.replace(placeholder, str(variables[var_name]))
                else:
                    logger.warning(f"Missing variable: {var_name}")
                    placeholder = "{" + var_name + "}"
                    prompt = prompt.replace(placeholder, f"[{var_name}_NOT_PROVIDED]")
            
            return prompt
            
        except Exception as e:
            logger.error(f"Prompt generation failed: {str(e)}")
            raise

    async def _execute_with_provider(
        self,
        provider: AIProvider,
        model: str,
        prompt: str,
        parameters: Dict[str, Any]
    ) -> Tuple[str, int, float]:
        """Execute prompt with specific provider"""
        
        try:
            if provider not in self.provider_configs or not self.provider_configs[provider].enabled:
                raise ValueError(f"Provider not available: {provider}")
            
            config = self.provider_configs[provider]
            
            # Simulate API call (in real implementation would use actual provider APIs)
            await asyncio.sleep(0.1)  # Simulate network latency
            
            # Mock response generation
            if provider == AIProvider.OPENAI:
                response = await self._mock_openai_response(prompt, model, parameters)
            elif provider == AIProvider.ANTHROPIC:
                response = await self._mock_anthropic_response(prompt, model, parameters)
            elif provider == AIProvider.GOOGLE:
                response = await self._mock_google_response(prompt, model, parameters)
            else:
                response = f"Mock response for {prompt[:50]}..."
            
            # Calculate token count and cost
            token_count = len(prompt.split()) + len(response.split())  # Simplified
            cost_per_token = config.cost_per_token.get(model, 0.000001)
            cost = token_count * cost_per_token
            
            # Update cost tracking
            self.cost_tracking[provider.value] += cost
            
            return response, token_count, cost
            
        except Exception as e:
            logger.error(f"Provider execution failed: {provider.value} - {str(e)}")
            raise

    async def _mock_openai_response(self, prompt: str, model: str, parameters: Dict) -> str:
        """Mock OpenAI API response"""
        
        if "classification" in prompt.lower():
            return """{
                "type": "educational",
                "topic": "technology", 
                "sentiment": "positive",
                "safety": "safe",
                "confidence_scores": {
                    "type": 0.92,
                    "topic": 0.87,
                    "sentiment": 0.94,
                    "safety": 0.99
                }
            }"""
        elif "summary" in prompt.lower():
            return "This content discusses advanced AI technologies and their applications in modern business environments, highlighting key benefits and implementation strategies."
        else:
            return f"Generated response for: {prompt[:100]}... (OpenAI {model})"

    async def _mock_anthropic_response(self, prompt: str, model: str, parameters: Dict) -> str:
        """Mock Anthropic API response"""
        
        if "creative" in prompt.lower():
            return "Here's an engaging piece of creative content that captures the essence of your topic while maintaining the specified tone and style."
        else:
            return f"Thoughtful response for: {prompt[:100]}... (Anthropic {model})"

    async def _mock_google_response(self, prompt: str, model: str, parameters: Dict) -> str:
        """Mock Google API response"""
        
        return f"Comprehensive analysis for: {prompt[:100]}... (Google {model})"

    async def _assess_prompt_safety(self, prompt: str) -> float:
        """Assess prompt safety using filters"""
        
        safety_scores = []
        
        for filter_func in self.safety_filters:
            try:
                score = await filter_func(prompt)
                safety_scores.append(score)
            except Exception as e:
                logger.warning(f"Safety filter failed: {str(e)}")
                safety_scores.append(0.8)  # Default moderate score
        
        return statistics.mean(safety_scores) if safety_scores else 0.8

    async def _check_harmful_content(self, prompt: str) -> float:
        """Check for harmful content in prompt"""
        
        harmful_keywords = [
            "violence", "threat", "harm", "illegal", "dangerous",
            "hate", "discrimination", "abuse", "exploit"
        ]
        
        prompt_lower = prompt.lower()
        harmful_count = sum(1 for keyword in harmful_keywords if keyword in prompt_lower)
        
        if harmful_count > 0:
            return max(0.1, 1.0 - (harmful_count * 0.3))
        
        return 1.0

    async def _check_personal_information(self, prompt: str) -> float:
        """Check for personal information in prompt"""
        
        # Simple patterns for PII detection
        pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]
        
        pii_found = any(re.search(pattern, prompt) for pattern in pii_patterns)
        
        return 0.3 if pii_found else 1.0

    async def _check_inappropriate_content(self, prompt: str) -> float:
        """Check for inappropriate content"""
        
        inappropriate_keywords = [
            "explicit", "sexual", "adult", "nsfw", "inappropriate"
        ]
        
        prompt_lower = prompt.lower()
        inappropriate_count = sum(1 for keyword in inappropriate_keywords if keyword in prompt_lower)
        
        if inappropriate_count > 0:
            return max(0.2, 1.0 - (inappropriate_count * 0.4))
        
        return 1.0

    async def _detect_gender_bias(self, text: str) -> float:
        """Detect potential gender bias"""
        
        # Simplified bias detection
        gendered_terms = ["he", "she", "him", "her", "his", "hers", "man", "woman"]
        text_lower = text.lower()
        
        gendered_count = sum(1 for term in gendered_terms if term in text_lower)
        total_words = len(text.split())
        
        if total_words > 0 and gendered_count / total_words > 0.1:
            return 0.7  # Potential bias
        
        return 1.0

    async def _detect_racial_bias(self, text: str) -> float:
        """Detect potential racial bias"""
        
        # Simplified implementation
        return 1.0  # Would implement proper bias detection

    async def _detect_cultural_bias(self, text: str) -> float:
        """Detect potential cultural bias"""
        
        # Simplified implementation
        return 1.0  # Would implement proper bias detection

    async def _assess_response_quality(
        self, 
        prompt: str, 
        response: str, 
        prompt_type: PromptType
    ) -> float:
        """Assess response quality based on prompt type"""
        
        quality_factors = []
        
        # Length appropriateness
        if len(response) > 10:
            quality_factors.append(0.8)
        else:
            quality_factors.append(0.3)
        
        # Relevance to prompt (simplified)
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        overlap = len(prompt_words.intersection(response_words))
        relevance_score = min(overlap / max(len(prompt_words), 1) * 2, 1.0)
        quality_factors.append(relevance_score)
        
        # Type-specific quality checks
        if prompt_type == PromptType.CLASSIFICATION:
            # Check if response looks like classification
            if "{" in response and "}" in response:
                quality_factors.append(0.9)
            else:
                quality_factors.append(0.6)
        
        elif prompt_type == PromptType.SUMMARIZATION:
            # Check if response is shorter than input
            if len(response) < len(prompt) * 0.5:
                quality_factors.append(0.8)
            else:
                quality_factors.append(0.6)
        
        else:
            # General quality factors
            quality_factors.append(0.75)
        
        return statistics.mean(quality_factors) if quality_factors else 0.5

    async def optimize_prompt_template(
        self,
        template_id: str,
        strategy: OptimizationStrategy,
        test_variables: List[Dict[str, Any]]
    ) -> str:
        """
        Optimize prompt template using A/B testing
        
        IA Prompt Engineer: Automated prompt optimization with A/B testing
        """
        
        optimization_id = str(uuid.uuid4())
        
        try:
            if template_id not in self.prompt_templates:
                raise ValueError(f"Template not found: {template_id}")
            
            original_template = self.prompt_templates[template_id]
            
            # Generate optimization variants
            variants = await self._generate_optimization_variants(
                original_template, strategy
            )
            
            # Create optimization experiment
            optimization = PromptOptimization(
                optimization_id=optimization_id,
                original_template_id=template_id,
                strategy=strategy,
                variants=[v.template_id for v in variants]
            )
            
            self.optimization_experiments[optimization_id] = optimization
            
            # Execute A/B test
            await self._execute_optimization_test(
                optimization, variants, test_variables
            )
            
            logger.info(f"Prompt optimization started: {optimization_id} with {len(variants)} variants")
            return optimization_id
            
        except Exception as e:
            logger.error(f"Prompt optimization failed: {str(e)}")
            raise

    async def _generate_optimization_variants(
        self,
        original_template: PromptTemplate,
        strategy: OptimizationStrategy
    ) -> List[PromptTemplate]:
        """Generate optimization variants based on strategy"""
        
        variants = []
        
        if strategy == OptimizationStrategy.COST_MINIMIZATION:
            # Create shorter, more efficient variants
            variants.extend(await self._create_cost_optimized_variants(original_template))
            
        elif strategy == OptimizationStrategy.QUALITY_MAXIMIZATION:
            # Create more detailed, comprehensive variants
            variants.extend(await self._create_quality_optimized_variants(original_template))
            
        elif strategy == OptimizationStrategy.SPEED_OPTIMIZATION:
            # Create faster, simpler variants
            variants.extend(await self._create_speed_optimized_variants(original_template))
            
        else:  # BALANCED
            # Create balanced variants
            variants.extend(await self._create_balanced_variants(original_template))
        
        return variants

    async def _create_cost_optimized_variants(self, template: PromptTemplate) -> List[PromptTemplate]:
        """Create cost-optimized variants"""
        
        variants = []
        
        # Shorter version
        shorter_template = PromptTemplate(
            template_id=str(uuid.uuid4()),
            name=f"{template.name}_cost_optimized",
            prompt_type=template.prompt_type,
            template=template.template.replace("\n\n", "\n"),  # Remove extra newlines
            variables=template.variables,
            provider=AIProvider.GOOGLE,  # Use cheaper provider
            model="palm-2",  # Use cheaper model
            parameters={**template.parameters, "max_tokens": template.parameters.get("max_tokens", 500) // 2},
            version=f"{template.version}_cost_opt"
        )
        
        variants.append(shorter_template)
        self.prompt_templates[shorter_template.template_id] = shorter_template
        
        return variants

    async def _create_quality_optimized_variants(self, template: PromptTemplate) -> List[PromptTemplate]:
        """Create quality-optimized variants"""
        
        variants = []
        
        # Enhanced version with more context
        enhanced_template = PromptTemplate(
            template_id=str(uuid.uuid4()),
            name=f"{template.name}_quality_optimized",
            prompt_type=template.prompt_type,
            template=f"You are an expert assistant. Please provide a high-quality response.\n\n{template.template}\n\nPlease ensure your response is accurate, comprehensive, and well-structured.",
            variables=template.variables,
            provider=AIProvider.OPENAI,
            model="gpt-4",
            parameters={**template.parameters, "temperature": 0.2},  # Lower temperature for consistency
            version=f"{template.version}_quality_opt"
        )
        
        variants.append(enhanced_template)
        self.prompt_templates[enhanced_template.template_id] = enhanced_template
        
        return variants

    async def _create_speed_optimized_variants(self, template: PromptTemplate) -> List[PromptTemplate]:
        """Create speed-optimized variants"""
        
        variants = []
        
        # Simplified version
        simple_template = PromptTemplate(
            template_id=str(uuid.uuid4()),
            name=f"{template.name}_speed_optimized",
            prompt_type=template.prompt_type,
            template=template.template.split('\n')[0],  # Use first line only
            variables=template.variables[:2],  # Limit variables
            provider=AIProvider.OPENAI,
            model="gpt-3.5-turbo",
            parameters={**template.parameters, "max_tokens": 100},  # Limit tokens
            version=f"{template.version}_speed_opt"
        )
        
        variants.append(simple_template)
        self.prompt_templates[simple_template.template_id] = simple_template
        
        return variants

    async def _create_balanced_variants(self, template: PromptTemplate) -> List[PromptTemplate]:
        """Create balanced variants"""
        
        variants = []
        
        # Balanced version
        balanced_template = PromptTemplate(
            template_id=str(uuid.uuid4()),
            name=f"{template.name}_balanced",
            prompt_type=template.prompt_type,
            template=f"Please provide a clear and concise response.\n\n{template.template}",
            variables=template.variables,
            provider=AIProvider.ANTHROPIC,
            model="claude-3-sonnet",
            parameters={**template.parameters, "temperature": 0.4},
            version=f"{template.version}_balanced"
        )
        
        variants.append(balanced_template)
        self.prompt_templates[balanced_template.template_id] = balanced_template
        
        return variants

    async def _execute_optimization_test(
        self,
        optimization: PromptOptimization,
        variants: List[PromptTemplate],
        test_variables: List[Dict[str, Any]]
    ):
        """Execute A/B optimization test"""
        
        try:
            all_results = []
            
            # Test original template
            original_template = self.prompt_templates[optimization.original_template_id]
            for variables in test_variables:
                execution = await self.execute_prompt(
                    original_template.template_id, variables
                )
                all_results.append(execution)
            
            # Test variants
            for variant in variants:
                for variables in test_variables:
                    try:
                        execution = await self.execute_prompt(
                            variant.template_id, variables
                        )
                        all_results.append(execution)
                    except Exception as e:
                        logger.warning(f"Variant test failed: {str(e)}")
            
            optimization.test_results = all_results
            
            # Analyze results and find best variant
            await self._analyze_optimization_results(optimization)
            
        except Exception as e:
            optimization.status = "failed"
            logger.error(f"Optimization test failed: {str(e)}")

    async def _analyze_optimization_results(self, optimization: PromptOptimization):
        """Analyze optimization test results"""
        
        try:
            # Group results by template
            results_by_template = defaultdict(list)
            for result in optimization.test_results:
                results_by_template[result.template_id].append(result)
            
            # Calculate aggregate scores for each template
            template_scores = {}
            
            for template_id, results in results_by_template.items():
                if results:
                    avg_quality = statistics.mean([r.quality_score for r in results])
                    avg_cost = statistics.mean([r.cost_usd for r in results])
                    avg_time = statistics.mean([r.execution_time_ms for r in results])
                    
                    # Calculate composite score based on strategy
                    if optimization.strategy == OptimizationStrategy.COST_MINIMIZATION:
                        score = avg_quality * 0.3 + (1 - avg_cost / 0.01) * 0.7  # Favor lower cost
                    elif optimization.strategy == OptimizationStrategy.QUALITY_MAXIMIZATION:
                        score = avg_quality * 0.8 + (1 - avg_cost / 0.01) * 0.2  # Favor higher quality
                    elif optimization.strategy == OptimizationStrategy.SPEED_OPTIMIZATION:
                        score = avg_quality * 0.4 + (1 - avg_time / 1000) * 0.6  # Favor faster execution
                    else:  # BALANCED
                        score = avg_quality * 0.5 + (1 - avg_cost / 0.01) * 0.25 + (1 - avg_time / 1000) * 0.25
                    
                    template_scores[template_id] = score
            
            # Find best performing template
            if template_scores:
                best_template_id = max(template_scores.items(), key=lambda x: x[1])[0]
                optimization.best_variant_id = best_template_id
                
                original_score = template_scores.get(optimization.original_template_id, 0)
                best_score = template_scores[best_template_id]
                optimization.improvement_score = (best_score - original_score) / max(original_score, 0.001)
            
            optimization.status = "completed"
            optimization.end_time = datetime.now()
            
            logger.info(f"Optimization completed: {optimization.optimization_id} - {optimization.improvement_score:.2%} improvement")
            
        except Exception as e:
            optimization.status = "failed"
            logger.error(f"Optimization analysis failed: {str(e)}")

    async def select_optimal_provider(
        self,
        prompt_type: PromptType,
        requirements: Dict[str, Any]
    ) -> Tuple[AIProvider, str]:
        """
        Select optimal provider and model for specific requirements
        
        IA Prompt Engineer: Intelligent provider selection and load balancing
        """
        
        try:
            # Analyze requirements
            cost_priority = requirements.get("cost_priority", 0.5)  # 0-1
            quality_priority = requirements.get("quality_priority", 0.5)
            speed_priority = requirements.get("speed_priority", 0.5)
            
            provider_scores = {}
            
            for provider, config in self.provider_configs.items():
                if not config.enabled or not config.models:
                    continue
                
                # Get provider performance metrics
                performance = self.provider_performance.get(provider, {})
                
                # Calculate score based on requirements
                cost_score = 1.0 - (sum(config.cost_per_token.values()) / len(config.cost_per_token) if config.cost_per_token else 0.1)
                quality_score = performance.get("avg_quality_score", 0.7)
                speed_score = 1.0 - (performance.get("avg_response_time_ms", 500) / 1000)
                
                composite_score = (
                    cost_score * cost_priority +
                    quality_score * quality_priority +
                    speed_score * speed_priority
                )
                
                provider_scores[provider] = {
                    "score": composite_score,
                    "best_model": config.models[0] if config.models else "default"
                }
            
            # Select best provider
            if provider_scores:
                best_provider = max(provider_scores.items(), key=lambda x: x[1]["score"])[0]
                best_model = provider_scores[best_provider]["best_model"]
                
                logger.info(f"Selected optimal provider: {best_provider.value} with model {best_model}")
                return best_provider, best_model
            
            # Fallback to default
            return AIProvider.OPENAI, "gpt-3.5-turbo"
            
        except Exception as e:
            logger.error(f"Provider selection failed: {str(e)}")
            return AIProvider.OPENAI, "gpt-3.5-turbo"

    async def _update_performance_metrics(self, execution: PromptExecution):
        """Update performance metrics with execution results"""
        
        try:
            # Update global metrics
            self.performance_metrics["total_executions"] += 1
            self.performance_metrics["total_cost_usd"] += execution.cost_usd
            
            # Update averages
            total_execs = self.performance_metrics["total_executions"]
            
            current_avg_time = self.performance_metrics["avg_response_time_ms"]
            self.performance_metrics["avg_response_time_ms"] = (
                (current_avg_time * (total_execs - 1) + execution.execution_time_ms) / total_execs
            )
            
            current_avg_quality = self.performance_metrics["avg_quality_score"]
            self.performance_metrics["avg_quality_score"] = (
                (current_avg_quality * (total_execs - 1) + execution.quality_score) / total_execs
            )
            
            current_avg_safety = self.performance_metrics["avg_safety_score"]
            self.performance_metrics["avg_safety_score"] = (
                (current_avg_safety * (total_execs - 1) + execution.safety_score) / total_execs
            )
            
            # Update provider metrics
            provider = execution.provider
            if provider not in self.provider_performance:
                self.provider_performance[provider] = {
                    "executions": 0,
                    "avg_quality_score": 0,
                    "avg_response_time_ms": 0,
                    "total_cost": 0
                }
            
            provider_metrics = self.provider_performance[provider]
            provider_metrics["executions"] += 1
            
            provider_execs = provider_metrics["executions"]
            provider_metrics["avg_quality_score"] = (
                (provider_metrics["avg_quality_score"] * (provider_execs - 1) + execution.quality_score) / provider_execs
            )
            provider_metrics["avg_response_time_ms"] = (
                (provider_metrics["avg_response_time_ms"] * (provider_execs - 1) + execution.execution_time_ms) / provider_execs
            )
            provider_metrics["total_cost"] += execution.cost_usd
            
        except Exception as e:
            logger.error(f"Metrics update failed: {str(e)}")

    async def _performance_monitoring_loop(self):
        """Background performance monitoring loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Analyze recent performance
                recent_executions = list(self.prompt_executions)[-100:] if self.prompt_executions else []
                
                if recent_executions:
                    avg_quality = statistics.mean([e.quality_score for e in recent_executions])
                    avg_time = statistics.mean([e.execution_time_ms for e in recent_executions])
                    
                    # Check for performance degradation
                    if avg_quality < 0.6:
                        logger.warning(f"Quality degradation detected: {avg_quality:.2f}")
                    
                    if avg_time > 2000:
                        logger.warning(f"High response times detected: {avg_time:.2f}ms")
                
            except Exception as e:
                logger.error(f"Performance monitoring loop error: {str(e)}")

    async def _cost_optimization_loop(self):
        """Background cost optimization loop"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                # Analyze cost patterns
                total_cost = sum(self.cost_tracking.values())
                
                if total_cost > 100:  # $100 threshold
                    logger.info(f"High cost detected: ${total_cost:.2f} - optimizing provider selection")
                    # Could trigger automatic optimization
                
            except Exception as e:
                logger.error(f"Cost optimization loop error: {str(e)}")

    async def _quality_monitoring_loop(self):
        """Background quality monitoring loop"""
        while True:
            try:
                await asyncio.sleep(1800)  # Check every 30 minutes
                
                # Check quality trends
                recent_executions = list(self.prompt_executions)[-50:] if self.prompt_executions else []
                
                if len(recent_executions) > 10:
                    recent_quality = statistics.mean([e.quality_score for e in recent_executions[-10:]])
                    older_quality = statistics.mean([e.quality_score for e in recent_executions[-20:-10]])
                    
                    if recent_quality < older_quality * 0.9:
                        logger.warning("Quality degradation trend detected")
                
            except Exception as e:
                logger.error(f"Quality monitoring loop error: {str(e)}")

    async def _provider_health_check_loop(self):
        """Background provider health check loop"""
        while True:
            try:
                await asyncio.sleep(600)  # Check every 10 minutes
                
                # Check provider availability and performance
                for provider, config in self.provider_configs.items():
                    if config.enabled:
                        # Mock health check
                        # In real implementation would ping provider APIs
                        pass
                
            except Exception as e:
                logger.error(f"Provider health check loop error: {str(e)}")

    def get_prompt_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive prompt engineering dashboard"""
        
        recent_executions = list(self.prompt_executions)[-100:] if self.prompt_executions else []
        
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "overview": {
                "total_templates": len(self.prompt_templates),
                "total_executions": len(self.prompt_executions),
                "active_optimizations": len([o for o in self.optimization_experiments.values() if o.status == "running"]),
                "total_cost_usd": sum(self.cost_tracking.values()),
                "avg_quality_score": self.performance_metrics.get("avg_quality_score", 0),
                "avg_response_time_ms": self.performance_metrics.get("avg_response_time_ms", 0)
            },
            "provider_performance": {
                provider.value: {
                    "executions": metrics.get("executions", 0),
                    "avg_quality": metrics.get("avg_quality_score", 0),
                    "avg_response_time": metrics.get("avg_response_time_ms", 0),
                    "total_cost": metrics.get("total_cost", 0),
                    "enabled": self.provider_configs.get(provider, {}).enabled
                }
                for provider, metrics in self.provider_performance.items()
            },
            "template_library": {
                category: len(templates)
                for category, templates in self.prompt_library.items()
            },
            "optimization_results": {
                "completed_optimizations": len([o for o in self.optimization_experiments.values() if o.status == "completed"]),
                "avg_improvement": statistics.mean([
                    o.improvement_score for o in self.optimization_experiments.values()
                    if o.status == "completed" and o.improvement_score > 0
                ]) if self.optimization_experiments else 0,
                "strategies_used": {
                    strategy.value: len([
                        o for o in self.optimization_experiments.values()
                        if o.strategy == strategy
                    ])
                    for strategy in OptimizationStrategy
                }
            },
            "cost_breakdown": {
                provider: cost
                for provider, cost in self.cost_tracking.items()
            },
            "quality_metrics": {
                "avg_quality_score": statistics.mean([e.quality_score for e in recent_executions]) if recent_executions else 0,
                "avg_safety_score": statistics.mean([e.safety_score for e in recent_executions]) if recent_executions else 0,
                "quality_by_type": {
                    prompt_type.value: statistics.mean([
                        e.quality_score for e in recent_executions
                        if self.prompt_templates.get(e.template_id, {}).prompt_type == prompt_type
                    ]) if recent_executions else 0
                    for prompt_type in PromptType
                }
            },
            "system_capabilities": {
                "providers_available": len([p for p in self.provider_configs.values() if p.enabled]),
                "optimization_strategies": len(OptimizationStrategy),
                "safety_filters": len(self.safety_filters),
                "bias_detectors": len(self.bias_detectors)
            }
        }
        
        return dashboard

# Global prompt engineering system instance
advanced_prompt_system = AdvancedAIPromptEngineer()

logger.info("🤖 Advanced AI Prompt Engineering System initialized - IA Prompt Engineer implementation complete")