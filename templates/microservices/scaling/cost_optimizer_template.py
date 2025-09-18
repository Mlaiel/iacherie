#!/usr/bin/env python3
"""Cost Optimizer Template - Infrastructure cost optimization"""

from typing import Dict, List

class CostOptimizerTemplate:
    """Cost optimization template"""
    
    def __init__(self):
        self.service_costs: Dict[str, float] = {}
        self.optimization_recommendations: List[str] = []
    
    def track_service_cost(self, service_name: str, monthly_cost: float):
        """Track monthly cost for service"""
        self.service_costs[service_name] = monthly_cost
    
    def analyze_costs(self) -> Dict:
        """Analyze costs and provide recommendations"""
        total_cost = sum(self.service_costs.values())
        
        # Find highest cost services
        sorted_services = sorted(
            self.service_costs.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        recommendations = []
        
        # Generate recommendations for top cost services
        for service, cost in sorted_services[:3]:
            if cost > total_cost * 0.3:  # Service costs >30% of total
                recommendations.append(f"Review {service} - high cost service (${cost:.2f}/month)")
        
        return {
            "total_monthly_cost": total_cost,
            "highest_cost_services": sorted_services[:5],
            "recommendations": recommendations
        }