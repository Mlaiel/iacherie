"""Recovery Planner - Crisis Recovery Strategy Management

Advanced crisis recovery planning system with AI-powered strategy generation
and automated recovery workflow orchestration.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json

# Core imports
from ..config.crisis_configs import CrisisConfiguration


class RecoveryPhase(Enum):
    """Recovery phases"""
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


class RecoveryStatus(Enum):
    """Recovery status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class RecoveryAction:
    """Individual recovery action"""
    action_id: str
    title: str
    description: str
    phase: RecoveryPhase
    priority: int  # 1-10, 10 being highest
    estimated_duration: timedelta
    required_resources: List[str]
    success_metrics: List[str]
    status: RecoveryStatus = RecoveryStatus.PLANNED
    assigned_to: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    success_score: Optional[float] = None


@dataclass
class RecoveryStrategy:
    """Complete recovery strategy"""
    strategy_id: str
    crisis_id: str
    crisis_type: str
    severity_level: str
    created_at: datetime
    actions: List[RecoveryAction] = field(default_factory=list)
    timeline: Dict[str, List[str]] = field(default_factory=dict)
    budget_allocation: Dict[str, float] = field(default_factory=dict)
    success_probability: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    contingency_plans: List[str] = field(default_factory=list)


class RecoveryPlanner:
    """Advanced crisis recovery planning system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Recovery configuration
        self.crisis_config = CrisisConfiguration()
        
        # Recovery templates
        self.recovery_templates = self._load_recovery_templates()
        
        # Active recovery strategies
        self.active_strategies: Dict[str, RecoveryStrategy] = {}
        self.completed_strategies: List[RecoveryStrategy] = []
        
        # Success tracking
        self.recovery_metrics = {
            'total_recoveries': 0,
            'successful_recoveries': 0,
            'average_recovery_time': timedelta(days=0),
            'success_rate': 0.0
        }
        
        self.logger.info("RecoveryPlanner initialized")
    
    def _load_recovery_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load recovery strategy templates"""
        return {
            'reputation_damage': {
                'phases': {
                    'immediate': [
                        'Issue public statement',
                        'Pause controversial content',
                        'Monitor social sentiment'
                    ],
                    'short_term': [
                        'Implement corrective actions',
                        'Engage with affected stakeholders',
                        'Launch reputation recovery campaign'
                    ],
                    'medium_term': [
                        'Rebuild trust through transparency',
                        'Demonstrate concrete changes',
                        'Strengthen community engagement'
                    ],
                    'long_term': [
                        'Maintain improved practices',
                        'Monitor reputation indicators',
                        'Build resilience measures'
                    ]
                },
                'success_metrics': [
                    'sentiment_improvement',
                    'engagement_recovery',
                    'trust_index',
                    'media_coverage_tone'
                ]
            },
            'content_controversy': {
                'phases': {
                    'immediate': [
                        'Remove or modify problematic content',
                        'Issue clarification statement',
                        'Activate support channels'
                    ],
                    'short_term': [
                        'Conduct internal review',
                        'Implement content guidelines',
                        'Train content team'
                    ],
                    'medium_term': [
                        'Launch positive content initiative',
                        'Rebuild audience trust',
                        'Strengthen content review process'
                    ],
                    'long_term': [
                        'Maintain content quality',
                        'Regular compliance audits',
                        'Community feedback integration'
                    ]
                }
            }
        }
    
    async def create_recovery_strategy(self, crisis_id: str, crisis_type: str, 
                                     severity_level: str, context: Dict[str, Any]) -> RecoveryStrategy:
        """Create comprehensive recovery strategy for crisis"""
        try:
            strategy_id = f"recovery_{crisis_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize strategy
            strategy = RecoveryStrategy(
                strategy_id=strategy_id,
                crisis_id=crisis_id,
                crisis_type=crisis_type,
                severity_level=severity_level,
                created_at=datetime.utcnow()
            )
            
            # Generate recovery actions based on crisis type
            actions = await self._generate_recovery_actions(crisis_type, severity_level, context)
            strategy.actions = actions
            
            # Create timeline
            strategy.timeline = self._create_recovery_timeline(actions)
            
            # Calculate budget allocation
            strategy.budget_allocation = self._calculate_budget_allocation(actions, severity_level)
            
            # Assess success probability
            strategy.success_probability = self._calculate_success_probability(crisis_type, severity_level, context)
            
            # Identify risk factors
            strategy.risk_factors = self._identify_risk_factors(crisis_type, context)
            
            # Create contingency plans
            strategy.contingency_plans = self._create_contingency_plans(crisis_type, actions)
            
            # Store active strategy
            self.active_strategies[strategy_id] = strategy
            
            self.logger.info(f"Recovery strategy created: {strategy_id}")
            return strategy
            
        except Exception as e:
            self.logger.error(f"Recovery strategy creation failed: {e}")
            raise
    
    async def _generate_recovery_actions(self, crisis_type: str, severity_level: str, 
                                       context: Dict[str, Any]) -> List[RecoveryAction]:
        """Generate specific recovery actions based on crisis"""
        actions = []
        
        # Get template actions
        template = self.recovery_templates.get(crisis_type, self.recovery_templates['reputation_damage'])
        
        # Generate actions for each phase
        for phase_name, phase_actions in template['phases'].items():
            phase = RecoveryPhase(phase_name)
            
            for i, action_desc in enumerate(phase_actions):
                action = RecoveryAction(
                    action_id=f"action_{len(actions)+1:03d}",
                    title=action_desc,
                    description=self._expand_action_description(action_desc, context),
                    phase=phase,
                    priority=self._calculate_action_priority(action_desc, severity_level),
                    estimated_duration=self._estimate_action_duration(action_desc, phase),
                    required_resources=self._identify_required_resources(action_desc),
                    success_metrics=self._define_success_metrics(action_desc)
                )
                actions.append(action)
        
        return actions
    
    def _expand_action_description(self, action: str, context: Dict[str, Any]) -> str:
        """Expand action description with context-specific details"""
        expansions = {
            'Issue public statement': f"Craft and publish a public statement addressing the {context.get('issue_type', 'situation')} "
                                    f"across all primary communication channels within 2 hours.",
            'Monitor social sentiment': f"Implement real-time sentiment monitoring across {', '.join(context.get('affected_platforms', ['all platforms']))} "
                                      f"with hourly reporting for first 48 hours.",
            'Engage with affected stakeholders': f"Direct outreach to {context.get('stakeholder_count', 'key')} stakeholders "
                                               f"including {', '.join(context.get('stakeholder_types', ['customers', 'partners']))}.",
        }
        
        return expansions.get(action, f"{action} - Customized response for {context.get('crisis_scope', 'current situation')}")
    
    def _calculate_action_priority(self, action: str, severity: str) -> int:
        """Calculate action priority based on action type and severity"""
        base_priorities = {
            'Issue public statement': 9,
            'Remove or modify problematic content': 10,
            'Monitor social sentiment': 8,
            'Pause controversial content': 9,
            'Activate support channels': 7,
            'Conduct internal review': 5,
            'Launch positive content initiative': 4,
            'Maintain improved practices': 2
        }
        
        base_priority = base_priorities.get(action, 5)
        
        # Adjust for severity
        if severity == 'critical':
            return min(10, base_priority + 2)
        elif severity == 'high':
            return min(10, base_priority + 1)
        elif severity == 'low':
            return max(1, base_priority - 1)
        
        return base_priority
    
    def _estimate_action_duration(self, action: str, phase: RecoveryPhase) -> timedelta:
        """Estimate duration for action completion"""
        durations = {
            RecoveryPhase.IMMEDIATE: {
                'default': timedelta(hours=4),
                'Issue public statement': timedelta(hours=2),
                'Remove or modify problematic content': timedelta(hours=1),
                'Monitor social sentiment': timedelta(days=1)
            },
            RecoveryPhase.SHORT_TERM: {
                'default': timedelta(days=3),
                'Conduct internal review': timedelta(days=5),
                'Implement corrective actions': timedelta(days=7)
            },
            RecoveryPhase.MEDIUM_TERM: {
                'default': timedelta(weeks=2),
                'Launch reputation recovery campaign': timedelta(weeks=4),
                'Rebuild trust through transparency': timedelta(weeks=6)
            },
            RecoveryPhase.LONG_TERM: {
                'default': timedelta(weeks=12),
                'Maintain improved practices': timedelta(weeks=52)
            }
        }
        
        phase_durations = durations.get(phase, durations[RecoveryPhase.IMMEDIATE])
        return phase_durations.get(action, phase_durations['default'])
    
    def _identify_required_resources(self, action: str) -> List[str]:
        """Identify resources required for action"""
        resource_map = {
            'Issue public statement': ['Communications Team', 'Legal Review', 'Executive Approval'],
            'Monitor social sentiment': ['Analytics Team', 'Monitoring Tools', 'Data Access'],
            'Conduct internal review': ['Internal Audit Team', 'Process Documentation', 'Stakeholder Access'],
            'Launch reputation recovery campaign': ['Marketing Team', 'Creative Resources', 'Media Budget'],
            'Engage with affected stakeholders': ['Customer Success Team', 'Communication Channels', 'Contact Database']
        }
        
        return resource_map.get(action, ['General Resources', 'Team Assignment'])
    
    def _define_success_metrics(self, action: str) -> List[str]:
        """Define success metrics for action"""
        metrics_map = {
            'Issue public statement': ['Statement reach', 'Sentiment improvement', 'Media pickup'],
            'Monitor social sentiment': ['Coverage completeness', 'Alert accuracy', 'Response time'],
            'Conduct internal review': ['Review completeness', 'Action items identified', 'Timeline adherence'],
            'Launch reputation recovery campaign': ['Brand sentiment', 'Engagement rates', 'Trust metrics'],
            'Engage with affected stakeholders': ['Response rate', 'Satisfaction scores', 'Relationship strength']
        }
        
        return metrics_map.get(action, ['Completion rate', 'Quality score', 'Timeline adherence'])
    
    def _create_recovery_timeline(self, actions: List[RecoveryAction]) -> Dict[str, List[str]]:
        """Create recovery timeline based on actions"""
        timeline = {}
        current_time = datetime.utcnow()
        
        # Group actions by phase
        for phase in RecoveryPhase:
            phase_actions = [a for a in actions if a.phase == phase]
            if phase_actions:
                # Sort by priority
                phase_actions.sort(key=lambda x: x.priority, reverse=True)
                
                timeline[phase.value] = [
                    f"{action.title} (Priority: {action.priority}, Duration: {action.estimated_duration})"
                    for action in phase_actions
                ]
        
        return timeline
    
    def _calculate_budget_allocation(self, actions: List[RecoveryAction], severity: str) -> Dict[str, float]:
        """Calculate budget allocation for recovery strategy"""
        base_budgets = {
            'critical': 100000,
            'high': 50000,
            'medium': 25000,
            'low': 10000
        }
        
        total_budget = base_budgets.get(severity, 25000)
        
        # Allocate by phase
        phase_weights = {
            RecoveryPhase.IMMEDIATE: 0.4,
            RecoveryPhase.SHORT_TERM: 0.3,
            RecoveryPhase.MEDIUM_TERM: 0.2,
            RecoveryPhase.LONG_TERM: 0.1
        }
        
        allocation = {}
        for phase, weight in phase_weights.items():
            allocation[phase.value] = total_budget * weight
        
        return allocation
    
    def _calculate_success_probability(self, crisis_type: str, severity: str, context: Dict[str, Any]) -> float:
        """Calculate probability of successful recovery"""
        base_probabilities = {
            'reputation_damage': {
                'critical': 0.6,
                'high': 0.75,
                'medium': 0.85,
                'low': 0.95
            },
            'content_controversy': {
                'critical': 0.7,
                'high': 0.8,
                'medium': 0.9,
                'low': 0.95
            }
        }
        
        base_prob = base_probabilities.get(crisis_type, base_probabilities['reputation_damage']).get(severity, 0.7)
        
        # Adjust based on context factors
        if context.get('previous_crises', 0) > 0:
            base_prob *= 0.9  # Previous crises reduce success probability
        
        if context.get('stakeholder_support', False):
            base_prob *= 1.1  # Stakeholder support increases probability
        
        if context.get('media_coverage_negative', False):
            base_prob *= 0.85  # Negative media coverage reduces probability
        
        return min(1.0, base_prob)
    
    def _identify_risk_factors(self, crisis_type: str, context: Dict[str, Any]) -> List[str]:
        """Identify risk factors that could impact recovery"""
        risk_factors = []
        
        # General risk factors
        if context.get('media_attention', False):
            risk_factors.append("High media attention increasing scrutiny")
        
        if context.get('competitor_pressure', False):
            risk_factors.append("Competitor exploitation of crisis")
        
        if context.get('regulatory_involvement', False):
            risk_factors.append("Regulatory investigation or intervention")
        
        if context.get('stakeholder_confidence_low', False):
            risk_factors.append("Low stakeholder confidence")
        
        # Crisis-specific risks
        if crisis_type == 'reputation_damage':
            risk_factors.extend([
                "Long-term brand perception impact",
                "Customer churn acceleration",
                "Partner relationship strain"
            ])
        
        return risk_factors
    
    def _create_contingency_plans(self, crisis_type: str, actions: List[RecoveryAction]) -> List[str]:
        """Create contingency plans for potential failures"""
        contingencies = [
            "Escalate to senior leadership if initial response fails",
            "Activate backup communication channels if primary channels compromised",
            "Implement emergency reputation protection measures if situation worsens"
        ]
        
        if crisis_type == 'content_controversy':
            contingencies.extend([
                "Complete content audit and removal if controversy spreads",
                "Temporary content publication pause if needed",
                "Third-party mediation if stakeholder conflicts arise"
            ])
        
        return contingencies
    
    async def execute_recovery_action(self, strategy_id: str, action_id: str) -> bool:
        """Execute a specific recovery action"""
        try:
            if strategy_id not in self.active_strategies:
                raise ValueError(f"Strategy {strategy_id} not found")
            
            strategy = self.active_strategies[strategy_id]
            action = next((a for a in strategy.actions if a.action_id == action_id), None)
            
            if not action:
                raise ValueError(f"Action {action_id} not found in strategy")
            
            if action.status != RecoveryStatus.PLANNED:
                raise ValueError(f"Action {action_id} is not in planned status")
            
            # Update action status
            action.status = RecoveryStatus.IN_PROGRESS
            action.started_at = datetime.utcnow()
            
            self.logger.info(f"Started recovery action: {action.title}")
            
            # Simulate action execution (in real implementation, this would trigger actual actions)
            await asyncio.sleep(1)  # Simulate processing time
            
            # Mark as completed (simplified for demo)
            action.status = RecoveryStatus.COMPLETED
            action.completed_at = datetime.utcnow()
            action.success_score = 0.85  # Simulated success score
            
            self.logger.info(f"Completed recovery action: {action.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Recovery action execution failed: {e}")
            return False
    
    async def get_recovery_status(self, strategy_id: str) -> Dict[str, Any]:
        """Get current status of recovery strategy"""
        try:
            if strategy_id not in self.active_strategies:
                raise ValueError(f"Strategy {strategy_id} not found")
            
            strategy = self.active_strategies[strategy_id]
            
            # Calculate progress metrics
            total_actions = len(strategy.actions)
            completed_actions = sum(1 for a in strategy.actions if a.status == RecoveryStatus.COMPLETED)
            in_progress_actions = sum(1 for a in strategy.actions if a.status == RecoveryStatus.IN_PROGRESS)
            
            progress_percentage = (completed_actions / total_actions * 100) if total_actions > 0 else 0
            
            # Calculate estimated completion
            remaining_actions = [a for a in strategy.actions if a.status == RecoveryStatus.PLANNED]
            estimated_completion = None
            if remaining_actions:
                total_remaining_time = sum([a.estimated_duration for a in remaining_actions], timedelta())
                estimated_completion = datetime.utcnow() + total_remaining_time
            
            return {
                'strategy_id': strategy_id,
                'crisis_id': strategy.crisis_id,
                'created_at': strategy.created_at.isoformat(),
                'progress_percentage': progress_percentage,
                'total_actions': total_actions,
                'completed_actions': completed_actions,
                'in_progress_actions': in_progress_actions,
                'pending_actions': total_actions - completed_actions - in_progress_actions,
                'estimated_completion': estimated_completion.isoformat() if estimated_completion else None,
                'success_probability': strategy.success_probability,
                'current_phase': self._get_current_phase(strategy),
                'next_actions': [
                    {
                        'action_id': a.action_id,
                        'title': a.title,
                        'priority': a.priority,
                        'estimated_duration': str(a.estimated_duration)
                    }
                    for a in strategy.actions 
                    if a.status == RecoveryStatus.PLANNED
                ][:3]  # Next 3 actions
            }
            
        except Exception as e:
            self.logger.error(f"Recovery status retrieval failed: {e}")
            raise
    
    def _get_current_phase(self, strategy: RecoveryStrategy) -> str:
        """Determine current recovery phase"""
        for phase in [RecoveryPhase.IMMEDIATE, RecoveryPhase.SHORT_TERM, 
                     RecoveryPhase.MEDIUM_TERM, RecoveryPhase.LONG_TERM]:
            phase_actions = [a for a in strategy.actions if a.phase == phase]
            incomplete_actions = [a for a in phase_actions if a.status != RecoveryStatus.COMPLETED]
            
            if incomplete_actions:
                return phase.value
        
        return "completed"
    
    async def create_recovery_plan(self, crisis_id: str, crisis_type: str, 
                                 severity_level: str = "medium", 
                                 affected_platforms: List[str] = None) -> Dict[str, Any]:
        """
        Create a comprehensive recovery plan for a crisis
        
        Args:
            crisis_id: Unique crisis identifier
            crisis_type: Type of crisis from CrisisType enum
            severity_level: Severity level (low, medium, high, critical)
            affected_platforms: List of affected platforms
            
        Returns:
            Dict containing the recovery plan details
        """
        try:
            # Create recovery strategy using existing method
            strategy = await self.create_recovery_strategy(
                crisis_id=crisis_id,
                crisis_type=crisis_type,
                severity_level=severity_level,
                affected_platforms=affected_platforms or []
            )
            
            # Format as a comprehensive plan
            recovery_plan = {
                'plan_id': strategy.strategy_id,
                'crisis_id': crisis_id,
                'crisis_type': crisis_type,
                'severity_level': severity_level,
                'affected_platforms': affected_platforms or [],
                'created_at': strategy.created_at.isoformat(),
                'estimated_recovery_time': str(strategy.estimated_recovery_time),
                'success_probability': strategy.success_probability,
                'total_actions': len(strategy.actions),
                'phases': self._format_plan_phases(strategy),
                'timeline': self._create_recovery_timeline(strategy.actions),
                'budget_estimate': self._calculate_budget_estimate(strategy.actions),
                'key_stakeholders': self._identify_key_stakeholders(crisis_type),
                'communication_strategy': self._create_communication_strategy(crisis_type, severity_level),
                'success_metrics': self._define_success_metrics(crisis_type),
                'contingency_plans': self._create_contingency_plans(crisis_type)
            }
            
            self.logger.info(f"Recovery plan created for crisis {crisis_id}: {len(strategy.actions)} actions planned")
            return recovery_plan
            
        except Exception as e:
            self.logger.error(f"Recovery plan creation failed for crisis {crisis_id}: {e}")
            raise
    
    def _format_plan_phases(self, strategy: RecoveryStrategy) -> Dict[str, List[Dict[str, Any]]]:
        """Format recovery actions by phase for the plan"""
        phases = {}
        for phase in RecoveryPhase:
            phase_actions = [a for a in strategy.actions if a.phase == phase]
            phases[phase.value] = [
                {
                    'action_id': a.action_id,
                    'title': a.title,
                    'description': a.description,
                    'priority': a.priority,
                    'estimated_duration': str(a.estimated_duration),
                    'required_resources': a.required_resources,
                    'status': a.status.value
                }
                for a in phase_actions
            ]
        return phases
    
    def _calculate_budget_estimate(self, actions: List[RecoveryAction]) -> Dict[str, float]:
        """Calculate estimated budget for recovery actions"""
        # Simple budget estimation based on action complexity
        budget_estimates = {
            'immediate_response': 5000.0,
            'content_removal': 1000.0,
            'legal_consultation': 10000.0,
            'public_relations': 15000.0,
            'platform_negotiation': 3000.0,
            'monitoring_enhancement': 2000.0,
            'process_improvement': 8000.0
        }
        
        total_budget = 0.0
        breakdown = {}
        
        for action in actions:
            # Estimate based on action title keywords
            action_cost = 2000.0  # Default
            for keyword, cost in budget_estimates.items():
                if keyword.replace('_', ' ') in action.title.lower():
                    action_cost = cost
                    break
            
            breakdown[action.action_id] = action_cost
            total_budget += action_cost
        
        return {
            'total_estimated_cost': total_budget,
            'breakdown_by_action': breakdown,
            'currency': 'USD'
        }
    
    def _identify_key_stakeholders(self, crisis_type: str) -> List[Dict[str, str]]:
        """Identify key stakeholders for the recovery plan"""
        stakeholder_mapping = {
            'reputation_damage': [
                {'role': 'PR Manager', 'responsibility': 'Public communications'},
                {'role': 'Legal Counsel', 'responsibility': 'Legal assessment'},
                {'role': 'Platform Managers', 'responsibility': 'Platform relations'},
                {'role': 'Content Team', 'responsibility': 'Content strategy adjustment'}
            ],
            'negative_sentiment': [
                {'role': 'Community Manager', 'responsibility': 'Community engagement'},
                {'role': 'Content Team', 'responsibility': 'Content adjustment'},
                {'role': 'Data Analyst', 'responsibility': 'Sentiment monitoring'}
            ],
            'platform_policy_violation': [
                {'role': 'Legal Counsel', 'responsibility': 'Policy compliance'},
                {'role': 'Platform Relations', 'responsibility': 'Platform negotiation'},
                {'role': 'Compliance Officer', 'responsibility': 'Policy adherence'}
            ]
        }
        
        return stakeholder_mapping.get(crisis_type, [
            {'role': 'Crisis Manager', 'responsibility': 'Overall coordination'},
            {'role': 'Communications Team', 'responsibility': 'Stakeholder communications'}
        ])
    
    def _create_communication_strategy(self, crisis_type: str, severity_level: str) -> Dict[str, Any]:
        """Create communication strategy for the recovery plan"""
        return {
            'internal_communications': {
                'frequency': 'hourly' if severity_level == 'critical' else 'daily',
                'channels': ['email', 'slack', 'emergency_hotline'],
                'stakeholders': ['management', 'legal', 'pr_team', 'technical_team']
            },
            'external_communications': {
                'public_statement_required': severity_level in ['high', 'critical'],
                'social_media_response': True,
                'media_outreach': severity_level == 'critical',
                'customer_notification': crisis_type in ['platform_policy_violation', 'reputation_damage']
            },
            'messaging_framework': {
                'acknowledge': 'Acknowledge the issue promptly',
                'responsibility': 'Take appropriate responsibility',
                'action': 'Communicate concrete actions being taken',
                'prevention': 'Outline prevention measures for future'
            }
        }
    
    def _define_success_metrics(self, crisis_type: str) -> List[Dict[str, str]]:
        """Define success metrics for recovery plan evaluation"""
        base_metrics = [
            {'metric': 'sentiment_recovery', 'target': 'Return to pre-crisis sentiment levels within 30 days'},
            {'metric': 'engagement_restoration', 'target': 'Restore engagement rates to 90% of pre-crisis levels'},
            {'metric': 'reputation_score', 'target': 'Achieve reputation score above 7.0/10'}
        ]
        
        crisis_specific_metrics = {
            'platform_policy_violation': [
                {'metric': 'policy_compliance', 'target': '100% compliance verification'},
                {'metric': 'platform_relations', 'target': 'Restore good standing on all platforms'}
            ],
            'reputation_damage': [
                {'metric': 'media_coverage', 'target': 'Achieve 60% positive media coverage'},
                {'metric': 'brand_mentions', 'target': 'Reduce negative mentions by 80%'}
            ]
        }
        
        return base_metrics + crisis_specific_metrics.get(crisis_type, [])
    
    def _create_contingency_plans(self, crisis_type: str) -> List[Dict[str, str]]:
        """Create contingency plans for potential escalations"""
        return [
            {
                'scenario': 'Recovery plan fails to show progress within 72 hours',
                'action': 'Activate escalated response protocol with external crisis management firm'
            },
            {
                'scenario': 'Media attention intensifies beyond planned response',
                'action': 'Implement full media strategy with press conferences and interviews'
            },
            {
                'scenario': 'Additional platforms affected during recovery',
                'action': 'Expand recovery plan scope and reallocate resources accordingly'
            },
            {
                'scenario': 'Legal implications emerge during recovery',
                'action': 'Prioritize legal consultation and adjust communications strategy'
            }
        ]


# Export classes
__all__ = [
    'RecoveryPlanner',
    'RecoveryStrategy', 
    'RecoveryAction',
    'RecoveryPhase',
    'RecoveryStatus'
]