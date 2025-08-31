"""🚀 Workflow Validator - IA Influencer Agent Platform Enterprise
==============================================================
Module: backend/data_management/validation/workflow_validator.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 VALIDATION WORKFLOW MULTI-CRÉATEURS
Validation complète des workflows de création de contenu
- Workflows spécialisés par type de créateur
- Validation étapes métier multi-formats
- Orchestration validation bout-en-bout
- Conformité business et qualité intégrée
"""from typing import Dict, List, Optional, Any, Union, Tuple, Set
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

# Import des autres validateurs
from .quality_assessor import QualityAssessor, QualityAssessmentResult, QualityLevel
from .metadata_extractor import MetadataExtractor, ContentMetadata
from .compliance_checker import ComplianceChecker, ComplianceResult, ComplianceLevel
from .fingerprint_validator import FingerprintValidator, FingerprintResult, SimilarityLevel

# Validation business
from ..business.business_validator import BusinessValidator, BusinessValidationResult

logger = logging.getLogger(__name__)

class WorkflowStep(Enum):
    """Étapes du workflow de validation"""    CONTENT_INGESTION = "content_ingestion"
    METADATA_EXTRACTION = "metadata_extraction"
    TECHNICAL_VALIDATION = "technical_validation"
    QUALITY_ASSESSMENT = "quality_assessment"
    FINGERPRINT_GENERATION = "fingerprint_generation"
    BUSINESS_VALIDATION = "business_validation"
    COMPLIANCE_CHECK = "compliance_check"
    FINAL_APPROVAL = "final_approval"

class WorkflowStatus(Enum):
    """Status du workflow"""    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    WARNING = "warning"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CreatorType(Enum):
    """Types de créateurs supportés"""    MUSICIAN = "musician"
    INFLUENCER = "influencer"
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    COMEDIAN = "comedian"
    FILMMAKER = "filmmaker"
    PODCASTER = "podcaster"

@dataclass
class WorkflowStepResult:
    """Résultat d'une étape de workflow"""    step: WorkflowStep
    status: WorkflowStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    result_data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowConfiguration:
    """Configuration du workflow"""    creator_type: CreatorType
    content_type: str  # audio, video, image, text
    target_platforms: List[str]
    quality_requirements: Dict[str, Any]
    compliance_jurisdictions: List[str]
    business_rules: Dict[str, Any]
    skip_steps: List[WorkflowStep] = field(default_factory=list)
    parallel_execution: bool = True
    timeout_seconds: int = 300

@dataclass
class WorkflowResult:
    """Résultat complet du workflow"""    workflow_id: str
    configuration: WorkflowConfiguration
    overall_status: WorkflowStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_seconds: Optional[float] = None
    step_results: Dict[WorkflowStep, WorkflowStepResult] = field(default_factory=dict)
    
    # Résultats agrégés
    final_metadata: Optional[ContentMetadata] = None
    quality_result: Optional[QualityAssessmentResult] = None
    compliance_result: Optional[ComplianceResult] = None
    fingerprint_result: Optional[FingerprintResult] = None
    business_result: Optional[BusinessValidationResult] = None
    
    # Recommandations finales
    approval_status: bool = False
    blocking_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

class WorkflowOrchestrator:
    """Orchestrateur principal des workflows"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.WorkflowOrchestrator")
        
        # Initialisations des validateurs
        self.metadata_extractor = MetadataExtractor()
        self.quality_assessor = QualityAssessor()
        self.compliance_checker = ComplianceChecker()
        self.fingerprint_validator = FingerprintValidator()
        self.business_validator = BusinessValidator()
        
        # Workflows actifs
        self._active_workflows: Dict[str, WorkflowResult] = {}
        
        # Configurations par type de créateur
        self.creator_workflows = self._initialize_creator_workflows()
    
    def _initialize_creator_workflows(self) -> Dict[CreatorType, Dict[str, Any]]:
        """Initialise les configurations de workflow par créateur"""        return {
            CreatorType.MUSICIAN: {
                'priority_steps': [
                    WorkflowStep.QUALITY_ASSESSMENT,
                    WorkflowStep.FINGERPRINT_GENERATION,
                    WorkflowStep.COMPLIANCE_CHECK
                ],
                'quality_thresholds': {
                    'minimum_score': 0.7,
                    'technical_quality': 0.8,
                    'professional_standard': 0.9
                },
                'required_metadata': ['duration', 'sample_rate', 'bitrate', 'genre'],
                'compliance_focus': ['copyright', 'platform_policy']
            },
            CreatorType.INFLUENCER: {
                'priority_steps': [
                    WorkflowStep.COMPLIANCE_CHECK,
                    WorkflowStep.QUALITY_ASSESSMENT,
                    WorkflowStep.BUSINESS_VALIDATION
                ],
                'quality_thresholds': {
                    'minimum_score': 0.6,
                    'engagement_potential': 0.8,
                    'platform_compliance': 0.9
                },
                'required_metadata': ['duration', 'resolution', 'target_audience'],
                'compliance_focus': ['privacy', 'platform_policy', 'business_terms']
            },
            CreatorType.PHOTOGRAPHER: {
                'priority_steps': [
                    WorkflowStep.METADATA_EXTRACTION,
                    WorkflowStep.QUALITY_ASSESSMENT,
                    WorkflowStep.COMPLIANCE_CHECK
                ],
                'quality_thresholds': {
                    'minimum_score': 0.8,
                    'technical_quality': 0.9,
                    'aesthetic_quality': 0.8
                },
                'required_metadata': ['resolution', 'camera_model', 'copyright'],
                'compliance_focus': ['copyright', 'privacy']
            },
            CreatorType.BLOGGER: {
                'priority_steps': [
                    WorkflowStep.COMPLIANCE_CHECK,
                    WorkflowStep.BUSINESS_VALIDATION,
                    WorkflowStep.QUALITY_ASSESSMENT
                ],
                'quality_thresholds': {
                    'minimum_score': 0.6,
                    'content_relevance': 0.8,
                    'accessibility': 0.7
                },
                'required_metadata': ['word_count', 'language', 'topic'],
                'compliance_focus': ['privacy', 'content_safety']
            },
            CreatorType.COMEDIAN: {
                'priority_steps': [
                    WorkflowStep.COMPLIANCE_CHECK,
                    WorkflowStep.QUALITY_ASSESSMENT,
                    WorkflowStep.FINGERPRINT_GENERATION
                ],
                'quality_thresholds': {
                    'minimum_score': 0.6,
                    'engagement_potential': 0.9,
                    'platform_compliance': 0.8
                },
                'required_metadata': ['duration', 'content_rating', 'humor_type'],
                'compliance_focus': ['content_safety', 'platform_policy']
            }
        }
    
    async def validate_content_workflow(self, file_path: str, 
                                      config: WorkflowConfiguration) -> WorkflowResult:
        """Lance un workflow de validation complet"""        
        workflow_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        workflow_result = WorkflowResult(
            workflow_id=workflow_id,
            configuration=config,
            overall_status=WorkflowStatus.RUNNING,
            start_time=start_time
        )
        
        self._active_workflows[workflow_id] = workflow_result
        
        try:
            self.logger.info(f"Démarrage workflow {workflow_id} pour {file_path}")
            
            # Exécution séquentielle des étapes critiques
            sequential_steps = [
                WorkflowStep.CONTENT_INGESTION,
                WorkflowStep.METADATA_EXTRACTION,
                WorkflowStep.TECHNICAL_VALIDATION
            ]
            
            for step in sequential_steps:
                if step in config.skip_steps:
                    continue
                
                step_result = await self._execute_workflow_step(
                    step, file_path, config, workflow_result
                )
                workflow_result.step_results[step] = step_result
                
                if step_result.status == WorkflowStatus.FAILED:
                    workflow_result.overall_status = WorkflowStatus.FAILED
                    return await self._finalize_workflow(workflow_result)
            
            # Exécution parallèle des étapes d'analyse
            if config.parallel_execution:
                parallel_results = await self._execute_parallel_steps(
                    file_path, config, workflow_result
                )
                workflow_result.step_results.update(parallel_results)
            else:
                sequential_results = await self._execute_sequential_steps(
                    file_path, config, workflow_result
                )
                workflow_result.step_results.update(sequential_results)
            
            # Étape finale d'approbation
            if WorkflowStep.FINAL_APPROVAL not in config.skip_steps:
                approval_result = await self._execute_final_approval(workflow_result)
                workflow_result.step_results[WorkflowStep.FINAL_APPROVAL] = approval_result
            
            # Finalisation
            return await self._finalize_workflow(workflow_result)
            
        except Exception as e:
            self.logger.error(f"Erreur workflow {workflow_id}: {e}")
            workflow_result.overall_status = WorkflowStatus.FAILED
            return await self._finalize_workflow(workflow_result)
        
        finally:
            if workflow_id in self._active_workflows:
                del self._active_workflows[workflow_id]
    
    async def _execute_workflow_step(self, step: WorkflowStep, 
                                   file_path: str,
                                   config: WorkflowConfiguration,
                                   workflow_result: WorkflowResult) -> WorkflowStepResult:
        """Exécute une étape spécifique du workflow"""        
        step_start = datetime.now()
        step_result = WorkflowStepResult(
            step=step,
            status=WorkflowStatus.RUNNING,
            start_time=step_start
        )
        
        try:
            if step == WorkflowStep.CONTENT_INGESTION:
                result = await self._step_content_ingestion(file_path)
            elif step == WorkflowStep.METADATA_EXTRACTION:
                result = await self._step_metadata_extraction(file_path)
            elif step == WorkflowStep.TECHNICAL_VALIDATION:
                result = await self._step_technical_validation(file_path, config)
            elif step == WorkflowStep.QUALITY_ASSESSMENT:
                result = await self._step_quality_assessment(file_path, config)
            elif step == WorkflowStep.FINGERPRINT_GENERATION:
                result = await self._step_fingerprint_generation(file_path, config)
            elif step == WorkflowStep.BUSINESS_VALIDATION:
                result = await self._step_business_validation(file_path, config, workflow_result)
            elif step == WorkflowStep.COMPLIANCE_CHECK:
                result = await self._step_compliance_check(file_path, config, workflow_result)
            else:
                raise ValueError(f"Étape non supportée: {step}")
            
            step_result.result_data = result
            step_result.status = WorkflowStatus.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Erreur étape {step}: {e}")
            step_result.status = WorkflowStatus.FAILED
            step_result.errors.append(str(e))
        
        # Finalisation timing
        step_result.end_time = datetime.now()
        step_result.duration_seconds = (step_result.end_time - step_result.start_time).total_seconds()
        
        return step_result
    
    async def _step_content_ingestion(self, file_path: str) -> Dict[str, Any]:
        """Étape d'ingestion du contenu"""        self.logger.debug(f"Ingestion contenu: {file_path}")
        
        # Vérifications basiques
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        file_size = Path(file_path).stat().st_size
        if file_size == 0:
            raise ValueError("Fichier vide")
        
        if file_size > 1024 * 1024 * 1024:  # 1GB limit
            raise ValueError("Fichier trop volumineux (>1GB)")
        
        return {
            'file_path': file_path,
            'file_size': file_size,
            'ingestion_successful': True
        }
    
    async def _step_metadata_extraction(self, file_path: str) -> Dict[str, Any]:
        """Étape d'extraction des métadonnées"""        self.logger.debug(f"Extraction métadonnées: {file_path}")
        
        loop = asyncio.get_event_loop()
        metadata = await loop.run_in_executor(
            None, self.metadata_extractor.extract_metadata, file_path
        )
        
        return {
            'metadata': metadata,
            'extraction_successful': True
        }
    
    async def _step_technical_validation(self, file_path: str, 
                                       config: WorkflowConfiguration) -> Dict[str, Any]:
        """Étape de validation technique"""        self.logger.debug(f"Validation technique: {file_path}")
        
        # Validation basique du format
        supported_formats = {
            'audio': ['.mp3', '.flac', '.wav', '.m4a'],
            'video': ['.mp4', '.avi', '.mov', '.mkv'],
            'image': ['.jpg', '.jpeg', '.png', '.gif'],
            'text': ['.txt', '.md', '.doc', '.pdf']
        }
        
        file_extension = Path(file_path).suffix.lower()
        expected_formats = supported_formats.get(config.content_type, [])
        
        format_valid = file_extension in expected_formats
        
        return {
            'format_valid': format_valid,
            'file_extension': file_extension,
            'expected_formats': expected_formats,
            'technical_validation_passed': format_valid
        }
    
    async def _step_quality_assessment(self, file_path: str, 
                                     config: WorkflowConfiguration) -> Dict[str, Any]:
        """Étape d'évaluation qualité"""        self.logger.debug(f"Évaluation qualité: {file_path}")
        
        loop = asyncio.get_event_loop()
        quality_result = await loop.run_in_executor(
            None,
            self.quality_assessor.assess_content_quality,
            file_path,
            config.content_type,
            config.creator_type.value
        )
        
        # Vérification des seuils
        creator_config = self.creator_workflows.get(config.creator_type, {})
        quality_thresholds = creator_config.get('quality_thresholds', {})
        
        threshold_checks = {}
        for threshold_name, threshold_value in quality_thresholds.items():
            if threshold_name == 'minimum_score':
                threshold_checks[threshold_name] = quality_result.overall_score >= threshold_value
            else:
                # Vérification des dimensions spécifiques
                dimension_score = quality_result.dimension_scores.get(threshold_name)
                if dimension_score:
                    threshold_checks[threshold_name] = dimension_score.score >= threshold_value
                else:
                    threshold_checks[threshold_name] = False
        
        return {
            'quality_result': quality_result,
            'threshold_checks': threshold_checks,
            'quality_assessment_passed': all(threshold_checks.values())
        }
    
    async def _step_fingerprint_generation(self, file_path: str, 
                                         config: WorkflowConfiguration) -> Dict[str, Any]:
        """Étape de génération d'empreinte"""        self.logger.debug(f"Génération empreinte: {file_path}")
        
        loop = asyncio.get_event_loop()
        fingerprint_result = await loop.run_in_executor(
            None,
            self.fingerprint_validator.generate_content_fingerprint,
            file_path,
            config.content_type
        )
        
        return {
            'fingerprint_result': fingerprint_result,
            'fingerprint_generated': fingerprint_result.fingerprint_data is not None
        }
    
    async def _step_business_validation(self, file_path: str, 
                                      config: WorkflowConfiguration,
                                      workflow_result: WorkflowResult) -> Dict[str, Any]:
        """Étape de validation business"""        self.logger.debug(f"Validation business: {file_path}")
        
        # Récupération des métadonnées extraites
        metadata_step = workflow_result.step_results.get(WorkflowStep.METADATA_EXTRACTION)
        if not metadata_step or not metadata_step.result_data.get('metadata'):
            raise ValueError("Métadonnées requises pour validation business")
        
        metadata = metadata_step.result_data['metadata']
        
        loop = asyncio.get_event_loop()
        business_result = await loop.run_in_executor(
            None,
            self.business_validator.validate_business_rules,
            metadata,
            config.creator_type.value,
            config.business_rules
        )
        
        return {
            'business_result': business_result,
            'business_validation_passed': business_result.is_valid
        }
    
    async def _step_compliance_check(self, file_path: str, 
                                   config: WorkflowConfiguration,
                                   workflow_result: WorkflowResult) -> Dict[str, Any]:
        """Étape de vérification conformité"""        self.logger.debug(f"Vérification conformité: {file_path}")
        
        # Récupération des métadonnées
        metadata_step = workflow_result.step_results.get(WorkflowStep.METADATA_EXTRACTION)
        if not metadata_step:
            raise ValueError("Métadonnées requises pour vérification conformité")
        
        metadata = metadata_step.result_data.get('metadata')
        content = {'file_path': file_path}  # Contenu basique
        
        loop = asyncio.get_event_loop()
        compliance_result = await loop.run_in_executor(
            None,
            self.compliance_checker.check_compliance,
            content,
            metadata.__dict__ if metadata else {},
            config.target_platforms,
            config.compliance_jurisdictions
        )
        
        return {
            'compliance_result': compliance_result,
            'compliance_passed': compliance_result.overall_compliance in [
                ComplianceLevel.COMPLIANT, ComplianceLevel.WARNING
            ]
        }
    
    async def _execute_parallel_steps(self, file_path: str, 
                                    config: WorkflowConfiguration,
                                    workflow_result: WorkflowResult) -> Dict[WorkflowStep, WorkflowStepResult]:
        """Exécute les étapes d'analyse en parallèle"""        
        parallel_steps = [
            WorkflowStep.QUALITY_ASSESSMENT,
            WorkflowStep.FINGERPRINT_GENERATION,
            WorkflowStep.BUSINESS_VALIDATION,
            WorkflowStep.COMPLIANCE_CHECK
        ]
        
        # Filtrage des étapes à exécuter
        steps_to_execute = [step for step in parallel_steps if step not in config.skip_steps]
        
        # Exécution en parallèle
        tasks = []
        for step in steps_to_execute:
            task = self._execute_workflow_step(step, file_path, config, workflow_result)
            tasks.append((step, task))
        
        results = {}
        completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for i, ((step, _), result) in enumerate(zip(tasks, completed_tasks)):
            if isinstance(result, Exception):
                # Création d'un résultat d'erreur
                error_result = WorkflowStepResult(
                    step=step,
                    status=WorkflowStatus.FAILED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    errors=[str(result)]
                )
                results[step] = error_result
            else:
                results[step] = result
        
        return results
    
    async def _execute_sequential_steps(self, file_path: str, 
                                      config: WorkflowConfiguration,
                                      workflow_result: WorkflowResult) -> Dict[WorkflowStep, WorkflowStepResult]:
        """Exécute les étapes d'analyse en séquentiel"""        
        sequential_steps = [
            WorkflowStep.QUALITY_ASSESSMENT,
            WorkflowStep.FINGERPRINT_GENERATION,
            WorkflowStep.BUSINESS_VALIDATION,
            WorkflowStep.COMPLIANCE_CHECK
        ]
        
        results = {}
        
        for step in sequential_steps:
            if step in config.skip_steps:
                continue
            
            step_result = await self._execute_workflow_step(step, file_path, config, workflow_result)
            results[step] = step_result
            
            # Arrêt en cas d'échec critique
            if step_result.status == WorkflowStatus.FAILED:
                creator_config = self.creator_workflows.get(config.creator_type, {})
                priority_steps = creator_config.get('priority_steps', [])
                
                if step in priority_steps:
                    self.logger.warning(f"Arrêt workflow - échec étape prioritaire: {step}")
                    break
        
        return results
    
    async def _execute_final_approval(self, workflow_result: WorkflowResult) -> WorkflowStepResult:
        """Étape finale d'approbation"""        
        step_start = datetime.now()
        approval_result = WorkflowStepResult(
            step=WorkflowStep.FINAL_APPROVAL,
            status=WorkflowStatus.RUNNING,
            start_time=step_start
        )
        
        try:
            # Analyse des résultats précédents
            blocking_issues = []
            warnings = []
            recommendations = []
            
            # Vérification qualité
            quality_step = workflow_result.step_results.get(WorkflowStep.QUALITY_ASSESSMENT)
            if quality_step and quality_step.result_data:
                quality_passed = quality_step.result_data.get('quality_assessment_passed', False)
                if not quality_passed:
                    blocking_issues.append("Qualité insuffisante")
                
                quality_result = quality_step.result_data.get('quality_result')
                if quality_result and quality_result.overall_level == QualityLevel.POOR:
                    blocking_issues.append("Niveau de qualité insuffisant")
            
            # Vérification conformité
            compliance_step = workflow_result.step_results.get(WorkflowStep.COMPLIANCE_CHECK)
            if compliance_step and compliance_step.result_data:
                compliance_passed = compliance_step.result_data.get('compliance_passed', False)
                if not compliance_passed:
                    blocking_issues.append("Non-conformité détectée")
                
                compliance_result = compliance_step.result_data.get('compliance_result')
                if compliance_result:
                    if compliance_result.overall_compliance == ComplianceLevel.CRITICAL:
                        blocking_issues.append("Problèmes de conformité critiques")
                    elif compliance_result.overall_compliance == ComplianceLevel.VIOLATION:
                        blocking_issues.append("Violations de conformité détectées")
            
            # Vérification business
            business_step = workflow_result.step_results.get(WorkflowStep.BUSINESS_VALIDATION)
            if business_step and business_step.result_data:
                business_passed = business_step.result_data.get('business_validation_passed', False)
                if not business_passed:
                    blocking_issues.append("Règles business non respectées")
            
            # Détermination du statut d'approbation
            approval_status = len(blocking_issues) == 0
            
            if approval_status:
                approval_result.status = WorkflowStatus.SUCCESS
                recommendations.append("Contenu approuvé pour publication")
            else:
                approval_result.status = WorkflowStatus.FAILED
                recommendations.extend([f"Corriger: {issue}" for issue in blocking_issues])
            
            approval_result.result_data = {
                'approval_status': approval_status,
                'blocking_issues': blocking_issues,
                'warnings': warnings,
                'recommendations': recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Erreur approbation finale: {e}")
            approval_result.status = WorkflowStatus.FAILED
            approval_result.errors.append(str(e))
        
        approval_result.end_time = datetime.now()
        approval_result.duration_seconds = (approval_result.end_time - approval_result.start_time).total_seconds()
        
        return approval_result
    
    async def _finalize_workflow(self, workflow_result: WorkflowResult) -> WorkflowResult:
        """Finalise le workflow et agrège les résultats"""        
        workflow_result.end_time = datetime.now()
        workflow_result.total_duration_seconds = (
            workflow_result.end_time - workflow_result.start_time
        ).total_seconds()
        
        # Agrégation des résultats
        try:
            # Métadonnées finales
            metadata_step = workflow_result.step_results.get(WorkflowStep.METADATA_EXTRACTION)
            if metadata_step and metadata_step.result_data:
                workflow_result.final_metadata = metadata_step.result_data.get('metadata')
            
            # Résultat qualité
            quality_step = workflow_result.step_results.get(WorkflowStep.QUALITY_ASSESSMENT)
            if quality_step and quality_step.result_data:
                workflow_result.quality_result = quality_step.result_data.get('quality_result')
            
            # Résultat conformité
            compliance_step = workflow_result.step_results.get(WorkflowStep.COMPLIANCE_CHECK)
            if compliance_step and compliance_step.result_data:
                workflow_result.compliance_result = compliance_step.result_data.get('compliance_result')
            
            # Résultat empreinte
            fingerprint_step = workflow_result.step_results.get(WorkflowStep.FINGERPRINT_GENERATION)
            if fingerprint_step and fingerprint_step.result_data:
                workflow_result.fingerprint_result = fingerprint_step.result_data.get('fingerprint_result')
            
            # Résultat business
            business_step = workflow_result.step_results.get(WorkflowStep.BUSINESS_VALIDATION)
            if business_step and business_step.result_data:
                workflow_result.business_result = business_step.result_data.get('business_result')
            
            # Status d'approbation
            approval_step = workflow_result.step_results.get(WorkflowStep.FINAL_APPROVAL)
            if approval_step and approval_step.result_data:
                workflow_result.approval_status = approval_step.result_data.get('approval_status', False)
                workflow_result.blocking_issues = approval_step.result_data.get('blocking_issues', [])
                workflow_result.recommendations = approval_step.result_data.get('recommendations', [])
            
            # Détermination du status global
            failed_steps = [step for step, result in workflow_result.step_results.items() 
                          if result.status == WorkflowStatus.FAILED]
            
            if failed_steps:
                workflow_result.overall_status = WorkflowStatus.FAILED
            elif workflow_result.blocking_issues:
                workflow_result.overall_status = WorkflowStatus.WARNING
            else:
                workflow_result.overall_status = WorkflowStatus.SUCCESS
            
            # Génération des prochaines étapes
            workflow_result.next_steps = self._generate_next_steps(workflow_result)
            
        except Exception as e:
            self.logger.error(f"Erreur finalisation workflow: {e}")
            workflow_result.overall_status = WorkflowStatus.FAILED
        
        self.logger.info(f"Workflow terminé: {workflow_result.workflow_id} - Status: {workflow_result.overall_status}")
        
        return workflow_result
    
    def _generate_next_steps(self, workflow_result: WorkflowResult) -> List[str]:
        """Génère les prochaines étapes recommandées"""        next_steps = []
        
        if workflow_result.approval_status:
            next_steps.append("Procéder à la publication")
            next_steps.append("Surveiller les métriques de performance")
        else:
            next_steps.append("Corriger les problèmes identifiés")
            
            if workflow_result.quality_result and workflow_result.quality_result.overall_score < 0.7:
                next_steps.append("Améliorer la qualité du contenu")
            
            if workflow_result.compliance_result and workflow_result.compliance_result.required_actions:
                next_steps.extend(workflow_result.compliance_result.required_actions[:2])
            
            next_steps.append("Relancer la validation après corrections")
        
        return next_steps

class WorkflowValidator:
    """Validateur de workflow principal avec API simplifiée"""    
    def __init__(self):
        self.orchestrator = WorkflowOrchestrator()
        self.logger = logging.getLogger(f"{__name__}.WorkflowValidator")
    
    async def validate_content(self, file_path: str, 
                             creator_type: str = "musician",
                             content_type: str = "audio",
                             target_platforms: List[str] = None,
                             custom_config: Dict[str, Any] = None) -> WorkflowResult:
        """Interface simplifiée pour validation de contenu"""        
        if target_platforms is None:
            target_platforms = ["youtube", "spotify", "instagram"]
        
        # Configuration par défaut
        config = WorkflowConfiguration(
            creator_type=CreatorType(creator_type),
            content_type=content_type,
            target_platforms=target_platforms,
            quality_requirements=custom_config.get('quality_requirements', {}) if custom_config else {},
            compliance_jurisdictions=custom_config.get('jurisdictions', ['EU', 'US']) if custom_config else ['EU', 'US'],
            business_rules=custom_config.get('business_rules', {}) if custom_config else {}
        )
        
        # Personnalisation de la configuration
        if custom_config:
            if 'skip_steps' in custom_config:
                config.skip_steps = [WorkflowStep(step) for step in custom_config['skip_steps']]
            if 'parallel_execution' in custom_config:
                config.parallel_execution = custom_config['parallel_execution']
            if 'timeout_seconds' in custom_config:
                config.timeout_seconds = custom_config['timeout_seconds']
        
        return await self.orchestrator.validate_content_workflow(file_path, config)
    
    async def validate_batch_content(self, file_paths: List[str], 
                                   creator_type: str = "musician",
                                   content_type: str = "audio",
                                   target_platforms: List[str] = None) -> List[WorkflowResult]:
        """Validation en lot de contenus"""        
        tasks = []
        for file_path in file_paths:
            task = self.validate_content(file_path, creator_type, content_type, target_platforms)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Gestion des erreurs
        workflow_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Création d'un résultat d'erreur
                error_result = WorkflowResult(
                    workflow_id=str(uuid.uuid4()),
                    configuration=WorkflowConfiguration(
                        creator_type=CreatorType(creator_type),
                        content_type=content_type,
                        target_platforms=target_platforms or [],
                        quality_requirements={},
                        compliance_jurisdictions=[],
                        business_rules={}
                    ),
                    overall_status=WorkflowStatus.FAILED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    blocking_issues=[f"Erreur: {str(result)}"]
                )
                workflow_results.append(error_result)
            else:
                workflow_results.append(result)
        
        return workflow_results
    
    def get_active_workflows(self) -> Dict[str, WorkflowResult]:
        """Retourne les workflows actifs"""        return self.orchestrator._active_workflows.copy()
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowResult]:
        """Retourne le status d'un workflow spécifique"""        return self.orchestrator._active_workflows.get(workflow_id)

# Export des classes principales
__all__ = [
    'WorkflowValidator',
    'WorkflowOrchestrator',
    'WorkflowResult',
    'WorkflowConfiguration',
    'WorkflowStepResult',
    'WorkflowStep',
    'WorkflowStatus',
    'CreatorType'
]
