"""Project management workflow system for collaborative projects

Revision ID: l8k9j0i1h2g3
Revises: k7j8i9h0g1f2
Create Date: 2025-09-05 06:55:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the project management workflow system for collaborative
projects with task management, revenue sharing automation, communication
integration, and milestone tracking.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'l8k9j0i1h2g3'
down_revision = 'k7j8i9h0g1f2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - Project management workflow system."""
    
    # Create project phase enum
    project_phase_enum = sa.Enum(
        'initiation', 'planning', 'execution', 'monitoring', 'closure',
        'pre_production', 'production', 'post_production', 'distribution',
        'marketing', 'launch', 'maintenance', 'analysis', 'optimization',
        name='project_phase'
    )
    
    # Create task status enum
    task_status_enum = sa.Enum(
        'not_started', 'in_progress', 'on_hold', 'completed', 'cancelled',
        'blocked', 'review_needed', 'approved', 'rejected', 'rework_required',
        name='task_status'
    )
    
    # Create task priority enum
    task_priority_enum = sa.Enum(
        'low', 'medium', 'high', 'urgent', 'critical',
        name='task_priority'
    )
    
    # Create resource type enum
    resource_type_enum = sa.Enum(
        'human', 'equipment', 'software', 'location', 'budget', 'service',
        'intellectual_property', 'content_asset', 'marketing_channel', 'time_slot',
        name='resource_type'
    )
    
    # Create project workflows table
    op.create_table('project_workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('collaboration_project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('collaboration_projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workflow_name', sa.String(200), nullable=False),
        sa.Column('workflow_template', sa.String(100)),
        sa.Column('current_phase', project_phase_enum, nullable=False, default='initiation'),
        sa.Column('phase_sequence', postgresql.ARRAY(sa.String(50)), nullable=False),
        sa.Column('phase_completion_status', postgresql.JSONB, nullable=False, default={}),
        sa.Column('workflow_rules', postgresql.JSONB, nullable=False, default={}),
        sa.Column('approval_requirements', postgresql.JSONB),
        sa.Column('notification_settings', postgresql.JSONB),
        sa.Column('escalation_rules', postgresql.JSONB),
        sa.Column('quality_gates', postgresql.JSONB),
        sa.Column('dependency_management', postgresql.JSONB),
        sa.Column('risk_mitigation_steps', postgresql.JSONB),
        sa.Column('communication_protocols', postgresql.JSONB),
        sa.Column('documentation_requirements', postgresql.JSONB),
        sa.Column('review_checkpoints', postgresql.JSONB),
        sa.Column('automated_triggers', postgresql.JSONB),
        sa.Column('workflow_metrics', postgresql.JSONB),
        sa.Column('is_template', sa.Boolean, nullable=False, default=False),
        sa.Column('template_category', sa.String(100)),
        sa.Column('usage_count', sa.Integer, nullable=False, default=0),
        sa.Column('success_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create project tasks table
    op.create_table('project_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_workflows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_tasks.id', ondelete='CASCADE')),
        sa.Column('task_name', sa.String(200), nullable=False),
        sa.Column('task_description', sa.Text),
        sa.Column('task_type', sa.String(50), nullable=False),
        sa.Column('status', task_status_enum, nullable=False, default='not_started'),
        sa.Column('priority', task_priority_enum, nullable=False, default='medium'),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('project_phase', project_phase_enum, nullable=False),
        sa.Column('estimated_hours', sa.Float),
        sa.Column('actual_hours', sa.Float, nullable=False, default=0.0),
        sa.Column('estimated_cost', sa.Numeric(10, 2)),
        sa.Column('actual_cost', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('progress_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('start_date', sa.DateTime),
        sa.Column('due_date', sa.DateTime),
        sa.Column('completed_date', sa.DateTime),
        sa.Column('dependencies', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), default=[]),
        sa.Column('required_skills', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('required_resources', postgresql.JSONB),
        sa.Column('deliverables', postgresql.JSONB),
        sa.Column('acceptance_criteria', postgresql.JSONB),
        sa.Column('quality_requirements', postgresql.JSONB),
        sa.Column('task_files', postgresql.ARRAY(sa.String(500)), default=[]),
        sa.Column('comments_count', sa.Integer, nullable=False, default=0),
        sa.Column('approval_required', sa.Boolean, nullable=False, default=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_at', sa.DateTime),
        sa.Column('rejection_reason', sa.Text),
        sa.Column('time_tracking', postgresql.JSONB),
        sa.Column('performance_metrics', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create resource allocation table
    op.create_table('resource_allocation',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_workflows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_tasks.id', ondelete='CASCADE')),
        sa.Column('resource_type', resource_type_enum, nullable=False),
        sa.Column('resource_name', sa.String(200), nullable=False),
        sa.Column('resource_description', sa.Text),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('allocation_percentage', sa.Float, nullable=False, default=100.0),
        sa.Column('hourly_rate', sa.Numeric(8, 2)),
        sa.Column('total_budget_allocated', sa.Numeric(15, 2)),
        sa.Column('budget_consumed', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('availability_start', sa.DateTime),
        sa.Column('availability_end', sa.DateTime),
        sa.Column('utilization_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('efficiency_score', sa.Float, nullable=False, default=0.0),
        sa.Column('resource_constraints', postgresql.JSONB),
        sa.Column('allocation_notes', sa.Text),
        sa.Column('performance_tracking', postgresql.JSONB),
        sa.Column('cost_tracking', postgresql.JSONB),
        sa.Column('skills_mapping', postgresql.JSONB),
        sa.Column('equipment_specifications', postgresql.JSONB),
        sa.Column('location_details', postgresql.JSONB),
        sa.Column('is_critical_path', sa.Boolean, nullable=False, default=False),
        sa.Column('risk_factors', postgresql.JSONB),
        sa.Column('backup_resources', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create revenue sharing automation table
    op.create_table('revenue_sharing_automation',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('collaboration_project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('collaboration_projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sharing_formula', postgresql.JSONB, nullable=False),
        sa.Column('participant_shares', postgresql.JSONB, nullable=False),
        sa.Column('contribution_weights', postgresql.JSONB, nullable=False),
        sa.Column('performance_bonuses', postgresql.JSONB),
        sa.Column('milestone_bonuses', postgresql.JSONB),
        sa.Column('quality_adjustments', postgresql.JSONB),
        sa.Column('time_based_adjustments', postgresql.JSONB),
        sa.Column('expense_deductions', postgresql.JSONB),
        sa.Column('minimum_share_guarantees', postgresql.JSONB),
        sa.Column('maximum_share_caps', postgresql.JSONB),
        sa.Column('revenue_recognition_rules', postgresql.JSONB),
        sa.Column('calculation_frequency', sa.String(20), nullable=False, default='monthly'),
        sa.Column('payment_schedule', postgresql.JSONB),
        sa.Column('tax_handling', postgresql.JSONB),
        sa.Column('dispute_resolution', postgresql.JSONB),
        sa.Column('audit_requirements', postgresql.JSONB),
        sa.Column('adjustment_mechanisms', postgresql.JSONB),
        sa.Column('automated_calculations', sa.Boolean, nullable=False, default=True),
        sa.Column('manual_override_allowed', sa.Boolean, nullable=False, default=True),
        sa.Column('transparency_level', sa.String(20), nullable=False, default='full'),
        sa.Column('historical_calculations', postgresql.JSONB),
        sa.Column('total_revenue_tracked', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('last_calculation_date', sa.DateTime),
        sa.Column('next_calculation_due', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create task communications table
    op.create_table('task_communications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message_type', sa.String(50), nullable=False),
        sa.Column('message_content', sa.Text, nullable=False),
        sa.Column('recipients', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column('thread_id', postgresql.UUID(as_uuid=True)),
        sa.Column('is_reply', sa.Boolean, nullable=False, default=False),
        sa.Column('parent_message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('task_communications.id')),
        sa.Column('attachments', postgresql.ARRAY(sa.String(500)), default=[]),
        sa.Column('priority_level', sa.String(20), nullable=False, default='normal'),
        sa.Column('requires_response', sa.Boolean, nullable=False, default=False),
        sa.Column('response_deadline', sa.DateTime),
        sa.Column('read_receipts', postgresql.JSONB),
        sa.Column('delivery_status', postgresql.JSONB),
        sa.Column('notification_sent', sa.Boolean, nullable=False, default=False),
        sa.Column('archived', sa.Boolean, nullable=False, default=False),
        sa.Column('pinned', sa.Boolean, nullable=False, default=False),
        sa.Column('tags', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('edit_history', postgresql.JSONB),
        sa.Column('reactions', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create project milestones table
    op.create_table('project_milestones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_workflows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('milestone_name', sa.String(200), nullable=False),
        sa.Column('milestone_description', sa.Text),
        sa.Column('milestone_type', sa.String(50), nullable=False),
        sa.Column('project_phase', project_phase_enum, nullable=False),
        sa.Column('target_date', sa.DateTime, nullable=False),
        sa.Column('actual_completion_date', sa.DateTime),
        sa.Column('status', sa.String(20), nullable=False, default='planned'),
        sa.Column('progress_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('associated_tasks', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), default=[]),
        sa.Column('completion_criteria', postgresql.JSONB, nullable=False),
        sa.Column('deliverables_required', postgresql.JSONB),
        sa.Column('quality_gates', postgresql.JSONB),
        sa.Column('stakeholder_approval_required', sa.Boolean, nullable=False, default=False),
        sa.Column('approvers', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), default=[]),
        sa.Column('approval_status', postgresql.JSONB),
        sa.Column('budget_checkpoint', sa.Numeric(15, 2)),
        sa.Column('budget_consumed_at_milestone', sa.Numeric(15, 2)),
        sa.Column('revenue_target', sa.Numeric(15, 2)),
        sa.Column('revenue_achieved', sa.Numeric(15, 2)),
        sa.Column('risk_assessment', postgresql.JSONB),
        sa.Column('impact_on_timeline', sa.String(50)),
        sa.Column('celebration_plan', sa.Text),
        sa.Column('lessons_learned', sa.Text),
        sa.Column('next_steps', sa.Text),
        sa.Column('milestone_dependencies', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), default=[]),
        sa.Column('automated_notifications', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create workflow analytics table
    op.create_table('workflow_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_workflows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analytics_date', sa.Date, nullable=False),
        sa.Column('total_tasks', sa.Integer, nullable=False, default=0),
        sa.Column('completed_tasks', sa.Integer, nullable=False, default=0),
        sa.Column('overdue_tasks', sa.Integer, nullable=False, default=0),
        sa.Column('blocked_tasks', sa.Integer, nullable=False, default=0),
        sa.Column('average_task_completion_time', sa.Float, nullable=False, default=0.0),
        sa.Column('budget_utilization_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('timeline_adherence_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('quality_score', sa.Float, nullable=False, default=0.0),
        sa.Column('team_productivity_score', sa.Float, nullable=False, default=0.0),
        sa.Column('communication_frequency', sa.Float, nullable=False, default=0.0),
        sa.Column('collaboration_effectiveness', sa.Float, nullable=False, default=0.0),
        sa.Column('risk_mitigation_success_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('stakeholder_satisfaction', sa.Float, nullable=False, default=0.0),
        sa.Column('milestone_hit_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('resource_efficiency', sa.Float, nullable=False, default=0.0),
        sa.Column('scope_creep_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('change_request_count', sa.Integer, nullable=False, default=0),
        sa.Column('escalation_count', sa.Integer, nullable=False, default=0),
        sa.Column('bottleneck_identification', postgresql.JSONB),
        sa.Column('performance_trends', postgresql.JSONB),
        sa.Column('cost_variance_analysis', postgresql.JSONB),
        sa.Column('time_variance_analysis', postgresql.JSONB),
        sa.Column('predictive_insights', postgresql.JSONB),
        sa.Column('recommendations', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # Project Workflows indexes
    op.create_index('idx_project_workflows_collaboration_id', 'project_workflows', ['collaboration_project_id'])
    op.create_index('idx_project_workflows_name', 'project_workflows', ['workflow_name'])
    op.create_index('idx_project_workflows_template', 'project_workflows', ['workflow_template'])
    op.create_index('idx_project_workflows_phase', 'project_workflows', ['current_phase'])
    op.create_index('idx_project_workflows_is_template', 'project_workflows', ['is_template'])
    op.create_index('idx_project_workflows_category', 'project_workflows', ['template_category'])
    op.create_index('idx_project_workflows_usage', 'project_workflows', ['usage_count'])
    op.create_index('idx_project_workflows_success_rate', 'project_workflows', ['success_rate'])
    
    # Project Tasks indexes
    op.create_index('idx_project_tasks_workflow_id', 'project_tasks', ['workflow_id'])
    op.create_index('idx_project_tasks_parent_task', 'project_tasks', ['parent_task_id'])
    op.create_index('idx_project_tasks_name', 'project_tasks', ['task_name'])
    op.create_index('idx_project_tasks_type', 'project_tasks', ['task_type'])
    op.create_index('idx_project_tasks_status', 'project_tasks', ['status'])
    op.create_index('idx_project_tasks_priority', 'project_tasks', ['priority'])
    op.create_index('idx_project_tasks_assigned_to', 'project_tasks', ['assigned_to'])
    op.create_index('idx_project_tasks_created_by', 'project_tasks', ['created_by'])
    op.create_index('idx_project_tasks_phase', 'project_tasks', ['project_phase'])
    op.create_index('idx_project_tasks_due_date', 'project_tasks', ['due_date'])
    op.create_index('idx_project_tasks_progress', 'project_tasks', ['progress_percentage'])
    op.create_index('idx_project_tasks_dependencies', 'project_tasks', ['dependencies'], postgresql_using='gin')
    op.create_index('idx_project_tasks_approval', 'project_tasks', ['approval_required'])
    
    # Resource Allocation indexes
    op.create_index('idx_resource_allocation_workflow_id', 'resource_allocation', ['workflow_id'])
    op.create_index('idx_resource_allocation_task_id', 'resource_allocation', ['task_id'])
    op.create_index('idx_resource_allocation_type', 'resource_allocation', ['resource_type'])
    op.create_index('idx_resource_allocation_user_id', 'resource_allocation', ['user_id'])
    op.create_index('idx_resource_allocation_percentage', 'resource_allocation', ['allocation_percentage'])
    op.create_index('idx_resource_allocation_availability', 'resource_allocation', ['availability_start', 'availability_end'])
    op.create_index('idx_resource_allocation_utilization', 'resource_allocation', ['utilization_rate'])
    op.create_index('idx_resource_allocation_efficiency', 'resource_allocation', ['efficiency_score'])
    op.create_index('idx_resource_allocation_critical_path', 'resource_allocation', ['is_critical_path'])
    
    # Revenue Sharing Automation indexes
    op.create_index('idx_revenue_sharing_project_id', 'revenue_sharing_automation', ['collaboration_project_id'])
    op.create_index('idx_revenue_sharing_frequency', 'revenue_sharing_automation', ['calculation_frequency'])
    op.create_index('idx_revenue_sharing_automated', 'revenue_sharing_automation', ['automated_calculations'])
    op.create_index('idx_revenue_sharing_total_revenue', 'revenue_sharing_automation', ['total_revenue_tracked'])
    op.create_index('idx_revenue_sharing_last_calc', 'revenue_sharing_automation', ['last_calculation_date'])
    op.create_index('idx_revenue_sharing_next_calc', 'revenue_sharing_automation', ['next_calculation_due'])
    op.create_index('idx_revenue_sharing_transparency', 'revenue_sharing_automation', ['transparency_level'])
    
    # Task Communications indexes
    op.create_index('idx_task_communications_task_id', 'task_communications', ['task_id'])
    op.create_index('idx_task_communications_sender', 'task_communications', ['sender_id'])
    op.create_index('idx_task_communications_type', 'task_communications', ['message_type'])
    op.create_index('idx_task_communications_thread', 'task_communications', ['thread_id'])
    op.create_index('idx_task_communications_parent', 'task_communications', ['parent_message_id'])
    op.create_index('idx_task_communications_priority', 'task_communications', ['priority_level'])
    op.create_index('idx_task_communications_requires_response', 'task_communications', ['requires_response'])
    op.create_index('idx_task_communications_deadline', 'task_communications', ['response_deadline'])
    op.create_index('idx_task_communications_archived', 'task_communications', ['archived'])
    op.create_index('idx_task_communications_recipients', 'task_communications', ['recipients'], postgresql_using='gin')
    
    # Project Milestones indexes
    op.create_index('idx_project_milestones_workflow_id', 'project_milestones', ['workflow_id'])
    op.create_index('idx_project_milestones_name', 'project_milestones', ['milestone_name'])
    op.create_index('idx_project_milestones_type', 'project_milestones', ['milestone_type'])
    op.create_index('idx_project_milestones_phase', 'project_milestones', ['project_phase'])
    op.create_index('idx_project_milestones_target_date', 'project_milestones', ['target_date'])
    op.create_index('idx_project_milestones_status', 'project_milestones', ['status'])
    op.create_index('idx_project_milestones_progress', 'project_milestones', ['progress_percentage'])
    op.create_index('idx_project_milestones_approval', 'project_milestones', ['stakeholder_approval_required'])
    op.create_index('idx_project_milestones_dependencies', 'project_milestones', ['milestone_dependencies'], postgresql_using='gin')
    
    # Workflow Analytics indexes
    op.create_index('idx_workflow_analytics_workflow_id', 'workflow_analytics', ['workflow_id'])
    op.create_index('idx_workflow_analytics_date', 'workflow_analytics', ['analytics_date'])
    op.create_index('idx_workflow_analytics_completion_rate', 'workflow_analytics', ['completed_tasks', 'total_tasks'])
    op.create_index('idx_workflow_analytics_budget_util', 'workflow_analytics', ['budget_utilization_percentage'])
    op.create_index('idx_workflow_analytics_timeline', 'workflow_analytics', ['timeline_adherence_percentage'])
    op.create_index('idx_workflow_analytics_quality', 'workflow_analytics', ['quality_score'])
    op.create_index('idx_workflow_analytics_productivity', 'workflow_analytics', ['team_productivity_score'])
    op.create_index('idx_workflow_analytics_milestone_rate', 'workflow_analytics', ['milestone_hit_rate'])


def downgrade() -> None:
    """Downgrade database schema - Remove project management workflow tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('workflow_analytics')
    op.drop_table('project_milestones')
    op.drop_table('task_communications')
    op.drop_table('revenue_sharing_automation')
    op.drop_table('resource_allocation')
    op.drop_table('project_tasks')
    op.drop_table('project_workflows')
    
    # Drop ENUM types
    sa.Enum(name='resource_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='task_priority').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='task_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='project_phase').drop(op.get_bind(), checkfirst=True)