#!/usr/bin/env python3
"""
🧪 AI Experiment Tracker Service - Enterprise Grade
Suivi et gestion des expérimentations IA pour Ainflue

© Fahed Mlaiel 2024-2025 - Propriété intellectuelle stricte
Architecture microservices enterprise - Niveau production
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

# Configuration logging enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExperimentStatus(Enum):
    """Statuts des expérimentations"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class MetricType(Enum):
    """Types de métriques"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    AUC_ROC = "auc_roc"
    LOSS = "loss"
    MAE = "mae"
    MSE = "mse"
    RMSE = "rmse"
    CUSTOM = "custom"

@dataclass
class Metric:
    """Métrique d'expérimentation"""
    name: str
    metric_type: MetricType
    value: float
    step: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Parameter:
    """Paramètre d'expérimentation"""
    name: str
    value: Any
    param_type: str  # string, int, float, bool, list, dict
    description: Optional[str] = None

@dataclass
class Artifact:
    """Artefact d'expérimentation"""
    name: str
    file_path: str
    artifact_type: str  # model, dataset, plot, log, config
    size: int
    created_at: datetime
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Experiment:
    """Expérimentation IA complète"""
    experiment_id: str
    name: str
    description: str
    status: ExperimentStatus
    created_by: str
    project_name: str
    tags: List[str]
    parameters: List[Parameter]
    metrics: List[Metric]
    artifacts: List[Artifact]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parent_experiment: Optional[str] = None
    notes: str = ""
    environment: Dict[str, Any] = field(default_factory=dict)

class AIExperimentTracker:
    """
    🧪 Tracker d'expérimentations IA enterprise
    Suivi complet des expérimentations ML/DL
    """
    
    def __init__(self, storage_path: str = "./experiments"):
        """
        Initialisation du tracker
        
        Args:
            storage_path: Chemin de stockage des expérimentations
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Stockage des expérimentations
        self.experiments: Dict[str, Experiment] = {}
        self.projects: Dict[str, List[str]] = defaultdict(list)  # project -> experiment_ids
        
        # Index pour recherche rapide
        self.experiments_by_tag: Dict[str, List[str]] = defaultdict(list)
        self.experiments_by_user: Dict[str, List[str]] = defaultdict(list)
        
        # Métriques enterprise
        self.metrics = {
            'total_experiments': 0,
            'active_experiments': 0,
            'completed_experiments': 0,
            'failed_experiments': 0,
            'total_artifacts': 0,
            'storage_usage_mb': 0
        }
        
        # Configuration visualisation
        plt.style.use('default')
        sns.set_palette("husl")
        
        logger.info(f"🧪 AI Experiment Tracker initialisé - Stockage: {storage_path}")
    
    async def create_experiment(
        self,
        name: str,
        description: str,
        created_by: str,
        project_name: str,
        tags: Optional[List[str]] = None,
        parent_experiment: Optional[str] = None
    ) -> str:
        """
        Créer une nouvelle expérimentation
        
        Args:
            name: Nom de l'expérimentation
            description: Description
            created_by: Créateur
            project_name: Nom du projet
            tags: Tags pour classification
            parent_experiment: Expérimentation parent si applicable
        
        Returns:
            ID de l'expérimentation créée
        """
        try:
            experiment_id = f"exp_{uuid.uuid4().hex[:8]}"
            
            experiment = Experiment(
                experiment_id=experiment_id,
                name=name,
                description=description,
                status=ExperimentStatus.CREATED,
                created_by=created_by,
                project_name=project_name,
                tags=tags or [],
                parameters=[],
                metrics=[],
                artifacts=[],
                created_at=datetime.utcnow(),
                parent_experiment=parent_experiment
            )
            
            # Capture de l'environnement
            experiment.environment = await self._capture_environment()
            
            # Stockage
            self.experiments[experiment_id] = experiment
            self.projects[project_name].append(experiment_id)
            
            # Indexation
            for tag in experiment.tags:
                self.experiments_by_tag[tag].append(experiment_id)
            self.experiments_by_user[created_by].append(experiment_id)
            
            # Métriques
            self.metrics['total_experiments'] += 1
            
            # Création du dossier de stockage
            exp_path = self.storage_path / experiment_id
            exp_path.mkdir(exist_ok=True)
            
            # Sauvegarde
            await self._save_experiment(experiment)
            
            logger.info(f"✅ Expérimentation créée: {experiment_id} - {name}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création expérimentation: {e}")
            raise
    
    async def start_experiment(self, experiment_id: str) -> bool:
        """
        Démarrer une expérimentation
        
        Args:
            experiment_id: ID de l'expérimentation
        
        Returns:
            True si succès
        """
        try:
            if experiment_id not in self.experiments:
                logger.error(f"❌ Expérimentation {experiment_id} introuvable")
                return False
            
            experiment = self.experiments[experiment_id]
            
            if experiment.status != ExperimentStatus.CREATED:
                logger.warning(f"⚠️ Expérimentation {experiment_id} déjà démarrée")
                return False
            
            experiment.status = ExperimentStatus.RUNNING
            experiment.started_at = datetime.utcnow()
            
            self.metrics['active_experiments'] += 1
            
            await self._save_experiment(experiment)
            
            logger.info(f"🚀 Expérimentation démarrée: {experiment_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage expérimentation: {e}")
            return False
    
    async def log_parameter(
        self,
        experiment_id: str,
        name: str,
        value: Any,
        param_type: Optional[str] = None,
        description: Optional[str] = None
    ) -> bool:
        """
        Enregistrer un paramètre
        
        Args:
            experiment_id: ID de l'expérimentation
            name: Nom du paramètre
            value: Valeur du paramètre
            param_type: Type du paramètre
            description: Description
        
        Returns:
            True si succès
        """
        try:
            if experiment_id not in self.experiments:
                return False
            
            experiment = self.experiments[experiment_id]
            
            # Déduction du type si non spécifié
            if param_type is None:
                param_type = type(value).__name__
            
            parameter = Parameter(
                name=name,
                value=value,
                param_type=param_type,
                description=description
            )
            
            # Vérification doublons
            existing_param = next((p for p in experiment.parameters if p.name == name), None)
            if existing_param:
                existing_param.value = value
                existing_param.param_type = param_type
            else:
                experiment.parameters.append(parameter)
            
            await self._save_experiment(experiment)
            
            logger.debug(f"📝 Paramètre enregistré: {name}={value} pour {experiment_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement paramètre: {e}")
            return False
    
    async def log_metric(
        self,
        experiment_id: str,
        name: str,
        value: float,
        step: int = 0,
        metric_type: Optional[MetricType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Enregistrer une métrique
        
        Args:
            experiment_id: ID de l'expérimentation
            name: Nom de la métrique
            value: Valeur de la métrique
            step: Étape/époque
            metric_type: Type de métrique
            metadata: Métadonnées additionnelles
        
        Returns:
            True si succès
        """
        try:
            if experiment_id not in self.experiments:
                return False
            
            experiment = self.experiments[experiment_id]
            
            # Déduction du type si non spécifié
            if metric_type is None:
                metric_type = MetricType.CUSTOM
            
            metric = Metric(
                name=name,
                metric_type=metric_type,
                value=value,
                step=step,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            experiment.metrics.append(metric)
            
            await self._save_experiment(experiment)
            
            logger.debug(f"📊 Métrique enregistrée: {name}={value} pour {experiment_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement métrique: {e}")
            return False
    
    async def log_artifact(
        self,
        experiment_id: str,
        name: str,
        file_path: str,
        artifact_type: str = "file",
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Enregistrer un artefact
        
        Args:
            experiment_id: ID de l'expérimentation
            name: Nom de l'artefact
            file_path: Chemin du fichier
            artifact_type: Type d'artefact
            description: Description
            metadata: Métadonnées
        
        Returns:
            True si succès
        """
        try:
            if experiment_id not in self.experiments:
                return False
            
            experiment = self.experiments[experiment_id]
            exp_path = self.storage_path / experiment_id
            
            # Copie du fichier dans le dossier de l'expérimentation
            source_path = Path(file_path)
            if source_path.exists():
                dest_path = exp_path / source_path.name
                
                # Copie du fichier
                import shutil
                shutil.copy2(source_path, dest_path)
                
                # Taille du fichier
                file_size = dest_path.stat().st_size
                
                artifact = Artifact(
                    name=name,
                    file_path=str(dest_path),
                    artifact_type=artifact_type,
                    size=file_size,
                    created_at=datetime.utcnow(),
                    description=description,
                    metadata=metadata or {}
                )
                
                experiment.artifacts.append(artifact)
                self.metrics['total_artifacts'] += 1
                self.metrics['storage_usage_mb'] += file_size / (1024 * 1024)
                
                await self._save_experiment(experiment)
                
                logger.info(f"📎 Artefact enregistré: {name} pour {experiment_id}")
                return True
            else:
                logger.error(f"❌ Fichier {file_path} introuvable")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement artefact: {e}")
            return False
    
    async def complete_experiment(
        self,
        experiment_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Terminer une expérimentation
        
        Args:
            experiment_id: ID de l'expérimentation
            notes: Notes finales
        
        Returns:
            True si succès
        """
        try:
            if experiment_id not in self.experiments:
                return False
            
            experiment = self.experiments[experiment_id]
            
            if experiment.status != ExperimentStatus.RUNNING:
                logger.warning(f"⚠️ Expérimentation {experiment_id} non en cours")
                return False
            
            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.utcnow()
            if notes:
                experiment.notes = notes
            
            self.metrics['active_experiments'] -= 1
            self.metrics['completed_experiments'] += 1
            
            await self._save_experiment(experiment)
            
            logger.info(f"✅ Expérimentation terminée: {experiment_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur completion expérimentation: {e}")
            return False
    
    async def fail_experiment(
        self,
        experiment_id: str,
        error_message: str
    ) -> bool:
        """
        Marquer une expérimentation comme échouée
        
        Args:
            experiment_id: ID de l'expérimentation
            error_message: Message d'erreur
        
        Returns:
            True si succès
        """
        try:
            if experiment_id not in self.experiments:
                return False
            
            experiment = self.experiments[experiment_id]
            experiment.status = ExperimentStatus.FAILED
            experiment.completed_at = datetime.utcnow()
            experiment.notes += f"\nERREUR: {error_message}"
            
            if experiment.status == ExperimentStatus.RUNNING:
                self.metrics['active_experiments'] -= 1
            
            self.metrics['failed_experiments'] += 1
            
            await self._save_experiment(experiment)
            
            logger.error(f"❌ Expérimentation échouée: {experiment_id} - {error_message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur marquage échec: {e}")
            return False
    
    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupérer une expérimentation
        
        Args:
            experiment_id: ID de l'expérimentation
        
        Returns:
            Données de l'expérimentation ou None
        """
        try:
            if experiment_id not in self.experiments:
                return None
            
            experiment = self.experiments[experiment_id]
            
            return {
                'experiment_id': experiment.experiment_id,
                'name': experiment.name,
                'description': experiment.description,
                'status': experiment.status.value,
                'created_by': experiment.created_by,
                'project_name': experiment.project_name,
                'tags': experiment.tags,
                'parameters': [
                    {
                        'name': p.name,
                        'value': p.value,
                        'type': p.param_type,
                        'description': p.description
                    }
                    for p in experiment.parameters
                ],
                'metrics': [
                    {
                        'name': m.name,
                        'type': m.metric_type.value,
                        'value': m.value,
                        'step': m.step,
                        'timestamp': m.timestamp.isoformat()
                    }
                    for m in experiment.metrics
                ],
                'artifacts': [
                    {
                        'name': a.name,
                        'type': a.artifact_type,
                        'size': a.size,
                        'created_at': a.created_at.isoformat(),
                        'description': a.description
                    }
                    for a in experiment.artifacts
                ],
                'created_at': experiment.created_at.isoformat(),
                'started_at': experiment.started_at.isoformat() if experiment.started_at else None,
                'completed_at': experiment.completed_at.isoformat() if experiment.completed_at else None,
                'parent_experiment': experiment.parent_experiment,
                'notes': experiment.notes,
                'environment': experiment.environment
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération expérimentation: {e}")
            return None
    
    def list_experiments(
        self,
        project_name: Optional[str] = None,
        status: Optional[ExperimentStatus] = None,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Lister les expérimentations avec filtres
        
        Args:
            project_name: Filtrer par projet
            status: Filtrer par statut
            created_by: Filtrer par créateur
            tags: Filtrer par tags
            limit: Limite de résultats
        
        Returns:
            Liste des expérimentations
        """
        try:
            experiments = list(self.experiments.values())
            
            # Filtres
            if project_name:
                experiments = [e for e in experiments if e.project_name == project_name]
            
            if status:
                experiments = [e for e in experiments if e.status == status]
            
            if created_by:
                experiments = [e for e in experiments if e.created_by == created_by]
            
            if tags:
                experiments = [
                    e for e in experiments
                    if any(tag in e.tags for tag in tags)
                ]
            
            # Tri par date de création (plus récent en premier)
            experiments.sort(key=lambda x: x.created_at, reverse=True)
            
            # Limitation
            experiments = experiments[:limit]
            
            # Conversion en dictionnaire
            result = []
            for exp in experiments:
                exp_data = self.get_experiment(exp.experiment_id)
                if exp_data:
                    result.append(exp_data)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur listing expérimentations: {e}")
            return []
    
    def compare_experiments(
        self,
        experiment_ids: List[str],
        metric_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Comparer plusieurs expérimentations
        
        Args:
            experiment_ids: IDs des expérimentations à comparer
            metric_names: Métriques à comparer (toutes si None)
        
        Returns:
            Données de comparaison
        """
        try:
            comparison = {
                'experiments': [],
                'metric_comparison': defaultdict(dict),
                'parameter_comparison': defaultdict(dict)
            }
            
            for exp_id in experiment_ids:
                if exp_id not in self.experiments:
                    continue
                
                exp_data = self.get_experiment(exp_id)
                if not exp_data:
                    continue
                
                comparison['experiments'].append(exp_data)
                
                # Comparaison des métriques
                for metric in exp_data['metrics']:
                    metric_name = metric['name']
                    if metric_names is None or metric_name in metric_names:
                        comparison['metric_comparison'][metric_name][exp_id] = metric['value']
                
                # Comparaison des paramètres
                for param in exp_data['parameters']:
                    param_name = param['name']
                    comparison['parameter_comparison'][param_name][exp_id] = param['value']
            
            return dict(comparison)
            
        except Exception as e:
            logger.error(f"❌ Erreur comparaison expérimentations: {e}")
            return {}
    
    async def generate_report(
        self,
        experiment_id: str,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Générer un rapport d'expérimentation
        
        Args:
            experiment_id: ID de l'expérimentation
            output_path: Chemin de sortie du rapport
        
        Returns:
            Chemin du rapport généré ou None
        """
        try:
            if experiment_id not in self.experiments:
                return None
            
            experiment = self.experiments[experiment_id]
            
            if output_path is None:
                output_path = self.storage_path / experiment_id / "report.html"
            
            # Génération du rapport HTML
            html_content = await self._generate_html_report(experiment)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"📄 Rapport généré: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Erreur génération rapport: {e}")
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtenir les métriques du tracker
        
        Returns:
            Métriques enterprise
        """
        return {
            **self.metrics,
            'projects_count': len(self.projects),
            'unique_users': len(self.experiments_by_user),
            'unique_tags': len(self.experiments_by_tag),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _capture_environment(self) -> Dict[str, Any]:
        """Capturer l'environnement d'exécution"""
        try:
            import sys
            import platform
            
            env = {
                'python_version': sys.version,
                'platform': platform.platform(),
                'hostname': platform.node(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Tentative de capture des packages installés
            try:
                import pkg_resources
                env['packages'] = {
                    pkg.project_name: pkg.version
                    for pkg in pkg_resources.working_set
                }
            except:
                pass
            
            return env
            
        except Exception as e:
            logger.error(f"❌ Erreur capture environnement: {e}")
            return {}
    
    async def _save_experiment(self, experiment: Experiment) -> None:
        """Sauvegarder une expérimentation"""
        try:
            exp_path = self.storage_path / experiment.experiment_id
            metadata_path = exp_path / "metadata.json"
            
            # Sérialisation de l'expérimentation
            exp_data = {
                'experiment_id': experiment.experiment_id,
                'name': experiment.name,
                'description': experiment.description,
                'status': experiment.status.value,
                'created_by': experiment.created_by,
                'project_name': experiment.project_name,
                'tags': experiment.tags,
                'parameters': [
                    {
                        'name': p.name,
                        'value': p.value,
                        'param_type': p.param_type,
                        'description': p.description
                    }
                    for p in experiment.parameters
                ],
                'metrics': [
                    {
                        'name': m.name,
                        'metric_type': m.metric_type.value,
                        'value': m.value,
                        'step': m.step,
                        'timestamp': m.timestamp.isoformat(),
                        'metadata': m.metadata
                    }
                    for m in experiment.metrics
                ],
                'artifacts': [
                    {
                        'name': a.name,
                        'file_path': a.file_path,
                        'artifact_type': a.artifact_type,
                        'size': a.size,
                        'created_at': a.created_at.isoformat(),
                        'description': a.description,
                        'metadata': a.metadata
                    }
                    for a in experiment.artifacts
                ],
                'created_at': experiment.created_at.isoformat(),
                'started_at': experiment.started_at.isoformat() if experiment.started_at else None,
                'completed_at': experiment.completed_at.isoformat() if experiment.completed_at else None,
                'parent_experiment': experiment.parent_experiment,
                'notes': experiment.notes,
                'environment': experiment.environment
            }
            
            # Écriture du fichier JSON
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(exp_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde expérimentation: {e}")
    
    async def _generate_html_report(self, experiment: Experiment) -> str:
        """Générer un rapport HTML"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Rapport - {experiment.name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .section {{ margin: 20px 0; }}
                    .metric {{ background: #e8f4f8; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                    .parameter {{ background: #f8f8e8; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{experiment.name}</h1>
                    <p><strong>ID:</strong> {experiment.experiment_id}</p>
                    <p><strong>Description:</strong> {experiment.description}</p>
                    <p><strong>Statut:</strong> {experiment.status.value}</p>
                    <p><strong>Créé par:</strong> {experiment.created_by}</p>
                    <p><strong>Projet:</strong> {experiment.project_name}</p>
                    <p><strong>Tags:</strong> {', '.join(experiment.tags)}</p>
                </div>
                
                <div class="section">
                    <h2>Paramètres</h2>
            """
            
            for param in experiment.parameters:
                html += f'<div class="parameter"><strong>{param.name}:</strong> {param.value} ({param.param_type})</div>'
            
            html += """
                </div>
                
                <div class="section">
                    <h2>Métriques</h2>
            """
            
            for metric in experiment.metrics:
                html += f'<div class="metric"><strong>{metric.name}:</strong> {metric.value} (step {metric.step})</div>'
            
            html += f"""
                </div>
                
                <div class="section">
                    <h2>Artefacts</h2>
                    <table>
                        <tr><th>Nom</th><th>Type</th><th>Taille</th><th>Description</th></tr>
            """
            
            for artifact in experiment.artifacts:
                size_mb = artifact.size / (1024 * 1024)
                html += f"""
                    <tr>
                        <td>{artifact.name}</td>
                        <td>{artifact.artifact_type}</td>
                        <td>{size_mb:.2f} MB</td>
                        <td>{artifact.description or 'N/A'}</td>
                    </tr>
                """
            
            html += f"""
                    </table>
                </div>
                
                <div class="section">
                    <h2>Notes</h2>
                    <p>{experiment.notes or 'Aucune note'}</p>
                </div>
                
                <div class="section">
                    <h2>Environnement</h2>
                    <pre>{json.dumps(experiment.environment, indent=2)}</pre>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"❌ Erreur génération HTML: {e}")
            return "<html><body><h1>Erreur génération rapport</h1></body></html>"

# Instance globale du tracker
ai_experiment_tracker = AIExperimentTracker()

# API publique
__all__ = [
    'AIExperimentTracker',
    'Experiment',
    'Metric',
    'Parameter',
    'Artifact',
    'ExperimentStatus',
    'MetricType',
    'ai_experiment_tracker'
]

if __name__ == "__main__":
    # Test de démonstration
    async def demo():
        tracker = AIExperimentTracker()
        
        # Création d'une expérimentation
        exp_id = await tracker.create_experiment(
            name="Test Classification",
            description="Expérimentation de classification pour démonstration",
            created_by="system",
            project_name="demo_project",
            tags=["classification", "demo", "test"]
        )
        
        # Démarrage
        await tracker.start_experiment(exp_id)
        
        # Enregistrement de paramètres
        await tracker.log_parameter(exp_id, "learning_rate", 0.001, "float")
        await tracker.log_parameter(exp_id, "batch_size", 32, "int")
        await tracker.log_parameter(exp_id, "optimizer", "adam", "string")
        
        # Enregistrement de métriques
        for epoch in range(5):
            accuracy = 0.8 + epoch * 0.03 + np.random.normal(0, 0.01)
            loss = 0.5 - epoch * 0.08 + np.random.normal(0, 0.02)
            
            await tracker.log_metric(exp_id, "accuracy", accuracy, epoch, MetricType.ACCURACY)
            await tracker.log_metric(exp_id, "loss", loss, epoch, MetricType.LOSS)
        
        # Completion
        await tracker.complete_experiment(exp_id, "Expérimentation terminée avec succès")
        
        # Récupération des données
        exp_data = tracker.get_experiment(exp_id)
        print(f"Expérimentation: {exp_data['name']}")
        print(f"Métriques: {len(exp_data['metrics'])}")
        
        # Métriques du tracker
        metrics = tracker.get_metrics()
        print(f"Métriques tracker: {metrics}")
    
    # Exécution du test
    asyncio.run(demo())