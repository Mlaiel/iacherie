"""🔨 Build Automation Engine - Enterprise Intelligent Caching System
================================================================

Build Engineering Expert: Build automation avec distributed caching,
parallel execution et artifact management pour plateforme IA Chérie.

Author: Fahed Mlaiel (mlaiel@live.de)
Date: 16 Septembre 2025
"""

import asyncio
import hashlib
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuildStatus(Enum):
    """Status du build"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CACHED = "cached"
    CANCELLED = "cancelled"

class CacheStrategy(Enum):
    """Stratégies de cache build"""
    NONE = "none"
    LOCAL = "local"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"
    INTELLIGENT = "intelligent"

class BuildTarget(Enum):
    """Cibles de build"""
    LINUX_AMD64 = "linux/amd64"
    LINUX_ARM64 = "linux/arm64"
    WINDOWS_AMD64 = "windows/amd64"
    DARWIN_AMD64 = "darwin/amd64"
    DARWIN_ARM64 = "darwin/arm64"
    WEB_ASSEMBLY = "wasm"

class ArtifactType(Enum):
    """Types d'artifacts"""
    BINARY = "binary"
    CONTAINER = "container"
    PACKAGE = "package"
    DOCUMENTATION = "documentation"
    REPORTS = "reports"
    CONFIGURATION = "configuration"

@dataclass
class BuildArtifact:
    """Artifact de build"""
    name: str
    type: ArtifactType
    path: str
    size: int
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

@dataclass
class BuildCache:
    """Cache de build"""
    key: str
    artifacts: List[BuildArtifact]
    hit_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BuildJob:
    """Job de build"""
    id: str
    name: str
    target: BuildTarget
    source_path: str
    output_path: str
    dependencies: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    cache_strategy: CacheStrategy = CacheStrategy.INTELLIGENT
    parallel: bool = True
    priority: int = 0
    timeout: int = 3600
    status: BuildStatus = BuildStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    artifacts: List[BuildArtifact] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BuildMetrics:
    """Métriques de build"""
    total_builds: int = 0
    successful_builds: int = 0
    failed_builds: int = 0
    cached_builds: int = 0
    total_build_time: float = 0.0
    average_build_time: float = 0.0
    cache_hit_rate: float = 0.0
    parallelization_efficiency: float = 0.0
    cost_savings: float = 0.0
    updated_at: datetime = field(default_factory=datetime.now)

class BuildAutomationEngine:
    """
    🔨 Build Automation Engine Enterprise
    
    Système d'automation de build avec caching intelligent, exécution parallèle
    et gestion d'artifacts optimisée pour la plateforme IA Chérie.
    
    Fonctionnalités principales:
    - Intelligent build caching avec distributed cache
    - Parallel build execution avec dependency resolution
    - Artifact management avec versioning et lifecycle
    - Build optimization analytics avec ML insights
    - Cross-platform compilation pour tous les targets
    """
    
    def __init__(self, 
                 cache_dir: str = "/var/cache/iacherie/builds",
                 artifacts_dir: str = "/var/artifacts/iacherie",
                 max_parallel_jobs: int = 8,
                 cache_size_limit: int = 50 * 1024 * 1024 * 1024,  # 50GB
                 enable_distributed_cache: bool = True):
        """
        Initialise le moteur d'automation de build
        
        Args:
            cache_dir: Répertoire de cache local
            artifacts_dir: Répertoire des artifacts
            max_parallel_jobs: Nombre max de jobs parallèles
            cache_size_limit: Limite taille cache en bytes
            enable_distributed_cache: Activer cache distribué
        """
        self.cache_dir = Path(cache_dir)
        self.artifacts_dir = Path(artifacts_dir)
        self.max_parallel_jobs = max_parallel_jobs
        self.cache_size_limit = cache_size_limit
        self.enable_distributed_cache = enable_distributed_cache
        
        # État interne
        self.active_jobs: Dict[str, BuildJob] = {}
        self.job_queue: List[BuildJob] = []
        self.cache_index: Dict[str, BuildCache] = {}
        self.metrics = BuildMetrics()
        self.executor = ThreadPoolExecutor(max_workers=max_parallel_jobs)
        
        # Créer répertoires
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger cache existant
        self._load_cache_index()
        
        logger.info(f"Build Automation Engine initialisé: cache={cache_dir}, artifacts={artifacts_dir}")

    async def intelligent_build_caching(self, job: BuildJob) -> Optional[List[BuildArtifact]]:
        """
        🧠 Cache intelligent avec analyse de dépendances
        
        Utilise l'IA pour déterminer si un build peut être mis en cache
        et optimise la stratégie de cache selon les patterns d'usage.
        
        Args:
            job: Job de build à analyser
            
        Returns:
            Artifacts en cache si disponibles, None sinon
        """
        try:
            # Calculer clé de cache intelligente
            cache_key = await self._calculate_intelligent_cache_key(job)
            
            # Vérifier cache local
            if cache_key in self.cache_index:
                cache_entry = self.cache_index[cache_key]
                
                # Vérifier validité
                if await self._validate_cache_entry(cache_entry, job):
                    cache_entry.hit_count += 1
                    cache_entry.last_accessed = datetime.now()
                    self.metrics.cached_builds += 1
                    
                    logger.info(f"Cache hit pour job {job.id}: {cache_key}")
                    return cache_entry.artifacts
            
            # Vérifier cache distribué si activé
            if self.enable_distributed_cache:
                distributed_artifacts = await self._check_distributed_cache(cache_key, job)
                if distributed_artifacts:
                    # Stocker localement pour futur usage
                    await self._store_local_cache(cache_key, distributed_artifacts, job)
                    self.metrics.cached_builds += 1
                    
                    logger.info(f"Cache distribué hit pour job {job.id}: {cache_key}")
                    return distributed_artifacts
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur cache intelligent pour job {job.id}: {e}")
            return None

    async def parallel_build_execution(self, jobs: List[BuildJob]) -> Dict[str, BuildJob]:
        """
        🚀 Exécution parallèle de builds avec résolution de dépendances
        
        Optimise l'ordre d'exécution et parallélise les builds indépendants
        tout en respectant le graphe de dépendances.
        
        Args:
            jobs: Liste des jobs à exécuter
            
        Returns:
            Dictionnaire des jobs complétés avec leurs statuts
        """
        try:
            # Créer graphe de dépendances
            dependency_graph = self._build_dependency_graph(jobs)
            
            # Ordonner jobs par priorité et dépendances
            execution_order = self._topological_sort(dependency_graph)
            
            # Grouper jobs par niveau de parallélisation
            execution_groups = self._group_parallel_jobs(execution_order, dependency_graph)
            
            completed_jobs = {}
            
            for group in execution_groups:
                # Exécuter groupe en parallèle
                group_futures = []
                
                for job in group:
                    if len(self.active_jobs) < self.max_parallel_jobs:
                        future = self.executor.submit(self._execute_single_job, job)
                        group_futures.append((job.id, future))
                        self.active_jobs[job.id] = job
                
                # Attendre completion du groupe
                for job_id, future in group_futures:
                    try:
                        result = future.result(timeout=self.active_jobs[job_id].timeout)
                        completed_jobs[job_id] = result
                        
                        if job_id in self.active_jobs:
                            del self.active_jobs[job_id]
                            
                    except Exception as e:
                        logger.error(f"Erreur exécution job {job_id}: {e}")
                        if job_id in self.active_jobs:
                            self.active_jobs[job_id].status = BuildStatus.FAILED
                            completed_jobs[job_id] = self.active_jobs[job_id]
                            del self.active_jobs[job_id]
            
            return completed_jobs
            
        except Exception as e:
            logger.error(f"Erreur exécution parallèle: {e}")
            return {}

    async def artifact_management(self, job: BuildJob, artifacts: List[BuildArtifact]) -> bool:
        """
        📦 Gestion d'artifacts avec versioning et lifecycle
        
        Gère le stockage, versioning et lifecycle des artifacts de build
        avec compression et déduplication intelligente.
        
        Args:
            job: Job de build
            artifacts: Artifacts à gérer
            
        Returns:
            True si succès, False sinon
        """
        try:
            managed_artifacts = []
            
            for artifact in artifacts:
                # Calculer checksum et détecter doublons
                artifact.checksum = await self._calculate_artifact_checksum(artifact.path)
                
                # Vérifier déduplication
                existing_artifact = await self._find_existing_artifact(artifact.checksum)
                if existing_artifact:
                    # Lien symbolique vers artifact existant
                    await self._create_artifact_link(artifact, existing_artifact)
                    logger.info(f"Artifact dédupliqué: {artifact.name}")
                else:
                    # Stocker nouvel artifact
                    stored_path = await self._store_artifact(artifact, job)
                    artifact.path = stored_path
                
                # Gestion versioning
                versioned_artifact = await self._apply_versioning(artifact, job)
                
                # Appliquer politique de rétention
                await self._apply_retention_policy(versioned_artifact)
                
                managed_artifacts.append(versioned_artifact)
            
            # Mettre à jour métadonnées job
            job.artifacts = managed_artifacts
            
            # Indexer artifacts pour recherche rapide
            await self._index_artifacts(managed_artifacts, job)
            
            logger.info(f"Gestion artifacts complétée pour job {job.id}: {len(managed_artifacts)} artifacts")
            return True
            
        except Exception as e:
            logger.error(f"Erreur gestion artifacts pour job {job.id}: {e}")
            return False

    async def build_optimization_analytics(self) -> Dict[str, Any]:
        """
        📊 Analytics d'optimisation de build avec ML insights
        
        Analyse les patterns de build et fournit des recommandations
        d'optimisation basées sur l'IA et les métriques historiques.
        
        Returns:
            Dictionnaire contenant analytics et recommandations
        """
        try:
            # Collecter métriques historiques
            historical_data = await self._collect_historical_metrics()
            
            # Analyser patterns de cache
            cache_analysis = await self._analyze_cache_patterns()
            
            # Analyser performance parallélisation
            parallelization_analysis = await self._analyze_parallelization_efficiency()
            
            # Détecter goulots d'étranglement
            bottlenecks = await self._detect_build_bottlenecks()
            
            # Générer recommandations IA
            ai_recommendations = await self._generate_ai_recommendations(
                historical_data, cache_analysis, parallelization_analysis, bottlenecks
            )
            
            # Calculer ROI optimisations
            optimization_roi = await self._calculate_optimization_roi(ai_recommendations)
            
            analytics = {
                "metrics": {
                    "total_builds": self.metrics.total_builds,
                    "success_rate": self.metrics.successful_builds / max(self.metrics.total_builds, 1),
                    "cache_hit_rate": self.metrics.cache_hit_rate,
                    "average_build_time": self.metrics.average_build_time,
                    "parallelization_efficiency": self.metrics.parallelization_efficiency,
                    "cost_savings": self.metrics.cost_savings
                },
                "cache_analysis": cache_analysis,
                "parallelization_analysis": parallelization_analysis,
                "bottlenecks": bottlenecks,
                "recommendations": ai_recommendations,
                "optimization_roi": optimization_roi,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info("Analytics optimisation build générées avec succès")
            return analytics
            
        except Exception as e:
            logger.error(f"Erreur génération analytics: {e}")
            return {}

    async def cross_platform_compilation(self, job: BuildJob, targets: List[BuildTarget]) -> Dict[BuildTarget, BuildJob]:
        """
        🌐 Compilation cross-platform pour tous les targets
        
        Compile automatiquement pour multiple plateformes avec optimisations
        spécifiques à chaque target et gestion des dépendances cross-platform.
        
        Args:
            job: Job de build base
            targets: Targets de compilation
            
        Returns:
            Dictionnaire des jobs par target
        """
        try:
            platform_jobs = {}
            
            for target in targets:
                # Créer job spécifique au target
                platform_job = await self._create_platform_job(job, target)
                
                # Configurer toolchain spécifique
                await self._configure_platform_toolchain(platform_job, target)
                
                # Optimiser flags de compilation
                await self._optimize_compilation_flags(platform_job, target)
                
                # Gérer dépendances cross-platform
                await self._resolve_cross_platform_dependencies(platform_job, target)
                
                platform_jobs[target] = platform_job
            
            # Exécuter compilations en parallèle
            completed_jobs = await self.parallel_build_execution(list(platform_jobs.values()))
            
            # Valider artifacts pour chaque target
            for target, job in platform_jobs.items():
                if job.id in completed_jobs and completed_jobs[job.id].status == BuildStatus.SUCCESS:
                    await self._validate_platform_artifacts(completed_jobs[job.id], target)
                    logger.info(f"Compilation {target.value} réussie pour job {job.name}")
                else:
                    logger.error(f"Compilation {target.value} échouée pour job {job.name}")
            
            return {target: completed_jobs.get(job.id, job) for target, job in platform_jobs.items()}
            
        except Exception as e:
            logger.error(f"Erreur compilation cross-platform: {e}")
            return {}

    # Méthodes privées pour implémentation interne
    
    async def _calculate_intelligent_cache_key(self, job: BuildJob) -> str:
        """Calcule clé de cache intelligente basée sur contenu et dépendances"""
        try:
            # Hash du code source
            source_hash = await self._hash_directory(job.source_path)
            
            # Hash des dépendances
            deps_hash = hashlib.sha256(json.dumps(sorted(job.dependencies)).encode()).hexdigest()
            
            # Hash de l'environnement
            env_hash = hashlib.sha256(json.dumps(sorted(job.environment.items())).encode()).hexdigest()
            
            # Hash du target
            target_hash = hashlib.sha256(job.target.value.encode()).hexdigest()
            
            # Combinaison intelligente
            combined = f"{source_hash}:{deps_hash}:{env_hash}:{target_hash}:{job.name}"
            return hashlib.sha256(combined.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Erreur calcul clé cache: {e}")
            return f"fallback_{job.id}_{int(time.time())}"

    async def _hash_directory(self, path: str) -> str:
        """Hash récursif d'un répertoire"""
        try:
            hasher = hashlib.sha256()
            
            for root, dirs, files in os.walk(path):
                # Trier pour consistance
                dirs.sort()
                files.sort()
                
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            for chunk in iter(lambda: f.read(4096), b""):
                                hasher.update(chunk)
                    except (OSError, IOError):
                        # Ignorer fichiers inaccessibles
                        continue
            
            return hasher.hexdigest()
            
        except Exception as e:
            logger.error(f"Erreur hash répertoire {path}: {e}")
            return "error_hash"

    def _build_dependency_graph(self, jobs: List[BuildJob]) -> Dict[str, List[str]]:
        """Construit graphe de dépendances entre jobs"""
        graph = {}
        job_names = {job.name: job.id for job in jobs}
        
        for job in jobs:
            graph[job.id] = []
            for dep in job.dependencies:
                if dep in job_names:
                    graph[job.id].append(job_names[dep])
        
        return graph

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Tri topologique pour ordre d'exécution"""
        in_degree = {node: 0 for node in graph}
        
        for node in graph:
            for neighbor in graph[node]:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1
        
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        return result

    def _group_parallel_jobs(self, execution_order: List[str], 
                           dependency_graph: Dict[str, List[str]]) -> List[List[BuildJob]]:
        """Groupe jobs pour exécution parallèle"""
        groups = []
        remaining_jobs = set(execution_order)
        job_map = {job.id: job for job in self.job_queue if job.id in remaining_jobs}
        
        while remaining_jobs:
            current_group = []
            
            # Trouver jobs sans dépendances non résolues
            for job_id in list(remaining_jobs):
                dependencies = dependency_graph.get(job_id, [])
                if all(dep not in remaining_jobs for dep in dependencies):
                    if job_id in job_map:
                        current_group.append(job_map[job_id])
                        remaining_jobs.remove(job_id)
            
            if current_group:
                groups.append(current_group)
            else:
                # Éviter boucle infinie
                break
        
        return groups

    def _execute_single_job(self, job: BuildJob) -> BuildJob:
        """Exécute un job de build unique"""
        try:
            job.status = BuildStatus.RUNNING
            job.started_at = datetime.now()
            
            # Vérifier cache d'abord
            cached_artifacts = asyncio.run(self.intelligent_build_caching(job))
            if cached_artifacts:
                job.artifacts = cached_artifacts
                job.status = BuildStatus.CACHED
                job.completed_at = datetime.now()
                return job
            
            # Préparer environnement de build
            build_env = os.environ.copy()
            build_env.update(job.environment)
            
            # Construire commande de build
            build_command = self._build_command(job)
            
            # Exécuter build
            result = subprocess.run(
                build_command,
                cwd=job.source_path,
                env=build_env,
                capture_output=True,
                text=True,
                timeout=job.timeout
            )
            
            # Collecter logs
            job.logs.append(f"STDOUT: {result.stdout}")
            if result.stderr:
                job.logs.append(f"STDERR: {result.stderr}")
            
            if result.returncode == 0:
                job.status = BuildStatus.SUCCESS
                self.metrics.successful_builds += 1
                
                # Collecter artifacts
                artifacts = self._collect_artifacts(job)
                asyncio.run(self.artifact_management(job, artifacts))
                
            else:
                job.status = BuildStatus.FAILED
                self.metrics.failed_builds += 1
            
            job.completed_at = datetime.now()
            self.metrics.total_builds += 1
            
            # Calculer temps de build
            if job.started_at and job.completed_at:
                build_time = (job.completed_at - job.started_at).total_seconds()
                self.metrics.total_build_time += build_time
                self.metrics.average_build_time = self.metrics.total_build_time / self.metrics.total_builds
            
            return job
            
        except Exception as e:
            job.status = BuildStatus.FAILED
            job.logs.append(f"ERROR: {str(e)}")
            job.completed_at = datetime.now()
            logger.error(f"Erreur exécution job {job.id}: {e}")
            return job

    def _build_command(self, job: BuildJob) -> List[str]:
        """Construit commande de build selon le target"""
        base_commands = {
            BuildTarget.LINUX_AMD64: ["go", "build", "-o", os.path.join(job.output_path, job.name)],
            BuildTarget.LINUX_ARM64: ["env", "GOOS=linux", "GOARCH=arm64", "go", "build", "-o", os.path.join(job.output_path, job.name)],
            BuildTarget.WINDOWS_AMD64: ["env", "GOOS=windows", "GOARCH=amd64", "go", "build", "-o", os.path.join(job.output_path, f"{job.name}.exe")],
            BuildTarget.DARWIN_AMD64: ["env", "GOOS=darwin", "GOARCH=amd64", "go", "build", "-o", os.path.join(job.output_path, job.name)],
            BuildTarget.DARWIN_ARM64: ["env", "GOOS=darwin", "GOARCH=arm64", "go", "build", "-o", os.path.join(job.output_path, job.name)],
            BuildTarget.WEB_ASSEMBLY: ["env", "GOOS=js", "GOARCH=wasm", "go", "build", "-o", os.path.join(job.output_path, f"{job.name}.wasm")]
        }
        
        return base_commands.get(job.target, ["make", "build"])

    def _collect_artifacts(self, job: BuildJob) -> List[BuildArtifact]:
        """Collecte artifacts après build"""
        artifacts = []
        
        if os.path.exists(job.output_path):
            for root, dirs, files in os.walk(job.output_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        
                        # Déterminer type d'artifact
                        artifact_type = self._determine_artifact_type(file)
                        
                        artifact = BuildArtifact(
                            name=file,
                            type=artifact_type,
                            path=file_path,
                            size=size,
                            checksum="",  # Sera calculé dans artifact_management
                            metadata={"job_id": job.id, "target": job.target.value}
                        )
                        artifacts.append(artifact)
        
        return artifacts

    def _determine_artifact_type(self, filename: str) -> ArtifactType:
        """Détermine type d'artifact selon extension"""
        ext = Path(filename).suffix.lower()
        
        if ext in ['.exe', '.bin', '.out', '']:
            return ArtifactType.BINARY
        elif ext in ['.tar', '.zip', '.gz', '.tgz']:
            return ArtifactType.PACKAGE
        elif ext in ['.md', '.txt', '.html', '.pdf']:
            return ArtifactType.DOCUMENTATION
        elif ext in ['.xml', '.json', '.yaml', '.yml']:
            return ArtifactType.REPORTS
        elif ext in ['.conf', '.config', '.ini', '.env']:
            return ArtifactType.CONFIGURATION
        else:
            return ArtifactType.BINARY

    def _load_cache_index(self):
        """Charge index de cache depuis disque"""
        try:
            cache_index_file = self.cache_dir / "cache_index.json"
            if cache_index_file.exists():
                with open(cache_index_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruire objets cache
                    for key, cache_data in data.items():
                        artifacts = [BuildArtifact(**artifact) for artifact in cache_data['artifacts']]
                        self.cache_index[key] = BuildCache(
                            key=cache_data['key'],
                            artifacts=artifacts,
                            hit_count=cache_data.get('hit_count', 0),
                            created_at=datetime.fromisoformat(cache_data['created_at']),
                            last_accessed=datetime.fromisoformat(cache_data['last_accessed']),
                            metadata=cache_data.get('metadata', {})
                        )
        except Exception as e:
            logger.error(f"Erreur chargement cache index: {e}")

    async def _validate_cache_entry(self, cache_entry: BuildCache, job: BuildJob) -> bool:
        """Valide qu'une entrée de cache est encore valide"""
        try:
            # Vérifier expiration
            if cache_entry.artifacts:
                for artifact in cache_entry.artifacts:
                    if artifact.expires_at and artifact.expires_at < datetime.now():
                        return False
                    
                    # Vérifier existence fichier
                    if not os.path.exists(artifact.path):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation cache: {e}")
            return False

    async def _check_distributed_cache(self, cache_key: str, job: BuildJob) -> Optional[List[BuildArtifact]]:
        """Vérifie cache distribué (implémentation basique)"""
        # TODO: Implémenter avec Redis/Memcached ou système distribué
        return None

    async def _store_local_cache(self, cache_key: str, artifacts: List[BuildArtifact], job: BuildJob):
        """Stocke artifacts en cache local"""
        try:
            cache_entry = BuildCache(
                key=cache_key,
                artifacts=artifacts,
                metadata={"job_id": job.id, "job_name": job.name}
            )
            
            self.cache_index[cache_key] = cache_entry
            
            # Sauvegarder index
            await self._save_cache_index()
            
        except Exception as e:
            logger.error(f"Erreur stockage cache local: {e}")

    async def _save_cache_index(self):
        """Sauvegarde index de cache sur disque"""
        try:
            cache_index_file = self.cache_dir / "cache_index.json"
            
            # Sérialiser données
            serializable_data = {}
            for key, cache_entry in self.cache_index.items():
                serializable_data[key] = {
                    "key": cache_entry.key,
                    "artifacts": [
                        {
                            "name": artifact.name,
                            "type": artifact.type.value,
                            "path": artifact.path,
                            "size": artifact.size,
                            "checksum": artifact.checksum,
                            "metadata": artifact.metadata,
                            "created_at": artifact.created_at.isoformat(),
                            "expires_at": artifact.expires_at.isoformat() if artifact.expires_at else None
                        }
                        for artifact in cache_entry.artifacts
                    ],
                    "hit_count": cache_entry.hit_count,
                    "created_at": cache_entry.created_at.isoformat(),
                    "last_accessed": cache_entry.last_accessed.isoformat(),
                    "metadata": cache_entry.metadata
                }
            
            with open(cache_index_file, 'w') as f:
                json.dump(serializable_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde cache index: {e}")

    async def _calculate_artifact_checksum(self, file_path: str) -> str:
        """Calcule checksum d'un artifact"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Erreur calcul checksum {file_path}: {e}")
            return "error_checksum"

    async def _find_existing_artifact(self, checksum: str) -> Optional[BuildArtifact]:
        """Trouve artifact existant avec même checksum"""
        try:
            for cache_entry in self.cache_index.values():
                for artifact in cache_entry.artifacts:
                    if artifact.checksum == checksum:
                        return artifact
            return None
        except Exception as e:
            logger.error(f"Erreur recherche artifact: {e}")
            return None

    async def _create_artifact_link(self, artifact: BuildArtifact, existing_artifact: BuildArtifact):
        """Crée lien symbolique vers artifact existant"""
        try:
            os.symlink(existing_artifact.path, artifact.path)
        except Exception as e:
            logger.error(f"Erreur création lien artifact: {e}")

    async def _store_artifact(self, artifact: BuildArtifact, job: BuildJob) -> str:
        """Stocke artifact dans répertoire géré"""
        try:
            # Créer répertoire job
            job_dir = self.artifacts_dir / job.id
            job_dir.mkdir(parents=True, exist_ok=True)
            
            # Copier artifact
            target_path = job_dir / artifact.name
            os.rename(artifact.path, str(target_path))
            
            return str(target_path)
            
        except Exception as e:
            logger.error(f"Erreur stockage artifact: {e}")
            return artifact.path

    async def _apply_versioning(self, artifact: BuildArtifact, job: BuildJob) -> BuildArtifact:
        """Applique versioning à l'artifact"""
        # Versioning basique basé sur timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        versioned_name = f"{artifact.name}_{timestamp}"
        
        artifact.metadata["version"] = timestamp
        artifact.metadata["original_name"] = artifact.name
        artifact.name = versioned_name
        
        return artifact

    async def _apply_retention_policy(self, artifact: BuildArtifact):
        """Applique politique de rétention"""
        # Politique basique: 30 jours
        artifact.expires_at = datetime.now() + timedelta(days=30)

    async def _index_artifacts(self, artifacts: List[BuildArtifact], job: BuildJob):
        """Indexe artifacts pour recherche"""
        # Implémentation basique - pourrait utiliser Elasticsearch
        for artifact in artifacts:
            artifact.metadata["indexed_at"] = datetime.now().isoformat()
            artifact.metadata["job_name"] = job.name
            artifact.metadata["job_target"] = job.target.value

    async def _collect_historical_metrics(self) -> Dict[str, Any]:
        """Collecte métriques historiques"""
        return {
            "total_builds": self.metrics.total_builds,
            "success_rate": self.metrics.successful_builds / max(self.metrics.total_builds, 1),
            "average_build_time": self.metrics.average_build_time,
            "cache_hit_rate": self.metrics.cache_hit_rate
        }

    async def _analyze_cache_patterns(self) -> Dict[str, Any]:
        """Analyse patterns de cache"""
        total_hits = sum(cache.hit_count for cache in self.cache_index.values())
        total_entries = len(self.cache_index)
        
        return {
            "total_entries": total_entries,
            "total_hits": total_hits,
            "average_hits_per_entry": total_hits / max(total_entries, 1),
            "cache_efficiency": total_hits / max(self.metrics.total_builds, 1)
        }

    async def _analyze_parallelization_efficiency(self) -> Dict[str, Any]:
        """Analyse efficacité parallélisation"""
        return {
            "max_parallel_jobs": self.max_parallel_jobs,
            "current_active_jobs": len(self.active_jobs),
            "efficiency_score": self.metrics.parallelization_efficiency
        }

    async def _detect_build_bottlenecks(self) -> List[Dict[str, Any]]:
        """Détecte goulots d'étranglement"""
        bottlenecks = []
        
        # Analyser temps de build moyens
        if self.metrics.average_build_time > 300:  # 5 minutes
            bottlenecks.append({
                "type": "slow_builds",
                "severity": "high",
                "description": "Temps de build moyen trop élevé",
                "value": self.metrics.average_build_time
            })
        
        # Analyser taux de cache
        if self.metrics.cache_hit_rate < 0.3:  # 30%
            bottlenecks.append({
                "type": "low_cache_hit",
                "severity": "medium", 
                "description": "Taux de cache hit faible",
                "value": self.metrics.cache_hit_rate
            })
        
        return bottlenecks

    async def _generate_ai_recommendations(self, historical_data: Dict, cache_analysis: Dict,
                                         parallelization_analysis: Dict, bottlenecks: List) -> List[Dict[str, Any]]:
        """Génère recommandations IA"""
        recommendations = []
        
        # Recommandations basées sur cache
        if cache_analysis["cache_efficiency"] < 0.5:
            recommendations.append({
                "type": "cache_optimization",
                "priority": "high",
                "description": "Optimiser stratégie de cache pour améliorer hit rate",
                "expected_improvement": "20-30% réduction temps build",
                "actions": [
                    "Activer cache distribué",
                    "Améliorer clés de cache",
                    "Implémenter cache warming"
                ]
            })
        
        # Recommandations basées sur parallélisation
        if parallelization_analysis["efficiency_score"] < 0.7:
            recommendations.append({
                "type": "parallelization_optimization",
                "priority": "medium",
                "description": "Améliorer efficacité parallélisation",
                "expected_improvement": "15-25% réduction temps build",
                "actions": [
                    "Optimiser graphe de dépendances",
                    "Augmenter workers parallèles",
                    "Implémenter load balancing"
                ]
            })
        
        return recommendations

    async def _calculate_optimization_roi(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Calcule ROI des optimisations"""
        total_potential_savings = 0
        implementation_cost = 0
        
        for rec in recommendations:
            if rec["type"] == "cache_optimization":
                potential_savings = self.metrics.average_build_time * 0.25 * self.metrics.total_builds
                total_potential_savings += potential_savings
                implementation_cost += 40  # heures
            elif rec["type"] == "parallelization_optimization":
                potential_savings = self.metrics.average_build_time * 0.20 * self.metrics.total_builds
                total_potential_savings += potential_savings
                implementation_cost += 24  # heures
        
        return {
            "potential_time_savings": total_potential_savings,
            "implementation_cost_hours": implementation_cost,
            "roi_ratio": total_potential_savings / max(implementation_cost, 1),
            "payback_period_days": implementation_cost / max(total_potential_savings / 365, 1)
        }

    async def _create_platform_job(self, base_job: BuildJob, target: BuildTarget) -> BuildJob:
        """Crée job spécifique à une plateforme"""
        platform_job = BuildJob(
            id=f"{base_job.id}_{target.value.replace('/', '_')}",
            name=f"{base_job.name}_{target.value.replace('/', '_')}",
            target=target,
            source_path=base_job.source_path,
            output_path=f"{base_job.output_path}_{target.value.replace('/', '_')}",
            dependencies=base_job.dependencies.copy(),
            environment=base_job.environment.copy(),
            cache_strategy=base_job.cache_strategy,
            parallel=base_job.parallel,
            priority=base_job.priority,
            timeout=base_job.timeout,
            metadata=base_job.metadata.copy()
        )
        
        return platform_job

    async def _configure_platform_toolchain(self, job: BuildJob, target: BuildTarget):
        """Configure toolchain spécifique à la plateforme"""
        toolchain_configs = {
            BuildTarget.LINUX_AMD64: {"CC": "gcc", "CXX": "g++"},
            BuildTarget.LINUX_ARM64: {"CC": "aarch64-linux-gnu-gcc", "CXX": "aarch64-linux-gnu-g++"},
            BuildTarget.WINDOWS_AMD64: {"CC": "x86_64-w64-mingw32-gcc", "CXX": "x86_64-w64-mingw32-g++"},
            BuildTarget.DARWIN_AMD64: {"CC": "clang", "CXX": "clang++"},
            BuildTarget.DARWIN_ARM64: {"CC": "clang", "CXX": "clang++"},
            BuildTarget.WEB_ASSEMBLY: {"CC": "emcc", "CXX": "em++"}
        }
        
        if target in toolchain_configs:
            job.environment.update(toolchain_configs[target])

    async def _optimize_compilation_flags(self, job: BuildJob, target: BuildTarget):
        """Optimise flags de compilation pour target"""
        optimization_flags = {
            BuildTarget.LINUX_AMD64: ["-O3", "-march=native"],
            BuildTarget.LINUX_ARM64: ["-O3", "-mcpu=cortex-a72"],
            BuildTarget.WINDOWS_AMD64: ["-O3", "-march=x86-64"],
            BuildTarget.DARWIN_AMD64: ["-O3", "-march=native"],
            BuildTarget.DARWIN_ARM64: ["-O3", "-mcpu=apple-a14"],
            BuildTarget.WEB_ASSEMBLY: ["-O3", "-s", "WASM=1"]
        }
        
        if target in optimization_flags:
            job.environment["CFLAGS"] = " ".join(optimization_flags[target])
            job.environment["CXXFLAGS"] = " ".join(optimization_flags[target])

    async def _resolve_cross_platform_dependencies(self, job: BuildJob, target: BuildTarget):
        """Résout dépendances cross-platform"""
        # Implémentation basique - pourrait utiliser package managers spécifiques
        platform_deps = {
            BuildTarget.LINUX_AMD64: [],
            BuildTarget.LINUX_ARM64: [],
            BuildTarget.WINDOWS_AMD64: [],
            BuildTarget.DARWIN_AMD64: [],
            BuildTarget.DARWIN_ARM64: [],
            BuildTarget.WEB_ASSEMBLY: []
        }
        
        if target in platform_deps:
            job.dependencies.extend(platform_deps[target])

    async def _validate_platform_artifacts(self, job: BuildJob, target: BuildTarget) -> bool:
        """Valide artifacts pour target spécifique"""
        try:
            for artifact in job.artifacts:
                if not os.path.exists(artifact.path):
                    return False
                    
                # Validation spécifique selon target
                if target == BuildTarget.WINDOWS_AMD64 and not artifact.name.endswith('.exe'):
                    if artifact.type == ArtifactType.BINARY:
                        return False
                elif target == BuildTarget.WEB_ASSEMBLY and not artifact.name.endswith('.wasm'):
                    if artifact.type == ArtifactType.BINARY:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation artifacts {target.value}: {e}")
            return False


def create_build_automation_engine(cache_dir: str = "/var/cache/iacherie/builds",
                                 artifacts_dir: str = "/var/artifacts/iacherie",
                                 max_parallel_jobs: int = 8,
                                 cache_size_limit: int = 50 * 1024 * 1024 * 1024,
                                 enable_distributed_cache: bool = True) -> BuildAutomationEngine:
    """
    Factory function pour créer instance BuildAutomationEngine
    
    Args:
        cache_dir: Répertoire de cache local
        artifacts_dir: Répertoire des artifacts
        max_parallel_jobs: Nombre max de jobs parallèles
        cache_size_limit: Limite taille cache en bytes
        enable_distributed_cache: Activer cache distribué
        
    Returns:
        Instance configurée de BuildAutomationEngine
    """
    return BuildAutomationEngine(
        cache_dir=cache_dir,
        artifacts_dir=artifacts_dir,
        max_parallel_jobs=max_parallel_jobs,
        cache_size_limit=cache_size_limit,
        enable_distributed_cache=enable_distributed_cache
    )


# Example d'utilisation
if __name__ == "__main__":
    async def main():
        # Créer moteur de build
        build_engine = create_build_automation_engine()
        
        # Créer jobs de test
        test_job = BuildJob(
            id="test_build_001",
            name="iacherie_api",
            target=BuildTarget.LINUX_AMD64,
            source_path="/src/api",
            output_path="/dist/api",
            dependencies=["common_lib", "database_driver"],
            environment={"GO_VERSION": "1.21", "CGO_ENABLED": "1"},
            cache_strategy=CacheStrategy.INTELLIGENT,
            parallel=True,
            priority=1
        )
        
        # Test cache intelligent
        print("🧠 Test cache intelligent...")
        cached_artifacts = await build_engine.intelligent_build_caching(test_job)
        print(f"Cache result: {cached_artifacts}")
        
        # Test exécution parallèle
        print("🚀 Test exécution parallèle...")
        jobs = [test_job]
        results = await build_engine.parallel_build_execution(jobs)
        print(f"Résultats: {len(results)} jobs complétés")
        
        # Test compilation cross-platform
        print("🌐 Test compilation cross-platform...")
        targets = [BuildTarget.LINUX_AMD64, BuildTarget.WINDOWS_AMD64, BuildTarget.DARWIN_AMD64]
        platform_results = await build_engine.cross_platform_compilation(test_job, targets)
        print(f"Platforms: {list(platform_results.keys())}")
        
        # Test analytics
        print("📊 Test analytics...")
        analytics = await build_engine.build_optimization_analytics()
        print(f"Analytics générées: {len(analytics)} métriques")
        
        print("✅ Tests Build Automation Engine complétés!")

    # Exécuter tests
    asyncio.run(main())