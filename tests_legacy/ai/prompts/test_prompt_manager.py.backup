# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Advanced PromptManager Tests
Ultra-professional test suite for the PromptManager system

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ COPYRIGHT WARNING ⚠️
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
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

from ai.prompts.prompt_manager import (
    PromptManager, PromptTemplate, PromptCategory, PromptType, PromptStatus,
    PromptVariable, PromptExecution
)


class TestPromptManager:
    """Ultra-comprehensive test suite for PromptManager"""
    
    @pytest.fixture
    async def prompt_manager(self):
        """Create a fresh PromptManager instance for each test"""
        manager = PromptManager()
        await manager.initialize()
        yield manager
        # No cleanup method available in PromptManager
    
    @pytest.fixture
    def sample_prompt_template(self):
        """Create a sample prompt template for testing"""
        return PromptTemplate(
            template_id=str(uuid.uuid4()),
            name="Test Content Creation Prompt",
            description="A test prompt for content creation scenarios",
            category=PromptCategory.CONTENT_CREATION,
            prompt_type=PromptType.INSTRUCTION,
            template_text="Create a {content_type} about {topic} for {target_audience} with tone {tone}",
            variables=[
                PromptVariable(
                    name="content_type",
                    type="string",
                    description="Type of content to create",
                    required=True,
                    validation_rules={"choices": ["blog_post", "video_script", "social_media_post"]}
                ),
                PromptVariable(
                    name="topic",
                    type="string", 
                    description="Main topic of the content",
                    required=True,
                    validation_rules={"min_length": 3, "max_length": 100}
                ),
                PromptVariable(
                    name="target_audience",
                    type="string",
                    description="Target audience for the content",
                    required=True,
                    default_value="general public"
                ),
                PromptVariable(
                    name="tone",
                    type="string",
                    description="Tone of voice for the content",
                    required=False,
                    default_value="professional",
                    validation_rules={"choices": ["professional", "casual", "friendly", "formal"]}
                )
            ],
            metadata={"author": "Fahed Mlaiel", "version": "1.0.0"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_variables(self):
        """Sample variables for prompt template testing"""
        return {
            "content_type": "blog_post",
            "topic": "Artificial Intelligence in Music Production",
            "target_audience": "music producers and AI enthusiasts",
            "tone": "professional"
        }
    
    # ===== INITIALIZATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_prompt_manager_initialization(self):
        """Test PromptManager initialization"""
        manager = PromptManager()
        await manager.initialize()
        
        assert manager is not None
        assert hasattr(manager, 'templates')
        assert hasattr(manager, 'template_versions')
        assert hasattr(manager, 'active_templates')
        assert hasattr(manager, 'execution_history')
        assert hasattr(manager, 'performance_cache')
        assert isinstance(manager.templates, dict)
        assert isinstance(manager.template_versions, dict)
        assert isinstance(manager.active_templates, dict)
        assert isinstance(manager.execution_history, list)
        assert isinstance(manager.performance_cache, dict)
    
    @pytest.mark.asyncio
    async def test_prompt_manager_configuration(self, prompt_manager):
        """Test PromptManager configuration settings"""
        config = prompt_manager.get_configuration()
        assert config is not None
        assert "max_template_size" in config
        assert "cache_expiry_minutes" in config
        assert "optimization_enabled" in config
        assert "analytics_enabled" in config
        assert "version_control_enabled" in config
        
        assert config["max_template_size"] > 0
        assert config["cache_expiry_minutes"] > 0
        assert isinstance(config["optimization_enabled"], bool)
        assert isinstance(config["analytics_enabled"], bool)
    
    # ===== TEMPLATE MANAGEMENT TESTS =====
    
    @pytest.mark.asyncio
    async def test_create_prompt_template(self, prompt_manager, sample_prompt_template):
        """Test creating a new prompt template"""
        result = await prompt_manager.create_template(sample_prompt_template)
        
        assert result["success"] is True
        assert "template_id" in result
        assert result["template_id"] == sample_prompt_template.template_id
        
        # Verify template was stored
        stored_template = await prompt_manager.get_template(sample_prompt_template.template_id)
        assert stored_template is not None
        assert stored_template.name == sample_prompt_template.name
        assert stored_template.template_text == sample_prompt_template.template_text
        assert len(stored_template.variables) == len(sample_prompt_template.variables)
    
    @pytest.mark.asyncio
    async def test_create_duplicate_template_fails(self, prompt_manager, sample_prompt_template):
        """Test that creating duplicate templates fails appropriately"""
        # Create first template
        result1 = await prompt_manager.create_template(sample_prompt_template)
        assert result1["success"] is True
        
        # Attempt to create duplicate
        result2 = await prompt_manager.create_template(sample_prompt_template)
        assert result2["success"] is False
        assert "already exists" in result2["error"].lower()
    
    @pytest.mark.asyncio
    async def test_update_prompt_template(self, prompt_manager, sample_prompt_template):
        """Test updating an existing prompt template"""
        # Create template
        await prompt_manager.create_template(sample_prompt_template)
        
        # Update template
        sample_prompt_template.name = "Updated Test Prompt"
        sample_prompt_template.description = "Updated description"
        sample_prompt_template.updated_at = datetime.now()
        
        result = await prompt_manager.update_template(sample_prompt_template)
        assert result["success"] is True
        
        # Verify update
        updated_template = await prompt_manager.get_template(sample_prompt_template.template_id)
        assert updated_template.name == "Updated Test Prompt"
        assert updated_template.description == "Updated description"
    
    @pytest.mark.asyncio
    async def test_delete_prompt_template(self, prompt_manager, sample_prompt_template):
        """Test deleting a prompt template"""
        # Create template
        await prompt_manager.create_template(sample_prompt_template)
        
        # Delete template
        result = await prompt_manager.delete_template(sample_prompt_template.template_id)
        assert result["success"] is True
        
        # Verify deletion
        deleted_template = await prompt_manager.get_template(sample_prompt_template.template_id)
        assert deleted_template is None
    
    @pytest.mark.asyncio
    async def test_list_templates_by_category(self, prompt_manager):
        """Test listing templates by category"""
        # Create multiple templates with different categories
        templates = []
        for category in [PromptCategory.CONTENT_CREATION, PromptCategory.MARKETING, PromptCategory.TECHNICAL]:
            template = PromptTemplate(
                template_id=str(uuid.uuid4()),
                name=f"Test {category.value} Template",
                description=f"Test template for {category.value}",
                category=category,
                prompt_type=PromptType.INSTRUCTION,
                template_text="Test template text",
                variables=[],
                metadata={},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            templates.append(template)
            await prompt_manager.create_template(template)
        
        # Test filtering by category
        content_templates = await prompt_manager.list_templates(
            category=PromptCategory.CONTENT_CREATION
        )
        assert len(content_templates) == 1
        assert content_templates[0].category == PromptCategory.CONTENT_CREATION
        
        marketing_templates = await prompt_manager.list_templates(
            category=PromptCategory.MARKETING
        )
        assert len(marketing_templates) == 1
        assert marketing_templates[0].category == PromptCategory.MARKETING
    
    # ===== PROMPT GENERATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_generate_prompt_from_template(self, prompt_manager, sample_prompt_template, sample_variables):
        """Test generating a prompt from template with variables"""
        # Create template
        await prompt_manager.create_template(sample_prompt_template)
        
        # Generate prompt
        result = await prompt_manager.generate_prompt(
            template_id=sample_prompt_template.template_id,
            variables=sample_variables
        )
        
        assert result["success"] is True
        assert "prompt" in result
        
        expected_prompt = "Create a blog_post about Artificial Intelligence in Music Production for music producers and AI enthusiasts with tone professional"
        assert result["prompt"] == expected_prompt
    
    @pytest.mark.asyncio
    async def test_generate_prompt_with_missing_required_variable_fails(self, prompt_manager, sample_prompt_template):
        """Test that generating prompt fails when required variables are missing"""
        await prompt_manager.create_template(sample_prompt_template)
        
        # Missing required 'content_type' variable
        incomplete_variables = {
            "topic": "AI Music",
            "target_audience": "musicians"
        }
        
        result = await prompt_manager.generate_prompt(
            template_id=sample_prompt_template.template_id,
            variables=incomplete_variables
        )
        
        assert result["success"] is False
        assert "required" in result["error"].lower()
        assert "content_type" in result["error"]
    
    @pytest.mark.asyncio
    async def test_generate_prompt_with_invalid_variable_value_fails(self, prompt_manager, sample_prompt_template):
        """Test that generating prompt fails with invalid variable values"""
        await prompt_manager.create_template(sample_prompt_template)
        
        # Invalid content_type (not in choices)
        invalid_variables = {
            "content_type": "invalid_type",
            "topic": "AI Music",
            "target_audience": "musicians",
            "tone": "professional"
        }
        
        result = await prompt_manager.generate_prompt(
            template_id=sample_prompt_template.template_id,
            variables=invalid_variables
        )
        
        assert result["success"] is False
        assert "validation" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_generate_prompt_with_default_values(self, prompt_manager, sample_prompt_template):
        """Test generating prompt using default values for optional variables"""
        await prompt_manager.create_template(sample_prompt_template)
        
        # Only provide required variables, let defaults fill in optional ones
        minimal_variables = {
            "content_type": "blog_post",
            "topic": "AI in Music"
        }
        
        result = await prompt_manager.generate_prompt(
            template_id=sample_prompt_template.template_id,
            variables=minimal_variables
        )
        
        assert result["success"] is True
        expected_prompt = "Create a blog_post about AI in Music for general public with tone professional"
        assert result["prompt"] == expected_prompt
    
    # ===== VARIABLE VALIDATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_validate_variables_success(self, prompt_manager, sample_prompt_template, sample_variables):
        """Test successful variable validation"""
        await prompt_manager.create_template(sample_prompt_template)
        
        validation_result = await prompt_manager.validate_variables(
            template_id=sample_prompt_template.template_id,
            variables=sample_variables
        )
        
        assert validation_result["valid"] is True
        assert validation_result["errors"] == []
    
    @pytest.mark.asyncio
    async def test_validate_variables_with_errors(self, prompt_manager, sample_prompt_template):
        """Test variable validation with multiple errors"""
        await prompt_manager.create_template(sample_prompt_template)
        
        # Variables with multiple validation errors
        invalid_variables = {
            "content_type": "invalid_choice",  # Invalid choice
            "topic": "AI",  # Too short (min_length: 3)
            "target_audience": "a" * 200,  # Potentially too long
            "tone": "invalid_tone"  # Invalid choice
        }
        
        validation_result = await prompt_manager.validate_variables(
            template_id=sample_prompt_template.template_id,
            variables=invalid_variables
        )
        
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        
        # Check specific error types
        error_messages = [error["message"] for error in validation_result["errors"]]
        assert any("content_type" in msg for msg in error_messages)
        assert any("tone" in msg for msg in error_messages)
    
    # ===== PERFORMANCE AND ANALYTICS TESTS =====
    
    @pytest.mark.asyncio
    async def test_prompt_performance_tracking(self, prompt_manager, sample_prompt_template, sample_variables):
        """Test performance tracking for prompt generation"""
        await prompt_manager.create_template(sample_prompt_template)
        
        # Generate prompt multiple times to build performance data
        for i in range(5):
            result = await prompt_manager.generate_prompt(
                template_id=sample_prompt_template.template_id,
                variables=sample_variables,
                track_performance=True
            )
            assert result["success"] is True
            
            # Simulate success/failure feedback
            await prompt_manager.record_prompt_feedback(
                template_id=sample_prompt_template.template_id,
                prompt_id=result.get("prompt_id"),
                success=i < 4,  # 4 successes, 1 failure
                performance_score=0.8 + (i * 0.05)
            )
        
        # Check performance metrics
        metrics = await prompt_manager.get_template_metrics(sample_prompt_template.template_id)
        assert metrics is not None
        assert metrics["usage_count"] == 5
        assert 0.7 <= metrics["success_rate"] <= 0.9  # 4/5 = 0.8
        assert metrics["average_performance_score"] > 0.7
    
    @pytest.mark.asyncio
    async def test_prompt_optimization_recommendations(self, prompt_manager, sample_prompt_template):
        """Test getting optimization recommendations for prompts"""
        await prompt_manager.create_template(sample_prompt_template)
        
        # Simulate low-performing prompt
        for i in range(10):
            result = await prompt_manager.generate_prompt(
                template_id=sample_prompt_template.template_id,
                variables={"content_type": "blog_post", "topic": f"Topic {i}"},
                track_performance=True
            )
            
            # Record poor performance
            await prompt_manager.record_prompt_feedback(
                template_id=sample_prompt_template.template_id,
                prompt_id=result.get("prompt_id"),
                success=i < 3,  # 30% success rate
                performance_score=0.3 + (i * 0.02)
            )
        
        # Get optimization recommendations
        recommendations = await prompt_manager.get_optimization_recommendations(
            sample_prompt_template.template_id
        )
        
        assert recommendations is not None
        assert len(recommendations) > 0
        assert any("performance" in rec.get("type", "").lower() for rec in recommendations)
    
    # ===== CACHING TESTS =====
    
    @pytest.mark.asyncio
    async def test_prompt_caching(self, prompt_manager, sample_prompt_template, sample_variables):
        """Test prompt generation caching"""
        await prompt_manager.create_template(sample_prompt_template)
        
        # First generation (should cache)
        start_time = datetime.now()
        result1 = await prompt_manager.generate_prompt(
            template_id=sample_prompt_template.template_id,
            variables=sample_variables,
            use_cache=True
        )
        first_duration = (datetime.now() - start_time).total_seconds()
        
        # Second generation (should use cache)
        start_time = datetime.now()
        result2 = await prompt_manager.generate_prompt(
            template_id=sample_prompt_template.template_id,
            variables=sample_variables,
            use_cache=True
        )
        second_duration = (datetime.now() - start_time).total_seconds()
        
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["prompt"] == result2["prompt"]
        
        # Second call should be faster due to caching
        assert second_duration < first_duration
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self, prompt_manager, sample_prompt_template, sample_variables):
        """Test cache invalidation when template is updated"""
        await prompt_manager.create_template(sample_prompt_template)
        
        # Generate and cache prompt
        result1 = await prompt_manager.generate_prompt(
            template_id=sample_prompt_template.template_id,
            variables=sample_variables,
            use_cache=True
        )
        
        # Update template (should invalidate cache)
        sample_prompt_template.template_text = "Updated: " + sample_prompt_template.template_text
        await prompt_manager.update_template(sample_prompt_template)
        
        # Generate again (should use new template, not cache)
        result2 = await prompt_manager.generate_prompt(
            template_id=sample_prompt_template.template_id,
            variables=sample_variables,
            use_cache=True
        )
        
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["prompt"] != result2["prompt"]
        assert result2["prompt"].startswith("Updated:")
    
    # ===== ERROR HANDLING TESTS =====
    
    @pytest.mark.asyncio
    async def test_nonexistent_template_error(self, prompt_manager):
        """Test error handling for nonexistent template"""
        fake_id = str(uuid.uuid4())
        
        result = await prompt_manager.generate_prompt(
            template_id=fake_id,
            variables={}
        )
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_malformed_template_error(self, prompt_manager):
        """Test error handling for malformed template"""
        malformed_template = PromptTemplate(
            template_id=str(uuid.uuid4()),
            name="Malformed Template",
            description="Template with malformed variables",
            category=PromptCategory.CONTENT_CREATION,
            prompt_type=PromptType.INSTRUCTION,
            template_text="Create {unclosed_variable content",  # Malformed variable syntax
            variables=[],
            metadata={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        result = await prompt_manager.create_template(malformed_template)
        assert result["success"] is False
        assert "malformed" in result["error"].lower() or "syntax" in result["error"].lower()
    
    # ===== CONCURRENT ACCESS TESTS =====
    
    @pytest.mark.asyncio
    async def test_concurrent_template_access(self, prompt_manager, sample_variables):
        """Test concurrent access to template generation"""
        # Create multiple templates
        templates = []
        for i in range(3):
            template = PromptTemplate(
                template_id=str(uuid.uuid4()),
                name=f"Concurrent Test Template {i}",
                description=f"Template {i} for concurrent testing",
                category=PromptCategory.CONTENT_CREATION,
                prompt_type=PromptType.INSTRUCTION,
                template_text=f"Template {i}: Create {{content_type}} about {{topic}}",
                variables=[
                    PromptVariable(name="content_type", type="string", description="Content type", required=True),
                    PromptVariable(name="topic", type="string", description="Topic", required=True)
                ],
                metadata={},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            templates.append(template)
            await prompt_manager.create_template(template)
        
        # Generate prompts concurrently
        async def generate_prompt_task(template_id):
            return await prompt_manager.generate_prompt(
                template_id=template_id,
                variables={"content_type": "article", "topic": "AI Technology"}
            )
        
        tasks = [generate_prompt_task(template.template_id) for template in templates]
        results = await asyncio.gather(*tasks)
        
        # Verify all generations succeeded
        for i, result in enumerate(results):
            assert result["success"] is True
            assert f"Template {i}" in result["prompt"]
    
    # ===== MEMORY AND RESOURCE MANAGEMENT TESTS =====
    
    @pytest.mark.asyncio
    async def test_memory_management_large_templates(self, prompt_manager):
        """Test memory management with large number of templates"""
        template_ids = []
        
        # Create many templates
        for i in range(100):
            template = PromptTemplate(
                template_id=str(uuid.uuid4()),
                name=f"Large Scale Template {i}",
                description=f"Template {i} for memory testing",
                category=PromptCategory.CONTENT_CREATION,
                prompt_type=PromptType.INSTRUCTION,
                template_text="Create content about {topic}",
                variables=[
                    PromptVariable(name="topic", type="string", description="Topic", required=True)
                ],
                metadata={"index": i},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            result = await prompt_manager.create_template(template)
            if result["success"]:
                template_ids.append(template.template_id)
        
        # Verify we can still access templates efficiently
        assert len(template_ids) == 100
        
        # Test listing templates doesn't cause memory issues
        all_templates = await prompt_manager.list_templates()
        assert len(all_templates) >= 100
        
        # Test cleanup
        for template_id in template_ids[:50]:  # Clean up half
            await prompt_manager.delete_template(template_id)
        
        remaining_templates = await prompt_manager.list_templates()
        assert len(remaining_templates) >= 50
    
    # ===== INTEGRATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, prompt_manager):
        """Test complete workflow from template creation to prompt generation"""
        # Step 1: Create sophisticated template
        complex_template = PromptTemplate(
            template_id=str(uuid.uuid4()),
            name="Complex Content Creation Template",
            description="Multi-variable template for sophisticated content creation",
            category=PromptCategory.CONTENT_CREATION,
            prompt_type=PromptType.INSTRUCTION,
            template_text="""
            Create a {content_format} about {main_topic} targeting {audience}.
            
            Requirements:
            - Tone: {tone}
            - Length: {length}
            - Include: {include_elements}
            - SEO Keywords: {seo_keywords}
            - Call-to-action: {cta}
            
            Additional context: {additional_context}
            """.strip(),
            variables=[
                PromptVariable(name="content_format", type="string", description="Content format", required=True,
                              validation_rules={"choices": ["blog_post", "video_script", "podcast_outline", "social_media_series"]}),
                PromptVariable(name="main_topic", type="string", description="Main topic", required=True,
                              validation_rules={"min_length": 5, "max_length": 100}),
                PromptVariable(name="audience", type="string", description="Target audience", required=True),
                PromptVariable(name="tone", type="string", description="Content tone", required=False, default_value="professional",
                              validation_rules={"choices": ["professional", "casual", "friendly", "authoritative", "conversational"]}),
                PromptVariable(name="length", type="string", description="Content length", required=False, default_value="medium",
                              validation_rules={"choices": ["short", "medium", "long", "comprehensive"]}),
                PromptVariable(name="include_elements", type="string", description="Elements to include", required=False, default_value="examples and statistics"),
                PromptVariable(name="seo_keywords", type="string", description="SEO keywords", required=False, default_value="relevant industry terms"),
                PromptVariable(name="cta", type="string", description="Call-to-action", required=False, default_value="engage with content"),
                PromptVariable(name="additional_context", type="string", description="Additional context", required=False, default_value="None")
            ],
            metadata={"complexity": "high", "category": "content_creation", "version": "2.0"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Step 2: Create template
        create_result = await prompt_manager.create_template(complex_template)
        assert create_result["success"] is True
        
        # Step 3: Validate comprehensive variables
        comprehensive_variables = {
            "content_format": "blog_post",
            "main_topic": "Advanced AI Applications in Digital Music Production",
            "audience": "music producers, audio engineers, and AI enthusiasts",
            "tone": "professional",
            "length": "comprehensive",
            "include_elements": "technical examples, industry case studies, and performance benchmarks",
            "seo_keywords": "AI music production, machine learning audio, automated mastering",
            "cta": "download our free AI music production guide",
            "additional_context": "Focus on practical applications and real-world implementation"
        }
        
        validation_result = await prompt_manager.validate_variables(
            template_id=complex_template.template_id,
            variables=comprehensive_variables
        )
        assert validation_result["valid"] is True
        
        # Step 4: Generate sophisticated prompt
        generation_result = await prompt_manager.generate_prompt(
            template_id=complex_template.template_id,
            variables=comprehensive_variables,
            track_performance=True
        )
        assert generation_result["success"] is True
        
        generated_prompt = generation_result["prompt"]
        assert "blog_post" in generated_prompt
        assert "Advanced AI Applications in Digital Music Production" in generated_prompt
        assert "music producers, audio engineers, and AI enthusiasts" in generated_prompt
        assert "comprehensive" in generated_prompt
        assert "AI music production, machine learning audio, automated mastering" in generated_prompt
        
        # Step 5: Record feedback and get analytics
        await prompt_manager.record_prompt_feedback(
            template_id=complex_template.template_id,
            prompt_id=generation_result.get("prompt_id"),
            success=True,
            performance_score=0.95
        )
        
        metrics = await prompt_manager.get_template_metrics(complex_template.template_id)
        assert metrics["usage_count"] >= 1
        assert metrics["success_rate"] == 1.0
        assert metrics["average_performance_score"] >= 0.9
        
        # Step 6: Test optimization recommendations
        recommendations = await prompt_manager.get_optimization_recommendations(
            complex_template.template_id
        )
        assert recommendations is not None  # Should return recommendations even for good templates
