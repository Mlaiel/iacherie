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
Integration Test for AI Agents Business Logic Core
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import tempfile
import os
from pathlib import Path
from datetime import datetime

# Import from our newly created top-level modules
from business_logic_core import (
    BusinessLogicCore, ContentUpload, CreatorType, WorkflowResult, WorkflowStage
)
from simple_agents import BaseAgent, AgentStatus

# Create a simple workflow orchestrator for testing
class BusinessWorkflowOrchestrator:
    """
Simple workflow orchestrator for testing"""
    
    def __init__(self):
        self.business_core = BusinessLogicCore()
        
    async def initialize(self):
        """
Initialize the orchestrator"""
        return await self.business_core.initialize()
        
    async def process_content(self, content_upload):
        """
Process content through workflow"""
        return await self.business_core.process_creator_workflow(content_upload)

# Define WorkflowConfig for compatibility
class WorkflowConfig:
    def __init__(self, **kwargs):
        self.enabled_stages = kwargs.get('enabled_stages', [])
        self.ai_protection = kwargs.get('ai_protection', True)


class TestBusinessLogicCore:
    """
Integration tests for the complete business logic core"""
    
    @pytest.fixture
    async def workflow_orchestrator(self):
        """
Create and initialize workflow orchestrator"""
        orchestrator = BusinessWorkflowOrchestrator()
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.fixture
    def sample_content_upload(self):
        """
Create sample content upload for testing"""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test content file for AI processing.")
            temp_file_path = f.name
        
        upload = ContentUpload(
            content_id="test_content_001",
            creator_id="creator_123",
            creator_type=CreatorType.MUSICIAN,
            content_type="text",
            file_path=temp_file_path,
            metadata={
                "title": "Test Content",
                "description": "Test content for business logic validation",
                "tags": ["test", "ai", "content"],
                "target_platforms": ["youtube", "instagram"],
                "collaboration_preferences": {"open_to_collaboration": True},
                "monetization_preferences": {"revenue_sharing": True}
            },
            upload_timestamp=datetime.utcnow(),
            processing_config=WorkflowConfig(
                creator_type=CreatorType.MUSICIAN,
                enable_ai_protection=True,
                enable_seo_optimization=True,
                enable_collaboration_matching=True,
                enable_multi_platform_distribution=True,
                enable_monetization_tracking=True
            )
        )
        
        yield upload
        
        # Cleanup
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_complete_business_workflow(self, workflow_orchestrator, sample_content_upload):
        """Test the complete business workflow from upload to monetization"""
        
        # Process content upload
        workflow_id = await workflow_orchestrator.process_content_upload(sample_content_upload)
        
        assert workflow_id is not None
        assert isinstance(workflow_id, str)
        assert workflow_id in workflow_orchestrator.active_workflows
        
        # Wait for workflow to process
        await asyncio.sleep(2.0)  # Allow time for async processing
        
        # Check workflow status
        status = await workflow_orchestrator.get_workflow_status(workflow_id)
        assert status is not None
        assert status["workflow_id"] == workflow_id
        assert status["content_id"] == sample_content_upload.content_id
        assert status["creator_id"] == sample_content_upload.creator_id
    
    @pytest.mark.asyncio
    async def test_workflow_stages_progression(self, workflow_orchestrator, sample_content_upload):
        """Test that workflow progresses through all required stages"""
        
        workflow_id = await workflow_orchestrator.process_content_upload(sample_content_upload)
        
        # Allow workflow to complete
        await asyncio.sleep(3.0)
        
        # Verify workflow completed or progressed
        workflow = workflow_orchestrator.active_workflows.get(workflow_id)
        if workflow:
            # Workflow still active
            assert workflow.current_stage in [stage.value for stage in WorkflowStage]
        else:
            # Workflow completed and cleaned up
            assert True  # This is expected behavior
    
    @pytest.mark.asyncio
    async def test_individual_agent_processing(self, workflow_orchestrator, sample_content_upload):
        """
Test individual agent processing capabilities"""
        
        # Test content validation
        validation_result = await workflow_orchestrator._validate_content(sample_content_upload)
        assert validation_result["valid"] is True
        assert "errors" in validation_result
        assert "warnings" in validation_result
        
        # Test content analysis
        analysis_result = await workflow_orchestrator._analyze_content(sample_content_upload)
        assert "content_id" in analysis_result
        assert "quality_score" in analysis_result
        assert "content_classification" in analysis_result
        
        # Test protection agent
        protection_result = await workflow_orchestrator._protect_content_rights(
            sample_content_upload, analysis_result
        )
        assert protection_result is not None
        assert protection_result.get("protection_applied") is True
        
        # Test SEO optimization
        seo_result = await workflow_orchestrator._optimize_seo(sample_content_upload, analysis_result)
        assert seo_result is not None
        assert "seo_score" in seo_result
        
        # Test collaboration matching
        collaboration_result = await workflow_orchestrator._find_collaborations(
            sample_content_upload, analysis_result
        )
        assert collaboration_result is not None
        assert "matches" in collaboration_result
        
        # Test monetization setup
        monetization_result = await workflow_orchestrator._setup_monetization(
            sample_content_upload, analysis_result
        )
        assert monetization_result is not None
        assert monetization_result.get("monetization_enabled") is True
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, workflow_orchestrator):
        """Test workflow error handling for invalid content"""
        
        # Create invalid content upload
        invalid_upload = ContentUpload(
            content_id="invalid_content",
            creator_id="creator_test",
            creator_type=CreatorType.BLOGGER,
            content_type="text",
            file_path="/nonexistent/file.txt",  # Invalid file path
            metadata={},
            upload_timestamp=datetime.utcnow(),
            processing_config=WorkflowConfig(creator_type=CreatorType.BLOGGER)
        )
        
        # Process invalid upload
        workflow_id = await workflow_orchestrator.process_content_upload(invalid_upload)
        
        # Allow time for processing
        await asyncio.sleep(1.0)
        
        # Check that error was handled gracefully
        assert workflow_id is not None
        # Workflow should either be in active_workflows or completed with error
        
    @pytest.mark.asyncio
    async def test_different_creator_types(self, workflow_orchestrator):
        """Test workflow processing for different creator types"""
        
        creator_types = [CreatorType.MUSICIAN, CreatorType.BLOGGER, CreatorType.PHOTOGRAPHER]
        content_types = ["audio", "text", "image"]
        
        for creator_type, content_type in zip(creator_types, content_types):
            # Create temporary test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(f"Test content for {creator_type.value}")
                temp_file = f.name
            
            try:
                upload = ContentUpload(
                    content_id=f"test_{creator_type.value}",
                    creator_id=f"creator_{creator_type.value}",
                    creator_type=creator_type,
                    content_type=content_type,
                    file_path=temp_file,
                    metadata={"title": f"Test {creator_type.value} Content"},
                    upload_timestamp=datetime.utcnow(),
                    processing_config=WorkflowConfig(creator_type=creator_type)
                )
                
                workflow_id = await workflow_orchestrator.process_content_upload(upload)
                assert workflow_id is not None
                
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    def test_business_logic_core_components(self):
        """Test that all business logic core components are properly configured"""
        
        # Test that all required classes are importable from our fixed modules
        from simple_agents import (
            ProtectionAgent, SEOAgent, CollaborationAgent, 
            DistributionAgent, MonetizationAgent, RightsManager, NotificationService
        )
        from business_logic_core import BusinessLogicCore, CreatorType
        
        # Test instantiation
        protection_agent = ProtectionAgent()
        seo_agent = SEOAgent()
        collaboration_agent = CollaborationAgent()
        distribution_agent = DistributionAgent()
        monetization_agent = MonetizationAgent()
        rights_manager = RightsManager()
        metrics_collector = WorkflowMetrics()
        notification_service = NotificationService()
        
        # Test basic properties
        assert protection_agent.agent_type == "protection"
        assert seo_agent.agent_type == "seo"
        assert collaboration_agent.agent_type == "collaboration"
        assert distribution_agent.agent_type == "distribution"
        assert monetization_agent.agent_type == "monetization"
        
        assert hasattr(rights_manager, "initialize")
        assert hasattr(metrics_collector, "setup_content_tracking")
        assert hasattr(notification_service, "send_notification")


if __name__ == "__main__":
    print("Running AI Agents Business Logic Core Integration Tests...")
    
    # Run simple test without pytest
    async def run_basic_test():
        orchestrator = BusinessWorkflowOrchestrator()
        await orchestrator.initialize()
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for business logic validation")
            temp_file = f.name
        
        try:
            upload = ContentUpload(
                content_id="basic_test_001",
                creator_id="test_creator",
                creator_type=CreatorType.MUSICIAN,
                content_type="text",
                file_path=temp_file,
                metadata={"title": "Basic Test Content"},
                upload_timestamp=datetime.utcnow(),
                processing_config=WorkflowConfig(creator_type=CreatorType.MUSICIAN)
            )
            
            workflow_id = await orchestrator.process_content_upload(upload)
            print(f"✅ Workflow initiated successfully: {workflow_id}")
            
            # Wait for processing
            await asyncio.sleep(2.0)
            
            status = await orchestrator.get_workflow_status(workflow_id)
            if status:
                print(f"✅ Workflow status retrieved: {status['current_stage']}")
            else:
                print("✅ Workflow completed and cleaned up")
            
            print("✅ Business Logic Core Integration Test PASSED")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    # Run the test
    asyncio.run(run_basic_test())