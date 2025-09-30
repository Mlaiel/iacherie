"""
🛡️ PROTECTION SERVICE ORCHESTRATION - Module Orchestration Services Protection Ainflue
===================================================================================

**Expert Team**: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Copyright**: ©2025 Ainflue Platform - Tous droits réservés

⚠️  PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
====================================================
Ce code constitue la propriété intellectuelle exclusive de Fahed Mlaiel.
- Email: mlaiel@live.de  
- Projet: Ainflue Platform
- Licence: Propriétaire - Usage commercial interdit sans autorisation
- Protection: Code source confidentiel

🛡️ LOGIQUE MÉTIER AINFLUE - PROTECTION SERVICE ORCHESTRATION
=========================================================
Orchestration services protection contenu Ainflue:
- Copyright analysis & DMCA processing services
- Content moderation & compliance services
- IP protection & anti-piracy services
- Legal compliance & audit trail services
- Security screening & threat detection services
"""

import asyncio
import logging
import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from collections import defaultdict, deque

# Ainflue Core Imports
from .distributed_service_registry import DistributedServiceRegistry, ServiceInstance
from .intelligent_load_balancer import IntelligentLoadBalancer

logger = logging.getLogger(__name__)

class ProtectionServiceType(Enum):
    """Types de services protection Ainflue."""
    COPYRIGHT_ANALYZER = "copyright_analyzer"
    DMCA_PROCESSOR = "dmca_processor"
    CONTENT_MODERATOR = "content_moderator"
    IP_PROTECTOR = "ip_protector"
    ANTI_PIRACY = "anti_piracy"
    LEGAL_COMPLIANCE = "legal_compliance"
    AUDIT_TRAIL = "audit_trail"
    SECURITY_SCREENER = "security_screener"
    THREAT_DETECTOR = "threat_detector"
    BLOCKCHAIN_VERIFIER = "blockchain_verifier"
    WATERMARK_DETECTOR = "watermark_detector"
    CONTENT_HASHER = "content_hasher"

class ProtectionLevel(Enum):
    """Niveaux de protection."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    MAXIMUM = "maximum"

class ThreatSeverity(Enum):
    """Sévérité des menaces."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class ProtectionRequest:
    """Requête de protection contenu."""
    request_id: str
    content_id: str
    content_type: str
    protection_level: ProtectionLevel
    required_services: Set[ProtectionServiceType]
    priority: ThreatSeverity
    creator_id: str
    legal_jurisdiction: str
    compliance_requirements: Set[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProtectionResult:
    """Résultat protection contenu."""
    request_id: str
    protection_score: float  # 0.0 - 1.0
    threats_detected: List[Dict[str, Any]]
    compliance_status: Dict[str, bool]
    legal_recommendations: List[str]
    audit_trail: List[Dict[str, Any]]
    blockchain_proof: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ProtectionServiceCapability:
    """Capacité service protection."""
    service_type: ProtectionServiceType
    supported_content_types: Set[str]
    supported_jurisdictions: Set[str]
    compliance_standards: Set[str]
    ai_confidence_threshold: float
    processing_speed: float  # items/second
    legal_review_required: bool
    audit_trail_enabled: bool
    real_time_detection: bool
    batch_processing: bool

class ProtectionServiceOrchestrator:
    """Orchestrateur services protection Ainflue."""
    
    def __init__(self, redis_client: aioredis.Redis,
                 registry: DistributedServiceRegistry,
                 load_balancer: IntelligentLoadBalancer):
        self.redis_client = redis_client
        self.registry = registry
        self.load_balancer = load_balancer
        
        # Services protection par type
        self.protection_services: Dict[ProtectionServiceType, List[ServiceInstance]] = defaultdict(list)
        self.service_capabilities: Dict[str, ProtectionServiceCapability] = {}
        
        # Configuration orchestration
        self.protection_workflows = self._initialize_protection_workflows()
        self.compliance_rules = self._initialize_compliance_rules()
        self.threat_models = self._initialize_threat_models()
        
        # Cache et métriques
        self.protection_cache: Dict[str, ProtectionResult] = {}
        self.threat_intelligence: Dict[str, Any] = {}
        
        # Tâches background
        self._running = False
        self._threat_intelligence_task: Optional[asyncio.Task] = None
        self._compliance_monitoring_task: Optional[asyncio.Task] = None
        
        logger.info("🛡️ ProtectionServiceOrchestrator initialisé")
    
    def _initialize_protection_workflows(self) -> Dict[ProtectionLevel, List[ProtectionServiceType]]:
        """Initialise workflows protection par niveau."""
        return {
            ProtectionLevel.BASIC: [
                ProtectionServiceType.CONTENT_HASHER,
                ProtectionServiceType.SECURITY_SCREENER
            ],
            ProtectionLevel.STANDARD: [
                ProtectionServiceType.CONTENT_HASHER,
                ProtectionServiceType.SECURITY_SCREENER,
                ProtectionServiceType.COPYRIGHT_ANALYZER,
                ProtectionServiceType.CONTENT_MODERATOR
            ],
            ProtectionLevel.PREMIUM: [
                ProtectionServiceType.CONTENT_HASHER,
                ProtectionServiceType.SECURITY_SCREENER,
                ProtectionServiceType.COPYRIGHT_ANALYZER,
                ProtectionServiceType.CONTENT_MODERATOR,
                ProtectionServiceType.WATERMARK_DETECTOR,
                ProtectionServiceType.THREAT_DETECTOR
            ],
            ProtectionLevel.ENTERPRISE: [
                ProtectionServiceType.CONTENT_HASHER,
                ProtectionServiceType.SECURITY_SCREENER,
                ProtectionServiceType.COPYRIGHT_ANALYZER,
                ProtectionServiceType.CONTENT_MODERATOR,
                ProtectionServiceType.WATERMARK_DETECTOR,
                ProtectionServiceType.THREAT_DETECTOR,
                ProtectionServiceType.IP_PROTECTOR,
                ProtectionServiceType.LEGAL_COMPLIANCE
            ],
            ProtectionLevel.MAXIMUM: [
                ProtectionServiceType.CONTENT_HASHER,
                ProtectionServiceType.SECURITY_SCREENER,
                ProtectionServiceType.COPYRIGHT_ANALYZER,
                ProtectionServiceType.CONTENT_MODERATOR,
                ProtectionServiceType.WATERMARK_DETECTOR,
                ProtectionServiceType.THREAT_DETECTOR,
                ProtectionServiceType.IP_PROTECTOR,
                ProtectionServiceType.LEGAL_COMPLIANCE,
                ProtectionServiceType.DMCA_PROCESSOR,
                ProtectionServiceType.ANTI_PIRACY,
                ProtectionServiceType.BLOCKCHAIN_VERIFIER,
                ProtectionServiceType.AUDIT_TRAIL
            ]
        }
    
    def _initialize_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialise règles compliance par juridiction."""
        return {
            'US': {
                'dmca_required': True,
                'fair_use_analysis': True,
                'copyright_notice': True,
                'takedown_procedures': 'dmca_standard'
            },
            'EU': {
                'gdpr_compliance': True,
                'copyright_directive': True,
                'data_portability': True,
                'right_to_erasure': True
            },
            'UK': {
                'uk_copyright_act': True,
                'ofcom_compliance': True,
                'data_protection_act': True
            },
            'FR': {
                'hadopi_compliance': True,
                'french_copyright_law': True,
                'cnil_requirements': True
            },
            'DE': {
                'urheberrecht': True,
                'bundesdatenschutzgesetz': True,
                'telemediengesetz': True
            }
        }
    
    def _initialize_threat_models(self) -> Dict[ThreatSeverity, Dict[str, Any]]:
        """Initialise modèles détection menaces."""
        return {
            ThreatSeverity.LOW: {
                'response_time_sla': 3600,  # 1 heure
                'automated_response': True,
                'human_review': False,
                'escalation_threshold': 0.7
            },
            ThreatSeverity.MEDIUM: {
                'response_time_sla': 1800,  # 30 minutes
                'automated_response': True,
                'human_review': False,
                'escalation_threshold': 0.8
            },
            ThreatSeverity.HIGH: {
                'response_time_sla': 600,   # 10 minutes
                'automated_response': True,
                'human_review': True,
                'escalation_threshold': 0.9
            },
            ThreatSeverity.CRITICAL: {
                'response_time_sla': 300,   # 5 minutes
                'automated_response': True,
                'human_review': True,
                'escalation_threshold': 0.95
            },
            ThreatSeverity.EMERGENCY: {
                'response_time_sla': 60,    # 1 minute
                'automated_response': True,
                'human_review': True,
                'escalation_threshold': 0.99
            }
        }
    
    async def start(self):
        """Démarre l'orchestrateur protection."""
        if self._running:
            return
        
        self._running = True
        
        # Démarrer tâches background
        self._threat_intelligence_task = asyncio.create_task(self._threat_intelligence_loop())
        self._compliance_monitoring_task = asyncio.create_task(self._compliance_monitoring_loop())
        
        # Charger services protection
        await self._load_protection_services()
        
        logger.info("✅ ProtectionServiceOrchestrator démarré")
    
    async def stop(self):
        """Arrête l'orchestrateur protection."""
        if not self._running:
            return
        
        self._running = False
        
        # Arrêter tâches
        if self._threat_intelligence_task:
            self._threat_intelligence_task.cancel()
        if self._compliance_monitoring_task:
            self._compliance_monitoring_task.cancel()
        
        # Attendre fin des tâches
        tasks = [t for t in [self._threat_intelligence_task, self._compliance_monitoring_task] if t and not t.done()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("🛑 ProtectionServiceOrchestrator arrêté")
    
    async def orchestrate_protection(self, request: ProtectionRequest) -> ProtectionResult:
        """Orchestre services protection pour requête."""
        try:
            start_time = time.time()
            
            # Vérifier cache
            cached_result = await self._get_cached_protection_result(request)
            if cached_result:
                logger.info(f"Résultat protection en cache pour {request.request_id}")
                return cached_result
            
            # Déterminer services requis
            required_services = self._determine_required_services(request)
            
            # Orchestrer services en parallèle et séquence
            protection_results = await self._execute_protection_workflow(request, required_services)
            
            # Agréger résultats
            final_result = await self._aggregate_protection_results(request, protection_results)
            
            # Cache résultat
            await self._cache_protection_result(request, final_result)
            
            # Audit trail
            await self._log_protection_audit(request, final_result, time.time() - start_time)
            
            logger.info(f"Protection orchestrée pour {request.request_id} en {time.time() - start_time:.2f}s")
            return final_result
            
        except Exception as e:
            logger.error(f"Erreur orchestration protection {request.request_id}: {e}")
            # Retourner résultat d'échec
            return ProtectionResult(
                request_id=request.request_id,
                protection_score=0.0,
                threats_detected=[{'error': str(e)}],
                compliance_status={},
                legal_recommendations=['Erreur lors de l\'analyse - révision manuelle requise'],
                audit_trail=[]
            )
    
    def _determine_required_services(self, request: ProtectionRequest) -> List[ProtectionServiceType]:
        """Détermine services requis pour requête protection."""
        # Services selon niveau protection
        workflow_services = self.protection_workflows.get(request.protection_level, [])
        
        # Services spécifiquement requis
        specific_services = list(request.required_services)
        
        # Combiner et dédupliquer
        all_services = list(set(workflow_services + specific_services))
        
        # Ordonner selon priorité
        service_priority = {
            ProtectionServiceType.CONTENT_HASHER: 1,
            ProtectionServiceType.SECURITY_SCREENER: 2,
            ProtectionServiceType.THREAT_DETECTOR: 3,
            ProtectionServiceType.COPYRIGHT_ANALYZER: 4,
            ProtectionServiceType.WATERMARK_DETECTOR: 5,
            ProtectionServiceType.CONTENT_MODERATOR: 6,
            ProtectionServiceType.IP_PROTECTOR: 7,
            ProtectionServiceType.ANTI_PIRACY: 8,
            ProtectionServiceType.LEGAL_COMPLIANCE: 9,
            ProtectionServiceType.DMCA_PROCESSOR: 10,
            ProtectionServiceType.BLOCKCHAIN_VERIFIER: 11,
            ProtectionServiceType.AUDIT_TRAIL: 12
        }
        
        all_services.sort(key=lambda s: service_priority.get(s, 99))
        return all_services
    
    async def _execute_protection_workflow(self, request: ProtectionRequest,
                                         services: List[ProtectionServiceType]) -> Dict[ProtectionServiceType, Any]:
        """Exécute workflow protection."""
        results = {}
        
        # Services parallèles (phase 1 - détection rapide)
        parallel_services = [
            ProtectionServiceType.CONTENT_HASHER,
            ProtectionServiceType.SECURITY_SCREENER,
            ProtectionServiceType.THREAT_DETECTOR
        ]
        
        parallel_tasks = []
        for service_type in parallel_services:
            if service_type in services:
                task = self._execute_protection_service(request, service_type)
                parallel_tasks.append((service_type, task))
        
        # Exécuter services parallèles
        if parallel_tasks:
            parallel_results = await asyncio.gather(
                *[task for _, task in parallel_tasks],
                return_exceptions=True
            )
            
            for i, (service_type, _) in enumerate(parallel_tasks):
                if not isinstance(parallel_results[i], Exception):
                    results[service_type] = parallel_results[i]
                else:
                    logger.error(f"Erreur service {service_type}: {parallel_results[i]}")
        
        # Services séquentiels (phase 2 - analyse approfondie)
        sequential_services = [s for s in services if s not in parallel_services]
        
        for service_type in sequential_services:
            try:
                # Utiliser contexte des services précédents
                context = self._build_service_context(results)
                result = await self._execute_protection_service(request, service_type, context)
                results[service_type] = result
                
            except Exception as e:
                logger.error(f"Erreur service séquentiel {service_type}: {e}")
        
        return results
    
    async def _execute_protection_service(self, request: ProtectionRequest,
                                        service_type: ProtectionServiceType,
                                        context: Optional[Dict[str, Any]] = None) -> Any:
        """Exécute un service protection spécifique."""
        # Trouver service disponible
        service_instance = await self._find_optimal_protection_service(request, service_type)
        if not service_instance:
            raise Exception(f"Aucun service {service_type.value} disponible")
        
        # Préparer payload
        payload = {
            'request_id': request.request_id,
            'content_id': request.content_id,
            'content_type': request.content_type,
            'protection_level': request.protection_level.value,
            'priority': request.priority.value,
            'creator_id': request.creator_id,
            'legal_jurisdiction': request.legal_jurisdiction,
            'compliance_requirements': list(request.compliance_requirements),
            'metadata': request.metadata,
            'context': context or {}
        }
        
        # Appel service
        async with aiohttp.ClientSession() as session:
            service_url = f"{service_instance.url}/protect"
            async with session.post(service_url, json=payload, timeout=30) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Service {service_type.value} retourné status {response.status}")
    
    async def _find_optimal_protection_service(self, request: ProtectionRequest,
                                             service_type: ProtectionServiceType) -> Optional[ServiceInstance]:
        """Trouve service protection optimal."""
        available_services = self.protection_services.get(service_type, [])
        if not available_services:
            return None
        
        # Filtrer par capacités
        compatible_services = []
        for service in available_services:
            capability = self.service_capabilities.get(service.service_id)
            if capability and self._is_service_compatible(request, capability):
                compatible_services.append(service)
        
        if not compatible_services:
            return None
        
        # Utiliser load balancer pour sélection finale
        context = {
            'protection_level': request.protection_level.value,
            'priority': request.priority.value,
            'legal_jurisdiction': request.legal_jurisdiction
        }
        
        return await self.load_balancer.select_optimal_instance(
            f"protection_{service_type.value}", context
        )
    
    def _is_service_compatible(self, request: ProtectionRequest,
                             capability: ProtectionServiceCapability) -> bool:
        """Vérifie compatibilité service avec requête."""
        # Vérifier type contenu supporté
        if request.content_type not in capability.supported_content_types:
            return False
        
        # Vérifier juridiction supportée
        if request.legal_jurisdiction not in capability.supported_jurisdictions:
            return False
        
        # Vérifier exigences compliance
        if not request.compliance_requirements.issubset(capability.compliance_standards):
            return False
        
        return True
    
    def _build_service_context(self, previous_results: Dict[ProtectionServiceType, Any]) -> Dict[str, Any]:
        """Construit contexte pour services séquentiels."""
        context = {}
        
        # Hash contenu si disponible
        if ProtectionServiceType.CONTENT_HASHER in previous_results:
            hash_result = previous_results[ProtectionServiceType.CONTENT_HASHER]
            context['content_hash'] = hash_result.get('hash')
            context['content_fingerprint'] = hash_result.get('fingerprint')
        
        # Menaces détectées
        if ProtectionServiceType.THREAT_DETECTOR in previous_results:
            threats = previous_results[ProtectionServiceType.THREAT_DETECTOR]
            context['detected_threats'] = threats.get('threats', [])
            context['threat_score'] = threats.get('score', 0.0)
        
        # Screening sécurité
        if ProtectionServiceType.SECURITY_SCREENER in previous_results:
            security = previous_results[ProtectionServiceType.SECURITY_SCREENER]
            context['security_flags'] = security.get('flags', [])
            context['security_score'] = security.get('score', 0.0)
        
        return context
    
    async def _aggregate_protection_results(self, request: ProtectionRequest,
                                          results: Dict[ProtectionServiceType, Any]) -> ProtectionResult:
        """Agrège résultats services protection."""
        all_threats = []
        protection_scores = []
        compliance_status = {}
        legal_recommendations = []
        audit_entries = []
        
        # Agréger résultats par service
        for service_type, result in results.items():
            if not result:
                continue
            
            # Menaces détectées
            if 'threats' in result:
                service_threats = result['threats']
                for threat in service_threats:
                    threat['detected_by'] = service_type.value
                all_threats.extend(service_threats)
            
            # Scores protection
            if 'protection_score' in result:
                protection_scores.append(result['protection_score'])
            
            # Status compliance
            if 'compliance' in result:
                compliance_status.update(result['compliance'])
            
            # Recommandations légales
            if 'legal_recommendations' in result:
                legal_recommendations.extend(result['legal_recommendations'])
            
            # Audit trail
            if 'audit_entry' in result:
                audit_entries.append({
                    'service': service_type.value,
                    'timestamp': datetime.now().isoformat(),
                    'result': result['audit_entry']
                })
        
        # Calculer score protection final
        final_protection_score = np.mean(protection_scores) if protection_scores else 0.0
        
        # Ajuster score selon sévérité menaces
        if all_threats:
            max_threat_severity = max([t.get('severity', 1) for t in all_threats])
            severity_penalty = max_threat_severity / 10.0
            final_protection_score = max(0.0, final_protection_score - severity_penalty)
        
        # Preuve blockchain si service disponible
        blockchain_proof = None
        if ProtectionServiceType.BLOCKCHAIN_VERIFIER in results:
            blockchain_result = results[ProtectionServiceType.BLOCKCHAIN_VERIFIER]
            blockchain_proof = blockchain_result.get('proof_hash')
        
        return ProtectionResult(
            request_id=request.request_id,
            protection_score=final_protection_score,
            threats_detected=all_threats,
            compliance_status=compliance_status,
            legal_recommendations=list(set(legal_recommendations)),  # Dédupliquer
            audit_trail=audit_entries,
            blockchain_proof=blockchain_proof
        )
    
    async def _get_cached_protection_result(self, request: ProtectionRequest) -> Optional[ProtectionResult]:
        """Récupère résultat protection en cache."""
        try:
            # Clé cache basée sur contenu et niveau protection
            cache_key = f"protection:{hashlib.sha256(f'{request.content_id}:{request.protection_level.value}'.encode()).hexdigest()}"
            
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                # Vérifier si cache encore valide (1 heure)
                cached_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cached_time < timedelta(hours=1):
                    return ProtectionResult(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur récupération cache protection: {e}")
            return None
    
    async def _cache_protection_result(self, request: ProtectionRequest, result: ProtectionResult):
        """Met en cache résultat protection."""
        try:
            cache_key = f"protection:{hashlib.sha256(f'{request.content_id}:{request.protection_level.value}'.encode()).hexdigest()}"
            
            # Sérialiser résultat
            result_data = {
                'request_id': result.request_id,
                'protection_score': result.protection_score,
                'threats_detected': result.threats_detected,
                'compliance_status': result.compliance_status,
                'legal_recommendations': result.legal_recommendations,
                'audit_trail': result.audit_trail,
                'blockchain_proof': result.blockchain_proof,
                'timestamp': result.timestamp.isoformat()
            }
            
            # Cache pour 1 heure
            await self.redis_client.setex(
                cache_key,
                3600,
                json.dumps(result_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Erreur mise en cache protection: {e}")
    
    async def _log_protection_audit(self, request: ProtectionRequest,
                                  result: ProtectionResult, processing_time: float):
        """Log audit trail protection."""
        try:
            audit_entry = {
                'request_id': request.request_id,
                'content_id': request.content_id,
                'creator_id': request.creator_id,
                'protection_level': request.protection_level.value,
                'protection_score': result.protection_score,
                'threats_count': len(result.threats_detected),
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat(),
                'compliance_status': result.compliance_status
            }
            
            # Log structuré pour audit
            audit_key = f"protection_audit:{datetime.now().strftime('%Y%m%d')}:{request.request_id}"
            await self.redis_client.setex(
                audit_key,
                timedelta(days=365).total_seconds(),  # Rétention 1 an
                json.dumps(audit_entry)
            )
            
            # Métriques globales
            await self._update_protection_metrics(request, result, processing_time)
            
        except Exception as e:
            logger.error(f"Erreur log audit protection: {e}")
    
    async def _update_protection_metrics(self, request: ProtectionRequest,
                                       result: ProtectionResult, processing_time: float):
        """Met à jour métriques protection."""
        try:
            # Incrémenter compteurs
            await self.redis_client.incr("protection_requests_total")
            await self.redis_client.incr(f"protection_requests_{request.protection_level.value}")
            
            if result.threats_detected:
                await self.redis_client.incr("protection_threats_detected")
            
            # Temps de traitement moyen
            await self.redis_client.lpush("protection_processing_times", processing_time)
            await self.redis_client.ltrim("protection_processing_times", 0, 999)  # Garder 1000 derniers
            
        except Exception as e:
            logger.error(f"Erreur mise à jour métriques protection: {e}")
    
    async def _load_protection_services(self):
        """Charge services protection depuis registry."""
        try:
            # Récupérer tous services avec tag "protection"
            all_services = await self.registry.get_services_by_tag("protection")
            
            for service in all_services:
                # Déterminer type service protection
                service_type = self._determine_service_type(service)
                if service_type:
                    self.protection_services[service_type].append(service)
                    
                    # Charger capacités service
                    capability = await self._load_service_capability(service)
                    if capability:
                        self.service_capabilities[service.service_id] = capability
            
            logger.info(f"✅ {len(all_services)} services protection chargés")
            
        except Exception as e:
            logger.error(f"Erreur chargement services protection: {e}")
    
    def _determine_service_type(self, service: ServiceInstance) -> Optional[ProtectionServiceType]:
        """Détermine type service protection."""
        service_name = service.service_name.lower()
        
        if 'copyright' in service_name:
            return ProtectionServiceType.COPYRIGHT_ANALYZER
        elif 'dmca' in service_name:
            return ProtectionServiceType.DMCA_PROCESSOR
        elif 'moderation' in service_name or 'moderate' in service_name:
            return ProtectionServiceType.CONTENT_MODERATOR
        elif 'ip_protect' in service_name:
            return ProtectionServiceType.IP_PROTECTOR
        elif 'anti_piracy' in service_name or 'piracy' in service_name:
            return ProtectionServiceType.ANTI_PIRACY
        elif 'compliance' in service_name or 'legal' in service_name:
            return ProtectionServiceType.LEGAL_COMPLIANCE
        elif 'audit' in service_name:
            return ProtectionServiceType.AUDIT_TRAIL
        elif 'security' in service_name or 'screen' in service_name:
            return ProtectionServiceType.SECURITY_SCREENER
        elif 'threat' in service_name:
            return ProtectionServiceType.THREAT_DETECTOR
        elif 'blockchain' in service_name:
            return ProtectionServiceType.BLOCKCHAIN_VERIFIER
        elif 'watermark' in service_name:
            return ProtectionServiceType.WATERMARK_DETECTOR
        elif 'hash' in service_name:
            return ProtectionServiceType.CONTENT_HASHER
        
        return None
    
    async def _load_service_capability(self, service: ServiceInstance) -> Optional[ProtectionServiceCapability]:
        """Charge capacités d'un service protection."""
        try:
            async with aiohttp.ClientSession() as session:
                capability_url = f"{service.url}/capabilities"
                async with session.get(capability_url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        return ProtectionServiceCapability(
                            service_type=ProtectionServiceType(data['service_type']),
                            supported_content_types=set(data['supported_content_types']),
                            supported_jurisdictions=set(data['supported_jurisdictions']),
                            compliance_standards=set(data['compliance_standards']),
                            ai_confidence_threshold=data['ai_confidence_threshold'],
                            processing_speed=data['processing_speed'],
                            legal_review_required=data['legal_review_required'],
                            audit_trail_enabled=data['audit_trail_enabled'],
                            real_time_detection=data['real_time_detection'],
                            batch_processing=data['batch_processing']
                        )
            return None
            
        except Exception as e:
            logger.error(f"Erreur chargement capacités service {service.service_id}: {e}")
            return None
    
    async def _threat_intelligence_loop(self):
        """Boucle mise à jour threat intelligence."""
        while self._running:
            try:
                # Collecter threat intelligence
                await self._update_threat_intelligence()
                await asyncio.sleep(300)  # Toutes les 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur threat intelligence loop: {e}")
                await asyncio.sleep(60)
    
    async def _compliance_monitoring_loop(self):
        """Boucle monitoring compliance."""
        while self._running:
            try:
                # Vérifier compliance réglementaire
                await self._monitor_compliance_status()
                await asyncio.sleep(3600)  # Toutes les heures
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur compliance monitoring loop: {e}")
                await asyncio.sleep(300)
    
    async def _update_threat_intelligence(self):
        """Met à jour threat intelligence."""
        try:
            # Agréger menaces récentes
            recent_threats = await self._aggregate_recent_threats()
            
            # Analyser patterns
            threat_patterns = await self._analyze_threat_patterns(recent_threats)
            
            # Mettre à jour modèles
            self.threat_intelligence.update({
                'last_update': datetime.now().isoformat(),
                'recent_threats': recent_threats,
                'patterns': threat_patterns
            })
            
            logger.info("✅ Threat intelligence mise à jour")
            
        except Exception as e:
            logger.error(f"Erreur mise à jour threat intelligence: {e}")
    
    async def _aggregate_recent_threats(self) -> List[Dict[str, Any]]:
        """Agrège menaces récentes."""
        try:
            # Récupérer audits récents (dernières 24h)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            threats = []
            current_date = start_date
            
            while current_date <= end_date:
                audit_pattern = f"protection_audit:{current_date.strftime('%Y%m%d')}:*"
                audit_keys = await self.redis_client.keys(audit_pattern)
                
                for key in audit_keys:
                    audit_data = await self.redis_client.get(key)
                    if audit_data:
                        audit = json.loads(audit_data)
                        if audit.get('threats_count', 0) > 0:
                            threats.append({
                                'timestamp': audit['timestamp'],
                                'content_id': audit['content_id'],
                                'threats_count': audit['threats_count'],
                                'protection_score': audit['protection_score']
                            })
                
                current_date += timedelta(days=1)
            
            return threats[-1000:]  # Dernières 1000 menaces
            
        except Exception as e:
            logger.error(f"Erreur agrégation menaces récentes: {e}")
            return []
    
    async def _analyze_threat_patterns(self, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse patterns dans menaces."""
        if not threats:
            return {}
        
        try:
            # Patterns temporels
            threat_times = [datetime.fromisoformat(t['timestamp']).hour for t in threats]
            peak_hours = [h for h in range(24) if threat_times.count(h) > np.mean([threat_times.count(h) for h in range(24)])]
            
            # Distribution scores protection
            protection_scores = [t['protection_score'] for t in threats]
            avg_protection_score = np.mean(protection_scores)
            
            # Tendances
            threats_by_hour = defaultdict(int)
            for threat in threats:
                hour = datetime.fromisoformat(threat['timestamp']).strftime('%H')
                threats_by_hour[hour] += 1
            
            return {
                'peak_threat_hours': peak_hours,
                'avg_protection_score': avg_protection_score,
                'threats_by_hour': dict(threats_by_hour),
                'total_threats_analyzed': len(threats)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse patterns menaces: {e}")
            return {}
    
    async def _monitor_compliance_status(self):
        """Monitor status compliance réglementaire."""
        try:
            # Vérifier audits compliance récents
            compliance_issues = await self._check_compliance_issues()
            
            if compliance_issues:
                logger.warning(f"🚨 {len(compliance_issues)} problèmes compliance détectés")
                
                # Alertes pour problèmes critiques
                critical_issues = [issue for issue in compliance_issues if issue.get('severity') == 'critical']
                if critical_issues:
                    await self._send_compliance_alerts(critical_issues)
            
        except Exception as e:
            logger.error(f"Erreur monitoring compliance: {e}")
    
    async def _check_compliance_issues(self) -> List[Dict[str, Any]]:
        """Vérifie problèmes compliance."""
        # Implémentation simplifiée - à étendre selon besoins réels
        return []
    
    async def _send_compliance_alerts(self, issues: List[Dict[str, Any]]):
        """Envoie alertes compliance."""
        for issue in issues:
            logger.critical(f"🚨 COMPLIANCE ALERT: {issue}")
    
    async def get_protection_metrics(self) -> Dict[str, Any]:
        """Récupère métriques protection."""
        try:
            total_requests = await self.redis_client.get("protection_requests_total")
            threats_detected = await self.redis_client.get("protection_threats_detected")
            
            # Temps de traitement moyens
            processing_times = await self.redis_client.lrange("protection_processing_times", 0, -1)
            avg_processing_time = np.mean([float(t) for t in processing_times]) if processing_times else 0
            
            return {
                'total_requests': int(total_requests) if total_requests else 0,
                'threats_detected': int(threats_detected) if threats_detected else 0,
                'avg_processing_time': avg_processing_time,
                'threat_intelligence_last_update': self.threat_intelligence.get('last_update'),
                'active_protection_services': sum(len(services) for services in self.protection_services.values())
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération métriques protection: {e}")
            return {}

# Factory pour création instance
async def create_protection_service_orchestrator(redis_client: aioredis.Redis,
                                               registry: DistributedServiceRegistry,
                                               load_balancer: IntelligentLoadBalancer) -> ProtectionServiceOrchestrator:
    """Crée instance ProtectionServiceOrchestrator."""
    orchestrator = ProtectionServiceOrchestrator(redis_client, registry, load_balancer)
    await orchestrator.start()
    return orchestrator

# Export classes principales
__all__ = [
    'ProtectionServiceOrchestrator',
    'ProtectionServiceType',
    'ProtectionLevel',
    'ThreatSeverity',
    'ProtectionRequest',
    'ProtectionResult',
    'ProtectionServiceCapability',
    'create_protection_service_orchestrator'
]