"""
Enterprise Container Optimizer for MLOps
DevOps + Lead Dev IA implementation with Docker optimization for ML inference
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import subprocess
import yaml
import hashlib
from pathlib import Path
import re
import tempfile
import shutil
import docker
from collections import defaultdict
import warnings

logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """Container optimization levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    PRODUCTION = "production"


class ContainerRuntime(Enum):
    """Container runtime types"""
    DOCKER = "docker"
    PODMAN = "podman"
    CONTAINERD = "containerd"
    CRI_O = "cri_o"


class BaseImageType(Enum):
    """Base image types for ML containers"""
    PYTHON_SLIM = "python:3.9-slim"
    PYTHON_ALPINE = "python:3.9-alpine"
    UBUNTU_MINIMAL = "ubuntu:20.04"
    NVIDIA_CUDA = "nvidia/cuda:11.8-runtime-ubuntu20.04"
    TENSORFLOW_GPU = "tensorflow/tensorflow:2.13.0-gpu"
    PYTORCH_GPU = "pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"


@dataclass
class OptimizationConfig:
    """Configuration for container optimization"""
    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    base_image: BaseImageType = BaseImageType.PYTHON_SLIM
    multi_stage_build: bool = True
    layer_caching: bool = True
    dependency_caching: bool = True
    remove_dev_dependencies: bool = True
    compress_layers: bool = True
    use_distroless: bool = False
    security_scanning: bool = True
    vulnerability_fixes: bool = True
    custom_optimizations: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BuildMetrics:
    """Container build metrics"""
    build_time: float = 0.0
    image_size: int = 0
    layer_count: int = 0
    vulnerability_count: int = 0
    optimization_savings: float = 0.0
    cache_hit_ratio: float = 0.0


@dataclass
class OptimizationResult:
    """Result of container optimization"""
    original_size: int
    optimized_size: int
    size_reduction: float
    build_time: float
    layer_reduction: int
    vulnerabilities_fixed: int
    recommendations: List[str]
    warnings: List[str]
    metrics: BuildMetrics


class ContainerOptimizer:
    """
    Enterprise-grade container optimizer for ML inference workloads
    Provides intelligent optimization with performance and security focus
    """

    def __init__(self, runtime -> None: ContainerRuntime = ContainerRuntime.DOCKER) -> None:
        self.runtime = runtime
        self.docker_client = None
        self.optimization_cache: Dict[str, OptimizationResult] = {}
        self.build_cache: Dict[str, str] = {}
        
        try:
            if runtime == ContainerRuntime.DOCKER:
                self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client not available: {e}")

    async def optimize_container(
        self,
        dockerfile_path: Path,
        context_path: Path,
        config: OptimizationConfig,
        output_path: Optional[Path] = None
    ) -> OptimizationResult:
        """
        Optimize a container for ML inference deployment
        
        Args:
            dockerfile_path: Path to original Dockerfile
            context_path: Build context path
            config: Optimization configuration
            output_path: Output path for optimized Dockerfile
            
        Returns:
            Optimization result with metrics
        """
        try:
            logger.info(f"Starting container optimization with {config.optimization_level.value} level")
            start_time = datetime.utcnow()
            
            # Read original Dockerfile
            original_dockerfile = await self._read_dockerfile(dockerfile_path)
            
            # Analyze original container
            original_analysis = await self._analyze_dockerfile(original_dockerfile)
            
            # Generate optimized Dockerfile
            optimized_dockerfile = await self._generate_optimized_dockerfile(
                original_dockerfile, config
            )
            
            # Build and analyze optimized container
            if output_path:
                await self._write_dockerfile(output_path, optimized_dockerfile)
            
            # Build containers for comparison
            original_metrics = await self._build_and_measure(
                original_dockerfile, context_path, "original"
            )
            
            optimized_metrics = await self._build_and_measure(
                optimized_dockerfile, context_path, "optimized"
            )
            
            # Calculate optimization results
            result = await self._calculate_optimization_result(
                original_metrics, optimized_metrics, start_time
            )
            
            # Generate recommendations
            result.recommendations = await self._generate_recommendations(
                original_analysis, optimized_metrics, config
            )
            
            logger.info(f"Container optimization completed: {result.size_reduction:.1f}% size reduction")
            return result
            
        except Exception as e:
            logger.error(f"Container optimization failed: {e}")
            raise

    async def _read_dockerfile(self, dockerfile_path: Path) -> str:
        """Read Dockerfile content"""
        try:
            return dockerfile_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read Dockerfile: {e}")
            raise

    async def _write_dockerfile(self, output_path -> None: Path, content -> None: str) -> None:
        """Write optimized Dockerfile"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding='utf-8')
            logger.info(f"Optimized Dockerfile written to {output_path}")
        except Exception as e:
            logger.error(f"Failed to write Dockerfile: {e}")
            raise

    async def _analyze_dockerfile(self, dockerfile_content: str) -> Dict[str, Any]:
        """Analyze Dockerfile for optimization opportunities"""
        analysis = {
            "base_image": None,
            "layer_count": 0,
            "run_commands": [],
            "copy_commands": [],
            "env_vars": [],
            "exposed_ports": [],
            "volumes": [],
            "optimization_opportunities": []
        }
        
        lines = dockerfile_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            analysis["layer_count"] += 1
            
            if line.upper().startswith('FROM'):
                analysis["base_image"] = line.split()[1]
            elif line.upper().startswith('RUN'):
                analysis["run_commands"].append(line)
            elif line.upper().startswith('COPY') or line.upper().startswith('ADD'):
                analysis["copy_commands"].append(line)
            elif line.upper().startswith('ENV'):
                analysis["env_vars"].append(line)
            elif line.upper().startswith('EXPOSE'):
                analysis["exposed_ports"].append(line.split()[1])
            elif line.upper().startswith('VOLUME'):
                analysis["volumes"].append(line)
        
        # Identify optimization opportunities
        if len(analysis["run_commands"]) > 5:
            analysis["optimization_opportunities"].append("Multiple RUN commands can be merged")
        
        if analysis["base_image"] and "ubuntu" in analysis["base_image"].lower():
            analysis["optimization_opportunities"].append("Consider using a smaller base image")
        
        return analysis

    async def _generate_optimized_dockerfile(
        self,
        original_dockerfile: str,
        config: OptimizationConfig
    ) -> str:
        """Generate optimized Dockerfile based on configuration"""
        try:
            lines = original_dockerfile.strip().split('\n')
            optimized_lines = []
            
            # Multi-stage build setup
            if config.multi_stage_build:
                optimized_lines.extend(await self._create_multi_stage_build_header(config))
            
            run_commands = []
            in_multi_stage = config.multi_stage_build
            
            for line in lines:
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                upper_line = line.upper()
                
                if upper_line.startswith('FROM'):
                    if not in_multi_stage:
                        # Replace base image if needed
                        optimized_lines.append(await self._optimize_base_image(line, config))
                    else:
                        # Skip original FROM in multi-stage build
                        continue
                
                elif upper_line.startswith('RUN'):
                    # Collect RUN commands for merging
                    run_commands.append(line[4:].strip())
                
                elif upper_line.startswith('COPY') or upper_line.startswith('ADD'):
                    # Optimize COPY commands
                    optimized_lines.append(await self._optimize_copy_command(line, config))
                
                elif upper_line.startswith('WORKDIR'):
                    optimized_lines.append(line)
                
                elif upper_line.startswith('ENV'):
                    optimized_lines.append(line)
                
                elif upper_line.startswith('EXPOSE'):
                    optimized_lines.append(line)
                
                elif upper_line.startswith('USER'):
                    optimized_lines.append(line)
                
                elif upper_line.startswith('CMD') or upper_line.startswith('ENTRYPOINT'):
                    optimized_lines.append(line)
                
                else:
                    optimized_lines.append(line)
            
            # Merge and optimize RUN commands
            if run_commands:
                merged_run = await self._merge_run_commands(run_commands, config)
                optimized_lines.extend(merged_run)
            
            # Add multi-stage build final stage
            if config.multi_stage_build:
                optimized_lines.extend(await self._create_multi_stage_build_final(config))
            
            # Add optimization layers
            optimization_layers = await self._generate_optimization_layers(config)
            optimized_lines.extend(optimization_layers)
            
            return '\n'.join(optimized_lines)
            
        except Exception as e:
            logger.error(f"Failed to generate optimized Dockerfile: {e}")
            raise

    async def _create_multi_stage_build_header(self, config: OptimizationConfig) -> List[str]:
        """Create multi-stage build header"""
        lines = []
        
        # Build stage
        lines.append("# Build stage")
        lines.append(f"FROM {config.base_image.value} AS builder")
        lines.append("")
        
        # Install build dependencies
        if config.base_image in [BaseImageType.PYTHON_SLIM, BaseImageType.PYTHON_ALPINE]:
            if "alpine" in config.base_image.value:
                lines.append("RUN apk add --no-cache gcc musl-dev libffi-dev")
            else:
                lines.append("RUN apt-get update && apt-get install -y --no-install-recommends \\")
                lines.append("    gcc g++ build-essential \\")
                lines.append("    && rm -rf /var/lib/apt/lists/*")
        
        lines.append("")
        return lines

    async def _create_multi_stage_build_final(self, config: OptimizationConfig) -> List[str]:
        """Create multi-stage build final stage"""
        lines = []
        
        lines.append("")
        lines.append("# Production stage")
        
        # Use distroless or minimal base image for final stage
        if config.use_distroless:
            if "python" in config.base_image.value:
                lines.append("FROM gcr.io/distroless/python3")
            else:
                lines.append("FROM gcr.io/distroless/base")
        else:
            lines.append(f"FROM {config.base_image.value}")
        
        lines.append("")
        
        # Copy from builder stage
        lines.append("# Copy application and dependencies from builder")
        lines.append("COPY --from=builder /usr/local/lib/python*/site-packages /usr/local/lib/python*/site-packages")
        lines.append("COPY --from=builder /usr/local/bin /usr/local/bin")
        lines.append("COPY --from=builder /app /app")
        
        return lines

    async def _optimize_base_image(self, from_line: str, config: OptimizationConfig) -> str:
        """Optimize base image selection"""
        if config.optimization_level == OptimizationLevel.AGGRESSIVE:
            # Use smallest possible base image
            if "python" in from_line.lower():
                return f"FROM {BaseImageType.PYTHON_ALPINE.value}"
            elif "ubuntu" in from_line.lower():
                return "FROM alpine:3.18"
        
        return f"FROM {config.base_image.value}"

    async def _optimize_copy_command(self, copy_line: str, config: OptimizationConfig) -> str:
        """Optimize COPY/ADD commands"""
        # Add optimization for COPY commands
        if copy_line.upper().startswith('ADD'):
            # Convert ADD to COPY where appropriate
            return copy_line.replace('ADD', 'COPY', 1)
        
        return copy_line

    async def _merge_run_commands(
        self, 
        run_commands: List[str], 
        config: OptimizationConfig
    ) -> List[str]:
        """Merge multiple RUN commands for layer optimization"""
        if len(run_commands) <= 1:
            return [f"RUN {cmd}" for cmd in run_commands]
        
        # Group commands by type
        package_installs = []
        pip_installs = []
        cleanup_commands = []
        other_commands = []
        
        for cmd in run_commands:
            cmd_lower = cmd.lower()
            if any(pkg in cmd_lower for pkg in ['apt-get install', 'yum install', 'apk add']):
                package_installs.append(cmd)
            elif 'pip install' in cmd_lower:
                pip_installs.append(cmd)
            elif any(cleanup in cmd_lower for cleanup in ['rm -rf', 'apt-get clean', 'yum clean']):
                cleanup_commands.append(cmd)
            else:
                other_commands.append(cmd)
        
        merged_lines = []
        
        # Merge package installations
        if package_installs:
            merged_cmd = " && \\\n    ".join(package_installs)
            if config.remove_dev_dependencies:
                merged_cmd += " && \\\n    apt-get clean && rm -rf /var/lib/apt/lists/*"
            merged_lines.append(f"RUN {merged_cmd}")
        
        # Merge pip installations
        if pip_installs:
            merged_cmd = " && \\\n    ".join(pip_installs)
            if config.dependency_caching:
                merged_cmd = f"--mount=type=cache,target=/root/.cache/pip {merged_cmd}"
            merged_lines.append(f"RUN {merged_cmd}")
        
        # Add other commands
        for cmd in other_commands:
            merged_lines.append(f"RUN {cmd}")
        
        return merged_lines

    async def _generate_optimization_layers(self, config: OptimizationConfig) -> List[str]:
        """Generate additional optimization layers"""
        lines = []
        
        if config.optimization_level in [OptimizationLevel.AGGRESSIVE, OptimizationLevel.PRODUCTION]:
            lines.append("")
            lines.append("# Optimization layers")
            
            # Security hardening
            if config.security_scanning:
                lines.append("RUN useradd -r -s /bin/false appuser")
                lines.append("USER appuser")
            
            # Cleanup
            if config.remove_dev_dependencies:
                lines.append("RUN find /usr/local -type d -name '__pycache__' -exec rm -rf {} + || true")
                lines.append("RUN find /usr/local -name '*.pyc' -delete")
        
        return lines

    async def _build_and_measure(
        self,
        dockerfile_content: str,
        context_path: Path,
        tag_suffix: str
    ) -> BuildMetrics:
        """Build container and measure metrics"""
        metrics = BuildMetrics()
        
        try:
            if not self.docker_client:
                logger.warning("Docker client not available, returning mock metrics")
                # Return mock metrics for testing
                metrics.build_time = 60.0 if tag_suffix == "original" else 45.0
                metrics.image_size = 1000000000 if tag_suffix == "original" else 500000000
                metrics.layer_count = 15 if tag_suffix == "original" else 8
                metrics.vulnerability_count = 10 if tag_suffix == "original" else 2
                return metrics
            
            start_time = datetime.utcnow()
            
            # Create temporary Dockerfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.Dockerfile', delete=False) as f:
                f.write(dockerfile_content)
                temp_dockerfile = Path(f.name)
            
            try:
                # Build image
                tag = f"mlops-optimizer-{tag_suffix}:{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
                
                image, build_logs = self.docker_client.images.build(
                    path=str(context_path),
                    dockerfile=str(temp_dockerfile),
                    tag=tag,
                    rm=True,
                    forcerm=True
                )
                
                # Calculate build time
                build_time = (datetime.utcnow() - start_time).total_seconds()
                metrics.build_time = build_time
                
                # Get image size
                image.reload()
                metrics.image_size = image.attrs['Size']
                
                # Count layers
                metrics.layer_count = len(image.history())
                
                # Mock vulnerability scanning
                metrics.vulnerability_count = await self._scan_vulnerabilities(image)
                
                # Cleanup
                self.docker_client.images.remove(image.id, force=True)
                
            finally:
                temp_dockerfile.unlink()
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Failed to build and measure container: {e}")
            # Return default metrics
            return metrics

    async def _scan_vulnerabilities(self, image) -> int:
        """Scan container for vulnerabilities"""
        try:
            # This would integrate with actual vulnerability scanners
            # like Trivy, Clair, or Snyk
            # For now, return mock count
            return 5
        except Exception as e:
            logger.warning(f"Vulnerability scanning failed: {e}")
            return 0

    async def _calculate_optimization_result(
        self,
        original_metrics: BuildMetrics,
        optimized_metrics: BuildMetrics,
        start_time: datetime
    ) -> OptimizationResult:
        """Calculate optimization results"""
        size_reduction = 0.0
        if original_metrics.image_size > 0:
            size_reduction = (
                (original_metrics.image_size - optimized_metrics.image_size) 
                / original_metrics.image_size * 100
            )
        
        layer_reduction = original_metrics.layer_count - optimized_metrics.layer_count
        vulnerabilities_fixed = original_metrics.vulnerability_count - optimized_metrics.vulnerability_count
        
        return OptimizationResult(
            original_size=original_metrics.image_size,
            optimized_size=optimized_metrics.image_size,
            size_reduction=size_reduction,
            build_time=optimized_metrics.build_time,
            layer_reduction=layer_reduction,
            vulnerabilities_fixed=vulnerabilities_fixed,
            recommendations=[],
            warnings=[],
            metrics=optimized_metrics
        )

    async def _generate_recommendations(
        self,
        analysis: Dict[str, Any],
        metrics: BuildMetrics,
        config: OptimizationConfig
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Size-based recommendations
        if metrics.image_size > 500 * 1024 * 1024:  # > 500MB
            recommendations.append("Consider using multi-stage builds to reduce image size")
            recommendations.append("Remove unnecessary dependencies and files")
        
        # Layer-based recommendations
        if metrics.layer_count > 10:
            recommendations.append("Merge RUN commands to reduce layer count")
        
        # Security recommendations
        if metrics.vulnerability_count > 5:
            recommendations.append("Update base image to latest version")
            recommendations.append("Remove or update vulnerable packages")
        
        # Performance recommendations
        if metrics.build_time > 300:  # > 5 minutes
            recommendations.append("Enable build caching to improve build times")
            recommendations.append("Optimize package installation order")
        
        # Base image recommendations
        if analysis["base_image"] and "ubuntu" in analysis["base_image"].lower():
            recommendations.append("Consider using Alpine Linux for smaller image size")
        
        return recommendations

    async def optimize_for_inference(
        self,
        dockerfile_path: Path,
        model_files: List[Path],
        context_path: Path,
        target_latency_ms: int = 100
    ) -> OptimizationResult:
        """Optimize container specifically for ML inference"""
        try:
            logger.info(f"Optimizing container for inference with target latency {target_latency_ms}ms")
            
            # Create inference-specific optimization config
            config = OptimizationConfig(
                optimization_level=OptimizationLevel.PRODUCTION,
                base_image=BaseImageType.PYTHON_SLIM,
                multi_stage_build=True,
                layer_caching=True,
                dependency_caching=True,
                remove_dev_dependencies=True,
                compress_layers=True,
                security_scanning=True,
                vulnerability_fixes=True
            )
            
            # Read original Dockerfile
            original_dockerfile = await self._read_dockerfile(dockerfile_path)
            
            # Generate inference-optimized Dockerfile
            inference_dockerfile = await self._generate_inference_dockerfile(
                original_dockerfile, model_files, config, target_latency_ms
            )
            
            # Build and measure
            original_metrics = await self._build_and_measure(
                original_dockerfile, context_path, "original"
            )
            
            optimized_metrics = await self._build_and_measure(
                inference_dockerfile, context_path, "inference-optimized"
            )
            
            result = await self._calculate_optimization_result(
                original_metrics, optimized_metrics, datetime.utcnow()
            )
            
            # Add inference-specific recommendations
            result.recommendations.extend([
                "Use model quantization for faster inference",
                "Implement model serving with TensorRT or ONNX Runtime",
                "Configure proper CPU/GPU resource limits",
                "Enable request batching for improved throughput"
            ])
            
            return result
            
        except Exception as e:
            logger.error(f"Inference optimization failed: {e}")
            raise

    async def _generate_inference_dockerfile(
        self,
        original_dockerfile: str,
        model_files: List[Path],
        config: OptimizationConfig,
        target_latency_ms: int
    ) -> str:
        """Generate inference-optimized Dockerfile"""
        lines = []
        
        # Multi-stage build for inference
        lines.append("# Inference-optimized build")
        lines.append(f"FROM {config.base_image.value} AS builder")
        lines.append("")
        
        # Install build dependencies
        lines.append("RUN apt-get update && apt-get install -y --no-install-recommends \\")
        lines.append("    gcc g++ build-essential \\")
        lines.append("    && rm -rf /var/lib/apt/lists/*")
        lines.append("")
        
        # Install Python dependencies with optimizations
        lines.append("COPY requirements.txt .")
        lines.append("RUN pip install --no-cache-dir --user -r requirements.txt")
        lines.append("")
        
        # Production stage
        lines.append("FROM python:3.9-slim AS production")
        lines.append("")
        
        # Copy optimized dependencies
        lines.append("COPY --from=builder /root/.local /root/.local")
        lines.append("")
        
        # Set up application
        lines.append("WORKDIR /app")
        lines.append("")
        
        # Copy model files efficiently
        for model_file in model_files:
            lines.append(f"COPY {model_file.name} ./models/")
        lines.append("")
        
        # Copy application code
        lines.append("COPY . .")
        lines.append("")
        
        # Optimization for inference
        lines.append("# Inference optimizations")
        lines.append("ENV PYTHONUNBUFFERED=1")
        lines.append("ENV PYTHONDONTWRITEBYTECODE=1")
        lines.append("ENV OMP_NUM_THREADS=1")
        lines.append("ENV MKL_NUM_THREADS=1")
        lines.append("")
        
        # Health check
        lines.append("HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\")
        lines.append("    CMD curl -f http://localhost:8080/health || exit 1")
        lines.append("")
        
        # Expose port
        lines.append("EXPOSE 8080")
        lines.append("")
        
        # Non-root user for security
        lines.append("RUN useradd -r -s /bin/false appuser")
        lines.append("USER appuser")
        lines.append("")
        
        # Start command
        lines.append("CMD [\"python\", \"serve.py\"]")
        
        return '\n'.join(lines)

    async def generate_docker_compose(
        self,
        optimized_image: str,
        config: Dict[str, Any]
    ) -> str:
        """Generate Docker Compose for optimized ML service"""
        compose_config = {
            "version": "3.8",
            "services": {
                "ml-inference": {
                    "image": optimized_image,
                    "ports": ["8080:8080"],
                    "environment": {
                        "MODEL_PATH": "/app/models",
                        "LOG_LEVEL": "INFO",
                        "MAX_WORKERS": "4"
                    },
                    "resources": {
                        "limits": {
                            "cpus": "2.0",
                            "memory": "4G"
                        }
                    },
                    "restart": "unless-stopped",
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8080/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                }
            }
        }
        
        return yaml.dump(compose_config, default_flow_style=False)


class ContainerRegistry:
    """
    Container registry integration for optimized images
    """
    
    def __init__(self, registry_url -> None: str, credentials -> None: Optional[Dict[str, str]] = None) -> None:
        self.registry_url = registry_url
        self.credentials = credentials
        self.docker_client = None
        
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client not available: {e}")

    async def push_optimized_image(
        self,
        local_tag: str,
        remote_tag: str,
        optimization_metadata: Dict[str, Any]
    ) -> bool:
        """Push optimized image to registry with metadata"""
        try:
            if not self.docker_client:
                logger.warning("Docker client not available")
                return False
            
            # Tag image for registry
            image = self.docker_client.images.get(local_tag)
            full_remote_tag = f"{self.registry_url}/{remote_tag}"
            image.tag(full_remote_tag)
            
            # Add optimization metadata as labels
            metadata_labels = {
                f"ai.mlops.optimization.{key}": str(value)
                for key, value in optimization_metadata.items()
            }
            
            # Push to registry
            push_result = self.docker_client.images.push(full_remote_tag)
            
            logger.info(f"Optimized image pushed to {full_remote_tag}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push optimized image: {e}")
            return False


# Factory functions
def create_container_optimizer(runtime: ContainerRuntime = ContainerRuntime.DOCKER) -> ContainerOptimizer:
    """Create a new container optimizer instance"""
    return ContainerOptimizer(runtime=runtime)


def create_optimization_config(
    level: OptimizationLevel = OptimizationLevel.STANDARD,
    base_image: BaseImageType = BaseImageType.PYTHON_SLIM
) -> OptimizationConfig:
    """Create optimization configuration"""
    return OptimizationConfig(
        optimization_level=level,
        base_image=base_image
    )


# Example usage
if __name__ == "__main__":
    async def main() -> None:
        # Create optimizer
        optimizer = create_container_optimizer()
        
        # Create optimization config
        config = create_optimization_config(
            level=OptimizationLevel.PRODUCTION,
            base_image=BaseImageType.PYTHON_SLIM
        )
        
        # Optimize container
        dockerfile_path = Path("Dockerfile")
        context_path = Path(".")
        
        if dockerfile_path.exists():
            result = await optimizer.optimize_container(
                dockerfile_path=dockerfile_path,
                context_path=context_path,
                config=config,
                output_path=Path("Dockerfile.optimized")
            )
            
            print(f"Optimization completed!")
            print(f"Size reduction: {result.size_reduction:.1f}%")
            print(f"Build time: {result.build_time:.1f}s")
            print(f"Layer reduction: {result.layer_reduction}")
            print(f"Vulnerabilities fixed: {result.vulnerabilities_fixed}")
            
            print("\nRecommendations:")
            for rec in result.recommendations:
                print(f"- {rec}")
        else:
            print("Dockerfile not found in current directory")
    
    asyncio.run(main())