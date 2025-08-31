"""IA Influencer Agent - Quality Assurance Filters
===============================================

Ultra-advanced professional quality assurance system for content validation.
Implements enterprise-grade QA filtering with AI-powered assessment.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""
import asyncio
import logging
import time
import hashlib
import statistics
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from pathlib import Path
import json
import re

from .config import FilterConfigManager
from .filter_engine import FilterResponse, FilterResult, FilterType, ContentItem


class QualityDimension(Enum):
    """Quality assessment dimensions."""    TECHNICAL_QUALITY = "technical_quality"
    CONTENT_QUALITY = "content_quality"
    METADATA_QUALITY = "metadata_quality"
    STRUCTURAL_QUALITY = "structural_quality"
    AUTHENTICITY = "authenticity"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    ORIGINALITY = "originality"


class QualityLevel(Enum):
    """Quality levels for content assessment."""    EXCEPTIONAL = "exceptional"  # 90-100%
    HIGH = "high"               # 80-89%
    GOOD = "good"               # 70-79%
    ACCEPTABLE = "acceptable"   # 60-69%
    POOR = "poor"               # 40-59%
    UNACCEPTABLE = "unacceptable"  # 0-39%


@dataclass
class QualityMetrics:
    """Quality assessment metrics."""    overall_score: float = 0.0
    dimension_scores: Dict[str, float] = None
    quality_level: QualityLevel = QualityLevel.POOR
    improvement_suggestions: List[str] = None
    critical_issues: List[str] = None
    quality_indicators: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dimension_scores is None:
            self.dimension_scores = {}
        if self.improvement_suggestions is None:
            self.improvement_suggestions = []
        if self.critical_issues is None:
            self.critical_issues = []
        if self.quality_indicators is None:
            self.quality_indicators = {}


class TechnicalQualityAnalyzer:
    """Analyzes technical quality aspects of content."""    
    def __init__(self):
        """Initialize technical quality analyzer."""        self.logger = logging.getLogger(__name__)
    
    async def analyze_technical_quality(self, content_item: ContentItem) -> Dict[str, float]:
        """Analyze technical quality aspects."""        try:
            technical_scores = {}
            
            # File integrity assessment
            technical_scores["file_integrity"] = await self._assess_file_integrity(content_item)
            
            # Format compliance
            technical_scores["format_compliance"] = await self._assess_format_compliance(content_item)
            
            # Encoding quality
            technical_scores["encoding_quality"] = await self._assess_encoding_quality(content_item)
            
            # Metadata consistency
            technical_scores["metadata_consistency"] = await self._assess_metadata_consistency(content_item)
            
            # File structure validation
            technical_scores["structure_validation"] = await self._validate_file_structure(content_item)
            
            return technical_scores
            
        except Exception as e:
            self.logger.error(f"Technical quality analysis failed: {str(e)}")
            return {"error": 0.0}
    
    async def _assess_file_integrity(self, content_item: ContentItem) -> float:
        """Assess file integrity and corruption indicators."""        try:
            score = 1.0
            
            # Check file size reasonableness
            if content_item.size:
                if content_item.size == 0:
                    score = 0.0
                elif content_item.size < 1024:  # Very small files might be corrupted
                    score -= 0.3
                elif content_item.size > 1024 * 1024 * 1024:  # Very large files
                    score -= 0.1
            
            # Check filename validity
            if content_item.filename:
                if not re.match(r'^[a-zA-Z0-9._\-\s\(\)\[\]]+$', content_item.filename):
                    score -= 0.2
                
                # Check for suspicious patterns
                if re.search(r'corrupt|broken|invalid|error', content_item.filename.lower()):
                    score -= 0.5
            
            return max(0.0, score)
            
        except Exception as e:
            self.logger.warning(f"File integrity assessment failed: {str(e)}")
            return 0.5
    
    async def _assess_format_compliance(self, content_item: ContentItem) -> float:
        """Assess format compliance and standard adherence."""        try:
            score = 0.8  # Base score
            
            # Check MIME type consistency
            if content_item.mime_type and content_item.filename:
                expected_extension = self._get_expected_extension(content_item.mime_type)
                actual_extension = Path(content_item.filename).suffix.lower()
                
                if expected_extension and actual_extension == expected_extension:
                    score += 0.2
                elif expected_extension and actual_extension != expected_extension:
                    score -= 0.3
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"Format compliance assessment failed: {str(e)}")
            return 0.5
    
    def _get_expected_extension(self, mime_type: str) -> Optional[str]:
        """Get expected file extension for MIME type."""        mime_extensions = {
            "audio/mpeg": ".mp3",
            "audio/wav": ".wav",
            "audio/flac": ".flac",
            "audio/aac": ".aac",
            "video/mp4": ".mp4",
            "video/avi": ".avi",
            "video/quicktime": ".mov",
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "text/plain": ".txt",
            "application/pdf": ".pdf"
        }
        return mime_extensions.get(mime_type)
    
    async def _assess_encoding_quality(self, content_item: ContentItem) -> float:
        """Assess encoding quality and compression artifacts."""        try:
            score = 0.7  # Base score
            
            # Analyze metadata for encoding information
            if content_item.metadata:
                bitrate = content_item.metadata.get("bitrate")
                if bitrate:
                    if isinstance(bitrate, (int, float)):
                        if bitrate >= 320000:  # High quality
                            score += 0.3
                        elif bitrate >= 128000:  # Acceptable quality
                            score += 0.1
                        elif bitrate < 96000:  # Low quality
                            score -= 0.3
                
                # Check for compression settings
                compression = content_item.metadata.get("compression", "").lower()
                if "lossless" in compression:
                    score += 0.2
                elif "high" in compression:
                    score += 0.1
                elif "low" in compression:
                    score -= 0.2
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"Encoding quality assessment failed: {str(e)}")
            return 0.5
    
    async def _assess_metadata_consistency(self, content_item: ContentItem) -> float:
        """Assess metadata consistency and completeness."""        try:
            if not content_item.metadata:
                return 0.2  # Low score for missing metadata
            
            score = 0.5  # Base score
            metadata = content_item.metadata
            
            # Check metadata completeness
            essential_fields = ["title", "artist", "duration", "format"]
            present_fields = sum(1 for field in essential_fields if field in metadata and metadata[field])
            completeness_score = present_fields / len(essential_fields)
            score += completeness_score * 0.3
            
            # Check metadata consistency
            if "duration" in metadata and "size" in metadata:
                # Basic consistency check for audio/video
                try:
                    duration = float(metadata["duration"])
                    size = int(metadata["size"])
                    if duration > 0 and size > 0:
                        # Rough bitrate estimation
                        estimated_bitrate = (size * 8) / duration
                        if 8000 <= estimated_bitrate <= 5000000:  # Reasonable range
                            score += 0.2
                except (ValueError, TypeError):
                    score -= 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"Metadata consistency assessment failed: {str(e)}")
            return 0.3
    
    async def _validate_file_structure(self, content_item: ContentItem) -> float:
        """Validate file structure and organization."""        try:
            score = 0.8  # Base score
            
            # Validate filename structure
            if content_item.filename:
                filename = content_item.filename
                
                # Check for good naming conventions
                if re.match(r'^[A-Z][a-z].*', filename):  # Starts with capital
                    score += 0.1
                
                # Check for descriptive naming
                if len(Path(filename).stem) >= 5:  # Meaningful length
                    score += 0.1
                
                # Penalize generic names
                generic_patterns = [r'^track\d+', r'^audio\d+', r'^video\d+', r'^untitled']
                if any(re.match(pattern, filename.lower()) for pattern in generic_patterns):
                    score -= 0.3
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"File structure validation failed: {str(e)}")
            return 0.5


class ContentQualityAnalyzer:
    """Analyzes content quality aspects."""    
    def __init__(self):
        """Initialize content quality analyzer."""        self.logger = logging.getLogger(__name__)
    
    async def analyze_content_quality(self, content_item: ContentItem) -> Dict[str, float]:
        """Analyze content quality aspects."""        try:
            content_scores = {}
            
            # Originality assessment
            content_scores["originality"] = await self._assess_originality(content_item)
            
            # Content richness
            content_scores["content_richness"] = await self._assess_content_richness(content_item)
            
            # Artistic value
            content_scores["artistic_value"] = await self._assess_artistic_value(content_item)
            
            # Professional quality
            content_scores["professional_quality"] = await self._assess_professional_quality(content_item)
            
            # Content coherence
            content_scores["coherence"] = await self._assess_content_coherence(content_item)
            
            return content_scores
            
        except Exception as e:
            self.logger.error(f"Content quality analysis failed: {str(e)}")
            return {"error": 0.0}
    
    async def _assess_originality(self, content_item: ContentItem) -> float:
        """Assess content originality and uniqueness."""        try:
            score = 0.7  # Base originality score
            
            # Check filename for originality indicators
            if content_item.filename:
                filename = content_item.filename.lower()
                
                # Penalize copy/remix indicators
                copy_indicators = ["copy", "remix", "cover", "version", "edit", "mix"]
                penalty = sum(0.1 for indicator in copy_indicators if indicator in filename)
                score -= min(penalty, 0.4)
                
                # Reward original naming
                if not re.search(r'\d{8,}', filename):  # No long numbers (generated names)
                    score += 0.1
                
                if len(set(filename.split())) > 2:  # Multiple unique words
                    score += 0.1
            
            # Check metadata for originality
            if content_item.metadata:
                if content_item.metadata.get("artist") and content_item.metadata.get("title"):
                    score += 0.1  # Has original attribution
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"Originality assessment failed: {str(e)}")
            return 0.5
    
    async def _assess_content_richness(self, content_item: ContentItem) -> float:
        """Assess content richness and depth."""        try:
            score = 0.5  # Base score
            
            # File size as richness indicator
            if content_item.size:
                if content_item.size > 10 * 1024 * 1024:  # > 10MB
                    score += 0.2
                elif content_item.size > 1 * 1024 * 1024:  # > 1MB
                    score += 0.1
                elif content_item.size < 100 * 1024:  # < 100KB
                    score -= 0.2
            
            # Metadata richness
            if content_item.metadata:
                metadata_fields = len(content_item.metadata)
                if metadata_fields >= 10:
                    score += 0.3
                elif metadata_fields >= 5:
                    score += 0.2
                elif metadata_fields >= 3:
                    score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"Content richness assessment failed: {str(e)}")
            return 0.5
    
    async def _assess_artistic_value(self, content_item: ContentItem) -> float:
        """Assess artistic and creative value."""        try:
            score = 0.6  # Base artistic score
            
            # Genre and style indicators
            if content_item.metadata:
                genre = content_item.metadata.get("genre", "").lower()
                
                # Artistic genres get higher scores
                artistic_genres = [
                    "jazz", "classical", "experimental", "ambient", "folk",
                    "indie", "alternative", "progressive", "world"
                ]
                
                if any(ag in genre for ag in artistic_genres):
                    score += 0.2
                
                # Commercial genres get moderate scores
                commercial_genres = ["pop", "rock", "hip-hop", "electronic", "country"]
                if any(cg in genre for cg in commercial_genres):
                    score += 0.1
            
            # Title creativity assessment
            if content_item.filename:
                title = Path(content_item.filename).stem
                
                # Creative title indicators
                if len(title.split()) >= 3:  # Multi-word titles
                    score += 0.1
                
                if re.search(r'[^\w\s]', title):  # Contains special characters
                    score += 0.05
                
                # Penalize generic titles
                generic_titles = ["untitled", "track", "song", "audio", "video", "new"]
                if any(gt in title.lower() for gt in generic_titles):
                    score -= 0.3
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"Artistic value assessment failed: {str(e)}")
            return 0.5
    
    async def _assess_professional_quality(self, content_item: ContentItem) -> float:
        """Assess professional production quality."""        try:
            score = 0.5  # Base score
            
            # Professional metadata indicators
            if content_item.metadata:
                metadata = content_item.metadata
                
                # Professional fields
                professional_fields = [
                    "producer", "engineer", "studio", "label", "isrc", "catalog"
                ]
                professional_count = sum(1 for field in professional_fields 
                                       if field in metadata and metadata[field])
                score += min(professional_count * 0.1, 0.3)
                
                # High quality indicators
                if metadata.get("bitrate"):
                    try:
                        bitrate = int(metadata["bitrate"])
                        if bitrate >= 320000:  # Professional quality
                            score += 0.2
                        elif bitrate >= 192000:  # Good quality
                            score += 0.1
                    except (ValueError, TypeError):
                        pass
                
                # Sample rate for audio
                if metadata.get("sample_rate"):
                    try:
                        sample_rate = int(metadata["sample_rate"])
                        if sample_rate >= 48000:  # Professional
                            score += 0.1
                        elif sample_rate >= 44100:  # Standard
                            score += 0.05
                    except (ValueError, TypeError):
                        pass
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"Professional quality assessment failed: {str(e)}")
            return 0.5
    
    async def _assess_content_coherence(self, content_item: ContentItem) -> float:
        """Assess content coherence and consistency."""        try:
            score = 0.8  # Base coherence score
            
            # Filename-metadata consistency
            if content_item.filename and content_item.metadata:
                filename_lower = content_item.filename.lower()
                
                # Check if title matches filename
                title = content_item.metadata.get("title", "").lower()
                if title and title in filename_lower:
                    score += 0.1
                
                # Check if artist matches filename
                artist = content_item.metadata.get("artist", "").lower()
                if artist and artist in filename_lower:
                    score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"Content coherence assessment failed: {str(e)}")
            return 0.6


class QualityAssuranceEngine:
    """Main quality assurance engine."""    
    def __init__(self, config_manager: FilterConfigManager):
        """Initialize quality assurance engine."""        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.technical_analyzer = TechnicalQualityAnalyzer()
        self.content_analyzer = ContentQualityAnalyzer()
    
    async def perform_quality_assessment(self, content_item: ContentItem) -> QualityMetrics:
        """Perform comprehensive quality assessment."""        try:
            start_time = time.time()
            
            # Analyze different quality dimensions
            technical_scores = await self.technical_analyzer.analyze_technical_quality(content_item)
            content_scores = await self.content_analyzer.analyze_content_quality(content_item)
            
            # Calculate dimension scores
            dimension_scores = {
                QualityDimension.TECHNICAL_QUALITY.value: statistics.mean(technical_scores.values()) if technical_scores else 0.5,
                QualityDimension.CONTENT_QUALITY.value: statistics.mean(content_scores.values()) if content_scores else 0.5,
                QualityDimension.METADATA_QUALITY.value: await self._assess_metadata_quality(content_item),
                QualityDimension.STRUCTURAL_QUALITY.value: await self._assess_structural_quality(content_item),
                QualityDimension.AUTHENTICITY.value: await self._assess_authenticity(content_item),
                QualityDimension.COMPLETENESS.value: await self._assess_completeness(content_item),
                QualityDimension.CONSISTENCY.value: await self._assess_consistency(content_item),
                QualityDimension.ORIGINALITY.value: content_scores.get("originality", 0.5)
            }
            
            # Calculate overall score
            overall_score = statistics.mean(dimension_scores.values())
            
            # Determine quality level
            quality_level = self._determine_quality_level(overall_score)
            
            # Generate improvement suggestions
            suggestions = await self._generate_improvement_suggestions(dimension_scores, technical_scores, content_scores)
            
            # Identify critical issues
            critical_issues = await self._identify_critical_issues(dimension_scores, technical_scores, content_scores)
            
            # Create quality indicators
            quality_indicators = {
                "assessment_time": time.time() - start_time,
                "technical_breakdown": technical_scores,
                "content_breakdown": content_scores,
                "overall_rating": quality_level.value,
                "recommendation": await self._generate_quality_recommendation(overall_score)
            }
            
            return QualityMetrics(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                quality_level=quality_level,
                improvement_suggestions=suggestions,
                critical_issues=critical_issues,
                quality_indicators=quality_indicators
            )
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {str(e)}")
            return QualityMetrics(
                overall_score=0.0,
                quality_level=QualityLevel.UNACCEPTABLE,
                critical_issues=[f"Assessment failed: {str(e)}"]
            )
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score."""        if score >= 0.9:
            return QualityLevel.EXCEPTIONAL
        elif score >= 0.8:
            return QualityLevel.HIGH
        elif score >= 0.7:
            return QualityLevel.GOOD
        elif score >= 0.6:
            return QualityLevel.ACCEPTABLE
        elif score >= 0.4:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE
    
    async def _assess_metadata_quality(self, content_item: ContentItem) -> float:
        """Assess metadata quality specifically."""        if not content_item.metadata:
            return 0.1
        
        score = 0.5
        metadata = content_item.metadata
        
        # Essential fields check
        essential_fields = ["title", "artist", "duration"]
        essential_score = sum(1 for field in essential_fields if field in metadata and metadata[field])
        score += (essential_score / len(essential_fields)) * 0.3
        
        # Extended fields check
        extended_fields = ["genre", "album", "year", "bitrate", "format"]
        extended_score = sum(1 for field in extended_fields if field in metadata and metadata[field])
        score += (extended_score / len(extended_fields)) * 0.2
        
        return min(1.0, score)
    
    async def _assess_structural_quality(self, content_item: ContentItem) -> float:
        """Assess structural quality of content."""        score = 0.7
        
        # File naming structure
        if content_item.filename:
            filename = content_item.filename
            if " - " in filename:  # Good structure indicator
                score += 0.1
            if re.match(r'^[A-Z]', filename):  # Proper capitalization
                score += 0.1
            if not re.search(r'[^\w\s\-\(\)\[\]\.]', filename):  # Clean characters
                score += 0.1
        
        return min(1.0, score)
    
    async def _assess_authenticity(self, content_item: ContentItem) -> float:
        """Assess content authenticity."""        score = 0.7
        
        if content_item.filename:
            filename = content_item.filename.lower()
            
            # Authentic naming patterns
            if not re.search(r'copy|fake|duplicate|clone', filename):
                score += 0.1
            
            # Original content indicators
            if content_item.metadata and content_item.metadata.get("artist"):
                score += 0.2
        
        return min(1.0, score)
    
    async def _assess_completeness(self, content_item: ContentItem) -> float:
        """Assess content completeness."""        score = 0.5
        
        # File size completeness indicator
        if content_item.size and content_item.size > 1024:
            score += 0.3
        
        # Metadata completeness
        if content_item.metadata and len(content_item.metadata) >= 5:
            score += 0.2
        
        return min(1.0, score)
    
    async def _assess_consistency(self, content_item: ContentItem) -> float:
        """Assess internal consistency."""        score = 0.8
        
        # Filename-metadata consistency
        if (content_item.filename and content_item.metadata and 
            content_item.metadata.get("title")):
            filename_words = set(re.findall(r'\w+', content_item.filename.lower()))
            title_words = set(re.findall(r'\w+', content_item.metadata["title"].lower()))
            
            if filename_words & title_words:  # Some overlap
                score += 0.2
        
        return min(1.0, score)
    
    async def _generate_improvement_suggestions(self, dimension_scores: Dict[str, float], 
                                              technical_scores: Dict[str, float],
                                              content_scores: Dict[str, float]) -> List[str]:
        """Generate improvement suggestions based on scores."""        suggestions = []
        
        # Technical improvements
        if technical_scores.get("encoding_quality", 1.0) < 0.6:
            suggestions.append("Consider using higher bitrate encoding for better audio quality")
        
        if technical_scores.get("metadata_consistency", 1.0) < 0.6:
            suggestions.append("Add complete and consistent metadata information")
        
        # Content improvements
        if content_scores.get("originality", 1.0) < 0.6:
            suggestions.append("Enhance content originality and uniqueness")
        
        if content_scores.get("professional_quality", 1.0) < 0.6:
            suggestions.append("Improve production quality and professional standards")
        
        # Metadata improvements
        if dimension_scores.get("metadata_quality", 1.0) < 0.6:
            suggestions.append("Complete missing metadata fields (title, artist, genre)")
        
        # Structural improvements
        if dimension_scores.get("structural_quality", 1.0) < 0.6:
            suggestions.append("Improve file naming and organizational structure")
        
        return suggestions
    
    async def _identify_critical_issues(self, dimension_scores: Dict[str, float],
                                       technical_scores: Dict[str, float],
                                       content_scores: Dict[str, float]) -> List[str]:
        """Identify critical quality issues."""        issues = []
        
        # Critical technical issues
        if technical_scores.get("file_integrity", 1.0) < 0.3:
            issues.append("File integrity compromised - possible corruption")
        
        if technical_scores.get("format_compliance", 1.0) < 0.3:
            issues.append("Format compliance issues detected")
        
        # Critical content issues
        if content_scores.get("originality", 1.0) < 0.3:
            issues.append("Originality concerns - possible copyright issues")
        
        # Critical overall issues
        if dimension_scores.get("authenticity", 1.0) < 0.3:
            issues.append("Authenticity concerns detected")
        
        if dimension_scores.get("completeness", 1.0) < 0.3:
            issues.append("Content appears incomplete or truncated")
        
        return issues
    
    async def _generate_quality_recommendation(self, overall_score: float) -> str:
        """Generate quality recommendation."""        if overall_score >= 0.9:
            return "Exceptional quality - ready for premium distribution"
        elif overall_score >= 0.8:
            return "High quality - suitable for professional platforms"
        elif overall_score >= 0.7:
            return "Good quality - acceptable for most platforms"
        elif overall_score >= 0.6:
            return "Acceptable quality - may need minor improvements"
        elif overall_score >= 0.4:
            return "Poor quality - significant improvements needed"
        else:
            return "Unacceptable quality - major revision required"
