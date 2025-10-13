"""
🎯 Content Optimization Service
Advanced SEO and content optimization system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import asyncio
import logging
import re

logger = logging.getLogger(__name__)


class ContentOptimizationService:
    """Advanced content optimization service for SEO and performance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.optimization_rules: Dict[str, Any] = {}
        self.content_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize optimization rules
        self._initialize_optimization_rules()
        
        self.logger.info("✅ ContentOptimizationService initialized")
    
    def _initialize_optimization_rules(self):
        """Initialize SEO and content optimization rules"""
        self.optimization_rules = {
            "title_length": {"min": 30, "max": 60, "weight": 0.9},
            "meta_description_length": {"min": 120, "max": 160, "weight": 0.8},
            "keyword_density": {"min": 0.5, "max": 3.0, "weight": 0.7},
            "heading_structure": {"required": True, "weight": 0.8},
            "image_alt_text": {"required": True, "weight": 0.6},
            "internal_links": {"min": 2, "weight": 0.5},
            "readability_score": {"min": 60, "weight": 0.7}
        }
    
    async def optimize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for SEO and performance"""
        try:
            title = content.get("title", "")
            body = content.get("body", "")
            meta_description = content.get("meta_description", "")
            
            optimization_results = {
                "original_content": content,
                "optimizations": [],
                "seo_score": 0,
                "recommendations": [],
                "optimized_content": content.copy()
            }
            
            # Title optimization
            title_opt = await self._optimize_title(title)
            if title_opt["needs_optimization"]:
                optimization_results["optimizations"].append(title_opt)
                optimization_results["optimized_content"]["title"] = title_opt["optimized_title"]
            
            # Meta description optimization
            meta_opt = await self._optimize_meta_description(meta_description, body)
            if meta_opt["needs_optimization"]:
                optimization_results["optimizations"].append(meta_opt)
                optimization_results["optimized_content"]["meta_description"] = meta_opt["optimized_description"]
            
            # Content structure optimization
            structure_opt = await self._optimize_content_structure(body)
            optimization_results["optimizations"].append(structure_opt)
            optimization_results["optimized_content"]["body"] = structure_opt["optimized_body"]
            
            # Calculate SEO score
            seo_score = await self._calculate_seo_score(optimization_results["optimized_content"])
            optimization_results["seo_score"] = seo_score
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(optimization_results["optimized_content"], seo_score)
            optimization_results["recommendations"] = recommendations
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {str(e)}")
            return {
                "error": "Optimization failed",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _optimize_title(self, title: str) -> Dict[str, Any]:
        """Optimize title for SEO"""
        title_length = len(title)
        needs_optimization = False
        optimized_title = title
        
        issues = []
        
        if title_length < self.optimization_rules["title_length"]["min"]:
            issues.append(f"Title too short ({title_length} chars, min: {self.optimization_rules['title_length']['min']})")
            needs_optimization = True
            # Extend title with relevant keywords
            optimized_title = f"{title} - Complete Guide & Tips"
            
        elif title_length > self.optimization_rules["title_length"]["max"]:
            issues.append(f"Title too long ({title_length} chars, max: {self.optimization_rules['title_length']['max']})")
            needs_optimization = True
            # Trim title while keeping key information
            optimized_title = title[:self.optimization_rules["title_length"]["max"]-3] + "..."
        
        return {
            "type": "title_optimization",
            "needs_optimization": needs_optimization,
            "original_title": title,
            "optimized_title": optimized_title,
            "issues": issues,
            "score_impact": 0.2 if needs_optimization else 0
        }
    
    async def _optimize_meta_description(self, meta_description: str, content: str) -> Dict[str, Any]:
        """Optimize meta description"""
        desc_length = len(meta_description)
        needs_optimization = False
        optimized_description = meta_description
        
        issues = []
        
        if not meta_description:
            # Generate meta description from content
            sentences = content.split('.')[:2]
            optimized_description = '. '.join(sentences).strip()[:160]
            needs_optimization = True
            issues.append("Missing meta description - generated from content")
            
        elif desc_length < self.optimization_rules["meta_description_length"]["min"]:
            issues.append(f"Meta description too short ({desc_length} chars)")
            needs_optimization = True
            optimized_description = f"{meta_description} Learn more about this topic and discover key insights."
            
        elif desc_length > self.optimization_rules["meta_description_length"]["max"]:
            issues.append(f"Meta description too long ({desc_length} chars)")
            needs_optimization = True
            optimized_description = meta_description[:157] + "..."
        
        return {
            "type": "meta_description_optimization",
            "needs_optimization": needs_optimization,
            "original_description": meta_description,
            "optimized_description": optimized_description,
            "issues": issues,
            "score_impact": 0.15 if needs_optimization else 0
        }
    
    async def _optimize_content_structure(self, content: str) -> Dict[str, Any]:
        """Optimize content structure with headings and formatting"""
        optimized_content = content
        optimizations = []
        
        # Add headings if missing
        if not re.search(r'<h[1-6]|#{1,6}', content):
            # Add basic heading structure
            paragraphs = content.split('\n\n')
            if len(paragraphs) > 1:
                optimized_content = f"## Introduction\n\n{paragraphs[0]}\n\n## Details\n\n" + '\n\n'.join(paragraphs[1:])
                optimizations.append("Added basic heading structure")
        
        # Improve readability with bullet points
        if len(content.split('.')) > 5:
            # Convert some sentences to bullet points for better readability
            optimizations.append("Suggested bullet point formatting for better readability")
        
        return {
            "type": "content_structure_optimization",
            "optimized_body": optimized_content,
            "optimizations_applied": optimizations,
            "score_impact": len(optimizations) * 0.1
        }
    
    async def _calculate_seo_score(self, content: Dict[str, Any]) -> float:
        """Calculate overall SEO score"""
        score = 0.0
        max_score = 0.0
        
        for rule_name, rule_config in self.optimization_rules.items():
            weight = rule_config["weight"]
            max_score += weight
            
            if rule_name == "title_length":
                title_len = len(content.get("title", ""))
                if rule_config["min"] <= title_len <= rule_config["max"]:
                    score += weight
                    
            elif rule_name == "meta_description_length":
                meta_len = len(content.get("meta_description", ""))
                if rule_config["min"] <= meta_len <= rule_config["max"]:
                    score += weight
                    
            elif rule_name == "heading_structure":
                body = content.get("body", "")
                if re.search(r'<h[1-6]|#{1,6}', body):
                    score += weight
        
        return round((score / max_score) * 100, 1) if max_score > 0 else 0.0
    
    async def _generate_recommendations(self, content: Dict[str, Any], seo_score: float) -> List[str]:
        """Generate SEO recommendations"""
        recommendations = []
        
        if seo_score < 70:
            recommendations.append("Improve overall SEO score by addressing content optimization issues")
        
        title = content.get("title", "")
        if len(title) < 30:
            recommendations.append("Extend title with relevant keywords for better SEO")
        elif len(title) > 60:
            recommendations.append("Shorten title to improve click-through rates")
        
        meta_desc = content.get("meta_description", "")
        if not meta_desc:
            recommendations.append("Add compelling meta description to improve search snippets")
        
        body = content.get("body", "")
        if not re.search(r'<h[1-6]|#{1,6}', body):
            recommendations.append("Add heading structure (H1, H2, H3) for better content organization")
        
        if len(body.split()) < 300:
            recommendations.append("Expand content to at least 300 words for better SEO performance")
        
        return recommendations
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "ContentOptimizationService",
            "status": "healthy",
            "optimization_rules": len(self.optimization_rules),
            "cached_results": len(self.content_cache),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


__all__ = ['ContentOptimizationService']