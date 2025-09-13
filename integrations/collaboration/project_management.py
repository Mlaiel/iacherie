"""
Project Management - Collaboration Module
=========================================
Gestion avancée de projets collaboratifs pour créateurs.
Workflow automation, task assignment, deadline tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class ProjectStatus(Enum):
    """Statuts de projet."""
    PLANNING = "planning"
    ACTIVE = "active"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class TaskStatus(Enum):
    """Statuts de tâche."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class TaskPriority(Enum):
    """Priorités de tâche."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class ProjectMember:
    """Membre d'un projet."""
    user_id: str
    name: str
    role: str
    permissions: List[str]
    joined_at: datetime
    contribution_score: float = 0.0

@dataclass
class Task:
    """Tâche de projet."""
    task_id: str
    title: str
    description: str
    assignee_id: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None

@dataclass
class Project:
    """Projet collaboratif."""
    project_id: str
    title: str
    description: str
    creator_id: str
    members: List[ProjectMember]
    status: ProjectStatus
    created_at: datetime
    deadline: Optional[datetime]
    tasks: List[Task] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    progress: float = 0.0

class ProjectManagement:
    """
    Gestionnaire de projets collaboratifs.
    Gestion complète workflow, tasks et deadlines.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialise le gestionnaire de projets."""
        self.config = config or {}
        self.projects: Dict[str, Project] = {}
        self.user_projects: Dict[str, Set[str]] = {}  # user_id -> project_ids
        self.task_dependencies: Dict[str, List[str]] = {}
        logger.info("Project Management initialisé")
    
    async def create_project(
        self,
        title: str,
        description: str,
        creator_id: str,
        deadline: Optional[datetime] = None,
        metadata: Dict[str, Any] = None
    ) -> Project:
        """Crée un nouveau projet collaboratif."""
        project_id = str(uuid.uuid4())
        
        creator_member = ProjectMember(
            user_id=creator_id,
            name="Project Creator",  # À récupérer via user service
            role="owner",
            permissions=["all"],
            joined_at=datetime.now()
        )
        
        project = Project(
            project_id=project_id,
            title=title,
            description=description,
            creator_id=creator_id,
            members=[creator_member],
            status=ProjectStatus.PLANNING,
            created_at=datetime.now(),
            deadline=deadline,
            metadata=metadata or {}
        )
        
        self.projects[project_id] = project
        
        # Track user projects
        if creator_id not in self.user_projects:
            self.user_projects[creator_id] = set()
        self.user_projects[creator_id].add(project_id)
        
        logger.info(f"Projet créé: {project_id} - {title}")
        return project
    
    async def add_member(
        self,
        project_id: str,
        user_id: str,
        name: str,
        role: str = "member",
        permissions: List[str] = None
    ) -> bool:
        """Ajoute un membre au projet."""
        if project_id not in self.projects:
            logger.error(f"Projet {project_id} introuvable")
            return False
        
        project = self.projects[project_id]
        
        # Vérifier si utilisateur déjà membre
        for member in project.members:
            if member.user_id == user_id:
                logger.warning(f"Utilisateur {user_id} déjà membre du projet")
                return False
        
        member = ProjectMember(
            user_id=user_id,
            name=name,
            role=role,
            permissions=permissions or ["read", "write"],
            joined_at=datetime.now()
        )
        
        project.members.append(member)
        
        # Track user projects
        if user_id not in self.user_projects:
            self.user_projects[user_id] = set()
        self.user_projects[user_id].add(project_id)
        
        logger.info(f"Membre {user_id} ajouté au projet {project_id}")
        return True
    
    async def create_task(
        self,
        project_id: str,
        title: str,
        description: str,
        assignee_id: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        dependencies: List[str] = None,
        estimated_hours: Optional[float] = None
    ) -> Optional[Task]:
        """Crée une nouvelle tâche."""
        if project_id not in self.projects:
            logger.error(f"Projet {project_id} introuvable")
            return None
        
        project = self.projects[project_id]
        
        # Vérifier si assignee est membre du projet
        if assignee_id:
            member_ids = [m.user_id for m in project.members]
            if assignee_id not in member_ids:
                logger.error(f"Assignee {assignee_id} pas membre du projet")
                return None
        
        task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            assignee_id=assignee_id,
            status=TaskStatus.TODO,
            priority=priority,
            created_at=datetime.now(),
            due_date=due_date,
            dependencies=dependencies or [],
            estimated_hours=estimated_hours
        )
        
        project.tasks.append(task)
        
        # Track dependencies
        if dependencies:
            self.task_dependencies[task_id] = dependencies
        
        # Recalculer progress du projet
        await self._update_project_progress(project_id)
        
        logger.info(f"Tâche créée: {task_id} - {title}")
        return task
    
    async def update_task_status(
        self,
        project_id: str,
        task_id: str,
        new_status: TaskStatus,
        user_id: str,
        actual_hours: Optional[float] = None
    ) -> bool:
        """Met à jour le statut d'une tâche."""
        if project_id not in self.projects:
            return False
        
        project = self.projects[project_id]
        task = self._find_task(project, task_id)
        
        if not task:
            logger.error(f"Tâche {task_id} introuvable")
            return False
        
        # Vérifier permissions
        if not self._user_can_update_task(project, user_id, task):
            logger.error(f"Utilisateur {user_id} pas autorisé à modifier tâche")
            return False
        
        # Vérifier dépendances pour certains statuts
        if new_status in [TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]:
            if not await self._check_dependencies_met(project, task):
                logger.error(f"Dépendances non satisfaites pour tâche {task_id}")
                return False
        
        old_status = task.status
        task.status = new_status
        
        if new_status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
        
        if actual_hours:
            task.actual_hours = actual_hours
        
        # Recalculer progress du projet
        await self._update_project_progress(project_id)
        
        logger.info(f"Tâche {task_id} status: {old_status.value} → {new_status.value}")
        return True
    
    async def assign_task(
        self,
        project_id: str,
        task_id: str,
        assignee_id: str,
        assigner_id: str
    ) -> bool:
        """Assigne une tâche à un membre."""
        if project_id not in self.projects:
            return False
        
        project = self.projects[project_id]
        task = self._find_task(project, task_id)
        
        if not task:
            return False
        
        # Vérifier que assignee est membre
        member_ids = [m.user_id for m in project.members]
        if assignee_id not in member_ids:
            logger.error(f"Assignee {assignee_id} pas membre du projet")
            return False
        
        # Vérifier permissions assigner
        if not self._user_can_assign_task(project, assigner_id):
            logger.error(f"Utilisateur {assigner_id} pas autorisé à assigner")
            return False
        
        old_assignee = task.assignee_id
        task.assignee_id = assignee_id
        
        logger.info(f"Tâche {task_id} assignée: {old_assignee} → {assignee_id}")
        return True
    
    async def get_project_dashboard(
        self,
        project_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retourne dashboard complet du projet."""
        if project_id not in self.projects:
            return None
        
        project = self.projects[project_id]
        
        # Statistiques des tâches
        task_stats = self._calculate_task_statistics(project)
        
        # Timeline et deadlines
        timeline = await self._generate_project_timeline(project)
        
        # Workload des membres
        member_workload = self._calculate_member_workload(project)
        
        # Risques et blockers
        risks = await self._identify_project_risks(project)
        
        return {
            "project": {
                "id": project.project_id,
                "title": project.title,
                "status": project.status.value,
                "progress": project.progress,
                "created_at": project.created_at.isoformat(),
                "deadline": project.deadline.isoformat() if project.deadline else None
            },
            "members": [
                {
                    "user_id": m.user_id,
                    "name": m.name,
                    "role": m.role,
                    "contribution_score": m.contribution_score
                }
                for m in project.members
            ],
            "task_statistics": task_stats,
            "timeline": timeline,
            "member_workload": member_workload,
            "risks": risks
        }
    
    async def get_user_dashboard(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Retourne dashboard utilisateur."""
        if user_id not in self.user_projects:
            return {
                "user_id": user_id,
                "projects": [],
                "tasks": [],
                "workload": {}
            }
        
        user_project_ids = self.user_projects[user_id]
        user_projects = []
        user_tasks = []
        
        for project_id in user_project_ids:
            if project_id in self.projects:
                project = self.projects[project_id]
                user_projects.append({
                    "project_id": project_id,
                    "title": project.title,
                    "status": project.status.value,
                    "progress": project.progress,
                    "role": self._get_user_role(project, user_id)
                })
                
                # Tâches assignées à l'utilisateur
                assigned_tasks = [
                    task for task in project.tasks 
                    if task.assignee_id == user_id
                ]
                
                for task in assigned_tasks:
                    user_tasks.append({
                        "task_id": task.task_id,
                        "project_id": project_id,
                        "title": task.title,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "due_date": task.due_date.isoformat() if task.due_date else None
                    })
        
        # Calculer workload
        workload = self._calculate_user_workload(user_tasks)
        
        return {
            "user_id": user_id,
            "projects": user_projects,
            "tasks": user_tasks,
            "workload": workload
        }
    
    def _find_task(self, project: Project, task_id: str) -> Optional[Task]:
        """Trouve une tâche dans un projet."""
        for task in project.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def _user_can_update_task(
        self, project: Project, user_id: str, task: Task
    ) -> bool:
        """Vérifie si utilisateur peut modifier une tâche."""
        # Propriétaire du projet peut tout modifier
        if project.creator_id == user_id:
            return True
        
        # Assignee peut modifier sa tâche
        if task.assignee_id == user_id:
            return True
        
        # Vérifier permissions membre
        for member in project.members:
            if member.user_id == user_id:
                return "write" in member.permissions or "all" in member.permissions
        
        return False
    
    def _user_can_assign_task(self, project: Project, user_id: str) -> bool:
        """Vérifie si utilisateur peut assigner des tâches."""
        if project.creator_id == user_id:
            return True
        
        for member in project.members:
            if member.user_id == user_id:
                return member.role in ["owner", "admin"] or "all" in member.permissions
        
        return False
    
    async def _check_dependencies_met(
        self, project: Project, task: Task
    ) -> bool:
        """Vérifie si les dépendances d'une tâche sont satisfaites."""
        if not task.dependencies:
            return True
        
        for dep_task_id in task.dependencies:
            dep_task = self._find_task(project, dep_task_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    async def _update_project_progress(self, project_id: str):
        """Met à jour le progress d'un projet."""
        if project_id not in self.projects:
            return
        
        project = self.projects[project_id]
        
        if not project.tasks:
            project.progress = 0.0
            return
        
        completed_tasks = len([
            task for task in project.tasks 
            if task.status == TaskStatus.COMPLETED
        ])
        
        project.progress = completed_tasks / len(project.tasks)
        
        # Mettre à jour statut projet si nécessaire
        if project.progress == 1.0 and project.status == ProjectStatus.ACTIVE:
            project.status = ProjectStatus.COMPLETED
    
    def _calculate_task_statistics(self, project: Project) -> Dict[str, Any]:
        """Calcule statistiques des tâches."""
        if not project.tasks:
            return {"total": 0}
        
        status_counts = {}
        priority_counts = {}
        
        for task in project.tasks:
            status = task.status.value
            priority = task.priority.value
            
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        overdue_tasks = [
            task for task in project.tasks
            if task.due_date and task.due_date < datetime.now() 
            and task.status != TaskStatus.COMPLETED
        ]
        
        return {
            "total": len(project.tasks),
            "by_status": status_counts,
            "by_priority": priority_counts,
            "overdue": len(overdue_tasks),
            "completion_rate": project.progress
        }
    
    async def _generate_project_timeline(self, project: Project) -> List[Dict[str, Any]]:
        """Génère timeline du projet."""
        timeline_events = []
        
        # Milestones basés sur les tâches avec deadline
        tasks_with_deadlines = [
            task for task in project.tasks 
            if task.due_date
        ]
        
        tasks_with_deadlines.sort(key=lambda t: t.due_date)
        
        for task in tasks_with_deadlines:
            timeline_events.append({
                "date": task.due_date.isoformat(),
                "type": "task_deadline",
                "title": f"Deadline: {task.title}",
                "status": task.status.value,
                "priority": task.priority.value
            })
        
        return timeline_events
    
    def _calculate_member_workload(self, project: Project) -> Dict[str, Any]:
        """Calcule workload des membres."""
        member_workload = {}
        
        for member in project.members:
            assigned_tasks = [
                task for task in project.tasks
                if task.assignee_id == member.user_id
            ]
            
            total_estimated = sum(
                task.estimated_hours or 0 
                for task in assigned_tasks
            )
            
            pending_tasks = [
                task for task in assigned_tasks
                if task.status not in [TaskStatus.COMPLETED]
            ]
            
            member_workload[member.user_id] = {
                "name": member.name,
                "total_tasks": len(assigned_tasks),
                "pending_tasks": len(pending_tasks),
                "estimated_hours": total_estimated,
                "workload_level": self._assess_workload_level(total_estimated)
            }
        
        return member_workload
    
    async def _identify_project_risks(self, project: Project) -> List[Dict[str, Any]]:
        """Identifie les risques du projet."""
        risks = []
        
        # Risque deadline
        if project.deadline and project.deadline < datetime.now() + timedelta(days=7):
            if project.progress < 0.8:
                risks.append({
                    "type": "deadline_risk",
                    "severity": "high",
                    "description": "Projet risque de dépasser deadline",
                    "recommendation": "Prioriser tâches critiques"
                })
        
        # Risque blockers
        blocked_tasks = [
            task for task in project.tasks
            if task.status == TaskStatus.BLOCKED
        ]
        
        if blocked_tasks:
            risks.append({
                "type": "blocked_tasks",
                "severity": "medium",
                "description": f"{len(blocked_tasks)} tâches bloquées",
                "recommendation": "Résoudre blockers en priorité"
            })
        
        # Risque workload
        overloaded_members = [
            member_id for member_id, workload in self._calculate_member_workload(project).items()
            if workload["workload_level"] == "high"
        ]
        
        if overloaded_members:
            risks.append({
                "type": "workload_imbalance",
                "severity": "medium", 
                "description": "Certains membres surchargés",
                "recommendation": "Rééquilibrer distribution tâches"
            })
        
        return risks
    
    def _get_user_role(self, project: Project, user_id: str) -> str:
        """Retourne le rôle d'un utilisateur dans le projet."""
        for member in project.members:
            if member.user_id == user_id:
                return member.role
        return "unknown"
    
    def _calculate_user_workload(self, user_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule workload d'un utilisateur."""
        pending_tasks = [
            task for task in user_tasks
            if task["status"] not in ["completed"]
        ]
        
        urgent_tasks = [
            task for task in pending_tasks
            if task["priority"] == "urgent"
        ]
        
        return {
            "total_tasks": len(user_tasks),
            "pending_tasks": len(pending_tasks),
            "urgent_tasks": len(urgent_tasks),
            "workload_level": self._assess_workload_level(len(pending_tasks))
        }
    
    def _assess_workload_level(self, workload_value: float) -> str:
        """Évalue le niveau de workload."""
        if workload_value > 40:  # Plus de 40h ou tâches
            return "high"
        elif workload_value > 20:
            return "medium"
        else:
            return "low"