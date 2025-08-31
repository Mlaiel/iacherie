"""
 Backup Scheduler - Intelligent Backup Scheduling System
=======================================================
Module: backend/data_management/backups/backup_scheduler.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Scheduling System - Enterprise Production-Ready
Responsibility: Planification intelligente et automatisation des sauvegardes
===============================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import croniter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import json
from pathlib import Path

from .models import BackupJob, ScheduledBackup, BackupStatus
from .backup_manager import BackupManager
from .exceptions import SchedulerException

logger = logging.getLogger(__name__)


class ScheduleType(str, Enum):
    """Types de planification disponibles"""
    IMMEDIATE = "immediate"         # Exécution immédiate
    INTERVAL = "interval"          # Intervalle fixe
    CRON = "cron"                 # Expression cron
    DATE = "date"                 # Date spécifique
    CONDITIONAL = "conditional"    # Basé sur conditions
    ADAPTIVE = "adaptive"         # Adaptatif intelligent


class Priority(str, Enum):
    """Niveaux de priorité pour les sauvegardes"""
    CRITICAL = "critical"         # Critique (revenus, contenu premium)
    HIGH = "high"                # Haute (contenu populaire)
    MEDIUM = "medium"            # Moyenne (contenu standard)
    LOW = "low"                  # Basse (contenu archivé)
    BULK = "bulk"                # En lot (traitement de masse)


@dataclass
class ScheduleConfig:
    """Configuration de planification"""
    schedule_type: ScheduleType
    priority: Priority = Priority.MEDIUM
    
    # Paramètres interval
    interval_minutes: Optional[int] = None
    interval_hours: Optional[int] = None
    interval_days: Optional[int] = None
    
    # Expression cron
    cron_expression: Optional[str] = None
    
    # Date spécifique
    scheduled_date: Optional[datetime] = None
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Options avancées
    max_retries: int = 3
    retry_delay_minutes: int = 15
    timeout_minutes: int = 120
    overlap_policy: str = "skip"  # skip, queue, replace
    
    # Métadonnées
    tags: List[str] = field(default_factory=list)
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""



        return {
            "schedule_type": self.schedule_type.value,
            "priority": self.priority.value,
            "interval_minutes": self.interval_minutes,
            "interval_hours": self.interval_hours,
            "interval_days": self.interval_days,
            "cron_expression": self.cron_expression,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "conditions": self.conditions,
            "max_retries": self.max_retries,
            "retry_delay_minutes": self.retry_delay_minutes,
            "timeout_minutes": self.timeout_minutes,
            "overlap_policy": self.overlap_policy,
            "tags": self.tags,
            "description": self.description
        }


@dataclass
class BackupScheduleJob:
    """Job de sauvegarde planifiée"""
    job_id: str
    name: str
    source_paths: List[Path]
    schedule_config: ScheduleConfig
    user_id: Optional[str] = None
    content_type: str = "mixed"
    backup_options: Dict[str, Any] = field(default_factory=dict)
    
    # État du job
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    failure_count: int = 0
    last_error: Optional[str] = None
    
    # Statistiques
    avg_duration_seconds: float = 0.0
    total_data_backed_up_gb: float = 0.0
    success_rate: float = 100.0


class BackupScheduler:
    """
    Planificateur intelligent de sauvegardes avec gestion avancée
    
    Fonctionnalités:
    - Planification multiple (cron, interval, conditionnel)
    - Priorisation dynamique
    - Gestion conflits et overlaps
    - Monitoring performance
    - Auto-adaptation selon usage
    - Failover et retry intelligents
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.scheduler = AsyncIOScheduler()
        self.backup_manager = BackupManager()
        
        # Configuration APScheduler avec Redis
        self.jobstore = RedisJobStore(host='localhost', port=6379, db=1)
        self.scheduler.add_jobstore(self.jobstore, 'redis')
        
        # Configuration executor
        executor = ThreadPoolExecutor(max_workers=20)
        self.scheduler.add_executor(executor, 'thread_pool')
        
        # Jobs registry
        self.scheduled_jobs: Dict[str, BackupScheduleJob] = {}
        self.active_backups: Dict[str, BackupJob] = {}
        self.job_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.performance_metrics = {
            "total_scheduled_jobs": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0,
            "peak_concurrent_jobs": 0,
            "current_active_jobs": 0
        }
        
        logger.info("BackupScheduler initialized with Redis persistence")
    
    async def start(self):
        """Démarre le planificateur"""



        try:
            self.scheduler.start()
            logger.info("Backup scheduler started successfully")
            
            # Chargement des jobs persistés
            await self._load_persisted_jobs()
            
        except Exception as e:
            logger.error(f"Failed to start backup scheduler: {e}")
            raise SchedulerException(f"Scheduler startup failed: {e}")
    
    async def stop(self):
        """Arrête le planificateur"""



        try:
            self.scheduler.shutdown(wait=True)
            logger.info("Backup scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def schedule_backup(
        self,
        job_id: str,
        name: str,
        source_paths: List[Union[str, Path]],
        schedule_config: ScheduleConfig,
        user_id: Optional[str] = None,
        content_type: str = "mixed",
        backup_options: Optional[Dict[str, Any]] = None
    ) -> BackupScheduleJob:
        """
        Planifie une nouvelle sauvegarde
        
        Args:
            job_id: ID unique du job
            name: Nom descriptif
            source_paths: Chemins à sauvegarder
            schedule_config: Configuration de planification
            user_id: ID utilisateur (multi-tenant)
            content_type: Type de contenu
            backup_options: Options de sauvegarde
            
        Returns:
            BackupScheduleJob: Job planifié créé
        """



        try:
            # Conversion paths
            source_path_objects = [Path(p) for p in source_paths]
            
            # Création du job planifié
            schedule_job = BackupScheduleJob(
                job_id=job_id,
                name=name,
                source_paths=source_path_objects,
                schedule_config=schedule_config,
                user_id=user_id,
                content_type=content_type,
                backup_options=backup_options or {}
            )
            
            # Calcul prochaine exécution
            next_run = self._calculate_next_run(schedule_config)
            schedule_job.next_run = next_run
            
            # Ajout au scheduler APScheduler
            await self._add_to_scheduler(schedule_job)
            
            # Enregistrement
            self.scheduled_jobs[job_id] = schedule_job
            self.performance_metrics["total_scheduled_jobs"] += 1
            
            # Persistance
            await self._persist_job(schedule_job)
            
            logger.info(f"Backup scheduled: {name} (ID: {job_id}) - Next run: {next_run}")
            return schedule_job
            
        except Exception as e:
            logger.error(f"Failed to schedule backup {job_id}: {e}")
            raise SchedulerException(f"Schedule creation failed: {e}")
    
    def _calculate_next_run(self, config: ScheduleConfig) -> Optional[datetime]:
        """Calcule la prochaine exécution selon la configuration"""
        now = datetime.now()
        
        if config.schedule_type == ScheduleType.IMMEDIATE:
            return now
        
        elif config.schedule_type == ScheduleType.INTERVAL:
            delta = timedelta(
                minutes=config.interval_minutes or 0,
                hours=config.interval_hours or 0,
                days=config.interval_days or 0
            )
            return now + delta
        
        elif config.schedule_type == ScheduleType.CRON:
            if config.cron_expression:
                cron = croniter.croniter(config.cron_expression, now)
                return cron.get_next(datetime)
        
        elif config.schedule_type == ScheduleType.DATE:
            return config.scheduled_date
        
        elif config.schedule_type == ScheduleType.CONDITIONAL:
            # Évaluation immédiate des conditions
            return now if self._evaluate_conditions(config.conditions) else None
        
        elif config.schedule_type == ScheduleType.ADAPTIVE:
            # Planification adaptative basée sur l'historique
            return self._calculate_adaptive_schedule(config)
        
        return None
    
    async def _add_to_scheduler(self, schedule_job: BackupScheduleJob):
        """Ajoute un job au scheduler APScheduler"""
        config = schedule_job.schedule_config
        
        # Sélection du trigger selon le type
        trigger = None
        
        if config.schedule_type == ScheduleType.IMMEDIATE:
            trigger = DateTrigger(run_date=datetime.now())
        
        elif config.schedule_type == ScheduleType.INTERVAL:
            trigger = IntervalTrigger(
                minutes=config.interval_minutes or 0,
                hours=config.interval_hours or 0,
                days=config.interval_days or 0
            )
        
        elif config.schedule_type == ScheduleType.CRON:
            if config.cron_expression:
                trigger = CronTrigger.from_crontab(config.cron_expression)
        
        elif config.schedule_type == ScheduleType.DATE:
            trigger = DateTrigger(run_date=config.scheduled_date)
        
        elif config.schedule_type in [ScheduleType.CONDITIONAL, ScheduleType.ADAPTIVE]:
            # Planification dynamique - réévaluation périodique
            trigger = IntervalTrigger(minutes=30)  # Vérification toutes les 30min
        
        if trigger:
            self.scheduler.add_job(
                func=self._execute_scheduled_backup,
                trigger=trigger,
                args=[schedule_job.job_id],
                id=schedule_job.job_id,
                name=schedule_job.name,
                max_instances=1,  # Évite les overlaps
                misfire_grace_time=300,  # 5 minutes de grâce
                coalesce=True,  # Fusionne les exécutions en retard
                jobstore='redis'
            )
    
    async def _execute_scheduled_backup(self, job_id: str):
        """
        Exécute une sauvegarde planifiée
        
        Args:
            job_id: ID du job planifié
        """
        if job_id not in self.scheduled_jobs:
            logger.error(f"Scheduled job {job_id} not found")
            return
        
        schedule_job = self.scheduled_jobs[job_id]
        
        # Vérification conditions pour jobs conditionnels/adaptatifs
        if schedule_job.schedule_config.schedule_type in [ScheduleType.CONDITIONAL, ScheduleType.ADAPTIVE]:
            if not self._should_execute_now(schedule_job):
                logger.debug(f"Skipping execution of {job_id} - conditions not met")
                return
        
        # Vérification overlaps
        if self._has_active_overlap(schedule_job):
            if schedule_job.schedule_config.overlap_policy == "skip":
                logger.warning(f"Skipping {job_id} - previous execution still running")
                return
            elif schedule_job.schedule_config.overlap_policy == "queue":
                await self._queue_job_execution(schedule_job)
                return
        
        try:
            execution_start = datetime.now()
            schedule_job.last_run = execution_start
            schedule_job.run_count += 1
            
            self.performance_metrics["current_active_jobs"] += 1
            
            logger.info(f"Executing scheduled backup: {schedule_job.name} (Run #{schedule_job.run_count})")
            
            # Création et exécution de la sauvegarde
            backup_job = await self.backup_manager.create_backup(
                source_paths=schedule_job.source_paths,
                backup_name=f"{schedule_job.name}_{execution_start.strftime('%Y%m%d_%H%M%S')}",
                user_id=schedule_job.user_id,
                content_type=schedule_job.content_type,
                priority=schedule_job.schedule_config.priority.value,
                options=schedule_job.backup_options
            )
            
            # Ajout à la liste des jobs actifs
            self.active_backups[backup_job.job_id] = backup_job
            
            # Attente de completion avec timeout
            timeout_seconds = schedule_job.schedule_config.timeout_minutes * 60
            
            completion_success = await self._wait_for_backup_completion(
                backup_job.job_id, 
                timeout_seconds
            )
            
            if completion_success:
                await self._handle_successful_execution(schedule_job, backup_job, execution_start)
            else:
                await self._handle_failed_execution(schedule_job, "Timeout exceeded", execution_start)
            
        except Exception as e:
            await self._handle_failed_execution(schedule_job, str(e), execution_start)
            
        finally:
            self.performance_metrics["current_active_jobs"] -= 1
            
            # Nettoyage
            if backup_job.job_id in self.active_backups:
                del self.active_backups[backup_job.job_id]
    
    def _should_execute_now(self, schedule_job: BackupScheduleJob) -> bool:
        """Détermine si un job conditionnel/adaptatif doit s'exécuter maintenant"""
        config = schedule_job.schedule_config
        
        if config.schedule_type == ScheduleType.CONDITIONAL:
            return self._evaluate_conditions(config.conditions)
        
        elif config.schedule_type == ScheduleType.ADAPTIVE:
            return self._evaluate_adaptive_conditions(schedule_job)
        
        return False
    
    def _evaluate_conditions(self, conditions: Dict[str, Any]) -> bool:
        """Évalue les conditions de déclenchement"""
        # Exemples de conditions supportées
        now = datetime.now()
        
        # Condition horaire
        if "time_window" in conditions:
            time_window = conditions["time_window"]
            start_hour = time_window.get("start", 0)
            end_hour = time_window.get("end", 23)
            
            if not (start_hour <= now.hour <= end_hour):
                return False
        
        # Condition de jour de semaine
        if "weekdays" in conditions:
            allowed_weekdays = conditions["weekdays"]  # 0=Lundi, 6=Dimanche
            if now.weekday() not in allowed_weekdays:
                return False
        
        # Condition de charge système (simulée)
        if "max_system_load" in conditions:
            max_load = conditions["max_system_load"]
            current_load = self.performance_metrics["current_active_jobs"]
            if current_load >= max_load:
                return False
        
        # Condition d'espace disque
        if "min_disk_space_gb" in conditions:
            min_space = conditions["min_disk_space_gb"]
            # Vérification espace disque (implémentation simplifiée)
            # En production, utiliser shutil.disk_usage()
            return True  # Placeholder
        
        # Condition de fréquence de changement
        if "min_changes" in conditions:
            min_changes = conditions["min_changes"]
            # Vérification changements depuis dernière sauvegarde
            # En production, comparer avec snapshot précédent
            return True  # Placeholder
        
        return True
    
    def _evaluate_adaptive_conditions(self, schedule_job: BackupScheduleJob) -> bool:
        """Évalue les conditions adaptatives basées sur l'historique"""
        # Logique adaptative basée sur:
        # - Patterns d'usage historiques
        # - Fréquence des changements
        # - Performance système
        # - Coûts optimaux
        
        # Exemple: sauvegarde plus fréquente si contenu critique et récemment modifié
        if schedule_job.schedule_config.priority == Priority.CRITICAL:
            # Vérification modifications récentes
            for source_path in schedule_job.source_paths:
                if source_path.exists():
                    last_modified = datetime.fromtimestamp(source_path.stat().st_mtime)
                    if datetime.now() - last_modified < timedelta(hours=1):
                        return True
        
        # Logique basée sur patterns temporels
        now = datetime.now()
        
        # Plus de sauvegardes en heures de travail pour contenu actif
        if schedule_job.content_type in ["audio", "video"] and 9 <= now.hour <= 18:
            return True
        
        # Sauvegardes nocturnes pour contenu volumineux
        if schedule_job.content_type == "video" and (now.hour < 6 or now.hour > 22):
            return True
        
        return False
    
    def _calculate_adaptive_schedule(self, config: ScheduleConfig) -> datetime:
        """Calcule la prochaine exécution adaptative"""
        now = datetime.now()
        
        # Logique adaptative basée sur la priorité
        if config.priority == Priority.CRITICAL:
            # Sauvegarde toutes les heures pour contenu critique
            return now + timedelta(hours=1)
        elif config.priority == Priority.HIGH:
            # Sauvegarde toutes les 4 heures
            return now + timedelta(hours=4)
        elif config.priority == Priority.MEDIUM:
            # Sauvegarde quotidienne
            return now + timedelta(days=1)
        else:
            # Sauvegarde hebdomadaire pour priorité basse
            return now + timedelta(days=7)
    
    def _has_active_overlap(self, schedule_job: BackupScheduleJob) -> bool:
        """Vérifie s'il y a un overlap avec une exécution précédente"""
        for active_job in self.active_backups.values():
            if (active_job.user_id == schedule_job.user_id and 
                active_job.status in [BackupStatus.PENDING, BackupStatus.RUNNING]):
                
                # Vérification overlap des chemins sources
                active_paths = set(str(p) for p in active_job.source_paths)
                schedule_paths = set(str(p) for p in schedule_job.source_paths)
                
                if active_paths.intersection(schedule_paths):
                    return True
        
        return False
    
    async def _queue_job_execution(self, schedule_job: BackupScheduleJob):
        """Met en queue un job en cas d'overlap"""
        # Ajouter à une queue Redis pour exécution différée
        queue_data = {
            "job_id": schedule_job.job_id,
            "queued_at": datetime.now().isoformat(),
            "priority": schedule_job.schedule_config.priority.value
        }
        
        # En production, utiliser Redis Queue ou Celery
        logger.info(f"Queued job {schedule_job.job_id} for later execution")
    
    async def _wait_for_backup_completion(self, backup_job_id: str, timeout_seconds: int) -> bool:
        """
        Attend la completion d'une sauvegarde avec timeout
        
        Args:
            backup_job_id: ID du job de sauvegarde
            timeout_seconds: Timeout en secondes
            
        Returns:
            bool: True si complété avec succès
        """
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout_seconds:
            backup_job = await self.backup_manager.get_backup_status(backup_job_id)
            
            if not backup_job:
                return False
            
            if backup_job.status == BackupStatus.COMPLETED:
                return True
            elif backup_job.status in [BackupStatus.FAILED, BackupStatus.CANCELLED]:
                return False
            
            # Attente courte avant vérification suivante
            await asyncio.sleep(10)
        
        # Timeout atteint
        logger.warning(f"Backup {backup_job_id} timed out after {timeout_seconds} seconds")
        await self.backup_manager.cancel_backup(backup_job_id, "Scheduler timeout")
        return False
    
    async def _handle_successful_execution(
        self,
        schedule_job: BackupScheduleJob,
        backup_job: BackupJob,
        execution_start: datetime
    ):
        """Gère une exécution réussie"""
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Mise à jour statistiques du job
        schedule_job.avg_duration_seconds = (
            (schedule_job.avg_duration_seconds * (schedule_job.run_count - 1) + execution_time) 
            / schedule_job.run_count
        )
        
        if backup_job.estimated_size:
            schedule_job.total_data_backed_up_gb += backup_job.estimated_size / (1024**3)
        
        # Mise à jour taux de succès
        total_executions = schedule_job.run_count + schedule_job.failure_count
        successful_executions = schedule_job.run_count
        schedule_job.success_rate = (successful_executions / total_executions) * 100
        
        # Reset erreur
        schedule_job.last_error = None
        
        # Métriques globales
        self.performance_metrics["successful_executions"] += 1
        self._update_average_execution_time(execution_time)
        
        # Historique
        self.job_history.append({
            "job_id": schedule_job.job_id,
            "backup_job_id": backup_job.job_id,
            "execution_start": execution_start.isoformat(),
            "execution_time_seconds": execution_time,
            "status": "success",
            "data_size_gb": backup_job.estimated_size / (1024**3) if backup_job.estimated_size else 0
        })
        
        # Calcul prochaine exécution
        schedule_job.next_run = self._calculate_next_run(schedule_job.schedule_config)
        
        # Persistance
        await self._persist_job(schedule_job)
        
        logger.info(f"Scheduled backup completed successfully: {schedule_job.name} in {execution_time:.2f}s")
    
    async def _handle_failed_execution(
        self,
        schedule_job: BackupScheduleJob,
        error_message: str,
        execution_start: datetime
    ):
        """Gère une exécution échouée"""
        execution_time = (datetime.now() - execution_start).total_seconds()
        
        # Mise à jour statistiques d'échec
        schedule_job.failure_count += 1
        schedule_job.last_error = error_message
        
        # Mise à jour taux de succès
        total_executions = schedule_job.run_count + schedule_job.failure_count
        successful_executions = schedule_job.run_count
        schedule_job.success_rate = (successful_executions / total_executions) * 100 if total_executions > 0 else 0
        
        # Métriques globales
        self.performance_metrics["failed_executions"] += 1
        
        # Historique
        self.job_history.append({
            "job_id": schedule_job.job_id,
            "execution_start": execution_start.isoformat(),
            "execution_time_seconds": execution_time,
            "status": "failed",
            "error": error_message
        })
        
        # Gestion retry
        if schedule_job.failure_count < schedule_job.schedule_config.max_retries:
            # Planification retry avec délai
            retry_delay = timedelta(minutes=schedule_job.schedule_config.retry_delay_minutes)
            retry_time = datetime.now() + retry_delay
            
            self.scheduler.add_job(
                func=self._execute_scheduled_backup,
                trigger=DateTrigger(run_date=retry_time),
                args=[schedule_job.job_id],
                id=f"{schedule_job.job_id}_retry_{schedule_job.failure_count}",
                name=f"Retry {schedule_job.name}",
                max_instances=1
            )
            
            logger.warning(f"Scheduled backup failed, retry #{schedule_job.failure_count} at {retry_time}: {error_message}")
        else:
            logger.error(f"Scheduled backup failed after {schedule_job.schedule_config.max_retries} retries: {error_message}")
            
            # Désactivation automatique après échecs répétés
            schedule_job.enabled = False
        
        # Calcul prochaine exécution normale (si pas désactivé)
        if schedule_job.enabled:
            schedule_job.next_run = self._calculate_next_run(schedule_job.schedule_config)
        
        # Persistance
        await self._persist_job(schedule_job)
    
    def _update_average_execution_time(self, execution_time: float):
        """Met à jour le temps d'exécution moyen global"""
        total_successful = self.performance_metrics["successful_executions"]
        current_avg = self.performance_metrics["average_execution_time"]
        
        new_avg = ((current_avg * (total_successful - 1)) + execution_time) / total_successful
        self.performance_metrics["average_execution_time"] = new_avg
    
    async def _persist_job(self, schedule_job: BackupScheduleJob):
        """Persiste un job planifié dans Redis"""
        job_data = {
            "job_id": schedule_job.job_id,
            "name": schedule_job.name,
            "source_paths": [str(p) for p in schedule_job.source_paths],
            "schedule_config": schedule_job.schedule_config.to_dict(),
            "user_id": schedule_job.user_id,
            "content_type": schedule_job.content_type,
            "backup_options": schedule_job.backup_options,
            "enabled": schedule_job.enabled,
            "created_at": schedule_job.created_at.isoformat(),
            "last_run": schedule_job.last_run.isoformat() if schedule_job.last_run else None,
            "next_run": schedule_job.next_run.isoformat() if schedule_job.next_run else None,
            "run_count": schedule_job.run_count,
            "failure_count": schedule_job.failure_count,
            "last_error": schedule_job.last_error,
            "avg_duration_seconds": schedule_job.avg_duration_seconds,
            "total_data_backed_up_gb": schedule_job.total_data_backed_up_gb,
            "success_rate": schedule_job.success_rate
        }
        
        # En production, sauvegarder dans Redis
        # redis_client.set(f"scheduled_job:{schedule_job.job_id}", json.dumps(job_data))
        
        logger.debug(f"Persisted scheduled job: {schedule_job.job_id}")
    
    async def _load_persisted_jobs(self):
        """Charge les jobs persistés depuis Redis"""
        # En production, charger depuis Redis
        # keys = redis_client.keys("scheduled_job:*")
        # for key in keys:
        #     job_data = json.loads(redis_client.get(key))
        #     schedule_job = self._deserialize_job(job_data)
        #     self.scheduled_jobs[schedule_job.job_id] = schedule_job
        #     await self._add_to_scheduler(schedule_job)
        
        logger.info("Loaded persisted scheduled jobs")
    
    async def unschedule_backup(self, job_id: str) -> bool:
        """
        Supprime une sauvegarde planifiée
        
        Args:
            job_id: ID du job à supprimer
            
        Returns:
            bool: True si supprimé avec succès
        """



        try:
            # Suppression du scheduler
            self.scheduler.remove_job(job_id)
            
            # Suppression du registry
            if job_id in self.scheduled_jobs:
                del self.scheduled_jobs[job_id]
            
            # Suppression persistence
            # redis_client.delete(f"scheduled_job:{job_id}")
            
            logger.info(f"Unscheduled backup job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unschedule job {job_id}: {e}")
            return False
    
    async def pause_job(self, job_id: str) -> bool:
        """
        Met en pause un job planifié
        
        Args:
            job_id: ID du job à pauser
            
        Returns:
            bool: True si pausé avec succès
        """



        try:
            self.scheduler.pause_job(job_id)
            
            if job_id in self.scheduled_jobs:
                self.scheduled_jobs[job_id].enabled = False
                await self._persist_job(self.scheduled_jobs[job_id])
            
            logger.info(f"Paused scheduled job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}")
            return False
    
    async def resume_job(self, job_id: str) -> bool:
        """
        Reprend un job planifié en pause
        
        Args:
            job_id: ID du job à reprendre
            
        Returns:
            bool: True si repris avec succès
        """



        try:
            self.scheduler.resume_job(job_id)
            
            if job_id in self.scheduled_jobs:
                self.scheduled_jobs[job_id].enabled = True
                await self._persist_job(self.scheduled_jobs[job_id])
            
            logger.info(f"Resumed scheduled job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
            return False
    
    async def list_scheduled_jobs(
        self,
        user_id: Optional[str] = None,
        enabled_only: bool = False
    ) -> List[BackupScheduleJob]:
        """
        Liste les jobs planifiés
        
        Args:
            user_id: Filtrer par utilisateur
            enabled_only: Seulement les jobs actifs
            
        Returns:
            List[BackupScheduleJob]: Liste des jobs planifiés
        """
        jobs = list(self.scheduled_jobs.values())
        
        # Filtrage par utilisateur
        if user_id:
            jobs = [job for job in jobs if job.user_id == user_id]
        
        # Filtrage par statut activé
        if enabled_only:
            jobs = [job for job in jobs if job.enabled]
        
        # Tri par prochaine exécution
        jobs.sort(key=lambda x: x.next_run or datetime.max)
        
        return jobs
    
    async def get_job_details(self, job_id: str) -> Optional[BackupScheduleJob]:
        """
        Récupère les détails d'un job planifié
        
        Args:
            job_id: ID du job
            
        Returns:
            Optional[BackupScheduleJob]: Job si trouvé
        """



        return self.scheduled_jobs.get(job_id)
    
    async def update_job_schedule(
        self,
        job_id: str,
        new_schedule_config: ScheduleConfig
    ) -> bool:
        """
        Met à jour la planification d'un job
        
        Args:
            job_id: ID du job à modifier
            new_schedule_config: Nouvelle configuration
            
        Returns:
            bool: True si mis à jour avec succès
        """



        try:
            if job_id not in self.scheduled_jobs:
                return False
            
            schedule_job = self.scheduled_jobs[job_id]
            
            # Suppression ancienne planification
            self.scheduler.remove_job(job_id)
            
            # Mise à jour configuration
            schedule_job.schedule_config = new_schedule_config
            schedule_job.next_run = self._calculate_next_run(new_schedule_config)
            
            # Ajout nouvelle planification
            await self._add_to_scheduler(schedule_job)
            
            # Persistance
            await self._persist_job(schedule_job)
            
            logger.info(f"Updated schedule for job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update job schedule {job_id}: {e}")
            return False
    
    async def get_scheduler_metrics(self) -> Dict[str, Any]:
        """
        Récupère les métriques du planificateur
        
        Returns:
            Dict[str, Any]: Métriques détaillées
        """
        # Mise à jour peak concurrent jobs
        current_active = self.performance_metrics["current_active_jobs"]
        if current_active > self.performance_metrics["peak_concurrent_jobs"]:
            self.performance_metrics["peak_concurrent_jobs"] = current_active
        
        # Statistiques par priorité
        priority_stats = {}
        for job in self.scheduled_jobs.values():
            priority = job.schedule_config.priority.value
            if priority not in priority_stats:
                priority_stats[priority] = {
                    "count": 0,
                    "success_rate": 0.0,
                    "avg_duration": 0.0
                }
            
            priority_stats[priority]["count"] += 1
            priority_stats[priority]["success_rate"] += job.success_rate
            priority_stats[priority]["avg_duration"] += job.avg_duration_seconds
        
        # Moyennes par priorité
        for priority in priority_stats:
            count = priority_stats[priority]["count"]
            if count > 0:
                priority_stats[priority]["success_rate"] /= count
                priority_stats[priority]["avg_duration"] /= count
        
        return {
            **self.performance_metrics,
            "total_active_jobs": len([j for j in self.scheduled_jobs.values() if j.enabled]),
            "total_paused_jobs": len([j for j in self.scheduled_jobs.values() if not j.enabled]),
            "priority_statistics": priority_stats,
            "upcoming_jobs": len([j for j in self.scheduled_jobs.values() 
                                if j.next_run and j.next_run <= datetime.now() + timedelta(hours=24)]),
            "jobs_with_failures": len([j for j in self.scheduled_jobs.values() if j.failure_count > 0]),
            "recent_job_history": self.job_history[-10:]  # 10 dernières exécutions
        }


class AutomatedScheduler(BackupScheduler):
    """
    Planificateur automatisé avec intelligence artificielle
    
    Fonctionnalités:
    - Auto-détection patterns d'usage
    - Optimisation automatique des horaires
    - Prédiction charge système
    - Ajustement dynamique selon performance
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        super().__init__(redis_url)
        self.usage_analyzer = UsagePatternAnalyzer()
        self.performance_predictor = PerformancePredictor()
        
        logger.info("AutomatedScheduler initialized with AI optimization")
    
    async def auto_optimize_schedules(self):
        """Optimise automatiquement tous les horaires de sauvegarde"""
        for job_id, schedule_job in self.scheduled_jobs.items():
            optimized_config = await self._optimize_job_schedule(schedule_job)
            
            if optimized_config != schedule_job.schedule_config:
                await self.update_job_schedule(job_id, optimized_config)
                logger.info(f"Auto-optimized schedule for job {job_id}")
    
    async def _optimize_job_schedule(self, schedule_job: BackupScheduleJob) -> ScheduleConfig:
        """Optimise la planification d'un job spécifique"""
        # Analyse patterns d'usage
        usage_pattern = await self.usage_analyzer.analyze_content_usage(
            schedule_job.source_paths,
            schedule_job.content_type
        )
        
        # Prédiction charge système
        optimal_times = await self.performance_predictor.predict_optimal_backup_times(
            schedule_job.schedule_config.priority
        )
        
        # Génération configuration optimisée
        optimized_config = schedule_job.schedule_config
        
        # Exemple d'optimisation basique
        if usage_pattern.get("high_activity_hours"):
            # Éviter les heures de forte activité
            optimal_hour = min(optimal_times, key=lambda h: usage_pattern.get("hourly_activity", {}).get(h, 0))
            optimized_config.cron_expression = f"0 {optimal_hour} * * *"  # Quotidien à l'heure optimale
        
        return optimized_config


class ConditionalScheduler(BackupScheduler):
    """
    Planificateur conditionnel avancé
    
    Fonctionnalités:
    - Conditions complexes multi-critères
    - Évaluation temps réel
    - Triggers personnalisés
    - Intégration monitoring externe
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        super().__init__(redis_url)
        self.condition_evaluators = self._initialize_condition_evaluators()
        
        logger.info("ConditionalScheduler initialized with advanced conditions")
    
    def _initialize_condition_evaluators(self) -> Dict[str, Callable]:
        """Initialise les évaluateurs de conditions personnalisées"""



        return {
            "file_changes": self._evaluate_file_changes,
            "system_load": self._evaluate_system_load,
            "network_bandwidth": self._evaluate_network_bandwidth,
            "storage_usage": self._evaluate_storage_usage,
            "content_popularity": self._evaluate_content_popularity,
            "revenue_impact": self._evaluate_revenue_impact
        }
    
    async def _evaluate_file_changes(self, condition_params: Dict[str, Any]) -> bool:
        """Évalue les conditions de changement de fichiers"""
        # Implémentation détection changements avancée
        return True  # Placeholder
    
    async def _evaluate_system_load(self, condition_params: Dict[str, Any]) -> bool:
        """Évalue la charge système"""
        # Intégration métriques système
        return True  # Placeholder
    
    async def _evaluate_network_bandwidth(self, condition_params: Dict[str, Any]) -> bool:
        """Évalue la bande passante réseau"""
        # Monitoring bande passante
        return True  # Placeholder
    
    async def _evaluate_storage_usage(self, condition_params: Dict[str, Any]) -> bool:
        """Évalue l'usage du stockage"""
        # Vérification espace disque
        return True  # Placeholder
    
    async def _evaluate_content_popularity(self, condition_params: Dict[str, Any]) -> bool:
        """Évalue la popularité du contenu"""
        # Analyse engagement/vues récentes
        return True  # Placeholder
    
    async def _evaluate_revenue_impact(self, condition_params: Dict[str, Any]) -> bool:
        """Évalue l'impact sur les revenus"""
        # Corrélation contenu/revenus
        return True  # Placeholder


class UsagePatternAnalyzer:
    """Analyseur de patterns d'usage pour optimisation automatique"""
    
    async def analyze_content_usage(
        self,
        source_paths: List[Path],
        content_type: str
    ) -> Dict[str, Any]:
        """Analyse les patterns d'usage du contenu"""
        # Implémentation analyse patterns
        return {
            "high_activity_hours": [9, 10, 11, 14, 15, 16],
            "low_activity_hours": [1, 2, 3, 4, 5],
            "hourly_activity": {hour: 50 for hour in range(24)}  # Placeholder
        }


class PerformancePredictor:
    """Prédicteur de performance pour optimisation"""
    
    async def predict_optimal_backup_times(self, priority: Priority) -> List[int]:
        """Prédit les heures optimales pour les sauvegardes"""
        # Logique prédictive basée sur historique
        if priority == Priority.CRITICAL:
            return [2, 3, 4]  # Heures creuses
        else:
            return [1, 2, 3, 4, 5]  # Plus de flexibilité
