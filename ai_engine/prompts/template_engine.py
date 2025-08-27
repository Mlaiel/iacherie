"""
Template Engine

Professional template processing system with variable substitution,
conditional logic, and multi-language support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import re
import json
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Types of templates"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    NESTED = "nested"
    MULTILINGUAL = "multilingual"


class VariableType(Enum):
    """Variable types for validation"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    DATETIME = "datetime"
    URL = "url"
    EMAIL = "email"


@dataclass
class TemplateVariable:
    """Variable definition with validation rules"""
    name: str
    var_type: VariableType
    required: bool = True
    default_value: Any = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    choices: Optional[List[str]] = None
    description: str = ""
    
    def validate(self, value: Any) -> bool:
        """Validate variable value against rules"""
        if value is None and self.required:
            return False
        if value is None and not self.required:
            return True
            
        # Type validation
        if self.var_type == VariableType.STRING and not isinstance(value, str):
            return False
        elif self.var_type == VariableType.INTEGER and not isinstance(value, int):
            return False
        elif self.var_type == VariableType.FLOAT and not isinstance(value, (int, float)):
            return False
        elif self.var_type == VariableType.BOOLEAN and not isinstance(value, bool):
            return False
        elif self.var_type == VariableType.LIST and not isinstance(value, list):
            return False
        elif self.var_type == VariableType.DICT and not isinstance(value, dict):
            return False
        
        # String-specific validations
        if self.var_type == VariableType.STRING and isinstance(value, str):
            if self.min_length and len(value) < self.min_length:
                return False
            if self.max_length and len(value) > self.max_length:
                return False
            if self.pattern and not re.match(self.pattern, value):
                return False
            if self.choices and value not in self.choices:
                return False
                
        return True


class TemplateProcessor:
    """Professional template processing with conditional logic"""
    
    def __init__(self):
        self.variable_pattern = re.compile(r'\{\{(\w+)\}\}')
        self.conditional_pattern = re.compile(r'\{\% if (\w+) \%\}(.*?)\{\% endif \%\}', re.DOTALL)
        self.loop_pattern = re.compile(r'\{\% for (\w+) in (\w+) \%\}(.*?)\{\% endfor \%\}', re.DOTALL)
        self.function_pattern = re.compile(r'\{\{(\w+)\((.*?)\)\}\}')
        
    def process_template(self, template: str, variables: Dict[str, Any], 
                        functions: Optional[Dict[str, Callable]] = None) -> str:
        """Process template with variables, conditionals, and functions"""
        try:
            result = template
            
            # Process functions first
            if functions:
                result = self._process_functions(result, functions, variables)
            
            # Process conditionals
            result = self._process_conditionals(result, variables)
            
            # Process loops
            result = self._process_loops(result, variables)
            
            # Process simple variables
            result = self._process_variables(result, variables)
            
            return result
            
        except Exception as e:
            logger.error(f"Template processing failed: {str(e)}")
            raise TemplateProcessingError(f"Failed to process template: {str(e)}")
    
    def _process_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Replace variable placeholders with actual values"""
        def replacer(match):
            var_name = match.group(1)
            value = variables.get(var_name, f"{{{{MISSING:{var_name}}}}}")
            return str(value) if value is not None else ""
        
        return self.variable_pattern.sub(replacer, template)
    
    def _process_conditionals(self, template: str, variables: Dict[str, Any]) -> str:
        """Process conditional blocks"""
        def replacer(match):
            condition_var = match.group(1)
            content = match.group(2)
            
            if variables.get(condition_var):
                return content
            return ""
        
        return self.conditional_pattern.sub(replacer, template)
    
    def _process_loops(self, template: str, variables: Dict[str, Any]) -> str:
        """Process loop blocks"""
        def replacer(match):
            loop_var = match.group(1)
            iterable_var = match.group(2)
            content = match.group(3)
            
            iterable = variables.get(iterable_var, [])
            if not isinstance(iterable, (list, tuple)):
                return ""
            
            result = ""
            for item in iterable:
                loop_variables = variables.copy()
                loop_variables[loop_var] = item
                processed_content = self._process_variables(content, loop_variables)
                result += processed_content
            
            return result
        
        return self.loop_pattern.sub(replacer, template)
    
    def _process_functions(self, template: str, functions: Dict[str, Callable], 
                          variables: Dict[str, Any]) -> str:
        """Process function calls in templates"""
        def replacer(match):
            func_name = match.group(1)
            args_str = match.group(2)
            
            if func_name not in functions:
                return f"{{{{UNKNOWN_FUNCTION:{func_name}}}}}"
            
            try:
                # Parse arguments (simple implementation)
                args = []
                if args_str.strip():
                    arg_parts = [arg.strip().strip('"\'') for arg in args_str.split(',')]
                    for arg in arg_parts:
                        if arg in variables:
                            args.append(variables[arg])
                        else:
                            args.append(arg)
                
                result = functions[func_name](*args)
                return str(result) if result is not None else ""
                
            except Exception as e:
                logger.error(f"Function {func_name} failed: {str(e)}")
                return f"{{{{ERROR:{func_name}}}}}"
        
        return self.function_pattern.sub(replacer, template)


class VariableResolver:
    """Professional variable resolution with context awareness"""
    
    def __init__(self):
        self.context_stack = []
        self.global_variables = {}
        
    def push_context(self, context: Dict[str, Any]):
        """Push new variable context"""
        self.context_stack.append(context)
        
    def pop_context(self) -> Optional[Dict[str, Any]]:
        """Pop variable context"""
        if self.context_stack:
            return self.context_stack.pop()
        return None
    
    def resolve_variable(self, name: str, default: Any = None) -> Any:
        """Resolve variable from context stack"""
        # Check context stack (most recent first)
        for context in reversed(self.context_stack):
            if name in context:
                return context[name]
        
        # Check global variables
        if name in self.global_variables:
            return self.global_variables[name]
        
        return default
    
    def set_global_variable(self, name: str, value: Any):
        """Set global variable"""
        self.global_variables[name] = value
    
    def get_all_variables(self) -> Dict[str, Any]:
        """Get all available variables"""
        result = self.global_variables.copy()
        
        # Merge context stack
        for context in self.context_stack:
            result.update(context)
        
        return result


class TemplateEngine:
    """Main template engine with caching and optimization"""
    
    def __init__(self):
        self.processor = TemplateProcessor()
        self.resolver = VariableResolver()
        self.template_cache = {}
        self.compiled_templates = {}
        self.performance_stats = {}
        
    async def render_template(self, template_id: str, template_text: str,
                            variables: Dict[str, Any],
                            template_variables: List[TemplateVariable] = None,
                            functions: Optional[Dict[str, Callable]] = None,
                            use_cache: bool = True) -> str:
        """Render template with full feature support"""
        start_time = datetime.now()
        
        try:
            # Validate variables
            if template_variables:
                validation_errors = self._validate_variables(variables, template_variables)
                if validation_errors:
                    raise TemplateValidationError(f"Variable validation failed: {validation_errors}")
            
            # Check cache
            cache_key = self._generate_cache_key(template_id, variables)
            if use_cache and cache_key in self.template_cache:
                logger.debug(f"Template cache hit for {template_id}")
                return self.template_cache[cache_key]
            
            # Process template
            result = self.processor.process_template(template_text, variables, functions)
            
            # Cache result
            if use_cache:
                self.template_cache[cache_key] = result
            
            # Update performance stats
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_stats(template_id, processing_time, True)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_stats(template_id, processing_time, False)
            logger.error(f"Template rendering failed for {template_id}: {str(e)}")
            raise
    
    def _validate_variables(self, variables: Dict[str, Any], 
                          template_variables: List[TemplateVariable]) -> List[str]:
        """Validate template variables"""
        errors = []
        
        for var_def in template_variables:
            value = variables.get(var_def.name)
            
            if not var_def.validate(value):
                errors.append(f"Invalid value for '{var_def.name}': {value}")
        
        return errors
    
    def _generate_cache_key(self, template_id: str, variables: Dict[str, Any]) -> str:
        """Generate cache key for template and variables"""
        var_hash = hash(json.dumps(variables, sort_keys=True, default=str))
        return f"{template_id}:{var_hash}"
    
    def _update_performance_stats(self, template_id: str, processing_time: float, success: bool):
        """Update performance statistics"""
        if template_id not in self.performance_stats:
            self.performance_stats[template_id] = {
                'total_calls': 0,
                'successful_calls': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'success_rate': 0.0
            }
        
        stats = self.performance_stats[template_id]
        stats['total_calls'] += 1
        stats['total_time'] += processing_time
        
        if success:
            stats['successful_calls'] += 1
        
        stats['avg_time'] = stats['total_time'] / stats['total_calls']
        stats['success_rate'] = stats['successful_calls'] / stats['total_calls']
    
    def get_performance_stats(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get performance statistics for template"""
        return self.performance_stats.get(template_id)
    
    def clear_cache(self, template_id: str = None):
        """Clear template cache"""
        if template_id:
            # Clear specific template cache
            keys_to_remove = [key for key in self.template_cache.keys() 
                            if key.startswith(f"{template_id}:")]
            for key in keys_to_remove:
                del self.template_cache[key]
        else:
            # Clear all cache
            self.template_cache.clear()


class TemplateProcessingError(Exception):
    """Template processing error"""
    pass


class TemplateValidationError(Exception):
    """Template validation error"""
    pass
