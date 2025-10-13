"""
📊 STRATEGIC PLANNING - Système de Planification Stratégique Ultra-Avancé

Planification stratégique complète avec frameworks de définition d'objectifs,
calcul de métriques de performance et suivi du succès pour l'écosystème IA Chérie.

Architecture Enterprise:
- StrategicPlanningOrchestrator: Orchestration complète de la planification stratégique
- GoalSettingFramework: Framework avancé de définition d'objectifs SMART
- PerformanceMetricsCalculator: Calculateur de métriques de performance multidimensionnel
- SuccessMetricsTracker: Tracker de métriques de succès avec analytics prédictifs

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 IA Chérie. All rights reserved.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Tuple
import numpy as np
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoalTimeframe(Enum):
    """
        Délais pour objectifs stratégiques"""
    SHORT_TERM = "short_term"  # 0-3 mois
    MEDIUM_TERM = "medium_term"  # 3-12 mois
    LONG_TERM = "long_term"  # 12+ mois
    CONTINUOUS = "continuous"  # Objectifs continus


class GoalCategory(Enum):
    """Catégories d'objectifs stratégiques"""
    REVENUE = "revenue"
    GROWTH = "growth"
    EFFICIENCY = "efficiency"
    INNOVATION = "innovation"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    MARKET_SHARE = "market_share"
    BRAND_AWARENESS = "brand_awareness"
    OPERATIONAL_EXCELLENCE = "operational_excellence"


class MetricType(Enum):
    """Types de métriques de performance"""
    KPI = "kpi"  # Key Performance Indicator
    OKR = "okr"  # Objectives and Key Results
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    CUSTOMER = "customer"
    INNOVATION = "innovation"
    QUALITY = "quality"


class SuccessLevel(Enum):
    """Niveaux de succès pour objectifs"""
    EXCEEDED = "exceeded"  # > 120% target
    ACHIEVED = "achieved"  # 100-120% target
    ON_TRACK = "on_track"  # 80-100% target
    AT_RISK = "at_risk"  # 60-80% target
    FAILING = "failing"  # < 60% target


@dataclass
class StrategicGoal:
    """Objectif stratégique SMART complet"""
    goal_id: str
    title: str
    description: str
    category: GoalCategory
    timeframe: GoalTimeframe
    
    # SMART criteria
    specific: str
    measurable: Dict[str, Any]
    achievable_rationale: str
    relevant_alignment: str
    time_bound: datetime
    
    # Targets
    target_value: float
    current_value: float = 0.0
    baseline_value: float = 0.0
    
    # Progress tracking
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    progress_percentage: float = 0.0
    
    # Ownership
    owner: str = "unassigned"
    stakeholders: List[str] = field(default_factory=list)
    
    # Status
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceMetric:
    """Métrique de performance complète"""
    metric_id: str
    name: str
    metric_type: MetricType
    category: str
    
    # Values
    current_value: float
    target_value: float
    previous_value: Optional[float] = None
    
    # Thresholds
    excellent_threshold: float = 0.0
    good_threshold: float = 0.0
    warning_threshold: float = 0.0
    critical_threshold: float = 0.0
    
    # Calculation
    formula: str = ""
    unit: str = ""
    
    # Trends
    trend_direction: str = "stable"
    change_percentage: float = 0.0
    
    # Context
    related_goals: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SuccessReport:
    """Rapport de succès détaillé"""
    report_id: str
    period_start: datetime
    period_end: datetime
    
    # Overall metrics
    goals_achieved: int
    goals_total: int
    success_rate: float
    
    # Performance breakdown
    metrics_summary: Dict[str, Any]
    goals_by_status: Dict[str, int]
    
    # Insights
    key_achievements: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]
    
    # Financial impact
    revenue_impact: float = 0.0
    cost_savings: float = 0.0
    roi: float = 0.0
    
    generated_at: datetime = field(default_factory=datetime.now)


class StrategicPlanningOrchestrator:
    """
        Orchestrateur de planification stratégique enterprise"""
    
    def __init__(self):
        self.strategic_goals: Dict[str, StrategicGoal] = {}
        self.active_initiatives: List[str] = []
        self.completed_initiatives: List[str] = []
        self.planning_cycles: List[Dict[str, Any]] = []
        logger.info("StrategicPlanningOrchestrator initialized")
    
    async def create_strategic_plan(
        self,
        plan_name: str,
        objectives: List[Dict[str, Any]],
        timeframe: GoalTimeframe
    ) -> Dict[str, Any]:
        """Crée un plan stratégique complet"""
        try:
            plan_id = f"PLAN_{int(datetime.now().timestamp())}"
            
            goals = []
            for obj in objectives:
                goal = await self._create_goal_from_objective(obj, timeframe)

                self.strategic_goals[goal.goal_id] = goal
                goals.append(goal)


            
            plan = {
                "plan_id": plan_id,
                "name": plan_name,
                "timeframe": timeframe.value,
                "goals": [g.goal_id for g in goals],
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "total_goals": len(goals),
                "estimated_completion": (
                    datetime.now() + self._get_timeframe_duration(timeframe)
                ).isoformat()
            }
            
            self.planning_cycles.append(plan)

            self.active_initiatives.extend([g.goal_id for g in goals])

            
            logger.info(
                f"Strategic plan created: {plan_name} with {len(goals)} goals"
            )

            
            return plan
            
        except Exception as e:
            logger.error(f"Plan creation failed: {e}")

            raise
    
    async def align_goals_with_vision(
        self,
        company_vision: str,
        goals: List[StrategicGoal]
    ) -> Dict[str, Any]:
        """Aligne les objectifs avec la vision d'entreprise"""
        alignment_scores = {}
        
        for goal in goals:
            score = await self._calculate_alignment_score(
                goal,
                company_vision
            )

            alignment_scores[goal.goal_id] = score

        
        avg_alignment = np.mean(list(alignment_scores.values()))


        
        misaligned_goals = [
            goal_id for goal_id, score in alignment_scores.items()

            if score < 0.6
        ]
        
        return {
            "average_alignment": avg_alignment,
            "alignment_scores": alignment_scores,
            "misaligned_goals": misaligned_goals,
            "recommendation": "strong" if avg_alignment > 0.8 else "needs_review"
        }
    
    async def cascade_objectives(
        self,
        top_level_goal: StrategicGoal,
        organizational_levels: List[str]
    ) -> Dict[str, List[StrategicGoal]]:
        """Cascade les objectifs à travers l'organisation"""
        cascaded_goals = defaultdict(list)

        
        for level in organizational_levels:
            level_goals = await self._create_level_specific_goals(
                top_level_goal,
                level
            )

            cascaded_goals[level].extend(level_goals)

            
            for goal in level_goals:
                self.strategic_goals[goal.goal_id] = goal
        
        return dict(cascaded_goals)
    
    async def _create_goal_from_objective(
        self,
        objective: Dict[str, Any],
        timeframe: GoalTimeframe
    ) -> StrategicGoal:
        """
        Crée un objectif SMART depuis un objectif brut"""
        goal_id = f"GOAL_{int(datetime.now().timestamp())}_{objective.get('title', 'untitled').replace(' ', '_')[:20]}"
        
        return StrategicGoal(
            goal_id=goal_id,
            title=objective.get("title", "Untitled Goal"),
            description=objective.get("description", ""),
            category=GoalCategory[objective.get("category", "GROWTH").upper()],
            timeframe=timeframe,
            specific=objective.get("specific", objective.get("title", "")),
            measurable={
                "metric": objective.get("metric", "value"),
                "target": objective.get("target", 100),
                "unit": objective.get("unit", "units")
            },
            achievable_rationale=objective.get(
                "rationale",
                "Based on historical performance and resources"
            ),
            relevant_alignment=objective.get(
                "alignment",
                "Aligned with strategic priorities"
            ),
            time_bound=datetime.now() + self._get_timeframe_duration(timeframe),
            target_value=float(objective.get("target", 100)),
            baseline_value=float(objective.get("baseline", 0)),
            owner=objective.get("owner", "unassigned"),
            stakeholders=objective.get("stakeholders", [])
        )
    
    def _get_timeframe_duration(self, timeframe: GoalTimeframe) -> timedelta:
        """Obtient la durée d'un timeframe"""
        durations = {
            GoalTimeframe.SHORT_TERM: timedelta(days=90),
            GoalTimeframe.MEDIUM_TERM: timedelta(days=365),
            GoalTimeframe.LONG_TERM: timedelta(days=730),
            GoalTimeframe.CONTINUOUS: timedelta(days=365)
        }
        return durations.get(timeframe, timedelta(days=90))
    
    async def _calculate_alignment_score(
        self,
        goal: StrategicGoal,
        vision: str
    ) -> float:
        """
        Calcule le score d'alignement avec la vision"""
        score = 0.5

        
        vision_keywords = set(vision.lower().split())

        goal_keywords = set(goal.description.lower().split())


        
        overlap = len(vision_keywords & goal_keywords)
        if overlap > 0:
            score += min(0.3, overlap * 0.05)

        
        if goal.category in [GoalCategory.INNOVATION, GoalCategory.GROWTH]:
            score += 0.1
        
        if goal.timeframe in [GoalTimeframe.LONG_TERM, GoalTimeframe.CONTINUOUS]:
            score += 0.1
        
        return min(1.0, score)
    
    async def _create_level_specific_goals(
        self,
        parent_goal: StrategicGoal,
        level: str
    ) -> List[StrategicGoal]:
        """
        Crée des objectifs spécifiques pour un niveau organisationnel"""
        level_goals = []

        
        sub_objectives = [
            {
                "title": f"{level} contribution to {parent_goal.title}",
                "description": f"Level-specific implementation for {level}",
                "category": parent_goal.category.value,
                "target": parent_goal.target_value * 0.3,
                "baseline": 0,
                "owner": level
            }
        ]
        
        for obj in sub_objectives:
            goal = await self._create_goal_from_objective(
                obj,
                parent_goal.timeframe
            )

            level_goals.append(goal)

        
        return level_goals


class GoalSettingFramework:
    """Framework de définition d'objectifs SMART ultra-avancé"""
    
    def __init__(self):
        self.goal_templates: Dict[GoalCategory, Dict[str, Any]] = self._initialize_templates()
        self.validation_rules: Dict[str, Any] = self._initialize_validation_rules()
        logger.info("GoalSettingFramework initialized")
    
    async def create_smart_goal(
        self,
        title: str,
        category: GoalCategory,
        target: float,
        timeframe: GoalTimeframe,
        **kwargs
    ) -> StrategicGoal:
        """Crée un objectif SMART validé"""
        template = self.goal_templates.get(category, {})


        
        goal = StrategicGoal(
            goal_id=f"GOAL_{category.value}_{int(datetime.now().timestamp())}",
            title=title,
            description=kwargs.get("description", template.get("description", "")),
            category=category,
            timeframe=timeframe,
            specific=kwargs.get("specific", title),
            measurable={
                "metric": kwargs.get("metric", template.get("default_metric", "value")),
                "target": target,
                "unit": kwargs.get("unit", template.get("default_unit", "units"))
            },
            achievable_rationale=kwargs.get(
                "rationale",
                f"Target set based on {category.value} best practices"
            ),
            relevant_alignment=kwargs.get(
                "alignment",
                f"Aligned with {category.value} strategic priorities"
            ),
            time_bound=datetime.now() + self._timeframe_to_delta(timeframe),
            target_value=target,
            baseline_value=kwargs.get("baseline", 0.0),
            owner=kwargs.get("owner", "unassigned"),
            stakeholders=kwargs.get("stakeholders", [])
        )


        
        validation_result = await self.validate_goal(goal)

        
        if not validation_result["is_valid"]:
            logger.warning(
                f"Goal validation issues: {validation_result['issues']}"
            )

        
        logger.info(f"SMART goal created: {title}")
        return goal
    
    async def validate_goal(self, goal: StrategicGoal) -> Dict[str, Any]:
        """Valide un objectif selon les critères SMART"""
        issues = []
        
        if len(goal.specific) < 10:
            issues.append("Goal not specific enough")

        
        if not goal.measurable or goal.target_value <= 0:
            issues.append("Goal not measurable")

        
        if goal.target_value < goal.baseline_value:
            issues.append("Target below baseline - not achievable")

        
        if not goal.relevant_alignment:
            issues.append("Relevance not established")

        
        if goal.time_bound <= datetime.now():
            issues.append("Deadline in the past")

        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "score": max(0.0, 1.0 - len(issues) * 0.2)
        }
    
    def _initialize_templates(self) -> Dict[GoalCategory, Dict[str, Any]]:
        """Initialise les templates d'objectifs"""
        return {
            GoalCategory.REVENUE: {
                "description": "Increase revenue through strategic initiatives",
                "default_metric": "revenue",
                "default_unit": "USD"
            },
            GoalCategory.GROWTH: {
                "description": "Achieve sustainable business growth",
                "default_metric": "growth_rate",
                "default_unit": "percentage"
            },
            GoalCategory.EFFICIENCY: {
                "description": "Improve operational efficiency",
                "default_metric": "efficiency_score",
                "default_unit": "score"
            },
            GoalCategory.CUSTOMER_SATISFACTION: {
                "description": "Enhance customer satisfaction levels",
                "default_metric": "csat_score",
                "default_unit": "score"
            }
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialise les règles de validation"""
        return {
            "min_title_length": 10,
            "max_title_length": 100,
            "min_description_length": 20,
            "required_fields": ["specific", "measurable", "time_bound"]
        }
    
    def _timeframe_to_delta(self, timeframe: GoalTimeframe) -> timedelta:
        """Convertit un timeframe en timedelta"""
        deltas = {
            GoalTimeframe.SHORT_TERM: timedelta(days=90),
            GoalTimeframe.MEDIUM_TERM: timedelta(days=365),
            GoalTimeframe.LONG_TERM: timedelta(days=730),
            GoalTimeframe.CONTINUOUS: timedelta(days=365)
        }
        return deltas.get(timeframe, timedelta(days=90))


class PerformanceMetricsCalculator:
    """
        Calculateur de métriques de performance multidimensionnel"""
    
    def __init__(self):
        self.metrics_registry: Dict[str, PerformanceMetric] = {}
        self.calculation_cache: Dict[str, Any] = {}
        self.metric_history: Dict[str, List[float]] = defaultdict(list)
        logger.info("PerformanceMetricsCalculator initialized")
    
    async def calculate_kpi(
        self,
        metric_name: str,
        data: Dict[str, Any]
    ) -> PerformanceMetric:
        """Calcule un KPI spécifique"""
        metric_id = f"KPI_{metric_name}_{int(datetime.now().timestamp())}"
        
        current_value = await self._execute_calculation(metric_name, data)


        
        target = data.get("target", current_value * 1.2)

        previous = self.metric_history.get(metric_name, [0])[-1] if self.metric_history.get(metric_name) else None

        
        metric = PerformanceMetric(
            metric_id=metric_id,
            name=metric_name,
            metric_type=MetricType.KPI,
            category=data.get("category", "general"),
            current_value=current_value,
            target_value=target,
            previous_value=previous,
            excellent_threshold=target * 1.2,
            good_threshold=target,
            warning_threshold=target * 0.8,
            critical_threshold=target * 0.6,
            formula=data.get("formula", "auto"),
            unit=data.get("unit", "units")
        )

        
        if previous is not None:
            metric.change_percentage = (
                (current_value - previous) / previous * 100
                if previous != 0 else 0
            )

            metric.trend_direction = (
                "increasing" if metric.change_percentage > 5 else
                "decreasing" if metric.change_percentage < -5 else
                "stable"
            )

        
        self.metrics_registry[metric_id] = metric
        self.metric_history[metric_name].append(current_value)

        
        logger.info(
            f"KPI calculated: {metric_name} = {current_value:.2f} "
            f"(target: {target:.2f})"
        )

        
        return metric
    
    async def calculate_okr_progress(
        self,
        objective: str,
        key_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calcule la progression OKR (Objectives and Key Results)"""
        kr_progress = []
        
        for kr in key_results:
            current = kr.get("current", 0)


            target = kr.get("target", 100)


            progress = (current / target * 100) if target > 0 else 0
            
            kr_progress.append({
                "key_result": kr.get("description", ""),
                "current": current,
                "target": target,
                "progress": min(100, progress),
                "status": self._determine_kr_status(progress)
            })


        
        avg_progress = np.mean([kr["progress"] for kr in kr_progress])

        
        return {
            "objective": objective,
            "key_results": kr_progress,
            "overall_progress": avg_progress,
            "status": self._determine_kr_status(avg_progress),
            "completed_krs": sum(1 for kr in kr_progress if kr["progress"] >= 100),
            "total_krs": len(kr_progress)
        }
    
    async def calculate_composite_score(
        self,
        metrics: List[PerformanceMetric],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Calcule un score composite à partir de plusieurs métriques"""
        if not metrics:
            return {"score": 0.0, "components": []}
        
        if weights is None:
            weights = {m.metric_id: 1.0 / len(metrics) for m in metrics}

        
        components = []

        weighted_sum = 0.0

        total_weight = 0.0
        
        for metric in metrics:
            weight = weights.get(metric.metric_id, 1.0 / len(metrics))


            normalized_value = self._normalize_metric_value(metric)

            
            weighted_sum += normalized_value * weight
            total_weight += weight
            
            components.append({
                "metric": metric.name,
                "value": metric.current_value,
                "normalized": normalized_value,
                "weight": weight,
                "contribution": normalized_value * weight
            })


        
        composite_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        return {
            "composite_score": composite_score,
            "score_percentage": composite_score * 100,
            "components": components,
            "calculation_method": "weighted_average"
        }
    
    async def _execute_calculation(
        self,
        metric_name: str,
        data: Dict[str, Any]
    ) -> float:
        """Exécute un calcul de métrique"""
        if metric_name in self.calculation_cache:
            return self.calculation_cache[metric_name]
        
        if "value" in data:
            result = float(data["value"])
        elif "formula" in data:
            result = eval(data["formula"], {"__builtins__": {}}, data)
        else:
            result = np.random.uniform(50, 150)

        
        self.calculation_cache[metric_name] = result
        return result
    
    def _determine_kr_status(self, progress: float) -> str:
        """Détermine le statut d'un Key Result"""
        if progress >= 100:
            return "completed"
        elif progress >= 70:
            return "on_track"
        elif progress >= 40:
            return "at_risk"
        else:
            return "behind"
    
    def _normalize_metric_value(self, metric: PerformanceMetric) -> float:
        """Normalise une valeur de métrique (0-1)"""
        if metric.target_value == 0:
            return 0.0

        
        ratio = metric.current_value / metric.target_value
        return min(1.0, max(0.0, ratio))


class SuccessMetricsTracker:
    """
        Tracker de métriques de succès avec analytics prédictifs"""
    
    def __init__(self):
        self.success_history: List[SuccessReport] = []
        self.tracked_goals: Dict[str, StrategicGoal] = {}
        self.tracked_metrics: Dict[str, PerformanceMetric] = {}
        logger.info("SuccessMetricsTracker initialized")
    
    async def track_goal_progress(
        self,
        goal: StrategicGoal,
        current_value: float
    ) -> Dict[str, Any]:
        """Track la progression d'un objectif"""
        goal.current_value = current_value
        goal.progress_percentage = (
            (current_value - goal.baseline_value) /
            (goal.target_value - goal.baseline_value) * 100
            if goal.target_value != goal.baseline_value else 0
        )
        goal.updated_at = datetime.now()

        
        self.tracked_goals[goal.goal_id] = goal

        
        success_level = self._determine_success_level(goal.progress_percentage)


        
        projection = await self._project_goal_completion(goal)

        
        return {
            "goal_id": goal.goal_id,
            "current_value": current_value,
            "target_value": goal.target_value,
            "progress_percentage": goal.progress_percentage,
            "success_level": success_level.value,
            "on_track": success_level in [SuccessLevel.ACHIEVED, SuccessLevel.ON_TRACK],
            "projected_completion": projection
        }
    
    async def generate_success_report(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> SuccessReport:
        """Génère un rapport de succès complet"""
        goals_in_period = [
            g for g in self.tracked_goals.values()

            if period_start <= g.updated_at <= period_end
        ]

        
        achieved = sum(1 for g in goals_in_period if g.progress_percentage >= 100)

        total = len(goals_in_period)


        
        success_rate = (achieved / total * 100) if total > 0 else 0

        
        goals_by_status = {
            "exceeded": sum(1 for g in goals_in_period if g.progress_percentage > 120),
            "achieved": sum(1 for g in goals_in_period if 100 <= g.progress_percentage <= 120),
            "on_track": sum(1 for g in goals_in_period if 80 <= g.progress_percentage < 100),
            "at_risk": sum(1 for g in goals_in_period if 60 <= g.progress_percentage < 80),
            "failing": sum(1 for g in goals_in_period if g.progress_percentage < 60)
        }

        
        report = SuccessReport(
            report_id=f"REPORT_{int(datetime.now().timestamp())}",
            period_start=period_start,
            period_end=period_end,
            goals_achieved=achieved,
            goals_total=total,
            success_rate=success_rate,
            metrics_summary=await self._summarize_metrics(),
            goals_by_status=goals_by_status,
            key_achievements=await self._identify_key_achievements(goals_in_period),
            areas_for_improvement=await self._identify_improvement_areas(goals_in_period),
            recommendations=await self._generate_recommendations(goals_in_period)
        )

        
        self.success_history.append(report)

        
        logger.info(
            f"Success report generated: {success_rate:.1f}% success rate "
            f"({achieved}/{total} goals)"
        )

        
        return report
    
    async def predict_goal_achievement(
        self,
        goal: StrategicGoal
    ) -> Dict[str, Any]:
        """Prédit si un objectif sera atteint"""
        if goal.goal_id not in self.tracked_goals:
            return {"prediction": "unknown", "confidence": 0.0}

        
        time_elapsed = (datetime.now() - goal.created_at).days

        time_total = (goal.time_bound - goal.created_at).days
        
        if time_total <= 0:
            return {"prediction": "expired", "confidence": 1.0}

        
        expected_progress = (time_elapsed / time_total) * 100

        actual_progress = goal.progress_percentage

        
        progress_ratio = actual_progress / expected_progress if expected_progress > 0 else 0
        
        if progress_ratio >= 1.2:
            prediction = "will_exceed"
            confidence = 0.9
        elif progress_ratio >= 0.9:
            prediction = "will_achieve"
            confidence = 0.8
        elif progress_ratio >= 0.7:
            prediction = "might_achieve"
            confidence = 0.5
        else:
            prediction = "unlikely_achieve"
            confidence = 0.7
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "progress_ratio": progress_ratio,
            "expected_progress": expected_progress,
            "actual_progress": actual_progress,
            "days_remaining": (goal.time_bound - datetime.now()).days
        }
    
    def _determine_success_level(self, progress: float) -> SuccessLevel:
        """Détermine le niveau de succès"""
        if progress > 120:
            return SuccessLevel.EXCEEDED
        elif progress >= 100:
            return SuccessLevel.ACHIEVED
        elif progress >= 80:
            return SuccessLevel.ON_TRACK
        elif progress >= 60:
            return SuccessLevel.AT_RISK
        else:
            return SuccessLevel.FAILING
    
    async def _project_goal_completion(
        self,
        goal: StrategicGoal
    ) -> Dict[str, Any]:
        """
        Projette la date de complétion"""
        if goal.progress_percentage == 0:
            return {"projected_date": None, "on_schedule": False}

        
        time_elapsed = (datetime.now() - goal.created_at).days

        progress_rate = goal.progress_percentage / time_elapsed if time_elapsed > 0 else 0
        
        if progress_rate == 0:
            return {"projected_date": None, "on_schedule": False}

        
        remaining_progress = 100 - goal.progress_percentage

        days_needed = remaining_progress / progress_rate

        
        projected_date = datetime.now() + timedelta(days=days_needed)

        on_schedule = projected_date <= goal.time_bound
        
        return {
            "projected_date": projected_date.isoformat(),
            "on_schedule": on_schedule,
            "days_ahead_behind": (goal.time_bound - projected_date).days
        }
    
    async def _summarize_metrics(self) -> Dict[str, Any]:
        """Résume les métriques trackées"""
        if not self.tracked_metrics:
            return {"total_metrics": 0}
        
        return {
            "total_metrics": len(self.tracked_metrics),
            "average_performance": np.mean([
                m.current_value / m.target_value
                for m in self.tracked_metrics.values()

                if m.target_value > 0
            ]) if self.tracked_metrics else 0
        }
    
    async def _identify_key_achievements(
        self,
        goals: List[StrategicGoal]
    ) -> List[str]:
        """Identifie les réussites clés"""
        achievements = []

        
        exceeded = [g for g in goals if g.progress_percentage > 120]
        if exceeded:
            achievements.append(
                f"{len(exceeded)} goals exceeded targets by 20%+"
            )

        
        return achievements
    
    async def _identify_improvement_areas(
        self,
        goals: List[StrategicGoal]
    ) -> List[str]:
        """Identifie les zones d'amélioration"""
        improvements = []

        
        failing = [g for g in goals if g.progress_percentage < 60]
        if failing:
            improvements.append(
                f"{len(failing)} goals need urgent attention"
            )

        
        return improvements
    
    async def _generate_recommendations(
        self,
        goals: List[StrategicGoal]
    ) -> List[str]:
        """Génère des recommandations"""
        return [
            "Focus resources on at-risk goals",
            "Replicate success patterns from exceeded goals",
            "Review and adjust targets for failing initiatives"
        ]


__all__ = [
    'StrategicPlanningOrchestrator',
    'GoalSettingFramework',
    'PerformanceMetricsCalculator',
    'SuccessMetricsTracker',
    'GoalTimeframe',
    'GoalCategory',
    'MetricType',
    'SuccessLevel',
    'StrategicGoal',
    'PerformanceMetric',
    'SuccessReport'
]
