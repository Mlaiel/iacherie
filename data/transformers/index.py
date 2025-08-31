"""
Index Module - Comprehensive module indexing for IA Influencer Agent Platform
============================================================================

Advanced indexing and discovery system for the transformers module ecosystem
providing intelligent module management and dependency resolution.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Type, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import inspect
import importlib
import sys

logger = logging.getLogger(__name__)


class ModuleType(Enum):
    """Types of transformer modules."""
    CORE_TRANSFORMER = "core_transformer"
    SPECIALIZED_PROCESSOR = "specialized_processor"
    UTILITY_MODULE = "utility_module"
    FORMAT_CONVERTER = "format_converter"
    QUALITY_ENHANCER = "quality_enhancer"
    BATCH_PROCESSOR = "batch_processor"
    REALTIME_CONVERTER = "realtime_converter"
    ENCODING_MANAGER = "encoding_manager"


class ModuleStatus(Enum):
    """Module availability status."""
    AVAILABLE = "available"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


@dataclass
class ModuleInfo:
    """Information about a transformer module."""
    name: str
    module_type: ModuleType
    description: str
    version: str = "1.0.0"
    
    # Module metadata
    file_path: str = ""
    class_name: str = ""
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    
    # Capabilities
    supported_formats: List[str] = field(default_factory=list)
    input_types: List[str] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)
    
    # Performance characteristics
    processing_speed: str = "medium"  # fast, medium, slow
    memory_usage: str = "medium"      # low, medium, high
    cpu_intensive: bool = False
    gpu_acceleration: bool = False
    
    # Status and metadata
    status: ModuleStatus = ModuleStatus.AVAILABLE
    load_time: Optional[float] = None
    last_used: Optional[float] = None
    usage_count: int = 0
    
    # Error information
    error_message: Optional[str] = None
    
    # Documentation
    documentation_url: Optional[str] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TransformationCapability:
    """Describes a transformation capability."""
    name: str
    input_format: str
    output_format: str
    quality_level: str
    processing_time: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)


class ModuleIndex:
    """
    Comprehensive module indexing system for the IA Influencer Agent Platform.
    
    Provides intelligent module discovery, dependency management, and
    transformation capability mapping for the entire transformers ecosystem.
    """
    
    def __init__(self, transformers_path: Optional[str] = None):
        """
        Initialize module index.
        
        Args:
            transformers_path: Path to transformers directory
        """
        self.transformers_path = transformers_path or str(Path(__file__).parent)
        
        # Module registry
        self.modules: Dict[str, ModuleInfo] = {}
        self.loaded_modules: Dict[str, Any] = {}
        
        # Capability mapping
        self.capabilities: Dict[str, List[TransformationCapability]] = {}
        self.format_matrix: Dict[str, Dict[str, List[str]]] = {}
        
        # Performance tracking
        self.performance_stats: Dict[str, Dict[str, Any]] = {}
        
        # Dependency graph
        self.dependency_graph: Dict[str, List[str]] = {}
        
        # Index metadata
        self.index_version = "1.0.0"
        self.last_scan: Optional[float] = None
        self.scan_count: int = 0
        
        logger.info("ModuleIndex initialized")
    
    async def scan_modules(self, force_rescan: bool = False) -> Dict[str, ModuleInfo]:
        """
        Scan and index all transformer modules.
        
        Args:
            force_rescan: Force complete rescan even if recently scanned
            
        Returns:
            Dictionary of discovered modules
        """



        try:
            # Check if recent scan exists
            if not force_rescan and self.last_scan:
                if time.time() - self.last_scan < 300:  # 5 minutes
                    logger.info("Using cached module scan")
                    return self.modules
            
            logger.info("Scanning transformer modules...")
            start_time = time.time()
            
            # Clear existing modules
            self.modules.clear()
            self.capabilities.clear()
            
            # Scan transformer directory
            transformers_dir = Path(self.transformers_path)
            
            # Core modules
            await self._scan_core_modules(transformers_dir)
            
            # Specialized processors
            await self._scan_specialized_processors(transformers_dir)
            
            # Utility modules
            await self._scan_utility_modules(transformers_dir)
            
            # Build dependency graph
            await self._build_dependency_graph()
            
            # Generate capability matrix
            await self._generate_capability_matrix()
            
            # Update scan metadata
            self.last_scan = time.time()
            self.scan_count += 1
            scan_duration = time.time() - start_time
            
            logger.info(f"Module scan completed: {len(self.modules)} modules found in {scan_duration:.2f}s")
            return self.modules
            
        except Exception as e:
            logger.error(f"Module scanning failed: {str(e)}")
            return {}
    
    async def get_module_info(self, module_name: str) -> Optional[ModuleInfo]:
        """Get detailed information about a specific module."""



        return self.modules.get(module_name)
    
    async def load_module(self, module_name: str) -> Optional[Any]:
        """
        Load a specific transformer module.
        
        Args:
            module_name: Name of module to load
            
        Returns:
            Loaded module instance
        """



        try:
            # Check if already loaded
            if module_name in self.loaded_modules:
                logger.debug(f"Module already loaded: {module_name}")
                return self.loaded_modules[module_name]
            
            # Get module info
            module_info = self.modules.get(module_name)
            if not module_info:
                logger.error(f"Module not found: {module_name}")
                return None
            
            # Update status
            module_info.status = ModuleStatus.LOADING
            load_start = time.time()
            
            # Load dependencies first
            await self._load_dependencies(module_name)
            
            # Import module
            module_path = f"backend.data.transformers.{module_name}"
            module = importlib.import_module(module_path)
            
            # Get main class
            if module_info.class_name:
                main_class = getattr(module, module_info.class_name)
                instance = main_class()
            else:
                instance = module
            
            # Store loaded module
            self.loaded_modules[module_name] = instance
            
            # Update module info
            module_info.status = ModuleStatus.LOADED
            module_info.load_time = time.time() - load_start
            module_info.last_used = time.time()
            module_info.usage_count += 1
            
            logger.info(f"Module loaded successfully: {module_name}")
            return instance
            
        except Exception as e:
            logger.error(f"Module loading failed: {module_name} - {str(e)}")
            
            # Update error status
            if module_name in self.modules:
                self.modules[module_name].status = ModuleStatus.ERROR
                self.modules[module_name].error_message = str(e)
            
            return None
    
    async def find_transformers_for_format(
        self,
        input_format: str,
        output_format: str
    ) -> List[str]:
        """
        Find transformers capable of converting between specific formats.
        
        Args:
            input_format: Input format
            output_format: Output format
            
        Returns:
            List of capable transformer names
        """
        capable_transformers = []
        
        for module_name, module_info in self.modules.items():
            if (input_format in module_info.input_types and 
                output_format in module_info.output_types):
                capable_transformers.append(module_name)
        
        # Sort by performance characteristics
        capable_transformers.sort(key=lambda x: self._get_transformer_score(x))
        
        return capable_transformers
    
    async def get_transformation_path(
        self,
        input_format: str,
        output_format: str
    ) -> Optional[List[str]]:
        """
        Find optimal transformation path between formats.
        
        Args:
            input_format: Source format
            output_format: Target format
            
        Returns:
            List of transformers in sequence, or None if no path exists
        """



        try:
            # Direct transformation available
            direct_transformers = await self.find_transformers_for_format(
                input_format, output_format
            )
            
            if direct_transformers:
                return [direct_transformers[0]]  # Return best direct transformer
            
            # Find multi-step path using graph traversal
            path = await self._find_transformation_path_bfs(input_format, output_format)
            return path
            
        except Exception as e:
            logger.error(f"Transformation path finding failed: {str(e)}")
            return None
    
    async def get_module_capabilities(self, module_name: str) -> List[TransformationCapability]:
        """Get all transformation capabilities of a module."""



        return self.capabilities.get(module_name, [])
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview."""



        try:
            # Module statistics
            total_modules = len(self.modules)
            loaded_modules = len(self.loaded_modules)
            
            # Status distribution
            status_counts = {}
            for module_info in self.modules.values():
                status = module_info.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Type distribution
            type_counts = {}
            for module_info in self.modules.values():
                module_type = module_info.module_type.value
                type_counts[module_type] = type_counts.get(module_type, 0) + 1
            
            # Format support
            supported_formats = set()
            for module_info in self.modules.values():
                supported_formats.update(module_info.supported_formats)
            
            # Performance overview
            fast_modules = sum(1 for m in self.modules.values() if m.processing_speed == "fast")
            gpu_modules = sum(1 for m in self.modules.values() if m.gpu_acceleration)
            
            return {
                "index_version": self.index_version,
                "last_scan": self.last_scan,
                "scan_count": self.scan_count,
                "total_modules": total_modules,
                "loaded_modules": loaded_modules,
                "status_distribution": status_counts,
                "type_distribution": type_counts,
                "supported_formats": list(supported_formats),
                "performance_summary": {
                    "fast_modules": fast_modules,
                    "gpu_accelerated": gpu_modules,
                    "total_capabilities": sum(len(caps) for caps in self.capabilities.values())
                },
                "dependency_complexity": len(self.dependency_graph)
            }
            
        except Exception as e:
            logger.error(f"System overview generation failed: {str(e)}")
            return {}
    
    async def validate_dependencies(self) -> Dict[str, List[str]]:
        """Validate all module dependencies."""
        validation_results = {}
        
        for module_name, module_info in self.modules.items():
            missing_deps = []
            
            # Check required dependencies
            for dep in module_info.dependencies:
                try:
                    importlib.import_module(dep)
                except ImportError:
                    missing_deps.append(dep)
            
            if missing_deps:
                validation_results[module_name] = missing_deps
        
        return validation_results
    
    async def get_optimization_suggestions(self) -> List[str]:
        """Get optimization suggestions for the transformer ecosystem."""
        suggestions = []
        
        # Check for missing dependencies
        missing_deps = await self.validate_dependencies()
        if missing_deps:
            suggestions.append(f"Install missing dependencies for {len(missing_deps)} modules")
        
        # Check for unloaded frequently used modules
        frequent_modules = [
            name for name, info in self.modules.items()
            if info.usage_count > 5 and name not in self.loaded_modules
        ]
        if frequent_modules:
            suggestions.append(f"Consider preloading {len(frequent_modules)} frequently used modules")
        
        # Check for redundant capabilities
        redundant_count = await self._count_redundant_capabilities()
        if redundant_count > 0:
            suggestions.append(f"Optimize {redundant_count} redundant transformation capabilities")
        
        return suggestions
    
    async def export_index(self, output_file: str) -> bool:
        """Export module index to file."""



        try:
            index_data = {
                "version": self.index_version,
                "generated_at": time.time(),
                "modules": {
                    name: {
                        "name": info.name,
                        "type": info.module_type.value,
                        "description": info.description,
                        "version": info.version,
                        "dependencies": info.dependencies,
                        "supported_formats": info.supported_formats,
                        "input_types": info.input_types,
                        "output_types": info.output_types,
                        "processing_speed": info.processing_speed,
                        "memory_usage": info.memory_usage,
                        "cpu_intensive": info.cpu_intensive,
                        "gpu_acceleration": info.gpu_acceleration
                    }
                    for name, info in self.modules.items()
                },
                "capabilities": {
                    name: [
                        {
                            "name": cap.name,
                            "input_format": cap.input_format,
                            "output_format": cap.output_format,
                            "quality_level": cap.quality_level,
                            "processing_time": cap.processing_time,
                            "description": cap.description
                        }
                        for cap in caps
                    ]
                    for name, caps in self.capabilities.items()
                },
                "dependency_graph": self.dependency_graph
            }
            
            with open(output_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            logger.info(f"Index exported to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Index export failed: {str(e)}")
            return False
    
    async def _scan_core_modules(self, transformers_dir: Path):
        """Scan core transformer modules."""
        core_modules = [
            ("data_transformer", "DataTransformer", "Main transformation coordinator"),
            ("audio_transformer", "AudioTransformer", "Professional audio processing"),
            ("video_transformer", "VideoTransformer", "Advanced video processing"),
            ("image_transformer", "ImageTransformer", "Image optimization and conversion"),
            ("text_transformer", "TextTransformer", "NLP and text processing"),
            ("metadata_transformer", "MetadataTransformer", "Metadata extraction and transformation")
        ]
        
        for module_name, class_name, description in core_modules:
            module_file = transformers_dir / f"{module_name}.py"
            
            if module_file.exists():
                module_info = ModuleInfo(
                    name=module_name,
                    module_type=ModuleType.CORE_TRANSFORMER,
                    description=description,
                    file_path=str(module_file),
                    class_name=class_name,
                    processing_speed="medium",
                    memory_usage="medium"
                )
                
                # Set supported formats based on module type
                if "audio" in module_name:
                    module_info.supported_formats = ["mp3", "wav", "aac", "flac", "ogg"]
                    module_info.input_types = ["audio"]
                    module_info.output_types = ["audio"]
                elif "video" in module_name:
                    module_info.supported_formats = ["mp4", "avi", "mov", "mkv", "webm"]
                    module_info.input_types = ["video"]
                    module_info.output_types = ["video"]
                    module_info.gpu_acceleration = True
                elif "image" in module_name:
                    module_info.supported_formats = ["jpg", "png", "gif", "bmp", "webp"]
                    module_info.input_types = ["image"]
                    module_info.output_types = ["image"]
                elif "text" in module_name:
                    module_info.supported_formats = ["txt", "md", "json", "xml"]
                    module_info.input_types = ["text"]
                    module_info.output_types = ["text"]
                
                self.modules[module_name] = module_info
    
    async def _scan_specialized_processors(self, transformers_dir: Path):
        """Scan specialized processor modules."""
        specialized_modules = [
            ("format_converter", "FormatConverter", "Universal format conversion"),
            ("quality_optimizer", "QualityOptimizer", "AI-powered quality enhancement"),
            ("encoding_manager", "EncodingManager", "Professional encoding optimization")
        ]
        
        for module_name, class_name, description in specialized_modules:
            module_file = transformers_dir / f"{module_name}.py"
            
            if module_file.exists():
                module_info = ModuleInfo(
                    name=module_name,
                    module_type=ModuleType.SPECIALIZED_PROCESSOR,
                    description=description,
                    file_path=str(module_file),
                    class_name=class_name,
                    processing_speed="medium",
                    memory_usage="high" if "quality" in module_name else "medium",
                    cpu_intensive=True,
                    gpu_acceleration="quality" in module_name
                )
                
                # Universal format support for these modules
                module_info.supported_formats = ["mp4", "mp3", "jpg", "png", "wav", "avi"]
                module_info.input_types = ["video", "audio", "image"]
                module_info.output_types = ["video", "audio", "image"]
                
                self.modules[module_name] = module_info
    
    async def _scan_utility_modules(self, transformers_dir: Path):
        """Scan utility modules."""
        utility_modules = [
            ("batch_processor", "BatchProcessor", "High-performance batch processing"),
            ("realtime_converter", "RealtimeConverter", "Live content transformation")
        ]
        
        for module_name, class_name, description in utility_modules:
            module_file = transformers_dir / f"{module_name}.py"
            
            if module_file.exists():
                module_info = ModuleInfo(
                    name=module_name,
                    module_type=ModuleType.UTILITY_MODULE,
                    description=description,
                    file_path=str(module_file),
                    class_name=class_name,
                    processing_speed="fast" if "realtime" in module_name else "medium",
                    memory_usage="high",
                    cpu_intensive=True
                )
                
                # These modules support all formats
                module_info.supported_formats = ["*"]
                module_info.input_types = ["any"]
                module_info.output_types = ["any"]
                
                self.modules[module_name] = module_info
    
    async def _build_dependency_graph(self):
        """Build module dependency graph."""
        self.dependency_graph.clear()
        
        for module_name, module_info in self.modules.items():
            deps = []
            
            # Add explicit dependencies
            deps.extend(module_info.dependencies)
            
            # Add implicit dependencies based on module type
            if module_info.module_type == ModuleType.CORE_TRANSFORMER:
                if module_name != "data_transformer":
                    deps.append("data_transformer")
            
            self.dependency_graph[module_name] = deps
    
    async def _generate_capability_matrix(self):
        """Generate transformation capability matrix."""
        self.capabilities.clear()
        
        for module_name, module_info in self.modules.items():
            capabilities = []
            
            # Generate capabilities based on supported formats
            if module_info.input_types and module_info.output_types:
                for input_type in module_info.input_types:
                    for output_type in module_info.output_types:
                        if input_type != output_type or input_type == "any":
                            capability = TransformationCapability(
                                name=f"{input_type}_to_{output_type}",
                                input_format=input_type,
                                output_format=output_type,
                                quality_level="high" if module_info.gpu_acceleration else "medium",
                                processing_time=module_info.processing_speed,
                                description=f"Transform {input_type} to {output_type}"
                            )
                            capabilities.append(capability)
            
            self.capabilities[module_name] = capabilities
    
    async def _load_dependencies(self, module_name: str):
        """Load module dependencies recursively."""
        module_info = self.modules.get(module_name)
        if not module_info:
            return
        
        for dep in module_info.dependencies:
            if dep in self.modules and dep not in self.loaded_modules:
                await self.load_module(dep)
    
    def _get_transformer_score(self, module_name: str) -> int:
        """Get transformer performance score for sorting."""
        module_info = self.modules.get(module_name)
        if not module_info:
            return 999
        
        score = 0
        
        # Speed scoring
        speed_scores = {"fast": 10, "medium": 20, "slow": 30}
        score += speed_scores.get(module_info.processing_speed, 25)
        
        # Memory scoring
        memory_scores = {"low": 5, "medium": 10, "high": 15}
        score += memory_scores.get(module_info.memory_usage, 10)
        
        # GPU acceleration bonus
        if module_info.gpu_acceleration:
            score -= 5
        
        return score
    
    async def _find_transformation_path_bfs(
        self,
        start_format: str,
        end_format: str
    ) -> Optional[List[str]]:
        """Find transformation path using breadth-first search."""
        from collections import deque
        
        # Build format graph
        format_graph = {}
        
        for module_name, capabilities in self.capabilities.items():
            for cap in capabilities:
                if cap.input_format not in format_graph:
                    format_graph[cap.input_format] = []
                format_graph[cap.input_format].append((cap.output_format, module_name))
        
        # BFS to find path
        queue = deque([(start_format, [])])
        visited = {start_format}
        
        while queue:
            current_format, path = queue.popleft()
            
            if current_format == end_format:
                return path
            
            if current_format in format_graph:
                for next_format, transformer in format_graph[current_format]:
                    if next_format not in visited:
                        visited.add(next_format)
                        queue.append((next_format, path + [transformer]))
        
        return None
    
    async def _count_redundant_capabilities(self) -> int:
        """Count redundant transformation capabilities."""
        capability_map = {}
        
        for module_name, capabilities in self.capabilities.items():
            for cap in capabilities:
                key = (cap.input_format, cap.output_format)
                if key not in capability_map:
                    capability_map[key] = []
                capability_map[key].append(module_name)
        
        redundant_count = sum(
            len(modules) - 1 for modules in capability_map.values()
            if len(modules) > 1
        )
        
        return redundant_count


# Global module index instance
_global_index: Optional[ModuleIndex] = None


def get_module_index() -> ModuleIndex:
    """Get global module index instance."""
    global _global_index
    
    if _global_index is None:
        _global_index = ModuleIndex()
    
    return _global_index


async def initialize_index() -> ModuleIndex:
    """Initialize and scan module index."""
    index = get_module_index()
    await index.scan_modules()
    return index


# Convenience functions for common operations
async def find_transformer(input_format: str, output_format: str) -> Optional[str]:
    """Find best transformer for format conversion."""
    index = get_module_index()
    transformers = await index.find_transformers_for_format(input_format, output_format)
    return transformers[0] if transformers else None


async def load_transformer(module_name: str) -> Optional[Any]:
    """Load a transformer module."""
    index = get_module_index()
    return await index.load_module(module_name)


async def get_available_formats() -> List[str]:
    """Get all supported formats."""
    index = get_module_index()
    formats = set()
    
    for module_info in index.modules.values():
        formats.update(module_info.supported_formats)
    
    return list(formats)


async def export_module_documentation(output_dir: str) -> bool:
    """Export comprehensive module documentation."""



    try:
        index = get_module_index()
        overview = await index.get_system_overview()
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Export main index
        await index.export_index(str(output_path / "module_index.json"))
        
        # Export overview
        with open(output_path / "system_overview.json", 'w') as f:
            json.dump(overview, f, indent=2)
        
        # Export capabilities matrix
        with open(output_path / "capabilities_matrix.json", 'w') as f:
            json.dump(index.capabilities, f, indent=2, default=str)
        
        logger.info(f"Documentation exported to: {output_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Documentation export failed: {str(e)}")
        return False
