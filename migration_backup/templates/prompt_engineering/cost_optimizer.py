"""
🎯 Cost Optimizer - AI Token Cost Management & Optimization System
================================================================

Enterprise-grade cost optimization for AI token usage with intelligent
routing, caching, and creator economy budget management.

⚠️  PROTECTION INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Tous droits réservés - Usage commercial interdit sans autorisation

Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer + Backend Senior + DevOps Expert
Team: Lead Dev IA + Backend Senior + ML Engineer + Security Expert
"""

import asyncio
import logging
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from pydantic import BaseModel, Field, validator
import tiktoken

from core.config import get_settings
from utils.exceptions import CostOptimizationError, ValidationError
from monitoring.prompt_metrics import PromptMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class CostTier(Enum):
    """Cost optimization tiers"""
    ECONOMY = "economy"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class OptimizationStrategy(Enum):
    """Cost optimization strategies"""
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    CREATOR_FOCUSED = "creator_focused"
    REVENUE_OPTIMIZED = "revenue_optimized"


class BudgetPeriod(Enum):
    """Budget tracking periods"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class CostModel(Enum):
    """Pricing models"""
    PER_TOKEN = "per_token"
    PER_REQUEST = "per_request"
    SUBSCRIPTION = "subscription"
    TIERED = "tiered"
    CREATOR_REVENUE_SHARE = "creator_revenue_share"


@dataclass
class ModelPricing:
    """Model pricing configuration"""
    model_name: str
    provider: str
    input_cost_per_1k: float
    output_cost_per_1k: float
    context_window: int
    quality_tier: str
    speed_tier: str
    special_capabilities: List[str] = field(default_factory=list)
    creator_economy_discount: float = 0.0
    volume_discounts: Dict[int, float] = field(default_factory=dict)
    effective_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CostEstimate:
    """Cost estimation result"""
    estimated_cost: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model_name: str
    confidence: float
    cost_breakdown: Dict[str, float]
    optimization_suggestions: List[str] = field(default_factory=list)
    alternative_models: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class BudgetUsage:
    """Budget usage tracking"""
    period: BudgetPeriod
    allocated_budget: float
    used_budget: float
    remaining_budget: float
    usage_percentage: float
    projected_overage: float
    cost_per_creator: Dict[str, float] = field(default_factory=dict)
    cost_per_template: Dict[str, float] = field(default_factory=dict)
    optimization_savings: float = 0.0


@dataclass
class CostOptimizationResult:
    """Cost optimization result"""
    original_cost: float
    optimized_cost: float
    savings_amount: float
    savings_percentage: float
    recommended_model: str
    strategy_used: OptimizationStrategy
    confidence_score: float
    trade_offs: Dict[str, Any]
    implementation_notes: List[str] = field(default_factory=list)


class CostOptimizerConfig(BaseModel):
    """Cost optimizer configuration"""
    daily_budget_limit: float = Field(default=100.0, ge=0.0)
    monthly_budget_limit: float = Field(default=3000.0, ge=0.0)
    cost_threshold_warning: float = Field(default=0.8, ge=0.0, le=1.0)
    enable_auto_optimization: bool = True
    enable_caching: bool = True
    cache_ttl_seconds: int = Field(default=3600, ge=60, le=86400)
    enable_budget_alerts: bool = True
    creator_economy_priority: bool = True
    quality_vs_cost_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    enable_predictive_scaling: bool = True
    volume_discount_threshold: int = Field(default=10000, ge=100)
    enable_real_time_monitoring: bool = True


class CostOptimizer:
    """
    🎯 Enterprise Cost Optimization System
    
    Intelligent cost management with:
    - Real-time token cost calculation
    - Multi-model pricing optimization
    - Budget tracking and alerts
    - Creator economy cost management
    - Predictive cost analysis
    - Automated optimization strategies
    - Volume discount management
    - Performance vs cost trade-off analysis
    """
    
    def __init__(self, config: Optional[CostOptimizerConfig] = None):
        self.config = config or CostOptimizerConfig()
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.model_pricing: Dict[str, ModelPricing] = {}
        self.token_encoders: Dict[str, Any] = {}
        self.cost_models: Dict[str, LinearRegression] = {}
        self.metrics_collector = PromptMetricsCollector()
        self._budget_cache: Dict[str, BudgetUsage] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize cost optimization system"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                retry_on_timeout=True
            )
            
            # Initialize PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=3,
                max_size=15,
                command_timeout=30
            )
            
            # Load model pricing
            await self._load_model_pricing()
            
            # Initialize token encoders
            await self._initialize_token_encoders()
            
            # Load cost prediction models
            await self._load_cost_models()
            
            # Create database tables
            await self._create_tables()
            
            # Start background tasks
            asyncio.create_task(self._budget_monitoring_task())
            asyncio.create_task(self._cost_optimization_task())
            
            self._initialized = True
            logger.info("Cost Optimizer initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Cost Optimizer: {e}")
            raise CostOptimizationError(f"Cost Optimizer initialization failed: {e}")
    
    async def _load_model_pricing(self) -> None:
        """Load model pricing configurations"""
        # Current market pricing (as of 2024)
        self.model_pricing = {
            "gpt-4": ModelPricing(
                model_name="gpt-4",
                provider="openai",
                input_cost_per_1k=0.03,
                output_cost_per_1k=0.06,
                context_window=8192,
                quality_tier="premium",
                speed_tier="medium",
                special_capabilities=["reasoning", "coding", "analysis"],
                creator_economy_discount=0.1,
                volume_discounts={10000: 0.05, 50000: 0.1, 100000: 0.15}
            ),
            "gpt-4-turbo": ModelPricing(
                model_name="gpt-4-turbo",
                provider="openai",
                input_cost_per_1k=0.01,
                output_cost_per_1k=0.03,
                context_window=128000,
                quality_tier="premium",
                speed_tier="fast",
                special_capabilities=["large_context", "multimodal"],
                creator_economy_discount=0.15,
                volume_discounts={10000: 0.08, 50000: 0.12, 100000: 0.18}
            ),
            "gpt-3.5-turbo": ModelPricing(
                model_name="gpt-3.5-turbo",
                provider="openai",
                input_cost_per_1k=0.0015,
                output_cost_per_1k=0.002,
                context_window=4096,
                quality_tier="standard",
                speed_tier="fast",
                special_capabilities=["chat"],
                creator_economy_discount=0.2,
                volume_discounts={10000: 0.1, 50000: 0.15, 100000: 0.25}
            ),
            "claude-3-opus": ModelPricing(
                model_name="claude-3-opus",
                provider="anthropic",
                input_cost_per_1k=0.015,
                output_cost_per_1k=0.075,
                context_window=200000,
                quality_tier="premium",
                speed_tier="medium",
                special_capabilities=["reasoning", "large_context"],
                creator_economy_discount=0.12,
                volume_discounts={10000: 0.06, 50000: 0.12, 100000: 0.18}
            ),
            "claude-3-sonnet": ModelPricing(
                model_name="claude-3-sonnet",
                provider="anthropic",
                input_cost_per_1k=0.003,
                output_cost_per_1k=0.015,
                context_window=200000,
                quality_tier="standard",
                speed_tier="fast",
                special_capabilities=["balanced", "large_context"],
                creator_economy_discount=0.15,
                volume_discounts={10000: 0.08, 50000: 0.15, 100000: 0.22}
            ),
            "claude-3-haiku": ModelPricing(
                model_name="claude-3-haiku",
                provider="anthropic",
                input_cost_per_1k=0.00025,
                output_cost_per_1k=0.00125,
                context_window=200000,
                quality_tier="economy",
                speed_tier="very_fast",
                special_capabilities=["speed", "large_context"],
                creator_economy_discount=0.25,
                volume_discounts={10000: 0.12, 50000: 0.2, 100000: 0.3}
            ),
            "gemini-pro": ModelPricing(
                model_name="gemini-pro",
                provider="google",
                input_cost_per_1k=0.00025,
                output_cost_per_1k=0.0005,
                context_window=32768,
                quality_tier="standard",
                speed_tier="fast",
                special_capabilities=["multimodal", "free_tier"],
                creator_economy_discount=0.3,
                volume_discounts={10000: 0.15, 50000: 0.25, 100000: 0.35}
            ),
            "command": ModelPricing(
                model_name="command",
                provider="cohere",
                input_cost_per_1k=0.001,
                output_cost_per_1k=0.002,
                context_window=4096,
                quality_tier="economy",
                speed_tier="fast",
                special_capabilities=["embeddings", "summarization"],
                creator_economy_discount=0.2,
                volume_discounts={10000: 0.1, 50000: 0.18, 100000: 0.28}
            )
        }
    
    async def _initialize_token_encoders(self) -> None:
        """Initialize token encoders for different models"""
        try:
            # OpenAI encoders
            self.token_encoders["gpt-4"] = tiktoken.get_encoding("cl100k_base")
            self.token_encoders["gpt-4-turbo"] = tiktoken.get_encoding("cl100k_base")
            self.token_encoders["gpt-3.5-turbo"] = tiktoken.get_encoding("cl100k_base")
            
            # For other providers, use approximation
            self.token_encoders["claude-3-opus"] = tiktoken.get_encoding("cl100k_base")
            self.token_encoders["claude-3-sonnet"] = tiktoken.get_encoding("cl100k_base")
            self.token_encoders["claude-3-haiku"] = tiktoken.get_encoding("cl100k_base")
            self.token_encoders["gemini-pro"] = tiktoken.get_encoding("cl100k_base")
            self.token_encoders["command"] = tiktoken.get_encoding("cl100k_base")
            
            logger.info("Token encoders initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize token encoders: {e}")
    
    async def _load_cost_models(self) -> None:
        """Load ML models for cost prediction"""
        try:
            # Load historical data for model training
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT input_tokens, output_tokens, actual_cost, model_name
                    FROM cost_tracking 
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    AND actual_cost > 0
                """)
            
            if len(rows) < 100:  # Need minimum data for training
                logger.info("Insufficient data for cost model training, using default pricing")
                return
            
            # Group by model and train prediction models
            model_data = {}
            for row in rows:
                model_name = row['model_name']
                if model_name not in model_data:
                    model_data[model_name] = {'X': [], 'y': []}
                
                model_data[model_name]['X'].append([row['input_tokens'], row['output_tokens']])
                model_data[model_name]['y'].append(row['actual_cost'])
            
            # Train models
            for model_name, data in model_data.items():
                if len(data['X']) >= 20:  # Minimum samples per model
                    X = np.array(data['X'])
                    y = np.array(data['y'])
                    
                    # Use Random Forest for better accuracy
                    rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
                    rf_model.fit(X, y)
                    self.cost_models[model_name] = rf_model
            
            logger.info(f"Trained cost models for {len(self.cost_models)} models")
        
        except Exception as e:
            logger.error(f"Failed to load cost models: {e}")
    
    async def _create_tables(self) -> None:
        """Create cost tracking database tables"""
        create_cost_tracking_table = """
        CREATE TABLE IF NOT EXISTS cost_tracking (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(255),
            template_id VARCHAR(255),
            model_name VARCHAR(100) NOT NULL,
            input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL,
            total_tokens INTEGER NOT NULL,
            estimated_cost FLOAT NOT NULL,
            actual_cost FLOAT,
            savings_amount FLOAT DEFAULT 0,
            optimization_strategy VARCHAR(50),
            creator_context JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (model_name, created_at),
            INDEX (template_id, created_at),
            INDEX (creator_context->>'creator_id', created_at)
        );
        """
        
        create_budget_tracking_table = """
        CREATE TABLE IF NOT EXISTS budget_tracking (
            id SERIAL PRIMARY KEY,
            budget_id VARCHAR(255) UNIQUE NOT NULL,
            period VARCHAR(20) NOT NULL,
            period_start TIMESTAMP NOT NULL,
            period_end TIMESTAMP NOT NULL,
            allocated_budget FLOAT NOT NULL,
            used_budget FLOAT DEFAULT 0,
            creator_id VARCHAR(255),
            template_category VARCHAR(100),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_optimization_history_table = """
        CREATE TABLE IF NOT EXISTS optimization_history (
            id SERIAL PRIMARY KEY,
            optimization_id VARCHAR(255) UNIQUE NOT NULL,
            original_model VARCHAR(100),
            optimized_model VARCHAR(100),
            original_cost FLOAT,
            optimized_cost FLOAT,
            savings_percentage FLOAT,
            quality_impact FLOAT,
            strategy_used VARCHAR(50),
            template_id VARCHAR(255),
            creator_context JSONB,
            applied BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_cost_tracking_table)
            await conn.execute(create_budget_tracking_table)
            await conn.execute(create_optimization_history_table)
    
    async def estimate_cost(
        self,
        prompt: str,
        model_name: str,
        expected_output_length: Optional[int] = None,
        creator_context: Optional[Dict[str, Any]] = None
    ) -> CostEstimate:
        """
        Estimate cost for a prompt with given model
        
        Args:
            prompt: Input prompt text
            model_name: Model to use for estimation
            expected_output_length: Expected output tokens (optional)
            creator_context: Creator context for discounts
            
        Returns:
            Cost estimation with optimization suggestions
        """
        try:
            # Get model pricing
            if model_name not in self.model_pricing:
                raise CostOptimizationError(f"Pricing not available for model: {model_name}")
            
            pricing = self.model_pricing[model_name]
            
            # Count input tokens
            input_tokens = await self._count_tokens(prompt, model_name)
            
            # Estimate output tokens
            if expected_output_length:
                output_tokens = expected_output_length
            else:
                output_tokens = await self._estimate_output_tokens(prompt, model_name)
            
            total_tokens = input_tokens + output_tokens
            
            # Calculate base cost
            input_cost = (input_tokens / 1000) * pricing.input_cost_per_1k
            output_cost = (output_tokens / 1000) * pricing.output_cost_per_1k
            base_cost = input_cost + output_cost
            
            # Apply discounts
            final_cost = base_cost
            
            # Creator economy discount
            if creator_context and self.config.creator_economy_priority:
                final_cost *= (1 - pricing.creator_economy_discount)
            
            # Volume discount
            monthly_tokens = await self._get_monthly_token_usage(creator_context)
            volume_discount = self._calculate_volume_discount(monthly_tokens, pricing.volume_discounts)
            final_cost *= (1 - volume_discount)
            
            # Cost breakdown
            cost_breakdown = {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "base_cost": base_cost,
                "creator_discount": base_cost * pricing.creator_economy_discount if creator_context else 0,
                "volume_discount": base_cost * volume_discount,
                "final_cost": final_cost
            }
            
            # Generate optimization suggestions
            suggestions = await self._generate_cost_suggestions(
                prompt, model_name, input_tokens, output_tokens, final_cost
            )
            
            # Find alternative models
            alternatives = await self._find_alternative_models(
                model_name, input_tokens, output_tokens, creator_context
            )
            
            # Calculate confidence based on historical data
            confidence = await self._calculate_cost_confidence(model_name, input_tokens, output_tokens)
            
            return CostEstimate(
                estimated_cost=final_cost,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                model_name=model_name,
                confidence=confidence,
                cost_breakdown=cost_breakdown,
                optimization_suggestions=suggestions,
                alternative_models=alternatives
            )
        
        except Exception as e:
            logger.error(f"Cost estimation failed: {e}")
            raise CostOptimizationError(f"Cost estimation failed: {e}")
    
    async def _count_tokens(self, text: str, model_name: str) -> int:
        """Count tokens for given text and model"""
        try:
            if model_name in self.token_encoders:
                encoder = self.token_encoders[model_name]
                return len(encoder.encode(text))
            else:
                # Fallback approximation
                return int(len(text.split()) * 1.3)
        
        except Exception as e:
            logger.warning(f"Token counting failed for {model_name}: {e}")
            return int(len(text.split()) * 1.3)
    
    async def _estimate_output_tokens(self, prompt: str, model_name: str) -> int:
        """Estimate output tokens based on prompt characteristics"""
        try:
            # Use ML model if available
            if model_name in self.cost_models:
                input_tokens = await self._count_tokens(prompt, model_name)
                predicted_cost = self.cost_models[model_name].predict([[input_tokens, 0]])[0]
                pricing = self.model_pricing[model_name]
                
                # Reverse engineer output tokens from predicted cost
                estimated_output = max(100, int((predicted_cost * 1000) / pricing.output_cost_per_1k))
                return min(estimated_output, 4000)  # Cap at reasonable limit
            
            # Heuristic estimation
            prompt_length = len(prompt.split())
            
            if "summarize" in prompt.lower() or "summary" in prompt.lower():
                return max(50, min(prompt_length // 4, 500))  # Summary is typically shorter
            elif "explain" in prompt.lower() or "describe" in prompt.lower():
                return max(100, min(prompt_length * 2, 1000))  # Explanations can be longer
            elif "list" in prompt.lower() or "bullet" in prompt.lower():
                return max(80, min(prompt_length, 400))  # Lists are structured
            elif "write" in prompt.lower() or "create" in prompt.lower():
                return max(200, min(prompt_length * 3, 2000))  # Creative content
            else:
                return max(100, min(prompt_length, 800))  # Default estimation
        
        except Exception as e:
            logger.warning(f"Output token estimation failed: {e}")
            return 500  # Conservative default
    
    async def _get_monthly_token_usage(self, creator_context: Optional[Dict[str, Any]]) -> int:
        """Get monthly token usage for volume discount calculation"""
        try:
            if not creator_context or 'creator_id' not in creator_context:
                return 0
            
            creator_id = creator_context['creator_id']
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT SUM(total_tokens) as total_tokens
                    FROM cost_tracking 
                    WHERE creator_context->>'creator_id' = $1
                    AND created_at >= $2
                """, creator_id, month_start)
                
                return int(row['total_tokens'] or 0)
        
        except Exception as e:
            logger.warning(f"Failed to get monthly token usage: {e}")
            return 0
    
    def _calculate_volume_discount(self, token_count: int, volume_discounts: Dict[int, float]) -> float:
        """Calculate volume discount based on token usage"""
        if not volume_discounts:
            return 0.0
        
        applicable_discount = 0.0
        for threshold, discount in sorted(volume_discounts.items(), reverse=True):
            if token_count >= threshold:
                applicable_discount = discount
                break
        
        return applicable_discount
    
    async def _generate_cost_suggestions(
        self,
        prompt: str,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        cost: float
    ) -> List[str]:
        """Generate cost optimization suggestions"""
        suggestions = []
        
        # High cost warning
        if cost > 0.50:
            suggestions.append("Consider using a more cost-effective model for this task")
        
        # Long prompt optimization
        if input_tokens > 3000:
            suggestions.append("Consider summarizing or breaking down the prompt to reduce token count")
        
        # Model-specific suggestions
        if model_name in ["gpt-4", "claude-3-opus"] and cost > 0.20:
            suggestions.append("Consider using GPT-4 Turbo or Claude-3 Sonnet for better cost efficiency")
        
        # Caching suggestion
        if await self._is_cacheable_prompt(prompt):
            suggestions.append("This prompt type benefits from caching - enable response caching")
        
        # Batch processing
        if "analyze" in prompt.lower() or "process" in prompt.lower():
            suggestions.append("Consider batch processing multiple items together to reduce per-item costs")
        
        return suggestions
    
    async def _find_alternative_models(
        self,
        current_model: str,
        input_tokens: int,
        output_tokens: int,
        creator_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find alternative models with cost comparison"""
        alternatives = []
        
        try:
            current_pricing = self.model_pricing[current_model]
            current_cost = await self._calculate_model_cost(
                current_model, input_tokens, output_tokens, creator_context
            )
            
            for model_name, pricing in self.model_pricing.items():
                if model_name == current_model:
                    continue
                
                # Check if alternative can handle the context
                if input_tokens + output_tokens > pricing.context_window:
                    continue
                
                alt_cost = await self._calculate_model_cost(
                    model_name, input_tokens, output_tokens, creator_context
                )
                
                savings = current_cost - alt_cost
                savings_percentage = (savings / current_cost) * 100 if current_cost > 0 else 0
                
                # Quality comparison (simplified)
                quality_score = self._compare_model_quality(current_model, model_name)
                
                alternatives.append({
                    "model_name": model_name,
                    "estimated_cost": alt_cost,
                    "savings_amount": savings,
                    "savings_percentage": savings_percentage,
                    "quality_tier": pricing.quality_tier,
                    "speed_tier": pricing.speed_tier,
                    "quality_score": quality_score,
                    "recommendation": "consider" if savings > 0.01 and quality_score >= 0.8 else "evaluate"
                })
            
            # Sort by savings potential
            alternatives.sort(key=lambda x: x['savings_percentage'], reverse=True)
            return alternatives[:5]  # Top 5 alternatives
        
        except Exception as e:
            logger.error(f"Failed to find alternative models: {e}")
            return []
    
    def _compare_model_quality(self, current_model: str, alternative_model: str) -> float:
        """Compare quality between models (simplified scoring)"""
        quality_tiers = {
            "premium": 1.0,
            "standard": 0.8,
            "economy": 0.6
        }
        
        current_tier = self.model_pricing[current_model].quality_tier
        alt_tier = self.model_pricing[alternative_model].quality_tier
        
        current_score = quality_tiers.get(current_tier, 0.7)
        alt_score = quality_tiers.get(alt_tier, 0.7)
        
        return alt_score / current_score
    
    async def _calculate_model_cost(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        creator_context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate cost for specific model and token counts"""
        try:
            pricing = self.model_pricing[model_name]
            
            input_cost = (input_tokens / 1000) * pricing.input_cost_per_1k
            output_cost = (output_tokens / 1000) * pricing.output_cost_per_1k
            base_cost = input_cost + output_cost
            
            # Apply discounts
            final_cost = base_cost
            
            if creator_context and self.config.creator_economy_priority:
                final_cost *= (1 - pricing.creator_economy_discount)
            
            monthly_tokens = await self._get_monthly_token_usage(creator_context)
            volume_discount = self._calculate_volume_discount(monthly_tokens, pricing.volume_discounts)
            final_cost *= (1 - volume_discount)
            
            return final_cost
        
        except Exception as e:
            logger.error(f"Cost calculation failed for {model_name}: {e}")
            return 0.0
    
    async def _calculate_cost_confidence(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate confidence in cost estimation"""
        try:
            # If we have a trained model, use its confidence
            if model_name in self.cost_models:
                # Check prediction variance on similar requests
                async with self.db_pool.acquire() as conn:
                    rows = await conn.fetch("""
                        SELECT actual_cost, estimated_cost
                        FROM cost_tracking 
                        WHERE model_name = $1
                        AND input_tokens BETWEEN $2 AND $3
                        AND output_tokens BETWEEN $4 AND $5
                        AND actual_cost IS NOT NULL
                        ORDER BY created_at DESC
                        LIMIT 50
                    """, model_name, 
                        int(input_tokens * 0.8), int(input_tokens * 1.2),
                        int(output_tokens * 0.8), int(output_tokens * 1.2))
                
                if len(rows) >= 5:
                    errors = [abs(row['actual_cost'] - row['estimated_cost']) / row['actual_cost'] 
                             for row in rows if row['actual_cost'] > 0]
                    avg_error = sum(errors) / len(errors)
                    confidence = max(0.1, 1.0 - avg_error)
                    return confidence
            
            # Default confidence based on model stability
            stable_models = ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"]
            return 0.9 if model_name in stable_models else 0.7
        
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {e}")
            return 0.7
    
    async def _is_cacheable_prompt(self, prompt: str) -> bool:
        """Determine if prompt is suitable for caching"""
        # Check for dynamic content
        dynamic_indicators = [
            "today", "now", "current", "latest", "recent", "this week", "this month",
            "real-time", "live", "breaking", "update", "new"
        ]
        
        prompt_lower = prompt.lower()
        has_dynamic_content = any(indicator in prompt_lower for indicator in dynamic_indicators)
        
        # Check for personalization
        personal_indicators = ["my", "mine", "i am", "i'm", "personal", "private"]
        has_personal_content = any(indicator in prompt_lower for indicator in personal_indicators)
        
        return not (has_dynamic_content or has_personal_content)
    
    async def optimize_cost(
        self,
        prompt: str,
        current_model: str,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        creator_context: Optional[Dict[str, Any]] = None,
        quality_threshold: float = 0.8
    ) -> CostOptimizationResult:
        """
        Optimize cost for a given prompt and model
        
        Args:
            prompt: Input prompt
            current_model: Current model selection
            strategy: Optimization strategy
            creator_context: Creator context for personalized optimization
            quality_threshold: Minimum quality threshold
            
        Returns:
            Cost optimization result with recommendations
        """
        try:
            # Get current cost estimate
            current_estimate = await self.estimate_cost(prompt, current_model, None, creator_context)
            original_cost = current_estimate.estimated_cost
            
            best_cost = original_cost
            best_model = current_model
            trade_offs = {}
            
            # Strategy-specific optimization
            if strategy == OptimizationStrategy.AGGRESSIVE:
                # Find cheapest viable option
                alternatives = current_estimate.alternative_models
                viable_alternatives = [
                    alt for alt in alternatives 
                    if alt['quality_score'] >= quality_threshold * 0.8  # Lower quality threshold
                ]
                
                if viable_alternatives:
                    best_alternative = min(viable_alternatives, key=lambda x: x['estimated_cost'])
                    best_cost = best_alternative['estimated_cost']
                    best_model = best_alternative['model_name']
                    trade_offs['quality_impact'] = 1 - best_alternative['quality_score']
                    trade_offs['speed_change'] = "may_vary"
            
            elif strategy == OptimizationStrategy.BALANCED:
                # Balance cost and quality
                alternatives = current_estimate.alternative_models
                scored_alternatives = []
                
                for alt in alternatives:
                    if alt['quality_score'] >= quality_threshold:
                        # Balanced score: 60% cost savings, 40% quality retention
                        score = (alt['savings_percentage'] * 0.6) + (alt['quality_score'] * 40)
                        scored_alternatives.append((score, alt))
                
                if scored_alternatives:
                    best_score, best_alternative = max(scored_alternatives, key=lambda x: x[0])
                    if best_alternative['estimated_cost'] < original_cost:
                        best_cost = best_alternative['estimated_cost']
                        best_model = best_alternative['model_name']
                        trade_offs['quality_impact'] = 1 - best_alternative['quality_score']
            
            elif strategy == OptimizationStrategy.CREATOR_FOCUSED:
                # Optimize for creator economy specific needs
                if creator_context and creator_context.get('creator_type'):
                    creator_type = creator_context['creator_type']
                    
                    # Creator-specific model preferences
                    creator_preferences = {
                        'musician': ['claude-3-sonnet', 'gpt-4-turbo'],  # Creative tasks
                        'blogger': ['gpt-3.5-turbo', 'claude-3-haiku'],  # Content generation
                        'photographer': ['gemini-pro', 'gpt-4-turbo'],  # Visual descriptions
                        'educator': ['claude-3-sonnet', 'gpt-4']  # Detailed explanations
                    }
                    
                    preferred_models = creator_preferences.get(creator_type, [])
                    
                    for model in preferred_models:
                        if model in self.model_pricing:
                            estimate = await self.estimate_cost(prompt, model, None, creator_context)
                            if estimate.estimated_cost < best_cost:
                                best_cost = estimate.estimated_cost
                                best_model = model
                                trade_offs['creator_optimized'] = True
            
            # Calculate savings
            savings_amount = original_cost - best_cost
            savings_percentage = (savings_amount / original_cost) * 100 if original_cost > 0 else 0
            
            # Generate implementation notes
            implementation_notes = []
            if best_model != current_model:
                implementation_notes.append(f"Switch from {current_model} to {best_model}")
                implementation_notes.append("Test quality before full deployment")
            
            if self.config.enable_caching and await self._is_cacheable_prompt(prompt):
                implementation_notes.append("Enable response caching for additional savings")
            
            # Calculate confidence
            confidence_score = await self._calculate_optimization_confidence(
                current_model, best_model, savings_percentage
            )
            
            result = CostOptimizationResult(
                original_cost=original_cost,
                optimized_cost=best_cost,
                savings_amount=savings_amount,
                savings_percentage=savings_percentage,
                recommended_model=best_model,
                strategy_used=strategy,
                confidence_score=confidence_score,
                trade_offs=trade_offs,
                implementation_notes=implementation_notes
            )
            
            # Store optimization result
            await self._store_optimization_result(result, prompt, creator_context)
            
            return result
        
        except Exception as e:
            logger.error(f"Cost optimization failed: {e}")
            raise CostOptimizationError(f"Cost optimization failed: {e}")
    
    async def _calculate_optimization_confidence(
        self,
        current_model: str,
        optimized_model: str,
        savings_percentage: float
    ) -> float:
        """Calculate confidence in optimization recommendation"""
        base_confidence = 0.7
        
        # Higher confidence for well-tested model switches
        tested_switches = [
            ("gpt-4", "gpt-4-turbo"),
            ("gpt-4", "claude-3-sonnet"),
            ("claude-3-opus", "claude-3-sonnet"),
            ("gpt-4", "gpt-3.5-turbo")
        ]
        
        if (current_model, optimized_model) in tested_switches:
            base_confidence += 0.2
        
        # Higher confidence for significant savings
        if savings_percentage > 50:
            base_confidence += 0.1
        elif savings_percentage > 25:
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    async def _store_optimization_result(
        self,
        result: CostOptimizationResult,
        prompt: str,
        creator_context: Optional[Dict[str, Any]]
    ) -> None:
        """Store optimization result in database"""
        try:
            optimization_id = f"opt_{int(time.time())}_{hashlib.md5(prompt.encode()).hexdigest()[:8]}"
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO optimization_history 
                    (optimization_id, original_model, optimized_model, original_cost,
                     optimized_cost, savings_percentage, strategy_used, creator_context)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, optimization_id, result.recommended_model, result.recommended_model,
                    result.original_cost, result.optimized_cost, result.savings_percentage,
                    result.strategy_used.value, json.dumps(creator_context or {}))
        
        except Exception as e:
            logger.error(f"Failed to store optimization result: {e}")
    
    async def calculate_cost(
        self,
        prompt: str,
        response: str,
        model_name: str,
        creator_context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate actual cost for completed request"""
        try:
            input_tokens = await self._count_tokens(prompt, model_name)
            output_tokens = await self._count_tokens(response, model_name)
            
            estimate = await self.estimate_cost(prompt, model_name, output_tokens, creator_context)
            
            # Store actual cost for model training
            await self._record_actual_cost(
                input_tokens, output_tokens, estimate.estimated_cost, model_name, creator_context
            )
            
            return estimate.estimated_cost
        
        except Exception as e:
            logger.error(f"Cost calculation failed: {e}")
            return 0.0
    
    async def _record_actual_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        actual_cost: float,
        model_name: str,
        creator_context: Optional[Dict[str, Any]]
    ) -> None:
        """Record actual cost for model improvement"""
        try:
            request_id = f"req_{int(time.time())}_{hash(str(creator_context))}"
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO cost_tracking 
                    (request_id, model_name, input_tokens, output_tokens, total_tokens,
                     estimated_cost, actual_cost, creator_context)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, request_id, model_name, input_tokens, output_tokens,
                    input_tokens + output_tokens, actual_cost, actual_cost,
                    json.dumps(creator_context or {}))
        
        except Exception as e:
            logger.error(f"Failed to record actual cost: {e}")
    
    async def get_budget_status(
        self,
        period: BudgetPeriod = BudgetPeriod.MONTHLY,
        creator_id: Optional[str] = None
    ) -> BudgetUsage:
        """Get current budget usage status"""
        try:
            # Calculate period boundaries
            now = datetime.utcnow()
            if period == BudgetPeriod.DAILY:
                period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                allocated_budget = self.config.daily_budget_limit
            elif period == BudgetPeriod.MONTHLY:
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                allocated_budget = self.config.monthly_budget_limit
            else:
                raise ValidationError(f"Unsupported budget period: {period}")
            
            # Query actual usage
            query_conditions = ["created_at >= $1"]
            query_params = [period_start]
            
            if creator_id:
                query_conditions.append("creator_context->>'creator_id' = $2")
                query_params.append(creator_id)
            
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(f"""
                    SELECT 
                        COALESCE(SUM(actual_cost), 0) as used_budget,
                        COUNT(*) as request_count
                    FROM cost_tracking 
                    WHERE {' AND '.join(query_conditions)}
                """, *query_params)
                
                used_budget = float(row['used_budget'] or 0)
                remaining_budget = max(0, allocated_budget - used_budget)
                usage_percentage = (used_budget / allocated_budget) * 100 if allocated_budget > 0 else 0
                
                # Predict overage
                days_in_period = (now - period_start).days + 1
                if period == BudgetPeriod.MONTHLY:
                    total_days = 30  # Approximate
                else:
                    total_days = 1
                
                projected_total = (used_budget / days_in_period) * total_days if days_in_period > 0 else used_budget
                projected_overage = max(0, projected_total - allocated_budget)
                
                return BudgetUsage(
                    period=period,
                    allocated_budget=allocated_budget,
                    used_budget=used_budget,
                    remaining_budget=remaining_budget,
                    usage_percentage=usage_percentage,
                    projected_overage=projected_overage
                )
        
        except Exception as e:
            logger.error(f"Failed to get budget status: {e}")
            raise CostOptimizationError(f"Budget status retrieval failed: {e}")
    
    async def _budget_monitoring_task(self) -> None:
        """Background task for budget monitoring and alerts"""
        try:
            while True:
                await asyncio.sleep(3600)  # Check every hour
                
                if not self._initialized:
                    continue
                
                try:
                    # Check daily and monthly budgets
                    daily_usage = await self.get_budget_status(BudgetPeriod.DAILY)
                    monthly_usage = await self.get_budget_status(BudgetPeriod.MONTHLY)
                    
                    # Send alerts if needed
                    if daily_usage.usage_percentage > self.config.cost_threshold_warning * 100:
                        await self._send_budget_alert("daily", daily_usage)
                    
                    if monthly_usage.usage_percentage > self.config.cost_threshold_warning * 100:
                        await self._send_budget_alert("monthly", monthly_usage)
                
                except Exception as e:
                    logger.error(f"Budget monitoring error: {e}")
        
        except asyncio.CancelledError:
            logger.info("Budget monitoring task cancelled")
        except Exception as e:
            logger.error(f"Budget monitoring task failed: {e}")
    
    async def _send_budget_alert(self, period: str, usage: BudgetUsage) -> None:
        """Send budget alert notification"""
        logger.warning(
            f"Budget alert: {period} usage at {usage.usage_percentage:.1f}% "
            f"(${usage.used_budget:.2f} of ${usage.allocated_budget:.2f})"
        )
        # Here you would integrate with notification systems
    
    async def _cost_optimization_task(self) -> None:
        """Background task for automatic cost optimization"""
        try:
            while True:
                await asyncio.sleep(21600)  # Run every 6 hours
                
                if not self._initialized or not self.config.enable_auto_optimization:
                    continue
                
                try:
                    # Find high-cost templates for optimization
                    await self._identify_optimization_opportunities()
                    
                    # Retrain cost models with new data
                    await self._retrain_cost_models()
                
                except Exception as e:
                    logger.error(f"Auto optimization error: {e}")
        
        except asyncio.CancelledError:
            logger.info("Cost optimization task cancelled")
        except Exception as e:
            logger.error(f"Cost optimization task failed: {e}")
    
    async def _identify_optimization_opportunities(self) -> None:
        """Identify high-cost templates that could benefit from optimization"""
        try:
            # Find templates with high costs in last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        template_id,
                        model_name,
                        AVG(actual_cost) as avg_cost,
                        COUNT(*) as usage_count,
                        SUM(actual_cost) as total_cost
                    FROM cost_tracking 
                    WHERE template_id IS NOT NULL
                    AND created_at >= $1
                    GROUP BY template_id, model_name
                    HAVING AVG(actual_cost) > 0.10
                    ORDER BY total_cost DESC
                    LIMIT 20
                """, week_ago)
                
                for row in rows:
                    logger.info(
                        f"Optimization opportunity: Template {row['template_id']} "
                        f"with model {row['model_name']} - "
                        f"avg cost: ${row['avg_cost']:.3f}, "
                        f"total cost: ${row['total_cost']:.2f}"
                    )
        
        except Exception as e:
            logger.error(f"Failed to identify optimization opportunities: {e}")
    
    async def _retrain_cost_models(self) -> None:
        """Retrain cost prediction models with new data"""
        try:
            # This would retrain the ML models with fresh data
            await self._load_cost_models()
            logger.info("Cost models retrained successfully")
        
        except Exception as e:
            logger.error(f"Failed to retrain cost models: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup cost optimizer resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            logger.info("Cost Optimizer cleanup completed")
        
        except Exception as e:
            logger.error(f"Cost Optimizer cleanup failed: {e}")


# Global cost optimizer instance
cost_optimizer = CostOptimizer()