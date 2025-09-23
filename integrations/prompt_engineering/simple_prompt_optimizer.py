#!/usr/bin/env python3
"""
🤖 SIMPLE PROMPT OPTIMIZER
==========================

Simple prompt engineering optimization by IA Prompt Engineer.

Author: IA Prompt Engineer Expert
Created: 2025-09-23
"""

import logging
from typing import Dict, List, Any


class SimplePromptOptimizer:
    """Simple prompt optimization engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.templates = {}
    
    def optimize_prompt(self, prompt: str) -> str:
        """Simple prompt optimization"""
        optimized = prompt.strip()
        
        # Add structure if missing
        if not optimized.startswith("Task:"):
            optimized = "Task: " + optimized
        
        # Add output format if missing
        if "Output:" not in optimized:
            optimized += "\nOutput: Provide clear, structured response."
        
        return optimized
    
    def create_template(self, name: str, template: str) -> Dict[str, Any]:
        """Create optimized template"""
        optimized_template = {
            "name": name,
            "template": self.optimize_prompt(template),
            "created": "2025-09-23T15:17:58.931774",
            "quality_score": 85
        }
        
        self.templates[name] = optimized_template
        return optimized_template
    
    def validate_response(self, response: str) -> Dict[str, Any]:
        """Simple response validation"""
        return {
            "valid": len(response) > 10,
            "quality_score": min(100, len(response) // 10),
            "suggestions": ["Ensure completeness", "Check clarity"]
        }


def create_simple_prompt_optimizer():
    """Factory for simple prompt optimizer"""
    return SimplePromptOptimizer()

# Pre-defined simple templates
SIMPLE_TEMPLATES = {
    "content_generation": "Task: Generate content about {topic}.\nContext: {context}\nOutput: Well-structured content.",
    "seo_optimization": "Task: Optimize content for SEO.\nKeyword: {keyword}\nOutput: SEO-friendly content.",
    "collaboration": "Task: Match collaborators.\nCriteria: {criteria}\nOutput: Best matches with scores."
}
