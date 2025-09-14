"""Collaboration Tools Integration
================================

Enterprise-grade collaboration tools integration for creator teams,
project management, and workflow automation across platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import base64
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode
import uuid

# Configure logger
logger = logging.getLogger(__name__)

class Project:
    """Project management and tracking"""
    
    def __init__(self, project_id -> None: str, name -> None: str, creator_id -> None: str) -> None:
        self.project_id = project_id
        self.name = name
        self.creator_id = creator_id
        self.description = ""
        self.status = "active"  # active, completed, on_hold, cancelled
        self.created_at = datetime.utcnow()
        self.deadline = None
        self.progress = 0.0
        self.team_members = []
        self.tasks = []
        self.budget = 0.0
        self.spent = 0.0

class Task:
    """Task management and assignment"""
    
    def __init__(self, task_id -> None: str, project_id -> None: str, title -> None: str) -> None:
        self.task_id = task_id
        self.project_id = project_id
        self.title = title
        self.description = ""
        self.assignee_id = ""
        self.status = "todo"  # todo, in_progress, review, completed
        self.priority = "medium"  # low, medium, high, urgent
        self.created_at = datetime.utcnow()
        self.due_date = None
        self.completed_at = None
        self.estimated_hours = 0
        self.actual_hours = 0
        self.tags = []

class TeamMember:
    """Team member management"""
    
    def __init__(self, member_id -> None: str, user_id -> None: str, role -> None: str) -> None:
        self.member_id = member_id
        self.user_id = user_id
        self.role = role  # owner, admin, editor, viewer, collaborator
        self.permissions = []
        self.joined_at = datetime.utcnow()
        self.status = "active"  # active, inactive, invited
        self.workload = 0.0
        self.performance_score = 0.0

class Document:
    """Document and file management"""
    
    def __init__(self, document_id -> None: str, project_id -> None: str, title -> None: str) -> None:
        self.document_id = document_id
        self.project_id = project_id
        self.title = title
        self.content = ""
        self.file_url = ""
        self.file_type = ""
        self.created_by = ""
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.version = 1
        self.collaborators = []
        self.comments = []

class CollaborationToolsError(Exception):
    """Custom exception for collaboration tools errors"""
    pass

class CollaborationTools:
    """
    Comprehensive collaboration tools integration for Ainflue platform.
    
    Features:
    - Project management and tracking
    - Task assignment and workflow automation
    - Team collaboration and communication
    - Document sharing and co-editing
    - Time tracking and productivity analytics
    - Integration with popular tools (Slack, Trello, Asana, Notion)
    - Creator-specific workflow templates
    - Performance monitoring and optimization
    """
    
    def __init__(self, tools_config -> None: Dict[str, Dict[str, Any]]) -> None:
        self.tools_config = tools_config
        self.session = None
        self.active_projects = {}
        self.rate_limits = {
            'requests_per_minute': 150,
            'requests_made': 0,
            'minute_start': datetime.utcnow().minute
        }
        
    async def __aenter__(self) -> None:
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting"""
        current_minute = datetime.utcnow().minute
        
        if current_minute != self.rate_limits['minute_start']:
            self.rate_limits['requests_made'] = 0
            self.rate_limits['minute_start'] = current_minute
            
        if self.rate_limits['requests_made'] >= self.rate_limits['requests_per_minute']:
            raise CollaborationToolsError("Rate limit exceeded")
            
        self.rate_limits['requests_made'] += 1

    async def _make_tool_request(self, tool: str, method: str, endpoint: str, 
                                data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """
        Make authenticated request to specific tool API.
        
        Args:
            tool: Tool name (slack, trello, asana, notion, github)
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: URL parameters
            
        Returns:
            API response data
        """
        self._check_rate_limit()
        
        tool_config = self.tools_config.get(tool)
        if not tool_config:
            raise CollaborationToolsError(f"Tool {tool} not configured")
        
        base_url = tool_config['base_url']
        headers = await self._get_tool_headers(tool)
        
        url = f"{base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            ) as response:
                
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    await asyncio.sleep(retry_after)
                    return await self._make_tool_request(tool, method, endpoint, data, params)
                
                response_data = await response.json()
                
                if response.status >= 400:
                    raise CollaborationToolsError(
                        f"{tool} API request failed: {response.status} - {response_data}"
                    )
                    
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"Request error for {tool}: {e}")
            raise CollaborationToolsError(f"Request error: {e}")

    async def _get_tool_headers(self, tool: str) -> Dict[str, str]:
        """Get authentication headers for tool"""
        tool_config = self.tools_config.get(tool)
        
        if tool == 'slack':
            return {
                'Authorization': f'Bearer {tool_config["bot_token"]}',
                'Content-Type': 'application/json'
            }
        elif tool == 'trello':
            return {
                'Authorization': f'OAuth oauth_consumer_key="{tool_config["api_key"]}", oauth_token="{tool_config["token"]}"',
                'Content-Type': 'application/json'
            }
        elif tool == 'asana':
            return {
                'Authorization': f'Bearer {tool_config["access_token"]}',
                'Content-Type': 'application/json'
            }
        elif tool == 'notion':
            return {
                'Authorization': f'Bearer {tool_config["integration_token"]}',
                'Content-Type': 'application/json',
                'Notion-Version': '2022-06-28'
            }
        elif tool == 'github':
            return {
                'Authorization': f'token {tool_config["access_token"]}',
                'Content-Type': 'application/json',
                'Accept': 'application/vnd.github.v3+json'
            }
        else:
            return {
                'Authorization': f'Bearer {tool_config.get("api_token", "")}',
                'Content-Type': 'application/json'
            }

    # Project Management
    async def create_project(self, project_data: Dict[str, Any]) -> Project:
        """
        Create a new project with team collaboration setup.
        
        Args:
            project_data: Project configuration
            
        Returns:
            Created Project object
        """
        required_fields = ['name', 'creator_id']
        for field in required_fields:
            if field not in project_data:
                raise CollaborationToolsError(f"Missing required field: {field}")
        
        project = Project(
            project_id=str(uuid.uuid4()),
            name=project_data['name'],
            creator_id=project_data['creator_id']
        )
        
        project.description = project_data.get('description', '')
        project.deadline = datetime.fromisoformat(project_data['deadline']) if project_data.get('deadline') else None
        project.budget = project_data.get('budget', 0.0)
        
        # Setup project in external tools
        tool_integrations = {}
        
        # Create Trello board if enabled
        if project_data.get('create_trello_board', False):
            trello_board = await self._create_trello_board(project)
            tool_integrations['trello'] = trello_board
        
        # Create Asana project if enabled
        if project_data.get('create_asana_project', False):
            asana_project = await self._create_asana_project(project)
            tool_integrations['asana'] = asana_project
        
        # Create Notion workspace if enabled
        if project_data.get('create_notion_workspace', False):
            notion_workspace = await self._create_notion_workspace(project)
            tool_integrations['notion'] = notion_workspace
        
        # Create Slack channel if enabled
        if project_data.get('create_slack_channel', False):
            slack_channel = await self._create_slack_channel(project)
            tool_integrations['slack'] = slack_channel
        
        # Create GitHub repository if enabled
        if project_data.get('create_github_repo', False):
            github_repo = await self._create_github_repository(project)
            tool_integrations['github'] = github_repo
        
        project.tool_integrations = tool_integrations
        
        # Add initial team members
        if project_data.get('team_members'):
            for member_data in project_data['team_members']:
                team_member = await self.add_team_member(project.project_id, member_data)
                project.team_members.append(team_member)
        
        # Create initial project structure
        await self._setup_project_structure(project, project_data)
        
        # Store project
        self.active_projects[project.project_id] = project
        
        logger.info(f"Created project: {project.project_id} with {len(tool_integrations)} tool integrations")
        return project

    async def get_project(self, project_id: str) -> Project:
        """
        Get project details with current status.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project object
        """
        if project_id in self.active_projects:
            project = self.active_projects[project_id]
        else:
            project = await self._fetch_project_from_storage(project_id)
        
        # Update project status from external tools
        await self._sync_project_status(project)
        
        return project

    async def update_project(self, project_id: str, updates: Dict[str, Any]) -> Project:
        """
        Update project information and sync with external tools.
        
        Args:
            project_id: Project ID
            updates: Project updates
            
        Returns:
            Updated Project object
        """
        project = await self.get_project(project_id)
        
        # Apply updates
        for field, value in updates.items():
            if hasattr(project, field):
                setattr(project, field, value)
        
        # Sync updates with external tools
        await self._sync_project_updates(project, updates)
        
        logger.info(f"Updated project: {project_id}")
        return project

    # Task Management
    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        """
        Create a new task and sync with external tools.
        
        Args:
            task_data: Task configuration
            
        Returns:
            Created Task object
        """
        required_fields = ['project_id', 'title']
        for field in required_fields:
            if field not in task_data:
                raise CollaborationToolsError(f"Missing required field: {field}")
        
        task = Task(
            task_id=str(uuid.uuid4()),
            project_id=task_data['project_id'],
            title=task_data['title']
        )
        
        task.description = task_data.get('description', '')
        task.assignee_id = task_data.get('assignee_id', '')
        task.priority = task_data.get('priority', 'medium')
        task.due_date = datetime.fromisoformat(task_data['due_date']) if task_data.get('due_date') else None
        task.estimated_hours = task_data.get('estimated_hours', 0)
        task.tags = task_data.get('tags', [])
        
        # Get project to access tool integrations
        project = await self.get_project(task.project_id)
        
        # Create task in external tools
        tool_tasks = {}
        
        # Create Trello card
        if 'trello' in project.tool_integrations:
            trello_card = await self._create_trello_card(task, project.tool_integrations['trello'])
            tool_tasks['trello'] = trello_card
        
        # Create Asana task
        if 'asana' in project.tool_integrations:
            asana_task = await self._create_asana_task(task, project.tool_integrations['asana'])
            tool_tasks['asana'] = asana_task
        
        # Create Notion page
        if 'notion' in project.tool_integrations:
            notion_page = await self._create_notion_task(task, project.tool_integrations['notion'])
            tool_tasks['notion'] = notion_page
        
        # Create GitHub issue
        if 'github' in project.tool_integrations:
            github_issue = await self._create_github_issue(task, project.tool_integrations['github'])
            tool_tasks['github'] = github_issue
        
        task.tool_references = tool_tasks
        
        # Add to project
        project.tasks.append(task)
        
        # Send notifications
        await self._send_task_notifications(task, 'created')
        
        logger.info(f"Created task: {task.task_id} in project {task.project_id}")
        return task

    async def update_task_status(self, task_id: str, status: str, updates: Dict[str, Any] = None) -> Task:
        """
        Update task status and sync with external tools.
        
        Args:
            task_id: Task ID
            status: New task status
            updates: Additional task updates
            
        Returns:
            Updated Task object
        """
        task = await self._get_task(task_id)
        old_status = task.status
        
        task.status = status
        if status == 'completed':
            task.completed_at = datetime.utcnow()
        
        # Apply additional updates
        if updates:
            for field, value in updates.items():
                if hasattr(task, field):
                    setattr(task, field, value)
        
        # Sync with external tools
        await self._sync_task_status(task)
        
        # Send notifications if status changed significantly
        if old_status != status:
            await self._send_task_notifications(task, 'status_changed')
        
        # Update project progress
        await self._update_project_progress(task.project_id)
        
        logger.info(f"Updated task {task_id} status from {old_status} to {status}")
        return task

    # Team Management
    async def add_team_member(self, project_id: str, member_data: Dict[str, Any]) -> TeamMember:
        """
        Add a team member to a project.
        
        Args:
            project_id: Project ID
            member_data: Team member information
            
        Returns:
            TeamMember object
        """
        required_fields = ['user_id', 'role']
        for field in required_fields:
            if field not in member_data:
                raise CollaborationToolsError(f"Missing required field: {field}")
        
        member = TeamMember(
            member_id=str(uuid.uuid4()),
            user_id=member_data['user_id'],
            role=member_data['role']
        )
        
        member.permissions = member_data.get('permissions', [])
        
        # Get project
        project = await self.get_project(project_id)
        
        # Add member to external tools
        await self._add_member_to_tools(member, project)
        
        # Add to project
        project.team_members.append(member)
        
        # Send welcome notifications
        await self._send_welcome_notifications(member, project)
        
        logger.info(f"Added team member {member.user_id} to project {project_id}")
        return member

    async def get_team_analytics(self, project_id: str) -> Dict[str, Any]:
        """
        Get comprehensive team analytics for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Team analytics data
        """
        project = await self.get_project(project_id)
        
        # Calculate team metrics
        total_members = len(project.team_members)
        active_members = len([m for m in project.team_members if m.status == 'active'])
        
        # Analyze task distribution
        task_distribution = await self._analyze_task_distribution(project)
        
        # Calculate performance metrics
        performance_metrics = await self._calculate_team_performance(project)
        
        # Analyze collaboration patterns
        collaboration_patterns = await self._analyze_collaboration_patterns(project)
        
        analytics = {
            'project_id': project_id,
            'team_overview': {
                'total_members': total_members,
                'active_members': active_members,
                'roles_distribution': await self._get_roles_distribution(project.team_members),
                'average_workload': sum(m.workload for m in project.team_members) / total_members if total_members > 0 else 0
            },
            'productivity_metrics': {
                'tasks_completed': len([t for t in project.tasks if t.status == 'completed']),
                'tasks_in_progress': len([t for t in project.tasks if t.status == 'in_progress']),
                'average_task_completion_time': performance_metrics['avg_completion_time'],
                'team_velocity': performance_metrics['velocity'],
                'burndown_rate': performance_metrics['burndown_rate']
            },
            'collaboration_insights': {
                'communication_frequency': collaboration_patterns['communication_frequency'],
                'cross_functional_collaboration': collaboration_patterns['cross_functional'],
                'knowledge_sharing_score': collaboration_patterns['knowledge_sharing'],
                'team_cohesion_index': collaboration_patterns['cohesion_index']
            },
            'workload_analysis': {
                'workload_distribution': task_distribution['workload_distribution'],
                'bottlenecks': task_distribution['bottlenecks'],
                'capacity_utilization': task_distribution['capacity_utilization'],
                'workload_balance_score': task_distribution['balance_score']
            },
            'optimization_recommendations': {
                'workflow_improvements': await self._suggest_workflow_improvements(project),
                'team_optimization': await self._suggest_team_optimization(project),
                'tool_usage_optimization': await self._analyze_tool_usage_optimization(project),
                'communication_improvements': await self._suggest_communication_improvements(project)
            }
        }
        
        return analytics

    # Document Management
    async def create_document(self, document_data: Dict[str, Any]) -> Document:
        """
        Create a shared document for collaboration.
        
        Args:
            document_data: Document configuration
            
        Returns:
            Created Document object
        """
        required_fields = ['project_id', 'title']
        for field in required_fields:
            if field not in document_data:
                raise CollaborationToolsError(f"Missing required field: {field}")
        
        document = Document(
            document_id=str(uuid.uuid4()),
            project_id=document_data['project_id'],
            title=document_data['title']
        )
        
        document.content = document_data.get('content', '')
        document.file_type = document_data.get('file_type', 'markdown')
        document.created_by = document_data.get('created_by', '')
        
        # Get project
        project = await self.get_project(document.project_id)
        
        # Create document in external tools
        tool_documents = {}
        
        # Create Notion page
        if 'notion' in project.tool_integrations:
            notion_page = await self._create_notion_document(document, project.tool_integrations['notion'])
            tool_documents['notion'] = notion_page
        
        # Create Google Docs if configured
        if 'google_workspace' in project.tool_integrations:
            google_doc = await self._create_google_document(document, project.tool_integrations['google_workspace'])
            tool_documents['google_docs'] = google_doc
        
        document.tool_references = tool_documents
        
        logger.info(f"Created document: {document.document_id} in project {document.project_id}")
        return document

    # Workflow Automation
    async def setup_workflow_automation(self, project_id: str, automation_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Setup automated workflows for project management.
        
        Args:
            project_id: Project ID
            automation_config: Automation configuration
            
        Returns:
            Automation setup result
        """
        project = await self.get_project(project_id)
        
        automation_setup = {
            'project_id': project_id,
            'enabled_automations': [],
            'triggers': [],
            'actions': []
        }
        
        # Setup task automation
        if automation_config.get('automate_tasks', False):
            task_automation = await self._setup_task_automation(project, automation_config.get('task_config', {}))
            automation_setup['enabled_automations'].append('task_automation')
            automation_setup['triggers'].extend(task_automation['triggers'])
            automation_setup['actions'].extend(task_automation['actions'])
        
        # Setup notification automation
        if automation_config.get('automate_notifications', False):
            notification_automation = await self._setup_notification_automation(project, automation_config.get('notification_config', {}))
            automation_setup['enabled_automations'].append('notification_automation')
            automation_setup['triggers'].extend(notification_automation['triggers'])
            automation_setup['actions'].extend(notification_automation['actions'])
        
        # Setup reporting automation
        if automation_config.get('automate_reporting', False):
            reporting_automation = await self._setup_reporting_automation(project, automation_config.get('reporting_config', {}))
            automation_setup['enabled_automations'].append('reporting_automation')
            automation_setup['triggers'].extend(reporting_automation['triggers'])
            automation_setup['actions'].extend(reporting_automation['actions'])
        
        # Setup integration sync automation
        if automation_config.get('automate_sync', False):
            sync_automation = await self._setup_sync_automation(project, automation_config.get('sync_config', {}))
            automation_setup['enabled_automations'].append('sync_automation')
            automation_setup['triggers'].extend(sync_automation['triggers'])
            automation_setup['actions'].extend(sync_automation['actions'])
        
        return automation_setup

    # Helper Methods for Enhanced Functionality
    async def _create_trello_board(self, project: Project) -> Dict[str, Any]:
        """Create Trello board for project"""
        board_data = {
            'name': project.name,
            'desc': project.description,
            'defaultLists': False
        }
        
        response = await self._make_tool_request('trello', 'POST', '/1/boards', data=board_data)
        
        # Create default lists
        lists_to_create = ['To Do', 'In Progress', 'Review', 'Done']
        for list_name in lists_to_create:
            await self._make_tool_request('trello', 'POST', '/1/lists', data={
                'name': list_name,
                'idBoard': response['id']
            })
        
        return {
            'board_id': response['id'],
            'board_url': response['url'],
            'board_name': response['name']
        }

    async def _create_asana_project(self, project: Project) -> Dict[str, Any]:
        """Create Asana project"""
        project_data = {
            'name': project.name,
            'notes': project.description,
            'team': self.tools_config['asana'].get('team_id')
        }
        
        response = await self._make_tool_request('asana', 'POST', '/projects', data={'data': project_data})
        
        return {
            'project_id': response['data']['gid'],
            'project_url': response['data']['permalink_url'],
            'project_name': response['data']['name']
        }

    async def _create_notion_workspace(self, project: Project) -> Dict[str, Any]:
        """Create Notion workspace for project"""
        page_data = {
            'parent': {'database_id': self.tools_config['notion'].get('database_id')},
            'properties': {
                'Name': {'title': [{'text': {'content': project.name}}]},
                'Description': {'rich_text': [{'text': {'content': project.description}}]}
            }
        }
        
        response = await self._make_tool_request('notion', 'POST', '/pages', data=page_data)
        
        return {
            'page_id': response['id'],
            'page_url': response['url'],
            'page_title': project.name
        }

    async def _create_slack_channel(self, project: Project) -> Dict[str, Any]:
        """Create Slack channel for project"""
        channel_name = f"project-{project.name.lower().replace(' ', '-')}"
        
        channel_data = {
            'name': channel_name,
            'purpose': project.description,
            'is_private': False
        }
        
        response = await self._make_tool_request('slack', 'POST', '/conversations.create', data=channel_data)
        
        return {
            'channel_id': response['channel']['id'],
            'channel_name': response['channel']['name'],
            'channel_url': f"https://slack.com/channels/{response['channel']['id']}"
        }

    async def _create_github_repository(self, project: Project) -> Dict[str, Any]:
        """Create GitHub repository for project"""
        repo_data = {
            'name': project.name.lower().replace(' ', '-'),
            'description': project.description,
            'private': True,
            'has_issues': True,
            'has_projects': True,
            'has_wiki': True
        }
        
        response = await self._make_tool_request('github', 'POST', '/user/repos', data=repo_data)
        
        return {
            'repo_id': response['id'],
            'repo_url': response['html_url'],
            'repo_name': response['full_name']
        }

    # Additional helper methods for comprehensive functionality...

# Example usage and testing
async def main() -> None:
    """Example usage of Collaboration Tools integration"""
    
    # Initialize the service
    tools_config = {
        'slack': {
            'base_url': 'https://slack.com/api',
            'bot_token': 'xoxb-your-bot-token'
        },
        'trello': {
            'base_url': 'https://api.trello.com',
            'api_key': 'your_trello_api_key',
            'token': 'your_trello_token'
        },
        'asana': {
            'base_url': 'https://app.asana.com/api/1.0',
            'access_token': 'your_asana_token',
            'team_id': 'your_team_id'
        },
        'notion': {
            'base_url': 'https://api.notion.com/v1',
            'integration_token': 'your_notion_token',
            'database_id': 'your_database_id'
        },
        'github': {
            'base_url': 'https://api.github.com',
            'access_token': 'your_github_token'
        }
    }
    
    collaboration_tools = CollaborationTools(tools_config)
    
    async with collaboration_tools:
        try:
            # Create a creator project
            project_data = {
                'name': 'Q1 Content Campaign',
                'creator_id': 'creator_123',
                'description': 'Quarterly content creation and distribution campaign',
                'deadline': '2025-03-31T23:59:59',
                'budget': 5000.0,
                'create_trello_board': True,
                'create_slack_channel': True,
                'create_notion_workspace': True,
                'team_members': [
                    {'user_id': 'editor_456', 'role': 'editor'},
                    {'user_id': 'designer_789', 'role': 'collaborator'}
                ]
            }
            
            project = await collaboration_tools.create_project(project_data)
            print(f"Created project: {project.name}")
            print(f"Tool integrations: {list(project.tool_integrations.keys())}")
            
            # Create a task
            task_data = {
                'project_id': project.project_id,
                'title': 'Create video script for Episode 1',
                'description': 'Write engaging script for the first episode of the series',
                'assignee_id': 'editor_456',
                'priority': 'high',
                'due_date': '2025-02-15T17:00:00',
                'estimated_hours': 8,
                'tags': ['content', 'video', 'script']
            }
            
            task = await collaboration_tools.create_task(task_data)
            print(f"Created task: {task.title}")
            
            # Setup workflow automation
            automation_config = {
                'automate_tasks': True,
                'automate_notifications': True,
                'automate_reporting': True,
                'task_config': {
                    'auto_assign_based_on_skills': True,
                    'auto_update_progress': True
                },
                'notification_config': {
                    'deadline_reminders': True,
                    'status_updates': True
                }
            }
            
            automation = await collaboration_tools.setup_workflow_automation(project.project_id, automation_config)
            print(f"Setup automation with {len(automation['enabled_automations'])} features")
            
            logger.info("Collaboration Tools integration example completed successfully")
            
        except CollaborationToolsError as e:
            logger.error(f"Collaboration Tools error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run example
    asyncio.run(main())