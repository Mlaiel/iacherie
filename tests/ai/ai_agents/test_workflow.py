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

"""
Comprehensive Tests for Workflow Management System

Industrial-grade testing for workflow orchestration, task coordination,
pipeline management, and automated process execution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import logging
import json
import uuid
from enum import Enum

from ai.ai_agents.workflow import (
    WorkflowEngine,
    WorkflowDefinition,
    WorkflowExecution,
    TaskNode,
    WorkflowStatus,
    TaskStatus,
    WorkflowConfig,
    ConditionalBranch,
    ParallelExecution,
    SequentialExecution
)

logger = logging.getLogger(__name__)


class TestWorkflowDefinition:
    """
Test workflow definition and structure"""
    
    def test_workflow_creation(self):
        """
Test creating workflow definitions"""
        workflow = WorkflowDefinition(
            workflow_id="test_workflow_001",
            name="Test Content Creation Workflow",
            description="Complete content creation and publishing pipeline",
            version="1.0"
        )
        
        assert workflow.workflow_id == "test_workflow_001"
        assert workflow.name == "Test Content Creation Workflow"
        assert workflow.version == "1.0"
        assert workflow.created_at is not None
        assert len(workflow.tasks) == 0
    
    def test_task_node_creation(self):
        """Test creating task nodes"""
        task = TaskNode(
            task_id="generate_content",
            task_type="content_generation",
            agent_type="ContentCreatorAgent",
            parameters={
                "content_type": "video",
                "duration": 60,
                "style": "educational"
            },
            timeout=300
        )
        
        assert task.task_id == "generate_content"
        assert task.task_type == "content_generation"
        assert task.agent_type == "ContentCreatorAgent"
        assert task.parameters["content_type"] == "video"
        assert task.timeout == 300
        assert task.status == TaskStatus.PENDING
    
    def test_workflow_task_addition(self):
        """Test adding tasks to workflow"""
        workflow = WorkflowDefinition(
            workflow_id="content_workflow",
            name="Content Workflow"
        )
        
        # Add sequential tasks
        content_task = TaskNode(
            task_id="create_content",
            task_type="content_generation",
            agent_type="ContentCreatorAgent"
        )
        
        optimization_task = TaskNode(
            task_id="optimize_content",
            task_type="content_optimization",
            agent_type="EngagementSpecialistAgent",
            dependencies=["create_content"]
        )
        
        publishing_task = TaskNode(
            task_id="publish_content",
            task_type="content_publishing",
            agent_type="SocialMediaManagerAgent",
            dependencies=["optimize_content"]
        )
        
        workflow.add_task(content_task)
        workflow.add_task(optimization_task)
        workflow.add_task(publishing_task)
        
        assert len(workflow.tasks) == 3
        assert workflow.get_task("create_content") is not None
        assert workflow.get_task("optimize_content").dependencies == ["create_content"]
        assert workflow.get_task("publish_content").dependencies == ["optimize_content"]
    
    def test_conditional_branching(self):
        """Test conditional workflow branching"""
        workflow = WorkflowDefinition(
            workflow_id="conditional_workflow",
            name="Conditional Workflow"
        )
        
        # Content analysis task
        analysis_task = TaskNode(
            task_id="analyze_content",
            task_type="content_analysis",
            agent_type="AnalyticsAgent"
        )
        
        # Conditional branches based on content score
        high_quality_branch = ConditionalBranch(
            condition="content_score >= 0.8",
            tasks=[
                TaskNode(
                    task_id="premium_promotion",
                    task_type="premium_promotion",
                    agent_type="SocialMediaManagerAgent"
                )
            ]
        )
        
        low_quality_branch = ConditionalBranch(
            condition="content_score < 0.8",
            tasks=[
                TaskNode(
                    task_id="content_enhancement",
                    task_type="content_enhancement",
                    agent_type="ContentCreatorAgent"
                ),
                TaskNode(
                    task_id="standard_promotion",
                    task_type="standard_promotion",
                    agent_type="SocialMediaManagerAgent"
                )
            ]
        )
        
        workflow.add_task(analysis_task)
        workflow.add_conditional_branch("analyze_content", high_quality_branch)
        workflow.add_conditional_branch("analyze_content", low_quality_branch)
        
        assert len(workflow.conditional_branches) == 1
        assert "analyze_content" in workflow.conditional_branches
        assert len(workflow.conditional_branches["analyze_content"]) == 2
    
    def test_parallel_execution(self):
        """Test parallel task execution definition"""
        workflow = WorkflowDefinition(
            workflow_id="parallel_workflow",
            name="Parallel Workflow"
        )
        
        # Content creation task
        content_task = TaskNode(
            task_id="create_base_content",
            task_type="content_generation",
            agent_type="ContentCreatorAgent"
        )
        
        # Parallel processing tasks
        parallel_tasks = ParallelExecution(
            execution_id="parallel_optimization",
            tasks=[
                TaskNode(
                    task_id="audio_enhancement",
                    task_type="audio_processing",
                    agent_type="AudioSpecialistAgent",
                    dependencies=["create_base_content"]
                ),
                TaskNode(
                    task_id="visual_enhancement",
                    task_type="visual_processing",
                    agent_type="ContentCreatorAgent",
                    dependencies=["create_base_content"]
                ),
                TaskNode(
                    task_id="hashtag_optimization",
                    task_type="hashtag_generation",
                    agent_type="EngagementSpecialistAgent",
                    dependencies=["create_base_content"]
                )
            ]
        )
        
        # Final assembly task
        assembly_task = TaskNode(
            task_id="assemble_final_content",
            task_type="content_assembly",
            agent_type="ContentCreatorAgent",
            dependencies=["parallel_optimization"]
        )
        
        workflow.add_task(content_task)
        workflow.add_parallel_execution(parallel_tasks)
        workflow.add_task(assembly_task)
        
        assert len(workflow.parallel_executions) == 1
        assert "parallel_optimization" in workflow.parallel_executions
        assert len(workflow.parallel_executions["parallel_optimization"].tasks) == 3
    
    def test_workflow_validation(self):
        """Test workflow definition validation"""
        workflow = WorkflowDefinition(
            workflow_id="validation_workflow",
            name="Validation Test Workflow"
        )
        
        # Add valid workflow structure
        task1 = TaskNode(task_id="task1", task_type="type1", agent_type="Agent1")
        task2 = TaskNode(task_id="task2", task_type="type2", agent_type="Agent2", dependencies=["task1"])
        task3 = TaskNode(task_id="task3", task_type="type3", agent_type="Agent3", dependencies=["task2"])
        
        workflow.add_task(task1)
        workflow.add_task(task2)
        workflow.add_task(task3)
        
        # Validate workflow
        validation_result = workflow.validate()
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
        
        # Add circular dependency
        task1.dependencies = ["task3"]  # Creates circular dependency
        
        validation_result = workflow.validate()
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        assert any("circular dependency" in error.lower() for error in validation_result["errors"])


class TestWorkflowEngine:
    """Test workflow engine functionality"""
    
    @pytest.fixture
    async def workflow_engine(self) -> WorkflowEngine:
        """
Create workflow engine for testing"""
        config = WorkflowConfig(
            max_concurrent_workflows=10,
            max_concurrent_tasks=20,
            default_timeout=300,
            enable_persistence=False,
            enable_monitoring=True
        )
        engine = WorkflowEngine(config)
        await engine.initialize()
        
        yield engine
        
        await engine.shutdown()
    
    @pytest.fixture
    def sample_content_workflow(self) -> WorkflowDefinition:
        """
Create sample content creation workflow"""
        workflow = WorkflowDefinition(
            workflow_id="sample_content_workflow",
            name="Sample Content Creation Workflow",
            description="End-to-end content creation and publishing"
        )
        
        # Define workflow tasks
        tasks = [
            TaskNode(
                task_id="content_planning",
                task_type="content_planning",
                agent_type="ContentCreatorAgent",
                parameters={
                    "content_type": "video",
                    "target_audience": "tech_enthusiasts",
                    "platform": "tiktok"
                }
            ),
            TaskNode(
                task_id="content_generation",
                task_type="content_generation",
                agent_type="ContentCreatorAgent",
                dependencies=["content_planning"],
                parameters={
                    "style": "educational",
                    "duration": 60
                }
            ),
            TaskNode(
                task_id="content_optimization",
                task_type="content_optimization",
                agent_type="EngagementSpecialistAgent",
                dependencies=["content_generation"]
            ),
            TaskNode(
                task_id="content_publishing",
                task_type="content_publishing",
                agent_type="SocialMediaManagerAgent",
                dependencies=["content_optimization"]
            )
        ]
        
        for task in tasks:
            workflow.add_task(task)
        
        return workflow
    
    async def test_engine_initialization(self):
        """Test workflow engine initialization"""
        config = WorkflowConfig()
        engine = WorkflowEngine(config)
        
        assert not engine.initialized
        assert engine.active_workflows == 0
        
        await engine.initialize()
        assert engine.initialized
        
        await engine.shutdown()
        assert not engine.initialized
    
    async def test_workflow_registration(self, workflow_engine, sample_content_workflow):
        """
Test workflow registration"""
        # Register workflow
        registration_result = await workflow_engine.register_workflow(sample_content_workflow)
        
        assert registration_result["success"] is True
        assert registration_result["workflow_id"] == sample_content_workflow.workflow_id
        
        # Verify workflow is registered
        registered_workflows = await workflow_engine.get_registered_workflows()
        assert sample_content_workflow.workflow_id in registered_workflows
        
        # Get workflow details
        workflow_details = await workflow_engine.get_workflow_definition(sample_content_workflow.workflow_id)
        assert workflow_details is not None
        assert workflow_details.name == sample_content_workflow.name
    
    async def test_workflow_execution(self, workflow_engine, sample_content_workflow):
        """Test workflow execution"""
        # Register workflow
        await workflow_engine.register_workflow(sample_content_workflow)
        
        # Start execution
        execution_request = {
            "workflow_id": sample_content_workflow.workflow_id,
            "execution_name": "Test Content Creation",
            "input_parameters": {
                "target_platform": "tiktok",
                "content_theme": "AI technology"
            }
        }
        
        execution_result = await workflow_engine.start_workflow_execution(execution_request)
        
        assert execution_result["success"] is True
        assert "execution_id" in execution_result
        
        execution_id = execution_result["execution_id"]
        
        # Monitor execution progress
        execution_status = await workflow_engine.get_execution_status(execution_id)
        assert execution_status["status"] in [WorkflowStatus.RUNNING, WorkflowStatus.COMPLETED]
        assert "current_task" in execution_status
        assert "progress" in execution_status
        
        # Wait for completion (with timeout)
        max_wait_time = 60  # seconds
        wait_time = 0
        while wait_time < max_wait_time:
            status = await workflow_engine.get_execution_status(execution_id)
            if status["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                break
            await asyncio.sleep(1)
            wait_time += 1
        
        # Verify final status
        final_status = await workflow_engine.get_execution_status(execution_id)
        assert final_status["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]
        
        if final_status["status"] == WorkflowStatus.COMPLETED:
            assert "output" in final_status
            assert final_status["progress"] == 100
    
    async def test_parallel_task_execution(self, workflow_engine):
        """Test parallel task execution"""
        # Create workflow with parallel tasks
        workflow = WorkflowDefinition(
            workflow_id="parallel_test_workflow",
            name="Parallel Execution Test"
        )
        
        # Base task
        base_task = TaskNode(
            task_id="base_task",
            task_type="base_processing",
            agent_type="BaseAgent"
        )
        
        # Parallel tasks
        parallel_execution = ParallelExecution(
            execution_id="parallel_processing",
            tasks=[
                TaskNode(
                    task_id="parallel_task_1",
                    task_type="processing_1",
                    agent_type="Agent1",
                    dependencies=["base_task"]
                ),
                TaskNode(
                    task_id="parallel_task_2",
                    task_type="processing_2",
                    agent_type="Agent2",
                    dependencies=["base_task"]
                ),
                TaskNode(
                    task_id="parallel_task_3",
                    task_type="processing_3",
                    agent_type="Agent3",
                    dependencies=["base_task"]
                )
            ]
        )
        
        # Final task
        final_task = TaskNode(
            task_id="final_task",
            task_type="final_processing",
            agent_type="FinalAgent",
            dependencies=["parallel_processing"]
        )
        
        workflow.add_task(base_task)
        workflow.add_parallel_execution(parallel_execution)
        workflow.add_task(final_task)
        
        # Register and execute
        await workflow_engine.register_workflow(workflow)
        
        execution_result = await workflow_engine.start_workflow_execution({
            "workflow_id": workflow.workflow_id,
            "execution_name": "Parallel Test Execution"
        })
        
        assert execution_result["success"] is True
        
        execution_id = execution_result["execution_id"]
        
        # Monitor parallel execution
        max_wait_time = 30
        wait_time = 0
        parallel_tasks_started = False
        
        while wait_time < max_wait_time:
            status = await workflow_engine.get_execution_status(execution_id)
            
            if "parallel_tasks" in status:
                parallel_tasks_started = True
                parallel_tasks = status["parallel_tasks"]
                assert len(parallel_tasks) == 3
                
                # Verify all parallel tasks are running or completed
                for task_status in parallel_tasks.values():
                    assert task_status in [TaskStatus.RUNNING, TaskStatus.COMPLETED, TaskStatus.PENDING]
            
            if status["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                break
                
            await asyncio.sleep(1)
            wait_time += 1
        
        assert parallel_tasks_started
    
    async def test_conditional_workflow_execution(self, workflow_engine):
        """Test conditional workflow execution"""
        # Create workflow with conditional branches
        workflow = WorkflowDefinition(
            workflow_id="conditional_test_workflow",
            name="Conditional Execution Test"
        )
        
        # Analysis task
        analysis_task = TaskNode(
            task_id="content_analysis",
            task_type="content_analysis",
            agent_type="AnalyticsAgent"
        )
        
        # High quality branch
        high_quality_branch = ConditionalBranch(
            condition="analysis_result.quality_score >= 0.8",
            tasks=[
                TaskNode(
                    task_id="premium_processing",
                    task_type="premium_processing",
                    agent_type="PremiumAgent"
                )
            ]
        )
        
        # Standard quality branch
        standard_branch = ConditionalBranch(
            condition="analysis_result.quality_score < 0.8",
            tasks=[
                TaskNode(
                    task_id="standard_processing",
                    task_type="standard_processing",
                    agent_type="StandardAgent"
                )
            ]
        )
        
        workflow.add_task(analysis_task)
        workflow.add_conditional_branch("content_analysis", high_quality_branch)
        workflow.add_conditional_branch("content_analysis", standard_branch)
        
        # Register and execute
        await workflow_engine.register_workflow(workflow)
        
        execution_result = await workflow_engine.start_workflow_execution({
            "workflow_id": workflow.workflow_id,
            "execution_name": "Conditional Test Execution",
            "input_parameters": {
                "test_quality_score": 0.9  # Should trigger high quality branch
            }
        })
        
        assert execution_result["success"] is True
        
        execution_id = execution_result["execution_id"]
        
        # Monitor conditional execution
        max_wait_time = 30
        wait_time = 0
        condition_evaluated = False
        
        while wait_time < max_wait_time:
            status = await workflow_engine.get_execution_status(execution_id)
            
            if "conditional_branches" in status:
                condition_evaluated = True
                branches = status["conditional_branches"]
                # Verify correct branch was selected
                assert "content_analysis" in branches
            
            if status["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                break
                
            await asyncio.sleep(1)
            wait_time += 1
        
        assert condition_evaluated
    
    async def test_workflow_error_handling(self, workflow_engine):
        """Test workflow error handling and recovery"""
        # Create workflow with failing task
        workflow = WorkflowDefinition(
            workflow_id="error_test_workflow",
            name="Error Handling Test"
        )
        
        # Normal task
        normal_task = TaskNode(
            task_id="normal_task",
            task_type="normal_processing",
            agent_type="NormalAgent"
        )
        
        # Failing task
        failing_task = TaskNode(
            task_id="failing_task",
            task_type="failing_processing",
            agent_type="FailingAgent",
            dependencies=["normal_task"],
            retry_attempts=2
        )
        
        # Recovery task
        recovery_task = TaskNode(
            task_id="recovery_task",
            task_type="recovery_processing",
            agent_type="RecoveryAgent",
            dependencies=["failing_task"],
            continue_on_failure=True
        )
        
        workflow.add_task(normal_task)
        workflow.add_task(failing_task)
        workflow.add_task(recovery_task)
        
        # Register and execute
        await workflow_engine.register_workflow(workflow)
        
        execution_result = await workflow_engine.start_workflow_execution({
            "workflow_id": workflow.workflow_id,
            "execution_name": "Error Handling Test"
        })
        
        assert execution_result["success"] is True
        
        execution_id = execution_result["execution_id"]
        
        # Monitor error handling
        max_wait_time = 45
        wait_time = 0
        error_detected = False
        recovery_attempted = False
        
        while wait_time < max_wait_time:
            status = await workflow_engine.get_execution_status(execution_id)
            
            if "failed_tasks" in status and len(status["failed_tasks"]) > 0:
                error_detected = True
                assert "failing_task" in status["failed_tasks"]
            
            if "retry_attempts" in status:
                recovery_attempted = True
                assert status["retry_attempts"]["failing_task"] >= 1
            
            if status["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                break
                
            await asyncio.sleep(1)
            wait_time += 1
        
        assert error_detected
        assert recovery_attempted
    
    async def test_workflow_pause_resume(self, workflow_engine, sample_content_workflow):
        """Test workflow pause and resume functionality"""
        # Register and start workflow
        await workflow_engine.register_workflow(sample_content_workflow)
        
        execution_result = await workflow_engine.start_workflow_execution({
            "workflow_id": sample_content_workflow.workflow_id,
            "execution_name": "Pause Resume Test"
        })
        
        execution_id = execution_result["execution_id"]
        
        # Wait for workflow to start
        await asyncio.sleep(2)
        
        # Pause workflow
        pause_result = await workflow_engine.pause_workflow_execution(execution_id)
        assert pause_result["success"] is True
        
        # Verify paused status
        status = await workflow_engine.get_execution_status(execution_id)
        assert status["status"] == WorkflowStatus.PAUSED
        
        # Resume workflow
        resume_result = await workflow_engine.resume_workflow_execution(execution_id)
        assert resume_result["success"] is True
        
        # Verify resumed status
        status = await workflow_engine.get_execution_status(execution_id)
        assert status["status"] in [WorkflowStatus.RUNNING, WorkflowStatus.COMPLETED]
    
    async def test_workflow_cancellation(self, workflow_engine, sample_content_workflow):
        """Test workflow cancellation"""
        # Register and start workflow
        await workflow_engine.register_workflow(sample_content_workflow)
        
        execution_result = await workflow_engine.start_workflow_execution({
            "workflow_id": sample_content_workflow.workflow_id,
            "execution_name": "Cancellation Test"
        })
        
        execution_id = execution_result["execution_id"]
        
        # Wait for workflow to start
        await asyncio.sleep(1)
        
        # Cancel workflow
        cancel_result = await workflow_engine.cancel_workflow_execution(execution_id)
        assert cancel_result["success"] is True
        
        # Verify cancelled status
        status = await workflow_engine.get_execution_status(execution_id)
        assert status["status"] == WorkflowStatus.CANCELLED
        
        # Verify cancellation reason
        assert "cancellation_reason" in status
    
    async def test_concurrent_workflow_executions(self, workflow_engine, sample_content_workflow):
        """Test concurrent workflow executions"""
        # Register workflow
        await workflow_engine.register_workflow(sample_content_workflow)
        
        # Start multiple concurrent executions
        execution_tasks = []
        execution_ids = []
        
        for i in range(5):
            execution_request = {
                "workflow_id": sample_content_workflow.workflow_id,
                "execution_name": f"Concurrent Execution {i+1}",
                "input_parameters": {"execution_number": i+1}
            }
            
            task = workflow_engine.start_workflow_execution(execution_request)
            execution_tasks.append(task)
        
        # Wait for all executions to start
        execution_results = await asyncio.gather(*execution_tasks)
        
        # Verify all executions started successfully
        for result in execution_results:
            assert result["success"] is True
            execution_ids.append(result["execution_id"])
        
        # Monitor all executions
        max_wait_time = 60
        wait_time = 0
        completed_executions = 0
        
        while wait_time < max_wait_time and completed_executions < len(execution_ids):
            completed_executions = 0
            
            for execution_id in execution_ids:
                status = await workflow_engine.get_execution_status(execution_id)
                if status["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                    completed_executions += 1
            
            await asyncio.sleep(2)
            wait_time += 2
        
        # Verify executions completed
        assert completed_executions >= len(execution_ids) * 0.8  # Allow for some failures
    
    async def test_workflow_metrics(self, workflow_engine, sample_content_workflow):
        """Test workflow execution metrics"""
        # Register and execute workflow
        await workflow_engine.register_workflow(sample_content_workflow)
        
        execution_result = await workflow_engine.start_workflow_execution({
            "workflow_id": sample_content_workflow.workflow_id,
            "execution_name": "Metrics Test"
        })
        
        execution_id = execution_result["execution_id"]
        
        # Wait for some execution progress
        await asyncio.sleep(5)
        
        # Get execution metrics
        metrics = await workflow_engine.get_execution_metrics(execution_id)
        
        assert "execution_time" in metrics
        assert "tasks_completed" in metrics
        assert "tasks_failed" in metrics
        assert "resource_usage" in metrics
        assert "performance_stats" in metrics
        
        # Verify metric values
        assert metrics["execution_time"] >= 0
        assert metrics["tasks_completed"] >= 0
        assert metrics["tasks_failed"] >= 0
        
        # Get engine-wide metrics
        engine_metrics = await workflow_engine.get_engine_metrics()
        
        assert "total_workflows_executed" in engine_metrics
        assert "average_execution_time" in engine_metrics
        assert "success_rate" in engine_metrics
        assert "active_executions" in engine_metrics
    
    @pytest.mark.performance
    async def test_workflow_performance(self, workflow_engine, sample_content_workflow, assert_performance):
        """Test workflow execution performance"""
        # Register workflow
        await workflow_engine.register_workflow(sample_content_workflow)
        
        # Test workflow startup performance
        start_time = datetime.now(timezone.utc)
        
        execution_result = await workflow_engine.start_workflow_execution({
            "workflow_id": sample_content_workflow.workflow_id,
            "execution_name": "Performance Test"
        })
        
        startup_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        assert execution_result["success"] is True
        assert startup_time < 5.0  # Should start within 5 seconds
        
        assert_performance("workflow_startup", max_time=5.0)
    
    async def test_workflow_persistence(self, workflow_engine):
        """Test workflow state persistence"""
        # Create engine with persistence enabled
        persistent_config = WorkflowConfig(enable_persistence=True)
        persistent_engine = WorkflowEngine(persistent_config)
        await persistent_engine.initialize()
        
        try:
            # Create and register workflow
            workflow = WorkflowDefinition(
                workflow_id="persistence_test_workflow",
                name="Persistence Test"
            )
            
            task = TaskNode(
                task_id="persistent_task",
                task_type="test_task",
                agent_type="TestAgent"
            )
            
            workflow.add_task(task)
            await persistent_engine.register_workflow(workflow)
            
            # Start execution
            execution_result = await persistent_engine.start_workflow_execution({
                "workflow_id": workflow.workflow_id,
                "execution_name": "Persistence Test"
            })
            
            execution_id = execution_result["execution_id"]
            
            # Simulate engine restart by creating new engine instance
            new_engine = WorkflowEngine(persistent_config)
            await new_engine.initialize()
            
            # Verify workflow state was persisted and restored
            restored_status = await new_engine.get_execution_status(execution_id)
            assert restored_status is not None
            assert "status" in restored_status
            
            await new_engine.shutdown()
            
        finally:
            await persistent_engine.shutdown()


class TestWorkflowIntegration:
    """Integration tests for complete workflow system"""
    
    @pytest.fixture
    async def integrated_workflow_system(self):
        """
Create integrated workflow system with all components"""
        config = WorkflowConfig(
            max_concurrent_workflows=20,
            max_concurrent_tasks=50,
            enable_persistence=True,
            enable_monitoring=True,
            enable_metrics=True
        )
        
        engine = WorkflowEngine(config)
        await engine.initialize()
        
        yield {"engine": engine, "config": config}
        
        await engine.shutdown()
    
    async def test_end_to_end_content_workflow(self, integrated_workflow_system):
        """Test complete end-to-end content creation workflow"""
        engine = integrated_workflow_system["engine"]
        
        # Create comprehensive content workflow
        workflow = WorkflowDefinition(
            workflow_id="e2e_content_workflow",
            name="End-to-End Content Creation",
            description="Complete content creation, optimization, and publishing pipeline"
        )
        
        # Define comprehensive workflow structure
        planning_task = TaskNode(
            task_id="content_planning",
            task_type="content_planning",
            agent_type="ContentCreatorAgent",
            parameters={
                "research_topics": True,
                "audience_analysis": True,
                "trend_analysis": True
            }
        )
        
        content_generation = TaskNode(
            task_id="content_generation",
            task_type="content_generation",
            agent_type="ContentCreatorAgent",
            dependencies=["content_planning"]
        )
        
        # Parallel optimization tasks
        parallel_optimization = ParallelExecution(
            execution_id="content_optimization",
            tasks=[
                TaskNode(
                    task_id="audio_optimization",
                    task_type="audio_processing",
                    agent_type="AudioSpecialistAgent",
                    dependencies=["content_generation"]
                ),
                TaskNode(
                    task_id="visual_optimization",
                    task_type="visual_enhancement",
                    agent_type="ContentCreatorAgent",
                    dependencies=["content_generation"]
                ),
                TaskNode(
                    task_id="engagement_optimization",
                    task_type="engagement_analysis",
                    agent_type="EngagementSpecialistAgent",
                    dependencies=["content_generation"]
                )
            ]
        )
        
        quality_assessment = TaskNode(
            task_id="quality_assessment",
            task_type="quality_analysis",
            agent_type="AnalyticsAgent",
            dependencies=["content_optimization"]
        )
        
        # Conditional publishing branch
        high_quality_branch = ConditionalBranch(
            condition="quality_score >= 0.8",
            tasks=[
                TaskNode(
                    task_id="premium_publishing",
                    task_type="premium_publishing",
                    agent_type="SocialMediaManagerAgent"
                )
            ]
        )
        
        standard_branch = ConditionalBranch(
            condition="quality_score < 0.8",
            tasks=[
                TaskNode(
                    task_id="content_revision",
                    task_type="content_enhancement",
                    agent_type="ContentCreatorAgent"
                ),
                TaskNode(
                    task_id="standard_publishing",
                    task_type="standard_publishing",
                    agent_type="SocialMediaManagerAgent",
                    dependencies=["content_revision"]
                )
            ]
        )
        
        # Build workflow
        workflow.add_task(planning_task)
        workflow.add_task(content_generation)
        workflow.add_parallel_execution(parallel_optimization)
        workflow.add_task(quality_assessment)
        workflow.add_conditional_branch("quality_assessment", high_quality_branch)
        workflow.add_conditional_branch("quality_assessment", standard_branch)
        
        # Register and execute workflow
        registration_result = await engine.register_workflow(workflow)
        assert registration_result["success"] is True
        
        execution_result = await engine.start_workflow_execution({
            "workflow_id": workflow.workflow_id,
            "execution_name": "E2E Content Creation Test",
            "input_parameters": {
                "content_type": "video",
                "target_platform": "tiktok",
                "target_audience": "tech_enthusiasts",
                "content_theme": "AI innovation"
            }
        })
        
        assert execution_result["success"] is True
        execution_id = execution_result["execution_id"]
        
        # Monitor workflow execution with detailed tracking
        max_wait_time = 120  # 2 minutes
        wait_time = 0
        execution_phases = {
            "planning_completed": False,
            "content_generated": False,
            "parallel_optimization_started": False,
            "quality_assessed": False,
            "conditional_branch_selected": False,
            "workflow_completed": False
        }
        
        while wait_time < max_wait_time:
            status = await engine.get_execution_status(execution_id)
            
            # Track execution phases
            if status.get("completed_tasks") and "content_planning" in status["completed_tasks"]:
                execution_phases["planning_completed"] = True
            
            if status.get("completed_tasks") and "content_generation" in status["completed_tasks"]:
                execution_phases["content_generated"] = True
            
            if status.get("parallel_tasks"):
                execution_phases["parallel_optimization_started"] = True
            
            if status.get("completed_tasks") and "quality_assessment" in status["completed_tasks"]:
                execution_phases["quality_assessed"] = True
            
            if status.get("conditional_branches"):
                execution_phases["conditional_branch_selected"] = True
            
            if status["status"] == WorkflowStatus.COMPLETED:
                execution_phases["workflow_completed"] = True
                break
            elif status["status"] == WorkflowStatus.FAILED:
                break
            
            await asyncio.sleep(2)
            wait_time += 2
        
        # Verify execution phases completed
        assert execution_phases["planning_completed"]
        assert execution_phases["content_generated"]
        assert execution_phases["parallel_optimization_started"]
        assert execution_phases["quality_assessed"]
        assert execution_phases["conditional_branch_selected"]
        
        # Get final execution report
        final_status = await engine.get_execution_status(execution_id)
        final_metrics = await engine.get_execution_metrics(execution_id)
        
        # Verify final results
        assert final_status["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]
        assert final_metrics["execution_time"] > 0
        assert final_metrics["tasks_completed"] >= 4  # Minimum tasks completed
        
        if final_status["status"] == WorkflowStatus.COMPLETED:
            assert "output" in final_status
            assert final_status["progress"] == 100
