"""
Enterprise Dependency Resolver for MLOps
DevOps + Lead Dev IA implementation with intelligent dependency management for ML environments
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import subprocess
import yaml
import hashlib
from pathlib import Path
import re
import semver
from collections import defaultdict, deque
import warnings

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of dependencies"""
    PYTHON_PACKAGE = "python_package"
    SYSTEM_PACKAGE = "system_package"
    ML_MODEL = "ml_model"
    DATA_SOURCE = "data_source"
    DOCKER_IMAGE = "docker_image"
    KUBERNETES_RESOURCE = "kubernetes_resource"
    CLOUD_SERVICE = "cloud_service"


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving dependency conflicts"""
    LATEST_VERSION = "latest_version"
    MOST_STABLE = "most_stable"
    MOST_COMPATIBLE = "most_compatible"
    USER_DEFINED = "user_defined"
    CONSERVATIVE = "conservative"


class EnvironmentType(Enum):
    """Types of ML environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    TRAINING = "training"
    INFERENCE = "inference"


@dataclass
class DependencySpec:
    """Specification for a dependency"""
    name: str
    version: Optional[str] = None
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    extras: List[str] = field(default_factory=list)
    source: Optional[str] = None
    optional: bool = False
    environment_specific: Dict[str, str] = field(default_factory=dict)
    conflicts_with: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)


@dataclass
class ResolvedDependency:
    """A resolved dependency with specific version"""
    name: str
    version: str
    source: str
    checksum: Optional[str] = None
    extras: List[str] = field(default_factory=list)
    dependencies: List['ResolvedDependency'] = field(default_factory=list)
    resolution_reason: str = ""


@dataclass
class DependencyGraph:
    """Dependency graph representation"""
    nodes: Dict[str, DependencySpec] = field(default_factory=dict)
    edges: Dict[str, Set[str]] = field(default_factory=dict)
    conflicts: List[Tuple[str, str, str]] = field(default_factory=list)


class DependencyResolver:
    """
    Enterprise-grade dependency resolver for ML environments
    Provides intelligent conflict resolution and environment consistency
    """

    def __init__(self):
        self.resolution_cache: Dict[str, List[ResolvedDependency]] = {}
        self.version_cache: Dict[str, List[str]] = {}
        self.conflict_history: List[Dict[str, Any]] = []
        self.resolution_strategies: Dict[str, ConflictResolutionStrategy] = {}
        
    async def resolve_dependencies(
        self,
        requirements: List[DependencySpec],
        environment: EnvironmentType = EnvironmentType.PRODUCTION,
        strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MOST_STABLE,
        allow_prereleases: bool = False
    ) -> List[ResolvedDependency]:
        """
        Resolve dependencies with intelligent conflict resolution
        
        Args:
            requirements: List of dependency specifications
            environment: Target environment type
            strategy: Conflict resolution strategy
            allow_prereleases: Whether to allow pre-release versions
            
        Returns:
            List of resolved dependencies
        """
        try:
            logger.info(f"Starting dependency resolution for {len(requirements)} requirements")
            
            # Build dependency graph
            graph = await self._build_dependency_graph(requirements)
            
            # Detect conflicts
            conflicts = await self._detect_conflicts(graph)
            
            if conflicts:
                logger.warning(f"Found {len(conflicts)} conflicts, attempting resolution")
                graph = await self._resolve_conflicts(graph, conflicts, strategy)
            
            # Perform topological sort
            resolved_order = await self._topological_sort(graph)
            
            # Resolve specific versions
            resolved_deps = await self._resolve_versions(
                resolved_order, environment, strategy, allow_prereleases
            )
            
            # Validate consistency
            await self._validate_resolution(resolved_deps)
            
            # Cache result
            cache_key = self._generate_cache_key(requirements, environment, strategy)
            self.resolution_cache[cache_key] = resolved_deps
            
            logger.info(f"Successfully resolved {len(resolved_deps)} dependencies")
            return resolved_deps
            
        except Exception as e:
            logger.error(f"Dependency resolution failed: {e}")
            raise

    async def _build_dependency_graph(
        self, 
        requirements: List[DependencySpec]
    ) -> DependencyGraph:
        """Build a dependency graph from requirements"""
        graph = DependencyGraph()
        
        # Add root requirements
        for req in requirements:
            graph.nodes[req.name] = req
            graph.edges[req.name] = set()
        
        # Recursively fetch dependencies
        processed = set()
        queue = deque(requirements)
        
        while queue:
            current = queue.popleft()
            if current.name in processed:
                continue
                
            processed.add(current.name)
            
            # Fetch dependencies for current package
            sub_deps = await self._fetch_package_dependencies(current)
            
            for dep_spec in sub_deps:
                if dep_spec.name not in graph.nodes:
                    graph.nodes[dep_spec.name] = dep_spec
                    graph.edges[dep_spec.name] = set()
                    queue.append(dep_spec)
                
                graph.edges[current.name].add(dep_spec.name)
        
        return graph

    async def _fetch_package_dependencies(
        self, 
        package: DependencySpec
    ) -> List[DependencySpec]:
        """Fetch dependencies for a package"""
        try:
            # Check cache first
            if package.name in self.version_cache:
                # Return cached dependencies (simplified)
                return []
            
            # Fetch from package index (PyPI, etc.)
            if package.source == "pypi" or not package.source:
                return await self._fetch_pypi_dependencies(package)
            elif package.source == "conda":
                return await self._fetch_conda_dependencies(package)
            else:
                return []
                
        except Exception as e:
            logger.warning(f"Failed to fetch dependencies for {package.name}: {e}")
            return []

    async def _fetch_pypi_dependencies(
        self, 
        package: DependencySpec
    ) -> List[DependencySpec]:
        """Fetch dependencies from PyPI"""
        try:
            # Simulate PyPI API call
            import urllib.request
            import json
            
            url = f"https://pypi.org/pypi/{package.name}/json"
            
            # In production, this would be an actual API call
            # For now, return some common ML dependencies based on package name
            common_ml_deps = {
                "tensorflow": ["numpy", "six", "protobuf"],
                "torch": ["numpy", "typing-extensions"],
                "sklearn": ["numpy", "scipy", "joblib"],
                "pandas": ["numpy", "python-dateutil", "pytz"],
                "matplotlib": ["numpy", "pyparsing", "python-dateutil"]
            }
            
            deps = []
            if package.name in common_ml_deps:
                for dep_name in common_ml_deps[package.name]:
                    deps.append(DependencySpec(name=dep_name))
            
            return deps
            
        except Exception as e:
            logger.warning(f"Failed to fetch PyPI dependencies for {package.name}: {e}")
            return []

    async def _fetch_conda_dependencies(
        self, 
        package: DependencySpec
    ) -> List[DependencySpec]:
        """Fetch dependencies from Conda"""
        # Similar to PyPI but for Conda packages
        return []

    async def _detect_conflicts(
        self, 
        graph: DependencyGraph
    ) -> List[Tuple[str, str, str]]:
        """Detect version conflicts in dependency graph"""
        conflicts = []
        
        # Group packages by name
        package_versions = defaultdict(list)
        
        for name, spec in graph.nodes.items():
            if spec.version:
                package_versions[name].append((name, spec.version, "direct"))
        
        # Check for version conflicts
        for package_name, versions in package_versions.items():
            if len(versions) > 1:
                unique_versions = set(v[1] for v in versions)
                if len(unique_versions) > 1:
                    conflicts.append((
                        package_name, 
                        str(unique_versions), 
                        "version_conflict"
                    ))
        
        # Check explicit conflicts
        for name, spec in graph.nodes.items():
            for conflict in spec.conflicts_with:
                if conflict in graph.nodes:
                    conflicts.append((name, conflict, "explicit_conflict"))
        
        return conflicts

    async def _resolve_conflicts(
        self,
        graph: DependencyGraph,
        conflicts: List[Tuple[str, str, str]],
        strategy: ConflictResolutionStrategy
    ) -> DependencyGraph:
        """Resolve conflicts in dependency graph"""
        resolved_graph = graph
        
        for conflict in conflicts:
            package_name, conflict_info, conflict_type = conflict
            
            if conflict_type == "version_conflict":
                resolved_version = await self._resolve_version_conflict(
                    package_name, conflict_info, strategy
                )
                # Update graph with resolved version
                if package_name in resolved_graph.nodes:
                    resolved_graph.nodes[package_name].version = resolved_version
            
            elif conflict_type == "explicit_conflict":
                # Try to find alternatives
                alternatives = await self._find_alternatives(package_name, conflict_info)
                if alternatives:
                    # Replace with alternative
                    alt_name = alternatives[0]
                    resolved_graph.nodes[alt_name] = resolved_graph.nodes[package_name]
                    del resolved_graph.nodes[package_name]
        
        return resolved_graph

    async def _resolve_version_conflict(
        self,
        package_name: str,
        conflict_info: str,
        strategy: ConflictResolutionStrategy
    ) -> str:
        """Resolve version conflict for a specific package"""
        try:
            # Parse available versions
            available_versions = await self._get_available_versions(package_name)
            
            if strategy == ConflictResolutionStrategy.LATEST_VERSION:
                return max(available_versions, key=lambda v: self._parse_version(v))
            
            elif strategy == ConflictResolutionStrategy.MOST_STABLE:
                # Filter out pre-releases and return latest stable
                stable_versions = [v for v in available_versions if not self._is_prerelease(v)]
                if stable_versions:
                    return max(stable_versions, key=lambda v: self._parse_version(v))
                return max(available_versions, key=lambda v: self._parse_version(v))
            
            elif strategy == ConflictResolutionStrategy.CONSERVATIVE:
                # Return oldest compatible version
                return min(available_versions, key=lambda v: self._parse_version(v))
            
            else:
                return max(available_versions, key=lambda v: self._parse_version(v))
                
        except Exception as e:
            logger.warning(f"Failed to resolve version conflict for {package_name}: {e}")
            return "latest"

    async def _get_available_versions(self, package_name: str) -> List[str]:
        """Get available versions for a package"""
        # Check cache first
        if package_name in self.version_cache:
            return self.version_cache[package_name]
        
        # Simulate fetching versions
        mock_versions = ["1.0.0", "1.1.0", "1.2.0", "2.0.0", "2.1.0"]
        self.version_cache[package_name] = mock_versions
        return mock_versions

    def _parse_version(self, version: str) -> Tuple[int, ...]:
        """Parse version string into comparable tuple"""
        try:
            return tuple(map(int, version.split('.')))
        except:
            return (0,)

    def _is_prerelease(self, version: str) -> bool:
        """Check if version is a pre-release"""
        prerelease_indicators = ['alpha', 'beta', 'rc', 'dev', 'pre']
        return any(indicator in version.lower() for indicator in prerelease_indicators)

    async def _find_alternatives(
        self, 
        package_name: str, 
        conflicting_package: str
    ) -> List[str]:
        """Find alternative packages that don't conflict"""
        # Package alternatives database
        alternatives_db = {
            "tensorflow": ["pytorch", "jax"],
            "pytorch": ["tensorflow", "jax"],
            "pandas": ["polars", "dask"],
            "numpy": ["cupy", "jax.numpy"]
        }
        
        return alternatives_db.get(package_name, [])

    async def _topological_sort(self, graph: DependencyGraph) -> List[str]:
        """Perform topological sort on dependency graph"""
        # Kahn's algorithm
        in_degree = defaultdict(int)
        
        # Calculate in-degrees
        for node in graph.nodes:
            in_degree[node] = 0
        
        for node, edges in graph.edges.items():
            for edge in edges:
                in_degree[edge] += 1
        
        # Find nodes with no incoming edges
        queue = deque([node for node in graph.nodes if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # Remove edges and update in-degrees
            for neighbor in graph.edges[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(result) != len(graph.nodes):
            raise ValueError("Circular dependency detected")
        
        return result

    async def _resolve_versions(
        self,
        packages: List[str],
        environment: EnvironmentType,
        strategy: ConflictResolutionStrategy,
        allow_prereleases: bool
    ) -> List[ResolvedDependency]:
        """Resolve specific versions for packages"""
        resolved = []
        
        for package_name in packages:
            try:
                # Get package spec
                spec = None
                for _, pkg_spec in [(name, spec) for name, spec in {}]:  # Would use actual graph
                    if pkg_spec.name == package_name:
                        spec = pkg_spec
                        break
                
                if not spec:
                    # Create minimal spec
                    spec = DependencySpec(name=package_name)
                
                # Resolve version
                if spec.version:
                    resolved_version = spec.version
                else:
                    available_versions = await self._get_available_versions(package_name)
                    
                    if not allow_prereleases:
                        available_versions = [v for v in available_versions if not self._is_prerelease(v)]
                    
                    if available_versions:
                        resolved_version = max(available_versions, key=lambda v: self._parse_version(v))
                    else:
                        resolved_version = "latest"
                
                # Create resolved dependency
                resolved_dep = ResolvedDependency(
                    name=package_name,
                    version=resolved_version,
                    source=spec.source or "pypi",
                    extras=spec.extras,
                    resolution_reason=f"Resolved using {strategy.value} strategy"
                )
                
                resolved.append(resolved_dep)
                
            except Exception as e:
                logger.warning(f"Failed to resolve version for {package_name}: {e}")
        
        return resolved

    async def _validate_resolution(self, resolved_deps: List[ResolvedDependency]):
        """Validate that the resolution is consistent"""
        # Check for duplicate packages
        package_names = [dep.name for dep in resolved_deps]
        if len(package_names) != len(set(package_names)):
            raise ValueError("Duplicate packages in resolution")
        
        # Check version compatibility (simplified)
        for dep in resolved_deps:
            if not self._is_valid_version(dep.version):
                raise ValueError(f"Invalid version {dep.version} for {dep.name}")

    def _is_valid_version(self, version: str) -> bool:
        """Check if version string is valid"""
        try:
            self._parse_version(version)
            return True
        except:
            return version in ["latest", "master", "main"]

    def _generate_cache_key(
        self,
        requirements: List[DependencySpec],
        environment: EnvironmentType,
        strategy: ConflictResolutionStrategy
    ) -> str:
        """Generate cache key for resolution result"""
        req_str = "|".join(sorted([f"{req.name}:{req.version}" for req in requirements]))
        key_str = f"{req_str}:{environment.value}:{strategy.value}"
        return hashlib.md5(key_str.encode()).hexdigest()

    async def generate_requirements_file(
        self,
        resolved_deps: List[ResolvedDependency],
        format_type: str = "pip",
        output_path: Optional[Path] = None
    ) -> str:
        """Generate requirements file from resolved dependencies"""
        try:
            if format_type == "pip":
                content = self._generate_pip_requirements(resolved_deps)
            elif format_type == "conda":
                content = self._generate_conda_requirements(resolved_deps)
            elif format_type == "poetry":
                content = self._generate_poetry_requirements(resolved_deps)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            if output_path:
                output_path.write_text(content)
                logger.info(f"Requirements file written to {output_path}")
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate requirements file: {e}")
            raise

    def _generate_pip_requirements(self, resolved_deps: List[ResolvedDependency]) -> str:
        """Generate pip requirements.txt format"""
        lines = []
        for dep in resolved_deps:
            line = f"{dep.name}=={dep.version}"
            if dep.extras:
                extras_str = ",".join(dep.extras)
                line = f"{dep.name}[{extras_str}]=={dep.version}"
            lines.append(line)
        
        return "\n".join(sorted(lines))

    def _generate_conda_requirements(self, resolved_deps: List[ResolvedDependency]) -> str:
        """Generate conda environment.yml format"""
        deps_list = []
        for dep in resolved_deps:
            deps_list.append(f"  - {dep.name}=={dep.version}")
        
        content = f"""name: ml-environment
channels:
  - conda-forge
  - defaults
dependencies:
{chr(10).join(deps_list)}
"""
        return content

    def _generate_poetry_requirements(self, resolved_deps: List[ResolvedDependency]) -> str:
        """Generate Poetry pyproject.toml dependencies section"""
        deps_dict = {}
        for dep in resolved_deps:
            deps_dict[dep.name] = dep.version
        
        # This would integrate with existing pyproject.toml
        deps_str = "\n".join([f'{name} = "{version}"' for name, version in sorted(deps_dict.items())])
        
        return f"""[tool.poetry.dependencies]
python = "^3.8"
{deps_str}
"""

    async def validate_environment_consistency(
        self,
        resolved_deps: List[ResolvedDependency],
        environment_path: Path
    ) -> Dict[str, Any]:
        """Validate that environment matches resolved dependencies"""
        try:
            validation_result = {
                "consistent": True,
                "missing_packages": [],
                "version_mismatches": [],
                "extra_packages": []
            }
            
            # Check installed packages (simplified)
            installed_packages = await self._get_installed_packages(environment_path)
            
            # Check for missing packages
            for dep in resolved_deps:
                if dep.name not in installed_packages:
                    validation_result["missing_packages"].append(dep.name)
                    validation_result["consistent"] = False
                elif installed_packages[dep.name] != dep.version:
                    validation_result["version_mismatches"].append({
                        "package": dep.name,
                        "expected": dep.version,
                        "actual": installed_packages[dep.name]
                    })
                    validation_result["consistent"] = False
            
            # Check for extra packages
            resolved_names = {dep.name for dep in resolved_deps}
            for pkg_name in installed_packages:
                if pkg_name not in resolved_names:
                    validation_result["extra_packages"].append(pkg_name)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Environment validation failed: {e}")
            raise

    async def _get_installed_packages(self, environment_path: Path) -> Dict[str, str]:
        """Get installed packages in environment"""
        # This would use pip list or conda list
        # Returning mock data for now
        return {
            "numpy": "1.21.0",
            "pandas": "1.3.0",
            "torch": "1.9.0"
        }


class DependencyManager:
    """
    High-level dependency management for MLOps environments
    """
    
    def __init__(self):
        self.resolver = DependencyResolver()
        self.environments: Dict[str, Dict[str, Any]] = {}
        
    async def create_environment(
        self,
        name: str,
        requirements: List[DependencySpec],
        environment_type: EnvironmentType = EnvironmentType.DEVELOPMENT,
        python_version: str = "3.9"
    ) -> Dict[str, Any]:
        """Create a new ML environment with resolved dependencies"""
        try:
            logger.info(f"Creating environment '{name}' with {len(requirements)} requirements")
            
            # Resolve dependencies
            resolved_deps = await self.resolver.resolve_dependencies(
                requirements=requirements,
                environment=environment_type
            )
            
            # Create environment configuration
            env_config = {
                "name": name,
                "type": environment_type.value,
                "python_version": python_version,
                "dependencies": resolved_deps,
                "created_at": datetime.utcnow().isoformat(),
                "status": "created"
            }
            
            self.environments[name] = env_config
            
            logger.info(f"Environment '{name}' created successfully with {len(resolved_deps)} resolved dependencies")
            return env_config
            
        except Exception as e:
            logger.error(f"Failed to create environment '{name}': {e}")
            raise

    async def update_environment(
        self,
        name: str,
        new_requirements: List[DependencySpec]
    ) -> Dict[str, Any]:
        """Update an existing environment with new requirements"""
        try:
            if name not in self.environments:
                raise ValueError(f"Environment '{name}' not found")
            
            env_config = self.environments[name]
            environment_type = EnvironmentType(env_config["type"])
            
            # Resolve new dependencies
            resolved_deps = await self.resolver.resolve_dependencies(
                requirements=new_requirements,
                environment=environment_type
            )
            
            # Update environment
            env_config["dependencies"] = resolved_deps
            env_config["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Environment '{name}' updated with {len(resolved_deps)} dependencies")
            return env_config
            
        except Exception as e:
            logger.error(f"Failed to update environment '{name}': {e}")
            raise

    async def export_environment(
        self,
        name: str,
        format_type: str = "pip",
        output_path: Optional[Path] = None
    ) -> str:
        """Export environment to requirements file"""
        try:
            if name not in self.environments:
                raise ValueError(f"Environment '{name}' not found")
            
            env_config = self.environments[name]
            resolved_deps = env_config["dependencies"]
            
            return await self.resolver.generate_requirements_file(
                resolved_deps=resolved_deps,
                format_type=format_type,
                output_path=output_path
            )
            
        except Exception as e:
            logger.error(f"Failed to export environment '{name}': {e}")
            raise


# Factory function for easy instantiation
def create_dependency_resolver() -> DependencyResolver:
    """Create a new dependency resolver instance"""
    return DependencyResolver()


def create_dependency_manager() -> DependencyManager:
    """Create a new dependency manager instance"""
    return DependencyManager()


# Example usage
if __name__ == "__main__":
    async def main():
        # Create dependency manager
        manager = create_dependency_manager()
        
        # Define requirements
        requirements = [
            DependencySpec(name="numpy", version=">=1.20.0"),
            DependencySpec(name="pandas", version=">=1.3.0"),
            DependencySpec(name="torch", version=">=1.9.0", extras=["audio"]),
            DependencySpec(name="transformers", version=">=4.20.0")
        ]
        
        # Create environment
        env_config = await manager.create_environment(
            name="ml-training",
            requirements=requirements,
            environment_type=EnvironmentType.TRAINING
        )
        
        print(f"Created environment: {env_config['name']}")
        print(f"Dependencies resolved: {len(env_config['dependencies'])}")
        
        # Export to requirements file
        requirements_content = await manager.export_environment(
            name="ml-training",
            format_type="pip"
        )
        
        print("\nGenerated requirements.txt:")
        print(requirements_content)
    
    asyncio.run(main())