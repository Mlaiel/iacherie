"""
Influencer Matching Manager - Ultra-Advanced Enterprise Management System

Unified interface for influencer-brand matching providing comprehensive
control, monitoring, and optimization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from .core.matching_engine import MatchingEngine
from ..base import BaseAgent, AgentResponse, AgentRequest
try:
    from core.exceptions import ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception):
        pass
    class ConfigurationError(Exception):
        pass
    class ProcessingError(Exception):
        pass

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()

logger = logging.getLogger(__name__)

@dataclass
class MatchingSystemStatus:
    """System status for influencer matching operations"""
    engine_status: str
    active_matching_jobs: int
    total_influencers_in_database: int
    total_successful_matches: int
    last_update: datetime
    performance_metrics: Dict[str, Any]

class InfluencerMatchingManager(BaseAgent):
    """
    Master Influencer Matching Manager
    
    Unified interface for influencer-brand matching providing:
    - AI-powered influencer discovery and matching
    - Comprehensive compatibility analysis
    - Audience overlap and demographic analysis
    - Brand safety assessment and risk evaluation
    - Campaign performance prediction
    - Budget estimation and optimization
    - Real-time matching recommendations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id=f"influencer-matching-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            agent_type="influencer_matching",
            version="1.0.0",
            config=config
        )
        
        # Core System Components
        self.engine = MatchingEngine(config)
        
        # System State
        self.is_running = False
        
        logger.info("InfluencerMatchingManager initialized")

    async def initialize(self) -> bool:
        """Initialize the influencer matching system"""
        try:
            await super().initialize()
            await self.engine.start()
            self.is_running = True
            logger.info("Influencer Matching System started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize influencer matching system: {e}")
            return False

    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process influencer matching requests"""
        try:
            action = request.action
            data = request.data
            
            if action == "find_matches":
                result = await self._find_matching_influencers(data)
            elif action == "analyze_compatibility":
                result = await self._analyze_compatibility(data)
            elif action == "assess_brand_safety":
                result = await self._assess_brand_safety(data)
            elif action == "predict_performance":
                result = await self._predict_campaign_performance(data)
            elif action == "calculate_budget":
                result = await self._calculate_collaboration_budget(data)
            elif action == "analyze_audience_overlap":
                result = await self._analyze_audience_overlap(data)
            elif action == "batch_analysis":
                result = await self._batch_influencer_analysis(data)
            else:
                raise ValidationError(f"Unknown action: {action}")
            
            return AgentResponse(
                success=True,
                request_id=request.request_id,
                data=result,
                message="Influencer matching completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Influencer matching processing failed: {e}")
            return AgentResponse(
                success=False,
                request_id=request.request_id,
                error=str(e),
                message="Influencer matching failed"
            )

    async def _find_matching_influencers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Find matching influencers for a brand campaign"""
        brand_profile = data.get('brand_profile', {})
        campaign_requirements = data.get('campaign_requirements', {})
        
        # Validate required data
        if not brand_profile or not campaign_requirements:
            raise ValidationError("Brand profile and campaign requirements are required")
        
        # Find matches using the engine
        matches = await self.engine.find_matching_influencers(brand_profile, campaign_requirements)
        
        # Categorize matches by compatibility score
        excellent_matches = [m for m in matches if m.compatibility_score >= 0.9]
        good_matches = [m for m in matches if 0.8 <= m.compatibility_score < 0.9]
        moderate_matches = [m for m in matches if 0.7 <= m.compatibility_score < 0.8]
        
        # Calculate summary statistics
        total_estimated_reach = sum(match.estimated_reach for match in matches)
        average_compatibility = sum(match.compatibility_score for match in matches) / len(matches) if matches else 0
        
        return {
            "total_matches_found": len(matches),
            "matches_by_tier": {
                "excellent": len(excellent_matches),
                "good": len(good_matches),
                "moderate": len(moderate_matches)
            },
            "top_matches": [self._serialize_match_result(match) for match in matches[:10]],
            "all_matches": [self._serialize_match_result(match) for match in matches],
            "summary_metrics": {
                "total_estimated_reach": total_estimated_reach,
                "average_compatibility_score": round(average_compatibility, 2),
                "recommended_budget_range": self._calculate_budget_range(matches[:5])
            },
            "search_criteria": campaign_requirements,
            "matching_timestamp": datetime.utcnow().isoformat()
        }

    async def _analyze_compatibility(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze compatibility between specific influencer and brand"""
        influencer_id = data.get('influencer_id', '')
        brand_profile = data.get('brand_profile', {})
        campaign_requirements = data.get('campaign_requirements', {})
        
        if not influencer_id or not brand_profile:
            raise ValidationError("Influencer ID and brand profile are required")
        
        # Get influencer profile (mock implementation)
        influencer_profile = await self.engine._get_influencer_profile(influencer_id)
        
        # Calculate compatibility score
        compatibility_score = await self.engine._calculate_compatibility_score(
            brand_profile, influencer_profile, campaign_requirements
        )
        
        # Analyze audience overlap
        audience_overlap = await self.engine.analyze_audience_overlap(
            influencer_id, brand_profile.get('target_audience', {})
        )
        
        # Generate detailed compatibility breakdown
        compatibility_breakdown = await self._generate_compatibility_breakdown(
            brand_profile, influencer_profile, campaign_requirements
        )
        
        return {
            "influencer_id": influencer_id,
            "overall_compatibility_score": compatibility_score,
            "compatibility_breakdown": compatibility_breakdown,
            "audience_overlap_analysis": audience_overlap,
            "collaboration_recommendation": self._get_collaboration_recommendation(compatibility_score),
            "improvement_suggestions": await self._get_improvement_suggestions(
                compatibility_score, compatibility_breakdown
            ),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    async def _assess_brand_safety(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess brand safety for specific influencer"""
        influencer_id = data.get('influencer_id', '')
        brand_guidelines = data.get('brand_guidelines', {})
        
        if not influencer_id:
            raise ValidationError("Influencer ID is required")
        
        # Perform brand safety assessment
        safety_assessment = await self.engine.assess_brand_safety(influencer_id, brand_guidelines)
        
        # Generate risk mitigation strategies
        risk_mitigation = await self._generate_risk_mitigation_strategies(safety_assessment)
        
        # Content monitoring recommendations
        monitoring_recommendations = await self._get_content_monitoring_recommendations(
            safety_assessment['overall_safety_score']
        )
        
        return {
            "influencer_id": influencer_id,
            "safety_assessment": safety_assessment,
            "risk_mitigation_strategies": risk_mitigation,
            "monitoring_recommendations": monitoring_recommendations,
            "compliance_checklist": await self._generate_compliance_checklist(brand_guidelines),
            "assessment_timestamp": datetime.utcnow().isoformat()
        }

    async def _predict_campaign_performance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict campaign performance for influencer"""
        influencer_id = data.get('influencer_id', '')
        campaign_details = data.get('campaign_details', {})
        
        if not influencer_id or not campaign_details:
            raise ValidationError("Influencer ID and campaign details are required")
        
        # Predict performance metrics
        performance_prediction = await self.engine.predict_campaign_performance(
            influencer_id, campaign_details
        )
        
        # Calculate ROI projections
        roi_projections = await self._calculate_roi_projections(
            performance_prediction, campaign_details
        )
        
        # Generate performance optimization recommendations
        optimization_recommendations = await self._get_performance_optimization_recommendations(
            performance_prediction, campaign_details
        )
        
        return {
            "influencer_id": influencer_id,
            "performance_prediction": performance_prediction,
            "roi_projections": roi_projections,
            "optimization_recommendations": optimization_recommendations,
            "benchmark_comparison": await self._compare_with_benchmarks(performance_prediction),
            "prediction_timestamp": datetime.utcnow().isoformat()
        }

    async def _calculate_collaboration_budget(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate collaboration budget for influencer"""
        influencer_id = data.get('influencer_id', '')
        campaign_type = data.get('campaign_type', 'brand_awareness')
        deliverables = data.get('deliverables', [])
        
        if not influencer_id:
            raise ValidationError("Influencer ID is required")
        
        # Calculate budget
        budget_calculation = await self.engine.calculate_collaboration_budget(
            influencer_id, campaign_type, deliverables
        )
        
        # Add market comparison
        market_comparison = await self._get_market_budget_comparison(
            influencer_id, budget_calculation['total_budget']
        )
        
        # Generate negotiation strategies
        negotiation_strategies = await self._get_negotiation_strategies(
            budget_calculation, market_comparison
        )
        
        return {
            "influencer_id": influencer_id,
            "budget_calculation": budget_calculation,
            "market_comparison": market_comparison,
            "negotiation_strategies": negotiation_strategies,
            "payment_terms_recommendations": await self._get_payment_terms_recommendations(
                budget_calculation['total_budget']
            ),
            "calculation_timestamp": datetime.utcnow().isoformat()
        }

    async def _analyze_audience_overlap(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audience overlap between influencer and brand target"""
        influencer_id = data.get('influencer_id', '')
        brand_target_audience = data.get('brand_target_audience', {})
        
        if not influencer_id or not brand_target_audience:
            raise ValidationError("Influencer ID and brand target audience are required")
        
        # Analyze overlap
        overlap_analysis = await self.engine.analyze_audience_overlap(
            influencer_id, brand_target_audience
        )
        
        # Generate audience insights
        audience_insights = await self._generate_audience_insights(overlap_analysis)
        
        # Targeting recommendations
        targeting_recommendations = await self._get_targeting_recommendations(
            overlap_analysis, brand_target_audience
        )
        
        return {
            "influencer_id": influencer_id,
            "overlap_analysis": overlap_analysis,
            "audience_insights": audience_insights,
            "targeting_recommendations": targeting_recommendations,
            "campaign_adjustments": await self._suggest_campaign_adjustments(overlap_analysis),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    async def _batch_influencer_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze multiple influencers in batch"""
        influencer_ids = data.get('influencer_ids', [])
        analysis_type = data.get('analysis_type', 'compatibility')
        brand_profile = data.get('brand_profile', {})
        
        if not influencer_ids:
            raise ValidationError("Influencer IDs list is required")
        
        # Process influencers in batches
        batch_size = 10
        results = {}
        
        for i in range(0, len(influencer_ids), batch_size):
            batch = influencer_ids[i:i + batch_size]
            batch_results = await self._process_influencer_batch(
                batch, analysis_type, brand_profile
            )
            results.update(batch_results)
        
        # Generate summary statistics
        summary = await self._generate_batch_summary(results, analysis_type)
        
        return {
            "total_influencers_analyzed": len(influencer_ids),
            "analysis_type": analysis_type,
            "individual_results": results,
            "summary_statistics": summary,
            "top_performers": await self._identify_top_performers(results, analysis_type),
            "recommendations": await self._generate_batch_recommendations(results),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    # Helper methods for result processing and analysis

    def _serialize_match_result(self, match_result) -> Dict[str, Any]:
        """Serialize match result to dictionary"""
        return {
            "influencer_id": match_result.influencer_id,
            "influencer_name": match_result.influencer_name,
            "compatibility_score": match_result.compatibility_score,
            "audience_match_score": match_result.audience_match_score,
            "engagement_rate": match_result.engagement_rate,
            "estimated_reach": match_result.estimated_reach,
            "collaboration_potential": match_result.collaboration_potential,
            "recommended_budget": match_result.recommended_budget,
            "match_reasons": match_result.match_reasons
        }

    def _calculate_budget_range(self, top_matches: List) -> Dict[str, float]:
        """Calculate budget range for top matches"""
        if not top_matches:
            return {"min": 0, "max": 0, "average": 0}
        
        budgets = [match.recommended_budget.get('total_budget', 0) for match in top_matches]
        
        return {
            "min": round(min(budgets), 2),
            "max": round(max(budgets), 2),
            "average": round(sum(budgets) / len(budgets), 2)
        }

    def _get_collaboration_recommendation(self, compatibility_score: float) -> str:
        """Get collaboration recommendation based on compatibility score"""
        if compatibility_score >= 0.9:
            return "Highly Recommended - Excellent fit for collaboration"
        elif compatibility_score >= 0.8:
            return "Recommended - Very good potential for partnership"
        elif compatibility_score >= 0.7:
            return "Consider - Good potential with some optimization"
        else:
            return "Not Recommended - Low compatibility score"

    async def get_system_status(self) -> MatchingSystemStatus:
        """Get comprehensive system status"""
        engine_status = await self.engine.get_status()
        
        return MatchingSystemStatus(
            engine_status=engine_status.get("status", "unknown"),
            active_matching_jobs=engine_status.get("active_jobs", 0),
            total_influencers_in_database=engine_status.get("total_influencer_profiles", 0),
            total_successful_matches=engine_status.get("matching_history_count", 0),
            last_update=datetime.utcnow(),
            performance_metrics=engine_status.get("metrics", {})
        )

    async def shutdown(self) -> None:
        """Graceful shutdown of the influencer matching system"""
        if self.is_running:
            logger.info("Shutting down Influencer Matching System...")
            await self.engine.stop()
            self.is_running = False
            logger.info("Influencer Matching System shutdown completed")
        await super().shutdown()

    def get_required_config_keys(self) -> List[str]:
        """Return required configuration keys"""
        return [
            "influencer_database_config",  # Database configuration for influencer profiles
            "matching_algorithms",         # Matching algorithm parameters
            "brand_safety_apis",          # Brand safety checking APIs
            "performance_prediction_models" # ML models for performance prediction
        ]

    async def _load_models_and_resources(self):
        """Load influencer matching models and resources"""
        # Load ML models for compatibility scoring
        # Initialize influencer database connections
        # Setup brand safety checking systems
        # Load performance prediction models
        pass

    # Additional helper methods (placeholder implementations)
    async def _generate_compatibility_breakdown(self, brand_profile: Dict[str, Any], influencer_profile: Dict[str, Any], campaign_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed compatibility breakdown"""
        return {
            "niche_alignment": 0.85,
            "audience_demographics": 0.75,
            "engagement_quality": 0.90,
            "brand_safety": 0.80,
            "content_style": 0.70,
            "collaboration_history": 0.85
        }

    async def _get_improvement_suggestions(self, compatibility_score: float, breakdown: Dict[str, Any]) -> List[str]:
        """Get improvement suggestions"""
        suggestions = []
        
        for factor, score in breakdown.items():
            if score < 0.7:
                suggestions.append(f"Improve {factor.replace('_', ' ')} alignment")
        
        return suggestions

    async def _generate_risk_mitigation_strategies(self, safety_assessment: Dict[str, Any]) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = []
        
        safety_score = safety_assessment.get('overall_safety_score', 0)
        if safety_score < 0.7:
            strategies.extend([
                "Implement content pre-approval process",
                "Establish clear brand guidelines communication",
                "Set up regular content monitoring",
                "Include brand safety clauses in contract"
            ])
        
        return strategies

    async def _get_content_monitoring_recommendations(self, safety_score: float) -> List[str]:
        """Get content monitoring recommendations"""
        if safety_score >= 0.8:
            return ["Standard monitoring - weekly reviews"]
        elif safety_score >= 0.6:
            return ["Enhanced monitoring - bi-weekly reviews", "Pre-approval for sensitive topics"]
        else:
            return ["Intensive monitoring - all content pre-approval", "Daily content reviews"]

    async def _generate_compliance_checklist(self, brand_guidelines: Dict[str, Any]) -> List[str]:
        """Generate compliance checklist"""
        return [
            "Review and sign brand guidelines agreement",
            "Confirm FTC compliance for sponsored content",
            "Verify content approval process",
            "Establish communication protocols",
            "Set content delivery timeline"
        ]

    async def _calculate_roi_projections(self, performance_prediction: Dict[str, Any], campaign_details: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate ROI projections"""
        predicted_metrics = performance_prediction.get('predicted_metrics', {})
        campaign_budget = campaign_details.get('budget', 5000)
        
        conversions = predicted_metrics.get('conversions', 0)
        avg_order_value = campaign_details.get('average_order_value', 50)
        
        projected_revenue = conversions * avg_order_value
        roi_percentage = ((projected_revenue - campaign_budget) / campaign_budget) * 100 if campaign_budget > 0 else 0
        
        return {
            "projected_revenue": round(projected_revenue, 2),
            "campaign_investment": campaign_budget,
            "projected_roi_percentage": round(roi_percentage, 2),
            "break_even_conversions": int(campaign_budget / avg_order_value) if avg_order_value > 0 else 0,
            "cost_per_conversion": round(campaign_budget / conversions, 2) if conversions > 0 else 0
        }

    async def _get_performance_optimization_recommendations(self, performance_prediction: Dict[str, Any], campaign_details: Dict[str, Any]) -> List[str]:
        """Get performance optimization recommendations"""
        return [
            "Optimize posting time for maximum audience engagement",
            "Use high-performing content formats based on influencer strengths",
            "Include clear call-to-action in all content",
            "Monitor and respond to audience comments actively"
        ]

    async def _compare_with_benchmarks(self, performance_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Compare with industry benchmarks"""
        predicted_metrics = performance_prediction.get('predicted_metrics', {})
        estimated_ctr = predicted_metrics.get('estimated_ctr', 0)
        
        return {
            "industry_average_ctr": 2.5,
            "predicted_ctr": estimated_ctr,
            "performance_vs_benchmark": "above average" if estimated_ctr > 2.5 else "below average",
            "benchmark_source": "Industry standard for influencer marketing"
        }

    async def _get_market_budget_comparison(self, influencer_id: str, calculated_budget: float) -> Dict[str, Any]:
        """Get market budget comparison"""
        return {
            "market_average": calculated_budget * 1.1,
            "market_range": {
                "low": calculated_budget * 0.8,
                "high": calculated_budget * 1.3
            },
            "position": "competitive"
        }

    async def _get_negotiation_strategies(self, budget_calculation: Dict[str, Any], market_comparison: Dict[str, Any]) -> List[str]:
        """Get negotiation strategies"""
        return [
            "Offer performance-based bonuses for exceeding engagement targets",
            "Consider package deals for multiple deliverables",
            "Negotiate usage rights for content repurposing",
            "Explore long-term partnership opportunities for better rates"
        ]

    async def _get_payment_terms_recommendations(self, total_budget: float) -> Dict[str, Any]:
        """Get payment terms recommendations"""
        return {
            "recommended_structure": "50% upfront, 50% on delivery",
            "milestone_payments": total_budget > 10000,
            "preferred_methods": ["bank transfer", "PayPal", "platform escrow"],
            "payment_timeline": "Within 30 days of content delivery"
        }

    async def _generate_audience_insights(self, overlap_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate audience insights"""
        overlap_score = overlap_analysis.get('overall_overlap_score', 0)
        
        if overlap_score >= 0.8:
            return {"primary_insight": "Excellent audience alignment - high conversion potential"}
        elif overlap_score >= 0.6:
            return {"primary_insight": "Good audience match - strong campaign potential"}
        else:
            return {"primary_insight": "Limited audience overlap - consider audience expansion strategies"}

    async def _get_targeting_recommendations(self, overlap_analysis: Dict[str, Any], brand_target: Dict[str, Any]) -> List[str]:
        """Get targeting recommendations"""
        return [
            "Focus on shared demographic segments for maximum impact",
            "Consider geographic targeting for better relevance",
            "Optimize content for primary audience interests"
        ]

    async def _suggest_campaign_adjustments(self, overlap_analysis: Dict[str, Any]) -> List[str]:
        """Suggest campaign adjustments based on audience overlap"""
        return [
            "Adjust messaging to appeal to influencer's core audience",
            "Consider timing adjustments for optimal audience reach",
            "Tailor content format to influencer's successful post types"
        ]

    async def _process_influencer_batch(self, influencer_ids: List[str], analysis_type: str, brand_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Process a batch of influencers"""
        results = {}
        
        for influencer_id in influencer_ids:
            if analysis_type == "compatibility":
                # Mock compatibility analysis
                results[influencer_id] = {"compatibility_score": 0.75, "status": "analyzed"}
            elif analysis_type == "safety":
                # Mock safety analysis
                results[influencer_id] = {"safety_score": 0.85, "status": "analyzed"}
        
        return results

    async def _generate_batch_summary(self, results: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Generate summary statistics for batch analysis"""
        if analysis_type == "compatibility":
            scores = [r.get("compatibility_score", 0) for r in results.values()]
            return {
                "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
                "high_compatibility_count": len([s for s in scores if s >= 0.8]),
                "total_analyzed": len(results)
            }
        
        return {"total_analyzed": len(results)}

    async def _identify_top_performers(self, results: Dict[str, Any], analysis_type: str) -> List[Dict[str, Any]]:
        """Identify top performing influencers from batch analysis"""
        if analysis_type == "compatibility":
            sorted_results = sorted(
                results.items(),
                key=lambda x: x[1].get("compatibility_score", 0),
                reverse=True
            )
            return [{"influencer_id": k, **v} for k, v in sorted_results[:5]]
        
        return []

    async def _generate_batch_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on batch analysis"""
        return [
            f"Focus on top {min(5, len(results))} influencers for immediate outreach",
            "Consider secondary tier influencers for broader reach",
            "Implement standardized onboarding process for selected influencers"
        ]