"""Multimedia Content Management Module - Professional Multi-Modal Content Processing System

Module spécialisé pour la gestion, l'analyse et la protection du contenu multimédia
combinant audio, vidéo, image et texte dans la plateforme IA Influencer Agent.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Multi-Modal AI Expert, Cross-Platform Specialist, Content Protection Expert
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import logging
import hashlib
import json
import asyncio
from enum import Enum
import zipfile
import tarfile

# Import content type managers
from .audio_content import AudioContentManager, AudioMetadata, AudioFingerprint
from .video_content import VideoContentManager, VideoMetadata, VideoFingerprint
from .image_content import ImageContentManager, ImageMetadata, ImageFingerprint
from .text_content import TextContentManager, TextMetadata, TextFingerprint

logger = logging.getLogger(__name__)

class MultimediaFormat(Enum):
    """
Supported multimedia container formats"""

    ZIP = {"ext": ".zip", "compression": True, "structured": True, "metadata": False}
    TAR = {"ext": ".tar", "compression": False, "structured": True, "metadata": False}
    TAR_GZ = {"ext": ".tar.gz", "compression": True, "structured": True, "metadata": False}
    BUNDLE = {"ext": ".bundle", "compression": True, "structured": True, "metadata": True}
    PACKAGE = {"ext": ".pkg", "compression": True, "structured": True, "metadata": True}
    ARCHIVE = {"ext": ".archive", "compression": True, "structured": True, "metadata": True}

class MultimediaContentType(Enum):
    """Multimedia content classification types"""

    PRESENTATION = "presentation"  # Slides with text, images, videos
    INTERACTIVE_MEDIA = "interactive_media"  # Games, apps with multimedia
    DOCUMENTARY_PACKAGE = "documentary_package"  # Video + transcripts + images
    MUSIC_ALBUM = "music_album"  # Audio tracks + artwork + metadata
    EBOOK_ENHANCED = "ebook_enhanced"  # Text + images + audio/video
    TUTORIAL_SERIES = "tutorial_series"  # Videos + documents + code
    NEWS_PACKAGE = "news_package"  # Article + images + video clips
    MARKETING_CAMPAIGN = "marketing_campaign"  # Mixed media for promotion
    PORTFOLIO = "portfolio"  # Collection of creative works
    COURSE_MATERIAL = "course_material"  # Educational content package
    PODCAST_EPISODE = "podcast_episode"  # Audio + transcript + show notes
    SOCIAL_MEDIA_CAMPAIGN = "social_media_campaign"  # Cross-platform content
    BRAND_PACKAGE = "brand_package"  # Logos, guidelines, assets
    RESEARCH_DATA = "research_data"  # Data + visualizations + reports

class SynchronizationType(Enum):
    """Types of synchronization between multimedia components"""

    TEMPORAL = "temporal"  # Time-based synchronization
    SPATIAL = "spatial"  # Layout-based synchronization
    SEMANTIC = "semantic"  # Content-based relationships
    INTERACTIVE = "interactive"  # User-triggered relationships
    SEQUENTIAL = "sequential"  # Order-based relationships

@dataclass
class MultimediaComponent:
    """Individual component within multimedia content"""
    component_id: str
    component_type: str  # audio, video, image, text
    file_path: str
    file_size: int
    format: str
    metadata: Optional[Dict[str, Any]] = None
    fingerprint: Optional[Dict[str, Any]] = None
    relationships: List[str] = field(default_factory=list)  # Related component IDs
    sync_points: List[Dict[str, Any]] = field(default_factory=list)
    processing_status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class MultimediaMetadata:
    """Comprehensive multimedia metadata structure"""
    # Package information
    total_components: int
    component_types: Dict[str, int]  # Count by type
    total_size: int
    package_format: str
    
    # Content analysis
    content_type: Optional[MultimediaContentType] = None
    primary_content_type: Optional[str] = None  # Dominant component type
    secondary_content_types: List[str] = field(default_factory=list)
    content_themes: List[str] = field(default_factory=list)
    
    # Synchronization analysis
    synchronization_type: Optional[SynchronizationType] = None
    sync_quality_score: Optional[float] = None
    temporal_alignment: bool = False
    spatial_coherence: bool = False
    
    # Quality metrics
    overall_quality_score: Optional[float] = None
    component_quality_scores: Dict[str, float] = field(default_factory=dict)
    consistency_score: Optional[float] = None
    completeness_score: Optional[float] = None
    
    # Descriptive metadata
    title: Optional[str] = None
    description: Optional[str] = None
    creator: Optional[str] = None
    production_company: Optional[str] = None
    series_title: Optional[str] = None
    episode_number: Optional[int] = None
    season_number: Optional[int] = None
    
    # Rights and licensing
    copyright: Optional[str] = None
    license: Optional[str] = None
    usage_rights: Optional[str] = None
    distribution_rights: Optional[str] = None
    
    # Technical metadata
    creation_software: Optional[str] = None
    creation_version: Optional[str] = None
    last_modified: Optional[datetime] = None
    
    # Publication metadata
    publication_date: Optional[datetime] = None
    target_audience: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None
    
    # Analytics metadata
    view_count: int = 0
    download_count: int = 0
    rating: Optional[float] = None
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    analyzed_at: Optional[datetime] = None
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MultimediaFingerprint:
    """
Multimedia fingerprint for content identification and protection"""
    content_id: str
    package_hash: str
    component_hashes: Dict[str, str]  # Component ID -> hash
    cross_modal_hash: str
    synchronization_hash: str
    structural_hash: str
    semantic_hash: str
    component_fingerprints: Dict[str, Any] = field(default_factory=dict)
    relationship_graph: Optional[Dict[str, List[str]]] = None
    temporal_signature: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: float = 0.0
    quality_indicators: Dict[str, float] = field(default_factory=dict)

class MultimediaContentManager:
    """
    Professional multimedia content management system with cross-modal analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Multimedia Content Manager
        
        Args:
            config: Configuration dictionary for multimedia processing
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.MultimediaContentManager")
        self.supported_formats = [fmt.value["ext"] for fmt in MultimediaFormat]
        
        # Initialize content managers
        self._init_content_managers()
        
        # Initialize processing components
        self._init_components()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for multimedia processing"""
        return {
            "max_file_size_mb": 2000,  # 2GB max
            "max_components": 1000,
            "enable_fingerprinting": True,
            "enable_cross_modal_analysis": True,
            "enable_synchronization_analysis": True,
            "enable_quality_analysis": True,
            "enable_relationship_detection": True,
            "temp_extraction_dir": "/tmp/multimedia_extraction",
            "supported_archives": [".zip", ".tar", ".tar.gz"],
            "component_analysis": {
                "audio": True,
                "video": True,
                "image": True,
                "text": True
            },
            "synchronization_threshold": 0.8,
            "quality_threshold": 0.7,
            "batch_processing": True,
            "parallel_processing": True,
            "max_workers": 4
        }
    
    def _init_content_managers(self):
        """Initialize individual content type managers"""
        self.audio_manager = AudioContentManager(self.config.get("audio_config", {}))
        self.video_manager = VideoContentManager(self.config.get("video_config", {}))
        self.image_manager = ImageContentManager(self.config.get("image_config", {}))
        self.text_manager = TextContentManager(self.config.get("text_config", {}))
        
    def _init_components(self):
        """Initialize multimedia processing components"""
        self.logger.info("Initializing Multimedia Content Manager components...")
        
        # Create temporary extraction directory
        self.temp_dir = Path(self.config["temp_extraction_dir"])
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Component type mapping
        self.component_managers = {
            "audio": self.audio_manager,
            "video": self.video_manager,
            "image": self.image_manager,
            "text": self.text_manager
        }
        
        # File extension to content type mapping
        self.extension_mapping = {
            # Audio
            ".mp3": "audio", ".wav": "audio", ".flac": "audio", ".aac": "audio", ".ogg": "audio",
            # Video
            ".mp4": "video", ".avi": "video", ".mov": "video", ".webm": "video", ".mkv": "video",
            # Image
            ".jpg": "image", ".jpeg": "image", ".png": "image", ".tiff": "image", ".webp": "image",
            # Text
            ".txt": "text", ".md": "text", ".pdf": "text", ".docx": "text", ".html": "text"
        }
        
        self.logger.info("Multimedia Content Manager initialized successfully")
    
    async def process_multimedia_package(
        self,
        package_path: Union[str, Path],
        extract_metadata: bool = True,
        generate_fingerprint: bool = True,
        cross_modal_analysis: bool = True,
        synchronization_analysis: bool = True,
        quality_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Process multimedia package with comprehensive cross-modal analysis
        
        Args:
            package_path: Path to multimedia package
            extract_metadata: Whether to extract metadata
            generate_fingerprint: Whether to generate fingerprint
            cross_modal_analysis: Whether to perform cross-modal analysis
            synchronization_analysis: Whether to analyze synchronization
            quality_analysis: Whether to perform quality analysis
            
        Returns:
            Dict containing processed multimedia information
        """
        try:
            package_path = Path(package_path)
            self.logger.info(f"Processing multimedia package: {package_path}")
            
            # Validate package
            if not await self._validate_multimedia_package(package_path):
                raise ValueError(f"Invalid multimedia package: {package_path}")
            
            # Extract package contents
            extraction_dir = await self._extract_package(package_path)
            
            try:
                # Discover and analyze components
                components = await self._discover_components(extraction_dir)
                
                if not components:
                    raise ValueError("No valid multimedia components found in package")
                
                results = {
                    "package_path": str(package_path),
                    "package_size": package_path.stat().st_size,
                    "processing_timestamp": datetime.now(timezone.utc),
                    "total_components": len(components),
                    "extraction_dir": str(extraction_dir)
                }
                
                # Process individual components
                processed_components = await self._process_components(components)
                results["components"] = processed_components
                
                # Extract multimedia metadata
                if extract_metadata:
                    metadata = await self._extract_multimedia_metadata(
                        package_path, processed_components
                    )
                    results["metadata"] = metadata
                
                # Generate multimedia fingerprint
                if generate_fingerprint:
                    fingerprint = await self._generate_multimedia_fingerprint(
                        processed_components, str(package_path)
                    )
                    results["fingerprint"] = fingerprint
                
                # Cross-modal analysis
                if cross_modal_analysis:
                    cross_modal_results = await self._perform_cross_modal_analysis(
                        processed_components
                    )
                    results["cross_modal_analysis"] = cross_modal_results
                
                # Synchronization analysis
                if synchronization_analysis:
                    sync_analysis = await self._analyze_synchronization(processed_components)
                    results["synchronization_analysis"] = sync_analysis
                
                # Quality analysis
                if quality_analysis:
                    quality_metrics = await self._analyze_multimedia_quality(processed_components)
                    results["quality_metrics"] = quality_metrics
                
                # Content classification
                content_type = await self._classify_multimedia_content(
                    processed_components, metadata if extract_metadata else None
                )
                results["content_classification"] = content_type
                
                self.logger.info(f"Multimedia processing completed for: {package_path}")
                return results
                
            finally:
                # Cleanup extraction directory
                await self._cleanup_extraction_dir(extraction_dir)
                
        except Exception as e:
            self.logger.error(f"Failed to process multimedia package {package_path}: {e}")
            raise
    
    async def _validate_multimedia_package(self, package_path: Path) -> bool:
        """Validate multimedia package format and accessibility"""
        try:
            # Check file existence and size
            if not package_path.exists():
                return False
            
            file_size_mb = package_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config["max_file_size_mb"]:
                self.logger.warning(f"Package size {file_size_mb:.2f}MB exceeds limit")
                return False
            
            # Check format support
            if package_path.suffix.lower() not in self.supported_formats:
                return False
            
            # Try to open the archive
            try:
                if package_path.suffix.lower() == '.zip':
                    with zipfile.ZipFile(package_path, 'r') as zf:
                        # Check if archive is valid
                        zf.testzip()
                elif package_path.suffix.lower() in ['.tar', '.tar.gz']:
                    with tarfile.open(package_path, 'r') as tf:
                        # Check if archive is valid
                        tf.getmembers()
                else:
                    # For custom formats, basic existence check
                    pass
                return True
            except Exception:
                return False
                
        except Exception as e:
            self.logger.error(f"Multimedia package validation failed: {e}")
            return False
    
    async def _extract_package(self, package_path: Path) -> Path:
        """Extract multimedia package to temporary directory"""
        try:
            # Create unique extraction directory
            import uuid
            extract_id = str(uuid.uuid4())[:8]
            extraction_dir = self.temp_dir / f"extract_{extract_id}"
            extraction_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract based on format
            if package_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(package_path, 'r') as zf:
                    zf.extractall(extraction_dir)
            elif package_path.suffix.lower() in ['.tar', '.tar.gz']:
                with tarfile.open(package_path, 'r') as tf:
                    tf.extractall(extraction_dir)
            else:
                # For unsupported formats, copy the file
                import shutil
                shutil.copy2(package_path, extraction_dir / package_path.name)
            
            self.logger.info(f"Package extracted to: {extraction_dir}")
            return extraction_dir
            
        except Exception as e:
            self.logger.error(f"Package extraction failed: {e}")
            raise
    
    async def _discover_components(self, extraction_dir: Path) -> List[MultimediaComponent]:
        """Discover multimedia components in extracted directory"""
        try:
            components = []
            component_id_counter = 0
            
            # Recursively find all files
            for file_path in extraction_dir.rglob('*'):
                if file_path.is_file():
                    file_ext = file_path.suffix.lower()
                    
                    # Determine component type
                    component_type = self.extension_mapping.get(file_ext, "unknown")
                    
                    if component_type != "unknown":
                        component = MultimediaComponent(
                            component_id=f"comp_{component_id_counter:04d}",
                            component_type=component_type,
                            file_path=str(file_path),
                            file_size=file_path.stat().st_size,
                            format=file_ext[1:],  # Remove dot
                            processing_status="discovered"
                        )
                        
                        components.append(component)
                        component_id_counter += 1
                        
                        # Limit number of components
                        if len(components) >= self.config["max_components"]:
                            self.logger.warning(f"Component limit reached: {self.config['max_components']}")
                            break
            
            self.logger.info(f"Discovered {len(components)} multimedia components")
            return components
            
        except Exception as e:
            self.logger.error(f"Component discovery failed: {e}")
            return []
    
    async def _process_components(self, components: List[MultimediaComponent]) -> List[MultimediaComponent]:
        """Process individual multimedia components"""
        try:
            processed_components = []
            
            for component in components:
                try:
                    self.logger.info(f"Processing component: {component.component_id} ({component.component_type})")
                    
                    # Get appropriate manager
                    manager = self.component_managers.get(component.component_type)
                    
                    if manager:
                        # Process component based on type
                        if component.component_type == "audio":
                            result = await manager.process_audio_file(component.file_path)
                        elif component.component_type == "video":
                            result = await manager.process_video_file(component.file_path)
                        elif component.component_type == "image":
                            result = await manager.process_image_file(component.file_path)
                        elif component.component_type == "text":
                            result = await manager.process_text_file(component.file_path)
                        else:
                            result = None
                        
                        if result:
                            component.metadata = result.get("metadata")
                            component.fingerprint = result.get("fingerprint")
                            component.processing_status = "completed"
                        else:
                            component.processing_status = "failed"
                    else:
                        component.processing_status = "unsupported"
                    
                    processed_components.append(component)
                    
                except Exception as e:
                    self.logger.error(f"Failed to process component {component.component_id}: {e}")
                    component.processing_status = "error"
                    processed_components.append(component)
            
            successful_count = len([c for c in processed_components if c.processing_status == "completed"])
            self.logger.info(f"Successfully processed {successful_count}/{len(components)} components")
            
            return processed_components
            
        except Exception as e:
            self.logger.error(f"Component processing failed: {e}")
            return components
    
    async def _extract_multimedia_metadata(
        self, 
        package_path: Path, 
        components: List[MultimediaComponent]
    ) -> MultimediaMetadata:
        """Extract comprehensive multimedia metadata"""
        try:
            # Count components by type
            component_types = {}
            total_size = 0
            
            for component in components:
                component_types[component.component_type] = component_types.get(component.component_type, 0) + 1
                total_size += component.file_size
            
            metadata = MultimediaMetadata(
                total_components=len(components),
                component_types=component_types,
                total_size=total_size,
                package_format=package_path.suffix.lower()[1:]
            )
            
            # Determine primary content type
            if component_types:
                primary_type = max(component_types.items(), key=lambda x: x[1])[0]
                metadata.primary_content_type = primary_type
                
                # Secondary types
                secondary_types = [ct for ct, count in component_types.items() if ct != primary_type and count > 0]
                metadata.secondary_content_types = secondary_types
            
            # Extract content themes from components
            themes = set()
            for component in components:
                if component.metadata:
                    # Extract themes from different component types
                    if component.component_type == "text" and hasattr(component.metadata, 'keywords'):
                        themes.update(component.metadata.keywords[:5])
                    elif component.component_type == "image" and hasattr(component.metadata, 'tags'):
                        themes.update(component.metadata.tags[:3])
                    elif component.component_type == "video" and hasattr(component.metadata, 'tags'):
                        themes.update(component.metadata.tags[:3])
            
            metadata.content_themes = list(themes)[:10]  # Limit to 10 themes
            
            # Package-level metadata extraction (from manifest files, etc.)
            await self._extract_package_metadata(package_path, metadata, components)
            
            metadata.analyzed_at = datetime.now(timezone.utc)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Multimedia metadata extraction failed: {e}")
            raise
    
    async def _extract_package_metadata(
        self, 
        package_path: Path, 
        metadata: MultimediaMetadata, 
        components: List[MultimediaComponent]
    ):
        """Extract package-level metadata from manifest files"""
        try:
            # Look for common metadata files
            manifest_files = [
                "manifest.json", "metadata.json", "package.json",
                "info.txt", "readme.txt", "README.md",
                "index.html", "description.xml"
            ]
            
            for component in components:
                file_name = Path(component.file_path).name.lower()
                
                if file_name in manifest_files:
                    try:
                        if file_name.endswith('.json'):
                            # Parse JSON metadata
                            with open(component.file_path, 'r', encoding='utf-8') as f:
                                json_data = json.load(f)
                                
                                metadata.title = json_data.get('title', metadata.title)
                                metadata.description = json_data.get('description', metadata.description)
                                metadata.creator = json_data.get('creator', metadata.creator)
                                metadata.copyright = json_data.get('copyright', metadata.copyright)
                                metadata.license = json_data.get('license', metadata.license)
                                
                                if 'tags' in json_data:
                                    metadata.tags.extend(json_data['tags'])
                                    
                        elif file_name.endswith(('.txt', '.md')):
                            # Parse text-based metadata
                            with open(component.file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                # Simple parsing for common patterns
                                lines = content.split('\n')
                                for line in lines[:20]:  # Check first 20 lines
                                    line = line.strip()
                                    if line.lower().startswith('title:'):
                                        metadata.title = line[6:].strip()
                                    elif line.lower().startswith('author:'):
                                        metadata.creator = line[7:].strip()
                                    elif line.lower().startswith('description:'):
                                        metadata.description = line[12:].strip()
                                        
                    except Exception as e:
                        self.logger.warning(f"Failed to parse metadata file {file_name}: {e}")
            
        except Exception as e:
            self.logger.error(f"Package metadata extraction failed: {e}")
    
    async def _generate_multimedia_fingerprint(
        self, 
        components: List[MultimediaComponent], 
        content_id: str
    ) -> MultimediaFingerprint:
        """Generate comprehensive multimedia fingerprint"""
        try:
            # Package-level hash
            package_data = {
                "component_count": len(components),
                "component_types": {c.component_type for c in components},
                "total_size": sum(c.file_size for c in components)
            }
            package_hash = hashlib.sha256(json.dumps(package_data, sort_keys=True).encode()).hexdigest()
            
            # Component hashes
            component_hashes = {}
            component_fingerprints = {}
            
            for component in components:
                if component.fingerprint:
                    # Use existing fingerprint hash
                    if hasattr(component.fingerprint, 'primary_hash'):
                        comp_hash = component.fingerprint.primary_hash
                    else:
                        comp_hash = hashlib.sha256(component.component_id.encode()).hexdigest()
                    
                    component_hashes[component.component_id] = comp_hash
                    component_fingerprints[component.component_id] = component.fingerprint
            
            # Cross-modal hash (combining different modalities)
            cross_modal_hash = await self._generate_cross_modal_hash(components)
            
            # Synchronization hash (relationships between components)
            synchronization_hash = await self._generate_synchronization_hash(components)
            
            # Structural hash (package organization)
            structural_hash = await self._generate_structural_hash(components)
            
            # Semantic hash (content meaning across modalities)
            semantic_hash = await self._generate_semantic_hash(components)
            
            # Relationship graph
            relationship_graph = await self._build_relationship_graph(components)
            
            # Temporal signature
            temporal_signature = await self._generate_temporal_signature(components)
            
            # Quality indicators
            quality_indicators = {
                "component_count": len(components),
                "modality_diversity": len(set(c.component_type for c in components)),
                "total_content_size": sum(c.file_size for c in components),
                "processing_success_rate": len([c for c in components if c.processing_status == "completed"]) / len(components)
            }
            
            # Confidence score
            confidence_score = min(1.0, (
                quality_indicators["processing_success_rate"] * 0.4 +
                min(quality_indicators["modality_diversity"] / 4, 1.0) * 0.3 +
                min(quality_indicators["component_count"] / 20, 1.0) * 0.3
            ))
            
            fingerprint = MultimediaFingerprint(
                content_id=hashlib.md5(content_id.encode()).hexdigest(),
                package_hash=package_hash,
                component_hashes=component_hashes,
                cross_modal_hash=cross_modal_hash,
                synchronization_hash=synchronization_hash,
                structural_hash=structural_hash,
                semantic_hash=semantic_hash,
                component_fingerprints=component_fingerprints,
                relationship_graph=relationship_graph,
                temporal_signature=temporal_signature,
                confidence_score=confidence_score,
                quality_indicators=quality_indicators
            )
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Multimedia fingerprint generation failed: {e}")
            raise
    
    async def _generate_cross_modal_hash(self, components: List[MultimediaComponent]) -> str:
        """Generate hash representing cross-modal content relationships"""
        try:
            modal_features = {}
            
            for component in components:
                if component.metadata:
                    modal_type = component.component_type
                    
                    # Extract representative features from each modality
                    if modal_type == "audio" and hasattr(component.metadata, 'duration'):
                        modal_features.setdefault('audio', []).append({
                            'duration': component.metadata.duration,
                            'sample_rate': getattr(component.metadata, 'sample_rate', 0)
                        })
                    elif modal_type == "video" and hasattr(component.metadata, 'duration'):
                        modal_features.setdefault('video', []).append({
                            'duration': component.metadata.duration,
                            'resolution': f"{component.metadata.width}x{component.metadata.height}"
                        })
                    elif modal_type == "image" and hasattr(component.metadata, 'width'):
                        modal_features.setdefault('image', []).append({
                            'dimensions': f"{component.metadata.width}x{component.metadata.height}",
                            'format': component.metadata.format
                        })
                    elif modal_type == "text" and hasattr(component.metadata, 'word_count'):
                        modal_features.setdefault('text', []).append({
                            'word_count': component.metadata.word_count,
                            'language': getattr(component.metadata, 'language', 'unknown')
                        })
            
            cross_modal_str = json.dumps(modal_features, sort_keys=True)
            return hashlib.sha256(cross_modal_str.encode()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Cross-modal hash generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _generate_synchronization_hash(self, components: List[MultimediaComponent]) -> str:
        """Generate hash representing synchronization between components"""
        try:
            sync_features = []
            
            # Look for temporal synchronization patterns
            audio_components = [c for c in components if c.component_type == "audio"]
            video_components = [c for c in components if c.component_type == "video"]
            
            # Check duration alignment
            if audio_components and video_components:
                for audio_comp in audio_components:
                    for video_comp in video_components:
                        if (audio_comp.metadata and video_comp.metadata and
                            hasattr(audio_comp.metadata, 'duration') and hasattr(video_comp.metadata, 'duration')):
                            
                            duration_diff = abs(audio_comp.metadata.duration - video_comp.metadata.duration)
                            sync_features.append({
                                'audio_id': audio_comp.component_id,
                                'video_id': video_comp.component_id,
                                'duration_diff': duration_diff,
                                'sync_likely': duration_diff < 1.0  # Within 1 second
                            })
            
            # Check naming patterns for relationships
            for i, comp1 in enumerate(components):
                for comp2 in components[i+1:]:
                    name1 = Path(comp1.file_path).stem
                    name2 = Path(comp2.file_path).stem
                    
                    # Simple name similarity check
                    common_prefix = len(os.path.commonprefix([name1, name2]))
                    if common_prefix > 3:  # Significant common prefix
                        sync_features.append({
                            'comp1_id': comp1.component_id,
                            'comp2_id': comp2.component_id,
                            'name_similarity': common_prefix,
                            'related_likely': True
                        })
            
            sync_str = json.dumps(sync_features, sort_keys=True)
            return hashlib.sha256(sync_str.encode()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Synchronization hash generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _generate_structural_hash(self, components: List[MultimediaComponent]) -> str:
        """Generate hash representing package structure"""
        try:
            # Extract directory structure
            directories = set()
            file_patterns = []
            
            for component in components:
                file_path = Path(component.file_path)
                
                # Directory structure
                if file_path.parent.name:
                    directories.add(file_path.parent.name)
                
                # File naming patterns
                file_patterns.append({
                    'name': file_path.stem,
                    'extension': file_path.suffix,
                    'type': component.component_type
                })
            
            structural_data = {
                'directories': sorted(list(directories)),
                'file_count_by_type': {ct: len([c for c in components if c.component_type == ct]) 
                                     for ct in set(c.component_type for c in components)},
                'total_files': len(components)
            }
            
            structural_str = json.dumps(structural_data, sort_keys=True)
            return hashlib.sha256(structural_str.encode()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Structural hash generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _generate_semantic_hash(self, components: List[MultimediaComponent]) -> str:
        """Generate hash representing semantic content across modalities"""
        try:
            semantic_features = []
            
            # Extract semantic information from each component
            for component in components:
                if component.metadata:
                    if component.component_type == "text" and hasattr(component.metadata, 'keywords'):
                        semantic_features.extend(component.metadata.keywords[:10])
                    elif component.component_type == "image" and hasattr(component.metadata, 'content_type'):
                        semantic_features.append(f"image_{component.metadata.content_type}")
                    elif component.component_type == "video" and hasattr(component.metadata, 'content_type'):
                        semantic_features.append(f"video_{component.metadata.content_type}")
                    elif component.component_type == "audio" and hasattr(component.metadata, 'content_type'):
                        semantic_features.append(f"audio_{component.metadata.content_type}")
            
            # Remove duplicates and sort
            semantic_features = sorted(list(set(semantic_features)))
            
            semantic_str = json.dumps(semantic_features, sort_keys=True)
            return hashlib.sha256(semantic_str.encode()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Semantic hash generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _build_relationship_graph(self, components: List[MultimediaComponent]) -> Dict[str, List[str]]:
        """Build relationship graph between components"""
        try:
            relationships = {}
            
            # Initialize empty relationships for all components
            for component in components:
                relationships[component.component_id] = []
            
            # Detect relationships based on various criteria
            for i, comp1 in enumerate(components):
                for comp2 in components[i+1:]:
                    
                    # Name-based relationships
                    name1 = Path(comp1.file_path).stem
                    name2 = Path(comp2.file_path).stem
                    
                    if len(os.path.commonprefix([name1, name2])) > 3:
                        relationships[comp1.component_id].append(comp2.component_id)
                        relationships[comp2.component_id].append(comp1.component_id)
                    
                    # Duration-based relationships (for temporal media)
                    if (comp1.component_type in ["audio", "video"] and 
                        comp2.component_type in ["audio", "video"] and
                        comp1.metadata and comp2.metadata and
                        hasattr(comp1.metadata, 'duration') and hasattr(comp2.metadata, 'duration')):
                        
                        duration_diff = abs(comp1.metadata.duration - comp2.metadata.duration)
                        if duration_diff < 2.0:  # Within 2 seconds
                            relationships[comp1.component_id].append(comp2.component_id)
                            relationships[comp2.component_id].append(comp1.component_id)
            
            return relationships
            
        except Exception as e:
            self.logger.error(f"Relationship graph building failed: {e}")
            return {}
    
    async def _generate_temporal_signature(self, components: List[MultimediaComponent]) -> Optional[str]:
        """Generate temporal signature for time-based components"""
        try:
            temporal_components = [c for c in components if c.component_type in ["audio", "video"]]
            
            if not temporal_components:
                return None
            
            temporal_data = []
            for component in temporal_components:
                if component.metadata and hasattr(component.metadata, 'duration'):
                    temporal_data.append({
                        'component_id': component.component_id,
                        'type': component.component_type,
                        'duration': component.metadata.duration
                    })
            
            if temporal_data:
                temporal_str = json.dumps(temporal_data, sort_keys=True)
                return hashlib.sha256(temporal_str.encode()).hexdigest()[:32]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Temporal signature generation failed: {e}")
            return None
    
    async def _perform_cross_modal_analysis(self, components: List[MultimediaComponent]) -> Dict[str, Any]:
        """Perform cross-modal content analysis"""
        try:
            analysis_results = {
                "modality_distribution": {},
                "content_alignment": {},
                "cross_modal_features": {},
                "similarity_scores": {}
            }
            
            # Analyze modality distribution
            modality_counts = {}
            for component in components:
                modality_counts[component.component_type] = modality_counts.get(component.component_type, 0) + 1
            
            analysis_results["modality_distribution"] = modality_counts
            
            # Content alignment analysis
            audio_components = [c for c in components if c.component_type == "audio" and c.metadata]
            video_components = [c for c in components if c.component_type == "video" and c.metadata]
            
            if audio_components and video_components:
                alignment_scores = []
                for audio_comp in audio_components:
                    for video_comp in video_components:
                        if (hasattr(audio_comp.metadata, 'duration') and 
                            hasattr(video_comp.metadata, 'duration')):
                            
                            duration_diff = abs(audio_comp.metadata.duration - video_comp.metadata.duration)
                            alignment_score = max(0, 1 - (duration_diff / 10))  # Normalize
                            alignment_scores.append(alignment_score)
                
                if alignment_scores:
                    analysis_results["content_alignment"]["audio_video_sync"] = np.mean(alignment_scores)
            
            # Cross-modal feature extraction
            text_keywords = []
            image_objects = []
            
            for component in components:
                if component.component_type == "text" and component.metadata:
                    if hasattr(component.metadata, 'keywords'):
                        text_keywords.extend(component.metadata.keywords[:5])
                elif component.component_type == "image" and component.metadata:
                    if hasattr(component.metadata, 'objects_detected'):
                        image_objects.extend(component.metadata.objects_detected[:5])
            
            analysis_results["cross_modal_features"] = {
                "text_keywords": list(set(text_keywords))[:20],
                "image_objects": list(set(image_objects))[:20]
            }
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Cross-modal analysis failed: {e}")
            return {}
    
    async def _analyze_synchronization(self, components: List[MultimediaComponent]) -> Dict[str, Any]:
        """Analyze synchronization between multimedia components"""
        try:
            sync_analysis = {
                "temporal_sync": {},
                "spatial_coherence": {},
                "semantic_alignment": {},
                "overall_sync_score": 0.0
            }
            
            # Temporal synchronization analysis
            temporal_components = [c for c in components if c.component_type in ["audio", "video"]]
            
            if len(temporal_components) >= 2:
                sync_scores = []
                
                for i, comp1 in enumerate(temporal_components):
                    for comp2 in temporal_components[i+1:]:
                        if (comp1.metadata and comp2.metadata and
                            hasattr(comp1.metadata, 'duration') and hasattr(comp2.metadata, 'duration')):
                            
                            duration1 = comp1.metadata.duration
                            duration2 = comp2.metadata.duration
                            
                            # Calculate synchronization score
                            if max(duration1, duration2) > 0:
                                sync_score = 1 - abs(duration1 - duration2) / max(duration1, duration2)
                                sync_scores.append(max(0, sync_score))
                
                if sync_scores:
                    sync_analysis["temporal_sync"]["average_score"] = np.mean(sync_scores)
                    sync_analysis["temporal_sync"]["component_pairs"] = len(sync_scores)
            
            # Spatial coherence (for visual components)
            visual_components = [c for c in components if c.component_type in ["image", "video"]]
            
            if len(visual_components) >= 2:
                coherence_scores = []
                
                for i, comp1 in enumerate(visual_components):
                    for comp2 in visual_components[i+1:]:
                        if (comp1.metadata and comp2.metadata and
                            hasattr(comp1.metadata, 'width') and hasattr(comp2.metadata, 'width')):
                            
                            # Compare aspect ratios
                            ratio1 = comp1.metadata.width / max(comp1.metadata.height, 1)
                            ratio2 = comp2.metadata.width / max(comp2.metadata.height, 1)
                            
                            ratio_diff = abs(ratio1 - ratio2)
                            coherence_score = max(0, 1 - ratio_diff)
                            coherence_scores.append(coherence_score)
                
                if coherence_scores:
                    sync_analysis["spatial_coherence"]["average_score"] = np.mean(coherence_scores)
            
            # Overall synchronization score
            scores = []
            if "average_score" in sync_analysis["temporal_sync"]:
                scores.append(sync_analysis["temporal_sync"]["average_score"])
            if "average_score" in sync_analysis["spatial_coherence"]:
                scores.append(sync_analysis["spatial_coherence"]["average_score"])
            
            if scores:
                sync_analysis["overall_sync_score"] = np.mean(scores)
            
            return sync_analysis
            
        except Exception as e:
            self.logger.error(f"Synchronization analysis failed: {e}")
            return {}
    
    async def _analyze_multimedia_quality(self, components: List[MultimediaComponent]) -> Dict[str, float]:
        """Analyze overall multimedia quality"""
        try:
            quality_metrics = {
                "component_quality_scores": {},
                "consistency_score": 0.0,
                "completeness_score": 0.0,
                "overall_quality": 0.0
            }
            
            # Collect individual component quality scores
            valid_components = 0
            total_quality = 0.0
            
            for component in components:
                if component.processing_status == "completed" and component.metadata:
                    component_quality = 0.5  # Default
                    
                    # Extract quality score based on component type
                    if hasattr(component.metadata, 'quality_score'):
                        component_quality = component.metadata.quality_score
                    elif hasattr(component.metadata, 'overall_quality'):
                        component_quality = component.metadata.overall_quality
                    
                    quality_metrics["component_quality_scores"][component.component_id] = component_quality
                    total_quality += component_quality
                    valid_components += 1
            
            # Average component quality
            if valid_components > 0:
                avg_component_quality = total_quality / valid_components
            else:
                avg_component_quality = 0.0
            
            # Consistency score (how similar are the quality scores)
            if len(quality_metrics["component_quality_scores"]) > 1:
                scores = list(quality_metrics["component_quality_scores"].values())
                consistency = 1.0 - (np.std(scores) / (np.mean(scores) + 1e-10))
                quality_metrics["consistency_score"] = max(0.0, min(1.0, consistency))
            else:
                quality_metrics["consistency_score"] = 1.0
            
            # Completeness score (ratio of successfully processed components)
            if components:
                completed_count = len([c for c in components if c.processing_status == "completed"])
                quality_metrics["completeness_score"] = completed_count / len(components)
            else:
                quality_metrics["completeness_score"] = 0.0
            
            # Overall quality score
            quality_metrics["overall_quality"] = (
                avg_component_quality * 0.5 +
                quality_metrics["consistency_score"] * 0.25 +
                quality_metrics["completeness_score"] * 0.25
            )
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Multimedia quality analysis failed: {e}")
            return {"overall_quality": 0.5, "error": str(e)}
    
    async def _classify_multimedia_content(
        self, 
        components: List[MultimediaComponent], 
        metadata: Optional[MultimediaMetadata] = None
    ) -> MultimediaContentType:
        """Classify multimedia content type based on components and structure"""
        try:
            # Count components by type
            component_counts = {}
            for component in components:
                component_counts[component.component_type] = component_counts.get(component.component_type, 0) + 1
            
            # Music album detection
            if (component_counts.get("audio", 0) >= 3 and 
                component_counts.get("image", 0) >= 1 and
                component_counts.get("text", 0) >= 1):
                return MultimediaContentType.MUSIC_ALBUM
            
            # Documentary package detection
            if (component_counts.get("video", 0) >= 1 and
                component_counts.get("text", 0) >= 1):
                return MultimediaContentType.DOCUMENTARY_PACKAGE
            
            # Tutorial series detection
            if (component_counts.get("video", 0) >= 2 and
                component_counts.get("text", 0) >= 1):
                return MultimediaContentType.TUTORIAL_SERIES
            
            # Portfolio detection (multiple images/videos)
            if (component_counts.get("image", 0) >= 5 or
                component_counts.get("video", 0) >= 3):
                return MultimediaContentType.PORTFOLIO
            
            # Enhanced eBook detection
            if (component_counts.get("text", 0) >= 1 and
                (component_counts.get("image", 0) >= 3 or component_counts.get("audio", 0) >= 1)):
                return MultimediaContentType.EBOOK_ENHANCED
            
            # Presentation detection
            if (component_counts.get("image", 0) >= 3 and
                component_counts.get("text", 0) >= 1):
                # Check for slide-like naming patterns
                slide_patterns = any(
                    "slide" in Path(comp.file_path).name.lower() or
                    "page" in Path(comp.file_path).name.lower()
                    for comp in components
                )
                if slide_patterns:
                    return MultimediaContentType.PRESENTATION
            
            # Podcast episode detection
            if (component_counts.get("audio", 0) == 1 and
                component_counts.get("text", 0) >= 1):
                return MultimediaContentType.PODCAST_EPISODE
            
            # Course material detection
            if (component_counts.get("video", 0) >= 1 and
                component_counts.get("text", 0) >= 2):
                # Look for educational keywords
                educational_keywords = ["lesson", "course", "chapter", "exercise"]
                has_educational_content = any(
                    any(keyword in Path(comp.file_path).name.lower() for keyword in educational_keywords)
                    for comp in components
                )
                if has_educational_content:
                    return MultimediaContentType.COURSE_MATERIAL
            
            # Marketing campaign detection
            if (component_counts.get("image", 0) >= 2 and
                component_counts.get("video", 0) >= 1):
                marketing_keywords = ["ad", "promo", "campaign", "brand"]
                has_marketing_content = any(
                    any(keyword in Path(comp.file_path).name.lower() for keyword in marketing_keywords)
                    for comp in components
                )
                if has_marketing_content:
                    return MultimediaContentType.MARKETING_CAMPAIGN
            
            # Default classification based on dominant content type
            if metadata and metadata.primary_content_type:
                primary_type = metadata.primary_content_type
                
                if primary_type == "video":
                    return MultimediaContentType.DOCUMENTARY_PACKAGE
                elif primary_type == "audio":
                    return MultimediaContentType.MUSIC_ALBUM
                elif primary_type == "image":
                    return MultimediaContentType.PORTFOLIO
                elif primary_type == "text":
                    return MultimediaContentType.EBOOK_ENHANCED
            
            # Final fallback
            return MultimediaContentType.INTERACTIVE_MEDIA
            
        except Exception as e:
            self.logger.error(f"Multimedia content classification failed: {e}")
            return MultimediaContentType.INTERACTIVE_MEDIA  # Default fallback
    
    async def _cleanup_extraction_dir(self, extraction_dir: Path):
        """Clean up temporary extraction directory"""
        try:
            import shutil
            if extraction_dir.exists():
                shutil.rmtree(extraction_dir)
                self.logger.info(f"Cleaned up extraction directory: {extraction_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup extraction directory: {e}")
    
    async def store_content(self, multimedia_content: Dict[str, Any]) -> str:
        """Store processed multimedia content in database"""
        try:
            # Generate unique content ID
            content_id = hashlib.sha256(
                f"{multimedia_content['package_path']}{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            # Here you would implement database storage
            # For now, return the generated ID
            
            self.logger.info(f"Multimedia content stored with ID: {content_id}")
            return content_id
            
        except Exception as e:
            self.logger.error(f"Failed to store multimedia content: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported multimedia formats"""
        return [fmt.value["ext"] for fmt in MultimediaFormat]
    
    def get_format_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific multimedia format"""
        for fmt in MultimediaFormat:
            if fmt.value["ext"] == f".{format_name.lower()}" or fmt.name.lower() == format_name.lower():
                return fmt.value
        return None
