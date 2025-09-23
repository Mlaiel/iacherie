#!/usr/bin/env python3
"""
🤖 ADVANCED PROMPT OPTIMIZER
============================

Intelligent prompt engineering with optimization and quality scoring.

Author: IA Prompt Engineer Expert
"""

import re
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class PromptTemplate:
    """Prompt template definition"""
    template_id: str
    name: str
    category: str  # content_generation, analysis, optimization, moderation
    template: str
    variables: List[str]
    expected_output_format: str
    quality_score: float = 0.0
    usage_count: int = 0
    success_rate: float = 0.0

@dataclass
class PromptOptimization:
    """Prompt optimization result"""
    original_prompt: str
    optimized_prompt: str
    improvements: List[str]
    quality_score_before: float
    quality_score_after: float
    optimization_techniques: List[str]

class AdvancedPromptOptimizer:
    """Advanced prompt engineering optimization system"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.templates: Dict[str, PromptTemplate] = {}
        self.optimization_rules = self._load_optimization_rules()
        self.quality_metrics = {
            "clarity": 0.0,
            "specificity": 0.0,
            "structure": 0.0,
            "completeness": 0.0
        }
    
    def optimize_prompt(self, prompt: str, category: str = "general") -> PromptOptimization:
        """Optimize a prompt using advanced techniques"""
        
        original_score = self._calculate_quality_score(prompt)
        optimized_prompt = prompt
        improvements = []
        techniques_used = []
        
        # Apply optimization techniques
        optimized_prompt, technique_improvements = self._apply_structure_optimization(optimized_prompt)
        if technique_improvements:
            improvements.extend(technique_improvements)
            techniques_used.append("structure_optimization")
        
        optimized_prompt, clarity_improvements = self._apply_clarity_optimization(optimized_prompt)
        if clarity_improvements:
            improvements.extend(clarity_improvements)
            techniques_used.append("clarity_optimization")
        
        optimized_prompt, specificity_improvements = self._apply_specificity_optimization(optimized_prompt, category)
        if specificity_improvements:
            improvements.extend(specificity_improvements)
            techniques_used.append("specificity_optimization")
        
        optimized_prompt, format_improvements = self._apply_format_optimization(optimized_prompt)
        if format_improvements:
            improvements.extend(format_improvements)
            techniques_used.append("format_optimization")
        
        final_score = self._calculate_quality_score(optimized_prompt)
        
        return PromptOptimization(
            original_prompt=prompt,
            optimized_prompt=optimized_prompt,
            improvements=improvements,
            quality_score_before=original_score,
            quality_score_after=final_score,
            optimization_techniques=techniques_used
        )
    
    def _apply_structure_optimization(self, prompt: str) -> Tuple[str, List[str]]:
        """Apply structural improvements to prompt"""
        improvements = []
        optimized = prompt
        
        # Add clear task definition if missing
        if not prompt.strip().startswith(("Task:", "Objective:", "Goal:")):
            optimized = f"Task: {optimized}"
            improvements.append("Added clear task definition")
        
        # Add context section if needed
        if "context" not in prompt.lower() and len(prompt.split()) > 20:
            parts = optimized.split("\n\n")
            if len(parts) == 1:
                optimized = f"Context: Provide relevant background information.\n\n{optimized}"
                improvements.append("Added context section")
        
        # Add output format specification
        if "output:" not in prompt.lower() and "format:" not in prompt.lower():
            optimized += "\n\nOutput: Provide a clear, structured response following the requirements above."
            improvements.append("Added output format specification")
        
        return optimized, improvements
    
    def _apply_clarity_optimization(self, prompt: str) -> Tuple[str, List[str]]:
        """Improve prompt clarity"""
        improvements = []
        optimized = prompt
        
        # Replace vague terms with specific ones
        vague_replacements = {
            "good": "high-quality",
            "bad": "poor-quality", 
            "nice": "well-formatted",
            "thing": "element",
            "stuff": "content",
            "some": "specific"
        }
        
        for vague, specific in vague_replacements.items():
            if vague in optimized.lower():
                optimized = re.sub(rf"\b{vague}\b", specific, optimized, flags=re.IGNORECASE)
                improvements.append(f"Replaced vague term '{vague}' with '{specific}'")
        
        # Remove redundant phrases
        redundant_phrases = [
            "please", "if possible", "try to", "maybe", "perhaps"
        ]
        
        for phrase in redundant_phrases:
            if phrase in optimized.lower():
                optimized = re.sub(rf"\b{phrase}\b", "", optimized, flags=re.IGNORECASE)
                optimized = re.sub(r"\s+", " ", optimized)  # Clean up extra spaces
                improvements.append(f"Removed redundant phrase '{phrase}'")
        
        return optimized, improvements
    
    def _apply_specificity_optimization(self, prompt: str, category: str) -> Tuple[str, List[str]]:
        """Add category-specific optimizations"""
        improvements = []
        optimized = prompt
        
        # Category-specific enhancements
        if category == "content_generation":
            if "tone:" not in prompt.lower():
                optimized += "\n\nTone: Professional and engaging."
                improvements.append("Added tone specification")
            
            if "length:" not in prompt.lower():
                optimized += "\nLength: Approximately 200-300 words."
                improvements.append("Added length specification")
        
        elif category == "analysis":
            if "criteria:" not in prompt.lower():
                optimized += "\n\nAnalysis Criteria: Evaluate based on accuracy, completeness, and relevance."
                improvements.append("Added analysis criteria")
        
        elif category == "optimization":
            if "metrics:" not in prompt.lower():
                optimized += "\n\nSuccess Metrics: Define clear, measurable improvements."
                improvements.append("Added success metrics")
        
        return optimized, improvements
    
    def _apply_format_optimization(self, prompt: str) -> Tuple[str, List[str]]:
        """Optimize prompt formatting"""
        improvements = []
        optimized = prompt
        
        # Ensure proper line breaks for readability
        if "\n" not in prompt and len(prompt) > 100:
            # Add line breaks at logical points
            sentences = optimized.split(". ")
            if len(sentences) > 2:
                mid_point = len(sentences) // 2
                optimized = ". ".join(sentences[:mid_point]) + ".\n\n" + ". ".join(sentences[mid_point:])
                improvements.append("Added line breaks for better readability")
        
        # Add numbered steps if multiple requirements
        if "and" in prompt and ":" not in prompt:
            # Convert complex requirements to numbered list
            parts = optimized.split(" and ")
            if len(parts) > 2:
                numbered_parts = [f"{i+1}. {part.strip()}" for i, part in enumerate(parts)]
                optimized = "\n".join(numbered_parts)
                improvements.append("Converted requirements to numbered list")
        
        return optimized, improvements
    
    def _calculate_quality_score(self, prompt: str) -> float:
        """Calculate prompt quality score (0-100)"""
        scores = {
            "clarity": self._score_clarity(prompt),
            "specificity": self._score_specificity(prompt),
            "structure": self._score_structure(prompt),
            "completeness": self._score_completeness(prompt)
        }
        
        # Weighted average
        weights = {"clarity": 0.3, "specificity": 0.3, "structure": 0.2, "completeness": 0.2}
        total_score = sum(scores[metric] * weights[metric] for metric in scores)
        
        return min(100, max(0, total_score * 100))
    
    def _score_clarity(self, prompt: str) -> float:
        """Score prompt clarity (0-1)"""
        clarity_score = 0.5  # Base score
        
        # Positive indicators
        if any(word in prompt.lower() for word in ["specific", "clear", "detailed"]):
            clarity_score += 0.2
        
        # Negative indicators  
        vague_words = ["thing", "stuff", "good", "bad", "nice"]
        vague_count = sum(1 for word in vague_words if word in prompt.lower())
        clarity_score -= vague_count * 0.1
        
        return max(0, min(1, clarity_score))
    
    def _score_specificity(self, prompt: str) -> float:
        """Score prompt specificity (0-1)"""
        specificity_score = 0.5
        
        # Check for specific requirements
        specific_indicators = ["format:", "length:", "tone:", "style:", "criteria:"]
        specificity_score += sum(0.1 for indicator in specific_indicators if indicator in prompt.lower())
        
        return max(0, min(1, specificity_score))
    
    def _score_structure(self, prompt: str) -> float:
        """Score prompt structure (0-1)"""
        structure_score = 0.3
        
        # Check for clear sections
        if any(start in prompt.lower() for start in ["task:", "objective:", "goal:"]):
            structure_score += 0.3
        
        if "output:" in prompt.lower() or "format:" in prompt.lower():
            structure_score += 0.2
        
        if "\n" in prompt:  # Has line breaks
            structure_score += 0.2
        
        return max(0, min(1, structure_score))
    
    def _score_completeness(self, prompt: str) -> float:
        """Score prompt completeness (0-1)"""
        completeness_score = 0.4
        
        # Check length (too short or too long is bad)
        word_count = len(prompt.split())
        if 10 <= word_count <= 100:
            completeness_score += 0.3
        elif word_count > 5:
            completeness_score += 0.1
        
        # Check for examples
        if "example:" in prompt.lower() or "for example" in prompt.lower():
            completeness_score += 0.2
        
        # Check for constraints
        if any(word in prompt.lower() for word in ["don't", "avoid", "not", "except"]):
            completeness_score += 0.1
        
        return max(0, min(1, completeness_score))
    
    def _load_optimization_rules(self) -> Dict[str, List[str]]:
        """Load prompt optimization rules"""
        return {
            "structure": [
                "Start with clear task definition",
                "Include context when needed", 
                "Specify desired output format",
                "Use logical organization"
            ],
            "clarity": [
                "Use specific, concrete language",
                "Avoid vague terms and phrases",
                "Be direct and concise",
                "Define technical terms"
            ],
            "specificity": [
                "Include relevant constraints",
                "Specify quality criteria",
                "Provide examples when helpful",
                "Define success metrics"
            ]
        }
    
    def create_template(self, name: str, category: str, template: str) -> PromptTemplate:
        """Create optimized prompt template"""
        
        # Optimize the template
        optimization = self.optimize_prompt(template, category)
        
        # Extract variables from template
        variables = re.findall(r'{([^}]+)}', optimization.optimized_prompt)
        
        template_obj = PromptTemplate(
            template_id=hashlib.md5(name.encode()).hexdigest()[:8],
            name=name,
            category=category,
            template=optimization.optimized_prompt,
            variables=variables,
            expected_output_format="structured_response",
            quality_score=optimization.quality_score_after
        )
        
        self.templates[template_obj.template_id] = template_obj
        return template_obj
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate prompt optimization report"""
        return {
            "total_templates": len(self.templates),
            "average_quality_score": sum(t.quality_score for t in self.templates.values()) / max(len(self.templates), 1),
            "optimization_rules": self.optimization_rules,
            "top_templates": sorted(
                self.templates.values(),
                key=lambda t: t.quality_score,
                reverse=True
            )[:5]  # Top 5 templates
        }

# Global prompt optimizer
prompt_optimizer = AdvancedPromptOptimizer()

# Create example optimized templates
example_templates = [
    {
        "name": "Content Generation",
        "category": "content_generation",
        "template": "Create engaging content about {topic} for {audience}"
    },
    {
        "name": "SEO Optimization",
        "category": "optimization", 
        "template": "Optimize this content for search engines: {content}"
    },
    {
        "name": "Collaboration Analysis",
        "category": "analysis",
        "template": "Analyze the collaboration potential between {brand} and {influencer}"
    }
]

for template_data in example_templates:
    prompt_optimizer.create_template(
        template_data["name"],
        template_data["category"],
        template_data["template"]
    )
