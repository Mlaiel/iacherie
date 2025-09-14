"""
Prompt Optimizer - IA Prompt Engineer Expert Implementation
==========================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise AI prompt optimization and management system.
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
import hashlib

logger = logging.getLogger(__name__)


class PromptType(Enum):
    """Types of AI prompts"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    CREATIVE_WRITING = "creative_writing"
    ANALYSIS = "analysis"
    INSTRUCTION_FOLLOWING = "instruction_following"


@dataclass
class PromptTemplate:
    """Prompt template structure"""
    name: str
    template: str
    prompt_type: PromptType
    variables: List[str]
    description: str
    examples: List[Dict[str, str]]
    created_at: datetime
    version: str = "1.0"


@dataclass
class OptimizationResult:
    """Prompt optimization result"""
    original_prompt: str
    optimized_prompt: str
    improvements: List[str]
    score_improvement: float
    optimization_time: float
    suggestions: List[str]


class PromptOptimizer:
    """
    Enterprise prompt optimization system implementing:
    - Prompt template management
    - Automatic prompt optimization
    - A/B testing for prompts
    - Performance tracking
    - Multi-language support
    - Context injection
    """
    
    def __init__(self) -> None:
        """Initialize prompt optimizer"""
        self.templates: Dict[str, PromptTemplate] = {}
        self.optimization_rules = self._load_optimization_rules()
        self.prompt_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.performance_metrics = {
            'total_optimizations': 0,
            'average_improvement': 0.0,
            'templates_created': 0,
            'prompts_generated': 0
        }
        
        # Language-specific optimizations
        self.language_patterns = {
            'en': {
                'politeness_markers': ['please', 'kindly', 'would you'],
                'clarity_markers': ['specifically', 'exactly', 'precisely'],
                'instruction_markers': ['step by step', 'detailed', 'comprehensive']
            },
            'fr': {
                'politeness_markers': ['s\'il vous plaît', 'veuillez', 'pourriez-vous'],
                'clarity_markers': ['spécifiquement', 'exactement', 'précisément'],
                'instruction_markers': ['étape par étape', 'détaillé', 'complet']
            }
        }
        
        logger.info("PromptOptimizer initialized with enterprise features")
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load prompt optimization rules"""
        return {
            'clarity_rules': [
                {
                    'pattern': r'can you',
                    'replacement': 'please',
                    'reason': 'More direct instruction'
                },
                {
                    'pattern': r'try to',
                    'replacement': '',
                    'reason': 'Remove uncertainty'
                },
                {
                    'pattern': r'maybe|perhaps|possibly',
                    'replacement': '',
                    'reason': 'Remove ambiguity'
                }
            ],
            'structure_rules': [
                {
                    'check': 'has_context',
                    'suggestion': 'Add context information before the main instruction'
                },
                {
                    'check': 'has_examples',
                    'suggestion': 'Include examples to clarify expected output'
                },
                {
                    'check': 'has_format_specification',
                    'suggestion': 'Specify desired output format'
                }
            ],
            'length_rules': [
                {
                    'min_length': 20,
                    'max_length': 2000,
                    'recommendation': 'Optimal prompt length is 50-500 characters'
                }
            ]
        }
    
    def create_template(self, name: str, template: str, prompt_type: PromptType,
                       description: str = "", examples: List[Dict[str, str]] = None) -> PromptTemplate:
        """Create a new prompt template"""
        try:
            # Extract variables from template
            variables = re.findall(r'\{(\w+)\}', template)
            
            template_obj = PromptTemplate(
                name=name,
                template=template,
                prompt_type=prompt_type,
                variables=variables,
                description=description,
                examples=examples or [],
                created_at=datetime.now()
            )
            
            self.templates[name] = template_obj
            self.performance_metrics['templates_created'] += 1
            
            logger.info(f"Template created: {name} with {len(variables)} variables")
            return template_obj
            
        except Exception as e:
            logger.error(f"Template creation failed: {e}")
            raise
    
    def generate_prompt(self, template_name: str, variables: Dict[str, str],
                       optimize: bool = True) -> str:
        """Generate prompt from template with variables"""
        try:
            if template_name not in self.templates:
                raise ValueError(f"Template '{template_name}' not found")
            
            template = self.templates[template_name]
            
            # Substitute variables
            prompt = template.template
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                prompt = prompt.replace(placeholder, str(var_value))
            
            # Check for missing variables
            remaining_vars = re.findall(r'\{(\w+)\}', prompt)
            if remaining_vars:
                logger.warning(f"Missing variables in prompt: {remaining_vars}")
            
            # Optimize if requested
            if optimize:
                optimization_result = self.optimize_prompt(prompt, template.prompt_type)
                prompt = optimization_result.optimized_prompt
            
            # Track generation
            self.performance_metrics['prompts_generated'] += 1
            
            # Store in history
            self.prompt_history.append({
                'template_name': template_name,
                'variables': variables,
                'generated_prompt': prompt,
                'timestamp': datetime.now().isoformat(),
                'optimized': optimize
            })
            
            logger.debug(f"Prompt generated from template: {template_name}")
            return prompt
            
        except Exception as e:
            logger.error(f"Prompt generation failed: {e}")
            raise
    
    def optimize_prompt(self, prompt: str, prompt_type: PromptType = None) -> OptimizationResult:
        """Optimize a prompt for better performance"""
        try:
            start_time = time.time()
            original_prompt = prompt
            optimized_prompt = prompt
            improvements = []
            suggestions = []
            
            # Apply clarity rules
            for rule in self.optimization_rules['clarity_rules']:
                pattern = rule['pattern']
                replacement = rule['replacement']
                reason = rule['reason']
                
                if re.search(pattern, optimized_prompt, re.IGNORECASE):
                    optimized_prompt = re.sub(pattern, replacement, optimized_prompt, flags=re.IGNORECASE)
                    improvements.append(f"Applied clarity rule: {reason}")
            
            # Check structure
            structure_score = self._analyze_prompt_structure(optimized_prompt)
            
            # Add structure improvements
            if not self._has_clear_instruction(optimized_prompt):
                suggestions.append("Add a clear, specific instruction")
            
            if len(optimized_prompt.split()) < 10:
                suggestions.append("Consider adding more context to improve clarity")
            
            if prompt_type and not self._has_output_format_specification(optimized_prompt):
                suggestions.append("Specify the desired output format")
            
            # Add role specification if beneficial
            if prompt_type in [PromptType.CODE_GENERATION, PromptType.ANALYSIS]:
                if not self._has_role_specification(optimized_prompt):
                    role_prefix = self._get_role_prefix(prompt_type)
                    optimized_prompt = f"{role_prefix}\n\n{optimized_prompt}"
                    improvements.append("Added role specification for better context")
            
            # Add step-by-step instruction for complex tasks
            if prompt_type in [PromptType.ANALYSIS, PromptType.CODE_GENERATION]:
                if "step by step" not in optimized_prompt.lower():
                    optimized_prompt = optimized_prompt + "\n\nPlease approach this step by step."
                    improvements.append("Added step-by-step instruction")
            
            # Clean up extra whitespace
            optimized_prompt = re.sub(r'\s+', ' ', optimized_prompt).strip()
            
            # Calculate improvement score
            original_score = self._calculate_prompt_score(original_prompt, prompt_type)
            optimized_score = self._calculate_prompt_score(optimized_prompt, prompt_type)
            score_improvement = optimized_score - original_score
            
            optimization_time = time.time() - start_time
            
            # Update statistics
            self.performance_metrics['total_optimizations'] += 1
            current_avg = self.performance_metrics['average_improvement']
            total_opts = self.performance_metrics['total_optimizations']
            new_avg = (current_avg * (total_opts - 1) + score_improvement) / total_opts
            self.performance_metrics['average_improvement'] = new_avg
            
            result = OptimizationResult(
                original_prompt=original_prompt,
                optimized_prompt=optimized_prompt,
                improvements=improvements,
                score_improvement=score_improvement,
                optimization_time=optimization_time,
                suggestions=suggestions
            )
            
            logger.info(f"Prompt optimized: {score_improvement:.2f} score improvement")
            return result
            
        except Exception as e:
            logger.error(f"Prompt optimization failed: {e}")
            raise
    
    def _analyze_prompt_structure(self, prompt: str) -> Dict[str, Any]:
        """Analyze the structure of a prompt"""
        analysis = {
            'word_count': len(prompt.split()),
            'character_count': len(prompt),
            'sentence_count': len(re.findall(r'[.!?]+', prompt)),
            'has_questions': '?' in prompt,
            'has_instructions': any(word in prompt.lower() for word in ['please', 'generate', 'create', 'write', 'analyze']),
            'has_context': len(prompt.split()) > 20,
            'has_examples': 'example' in prompt.lower() or 'for instance' in prompt.lower(),
            'clarity_score': 0.0
        }
        
        # Calculate clarity score
        clarity_factors = [
            analysis['has_instructions'],
            analysis['word_count'] > 10,
            analysis['word_count'] < 200,
            not bool(re.search(r'maybe|perhaps|try to', prompt.lower()))
        ]
        
        analysis['clarity_score'] = sum(clarity_factors) / len(clarity_factors)
        
        return analysis
    
    def _calculate_prompt_score(self, prompt: str, prompt_type: PromptType = None) -> float:
        """Calculate overall quality score for a prompt"""
        analysis = self._analyze_prompt_structure(prompt)
        
        # Base score from structure
        score = analysis['clarity_score'] * 40
        
        # Length bonus/penalty
        word_count = analysis['word_count']
        if 20 <= word_count <= 100:
            score += 20
        elif 10 <= word_count <= 200:
            score += 10
        elif word_count < 10:
            score -= 20
        
        # Instruction clarity
        if analysis['has_instructions']:
            score += 15
        
        # Context bonus
        if analysis['has_context']:
            score += 10
        
        # Examples bonus
        if analysis['has_examples']:
            score += 15
        
        # Type-specific scoring
        if prompt_type:
            if prompt_type == PromptType.CODE_GENERATION:
                if 'step by step' in prompt.lower():
                    score += 10
                if any(lang in prompt.lower() for lang in ['python', 'javascript', 'java', 'c++']):
                    score += 5
            
            elif prompt_type == PromptType.CREATIVE_WRITING:
                if any(word in prompt.lower() for word in ['creative', 'imagine', 'story']):
                    score += 10
        
        return min(100, max(0, score))  # Clamp between 0-100
    
    def _has_clear_instruction(self, prompt: str) -> bool:
        """Check if prompt has clear instruction"""
        instruction_words = ['write', 'create', 'generate', 'analyze', 'explain', 'describe', 'list']
        return any(word in prompt.lower() for word in instruction_words)
    
    def _has_output_format_specification(self, prompt: str) -> bool:
        """Check if prompt specifies output format"""
        format_words = ['format', 'json', 'list', 'table', 'bullet points', 'numbered']
        return any(word in prompt.lower() for word in format_words)
    
    def _has_role_specification(self, prompt: str) -> bool:
        """Check if prompt has role specification"""
        role_indicators = ['you are', 'act as', 'as a', 'your role']
        return any(phrase in prompt.lower() for phrase in role_indicators)
    
    def _get_role_prefix(self, prompt_type: PromptType) -> str:
        """Get appropriate role prefix for prompt type"""
        role_prefixes = {
            PromptType.CODE_GENERATION: "You are an expert software developer.",
            PromptType.ANALYSIS: "You are a skilled analyst with expertise in data interpretation.",
            PromptType.CREATIVE_WRITING: "You are a creative writer with excellent storytelling abilities.",
            PromptType.TRANSLATION: "You are a professional translator with native-level fluency.",
            PromptType.SUMMARIZATION: "You are an expert at creating clear, concise summaries."
        }
        
        return role_prefixes.get(prompt_type, "You are a helpful assistant.")
    
    def compare_prompts(self, prompt_a: str, prompt_b: str, 
                       prompt_type: PromptType = None) -> Dict[str, Any]:
        """Compare two prompts and provide recommendations"""
        try:
            score_a = self._calculate_prompt_score(prompt_a, prompt_type)
            score_b = self._calculate_prompt_score(prompt_b, prompt_type)
            
            analysis_a = self._analyze_prompt_structure(prompt_a)
            analysis_b = self._analyze_prompt_structure(prompt_b)
            
            comparison = {
                'prompt_a': {
                    'text': prompt_a,
                    'score': score_a,
                    'analysis': analysis_a
                },
                'prompt_b': {
                    'text': prompt_b,
                    'score': score_b,
                    'analysis': analysis_b
                },
                'winner': 'A' if score_a > score_b else 'B' if score_b > score_a else 'Tie',
                'score_difference': abs(score_a - score_b),
                'recommendations': []
            }
            
            # Generate recommendations
            if analysis_a['word_count'] > analysis_b['word_count'] * 2:
                comparison['recommendations'].append("Prompt A might be too verbose")
            
            if analysis_b['clarity_score'] > analysis_a['clarity_score']:
                comparison['recommendations'].append("Prompt B has better clarity")
            
            if analysis_a['has_examples'] and not analysis_b['has_examples']:
                comparison['recommendations'].append("Prompt A provides better examples")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Prompt comparison failed: {e}")
            raise
    
    def get_template_suggestions(self, prompt_type: PromptType, 
                               domain: str = "general") -> List[str]:
        """Get template suggestions for specific prompt type and domain"""
        suggestions = {
            PromptType.TEXT_GENERATION: [
                "Generate a {content_type} about {topic} that is {tone} and {length}.",
                "Write a {format} that explains {concept} for {audience}.",
                "Create {content_type} content that covers {main_points}."
            ],
            PromptType.CODE_GENERATION: [
                "Write a {language} function that {functionality}. Include error handling and comments.",
                "Create a {language} script that {task}. Follow best practices and add documentation.",
                "Implement {algorithm} in {language} with {requirements}."
            ],
            PromptType.ANALYSIS: [
                "Analyze the {data_type} and identify {analysis_focus}. Provide insights and recommendations.",
                "Examine {subject} from {perspective} and explain {key_aspects}.",
                "Review {content} and provide {analysis_type} with supporting evidence."
            ]
        }
        
        return suggestions.get(prompt_type, [])
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get prompt optimization performance metrics"""
        metrics = self.performance_metrics.copy()
        
        # Add template statistics
        if self.templates:
            template_types = [t.prompt_type.value for t in self.templates.values()]
            metrics['template_types_distribution'] = {
                ptype: template_types.count(ptype) for ptype in set(template_types)
            }
        
        metrics['total_templates'] = len(self.templates)
        metrics['prompt_history_size'] = len(self.prompt_history)
        
        return metrics
    
    def export_templates(self) -> str:
        """Export all templates as JSON"""
        try:
            export_data = {}
            for name, template in self.templates.items():
                export_data[name] = {
                    'template': template.template,
                    'prompt_type': template.prompt_type.value,
                    'variables': template.variables,
                    'description': template.description,
                    'examples': template.examples,
                    'created_at': template.created_at.isoformat(),
                    'version': template.version
                }
            
            return json.dumps(export_data, indent=2)
            
        except Exception as e:
            logger.error(f"Template export failed: {e}")
            raise


# Global instance
prompt_optimizer = PromptOptimizer()