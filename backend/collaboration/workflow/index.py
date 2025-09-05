"""Index Module - Workflow System Entry Point
==========================================

Centralized entry point for the AI-powered workflow system providing
quick access to all workflow orchestration components.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from . import (
    ProjectOrchestrator,
    TaskScheduler,
    MilestoneTracker,
    TimelineOptimizer,
    ResourceAllocator,
    ApprovalEngine,
    VersionController,
    QualityAssurance,
    ProgressTracker,
    DeadlineManager,
    CollaborationWorkspace
)

def get_workflow_engine(config=None):
    """Get unified workflow engine with all components"""
    return {
        'project_orchestrator': ProjectOrchestrator(config),
        'task_scheduler': TaskScheduler(config),
        'milestone_tracker': MilestoneTracker(config),
        'timeline_optimizer': TimelineOptimizer(config),
        'resource_allocator': ResourceAllocator(config),
        'approval_engine': ApprovalEngine(config),
        'version_controller': VersionController(config),
        'quality_assurance': QualityAssurance(config),
        'progress_tracker': ProgressTracker(config),
        'deadline_manager': DeadlineManager(config),
        'collaboration_workspace': CollaborationWorkspace(config)
    }

async def orchestrate_complete_project(
    project_definition: dict,
    collaborators: list,
    requirements: dict,
    workflow_config: dict = None
):
    """Orchestrate complete project workflow from start to finish"""
    engine = get_workflow_engine(workflow_config)
    
    results = {}
    
    # Step 1: Initialize project orchestration
    orchestration = await engine['project_orchestrator'].create_workflow(
        project_definition, collaborators
    )
    results['orchestration'] = orchestration
    
    # Step 2: Schedule tasks
    task_schedule = await engine['task_scheduler'].create_schedule(
        orchestration['workflow_id'], project_definition['tasks']
    )
    results['schedule'] = task_schedule
    
    # Step 3: Set up milestones
    milestones = await engine['milestone_tracker'].setup_milestones(
        orchestration['workflow_id'], project_definition['milestones']
    )
    results['milestones'] = milestones
    
    # Step 4: Optimize timeline
    optimized_timeline = await engine['timeline_optimizer'].optimize_timeline(
        orchestration['workflow_id'], requirements
    )
    results['timeline'] = optimized_timeline
    
    # Step 5: Allocate resources
    resource_allocation = await engine['resource_allocator'].allocate_resources(
        orchestration['workflow_id'], collaborators, requirements
    )
    results['resources'] = resource_allocation
    
    # Step 6: Set up approval workflows
    approval_workflows = await engine['approval_engine'].setup_approvals(
        orchestration['workflow_id'], project_definition.get('approval_rules', [])
    )
    results['approvals'] = approval_workflows
    
    # Step 7: Initialize workspace
    workspace = await engine['collaboration_workspace'].create_workspace(
        orchestration['workflow_id'], collaborators
    )
    results['workspace'] = workspace
    
    return results

async def get_project_status(project_id: str, workflow_engine=None):
    """Get comprehensive project status and analytics"""
    if not workflow_engine:
        workflow_engine = get_workflow_engine()
    
    status = {}
    
    # Progress metrics
    progress = await workflow_engine['progress_tracker'].get_project_progress(project_id)
    status['progress'] = progress
    
    # Milestone status
    milestone_status = await workflow_engine['milestone_tracker'].get_milestone_status(project_id)
    status['milestones'] = milestone_status
    
    # Timeline analysis
    timeline_analysis = await workflow_engine['timeline_optimizer'].analyze_timeline(project_id)
    status['timeline'] = timeline_analysis
    
    # Resource utilization
    resource_status = await workflow_engine['resource_allocator'].get_utilization_report(project_id)
    status['resources'] = resource_status
    
    # Quality metrics
    quality_report = await workflow_engine['quality_assurance'].get_quality_report(project_id)
    status['quality'] = quality_report
    
    # Deadline analysis
    deadline_analysis = await workflow_engine['deadline_manager'].analyze_deadlines(project_id)
    status['deadlines'] = deadline_analysis
    
    return status