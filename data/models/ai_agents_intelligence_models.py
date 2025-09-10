"""AI Agents Intelligence Models
=============================

Advanced AI agents and intelligence orchestration models for IA Influencer Agent platform.
Comprehensive 53 AI agents management system with multi-agent collaboration,
performance monitoring, and scalable intelligence orchestration.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

🚀 ENTERPRISE FEATURES:
• 53 AI agents management & orchestration
• Task distribution & load balancing
• Performance monitoring & optimization
• Agent training & model updating
• Multi-agent collaboration workflows
• Real-time decision making & adaptation
• Agent performance analytics & reporting
• Scalable intelligence orchestration
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, date
from enum import Enum
import uuid
from typing import Optional, Dict, Any, List

# Import base from enterprise content models
from .enterprise_content_models import Base

# ============================================================================
# ENUMS - AI Agent System
# ============================================================================

class AgentType(Enum):
    """53 different AI agent types for comprehensive platform intelligence"""
    # Content Analysis Agents (8 agents)
    CONTENT_ANALYZER = "content_analyzer"
    QUALITY_ASSESSOR = "quality_assessor"
    METADATA_EXTRACTOR = "metadata_extractor"
    AUDIO_ANALYZER = "audio_analyzer"
    VIDEO_ANALYZER = "video_analyzer"
    IMAGE_ANALYZER = "image_analyzer"
    TEXT_ANALYZER = "text_analyzer"
    MULTIMODAL_ANALYZER = "multimodal_analyzer"
    
    # User Behavior Agents (7 agents)
    USER_BEHAVIOR_TRACKER = "user_behavior_tracker"
    ENGAGEMENT_PREDICTOR = "engagement_predictor"
    PREFERENCE_LEARNER = "preference_learner"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    AUDIENCE_SEGMENTER = "audience_segmenter"
    CHURN_PREDICTOR = "churn_predictor"
    LOYALTY_SCORER = "loyalty_scorer"
    
    # Revenue Optimization Agents (6 agents)
    REVENUE_OPTIMIZER = "revenue_optimizer"
    PRICING_STRATEGIST = "pricing_strategist"
    DEMAND_FORECASTER = "demand_forecaster"
    MONETIZATION_ADVISOR = "monetization_advisor"
    CONVERSION_OPTIMIZER = "conversion_optimizer"
    ROI_CALCULATOR = "roi_calculator"
    
    # Protection Intelligence Agents (8 agents)
    FINGERPRINT_MATCHER = "fingerprint_matcher"
    VIOLATION_DETECTOR = "violation_detector"
    DEEPFAKE_DETECTOR = "deepfake_detector"
    PIRACY_HUNTER = "piracy_hunter"
    LEGAL_COMPLIANCE_CHECKER = "legal_compliance_checker"
    RISK_ASSESSOR = "risk_assessor"
    FRAUD_DETECTOR = "fraud_detector"
    THREAT_ANALYZER = "threat_analyzer"
    
    # Collaboration & Social Agents (6 agents)
    COLLABORATION_MATCHER = "collaboration_matcher"
    SOCIAL_NETWORK_ANALYZER = "social_network_analyzer"
    INFLUENCE_SCORER = "influence_scorer"
    TREND_DETECTOR = "trend_detector"
    VIRAL_PREDICTOR = "viral_predictor"
    COMMUNITY_BUILDER = "community_builder"
    
    # SEO & Distribution Agents (6 agents)
    SEO_OPTIMIZER = "seo_optimizer"
    KEYWORD_RESEARCHER = "keyword_researcher"
    CONTENT_SCHEDULER = "content_scheduler"
    PLATFORM_OPTIMIZER = "platform_optimizer"
    TRAFFIC_ANALYZER = "traffic_analyzer"
    SEARCH_RANKER = "search_ranker"
    
    # Blockchain & Technical Agents (5 agents)
    BLOCKCHAIN_MONITOR = "blockchain_monitor"
    SMART_CONTRACT_EXECUTOR = "smart_contract_executor"
    NFT_VALUER = "nft_valuer"
    CRYPTO_ANALYZER = "crypto_analyzer"
    DEFI_INTEGRATOR = "defi_integrator"
    
    # Performance & System Agents (7 agents)
    PERFORMANCE_MONITOR = "performance_monitor"
    LOAD_BALANCER = "load_balancer"
    RESOURCE_OPTIMIZER = "resource_optimizer"
    SYSTEM_HEALTH_CHECKER = "system_health_checker"
    DATA_QUALITY_VALIDATOR = "data_quality_validator"
    ANOMALY_DETECTOR = "anomaly_detector"
    PREDICTIVE_MAINTENANCE = "predictive_maintenance"


class TaskType(Enum):
    """Types of tasks that AI agents can perform"""
    CONTENT_ANALYSIS = "content_analysis"
    USER_ANALYSIS = "user_analysis"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    PROTECTION_MONITORING = "protection_monitoring"
    SEO_OPTIMIZATION = "seo_optimization"
    COLLABORATION_MATCHING = "collaboration_matching"
    PERFORMANCE_MONITORING = "performance_monitoring"
    DATA_PROCESSING = "data_processing"
    PREDICTION = "prediction"
    CLASSIFICATION = "classification"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    PATTERN_RECOGNITION = "pattern_recognition"
    OPTIMIZATION = "optimization"
    AUTOMATION = "automation"


class AgentStatus(Enum):
    """Current status of AI agents"""
    ACTIVE = "active"
    IDLE = "idle"
    TRAINING = "training"
    UPDATING = "updating"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    OFFLINE = "offline"
    OVERLOADED = "overloaded"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"


class TaskPriority(Enum):
    """Priority levels for agent tasks"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"
    SCHEDULED = "scheduled"
    BACKGROUND = "background"


class PerformanceMetric(Enum):
    """Performance metrics for agent evaluation"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    SPEED = "speed"
    EFFICIENCY = "efficiency"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    RESOURCE_USAGE = "resource_usage"
    COST_EFFECTIVENESS = "cost_effectiveness"


class OrchestrationStrategy(Enum):
    """Strategies for multi-agent orchestration"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ADAPTIVE = "adaptive"
    HIERARCHICAL = "hierarchical"
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    CONSENSUS = "consensus"
    DEMOCRATIC = "democratic"
    PRIORITY_BASED = "priority_based"


# ============================================================================
# AI AGENT MODELS
# ============================================================================

class AIAgentModel(Base):
    """
    Enterprise AI agent model for comprehensive agent management and orchestration.
    Individual agent tracking with performance monitoring and capability management.
    """
    __tablename__ = 'ai_agents'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_type = Column(SQLEnum(AgentType), nullable=False, index=True)
    status = Column(SQLEnum(AgentStatus), nullable=False, default=AgentStatus.IDLE, index=True)
    
    # Agent configuration
    agent_name = Column(String(200), nullable=False, index=True)
    agent_version = Column(String(50), nullable=False, default="1.0.0")
    model_version = Column(String(100))  # AI model version being used
    configuration = Column(JSONB, default=dict)  # Agent-specific configuration
    capabilities = Column(JSONB, default=list)  # List of capabilities
    
    # Technical specifications
    framework = Column(String(100))  # "tensorflow", "pytorch", "sklearn", etc.
    model_architecture = Column(String(200))
    model_size_mb = Column(Float)
    memory_requirements_mb = Column(Float)
    cpu_requirements = Column(Float)  # CPU cores needed
    gpu_requirements = Column(String(100))  # GPU requirements
    
    # Performance specifications
    max_concurrent_tasks = Column(Integer, default=1)
    average_processing_time = Column(Float, default=0.0)  # seconds
    accuracy_target = Column(Float, default=0.9)  # target accuracy 0-1
    throughput_target = Column(Integer, default=100)  # tasks per hour
    
    # Training information
    training_data_size = Column(Integer)  # number of training samples
    last_training_date = Column(DateTime(timezone=True))
    training_duration_hours = Column(Float)
    training_cost = Column(Float)
    validation_accuracy = Column(Float)
    test_accuracy = Column(Float)
    
    # Performance metrics
    total_tasks_completed = Column(Integer, default=0)
    total_tasks_failed = Column(Integer, default=0)
    current_accuracy = Column(Float, default=0.0)
    current_speed = Column(Float, default=0.0)  # tasks per minute
    success_rate = Column(Float, default=0.0)  # percentage
    average_confidence = Column(Float, default=0.0)  # average confidence score
    
    # Resource usage
    cpu_usage_percent = Column(Float, default=0.0)
    memory_usage_mb = Column(Float, default=0.0)
    gpu_usage_percent = Column(Float, default=0.0)
    network_usage_mbps = Column(Float, default=0.0)
    storage_usage_gb = Column(Float, default=0.0)
    
    # Operational data
    uptime_hours = Column(Float, default=0.0)
    last_task_timestamp = Column(DateTime(timezone=True))
    last_health_check = Column(DateTime(timezone=True))
    error_count_today = Column(Integer, default=0)
    maintenance_scheduled = Column(DateTime(timezone=True))
    
    # Learning & adaptation
    learning_enabled = Column(Boolean, default=True)
    adaptation_rate = Column(Float, default=0.1)  # learning rate
    feedback_score = Column(Float, default=0.0)  # user feedback score
    improvement_rate = Column(Float, default=0.0)  # rate of improvement
    knowledge_base_size = Column(Integer, default=0)
    
    # Dependencies & Integration
    dependencies = Column(JSONB, default=list)  # Other agents this depends on
    integrations = Column(JSONB, default=list)  # External systems integrated
    data_sources = Column(JSONB, default=list)  # Data sources used
    output_destinations = Column(JSONB, default=list)  # Where outputs go
    
    # Quality & Validation
    validation_status = Column(String(50), default="validated")
    quality_score = Column(Float, default=1.0)  # 0-1 quality rating
    bias_score = Column(Float, default=0.0)  # bias detection score
    fairness_score = Column(Float, default=1.0)  # fairness assessment
    explainability_score = Column(Float, default=0.5)  # how explainable
    
    # Deployment information
    deployment_environment = Column(String(50), default="production")
    container_id = Column(String(200))
    endpoint_url = Column(String(500))
    health_check_url = Column(String(500))
    monitoring_dashboard_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deployed_at = Column(DateTime(timezone=True))
    last_trained_at = Column(DateTime(timezone=True))
    
    # System flags
    is_active = Column(Boolean, default=True, index=True)
    is_production_ready = Column(Boolean, default=False)
    is_experimental = Column(Boolean, default=False)
    is_deprecated = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    task_assignments = relationship("AgentTaskModel", back_populates="agent", cascade="all, delete-orphan")
    performance_records = relationship("AgentPerformanceModel", back_populates="agent", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_agent_type_status', 'agent_type', 'status'),
        Index('idx_agent_performance_active', 'success_rate', 'is_active'),
        Index('idx_agent_created_version', 'created_at', 'agent_version'),
        Index('idx_agent_accuracy_speed', 'current_accuracy', 'current_speed'),
    )
    
    def __repr__(self):
        return f"<AIAgentModel(id={self.id}, type={self.agent_type.value}, status={self.status.value})>"


class AgentTaskModel(Base):
    """
    Agent task management model for tracking individual AI agent assignments.
    Comprehensive task lifecycle with performance monitoring and result tracking.
    """
    __tablename__ = 'agent_tasks'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('ai_agents.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=True, index=True)
    
    # Task classification
    task_type = Column(SQLEnum(TaskType), nullable=False, index=True)
    priority = Column(SQLEnum(TaskPriority), nullable=False, default=TaskPriority.NORMAL, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    
    # Task details
    task_name = Column(String(300), nullable=False)
    task_description = Column(Text)
    task_parameters = Column(JSONB, default=dict)  # Input parameters
    expected_output_format = Column(String(100))
    timeout_seconds = Column(Integer, default=300)
    
    # Input/Output data
    input_data = Column(JSONB)  # Input data for the task
    output_data = Column(JSONB)  # Results from the agent
    intermediate_results = Column(JSONB, default=list)  # Step-by-step results
    error_details = Column(Text)
    
    # Performance tracking
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    processing_duration = Column(Float)  # seconds
    queue_wait_time = Column(Float)  # seconds waited in queue
    resource_usage = Column(JSONB, default=dict)  # CPU, memory, etc.
    
    # Quality metrics
    confidence_score = Column(Float, default=0.0)  # Agent's confidence in result
    accuracy_score = Column(Float)  # Actual accuracy if known
    quality_rating = Column(Float)  # Human quality rating
    user_satisfaction = Column(Float)  # User satisfaction score
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)  # 0-100
    steps_completed = Column(Integer, default=0)
    steps_total = Column(Integer, default=1)
    current_step_description = Column(String(300))
    
    # Dependencies & Workflow
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey('agent_tasks.id'))
    workflow_id = Column(String(200))  # Group related tasks
    dependency_tasks = Column(JSONB, default=list)  # Task IDs this depends on
    blocking_tasks = Column(JSONB, default=list)  # Tasks blocked by this one
    
    # Retry & Error handling
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    retry_strategy = Column(String(50), default="exponential_backoff")
    last_error_message = Column(Text)
    error_category = Column(String(100))
    
    # Business context
    business_priority = Column(String(50))
    deadline = Column(DateTime(timezone=True))
    cost_budget = Column(Float)  # Maximum cost allowed
    actual_cost = Column(Float)  # Actual cost incurred
    roi_expected = Column(Float)  # Expected return on investment
    
    # Feedback & Learning
    feedback_provided = Column(Boolean, default=False)
    feedback_score = Column(Float)  # -1 to 1 feedback score
    feedback_comments = Column(Text)
    learning_value = Column(Float, default=0.0)  # Value for agent learning
    
    # Monitoring & Alerting
    monitoring_enabled = Column(Boolean, default=True)
    alert_thresholds = Column(JSONB, default=dict)
    alerts_triggered = Column(JSONB, default=list)
    notification_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    scheduled_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # System flags
    is_critical = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    is_benchmark = Column(Boolean, default=False)  # Use for performance benchmarking
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    agent = relationship("AIAgentModel", back_populates="task_assignments")
    user = relationship("UserModel", backref="agent_tasks")
    content = relationship("ContentModel", backref="agent_tasks")
    parent_task = relationship("AgentTaskModel", remote_side=[id], backref="subtasks")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_task_agent_status', 'agent_id', 'status'),
        Index('idx_task_type_priority', 'task_type', 'priority'),
        Index('idx_task_created_deadline', 'created_at', 'deadline'),
        Index('idx_task_user_workflow', 'user_id', 'workflow_id'),
    )
    
    def __repr__(self):
        return f"<AgentTaskModel(id={self.id}, type={self.task_type.value}, status={self.status})>"


class AgentPerformanceModel(Base):
    """
    Agent performance tracking model for monitoring and optimization.
    Detailed performance metrics and analytics for AI agent improvement.
    """
    __tablename__ = 'agent_performance'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('ai_agents.id'), nullable=False, index=True)
    
    # Performance classification
    metric_type = Column(SQLEnum(PerformanceMetric), nullable=False, index=True)
    measurement_period = Column(String(20), nullable=False, default="hourly", index=True)
    
    # Performance data
    measurement_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    target_value = Column(Float)
    baseline_value = Column(Float)
    improvement_percentage = Column(Float)
    
    # Context information
    task_count = Column(Integer, default=0)
    workload_complexity = Column(Float, default=1.0)  # 0-5 complexity score
    resource_availability = Column(Float, default=1.0)  # 0-1 availability
    concurrent_agents = Column(Integer, default=1)
    
    # Detailed metrics
    accuracy_metrics = Column(JSONB, default=dict)  # Detailed accuracy breakdown
    speed_metrics = Column(JSONB, default=dict)  # Speed analysis
    resource_metrics = Column(JSONB, default=dict)  # Resource usage details
    quality_metrics = Column(JSONB, default=dict)  # Quality assessment
    
    # Comparative analysis
    vs_previous_period = Column(Float)  # Comparison to previous period
    vs_target = Column(Float)  # Comparison to target
    vs_peer_agents = Column(Float)  # Comparison to similar agents
    percentile_rank = Column(Float)  # Performance percentile
    
    # Statistical data
    confidence_interval = Column(JSONB, default=dict)  # Statistical confidence
    standard_deviation = Column(Float)
    variance = Column(Float)
    outlier_count = Column(Integer, default=0)
    data_quality_score = Column(Float, default=1.0)
    
    # Environmental factors
    system_load = Column(Float, default=0.0)  # Overall system load
    network_latency = Column(Float, default=0.0)  # Network conditions
    data_quality = Column(Float, default=1.0)  # Input data quality
    user_activity_level = Column(String(20), default="normal")
    
    # Performance insights
    bottleneck_identified = Column(String(200))
    optimization_suggestions = Column(JSONB, default=list)
    performance_issues = Column(JSONB, default=list)
    improvement_opportunities = Column(JSONB, default=list)
    
    # Alerts & Notifications
    threshold_breached = Column(Boolean, default=False)
    alert_level = Column(String(20), default="normal")
    alert_message = Column(Text)
    escalation_required = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # System flags
    is_anomaly = Column(Boolean, default=False)
    is_benchmark = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    agent = relationship("AIAgentModel", back_populates="performance_records")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_performance_agent_timestamp', 'agent_id', 'measurement_timestamp'),
        Index('idx_performance_metric_period', 'metric_type', 'measurement_period'),
        Index('idx_performance_value_target', 'metric_value', 'target_value'),
    )
    
    def __repr__(self):
        return f"<AgentPerformanceModel(id={self.id}, metric={self.metric_type.value}, value={self.metric_value})>"


class IntelligenceOrchestrationModel(Base):
    """
    Multi-agent orchestration model for coordinating AI agent workflows.
    Advanced orchestration with strategy management and performance optimization.
    """
    __tablename__ = 'intelligence_orchestration'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    orchestration_name = Column(String(300), nullable=False)
    strategy = Column(SQLEnum(OrchestrationStrategy), nullable=False, index=True)
    
    # Orchestration configuration
    agent_ids = Column(JSONB, nullable=False)  # List of participating agent IDs
    workflow_definition = Column(JSONB, nullable=False)  # Workflow structure
    execution_order = Column(JSONB, default=list)  # Order of agent execution
    coordination_rules = Column(JSONB, default=dict)  # Rules for coordination
    
    # Performance configuration
    timeout_minutes = Column(Integer, default=60)
    max_retries = Column(Integer, default=3)
    failure_tolerance = Column(Float, default=0.1)  # % of agents that can fail
    success_threshold = Column(Float, default=0.8)  # Required success rate
    
    # Execution tracking
    status = Column(String(50), default="pending", index=True)
    current_step = Column(String(200))
    progress_percentage = Column(Float, default=0.0)
    agents_completed = Column(Integer, default=0)
    agents_failed = Column(Integer, default=0)
    
    # Results & Output
    final_results = Column(JSONB)
    intermediate_results = Column(JSONB, default=dict)
    error_summary = Column(Text)
    performance_summary = Column(JSONB, default=dict)
    
    # Resource management
    resource_allocation = Column(JSONB, default=dict)  # Resource distribution
    cost_budget = Column(Float)
    actual_cost = Column(Float, default=0.0)
    efficiency_score = Column(Float, default=0.0)
    
    # Quality & Validation
    output_quality_score = Column(Float, default=0.0)
    consensus_score = Column(Float, default=0.0)  # Agreement between agents
    confidence_score = Column(Float, default=0.0)
    validation_passed = Column(Boolean, default=False)
    
    # Timing information
    scheduled_start = Column(DateTime(timezone=True))
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    total_duration = Column(Float)  # seconds
    
    # Learning & Optimization
    optimization_applied = Column(Boolean, default=False)
    learning_insights = Column(JSONB, default=list)
    improvement_suggestions = Column(JSONB, default=list)
    adaptation_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    
    # System flags
    is_template = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_orchestration_strategy_status', 'strategy', 'status'),
        Index('idx_orchestration_created_completed', 'created_at', 'completed_at'),
    )
    
    def __repr__(self):
        return f"<IntelligenceOrchestrationModel(id={self.id}, strategy={self.strategy.value}, status={self.status})>"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_ai_agent_example(agent_type: AgentType = AgentType.CONTENT_ANALYZER) -> AIAgentModel:
    """Create example AI agent for testing and development"""
    return AIAgentModel(
        agent_type=agent_type,
        agent_name=f"Sample {agent_type.value.replace('_', ' ').title()}",
        agent_version="1.0.0",
        framework="tensorflow",
        model_architecture="transformer",
        max_concurrent_tasks=5,
        accuracy_target=0.95,
        capabilities=[f"{agent_type.value}_capability", "general_analysis"]
    )


def create_agent_task_example(agent_id: str, task_type: TaskType = TaskType.CONTENT_ANALYSIS) -> AgentTaskModel:
    """Create example agent task for testing and development"""
    return AgentTaskModel(
        agent_id=agent_id,
        task_type=task_type,
        task_name=f"Sample {task_type.value.replace('_', ' ').title()} Task",
        task_description="This is a sample task for testing purposes",
        task_parameters={"input_type": "text", "analysis_depth": "standard"},
        timeout_seconds=300,
        priority=TaskPriority.NORMAL
    )


def create_performance_record_example(agent_id: str, 
                                    metric_type: PerformanceMetric = PerformanceMetric.ACCURACY) -> AgentPerformanceModel:
    """Create example performance record for testing and development"""
    return AgentPerformanceModel(
        agent_id=agent_id,
        metric_type=metric_type,
        measurement_timestamp=datetime.utcnow(),
        metric_value=0.85,
        target_value=0.90,
        baseline_value=0.80,
        task_count=100,
        period_start=datetime.utcnow(),
        period_end=datetime.utcnow()
    )


def calculate_agent_efficiency(agent: AIAgentModel) -> float:
    """Calculate overall efficiency score for an agent"""
    if agent.total_tasks_completed == 0:
        return 0.0
    
    # Combine success rate, speed, and accuracy
    success_rate = agent.success_rate / 100.0  # Convert percentage to 0-1
    speed_factor = min(1.0, agent.current_speed / 100.0)  # Normalize speed
    accuracy_factor = agent.current_accuracy
    
    # Weighted average
    efficiency = (success_rate * 0.4) + (speed_factor * 0.3) + (accuracy_factor * 0.3)
    return round(efficiency, 3)


def recommend_orchestration_strategy(agent_types: List[AgentType], 
                                   task_complexity: str = "medium") -> OrchestrationStrategy:
    """Recommend orchestration strategy based on agent types and task complexity"""
    if len(agent_types) == 1:
        return OrchestrationStrategy.SEQUENTIAL
    
    if task_complexity == "low":
        return OrchestrationStrategy.PARALLEL
    elif task_complexity == "high":
        return OrchestrationStrategy.HIERARCHICAL
    else:
        return OrchestrationStrategy.ADAPTIVE


# ============================================================================
# EXPORT SECTION
# ============================================================================

__all__ = [
    # Models
    'AIAgentModel', 'AgentTaskModel', 'AgentPerformanceModel', 'IntelligenceOrchestrationModel',
    
    # Agent Enums
    'AgentType', 'TaskType', 'AgentStatus', 'TaskPriority', 'PerformanceMetric', 'OrchestrationStrategy',
    
    # Utility Functions
    'create_ai_agent_example', 'create_agent_task_example', 'create_performance_record_example',
    'calculate_agent_efficiency', 'recommend_orchestration_strategy'
]