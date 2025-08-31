# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Advanced Template Engine Tests
Ultra-professional test suite for the Template Engine system

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

 COPYRIGHT WARNING 
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de)
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted under German and International copyright law.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import uuid
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

from ai.prompts.template_engine import (
    TemplateEngine, TemplateProcessor, VariableResolver, TemplateType,
    VariableType, TemplateVariable, TemplateProcessingError, TemplateValidationError
)


class TestTemplateEngine:
    """Ultra-comprehensive test suite for TemplateEngine"""
    
    @pytest.fixture
    async def template_engine(self):
        """Create a fresh TemplateEngine instance for each test"""
        engine = TemplateEngine()
        await engine.initialize()
        yield engine
        await engine.cleanup()
    
    @pytest.fixture
    def sample_template_variables(self):
        """Create sample template variables for testing"""



        return [
            TemplateVariable(
                name="user_name",
                var_type=VariableType.STRING,
                required=True,
                min_length=2,
                max_length=50,
                description="User's full name"
            ),
            TemplateVariable(
                name="age",
                var_type=VariableType.INTEGER,
                required=False,
                default_value=25,
                description="User's age"
            ),
            TemplateVariable(
                name="email",
                var_type=VariableType.EMAIL,
                required=True,
                pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                description="User's email address"
            ),
            TemplateVariable(
                name="preferences",
                var_type=VariableType.LIST,
                required=False,
                default_value=[],
                description="User preferences list"
            ),
            TemplateVariable(
                name="is_premium",
                var_type=VariableType.BOOLEAN,
                required=False,
                default_value=False,
                description="Premium membership status"
            )
        ]
    
    @pytest.fixture
    def sample_template_data(self):
        """Sample data for template processing"""



        return {
            "user_name": "Fahed Mlaiel",
            "age": 30,
            "email": "mlaiel@live.de",
            "preferences": ["AI", "Music Production", "Technology"],
            "is_premium": True,
            "country": "Germany",
            "language": "en"
        }
    
    # ===== INITIALIZATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_template_engine_initialization(self, template_engine):
        """Test TemplateEngine initialization"""
        assert template_engine is not None
        assert hasattr(template_engine, 'processor')
        assert hasattr(template_engine, 'variable_resolver')
        assert hasattr(template_engine, 'conditional_processor')
        assert hasattr(template_engine, 'loop_processor')
        assert hasattr(template_engine, 'multilang_processor')
        
        assert isinstance(template_engine.processor, TemplateProcessor)
        assert isinstance(template_engine.variable_resolver, VariableResolver)
    
    @pytest.mark.asyncio
    async def test_template_engine_configuration(self, template_engine):
        """Test TemplateEngine configuration"""
        config = await template_engine.get_configuration()
        assert config is not None
        assert "variable_syntax" in config
        assert "conditional_syntax" in config
        assert "loop_syntax" in config
        assert "cache_enabled" in config
        assert "security_enabled" in config
        
        assert config["variable_syntax"]["open"] == "{{"
        assert config["variable_syntax"]["close"] == "}}"
        assert isinstance(config["cache_enabled"], bool)
        assert isinstance(config["security_enabled"], bool)
    
    # ===== VARIABLE VALIDATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_variable_validation_success(self, template_engine, sample_template_variables):
        """Test successful variable validation"""
        test_values = {
            "user_name": "Fahed Mlaiel",
            "age": 30,
            "email": "mlaiel@live.de",
            "preferences": ["AI", "Music"],
            "is_premium": True
        }
        
        for variable in sample_template_variables:
            if variable.name in test_values:
                result = await template_engine.validate_variable(
                    variable, test_values[variable.name]
                )
                assert result["valid"] is True
                assert result["errors"] == []
    
    @pytest.mark.asyncio
    async def test_variable_validation_type_errors(self, template_engine):
        """Test variable validation with type errors"""
        string_var = TemplateVariable(
            name="test_string",
            var_type=VariableType.STRING,
            required=True
        )
        
        # Test wrong type
        result = await template_engine.validate_variable(string_var, 123)
        assert result["valid"] is False
        assert "type" in result["errors"][0].lower()
        
        # Test integer variable with string
        int_var = TemplateVariable(
            name="test_int",
            var_type=VariableType.INTEGER,
            required=True
        )
        
        result = await template_engine.validate_variable(int_var, "not_a_number")
        assert result["valid"] is False
        assert "type" in result["errors"][0].lower()
    
    @pytest.mark.asyncio
    async def test_variable_validation_length_constraints(self, template_engine):
        """Test variable validation with length constraints"""
        string_var = TemplateVariable(
            name="constrained_string",
            var_type=VariableType.STRING,
            required=True,
            min_length=5,
            max_length=20
        )
        
        # Test too short
        result = await template_engine.validate_variable(string_var, "123")
        assert result["valid"] is False
        assert "length" in result["errors"][0].lower()
        
        # Test too long
        result = await template_engine.validate_variable(string_var, "a" * 25)
        assert result["valid"] is False
        assert "length" in result["errors"][0].lower()
        
        # Test valid length
        result = await template_engine.validate_variable(string_var, "valid_string")
        assert result["valid"] is True
    
    @pytest.mark.asyncio
    async def test_variable_validation_pattern_matching(self, template_engine):
        """Test variable validation with pattern matching"""
        email_var = TemplateVariable(
            name="email",
            var_type=VariableType.EMAIL,
            required=True,
            pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # Test invalid email
        result = await template_engine.validate_variable(email_var, "invalid_email")
        assert result["valid"] is False
        assert "pattern" in result["errors"][0].lower() or "email" in result["errors"][0].lower()
        
        # Test valid email
        result = await template_engine.validate_variable(email_var, "test@example.com")
        assert result["valid"] is True
    
    # ===== SIMPLE TEMPLATE PROCESSING TESTS =====
    
    @pytest.mark.asyncio
    async def test_simple_variable_substitution(self, template_engine, sample_template_data):
        """Test simple variable substitution in templates"""
        template = "Hello {{user_name}}, welcome to our platform!"
        
        result = await template_engine.process_template(
            template=template,
            variables=sample_template_data
        )
        
        assert result["success"] is True
        assert result["processed_template"] == "Hello Fahed Mlaiel, welcome to our platform!"
    
    @pytest.mark.asyncio
    async def test_multiple_variable_substitution(self, template_engine, sample_template_data):
        """Test multiple variable substitution"""
        template = """
        Dear {{user_name}},
        
        Your email {{email}} has been verified.
        Age: {{age}}
        Premium Status: {{is_premium}}
        Country: {{country}}
        """
        
        result = await template_engine.process_template(
            template=template,
            variables=sample_template_data
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        assert "Fahed Mlaiel" in processed
        assert "mlaiel@live.de" in processed
        assert "30" in processed
        assert "True" in processed
        assert "Germany" in processed
    
    @pytest.mark.asyncio
    async def test_missing_variable_handling(self, template_engine):
        """Test handling of missing variables"""
        template = "Hello {{user_name}}, your score is {{missing_variable}}"
        variables = {"user_name": "Fahed"}
        
        # Test with strict mode (should fail)
        result = await template_engine.process_template(
            template=template,
            variables=variables,
            strict_mode=True
        )
        
        assert result["success"] is False
        assert "missing_variable" in result["error"]
        
        # Test with lenient mode (should succeed with placeholder)
        result = await template_engine.process_template(
            template=template,
            variables=variables,
            strict_mode=False
        )
        
        assert result["success"] is True
        assert "{{missing_variable}}" in result["processed_template"] or "[MISSING]" in result["processed_template"]
    
    # ===== CONDITIONAL PROCESSING TESTS =====
    
    @pytest.mark.asyncio
    async def test_conditional_if_statement(self, template_engine, sample_template_data):
        """Test conditional if statements in templates"""
        template = """
        Welcome {{user_name}}!
        {% if is_premium %}
        You have premium access to all features.
        {% endif %}
        """
        
        result = await template_engine.process_template(
            template=template,
            variables=sample_template_data
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        assert "Welcome Fahed Mlaiel!" in processed
        assert "premium access" in processed  # Should be included because is_premium is True
    
    @pytest.mark.asyncio
    async def test_conditional_if_else_statement(self, template_engine):
        """Test conditional if-else statements"""
        template = """
        {% if is_premium %}
        Premium user detected.
        {% else %}
        Standard user detected.
        {% endif %}
        """
        
        # Test with premium user
        premium_data = {"is_premium": True}
        result = await template_engine.process_template(
            template=template,
            variables=premium_data
        )
        
        assert result["success"] is True
        assert "Premium user detected" in result["processed_template"]
        assert "Standard user detected" not in result["processed_template"]
        
        # Test with standard user
        standard_data = {"is_premium": False}
        result = await template_engine.process_template(
            template=template,
            variables=standard_data
        )
        
        assert result["success"] is True
        assert "Standard user detected" in result["processed_template"]
        assert "Premium user detected" not in result["processed_template"]
    
    @pytest.mark.asyncio
    async def test_complex_conditional_expressions(self, template_engine):
        """Test complex conditional expressions"""
        template = """
        {% if age >= 18 and country == "Germany" %}
        You can access all content in Germany.
        {% elif age >= 18 %}
        You can access age-appropriate content.
        {% else %}
        Parental guidance required.
        {% endif %}
        """
        
        # Test German adult
        german_adult = {"age": 25, "country": "Germany"}
        result = await template_engine.process_template(template=template, variables=german_adult)
        assert result["success"] is True
        assert "access all content in Germany" in result["processed_template"]
        
        # Test non-German adult
        other_adult = {"age": 22, "country": "USA"}
        result = await template_engine.process_template(template=template, variables=other_adult)
        assert result["success"] is True
        assert "age-appropriate content" in result["processed_template"]
        
        # Test minor
        minor = {"age": 16, "country": "Germany"}
        result = await template_engine.process_template(template=template, variables=minor)
        assert result["success"] is True
        assert "Parental guidance required" in result["processed_template"]
    
    # ===== LOOP PROCESSING TESTS =====
    
    @pytest.mark.asyncio
    async def test_simple_loop_processing(self, template_engine, sample_template_data):
        """Test simple loop processing"""
        template = """
        Your preferences:
        {% for preference in preferences %}
        - {{preference}}
        {% endfor %}
        """
        
        result = await template_engine.process_template(
            template=template,
            variables=sample_template_data
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        assert "- AI" in processed
        assert "- Music Production" in processed
        assert "- Technology" in processed
    
    @pytest.mark.asyncio
    async def test_loop_with_index(self, template_engine):
        """Test loop processing with index"""
        template = """
        {% for item in items %}
        {{loop.index}}: {{item}}
        {% endfor %}
        """
        
        variables = {"items": ["First", "Second", "Third"]}
        result = await template_engine.process_template(
            template=template,
            variables=variables
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        assert "1: First" in processed
        assert "2: Second" in processed
        assert "3: Third" in processed
    
    @pytest.mark.asyncio
    async def test_nested_loop_processing(self, template_engine):
        """Test nested loop processing"""
        template = """
        {% for category in categories %}
        Category: {{category.name}}
        {% for item in category.items %}
          - {{item}}
        {% endfor %}
        {% endfor %}
        """
        
        variables = {
            "categories": [
                {"name": "Music", "items": ["Guitar", "Piano", "Drums"]},
                {"name": "Tech", "items": ["AI", "Programming", "Robotics"]}
            ]
        }
        
        result = await template_engine.process_template(
            template=template,
            variables=variables
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        assert "Category: Music" in processed
        assert "- Guitar" in processed
        assert "Category: Tech" in processed
        assert "- AI" in processed
    
    # ===== MULTILANGUAGE PROCESSING TESTS =====
    
    @pytest.mark.asyncio
    async def test_multilanguage_template_processing(self, template_engine):
        """Test multilanguage template processing"""
        template = """
        {% lang en %}
        Welcome {{user_name}}!
        {% endlang %}
        {% lang de %}
        Willkommen {{user_name}}!
        {% endlang %}
        {% lang fr %}
        Bienvenue {{user_name}}!
        {% endlang %}
        """
        
        variables = {"user_name": "Fahed", "language": "de"}
        
        result = await template_engine.process_template(
            template=template,
            variables=variables,
            language="de"
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        assert "Willkommen Fahed!" in processed
        assert "Welcome" not in processed
        assert "Bienvenue" not in processed
    
    @pytest.mark.asyncio
    async def test_multilanguage_with_fallback(self, template_engine):
        """Test multilanguage processing with fallback"""
        template = """
        {% lang en %}
        Default English content for {{user_name}}
        {% endlang %}
        {% lang de %}
        German content for {{user_name}}
        {% endlang %}
        """
        
        variables = {"user_name": "Fahed"}
        
        # Test with unsupported language (should fallback to English)
        result = await template_engine.process_template(
            template=template,
            variables=variables,
            language="es",  # Spanish not supported
            fallback_language="en"
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        assert "Default English content for Fahed" in processed
    
    # ===== ADVANCED TEMPLATE FEATURES TESTS =====
    
    @pytest.mark.asyncio
    async def test_template_inheritance(self, template_engine):
        """Test template inheritance functionality"""
        base_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{% block title %}Default Title{% endblock %}</title>
        </head>
        <body>
            {% block content %}{% endblock %}
        </body>
        </html>
        """
        
        child_template = """
        {% extends "base" %}
        {% block title %}{{page_title}}{% endblock %}
        {% block content %}
        <h1>Welcome {{user_name}}</h1>
        <p>{{content_text}}</p>
        {% endblock %}
        """
        
        # Register base template
        await template_engine.register_template("base", base_template)
        
        variables = {
            "page_title": "AI Music Platform",
            "user_name": "Fahed Mlaiel",
            "content_text": "Welcome to the future of music creation!"
        }
        
        result = await template_engine.process_template(
            template=child_template,
            variables=variables
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        assert "<title>AI Music Platform</title>" in processed
        assert "<h1>Welcome Fahed Mlaiel</h1>" in processed
        assert "Welcome to the future of music creation!" in processed
    
    @pytest.mark.asyncio
    async def test_template_macros(self, template_engine):
        """Test template macros functionality"""
        template = """
        {% macro render_user_card(user) %}
        <div class="user-card">
            <h3>{{user.name}}</h3>
            <p>{{user.email}}</p>
            {% if user.is_premium %}
            <span class="premium-badge">Premium</span>
            {% endif %}
        </div>
        {% endmacro %}
        
        {% for user in users %}
        {{render_user_card(user)}}
        {% endfor %}
        """
        
        variables = {
            "users": [
                {"name": "Fahed Mlaiel", "email": "mlaiel@live.de", "is_premium": True},
                {"name": "John Doe", "email": "john@example.com", "is_premium": False}
            ]
        }
        
        result = await template_engine.process_template(
            template=template,
            variables=variables
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        assert "Fahed Mlaiel" in processed
        assert "mlaiel@live.de" in processed
        assert "premium-badge" in processed
        assert "John Doe" in processed
        assert processed.count("user-card") == 2
    
    # ===== SECURITY TESTS =====
    
    @pytest.mark.asyncio
    async def test_template_security_xss_prevention(self, template_engine):
        """Test XSS prevention in templates"""
        template = "Hello {{user_input}}!"
        
        # Test with potentially malicious input
        malicious_variables = {
            "user_input": "<script>alert('XSS')</script>"
        }
        
        result = await template_engine.process_template(
            template=template,
            variables=malicious_variables,
            auto_escape=True
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        assert "<script>" not in processed
        assert "&lt;script&gt;" in processed or "alert" not in processed
    
    @pytest.mark.asyncio
    async def test_template_security_injection_prevention(self, template_engine):
        """Test injection attack prevention"""
        template = "User data: {{user_data}}"
        
        # Test with template injection attempt
        injection_variables = {
            "user_data": "{{config.secret_key}}"
        }
        
        result = await template_engine.process_template(
            template=template,
            variables=injection_variables,
            security_mode=True
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        # Should not process the nested template syntax
        assert "{{config.secret_key}}" in processed or "[SANITIZED]" in processed
    
    # ===== PERFORMANCE TESTS =====
    
    @pytest.mark.asyncio
    async def test_template_caching_performance(self, template_engine):
        """Test template caching for performance"""
        template = "Welcome {{user_name}} to {{platform_name}}!"
        variables = {"user_name": "Fahed", "platform_name": "AI Music Platform"}
        
        # First execution (should cache)
        start_time = datetime.now()
        result1 = await template_engine.process_template(
            template=template,
            variables=variables,
            use_cache=True
        )
        first_duration = (datetime.now() - start_time).total_seconds()
        
        # Second execution (should use cache)
        start_time = datetime.now()
        result2 = await template_engine.process_template(
            template=template,
            variables=variables,
            use_cache=True
        )
        second_duration = (datetime.now() - start_time).total_seconds()
        
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["processed_template"] == result2["processed_template"]
        
        # Second execution should be faster due to caching
        assert second_duration <= first_duration
    
    @pytest.mark.asyncio
    async def test_large_template_processing(self, template_engine):
        """Test processing of large templates"""
        # Create a large template with many variables
        template_parts = []
        variables = {}
        
        for i in range(100):
            template_parts.append(f"Variable {i}: {{var_{i}}}")
            variables[f"var_{i}"] = f"Value {i}"
        
        large_template = "\n".join(template_parts)
        
        start_time = datetime.now()
        result = await template_engine.process_template(
            template=large_template,
            variables=variables
        )
        duration = (datetime.now() - start_time).total_seconds()
        
        assert result["success"] is True
        assert duration < 5.0  # Should complete within 5 seconds
        
        processed = result["processed_template"]
        assert "Value 0" in processed
        assert "Value 99" in processed
    
    # ===== ERROR HANDLING TESTS =====
    
    @pytest.mark.asyncio
    async def test_malformed_template_syntax_error(self, template_engine):
        """Test error handling for malformed template syntax"""
        malformed_templates = [
            "{{unclosed_variable",
            "{% if condition %}{% endif %}}",  # Extra closing
            "{% for item in items %}{% endloop %}",  # Wrong closing tag
            "{{variable.invalid..attribute}}"  # Invalid attribute access
        ]
        
        for malformed_template in malformed_templates:
            result = await template_engine.process_template(
                template=malformed_template,
                variables={"condition": True, "items": [1, 2, 3], "variable": {"attr": "value"}}
            )
            
            assert result["success"] is False
            assert "syntax" in result["error"].lower() or "malformed" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_circular_template_dependency_error(self, template_engine):
        """Test error handling for circular template dependencies"""
        template_a = "{% extends 'template_b' %} Content A"
        template_b = "{% extends 'template_a' %} Content B"
        
        await template_engine.register_template("template_a", template_a)
        await template_engine.register_template("template_b", template_b)
        
        result = await template_engine.process_template(
            template="{% extends 'template_a' %}",
            variables={}
        )
        
        assert result["success"] is False
        assert "circular" in result["error"].lower() or "dependency" in result["error"].lower()
    
    # ===== INTEGRATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_comprehensive_template_integration(self, template_engine):
        """Test comprehensive template with all features"""
        complex_template = """
        {% lang en %}
        # Welcome to AI Music Platform, {{user_name}}!
        
        {% if is_premium %}
         **Premium User Benefits:**
        {% for benefit in premium_benefits %}
        - {{benefit}}
        {% endfor %}
        {% else %}
         **Standard User Features:**
        {% for feature in standard_features %}
        - {{feature}}
        {% endfor %}
        {% endif %}
        
        ## Your Statistics
        - Account Age: {{account_age}} days
        - Total Projects: {{project_count}}
        {% if project_count > 0 %}
        - Average Rating: {{average_rating}}/5.0
        {% endif %}
        
        ## Recent Activity
        {% for activity in recent_activities %}
        {{loop.index}}. {{activity.timestamp}}: {{activity.description}}
        {% endfor %}
        
        {% macro render_project(project) %}
        **{{project.name}}** ({{project.status}})
        Created: {{project.created_date}}
        {% if project.is_public %}
         Public Project
        {% else %}
         Private Project
        {% endif %}
        {% endmacro %}
        
        ## Your Projects
        {% for project in projects %}
        {{render_project(project)}}
        {% endfor %}
        
        ---
        Generated at: {{current_timestamp}}
        {% endlang %}
        """
        
        comprehensive_variables = {
            "user_name": "Fahed Mlaiel",
            "is_premium": True,
            "premium_benefits": [
                "Unlimited project storage",
                "Advanced AI features",
                "Priority support",
                "Commercial licensing"
            ],
            "standard_features": [
                "5 projects limit",
                "Basic AI features",
                "Community support"
            ],
            "account_age": 365,
            "project_count": 15,
            "average_rating": 4.7,
            "recent_activities": [
                {"timestamp": "2025-01-15 10:30", "description": "Created new AI composition"},
                {"timestamp": "2025-01-14 16:45", "description": "Shared project with collaborator"},
                {"timestamp": "2025-01-13 09:15", "description": "Upgraded to premium"}
            ],
            "projects": [
                {
                    "name": "Ambient AI Symphony",
                    "status": "completed",
                    "created_date": "2024-12-01",
                    "is_public": True
                },
                {
                    "name": "Electronic Dance Track",
                    "status": "in_progress", 
                    "created_date": "2025-01-10",
                    "is_public": False
                }
            ],
            "current_timestamp": "2025-01-15 12:00:00",
            "language": "en"
        }
        
        result = await template_engine.process_template(
            template=complex_template,
            variables=comprehensive_variables,
            language="en"
        )
        
        assert result["success"] is True
        processed = result["processed_template"]
        
        # Verify all features work together
        assert "Fahed Mlaiel" in processed
        assert "Premium User Benefits" in processed
        assert "Unlimited project storage" in processed
        assert "Account Age: 365 days" in processed
        assert "Average Rating: 4.7/5.0" in processed
        assert "1. 2025-01-15 10:30" in processed
        assert "Ambient AI Symphony" in processed
        assert " Public Project" in processed
        assert " Private Project" in processed
        assert "Generated at: 2025-01-15 12:00:00" in processed
