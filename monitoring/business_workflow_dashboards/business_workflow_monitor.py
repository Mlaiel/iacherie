"""
Business Workflow Monitor for Ainflue Platform
Comprehensive monitoring across the entire business workflow

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStageMetrics:
    """Metrics for a specific workflow stage"""
    stage_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_processing_time: float
    error_rate: float
    throughput: float
    active_users: int
    bottlenecks: List[str]
    timestamp: datetime


class BusinessWorkflowMonitor:
    """
    Comprehensive business workflow monitoring system
    Tracks the complete user journey: Upload → AI Processing → Protection → SEO → Collaboration → Distribution
    """
    
    def __init__(self) -> None:
        """Initialize business workflow monitor"""
        self.workflow_stages = [
            "content_upload",
            "ai_processing", 
            "content_protection",
            "seo_optimization",
            "collaboration_matching",
            "multi_platform_distribution",
            "monetization"
        ]
        
        self.stage_metrics = {}
        self.workflow_transitions = defaultdict(list)
        self.user_journeys = defaultdict(list)
        self.business_kpis = {}
        
        # Initialize metrics collection
        self._initialize_metrics_collection()
    
    def track_workflow_stage(self, user_id: str, stage_name: str, 
                           request_data: Dict[str, Any],
                           processing_time: float,
                           success: bool,
                           error_details: Optional[str] = None) -> None:
        """
        Track user progress through workflow stage
        
        Args:
            user_id: Unique user identifier
            stage_name: Workflow stage name
            request_data: Request data for context
            processing_time: Time taken to process request
            success: Whether request was successful
            error_details: Error details if failed
        """
        try:
            timestamp = datetime.utcnow()
            
            # Record user journey
            journey_event = {
                "timestamp": timestamp,
                "stage": stage_name,
                "success": success,
                "processing_time": processing_time,
                "request_data": request_data,
                "error_details": error_details
            }
            self.user_journeys[user_id].append(journey_event)
            
            # Update stage metrics
            self._update_stage_metrics(stage_name, processing_time, success)
            
            # Track workflow transitions
            self._track_workflow_transition(user_id, stage_name, timestamp)
            
            # Update business KPIs
            self._update_business_kpis(stage_name, request_data, success)
            
            logger.debug(
                f"Tracked workflow stage: {stage_name} for user {user_id} "
                f"(success: {success}, time: {processing_time:.2f}s)"
            )
            
        except Exception as e:
            logger.error(f"Error tracking workflow stage: {e}")
    
    def get_workflow_overview(self, time_period: str = "24h") -> Dict[str, Any]:
        """
        Get comprehensive workflow overview
        
        Args:
            time_period: Time period for analysis
            
        Returns:
            Workflow overview with metrics and insights
        """
        try:
            hours = self._parse_time_period(time_period)
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            overview = {
                "time_period": time_period,
                "generated_at": datetime.utcnow().isoformat(),
                "stage_metrics": {},
                "workflow_health": {},
                "user_journey_analysis": {},
                "business_impact": {},
                "bottlenecks": [],
                "recommendations": []
            }
            
            # Get stage-by-stage metrics
            for stage in self.workflow_stages:
                stage_metrics = self._get_stage_metrics(stage, cutoff_time)
                overview["stage_metrics"][stage] = stage_metrics
            
            # Analyze workflow health
            overview["workflow_health"] = self._analyze_workflow_health(cutoff_time)
            
            # Analyze user journeys
            overview["user_journey_analysis"] = self._analyze_user_journeys(cutoff_time)
            
            # Calculate business impact
            overview["business_impact"] = self._calculate_business_impact(cutoff_time)
            
            # Identify bottlenecks
            overview["bottlenecks"] = self._identify_bottlenecks(cutoff_time)
            
            # Generate recommendations
            overview["recommendations"] = self._generate_workflow_recommendations(overview)
            
            return overview
            
        except Exception as e:
            logger.error(f"Error getting workflow overview: {e}")
            return {"error": str(e)}
    
    def _update_stage_metrics(self, stage_name -> None: str, processing_time -> None: float, success -> None: bool) -> None:
        """Update metrics for workflow stage"""
        if stage_name not in self.stage_metrics:
            self.stage_metrics[stage_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_processing_time": 0.0,
                "active_users": set(),
                "errors": []
            }
        
        metrics = self.stage_metrics[stage_name]
        metrics["total_requests"] += 1
        metrics["total_processing_time"] += processing_time
        
        if success:
            metrics["successful_requests"] += 1
        else:
            metrics["failed_requests"] += 1
    
    def _track_workflow_transition(self, user_id -> None: str, current_stage -> None: str, timestamp -> None: datetime) -> None:
        """Track transitions between workflow stages"""
        user_journey = self.user_journeys.get(user_id, [])
        
        if len(user_journey) >= 2:
            previous_event = user_journey[-2]
            previous_stage = previous_event["stage"]
            
            if previous_stage != current_stage:
                transition_time = (timestamp - previous_event["timestamp"]).total_seconds()
                
                transition_key = f"{previous_stage}->{current_stage}"
                self.workflow_transitions[transition_key].append({
                    "timestamp": timestamp,
                    "user_id": user_id,
                    "transition_time": transition_time
                })
    
    def _update_business_kpis(self, stage_name -> None: str, request_data -> None: Dict[str, Any], success -> None: bool) -> None:
        """Update business KPIs based on workflow activity"""
        if "business_kpis" not in self.__dict__:
            self.business_kpis = defaultdict(lambda: defaultdict(int))
        
        # Update stage-specific KPIs
        self.business_kpis[stage_name]["total_activity"] += 1
        if success:
            self.business_kpis[stage_name]["successful_activity"] += 1
        
        # Update content-type specific metrics
        if "content_type" in request_data:
            content_type = request_data["content_type"]
            self.business_kpis["content_types"][content_type] += 1
        
        # Update user engagement metrics
        if "user_type" in request_data:
            user_type = request_data["user_type"]
            self.business_kpis["user_types"][user_type] += 1
    
    def _get_stage_metrics(self, stage_name: str, cutoff_time: datetime) -> Dict[str, Any]:
        """Get metrics for specific workflow stage"""
        if stage_name not in self.stage_metrics:
            return {
                "total_requests": 0,
                "success_rate": 0.0,
                "average_processing_time": 0.0,
                "throughput": 0.0,
                "error_rate": 0.0
            }
        
        metrics = self.stage_metrics[stage_name]
        
        total_requests = metrics["total_requests"]
        successful_requests = metrics["successful_requests"]
        failed_requests = metrics["failed_requests"]
        total_processing_time = metrics["total_processing_time"]
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0.0,
            "error_rate": failed_requests / total_requests if total_requests > 0 else 0.0,
            "average_processing_time": total_processing_time / total_requests if total_requests > 0 else 0.0,
            "throughput": total_requests / 24.0,  # requests per hour (assuming 24h period)
            "active_users": len(metrics["active_users"])
        }
    
    def _analyze_workflow_health(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Analyze overall workflow health"""
        health_metrics = {
            "overall_health_score": 0.0,
            "stage_health": {},
            "critical_issues": [],
            "performance_status": "unknown"
        }
        
        total_health_score = 0.0
        stage_count = 0
        
        for stage in self.workflow_stages:
            stage_metrics = self._get_stage_metrics(stage, cutoff_time)
            
            # Calculate health score for stage (0-100)
            success_rate = stage_metrics["success_rate"]
            avg_processing_time = stage_metrics["average_processing_time"]
            
            # Health factors
            success_score = success_rate * 40  # 40 points for success rate
            performance_score = max(0, 30 - avg_processing_time)  # 30 points for performance
            throughput_score = min(30, stage_metrics["throughput"])  # 30 points for throughput
            
            stage_health_score = success_score + performance_score + throughput_score
            
            health_metrics["stage_health"][stage] = {
                "health_score": stage_health_score,
                "success_rate": success_rate,
                "performance_rating": "good" if avg_processing_time < 5.0 else "poor",
                "throughput_rating": "good" if stage_metrics["throughput"] > 10 else "low"
            }
            
            total_health_score += stage_health_score
            stage_count += 1
            
            # Identify critical issues
            if success_rate < 0.9:
                health_metrics["critical_issues"].append(
                    f"Low success rate in {stage}: {success_rate:.1%}"
                )
            
            if avg_processing_time > 10.0:
                health_metrics["critical_issues"].append(
                    f"High processing time in {stage}: {avg_processing_time:.1f}s"
                )
        
        # Calculate overall health score
        if stage_count > 0:
            health_metrics["overall_health_score"] = total_health_score / stage_count
        
        # Determine performance status
        if health_metrics["overall_health_score"] >= 80:
            health_metrics["performance_status"] = "excellent"
        elif health_metrics["overall_health_score"] >= 60:
            health_metrics["performance_status"] = "good"
        elif health_metrics["overall_health_score"] >= 40:
            health_metrics["performance_status"] = "fair"
        else:
            health_metrics["performance_status"] = "poor"
        
        return health_metrics
    
    def _analyze_user_journeys(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Analyze user journeys through the workflow"""
        
        journey_analysis = {
            "total_users": 0,
            "complete_journeys": 0,
            "incomplete_journeys": 0,
            "average_journey_time": 0.0,
            "completion_rate": 0.0,
            "common_drop_off_points": []
        }
        
        complete_journeys = []
        incomplete_journeys = []
        drop_off_counts = defaultdict(int)
        
        for user_id, journey in self.user_journeys.items():
            # Filter events by time
            filtered_journey = [
                event for event in journey 
                if event["timestamp"] > cutoff_time
            ]
            
            if not filtered_journey:
                continue
            
            journey_analysis["total_users"] += 1
            
            # Check if journey is complete (reached final stage)
            stages_visited = [event["stage"] for event in filtered_journey]
            
            if "monetization" in stages_visited:
                complete_journeys.append(filtered_journey)
                journey_analysis["complete_journeys"] += 1
            else:
                incomplete_journeys.append(filtered_journey)
                journey_analysis["incomplete_journeys"] += 1
                
                # Track drop-off point
                if stages_visited:
                    last_stage = stages_visited[-1]
                    drop_off_counts[last_stage] += 1
        
        # Calculate completion rate
        total_journeys = journey_analysis["complete_journeys"] + journey_analysis["incomplete_journeys"]
        if total_journeys > 0:
            journey_analysis["completion_rate"] = journey_analysis["complete_journeys"] / total_journeys
        
        # Calculate average journey time for complete journeys
        if complete_journeys:
            journey_times = []
            for journey in complete_journeys:
                start_time = journey[0]["timestamp"]
                end_time = journey[-1]["timestamp"]
                journey_time = (end_time - start_time).total_seconds()
                journey_times.append(journey_time)
            
            journey_analysis["average_journey_time"] = sum(journey_times) / len(journey_times)
        
        # Identify common drop-off points
        journey_analysis["common_drop_off_points"] = [
            {"stage": stage, "count": count} 
            for stage, count in sorted(drop_off_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return journey_analysis
    
    def _calculate_business_impact(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Calculate business impact metrics"""
        
        business_impact = {
            "revenue_impact": {},
            "user_engagement": {},
            "content_metrics": {}
        }
        
        # Calculate revenue impact
        total_monetization_events = self.business_kpis.get("monetization", {}).get("successful_activity", 0)
        estimated_revenue_per_event = 5.0  # Example value
        business_impact["revenue_impact"] = {
            "estimated_revenue": total_monetization_events * estimated_revenue_per_event,
            "monetization_events": total_monetization_events,
            "revenue_per_user": estimated_revenue_per_event
        }
        
        # Calculate user engagement
        total_users = len([
            user_id for user_id, journey in self.user_journeys.items()
            if any(event["timestamp"] > cutoff_time for event in journey)
        ])
        
        business_impact["user_engagement"] = {
            "active_users": total_users,
            "engagement_rate": min(1.0, total_users / 1000),
            "returning_users": total_users // 2
        }
        
        # Calculate content metrics
        content_types = self.business_kpis.get("content_types", {})
        business_impact["content_metrics"] = {
            "total_content_uploads": sum(content_types.values()),
            "content_type_distribution": dict(content_types),
            "most_popular_content": max(content_types.items(), key=lambda x: x[1])[0] if content_types else "unknown"
        }
        
        return business_impact
    
    def _identify_bottlenecks(self, cutoff_time: datetime) -> List[Dict[str, Any]]:
        """Identify bottlenecks in the workflow"""
        
        bottlenecks = []
        
        for stage in self.workflow_stages:
            stage_metrics = self._get_stage_metrics(stage, cutoff_time)
            
            # Check for performance bottlenecks
            if stage_metrics["average_processing_time"] > 10.0:
                bottlenecks.append({
                    "type": "performance",
                    "stage": stage,
                    "severity": "high",
                    "description": f"High processing time: {stage_metrics['average_processing_time']:.1f}s",
                    "metric_value": stage_metrics["average_processing_time"],
                    "recommendation": f"Optimize {stage} processing pipeline"
                })
            
            # Check for error rate bottlenecks
            if stage_metrics["error_rate"] > 0.1:
                bottlenecks.append({
                    "type": "reliability",
                    "stage": stage,
                    "severity": "critical",
                    "description": f"High error rate: {stage_metrics['error_rate']:.1%}",
                    "metric_value": stage_metrics["error_rate"],
                    "recommendation": f"Debug and fix errors in {stage}"
                })
        
        return sorted(bottlenecks, key=lambda x: {"critical": 3, "high": 2, "medium": 1}.get(x["severity"], 0), reverse=True)
    
    def _generate_workflow_recommendations(self, overview: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on workflow analysis"""
        
        recommendations = []
        
        # Recommendations based on overall health
        health_score = overview["workflow_health"]["overall_health_score"]
        if health_score < 50:
            recommendations.append("Critical: Overall workflow health is poor. Immediate investigation required.")
        elif health_score < 70:
            recommendations.append("Warning: Workflow performance is below optimal. Consider optimization.")
        
        # Recommendations based on bottlenecks
        bottlenecks = overview["bottlenecks"]
        critical_bottlenecks = [b for b in bottlenecks if b["severity"] == "critical"]
        if critical_bottlenecks:
            recommendations.append(f"Urgent: Address {len(critical_bottlenecks)} critical bottlenecks in workflow.")
        
        # Recommendations based on user journey completion
        completion_rate = overview["user_journey_analysis"]["completion_rate"]
        if completion_rate < 0.5:
            recommendations.append("Low user journey completion rate. Analyze drop-off points and optimize user experience.")
        
        return recommendations
    
    def _parse_time_period(self, time_period: str) -> int:
        """Parse time period string to hours"""
        if time_period.endswith('h'):
            return int(time_period[:-1])
        elif time_period.endswith('d'):
            return int(time_period[:-1]) * 24
        elif time_period.endswith('w'):
            return int(time_period[:-1]) * 24 * 7
        else:
            return 24  # Default to 24 hours
    
    def _initialize_metrics_collection(self) -> None:
        """Initialize metrics collection for all workflow stages"""
        for stage in self.workflow_stages:
            self.stage_metrics[stage] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_processing_time": 0.0,
                "active_users": set(),
                "errors": []
            }


# Global business workflow monitor instance
business_workflow_monitor = BusinessWorkflowMonitor()