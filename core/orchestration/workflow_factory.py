"""Workflow Factory - Advanced Workflow Construction & Template System

Intelligent workflow factory for creating, templating, and managing complex
orchestration workflows with dynamic generation and reusable components.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import yaml

from backend.core.utils.metrics_collector import MetricsCollector
from backend.core.utils.event_dispatcher import EventDispatcher


class WorkflowType(Enum):
    """Workflow type classification."""    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    SAGA = "saga"
    PIPELINE = "pipeline"
    DAG = "dag"
    HYBRID = "hybrid"


class ComponentType(Enum):
    """Workflow component types."""    TASK = "task"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL_GROUP = "parallel_group"
    DECISION = "decision"
    GATEWAY = "gateway"
    SERVICE_CALL = "service_call"
    HUMAN_TASK = "human_task"
    TIMER = "timer"
    EVENT = "event"


class TemplateScope(Enum):
    """Template scope levels."""    GLOBAL = "global"
    DOMAIN = "domain"
    PROJECT = "project"
    TEAM = "team"
    USER = "user"


@dataclass
class WorkflowComponent:
    """Individual workflow component."""    component_id: str
    name: str
    component_type: ComponentType
    implementation: Dict[str, Any]
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    dependencies: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowTemplate:
    """Workflow template definition."""    template_id: str
    name: str
    description: str
    workflow_type: WorkflowType
    version: str
    scope: TemplateScope
    components: List[WorkflowComponent] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    default_values: Dict[str, Any] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""    workflow_id: str
    name: str
    description: str
    workflow_type: WorkflowType
    template_id: Optional[str] = None
    components: List[WorkflowComponent] = field(default_factory=list)
    flow_definition: Dict[str, Any] = field(default_factory=dict)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    version: str = "1.0.0"
    status: str = "draft"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentLibrary:
    """Reusable component library."""    library_id: str
    name: str
    description: str
    components: Dict[str, WorkflowComponent] = field(default_factory=dict)
    categories: Dict[str, List[str]] = field(default_factory=dict)
    version: str = "1.0.0"
    scope: TemplateScope = TemplateScope.GLOBAL
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowBlueprint:
    """Workflow blueprint for generation."""    blueprint_id: str
    name: str
    description: str
    pattern: str
    requirements: Dict[str, Any]
    generation_rules: Dict[str, Any] = field(default_factory=dict)
    optimization_hints: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowFactory:
    """    Advanced workflow factory for creating and managing orchestration workflows.
    
    Provides comprehensive workflow construction capabilities including:
    - Template-based workflow creation with reusable components
    - Dynamic workflow generation from blueprints and patterns
    - Component library management with categorization
    - Workflow validation and optimization
    - Multi-format import/export (JSON, YAML, BPMN)
    - Intelligent workflow suggestions and recommendations
    """    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.event_dispatcher = EventDispatcher()
        
        # Storage
        self.workflow_templates: Dict[str, WorkflowTemplate] = {}
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.component_libraries: Dict[str, ComponentLibrary] = {}
        self.workflow_blueprints: Dict[str, WorkflowBlueprint] = {}
        
        # Factory statistics
        self.factory_stats = {
            'workflows_created': 0,
            'templates_used': 0,
            'components_reused': 0,
            'validations_performed': 0,
            'optimizations_applied': 0,
            'blueprints_generated': 0
        }
        
        # Built-in components
        self._initialize_builtin_components()
        
        self.logger.info("WorkflowFactory initialized")
    
    def _initialize_builtin_components(self) -> None:
        """Initialize built-in workflow components."""        builtin_library = ComponentLibrary(
            library_id="builtin",
            name="Built-in Components",
            description="Standard workflow components"
        )
        
        # Basic task component
        task_component = WorkflowComponent(
            component_id="basic_task",
            name="Basic Task",
            component_type=ComponentType.TASK,
            implementation={
                'type': 'function_call',
                'function': 'execute_task',
                'parameters': {}
            }
        )
        builtin_library.components[task_component.component_id] = task_component
        
        # Conditional component
        condition_component = WorkflowComponent(
            component_id="condition",
            name="Conditional Branch",
            component_type=ComponentType.CONDITION,
            implementation={
                'type': 'condition_check',
                'condition': 'expression',
                'true_path': 'next_true',
                'false_path': 'next_false'
            }
        )
        builtin_library.components[condition_component.component_id] = condition_component
        
        # Parallel group component
        parallel_component = WorkflowComponent(
            component_id="parallel_group",
            name="Parallel Execution Group",
            component_type=ComponentType.PARALLEL_GROUP,
            implementation={
                'type': 'parallel_execution',
                'tasks': [],
                'wait_all': True
            }
        )
        builtin_library.components[parallel_component.component_id] = parallel_component
        
        self.component_libraries[builtin_library.library_id] = builtin_library
    
    async def register_template(self, template: WorkflowTemplate) -> bool:
        """        Register workflow template.
        
        Args:
            template: Workflow template to register
            
        Returns:
            bool: Success status
        """        try:
            # Validate template
            validation_result = await self._validate_template(template)
            if not validation_result['valid']:
                self.logger.error(f"Template validation failed: {validation_result['errors']}")
                return False
            
            self.workflow_templates[template.template_id] = template
            
            await self.event_dispatcher.emit('workflow_template_registered', {
                'template_id': template.template_id,
                'name': template.name,
                'type': template.workflow_type.value,
                'component_count': len(template.components)
            })
            
            await self.metrics_collector.increment('workflow_templates.registered')
            
            self.logger.info(f"Workflow template registered: {template.template_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register template: {e}")
            return False
    
    async def create_workflow_from_template(
        self,
        template_id: str,
        workflow_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """        Create workflow from template.
        
        Args:
            template_id: Template identifier
            workflow_name: Name for new workflow
            parameters: Template parameters
            
        Returns:
            Optional[str]: Workflow ID if successful
        """        try:
            if template_id not in self.workflow_templates:
                raise ValueError(f"Template not found: {template_id}")
            
            template = self.workflow_templates[template_id]
            parameters = parameters or {}
            
            # Create workflow definition
            workflow_id = str(uuid.uuid4())
            
            # Apply template parameters
            components = await self._apply_template_parameters(template.components, parameters)
            
            workflow_definition = WorkflowDefinition(
                workflow_id=workflow_id,
                name=workflow_name,
                description=f"Created from template: {template.name}",
                workflow_type=template.workflow_type,
                template_id=template_id,
                components=components,
                flow_definition=await self._generate_flow_definition(components, template.workflow_type),
                configuration=template.default_values.copy()
            )
            
            # Validate workflow
            validation_result = await self._validate_workflow(workflow_definition)
            if not validation_result['valid']:
                self.logger.error(f"Workflow validation failed: {validation_result['errors']}")
                return None
            
            self.workflow_definitions[workflow_id] = workflow_definition
            self.factory_stats['workflows_created'] += 1
            self.factory_stats['templates_used'] += 1
            
            await self.event_dispatcher.emit('workflow_created_from_template', {
                'workflow_id': workflow_id,
                'template_id': template_id,
                'name': workflow_name,
                'component_count': len(components)
            })
            
            await self.metrics_collector.increment('workflows.created_from_template')
            
            self.logger.info(f"Workflow created from template: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow from template: {e}")
            return None
    
    async def create_workflow_from_blueprint(self, blueprint: WorkflowBlueprint) -> Optional[str]:
        """        Create workflow from blueprint.
        
        Args:
            blueprint: Workflow blueprint
            
        Returns:
            Optional[str]: Workflow ID if successful
        """        try:
            workflow_id = str(uuid.uuid4())
            
            # Generate workflow from blueprint
            workflow_definition = await self._generate_from_blueprint(blueprint, workflow_id)
            
            if not workflow_definition:
                return None
            
            # Validate generated workflow
            validation_result = await self._validate_workflow(workflow_definition)
            if not validation_result['valid']:
                # Try to auto-fix common issues
                workflow_definition = await self._auto_fix_workflow(workflow_definition, validation_result)
                
                # Re-validate
                validation_result = await self._validate_workflow(workflow_definition)
                if not validation_result['valid']:
                    self.logger.error(f"Blueprint workflow validation failed: {validation_result['errors']}")
                    return None
            
            self.workflow_definitions[workflow_id] = workflow_definition
            self.factory_stats['workflows_created'] += 1
            self.factory_stats['blueprints_generated'] += 1
            
            await self.event_dispatcher.emit('workflow_created_from_blueprint', {
                'workflow_id': workflow_id,
                'blueprint_id': blueprint.blueprint_id,
                'name': workflow_definition.name
            })
            
            await self.metrics_collector.increment('workflows.created_from_blueprint')
            
            self.logger.info(f"Workflow created from blueprint: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow from blueprint: {e}")
            return None
    
    async def build_custom_workflow(
        self,
        name: str,
        workflow_type: WorkflowType,
        components: List[WorkflowComponent]
    ) -> Optional[str]:
        """        Build custom workflow from components.
        
        Args:
            name: Workflow name
            workflow_type: Type of workflow
            components: List of workflow components
            
        Returns:
            Optional[str]: Workflow ID if successful
        """        try:
            workflow_id = str(uuid.uuid4())
            
            # Validate components
            for component in components:
                if not await self._validate_component(component):
                    self.logger.error(f"Invalid component: {component.component_id}")
                    return None
            
            # Generate flow definition
            flow_definition = await self._generate_flow_definition(components, workflow_type)
            
            workflow_definition = WorkflowDefinition(
                workflow_id=workflow_id,
                name=name,
                description=f"Custom {workflow_type.value} workflow",
                workflow_type=workflow_type,
                components=components,
                flow_definition=flow_definition
            )
            
            # Validate complete workflow
            validation_result = await self._validate_workflow(workflow_definition)
            if not validation_result['valid']:
                self.logger.error(f"Custom workflow validation failed: {validation_result['errors']}")
                return None
            
            self.workflow_definitions[workflow_id] = workflow_definition
            self.factory_stats['workflows_created'] += 1
            
            await self.event_dispatcher.emit('custom_workflow_created', {
                'workflow_id': workflow_id,
                'name': name,
                'type': workflow_type.value,
                'component_count': len(components)
            })
            
            await self.metrics_collector.increment('workflows.custom_created')
            
            self.logger.info(f"Custom workflow created: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to build custom workflow: {e}")
            return None
    
    async def register_component_library(self, library: ComponentLibrary) -> bool:
        """        Register component library.
        
        Args:
            library: Component library to register
            
        Returns:
            bool: Success status
        """        try:
            # Validate library components
            for component in library.components.values():
                if not await self._validate_component(component):
                    self.logger.error(f"Invalid component in library: {component.component_id}")
                    return False
            
            self.component_libraries[library.library_id] = library
            
            await self.event_dispatcher.emit('component_library_registered', {
                'library_id': library.library_id,
                'name': library.name,
                'component_count': len(library.components)
            })
            
            await self.metrics_collector.increment('component_libraries.registered')
            
            self.logger.info(f"Component library registered: {library.library_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register component library: {e}")
            return False
    
    async def get_component_suggestions(
        self,
        workflow_type: WorkflowType,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """        Get component suggestions for workflow.
        
        Args:
            workflow_type: Type of workflow
            requirements: Workflow requirements
            
        Returns:
            List of suggested components
        """        try:
            suggestions = []
            
            # Search through all component libraries
            for library in self.component_libraries.values():
                for component in library.components.values():
                    score = await self._calculate_component_relevance_score(
                        component, workflow_type, requirements
                    )
                    
                    if score > 0.3:  # Threshold for relevance
                        suggestions.append({
                            'component': component,
                            'library_id': library.library_id,
                            'relevance_score': score,
                            'recommendation_reason': await self._get_recommendation_reason(
                                component, workflow_type, requirements
                            )
                        })
            
            # Sort by relevance score
            suggestions.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return suggestions[:10]  # Return top 10 suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to get component suggestions: {e}")
            return []
    
    async def optimize_workflow(self, workflow_id: str) -> bool:
        """        Optimize existing workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            bool: Success status
        """        try:
            if workflow_id not in self.workflow_definitions:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            workflow = self.workflow_definitions[workflow_id]
            
            # Apply optimizations
            optimized = False
            
            # Remove redundant components
            if await self._remove_redundant_components(workflow):
                optimized = True
            
            # Optimize parallel execution
            if await self._optimize_parallel_execution(workflow):
                optimized = True
            
            # Optimize resource usage
            if await self._optimize_resource_usage(workflow):
                optimized = True
            
            # Update flow definition
            workflow.flow_definition = await self._generate_flow_definition(
                workflow.components, workflow.workflow_type
            )
            
            if optimized:
                self.factory_stats['optimizations_applied'] += 1
                
                await self.event_dispatcher.emit('workflow_optimized', {
                    'workflow_id': workflow_id,
                    'optimizations_applied': True
                })
                
                await self.metrics_collector.increment('workflows.optimized')
            
            self.logger.info(f"Workflow optimization completed: {workflow_id}")
            return optimized
            
        except Exception as e:
            self.logger.error(f"Failed to optimize workflow: {e}")
            return False
    
    async def export_workflow(self, workflow_id: str, format_type: str = "json") -> Optional[str]:
        """        Export workflow definition.
        
        Args:
            workflow_id: Workflow identifier
            format_type: Export format (json, yaml, bpmn)
            
        Returns:
            Optional[str]: Exported workflow string
        """        try:
            if workflow_id not in self.workflow_definitions:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            workflow = self.workflow_definitions[workflow_id]
            
            if format_type.lower() == "yaml":
                return await self._export_to_yaml(workflow)
            elif format_type.lower() == "bpmn":
                return await self._export_to_bpmn(workflow)
            else:  # Default to JSON
                return await self._export_to_json(workflow)
            
        except Exception as e:
            self.logger.error(f"Failed to export workflow: {e}")
            return None
    
    async def import_workflow(self, workflow_data: str, format_type: str = "json") -> Optional[str]:
        """        Import workflow definition.
        
        Args:
            workflow_data: Workflow data string
            format_type: Import format (json, yaml, bpmn)
            
        Returns:
            Optional[str]: Workflow ID if successful
        """        try:
            if format_type.lower() == "yaml":
                workflow = await self._import_from_yaml(workflow_data)
            elif format_type.lower() == "bpmn":
                workflow = await self._import_from_bpmn(workflow_data)
            else:  # Default to JSON
                workflow = await self._import_from_json(workflow_data)
            
            if not workflow:
                return None
            
            # Generate new ID
            workflow.workflow_id = str(uuid.uuid4())
            
            # Validate imported workflow
            validation_result = await self._validate_workflow(workflow)
            if not validation_result['valid']:
                self.logger.error(f"Imported workflow validation failed: {validation_result['errors']}")
                return None
            
            self.workflow_definitions[workflow.workflow_id] = workflow
            self.factory_stats['workflows_created'] += 1
            
            await self.event_dispatcher.emit('workflow_imported', {
                'workflow_id': workflow.workflow_id,
                'format': format_type,
                'name': workflow.name
            })
            
            await self.metrics_collector.increment('workflows.imported')
            
            self.logger.info(f"Workflow imported: {workflow.workflow_id}")
            return workflow.workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to import workflow: {e}")
            return None
    
    async def _apply_template_parameters(
        self,
        components: List[WorkflowComponent],
        parameters: Dict[str, Any]
    ) -> List[WorkflowComponent]:
        """Apply template parameters to components."""        applied_components = []
        
        for component in components:
            # Create copy of component
            new_component = WorkflowComponent(
                component_id=component.component_id,
                name=component.name,
                component_type=component.component_type,
                implementation=component.implementation.copy(),
                inputs=component.inputs.copy(),
                outputs=component.outputs.copy(),
                conditions=component.conditions.copy(),
                retry_policy=component.retry_policy.copy(),
                timeout=component.timeout,
                dependencies=component.dependencies.copy(),
                properties=component.properties.copy(),
                metadata=component.metadata.copy()
            )
            
            # Apply parameters
            new_component.implementation = await self._substitute_parameters(
                new_component.implementation, parameters
            )
            new_component.inputs = await self._substitute_parameters(
                new_component.inputs, parameters
            )
            new_component.properties = await self._substitute_parameters(
                new_component.properties, parameters
            )
            
            applied_components.append(new_component)
        
        return applied_components
    
    async def _substitute_parameters(self, data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute template parameters in data."""        result = {}
        
        for key, value in data.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                param_name = value[2:-2].strip()
                result[key] = parameters.get(param_name, value)
            elif isinstance(value, dict):
                result[key] = await self._substitute_parameters(value, parameters)
            elif isinstance(value, list):
                result[key] = [
                    await self._substitute_parameters(item, parameters) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    async def _generate_flow_definition(
        self,
        components: List[WorkflowComponent],
        workflow_type: WorkflowType
    ) -> Dict[str, Any]:
        """Generate flow definition from components."""        flow_definition = {
            'type': workflow_type.value,
            'start': components[0].component_id if components else None,
            'nodes': {},
            'edges': []
        }
        
        # Add nodes
        for component in components:
            flow_definition['nodes'][component.component_id] = {
                'type': component.component_type.value,
                'name': component.name,
                'implementation': component.implementation,
                'properties': component.properties
            }
        
        # Generate edges based on workflow type
        if workflow_type == WorkflowType.SEQUENTIAL:
            for i in range(len(components) - 1):
                flow_definition['edges'].append({
                    'from': components[i].component_id,
                    'to': components[i + 1].component_id,
                    'condition': None
                })
        
        elif workflow_type == WorkflowType.PARALLEL:
            if components:
                start_node = components[0].component_id
                for i in range(1, len(components)):
                    flow_definition['edges'].append({
                        'from': start_node,
                        'to': components[i].component_id,
                        'condition': None
                    })
        
        # Add conditional edges for conditional workflows
        elif workflow_type == WorkflowType.CONDITIONAL:
            for component in components:
                if component.component_type == ComponentType.CONDITION:
                    # Add conditional edges based on component conditions
                    for condition, next_component in component.conditions.items():
                        flow_definition['edges'].append({
                            'from': component.component_id,
                            'to': next_component,
                            'condition': condition
                        })
        
        return flow_definition
    
    async def _generate_from_blueprint(
        self,
        blueprint: WorkflowBlueprint,
        workflow_id: str
    ) -> Optional[WorkflowDefinition]:
        """Generate workflow from blueprint."""        try:
            # Parse blueprint pattern
            pattern = blueprint.pattern
            requirements = blueprint.requirements
            
            components = []
            
            if pattern == "data_processing_pipeline":
                components = await self._generate_data_pipeline_components(requirements)
            elif pattern == "approval_workflow":
                components = await self._generate_approval_workflow_components(requirements)
            elif pattern == "monitoring_workflow":
                components = await self._generate_monitoring_workflow_components(requirements)
            else:
                # Generic pattern
                components = await self._generate_generic_components(requirements)
            
            if not components:
                return None
            
            workflow_type = WorkflowType(requirements.get('type', 'sequential'))
            
            return WorkflowDefinition(
                workflow_id=workflow_id,
                name=blueprint.name,
                description=blueprint.description,
                workflow_type=workflow_type,
                components=components,
                flow_definition=await self._generate_flow_definition(components, workflow_type)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate from blueprint: {e}")
            return None
    
    async def _generate_data_pipeline_components(self, requirements: Dict[str, Any]) -> List[WorkflowComponent]:
        """Generate components for data processing pipeline."""        components = []
        
        # Data ingestion component
        components.append(WorkflowComponent(
            component_id="data_ingestion",
            name="Data Ingestion",
            component_type=ComponentType.TASK,
            implementation={
                'type': 'data_ingestion',
                'source': requirements.get('data_source', 'file'),
                'format': requirements.get('data_format', 'json')
            }
        ))
        
        # Data validation component
        components.append(WorkflowComponent(
            component_id="data_validation",
            name="Data Validation",
            component_type=ComponentType.TASK,
            implementation={
                'type': 'data_validation',
                'schema': requirements.get('validation_schema', {}),
                'strict': requirements.get('strict_validation', True)
            }
        ))
        
        # Data processing component
        components.append(WorkflowComponent(
            component_id="data_processing",
            name="Data Processing",
            component_type=ComponentType.TASK,
            implementation={
                'type': 'data_processing',
                'operations': requirements.get('processing_operations', []),
                'parallel': requirements.get('parallel_processing', False)
            }
        ))
        
        # Data output component
        components.append(WorkflowComponent(
            component_id="data_output",
            name="Data Output",
            component_type=ComponentType.TASK,
            implementation={
                'type': 'data_output',
                'destination': requirements.get('output_destination', 'file'),
                'format': requirements.get('output_format', 'json')
            }
        ))
        
        return components
    
    async def _generate_approval_workflow_components(self, requirements: Dict[str, Any]) -> List[WorkflowComponent]:
        """Generate components for approval workflow."""        components = []
        
        # Request submission
        components.append(WorkflowComponent(
            component_id="request_submission",
            name="Request Submission",
            component_type=ComponentType.TASK,
            implementation={
                'type': 'request_submission',
                'form_schema': requirements.get('form_schema', {}),
                'validation': requirements.get('input_validation', {})
            }
        ))
        
        # Approval decision
        components.append(WorkflowComponent(
            component_id="approval_decision",
            name="Approval Decision",
            component_type=ComponentType.CONDITION,
            implementation={
                'type': 'human_approval',
                'approvers': requirements.get('approvers', []),
                'approval_criteria': requirements.get('approval_criteria', {})
            },
            conditions={
                'approved': 'request_approved',
                'rejected': 'request_rejected'
            }
        ))
        
        # Approval actions
        components.append(WorkflowComponent(
            component_id="request_approved",
            name="Request Approved",
            component_type=ComponentType.TASK,
            implementation={
                'type': 'approval_action',
                'action': 'approve',
                'notifications': requirements.get('approval_notifications', [])
            }
        ))
        
        components.append(WorkflowComponent(
            component_id="request_rejected",
            name="Request Rejected",
            component_type=ComponentType.TASK,
            implementation={
                'type': 'approval_action',
                'action': 'reject',
                'notifications': requirements.get('rejection_notifications', [])
            }
        ))
        
        return components
    
    async def _generate_monitoring_workflow_components(self, requirements: Dict[str, Any]) -> List[WorkflowComponent]:
        """Generate components for monitoring workflow."""        components = []
        
        # Metric collection
        components.append(WorkflowComponent(
            component_id="metric_collection",
            name="Metric Collection",
            component_type=ComponentType.TASK,
            implementation={
                'type': 'metric_collection',
                'metrics': requirements.get('metrics', []),
                'interval': requirements.get('collection_interval', 60)
            }
        ))
        
        # Threshold checking
        components.append(WorkflowComponent(
            component_id="threshold_check",
            name="Threshold Check",
            component_type=ComponentType.CONDITION,
            implementation={
                'type': 'threshold_check',
                'thresholds': requirements.get('thresholds', {}),
                'evaluation_logic': requirements.get('evaluation_logic', 'any')
            },
            conditions={
                'threshold_exceeded': 'alert_triggered',
                'threshold_ok': 'monitoring_continue'
            }
        ))
        
        # Alert handling
        components.append(WorkflowComponent(
            component_id="alert_triggered",
            name="Alert Triggered",
            component_type=ComponentType.TASK,
            implementation={
                'type': 'alert_handling',
                'alert_channels': requirements.get('alert_channels', []),
                'escalation_rules': requirements.get('escalation_rules', {})
            }
        ))
        
        # Continue monitoring
        components.append(WorkflowComponent(
            component_id="monitoring_continue",
            name="Continue Monitoring",
            component_type=ComponentType.TASK,
            implementation={
                'type': 'monitoring_continue',
                'wait_interval': requirements.get('monitoring_interval', 300)
            }
        ))
        
        return components
    
    async def _generate_generic_components(self, requirements: Dict[str, Any]) -> List[WorkflowComponent]:
        """Generate generic components based on requirements."""        components = []
        
        # Generate basic task components
        task_count = requirements.get('task_count', 3)
        
        for i in range(task_count):
            components.append(WorkflowComponent(
                component_id=f"task_{i + 1}",
                name=f"Task {i + 1}",
                component_type=ComponentType.TASK,
                implementation={
                    'type': 'generic_task',
                    'operation': requirements.get(f'task_{i + 1}_operation', 'execute'),
                    'parameters': requirements.get(f'task_{i + 1}_parameters', {})
                }
            ))
        
        return components
    
    async def _calculate_component_relevance_score(
        self,
        component: WorkflowComponent,
        workflow_type: WorkflowType,
        requirements: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for component suggestion."""        score = 0.0
        
        # Base score for component type compatibility
        if workflow_type == WorkflowType.SEQUENTIAL and component.component_type == ComponentType.TASK:
            score += 0.3
        elif workflow_type == WorkflowType.PARALLEL and component.component_type in [ComponentType.TASK, ComponentType.PARALLEL_GROUP]:
            score += 0.3
        elif workflow_type == WorkflowType.CONDITIONAL and component.component_type in [ComponentType.CONDITION, ComponentType.DECISION]:
            score += 0.4
        
        # Score based on requirements matching
        implementation_type = component.implementation.get('type', '')
        required_type = requirements.get('component_type', '')
        
        if implementation_type == required_type:
            score += 0.4
        elif required_type in implementation_type:
            score += 0.2
        
        # Score based on tags and metadata
        required_tags = requirements.get('tags', [])
        component_tags = component.metadata.get('tags', [])
        
        if required_tags and component_tags:
            matching_tags = set(required_tags) & set(component_tags)
            score += len(matching_tags) / len(required_tags) * 0.3
        
        return min(score, 1.0)
    
    async def _get_recommendation_reason(
        self,
        component: WorkflowComponent,
        workflow_type: WorkflowType,
        requirements: Dict[str, Any]
    ) -> str:
        """Get reason for component recommendation."""        reasons = []
        
        if component.component_type == ComponentType.TASK:
            reasons.append("Suitable for task execution")
        
        if component.component_type == ComponentType.CONDITION and workflow_type == WorkflowType.CONDITIONAL:
            reasons.append("Perfect for conditional workflows")
        
        implementation_type = component.implementation.get('type', '')
        if implementation_type in requirements.get('preferred_types', []):
            reasons.append(f"Matches preferred type: {implementation_type}")
        
        if not reasons:
            reasons.append("General purpose component")
        
        return "; ".join(reasons)
    
    async def _remove_redundant_components(self, workflow: WorkflowDefinition) -> bool:
        """Remove redundant components from workflow."""        original_count = len(workflow.components)
        
        # Simple redundancy check - remove duplicate component IDs
        seen_ids = set()
        unique_components = []
        
        for component in workflow.components:
            if component.component_id not in seen_ids:
                seen_ids.add(component.component_id)
                unique_components.append(component)
        
        workflow.components = unique_components
        
        return len(workflow.components) < original_count
    
    async def _optimize_parallel_execution(self, workflow: WorkflowDefinition) -> bool:
        """Optimize parallel execution in workflow."""        if workflow.workflow_type != WorkflowType.PARALLEL:
            return False
        
        # Group independent tasks for parallel execution
        # This is a simplified optimization
        optimized = False
        
        # Look for tasks that can be executed in parallel
        parallel_groups = []
        current_group = []
        
        for component in workflow.components:
            if component.component_type == ComponentType.TASK and not component.dependencies:
                current_group.append(component)
            else:
                if len(current_group) > 1:
                    parallel_groups.append(current_group)
                current_group = [component]
        
        if len(current_group) > 1:
            parallel_groups.append(current_group)
        
        # Create parallel group components
        for i, group in enumerate(parallel_groups):
            if len(group) > 1:
                parallel_component = WorkflowComponent(
                    component_id=f"parallel_group_{i}",
                    name=f"Parallel Group {i + 1}",
                    component_type=ComponentType.PARALLEL_GROUP,
                    implementation={
                        'type': 'parallel_execution',
                        'tasks': [comp.component_id for comp in group],
                        'wait_all': True
                    }
                )
                
                # Replace individual components with parallel group
                for comp in group:
                    workflow.components.remove(comp)
                workflow.components.append(parallel_component)
                
                optimized = True
        
        return optimized
    
    async def _optimize_resource_usage(self, workflow: WorkflowDefinition) -> bool:
        """Optimize resource usage in workflow."""        optimized = False
        
        # Add resource constraints to components that don't have them
        for component in workflow.components:
            if 'resource_requirements' not in component.properties:
                component.properties['resource_requirements'] = {
                    'cpu': 'medium',
                    'memory': 'medium',
                    'priority': 'normal'
                }
                optimized = True
        
        return optimized
    
    async def _auto_fix_workflow(
        self,
        workflow: WorkflowDefinition,
        validation_result: Dict[str, Any]
    ) -> WorkflowDefinition:
        """Auto-fix common workflow issues."""        # Fix missing component IDs
        for i, component in enumerate(workflow.components):
            if not component.component_id:
                component.component_id = f"component_{i}"
        
        # Fix circular dependencies (simplified)
        for component in workflow.components:
            if component.component_id in component.dependencies:
                component.dependencies.remove(component.component_id)
        
        return workflow
    
    async def _validate_template(self, template: WorkflowTemplate) -> Dict[str, Any]:
        """Validate workflow template."""        result = {'valid': True, 'errors': [], 'warnings': []}
        
        if not template.template_id:
            result['valid'] = False
            result['errors'].append("Template ID is required")
        
        if not template.name:
            result['valid'] = False
            result['errors'].append("Template name is required")
        
        # Validate components
        for component in template.components:
            component_result = await self._validate_component(component)
            if not component_result:
                result['valid'] = False
                result['errors'].append(f"Invalid component: {component.component_id}")
        
        return result
    
    async def _validate_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Validate workflow definition."""        result = {'valid': True, 'errors': [], 'warnings': []}
        
        if not workflow.workflow_id:
            result['valid'] = False
            result['errors'].append("Workflow ID is required")
        
        if not workflow.name:
            result['valid'] = False
            result['errors'].append("Workflow name is required")
        
        if not workflow.components:
            result['valid'] = False
            result['errors'].append("Workflow must have at least one component")
        
        # Validate each component
        for component in workflow.components:
            if not await self._validate_component(component):
                result['valid'] = False
                result['errors'].append(f"Invalid component: {component.component_id}")
        
        # Check for circular dependencies
        if await self._has_circular_dependencies(workflow.components):
            result['valid'] = False
            result['errors'].append("Circular dependencies detected")
        
        self.factory_stats['validations_performed'] += 1
        
        return result
    
    async def _validate_component(self, component: WorkflowComponent) -> bool:
        """Validate individual component."""        if not component.component_id:
            return False
        
        if not component.name:
            return False
        
        if not component.implementation:
            return False
        
        return True
    
    async def _has_circular_dependencies(self, components: List[WorkflowComponent]) -> bool:
        """Check for circular dependencies."""        # Simple circular dependency check
        component_map = {comp.component_id: comp for comp in components}
        
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            component = component_map.get(node)
            if component:
                for dep in component.dependencies:
                    if dep not in visited:
                        if has_cycle(dep, visited, rec_stack):
                            return True
                    elif dep in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for component in components:
            if component.component_id not in visited:
                if has_cycle(component.component_id, visited, set()):
                    return True
        
        return False
    
    async def _export_to_json(self, workflow: WorkflowDefinition) -> str:
        """Export workflow to JSON format."""        workflow_dict = {
            'workflow_id': workflow.workflow_id,
            'name': workflow.name,
            'description': workflow.description,
            'type': workflow.workflow_type.value,
            'version': workflow.version,
            'components': [
                {
                    'component_id': comp.component_id,
                    'name': comp.name,
                    'type': comp.component_type.value,
                    'implementation': comp.implementation,
                    'inputs': comp.inputs,
                    'outputs': comp.outputs,
                    'dependencies': comp.dependencies,
                    'properties': comp.properties
                }
                for comp in workflow.components
            ],
            'flow_definition': workflow.flow_definition,
            'configuration': workflow.configuration,
            'metadata': workflow.metadata
        }
        
        return json.dumps(workflow_dict, indent=2, default=str)
    
    async def _export_to_yaml(self, workflow: WorkflowDefinition) -> str:
        """Export workflow to YAML format."""        workflow_dict = {
            'workflow_id': workflow.workflow_id,
            'name': workflow.name,
            'description': workflow.description,
            'type': workflow.workflow_type.value,
            'version': workflow.version,
            'components': [
                {
                    'component_id': comp.component_id,
                    'name': comp.name,
                    'type': comp.component_type.value,
                    'implementation': comp.implementation,
                    'inputs': comp.inputs,
                    'outputs': comp.outputs,
                    'dependencies': comp.dependencies,
                    'properties': comp.properties
                }
                for comp in workflow.components
            ],
            'flow_definition': workflow.flow_definition,
            'configuration': workflow.configuration,
            'metadata': workflow.metadata
        }
        
        return yaml.dump(workflow_dict, default_flow_style=False)
    
    async def _export_to_bpmn(self, workflow: WorkflowDefinition) -> str:
        """Export workflow to BPMN format."""        # Simplified BPMN export
        bpmn_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="{workflow.workflow_id}" name="{workflow.name}">
"""        
        for component in workflow.components:
            if component.component_type == ComponentType.TASK:
                bpmn_xml += f'    <task id="{component.component_id}" name="{component.name}" />\n'
            elif component.component_type == ComponentType.CONDITION:
                bpmn_xml += f'    <exclusiveGateway id="{component.component_id}" name="{component.name}" />\n'
        
        bpmn_xml += """  </process>
</definitions>"""        
        return bpmn_xml
    
    async def _import_from_json(self, workflow_data: str) -> Optional[WorkflowDefinition]:
        """Import workflow from JSON format."""        try:
            data = json.loads(workflow_data)
            
            components = []
            for comp_data in data.get('components', []):
                component = WorkflowComponent(
                    component_id=comp_data['component_id'],
                    name=comp_data['name'],
                    component_type=ComponentType(comp_data['type']),
                    implementation=comp_data.get('implementation', {}),
                    inputs=comp_data.get('inputs', {}),
                    outputs=comp_data.get('outputs', {}),
                    dependencies=comp_data.get('dependencies', []),
                    properties=comp_data.get('properties', {})
                )
                components.append(component)
            
            return WorkflowDefinition(
                workflow_id=data['workflow_id'],
                name=data['name'],
                description=data.get('description', ''),
                workflow_type=WorkflowType(data['type']),
                components=components,
                flow_definition=data.get('flow_definition', {}),
                configuration=data.get('configuration', {}),
                version=data.get('version', '1.0.0'),
                metadata=data.get('metadata', {})
            )
            
        except Exception as e:
            self.logger.error(f"Failed to import from JSON: {e}")
            return None
    
    async def _import_from_yaml(self, workflow_data: str) -> Optional[WorkflowDefinition]:
        """Import workflow from YAML format."""        try:
            data = yaml.safe_load(workflow_data)
            return await self._import_from_json(json.dumps(data))
        except Exception as e:
            self.logger.error(f"Failed to import from YAML: {e}")
            return None
    
    async def _import_from_bpmn(self, workflow_data: str) -> Optional[WorkflowDefinition]:
        """Import workflow from BPMN format."""        # Simplified BPMN import
        # In production, use proper BPMN parsing library
        try:
            # Extract basic information from BPMN XML
            import xml.etree.ElementTree as ET
            root = ET.fromstring(workflow_data)
            
            # Find process element
            process = root.find('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}process')
            if process is None:
                return None
            
            workflow_id = process.get('id', str(uuid.uuid4()))
            name = process.get('name', 'Imported BPMN Workflow')
            
            components = []
            
            # Extract tasks
            tasks = process.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}task')
            for task in tasks:
                component = WorkflowComponent(
                    component_id=task.get('id'),
                    name=task.get('name', 'Imported Task'),
                    component_type=ComponentType.TASK,
                    implementation={'type': 'bpmn_task'}
                )
                components.append(component)
            
            return WorkflowDefinition(
                workflow_id=workflow_id,
                name=name,
                description='Imported from BPMN',
                workflow_type=WorkflowType.SEQUENTIAL,
                components=components
            )
            
        except Exception as e:
            self.logger.error(f"Failed to import from BPMN: {e}")
            return None
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow definition by ID."""        return self.workflow_definitions.get(workflow_id)
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows."""        return [
            {
                'workflow_id': workflow.workflow_id,
                'name': workflow.name,
                'description': workflow.description,
                'type': workflow.workflow_type.value,
                'component_count': len(workflow.components),
                'status': workflow.status,
                'created_at': workflow.created_at.isoformat(),
                'version': workflow.version
            }
            for workflow in self.workflow_definitions.values()
        ]
    
    async def list_templates(self) -> List[Dict[str, Any]]:
        """List all workflow templates."""        return [
            {
                'template_id': template.template_id,
                'name': template.name,
                'description': template.description,
                'type': template.workflow_type.value,
                'scope': template.scope.value,
                'component_count': len(template.components),
                'version': template.version,
                'created_at': template.created_at.isoformat()
            }
            for template in self.workflow_templates.values()
        ]
    
    async def get_factory_stats(self) -> Dict[str, Any]:
        """Get workflow factory statistics."""        return {
            **self.factory_stats,
            'total_workflows': len(self.workflow_definitions),
            'total_templates': len(self.workflow_templates),
            'total_libraries': len(self.component_libraries),
            'total_blueprints': len(self.workflow_blueprints)
        }
