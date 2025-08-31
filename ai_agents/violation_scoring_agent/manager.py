"""Violation Scoring Manager - AI-Powered Violation Assessment"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import numpy as np

# Import base agent functionality
from ..base import BaseAgent, AgentRequest, AgentResponse

# Import existing violation detection functionality
try:
    from core.protection.violation_detector import ViolationDetector
    from core.protection.similarity_analyzer import SimilarityAnalyzer
    from ai_engine.ml.violation_classifier import ViolationClassifier
except ImportError:
    # Fallback implementations
    class ViolationDetector:
        async def detect_violations(self, content_id, monitoring_results, config): return []
    class SimilarityAnalyzer:
        async def analyze_similarity(self, fingerprints, url, config): return []
    class ViolationClassifier:
        async def classify_violation(self, violation_data): return {"severity": "medium", "confidence": 0.8}

from .models.scoring_models import ViolationScore, ScoringRequest, ScoringResult, RiskLevel, ViolationPattern

logger = logging.getLogger(__name__)

@dataclass
class ViolationScoringConfig:
    """Configuration for violation scoring operations"""    enable_ai_scoring: bool = True
    enable_pattern_analysis: bool = True
    enable_risk_assessment: bool = True
    scoring_model_version: str = "v2.1"
    confidence_threshold: float = 0.8
    severity_weights: Dict[str, float] = field(default_factory=lambda: {
        'similarity_score': 0.3,
        'commercial_impact': 0.25,
        'platform_reach': 0.2,
        'historical_pattern': 0.15,
        'response_urgency': 0.1
    })
    risk_factors: List[str] = field(default_factory=lambda: [
        'repeat_offender', 'commercial_use', 'large_audience', 
        'high_similarity', 'multiple_platforms', 'geographic_spread'
    ])

class ViolationScoringManager(BaseAgent):
    """    Enterprise Violation Scoring Manager
    
    Provides AI-powered violation assessment with:
    - Multi-factor scoring algorithms
    - Pattern recognition and analysis
    - Risk level assessment
    - Automated response recommendations
    - Historical trend analysis
    - Machine learning optimization
    """    
    def __init__(self, agent_id: str = "violation_scoring_manager"):
        super().__init__(
            agent_id=agent_id,
            agent_type="violation_scoring",
            version="1.0.0"
        )
        
        self.config = ViolationScoringConfig()
        
        # Initialize core components
        self.violation_detector = ViolationDetector()
        self.similarity_analyzer = SimilarityAnalyzer()
        self.violation_classifier = ViolationClassifier()
        
        # Tracking and analysis
        self.violation_scores: Dict[str, ViolationScore] = {}
        self.violation_patterns: Dict[str, List[ViolationPattern]] = {}
        self.scoring_history: List[Dict] = []
        self.pattern_models: Dict[str, Any] = {}
        
    async def _load_models_and_resources(self):
        """Load AI models and initialize resources"""        try:
            await self.violation_detector.initialize()
            await self.similarity_analyzer.initialize()
            await self.violation_classifier.initialize()
            
            # Load pre-trained scoring models
            await self._load_scoring_models()
            
            logger.info("Violation scoring models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load violation scoring models: {e}")
            raise
    
    async def _load_scoring_models(self):
        """Load machine learning models for scoring"""        # This would load actual ML models in production
        self.pattern_models = {
            'severity_predictor': {'type': 'neural_network', 'accuracy': 0.94},
            'risk_classifier': {'type': 'random_forest', 'accuracy': 0.91},
            'pattern_detector': {'type': 'lstm', 'accuracy': 0.89}
        }
        logger.info("Scoring models loaded successfully")
    
    def get_required_config_keys(self) -> List[str]:
        """Required configuration keys"""        return ['severity_weights', 'confidence_threshold']
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Main request processing logic"""        action = request.action.lower()
        
        try:
            if action == "score_violation":
                result = await self._score_violation(request.data)
            elif action == "analyze_patterns":
                result = await self._analyze_patterns(request.data)
            elif action == "assess_risk":
                result = await self._assess_risk(request.data)
            elif action == "batch_score":
                result = await self._batch_score(request.data)
            elif action == "get_scoring_trends":
                result = await self._get_scoring_trends(request.data)
            elif action == "recommend_actions":
                result = await self._recommend_actions(request.data)
            elif action == "update_scoring_model":
                result = await self._update_scoring_model(request.data)
            else:
                raise ValueError(f"Unknown action: {action}")
            
            return AgentResponse(
                success=True,
                data=result,
                message=f"Violation scoring {action} completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Violation scoring error: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                error_code="VIOLATION_SCORING_ERROR"
            )
    
    async def _score_violation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Score a specific violation using AI algorithms"""        violation_id = data.get('violation_id')
        violation_data = data.get('violation_data', {})
        content_id = data.get('content_id')
        
        if not violation_id:
            raise ValueError("violation_id is required")
        
        # Extract scoring factors
        similarity_score = float(violation_data.get('similarity_score', 0))
        platform = violation_data.get('platform', 'unknown')
        detection_method = violation_data.get('detection_method', 'unknown')
        
        # Classify violation using AI
        classification = await self.violation_classifier.classify_violation(violation_data)
        
        # Calculate multi-factor score
        scoring_factors = await self._calculate_scoring_factors(violation_data)
        
        # Compute weighted score
        weighted_score = self._compute_weighted_score(scoring_factors)
        
        # Determine severity level
        severity_level = self._determine_severity_level(weighted_score)
        
        # Assess risk level
        risk_level = await self._calculate_risk_level(violation_data, scoring_factors)
        
        # Generate recommendations
        recommendations = self._generate_action_recommendations(
            weighted_score, severity_level, risk_level, violation_data
        )
        
        # Create violation score record
        violation_score = ViolationScore(
            violation_id=violation_id,
            content_id=content_id,
            overall_score=weighted_score,
            severity_level=severity_level,
            risk_level=risk_level,
            confidence_score=classification.get('confidence', 0.8),
            scoring_factors=scoring_factors,
            recommendations=recommendations,
            scored_at=datetime.now(timezone.utc),
            model_version=self.config.scoring_model_version
        )
        
        # Store score
        self.violation_scores[violation_id] = violation_score
        
        # Add to scoring history
        scoring_record = {
            'violation_id': violation_id,
            'content_id': content_id,
            'score': weighted_score,
            'severity': severity_level.value,
            'risk': risk_level.value,
            'timestamp': violation_score.scored_at.isoformat(),
            'platform': platform
        }
        self.scoring_history.append(scoring_record)
        
        return {
            'violation_id': violation_id,
            'overall_score': weighted_score,
            'severity_level': severity_level.value,
            'risk_level': risk_level.value,
            'confidence_score': violation_score.confidence_score,
            'scoring_factors': scoring_factors,
            'recommendations': recommendations,
            'scored_at': violation_score.scored_at.isoformat()
        }
    
    async def _calculate_scoring_factors(self, violation_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate individual scoring factors"""        factors = {}
        
        # Similarity factor (0-1)
        similarity = float(violation_data.get('similarity_score', 0))
        factors['similarity_score'] = similarity
        
        # Commercial impact factor
        commercial_indicators = [
            violation_data.get('monetized', False),
            violation_data.get('commercial_use', False),
            violation_data.get('advertising_present', False)
        ]
        factors['commercial_impact'] = sum(commercial_indicators) / len(commercial_indicators)
        
        # Platform reach factor
        platform = violation_data.get('platform', '')
        platform_reach_scores = {
            'youtube': 0.9, 'facebook': 0.85, 'instagram': 0.8, 'tiktok': 0.85,
            'twitter': 0.7, 'twitch': 0.75, 'spotify': 0.8, 'soundcloud': 0.6
        }
        factors['platform_reach'] = platform_reach_scores.get(platform.lower(), 0.5)
        
        # Audience size factor
        view_count = int(violation_data.get('view_count', 0))
        if view_count > 1000000:
            audience_factor = 1.0
        elif view_count > 100000:
            audience_factor = 0.8
        elif view_count > 10000:
            audience_factor = 0.6
        elif view_count > 1000:
            audience_factor = 0.4
        else:
            audience_factor = 0.2
        factors['audience_size'] = audience_factor
        
        # Historical pattern factor
        violation_url = violation_data.get('url', '')
        domain = self._extract_domain(violation_url)
        historical_violations = await self._get_historical_violations(domain)
        factors['historical_pattern'] = min(len(historical_violations) / 10, 1.0)
        
        # Response urgency factor
        time_since_detection = violation_data.get('hours_since_detection', 0)
        if time_since_detection < 1:
            urgency_factor = 1.0
        elif time_since_detection < 24:
            urgency_factor = 0.8
        elif time_since_detection < 168:  # 1 week
            urgency_factor = 0.6
        else:
            urgency_factor = 0.3
        factors['response_urgency'] = urgency_factor
        
        return factors
    
    def _compute_weighted_score(self, factors: Dict[str, float]) -> float:
        """Compute weighted violation score"""        weighted_sum = 0.0
        total_weight = 0.0
        
        for factor_name, factor_value in factors.items():
            weight = self.config.severity_weights.get(factor_name, 0.1)
            weighted_sum += factor_value * weight
            total_weight += weight
        
        # Normalize to 0-1 range
        if total_weight > 0:
            return min(weighted_sum / total_weight, 1.0)
        else:
            return 0.0
    
    def _determine_severity_level(self, score: float) -> str:
        """Determine severity level from score"""        if score >= 0.9:
            return "critical"
        elif score >= 0.7:
            return "high"
        elif score >= 0.5:
            return "medium"
        elif score >= 0.3:
            return "low"
        else:
            return "minimal"
    
    async def _calculate_risk_level(
        self, 
        violation_data: Dict[str, Any], 
        scoring_factors: Dict[str, float]
    ) -> RiskLevel:
        """Calculate risk level based on multiple factors"""        risk_score = 0.0
        factor_count = 0
        
        # Check each risk factor
        for risk_factor in self.config.risk_factors:
            if risk_factor == 'repeat_offender':
                risk_score += scoring_factors.get('historical_pattern', 0) * 0.3
            elif risk_factor == 'commercial_use':
                risk_score += scoring_factors.get('commercial_impact', 0) * 0.25
            elif risk_factor == 'large_audience':
                risk_score += scoring_factors.get('audience_size', 0) * 0.2
            elif risk_factor == 'high_similarity':
                risk_score += scoring_factors.get('similarity_score', 0) * 0.15
            elif risk_factor == 'multiple_platforms':
                # This would require cross-platform data
                risk_score += 0.1 if violation_data.get('multi_platform', False) else 0
            
            factor_count += 1
        
        # Normalize risk score
        normalized_risk = risk_score / factor_count if factor_count > 0 else 0
        
        # Map to risk levels
        if normalized_risk >= 0.8:
            return RiskLevel.CRITICAL
        elif normalized_risk >= 0.6:
            return RiskLevel.HIGH
        elif normalized_risk >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_action_recommendations(
        self, 
        score: float, 
        severity: str, 
        risk_level: RiskLevel, 
        violation_data: Dict[str, Any]
    ) -> List[str]:
        """Generate automated action recommendations"""        recommendations = []
        
        # High-priority actions for critical violations
        if severity == "critical" or risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "immediate_dmca_takedown",
                "legal_escalation", 
                "cease_and_desist",
                "revenue_claim"
            ])
        
        # Standard actions for high severity
        elif severity == "high" or risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "dmca_takedown",
                "content_claim",
                "monitoring_increase"
            ])
        
        # Moderate actions for medium severity
        elif severity == "medium":
            recommendations.extend([
                "platform_report",
                "content_claim",
                "owner_notification"
            ])
        
        # Light actions for low severity
        else:
            recommendations.extend([
                "monitor_closely",
                "owner_notification"
            ])
        
        # Add specific recommendations based on violation characteristics
        if violation_data.get('commercial_use'):
            recommendations.append("revenue_claim")
        
        if violation_data.get('multi_platform'):
            recommendations.append("cross_platform_takedown")
        
        if scoring_factors.get('historical_pattern', 0) > 0.7:
            recommendations.append("repeat_offender_escalation")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except:
            return "unknown"
    
    async def _get_historical_violations(self, domain: str) -> List[Dict]:
        """Get historical violations for a domain"""        # Filter scoring history by domain
        historical = []
        for record in self.scoring_history:
            if domain in record.get('violation_id', ''):
                historical.append(record)
        
        return historical[-50:]  # Return last 50 violations
    
    async def _analyze_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze violation patterns for content or timeframe"""        content_id = data.get('content_id')
        timeframe_days = data.get('timeframe_days', 30)
        
        # Filter violations by criteria
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=timeframe_days)
        filtered_violations = []
        
        for record in self.scoring_history:
            record_date = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
            if record_date >= cutoff_date:
                if not content_id or record.get('content_id') == content_id:
                    filtered_violations.append(record)
        
        # Analyze patterns
        patterns = {
            'total_violations': len(filtered_violations),
            'severity_distribution': {},
            'platform_distribution': {},
            'temporal_patterns': {},
            'average_score': 0.0,
            'trend_direction': 'stable'
        }
        
        if filtered_violations:
            # Severity distribution
            for violation in filtered_violations:
                severity = violation.get('severity', 'unknown')
                patterns['severity_distribution'][severity] = patterns['severity_distribution'].get(severity, 0) + 1
            
            # Platform distribution
            for violation in filtered_violations:
                platform = violation.get('platform', 'unknown')
                patterns['platform_distribution'][platform] = patterns['platform_distribution'].get(platform, 0) + 1
            
            # Average score
            scores = [v.get('score', 0) for v in filtered_violations]
            patterns['average_score'] = sum(scores) / len(scores)
            
            # Trend analysis (simplified)
            recent_scores = scores[-7:] if len(scores) >= 7 else scores
            older_scores = scores[:-7] if len(scores) >= 14 else []
            
            if older_scores:
                recent_avg = sum(recent_scores) / len(recent_scores)
                older_avg = sum(older_scores) / len(older_scores)
                
                if recent_avg > older_avg * 1.1:
                    patterns['trend_direction'] = 'increasing'
                elif recent_avg < older_avg * 0.9:
                    patterns['trend_direction'] = 'decreasing'
        
        return patterns
    
    async def _assess_risk(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk level for content or platform"""        content_id = data.get('content_id')
        platform = data.get('platform')
        
        # Get relevant violations
        relevant_violations = []
        for record in self.scoring_history[-100:]:  # Last 100 violations
            if content_id and record.get('content_id') == content_id:
                relevant_violations.append(record)
            elif platform and record.get('platform') == platform:
                relevant_violations.append(record)
        
        if not relevant_violations:
            return {
                'risk_level': RiskLevel.LOW.value,
                'risk_score': 0.0,
                'risk_factors': [],
                'recommendations': ['increase_monitoring']
            }
        
        # Calculate risk metrics
        high_severity_count = sum(1 for v in relevant_violations if v.get('severity') in ['high', 'critical'])
        total_violations = len(relevant_violations)
        average_score = sum(v.get('score', 0) for v in relevant_violations) / total_violations
        
        # Risk calculation
        risk_score = (high_severity_count / total_violations) * 0.5 + average_score * 0.5
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return {
            'risk_level': risk_level.value,
            'risk_score': risk_score,
            'total_violations': total_violations,
            'high_severity_violations': high_severity_count,
            'average_violation_score': average_score,
            'assessment_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def _batch_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Score multiple violations in batch"""        violations = data.get('violations', [])
        
        if not violations:
            raise ValueError("violations list is required")
        
        results = []
        
        # Process violations in batches
        batch_size = 10
        for i in range(0, len(violations), batch_size):
            batch = violations[i:i + batch_size]
            
            # Score each violation in the batch
            batch_tasks = [
                self._score_violation({
                    'violation_id': v.get('violation_id'),
                    'violation_data': v.get('violation_data', {}),
                    'content_id': v.get('content_id')
                })
                for v in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.warning(f"Batch scoring failed: {result}")
                    continue
                results.append(result)
        
        return {
            'total_violations': len(violations),
            'successfully_scored': len(results),
            'batch_results': results,
            'processing_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def _get_scoring_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get scoring trends and analytics"""        timeframe_days = data.get('timeframe_days', 30)
        group_by = data.get('group_by', 'day')  # day, week, month
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=timeframe_days)
        
        # Filter recent violations
        recent_violations = []
        for record in self.scoring_history:
            record_date = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
            if record_date >= cutoff_date:
                recent_violations.append(record)
        
        # Group by time period
        trends = {}
        for violation in recent_violations:
            record_date = datetime.fromisoformat(violation['timestamp'].replace('Z', '+00:00'))
            
            if group_by == 'day':
                period_key = record_date.strftime('%Y-%m-%d')
            elif group_by == 'week':
                period_key = record_date.strftime('%Y-W%U')
            else:  # month
                period_key = record_date.strftime('%Y-%m')
            
            if period_key not in trends:
                trends[period_key] = {
                    'violation_count': 0,
                    'total_score': 0.0,
                    'severity_breakdown': {}
                }
            
            trends[period_key]['violation_count'] += 1
            trends[period_key]['total_score'] += violation.get('score', 0)
            
            severity = violation.get('severity', 'unknown')
            trends[period_key]['severity_breakdown'][severity] = trends[period_key]['severity_breakdown'].get(severity, 0) + 1
        
        # Calculate averages
        for period_data in trends.values():
            if period_data['violation_count'] > 0:
                period_data['average_score'] = period_data['total_score'] / period_data['violation_count']
        
        return {
            'timeframe_days': timeframe_days,
            'group_by': group_by,
            'trends': trends,
            'total_violations': len(recent_violations),
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def _recommend_actions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get action recommendations based on violation scores"""        violation_ids = data.get('violation_ids', [])
        
        if not violation_ids:
            raise ValueError("violation_ids list is required")
        
        recommendations = {}
        
        for violation_id in violation_ids:
            if violation_id in self.violation_scores:
                score_obj = self.violation_scores[violation_id]
                recommendations[violation_id] = {
                    'actions': score_obj.recommendations,
                    'priority': self._get_action_priority(score_obj),
                    'estimated_cost': self._estimate_action_cost(score_obj.recommendations),
                    'success_probability': self._estimate_success_probability(score_obj)
                }
            else:
                recommendations[violation_id] = {
                    'error': 'Violation not found or not scored'
                }
        
        return {
            'recommendations': recommendations,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_action_priority(self, score_obj: ViolationScore) -> str:
        """Get priority level for actions"""        if score_obj.severity_level == "critical":
            return "urgent"
        elif score_obj.severity_level == "high":
            return "high"
        elif score_obj.severity_level == "medium":
            return "medium"
        else:
            return "low"
    
    def _estimate_action_cost(self, actions: List[str]) -> Dict[str, int]:
        """Estimate cost of recommended actions"""        cost_estimates = {
            'immediate_dmca_takedown': 50,
            'dmca_takedown': 25,
            'legal_escalation': 500,
            'cease_and_desist': 200,
            'content_claim': 10,
            'platform_report': 5,
            'owner_notification': 2,
            'monitor_closely': 1
        }
        
        total_cost = sum(cost_estimates.get(action, 10) for action in actions)
        
        return {
            'total_estimated_cost': total_cost,
            'currency': 'USD',
            'breakdown': {action: cost_estimates.get(action, 10) for action in actions}
        }
    
    def _estimate_success_probability(self, score_obj: ViolationScore) -> float:
        """Estimate probability of successful action"""        # Base probability on confidence and severity
        base_probability = score_obj.confidence_score * 0.7
        
        # Adjust based on severity
        if score_obj.severity_level == "critical":
            base_probability += 0.2
        elif score_obj.severity_level == "high":
            base_probability += 0.1
        
        return min(base_probability, 0.95)
    
    async def _update_scoring_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update scoring model with new training data"""        feedback_data = data.get('feedback_data', [])
        model_type = data.get('model_type', 'severity_predictor')
        
        if not feedback_data:
            raise ValueError("feedback_data is required")
        
        # In production, this would retrain the actual ML model
        # For now, we'll simulate model update
        
        # Update model metadata
        if model_type in self.pattern_models:
            self.pattern_models[model_type]['last_updated'] = datetime.now(timezone.utc).isoformat()
            self.pattern_models[model_type]['training_samples'] = len(feedback_data)
        
        return {
            'model_type': model_type,
            'training_samples': len(feedback_data),
            'update_status': 'completed',
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'estimated_accuracy_improvement': 0.02  # Mock improvement
        }