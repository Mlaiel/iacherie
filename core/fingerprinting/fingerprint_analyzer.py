"""IA Influencer Agent - Fingerprint Analyzer
Advanced analysis and intelligence for fingerprint data

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved to Fahed Mlaiel
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited
"""import asyncio
import logging
import numpy as np
import json
import time
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from .fingerprint_manager import FingerprintResult, ContentType

logger = logging.getLogger(__name__)


@dataclass
class AnalysisReport:
    """Report generated from fingerprint analysis"""    report_id: str
    analysis_type: str
    target_fingerprint: str
    findings: Dict[str, Any]
    confidence_score: float
    recommendations: List[str]
    generated_at: float


@dataclass
class SimilarityCluster:
    """Cluster of similar fingerprints"""    cluster_id: str
    representative_fingerprint: FingerprintResult
    members: List[FingerprintResult]
    similarity_scores: List[float]
    cluster_center: Dict[str, Any]
    quality_score: float


class FingerprintAnalyzer:
    """    Advanced analyzer for fingerprint data providing intelligence,
    clustering, pattern detection, and forensic analysis
    """    
    def __init__(self):
        """Initialize the fingerprint analyzer"""        self.analysis_cache = {}
        self.clustering_cache = {}
        self.pattern_database = defaultdict(list)
        
        # Analysis thresholds
        self.similarity_threshold = 0.85
        self.cluster_min_size = 2
        self.pattern_confidence_threshold = 0.8
        
        logger.info("FingerprintAnalyzer initialized")
    
    async def analyze_fingerprint_quality(
        self, 
        fingerprint: FingerprintResult
    ) -> AnalysisReport:
        """        Analyze the quality and reliability of a fingerprint
        
        Args:
            fingerprint: Fingerprint result to analyze
        
        Returns:
            Quality analysis report
        """        try:
            report_id = f"quality_{fingerprint.request_id}_{int(time.time())}"
            
            if not fingerprint.success:
                return AnalysisReport(
                    report_id=report_id,
                    analysis_type="quality_analysis",
                    target_fingerprint=fingerprint.request_id,
                    findings={"error": "Fingerprint extraction failed"},
                    confidence_score=0.0,
                    recommendations=["Re-extract fingerprint with different parameters"],
                    generated_at=time.time()
                )
            
            findings = {}
            quality_scores = []
            recommendations = []
            
            # Analyze each method's confidence and data quality
            methods_data = fingerprint.fingerprint_data.get('methods', {})
            
            for method, data in methods_data.items():
                method_quality = await self._analyze_method_quality(method, data, fingerprint.content_type)
                findings[f"{method}_quality"] = method_quality
                quality_scores.append(method_quality['score'])
                
                if method_quality['score'] < 0.7:
                    recommendations.append(f"Consider re-processing with optimized {method} parameters")
            
            # Overall quality assessment
            overall_quality = np.mean(quality_scores) if quality_scores else 0.0
            
            findings.update({
                "overall_quality_score": overall_quality,
                "processing_time": fingerprint.processing_time,
                "file_size": fingerprint.fingerprint_data.get('file_size', 0),
                "content_type": fingerprint.content_type.value,
                "methods_analyzed": len(methods_data),
                "timestamp": fingerprint.fingerprint_data.get('created_at', 0)
            })
            
            # Generate quality-based recommendations
            if overall_quality > 0.9:
                recommendations.append("Excellent fingerprint quality - suitable for high-precision matching")
            elif overall_quality > 0.7:
                recommendations.append("Good fingerprint quality - suitable for standard matching")
            elif overall_quality > 0.5:
                recommendations.append("Moderate fingerprint quality - consider additional processing")
            else:
                recommendations.append("Poor fingerprint quality - recommend re-processing with different settings")
            
            report = AnalysisReport(
                report_id=report_id,
                analysis_type="quality_analysis",
                target_fingerprint=fingerprint.request_id,
                findings=findings,
                confidence_score=overall_quality,
                recommendations=recommendations,
                generated_at=time.time()
            )
            
            # Cache the analysis
            self.analysis_cache[report_id] = report
            
            logger.info(f"Generated quality analysis report {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error in quality analysis: {str(e)}")
            raise
    
    async def _analyze_method_quality(
        self, 
        method: str, 
        data: Dict[str, Any], 
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Analyze quality of specific fingerprinting method"""        try:
            if 'error' in data:
                return {
                    'score': 0.0,
                    'status': 'failed',
                    'error': data['error']
                }
            
            # Base quality from confidence if available
            base_score = data.get('confidence', 0.5)
            quality_factors = [base_score]
            
            # Content-type specific quality checks
            if content_type == ContentType.AUDIO:
                quality_factors.extend(await self._analyze_audio_method_quality(method, data))
            elif content_type == ContentType.VIDEO:
                quality_factors.extend(await self._analyze_video_method_quality(method, data))
            elif content_type == ContentType.IMAGE:
                quality_factors.extend(await self._analyze_image_method_quality(method, data))
            
            # Calculate weighted quality score
            quality_score = np.mean(quality_factors)
            
            return {
                'score': float(quality_score),
                'status': 'success',
                'factors_analyzed': len(quality_factors),
                'base_confidence': base_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing method quality: {str(e)}")
            return {'score': 0.0, 'status': 'error', 'error': str(e)}
    
    async def _analyze_audio_method_quality(self, method: str, data: Dict) -> List[float]:
        """Analyze audio method quality factors"""        factors = []
        
        try:
            if method == 'chromaprint':
                # Check if raw fingerprint exists and has reasonable length
                raw_fp = data.get('raw_fingerprint')
                if raw_fp and len(str(raw_fp)) > 50:
                    factors.append(0.9)
                else:
                    factors.append(0.3)
                    
            elif method == 'spectral_hash':
                # Check spectral feature consistency
                centroid = data.get('centroid_mean', 0)
                rolloff = data.get('rolloff_mean', 0)
                if centroid > 0 and rolloff > centroid:  # Rolloff should be higher than centroid
                    factors.append(0.8)
                else:
                    factors.append(0.4)
                    
            elif method == 'mfcc':
                # Check MFCC coefficient count and variance
                mfcc_means = data.get('mfcc_means', [])
                if len(mfcc_means) >= 12:  # Standard MFCC count
                    variance = np.var(mfcc_means) if mfcc_means else 0
                    if variance > 0.1:  # Good dynamic range
                        factors.append(0.85)
                    else:
                        factors.append(0.6)
                else:
                    factors.append(0.4)
                    
            elif method == 'tempo_rhythm':
                # Check tempo reasonableness and beat detection
                tempo = data.get('tempo', 0)
                beat_count = data.get('beat_count', 0)
                if 60 <= tempo <= 200 and beat_count > 10:  # Reasonable tempo and beats detected
                    factors.append(0.8)
                else:
                    factors.append(0.5)
                    
        except Exception as e:
            logger.error(f"Error in audio quality analysis: {str(e)}")
            factors.append(0.3)
        
        return factors
    
    async def _analyze_video_method_quality(self, method: str, data: Dict) -> List[float]:
        """Analyze video method quality factors"""        factors = []
        
        try:
            if method == 'perceptual_hash':
                # Check frame count and hash sequence quality
                frame_count = data.get('frame_count', 0)
                hash_sequence = data.get('hash_sequence', [])
                if frame_count > 10 and len(hash_sequence) == frame_count:
                    factors.append(0.9)
                else:
                    factors.append(0.5)
                    
            elif method == 'histogram':
                # Check histogram completeness
                frame_histograms = data.get('frame_histograms', [])
                avg_histogram = data.get('average_histogram', {})
                if frame_histograms and len(avg_histogram) == 3:  # H, S, V channels
                    factors.append(0.85)
                else:
                    factors.append(0.4)
                    
            elif method == 'optical_flow':
                # Check motion detection quality
                avg_magnitude = data.get('average_magnitude', 0)
                if avg_magnitude > 0.1:  # Some motion detected
                    factors.append(0.8)
                else:
                    factors.append(0.6)  # Static video is still valid
                    
            elif method == 'edge_detection':
                # Check edge detection results
                avg_density = data.get('average_edge_density', 0)
                if 0.01 <= avg_density <= 0.5:  # Reasonable edge density
                    factors.append(0.8)
                else:
                    factors.append(0.5)
                    
        except Exception as e:
            logger.error(f"Error in video quality analysis: {str(e)}")
            factors.append(0.3)
        
        return factors
    
    async def _analyze_image_method_quality(self, method: str, data: Dict) -> List[float]:
        """Analyze image method quality factors"""        factors = []
        
        try:
            if method == 'perceptual_hash':
                # Check hash completeness
                hashes = data.get('hashes', {})
                if len(hashes) >= 4:  # Multiple hash types
                    factors.append(0.9)
                else:
                    factors.append(0.5)
                    
            elif method == 'histogram':
                # Check histogram data
                bgr_hists = data.get('bgr_histograms', [])
                hsv_hists = data.get('hsv_histograms', [])
                if len(bgr_hists) == 3 and len(hsv_hists) == 3:
                    factors.append(0.85)
                else:
                    factors.append(0.4)
                    
            elif method == 'sift_features':
                # Check feature detection
                keypoint_count = data.get('keypoint_count', 0)
                if keypoint_count > 20:  # Good feature detection
                    factors.append(0.9)
                elif keypoint_count > 5:
                    factors.append(0.7)
                else:
                    factors.append(0.3)
                    
            elif method == 'texture_analysis':
                # Check texture feature completeness
                lbp_hist = data.get('lbp_histogram', [])
                gabor_resp = data.get('gabor_responses', [])
                if len(lbp_hist) > 0 and len(gabor_resp) > 0:
                    factors.append(0.8)
                else:
                    factors.append(0.4)
                    
        except Exception as e:
            logger.error(f"Error in image quality analysis: {str(e)}")
            factors.append(0.3)
        
        return factors
    
    async def detect_duplicate_content(
        self, 
        fingerprints: List[FingerprintResult],
        similarity_threshold: float = None
    ) -> List[List[FingerprintResult]]:
        """        Detect duplicate or near-duplicate content from fingerprint list
        
        Args:
            fingerprints: List of fingerprint results to analyze
            similarity_threshold: Custom threshold for duplicate detection
        
        Returns:
            List of groups containing duplicate content
        """        try:
            threshold = similarity_threshold or self.similarity_threshold
            duplicate_groups = []
            processed_fingerprints = set()
            
            for i, fp1 in enumerate(fingerprints):
                if fp1.request_id in processed_fingerprints or not fp1.success:
                    continue
                
                current_group = [fp1]
                processed_fingerprints.add(fp1.request_id)
                
                # Compare with remaining fingerprints
                for j in range(i + 1, len(fingerprints)):
                    fp2 = fingerprints[j]
                    
                    if (fp2.request_id in processed_fingerprints or 
                        not fp2.success or 
                        fp1.content_type != fp2.content_type):
                        continue
                    
                    # Calculate similarity
                    similarity = await self._calculate_fingerprint_similarity(fp1, fp2)
                    
                    if similarity >= threshold:
                        current_group.append(fp2)
                        processed_fingerprints.add(fp2.request_id)
                
                # Add group if it contains duplicates
                if len(current_group) > 1:
                    duplicate_groups.append(current_group)
            
            logger.info(f"Detected {len(duplicate_groups)} duplicate groups")
            return duplicate_groups
            
        except Exception as e:
            logger.error(f"Error detecting duplicates: {str(e)}")
            return []
    
    async def _calculate_fingerprint_similarity(
        self, 
        fp1: FingerprintResult, 
        fp2: FingerprintResult
    ) -> float:
        """Calculate overall similarity between two fingerprints"""        try:
            if fp1.content_type != fp2.content_type:
                return 0.0
            
            # Get methods data
            methods1 = fp1.fingerprint_data.get('methods', {})
            methods2 = fp2.fingerprint_data.get('methods', {})
            
            similarities = []
            
            # Compare common methods
            for method in set(methods1.keys()) & set(methods2.keys()):
                if 'error' not in methods1[method] and 'error' not in methods2[method]:
                    method_similarity = await self._compare_method_data(
                        method, methods1[method], methods2[method], fp1.content_type
                    )
                    similarities.append(method_similarity)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    async def _compare_method_data(
        self, 
        method: str, 
        data1: Dict, 
        data2: Dict, 
        content_type: ContentType
    ) -> float:
        """Compare data from specific fingerprinting method"""        try:
            # Use the primary hash/signature from each method
            if content_type == ContentType.AUDIO:
                if method == 'chromaprint':
                    hash1 = data1.get('hash', '')
                    hash2 = data2.get('hash', '')
                elif method == 'spectral_hash':
                    hash1 = data1.get('spectral_hash', '')
                    hash2 = data2.get('spectral_hash', '')
                elif method == 'mfcc':
                    hash1 = data1.get('mfcc_hash', '')
                    hash2 = data2.get('mfcc_hash', '')
                elif method == 'tempo_rhythm':
                    hash1 = data1.get('rhythm_hash', '')
                    hash2 = data2.get('rhythm_hash', '')
                else:
                    return 0.0
                    
            elif content_type == ContentType.VIDEO:
                if method == 'perceptual_hash':
                    hash1 = data1.get('sequence_hash', '')
                    hash2 = data2.get('sequence_hash', '')
                elif method == 'histogram':
                    hash1 = data1.get('histogram_hash', '')
                    hash2 = data2.get('histogram_hash', '')
                elif method == 'optical_flow':
                    hash1 = data1.get('motion_hash', '')
                    hash2 = data2.get('motion_hash', '')
                elif method == 'edge_detection':
                    hash1 = data1.get('edge_hash', '')
                    hash2 = data2.get('edge_hash', '')
                else:
                    return 0.0
                    
            elif content_type == ContentType.IMAGE:
                if method == 'perceptual_hash':
                    hash1 = data1.get('combined_hash', '')
                    hash2 = data2.get('combined_hash', '')
                elif method == 'histogram':
                    hash1 = data1.get('histogram_hash', '')
                    hash2 = data2.get('histogram_hash', '')
                elif method == 'sift_features':
                    hash1 = data1.get('feature_hash', '')
                    hash2 = data2.get('feature_hash', '')
                elif method == 'texture_analysis':
                    hash1 = data1.get('texture_hash', '')
                    hash2 = data2.get('texture_hash', '')
                else:
                    return 0.0
            else:
                return 0.0
            
            # Compare hashes
            if hash1 == hash2:
                return 1.0
            elif len(hash1) == len(hash2) and len(hash1) > 0:
                # Calculate normalized Hamming distance
                hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                similarity = 1.0 - (hamming_distance / len(hash1))
                return max(0.0, similarity)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error comparing method data: {str(e)}")
            return 0.0
    
    async def cluster_similar_content(
        self, 
        fingerprints: List[FingerprintResult],
        min_cluster_size: int = None
    ) -> List[SimilarityCluster]:
        """        Cluster fingerprints by similarity
        
        Args:
            fingerprints: List of fingerprint results
            min_cluster_size: Minimum size for a cluster
        
        Returns:
            List of similarity clusters
        """        try:
            min_size = min_cluster_size or self.cluster_min_size
            clusters = []
            
            # Group by content type first
            content_groups = defaultdict(list)
            for fp in fingerprints:
                if fp.success:
                    content_groups[fp.content_type].append(fp)
            
            # Cluster each content type separately
            for content_type, fps in content_groups.items():
                if len(fps) < min_size:
                    continue
                
                type_clusters = await self._cluster_by_content_type(fps, content_type, min_size)
                clusters.extend(type_clusters)
            
            logger.info(f"Generated {len(clusters)} similarity clusters")
            return clusters
            
        except Exception as e:
            logger.error(f"Error clustering content: {str(e)}")
            return []
    
    async def _cluster_by_content_type(
        self, 
        fingerprints: List[FingerprintResult], 
        content_type: ContentType,
        min_size: int
    ) -> List[SimilarityCluster]:
        """Cluster fingerprints of same content type"""        try:
            clusters = []
            used_fingerprints = set()
            
            for i, fp1 in enumerate(fingerprints):
                if fp1.request_id in used_fingerprints:
                    continue
                
                cluster_members = [fp1]
                similarity_scores = []
                used_fingerprints.add(fp1.request_id)
                
                # Find similar fingerprints
                for j in range(i + 1, len(fingerprints)):
                    fp2 = fingerprints[j]
                    
                    if fp2.request_id in used_fingerprints:
                        continue
                    
                    similarity = await self._calculate_fingerprint_similarity(fp1, fp2)
                    
                    if similarity >= self.similarity_threshold:
                        cluster_members.append(fp2)
                        similarity_scores.append(similarity)
                        used_fingerprints.add(fp2.request_id)
                
                # Create cluster if minimum size is met
                if len(cluster_members) >= min_size:
                    cluster_id = f"cluster_{content_type.value}_{int(time.time())}_{len(clusters)}"
                    
                    # Calculate cluster quality
                    quality_score = np.mean(similarity_scores) if similarity_scores else 1.0
                    
                    cluster = SimilarityCluster(
                        cluster_id=cluster_id,
                        representative_fingerprint=fp1,  # First member as representative
                        members=cluster_members,
                        similarity_scores=similarity_scores,
                        cluster_center=await self._calculate_cluster_center(cluster_members),
                        quality_score=quality_score
                    )
                    
                    clusters.append(cluster)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error clustering by content type: {str(e)}")
            return []
    
    async def _calculate_cluster_center(self, cluster_members: List[FingerprintResult]) -> Dict[str, Any]:
        """Calculate centroid of cluster for analysis"""        try:
            center = {
                'member_count': len(cluster_members),
                'content_type': cluster_members[0].content_type.value,
                'average_processing_time': np.mean([fp.processing_time for fp in cluster_members]),
                'average_file_size': np.mean([
                    fp.fingerprint_data.get('file_size', 0) for fp in cluster_members
                ]),
                'common_methods': self._find_common_methods(cluster_members)
            }
            
            return center
            
        except Exception as e:
            logger.error(f"Error calculating cluster center: {str(e)}")
            return {}
    
    def _find_common_methods(self, fingerprints: List[FingerprintResult]) -> List[str]:
        """Find methods common to all fingerprints in cluster"""        try:
            if not fingerprints:
                return []
            
            # Get methods from first fingerprint
            common_methods = set(fingerprints[0].fingerprint_data.get('methods', {}).keys())
            
            # Find intersection with all other fingerprints
            for fp in fingerprints[1:]:
                fp_methods = set(fp.fingerprint_data.get('methods', {}).keys())
                common_methods &= fp_methods
            
            return list(common_methods)
            
        except Exception as e:
            logger.error(f"Error finding common methods: {str(e)}")
            return []
    
    async def generate_forensic_report(
        self, 
        target_fingerprint: FingerprintResult,
        reference_database: List[FingerprintResult]
    ) -> AnalysisReport:
        """        Generate comprehensive forensic analysis report
        
        Args:
            target_fingerprint: Target fingerprint to analyze
            reference_database: Database of reference fingerprints
        
        Returns:
            Forensic analysis report
        """        try:
            report_id = f"forensic_{target_fingerprint.request_id}_{int(time.time())}"
            
            findings = {}
            recommendations = []
            confidence_factors = []
            
            # Quality analysis
            quality_report = await self.analyze_fingerprint_quality(target_fingerprint)
            findings['quality_analysis'] = quality_report.findings
            confidence_factors.append(quality_report.confidence_score)
            
            # Similarity search in database
            similar_matches = []
            for ref_fp in reference_database:
                if ref_fp.content_type == target_fingerprint.content_type:
                    similarity = await self._calculate_fingerprint_similarity(target_fingerprint, ref_fp)
                    if similarity > 0.7:  # Lower threshold for forensic analysis
                        similar_matches.append({
                            'reference_id': ref_fp.request_id,
                            'similarity_score': similarity,
                            'file_path': ref_fp.file_path
                        })
            
            # Sort by similarity
            similar_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            findings['similar_matches'] = similar_matches[:10]  # Top 10 matches
            
            # Uniqueness assessment
            if similar_matches:
                max_similarity = similar_matches[0]['similarity_score']
                if max_similarity > 0.95:
                    uniqueness = "Very Low - Near exact match found"
                    recommendations.append("Investigate potential copyright infringement")
                elif max_similarity > 0.85:
                    uniqueness = "Low - High similarity match found"
                    recommendations.append("Review content for potential similarity issues")
                elif max_similarity > 0.7:
                    uniqueness = "Moderate - Some similar content exists"
                    recommendations.append("Monitor for potential conflicts")
                else:
                    uniqueness = "High - No significant matches found"
                    recommendations.append("Content appears to be unique")
            else:
                uniqueness = "Very High - No similar content found"
                recommendations.append("Content is highly unique")
            
            findings['uniqueness_assessment'] = uniqueness
            
            # Temporal analysis if timestamps available
            creation_time = target_fingerprint.fingerprint_data.get('created_at', 0)
            if creation_time:
                findings['temporal_analysis'] = {
                    'creation_timestamp': creation_time,
                    'creation_date': datetime.fromtimestamp(creation_time).isoformat(),
                    'age_hours': (time.time() - creation_time) / 3600
                }
            
            # Technical characteristics
            findings['technical_characteristics'] = {
                'content_type': target_fingerprint.content_type.value,
                'file_size': target_fingerprint.fingerprint_data.get('file_size', 0),
                'processing_time': target_fingerprint.processing_time,
                'methods_used': list(target_fingerprint.fingerprint_data.get('methods', {}).keys()),
                'combined_hash': target_fingerprint.fingerprint_data.get('combined_hash', '')
            }
            
            # Overall confidence
            overall_confidence = np.mean(confidence_factors) if confidence_factors else 0.5
            
            # Generate recommendations based on findings
            if overall_confidence < 0.6:
                recommendations.append("Consider re-processing with higher quality settings")
            
            if len(similar_matches) == 0:
                recommendations.append("Content can be safely used for protection tracking")
            
            forensic_report = AnalysisReport(
                report_id=report_id,
                analysis_type="forensic_analysis",
                target_fingerprint=target_fingerprint.request_id,
                findings=findings,
                confidence_score=overall_confidence,
                recommendations=recommendations,
                generated_at=time.time()
            )
            
            # Cache the report
            self.analysis_cache[report_id] = forensic_report
            
            logger.info(f"Generated forensic report {report_id}")
            return forensic_report
            
        except Exception as e:
            logger.error(f"Error generating forensic report: {str(e)}")
            raise
    
    def get_cached_analysis(self, report_id: str) -> Optional[AnalysisReport]:
        """Get cached analysis report by ID"""        return self.analysis_cache.get(report_id)
    
    def clear_analysis_cache(self, older_than_hours: Optional[int] = None):
        """Clear analysis cache"""        try:
            if older_than_hours is None:
                self.analysis_cache.clear()
                logger.info("Cleared all analysis cache")
            else:
                cutoff_time = time.time() - (older_than_hours * 3600)
                expired_keys = [
                    report_id for report_id, report in self.analysis_cache.items()
                    if report.generated_at < cutoff_time
                ]
                
                for key in expired_keys:
                    del self.analysis_cache[key]
                
                logger.info(f"Cleared {len(expired_keys)} expired analysis entries")
                
        except Exception as e:
            logger.error(f"Error clearing analysis cache: {str(e)}")
    
    def get_analyzer_stats(self) -> Dict[str, Any]:
        """Get analyzer statistics and configuration"""        try:
            return {
                'analyzer': 'FingerprintAnalyzer',
                'version': '1.0.0',
                'cached_analyses': len(self.analysis_cache),
                'similarity_threshold': self.similarity_threshold,
                'cluster_min_size': self.cluster_min_size,
                'pattern_confidence_threshold': self.pattern_confidence_threshold,
                'analysis_types': [
                    'quality_analysis',
                    'duplicate_detection',
                    'similarity_clustering',
                    'forensic_analysis'
                ],
                'supported_content_types': [
                    ContentType.AUDIO.value,
                    ContentType.VIDEO.value,
                    ContentType.IMAGE.value
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting analyzer stats: {str(e)}")
            return {'error': str(e)}
