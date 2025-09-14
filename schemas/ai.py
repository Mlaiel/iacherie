"""AI & Machine Learning Schemas for IA Influencer Agent Platform
Advanced AI model configurations, ML pipelines, and intelligent processing schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class AIModelConfiguration(UUIDSchema, TimestampSchema, AuditSchema):
    """
AI model configuration and management schema."""
    
    model_name: str = Field(description="AI model name")
    model_type: str = Field(description="Type of AI model")
    model_version: str = Field(description="Model version identifier")
    model_provider: str = Field(description="AI model provider/vendor")
    
    # Model specifications
    architecture: str = Field(description="Model architecture type")
    parameter_count: Optional[int] = Field(None, description="Number of model parameters")
    input_modalities: List[str] = Field(description="Supported input modalities")
    output_modalities: List[str] = Field(description="Supported output modalities")
    
    # Configuration parameters
    model_parameters: Dict[str, Any] = Field(default_factory=dict)
    hyperparameters: Dict[str, Union[int, float, str]] = Field(default_factory=dict)
    training_configuration: Optional[Dict[str, Any]] = None
    fine_tuning_parameters: Optional[Dict[str, Any]] = None
    
    # Performance specifications
    max_tokens: Optional[int] = None
    context_window: Optional[int] = None
    processing_time_target: float = Field(default=5.0, description="Target processing time in seconds")
    accuracy_target: float = Field(default=0.95, ge=0.0, le=1.0)
    
    # Resource requirements
    gpu_requirements: Optional[Dict[str, Any]] = None
    memory_requirements: Dict[str, str] = Field(default_factory=dict)
    compute_requirements: Dict[str, Any] = Field(default_factory=dict)
    storage_requirements: Optional[str] = None
    
    # API configuration
    api_endpoint: Optional[str] = None
    api_key_required: bool = Field(default=True)
    rate_limits: Dict[str, int] = Field(default_factory=dict)
    pricing_model: Optional[Dict[str, Any]] = None
    
    # Capabilities
    supported_languages: List[str] = Field(default_factory=list)
    content_types_supported: List[str] = Field(default_factory=list)
    special_features: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    
    # Quality and safety
    safety_filters: Dict[str, bool] = Field(default_factory=dict)
    content_moderation: bool = Field(default=True)
    bias_mitigation: bool = Field(default=True)
    privacy_compliance: List[str] = Field(default_factory=list)
    
    # Monitoring and maintenance
    performance_monitoring: bool = Field(default=True)
    automatic_updates: bool = Field(default=False)
    fallback_models: List[str] = Field(default_factory=list)
    health_check_frequency: str = Field(default="hourly")
    
    # Usage statistics
    usage_statistics: Dict[str, int] = Field(default_factory=dict)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    error_rates: Dict[str, float] = Field(default_factory=dict)
    
    # Status
    is_active: bool = Field(default=True)
    deployment_status: str = Field(default="deployed")
    last_health_check: Optional[datetime] = None
    
    @validator('model_type')
    def validate_model_type(cls, v) -> None:
        """Validate model type."""
        allowed_types = {
            "language_model", "computer_vision", "audio_processing", "multimodal",
            "content_generation", "content_analysis", "sentiment_analysis",
            "object_detection", "face_recognition", "voice_synthesis",
            "recommendation_engine", "classification", "regression", "clustering"
        }
        if v not in allowed_types:
            raise ValueError(f'Model type must be one of: {", ".join(allowed_types)}')
        return v


class AIProcessingRequest(UUIDSchema, TimestampSchema):
    """AI processing request schema."""
    
    requester_id: UUID = Field(description="User/system making the request")
    model_id: UUID = Field(description="AI model to use")
    processing_type: str = Field(description="Type of AI processing requested")
    priority_level: str = Field(default="normal", description="Processing priority")
    
    # Input data
    input_content: Optional[str] = None
    input_files: List[str] = Field(default_factory=list)
    input_metadata: Dict[str, Any] = Field(default_factory=dict)
    content_type: str = Field(description="Type of content to process")
    
    # Processing parameters
    processing_parameters: Dict[str, Any] = Field(default_factory=dict)
    output_format: str = Field(default="json")
    quality_level: str = Field(default="standard")
    processing_options: List[str] = Field(default_factory=list)
    
    # Context and constraints
    context_information: Optional[str] = None
    processing_constraints: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=300, ge=1)
    max_retries: int = Field(default=3, ge=0)
    
    # Callback and notification
    callback_url: Optional[str] = None
    notification_channels: List[str] = Field(default_factory=list)
    webhook_settings: Optional[Dict[str, str]] = None
    
    # Status tracking
    request_status: str = Field(default="pending")
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    
    # Resource tracking
    estimated_processing_time: Optional[float] = None
    actual_processing_time: Optional[float] = None
    compute_resources_used: Optional[Dict[str, float]] = None
    processing_cost: Optional[Decimal] = None
    
    @validator('processing_type')
    def validate_processing_type(cls, v) -> None:
        """Validate processing type."""
        allowed_types = {
            "content_generation", "content_analysis", "content_enhancement",
            "content_moderation", "sentiment_analysis", "language_translation",
            "image_recognition", "video_analysis", "audio_processing",
            "recommendation_generation", "trend_prediction", "performance_optimization"
        }
        if v not in allowed_types:
            raise ValueError(f'Processing type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('priority_level')
    def validate_priority_level(cls, v) -> None:
        """Validate priority level."""
        allowed_levels = {"low", "normal", "high", "urgent", "critical"}
        if v not in allowed_levels:
            raise ValueError(f'Priority level must be one of: {", ".join(allowed_levels)}')
        return v


class AIProcessingResult(UUIDSchema, TimestampSchema):
    """AI processing result schema."""
    
    request_id: UUID = Field(description="Associated processing request")
    model_id: UUID = Field(description="AI model used")
    processing_status: str = Field(description="Final processing status")
    
    # Processing results
    output_content: Optional[str] = None
    output_files: List[str] = Field(default_factory=list)
    output_metadata: Dict[str, Any] = Field(default_factory=dict)
    structured_output: Optional[Dict[str, Any]] = None
    
    # Quality and confidence
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    accuracy_metrics: Dict[str, float] = Field(default_factory=dict)
    reliability_indicators: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing details
    processing_time_seconds: float = Field(ge=0.0)
    model_version_used: str = Field(description="Model version used for processing")
    processing_parameters_used: Dict[str, Any] = Field(default_factory=dict)
    fallback_models_used: List[str] = Field(default_factory=list)
    
    # Resource consumption
    compute_resources_consumed: Dict[str, float] = Field(default_factory=dict)
    memory_peak_usage: Optional[float] = None
    gpu_utilization: Optional[float] = None
    processing_cost: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Error handling
    errors_encountered: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    retry_attempts: int = Field(default=0, ge=0)
    error_recovery_actions: List[str] = Field(default_factory=list)
    
    # Validation and verification
    output_validation_passed: bool = Field(default=True)
    content_safety_check: bool = Field(default=True)
    plagiarism_check: Optional[bool] = None
    originality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Analytics and insights
    processing_insights: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    alternative_approaches: List[str] = Field(default_factory=list)
    
    # Feedback and learning
    user_feedback_score: Optional[float] = Field(None, ge=0.0, le=5.0)
    automated_quality_assessment: Optional[float] = Field(None, ge=0.0, le=1.0)
    learning_data_contribution: bool = Field(default=False)
    
    @validator('processing_status')
    def validate_processing_status(cls, v) -> None:
        """Validate processing status."""
        allowed_statuses = {
            "completed", "partial_success", "failed", "timeout",
            "cancelled", "error", "quality_issue", "safety_violation"
        }
        if v not in allowed_statuses:
            raise ValueError(f'Processing status must be one of: {", ".join(allowed_statuses)}')
        return v


class MLPipeline(UUIDSchema, TimestampSchema, AuditSchema):
    """Machine Learning pipeline configuration schema."""
    
    pipeline_name: str = Field(description="ML pipeline name")
    pipeline_type: str = Field(description="Type of ML pipeline")
    pipeline_purpose: str = Field(description="Purpose of the pipeline")
    
    # Pipeline stages
    data_ingestion: Dict[str, Any] = Field(default_factory=dict)
    data_preprocessing: Dict[str, Any] = Field(default_factory=dict)
    feature_engineering: Dict[str, Any] = Field(default_factory=dict)
    model_training: Dict[str, Any] = Field(default_factory=dict)
    model_validation: Dict[str, Any] = Field(default_factory=dict)
    model_deployment: Dict[str, Any] = Field(default_factory=dict)
    
    # Pipeline configuration
    input_data_sources: List[str] = Field(description="Data sources for the pipeline")
    output_destinations: List[str] = Field(default_factory=list)
    processing_schedule: str = Field(description="Pipeline execution schedule")
    resource_requirements: Dict[str, Any] = Field(default_factory=dict)
    
    # Data handling
    data_quality_checks: List[Dict[str, Any]] = Field(default_factory=list)
    data_transformation_rules: List[Dict[str, str]] = Field(default_factory=list)
    feature_selection_criteria: Dict[str, Any] = Field(default_factory=dict)
    data_validation_rules: List[str] = Field(default_factory=list)
    
    # Model configuration
    algorithm_selection: List[str] = Field(default_factory=list)
    hyperparameter_tuning: Dict[str, Any] = Field(default_factory=dict)
    cross_validation_strategy: str = Field(default="k_fold")
    evaluation_metrics: List[str] = Field(default_factory=list)
    
    # Performance monitoring
    performance_thresholds: Dict[str, float] = Field(default_factory=dict)
    drift_detection: bool = Field(default=True)
    model_retraining_triggers: List[str] = Field(default_factory=list)
    a_b_testing_configuration: Optional[Dict[str, Any]] = None
    
    # Deployment settings
    deployment_strategy: str = Field(description="Model deployment strategy")
    rollback_configuration: Dict[str, Any] = Field(default_factory=dict)
    canary_deployment_settings: Optional[Dict[str, Any]] = None
    blue_green_deployment: bool = Field(default=False)
    
    # Pipeline execution
    pipeline_status: str = Field(default="inactive")
    last_execution_time: Optional[datetime] = None
    next_scheduled_execution: Optional[datetime] = None
    execution_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Pipeline metrics
    success_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    average_execution_time: float = Field(default=0.0, ge=0.0)
    resource_efficiency: float = Field(default=0.0, ge=0.0, le=1.0)
    cost_per_execution: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    @validator('pipeline_type')
    def validate_pipeline_type(cls, v) -> None:
        """Validate pipeline type."""
        allowed_types = {
            "training_pipeline", "inference_pipeline", "data_processing",
            "feature_engineering", "model_evaluation", "automated_retraining",
            "batch_processing", "real_time_processing", "hybrid_pipeline"
        }
        if v not in allowed_types:
            raise ValueError(f'Pipeline type must be one of: {", ".join(allowed_types)}')
        return v


class ContentIntelligence(UUIDSchema, TimestampSchema):
    """AI-powered content intelligence and insights schema."""
    
    content_id: UUID = Field(description="Content being analyzed")
    analysis_type: str = Field(description="Type of intelligence analysis")
    ai_model_used: str = Field(description="AI model used for analysis")
    
    # Content understanding
    content_summary: str = Field(description="AI-generated content summary")
    key_topics: List[str] = Field(default_factory=list)
    main_themes: List[str] = Field(default_factory=list)
    content_category: str = Field(description="AI-determined content category")
    
    # Semantic analysis
    semantic_keywords: List[str] = Field(default_factory=list)
    entity_extraction: List[Dict[str, str]] = Field(default_factory=list)
    relationship_mapping: Dict[str, List[str]] = Field(default_factory=dict)
    concept_hierarchy: Dict[str, Any] = Field(default_factory=dict)
    
    # Sentiment and emotion
    overall_sentiment: str = Field(description="Overall content sentiment")
    sentiment_score: float = Field(ge=-1.0, le=1.0, description="Sentiment polarity score")
    emotion_analysis: Dict[str, float] = Field(default_factory=dict)
    tone_analysis: Dict[str, float] = Field(default_factory=dict)
    
    # Quality assessment
    content_quality_score: float = Field(ge=0.0, le=1.0)
    readability_score: float = Field(ge=0.0, le=1.0)
    engagement_potential: float = Field(ge=0.0, le=1.0)
    virality_prediction: float = Field(ge=0.0, le=1.0)
    
    # Audience targeting
    target_audience_analysis: Dict[str, Any] = Field(default_factory=dict)
    demographic_appeal: Dict[str, float] = Field(default_factory=dict)
    psychographic_alignment: Dict[str, float] = Field(default_factory=dict)
    persona_matching: List[str] = Field(default_factory=list)
    
    # Content optimization
    optimization_suggestions: List[str] = Field(default_factory=list)
    seo_recommendations: List[str] = Field(default_factory=list)
    engagement_enhancement_tips: List[str] = Field(default_factory=list)
    platform_specific_advice: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Performance predictions
    predicted_reach: Dict[str, int] = Field(default_factory=dict)
    predicted_engagement: Dict[str, float] = Field(default_factory=dict)
    optimal_posting_time: Dict[str, datetime] = Field(default_factory=dict)
    success_probability: float = Field(ge=0.0, le=1.0)
    
    # Content risks
    risk_assessment: Dict[str, str] = Field(default_factory=dict)
    controversy_potential: float = Field(ge=0.0, le=1.0)
    brand_safety_score: float = Field(ge=0.0, le=1.0)
    compliance_check: Dict[str, bool] = Field(default_factory=dict)
    
    # Competitive intelligence
    similar_content_analysis: List[Dict[str, Any]] = Field(default_factory=list)
    competitive_positioning: str = Field(description="Competitive position assessment")
    differentiation_opportunities: List[str] = Field(default_factory=list)
    market_gap_identification: List[str] = Field(default_factory=list)
    
    # Actionable insights
    immediate_actions: List[str] = Field(default_factory=list)
    strategic_recommendations: List[str] = Field(default_factory=list)
    long_term_opportunities: List[str] = Field(default_factory=list)
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v) -> None:
        """Validate analysis type."""
        allowed_types = {
            "comprehensive_analysis", "sentiment_analysis", "quality_assessment",
            "audience_targeting", "performance_prediction", "seo_analysis",
            "competitive_intelligence", "risk_assessment", "optimization_analysis"
        }
        if v not in allowed_types:
            raise ValueError(f'Analysis type must be one of: {", ".join(allowed_types)}')
        return v


class AIRecommendationEngine(UUIDSchema, TimestampSchema):
    """AI-powered recommendation engine schema."""
    
    user_id: UUID = Field(description="User receiving recommendations")
    recommendation_type: str = Field(description="Type of recommendations")
    recommendation_context: str = Field(description="Context for recommendations")
    
    # Recommendation configuration
    recommendation_algorithm: str = Field(description="Algorithm used for recommendations")
    personalization_level: float = Field(default=0.8, ge=0.0, le=1.0)
    diversity_factor: float = Field(default=0.3, ge=0.0, le=1.0)
    novelty_weight: float = Field(default=0.2, ge=0.0, le=1.0)
    
    # User profile analysis
    user_preferences: Dict[str, float] = Field(default_factory=dict)
    behavioral_patterns: Dict[str, Any] = Field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list)
    implicit_feedback: Dict[str, float] = Field(default_factory=dict)
    
    # Content recommendations
    recommended_content: List[Dict[str, Any]] = Field(default_factory=list)
    content_similarity_scores: Dict[str, float] = Field(default_factory=dict)
    recommendation_confidence: Dict[str, float] = Field(default_factory=dict)
    explanation_reasoning: Dict[str, str] = Field(default_factory=dict)
    
    # Strategy recommendations
    content_strategy_suggestions: List[str] = Field(default_factory=list)
    posting_schedule_recommendations: Dict[str, List[str]] = Field(default_factory=dict)
    audience_targeting_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    collaboration_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Performance optimization
    optimization_recommendations: List[str] = Field(default_factory=list)
    platform_specific_advice: Dict[str, List[str]] = Field(default_factory=dict)
    monetization_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    growth_strategies: List[str] = Field(default_factory=list)
    
    # Recommendation quality
    recommendation_freshness: float = Field(ge=0.0, le=1.0)
    coverage_score: float = Field(ge=0.0, le=1.0)
    serendipity_score: float = Field(ge=0.0, le=1.0)
    precision_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # User feedback integration
    feedback_collection_method: List[str] = Field(default_factory=list)
    implicit_feedback_signals: List[str] = Field(default_factory=list)
    recommendation_effectiveness: Dict[str, float] = Field(default_factory=dict)
    user_satisfaction_score: Optional[float] = Field(None, ge=0.0, le=5.0)
    
    # A/B testing
    recommendation_variant: Optional[str] = None
    test_group_assignment: Optional[str] = None
    experiment_parameters: Optional[Dict[str, Any]] = None
    conversion_tracking: Dict[str, float] = Field(default_factory=dict)
    
    @validator('recommendation_type')
    def validate_recommendation_type(cls, v) -> None:
        """Validate recommendation type."""
        allowed_types = {
            "content_recommendations", "collaboration_matching", "audience_targeting",
            "optimization_suggestions", "strategy_recommendations", "trend_opportunities",
            "monetization_advice", "platform_expansion", "performance_improvement"
        }
        if v not in allowed_types:
            raise ValueError(f'Recommendation type must be one of: {", ".join(allowed_types)}')
        return v


class NeuralNetworkConfiguration(UUIDSchema, TimestampSchema):
    """Advanced neural network configuration schema."""
    
    network_name: str = Field(description="Neural network name")
    architecture_type: str = Field(description="Type of neural network architecture")
    task_type: str = Field(description="Primary task for the network")
    
    # Network architecture
    layer_configuration: List[Dict[str, Any]] = Field(default_factory=list)
    activation_functions: Dict[str, str] = Field(default_factory=dict)
    network_topology: Dict[str, Any] = Field(default_factory=dict)
    parameter_count: int = Field(ge=1, description="Total network parameters")
    
    # Training configuration
    training_algorithm: str = Field(description="Training algorithm")
    optimization_method: str = Field(description="Optimization method")
    loss_function: str = Field(description="Loss function used")
    regularization_techniques: List[str] = Field(default_factory=list)
    
    # Hyperparameters
    learning_rate: float = Field(gt=0.0, description="Learning rate")
    batch_size: int = Field(ge=1, description="Training batch size")
    num_epochs: int = Field(ge=1, description="Number of training epochs")
    dropout_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Data configuration
    input_shape: List[int] = Field(description="Input data shape")
    output_shape: List[int] = Field(description="Output data shape")
    data_preprocessing: Dict[str, Any] = Field(default_factory=dict)
    augmentation_strategies: List[str] = Field(default_factory=list)
    
    # Performance metrics
    training_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    validation_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    test_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    convergence_time: Optional[float] = Field(None, ge=0.0)
    
    # Deployment specifications
    inference_latency_target: float = Field(gt=0.0, description="Target inference latency")
    memory_footprint: Optional[str] = None
    compute_requirements: Dict[str, Any] = Field(default_factory=dict)
    scalability_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Monitoring and maintenance
    performance_monitoring: bool = Field(default=True)
    automatic_retraining: bool = Field(default=False)
    model_versioning: bool = Field(default=True)
    a_b_testing_enabled: bool = Field(default=False)
    
    @validator('architecture_type')
    def validate_architecture_type(cls, v) -> None:
        """Validate architecture type."""
        allowed_types = {
            "feedforward", "convolutional", "recurrent", "transformer",
            "attention_based", "generative_adversarial", "autoencoder",
            "reinforcement_learning", "graph_neural", "hybrid"
        }
        if v not in allowed_types:
            raise ValueError(f'Architecture type must be one of: {", ".join(allowed_types)}')
        return v
