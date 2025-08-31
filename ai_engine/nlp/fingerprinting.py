"""Content Fingerprinting Module for IA Influencer Agent Platform

Advanced content fingerprinting and copyright protection system for digital content
creators and influencers. Provides robust content identification and plagiarism detection.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""
import asyncio
import logging
import hashlib
import hmac
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json
import re
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.util import ngrams
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

@dataclass
class ContentFingerprint:
    """Comprehensive content fingerprint"""    content_id: str
    content_hash: str
    structural_hash: str
    semantic_hash: str
    linguistic_fingerprint: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: datetime = field(default_factory=datetime.utcnow)
    creator_id: Optional[str] = None
    platform_source: Optional[str] = None
    copyright_claim: Optional[Dict[str, Any]] = None

@dataclass
class SimilarityMatch:
    """Content similarity match result"""    source_fingerprint: ContentFingerprint
    target_fingerprint: ContentFingerprint
    similarity_score: float
    match_type: str  # 'exact', 'substantial', 'partial', 'semantic'
    matching_elements: Dict[str, Any]
    confidence_level: float
    detected_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CopyrightViolation:
    """Copyright violation detection result"""    violation_id: str
    original_content: ContentFingerprint
    suspected_copy: ContentFingerprint
    violation_type: str  # 'plagiarism', 'unauthorized_use', 'substantial_similarity'
    severity: str  # 'high', 'medium', 'low'
    evidence: Dict[str, Any]
    recommended_action: str
    confidence_score: float
    detected_at: datetime = field(default_factory=datetime.utcnow)

class FingerprintGenerator(ABC):
    """Abstract base class for fingerprint generators"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def generate_fingerprint(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate fingerprint for content"""        pass

class AdvancedContentFingerprinter:
    """    Advanced content fingerprinting system
    
    Capabilities:
    - Multi-level hash generation (structural, semantic, linguistic)
    - Content similarity detection
    - Plagiarism identification
    - Copyright protection
    - Content provenance tracking
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.fingerprint_generators = {}
        self.similarity_threshold = self.config.get('similarity_threshold', 0.8)
        self.semantic_threshold = self.config.get('semantic_threshold', 0.7)
        self.fingerprint_database = {}
        self.violation_history = []
        
        # Initialize components
        self._initialize_generators()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""        return {
            'similarity_threshold': 0.8,
            'semantic_threshold': 0.7,
            'hash_algorithm': 'sha256',
            'ngram_sizes': [2, 3, 4, 5],
            'min_content_length': 50,
            'enable_semantic_hashing': True,
            'enable_structural_analysis': True,
            'cache_fingerprints': True,
            'max_cache_size': 10000
        }
    
    def _initialize_generators(self):
        """Initialize fingerprint generators"""        self.fingerprint_generators = {
            'hash': HashFingerprintGenerator(self.config),
            'structural': StructuralFingerprintGenerator(self.config),
            'semantic': SemanticFingerprintGenerator(self.config),
            'linguistic': LinguisticFingerprintGenerator(self.config),
            'ngram': NGramFingerprintGenerator(self.config)
        }
    
    async def create_comprehensive_fingerprint(self, content: str, metadata: Dict[str, Any] = None) -> ContentFingerprint:
        """Create comprehensive content fingerprint"""        if len(content) < self.config.get('min_content_length', 50):
            raise ValueError("Content too short for reliable fingerprinting")
        
        metadata = metadata or {}
        content_id = self._generate_content_id(content, metadata)
        
        try:
            # Generate all fingerprint components
            fingerprint_data = {}
            
            # Basic hash fingerprint
            hash_fp = await self.fingerprint_generators['hash'].generate_fingerprint(content, metadata)
            fingerprint_data['hash'] = hash_fp
            
            # Structural fingerprint
            structural_fp = await self.fingerprint_generators['structural'].generate_fingerprint(content, metadata)
            fingerprint_data['structural'] = structural_fp
            
            # Semantic fingerprint
            if self.config.get('enable_semantic_hashing', True):
                semantic_fp = await self.fingerprint_generators['semantic'].generate_fingerprint(content, metadata)
                fingerprint_data['semantic'] = semantic_fp
            
            # Linguistic fingerprint
            linguistic_fp = await self.fingerprint_generators['linguistic'].generate_fingerprint(content, metadata)
            fingerprint_data['linguistic'] = linguistic_fp
            
            # N-gram fingerprint
            ngram_fp = await self.fingerprint_generators['ngram'].generate_fingerprint(content, metadata)
            fingerprint_data['ngram'] = ngram_fp
            
            # Create comprehensive fingerprint
            fingerprint = ContentFingerprint(
                content_id=content_id,
                content_hash=hash_fp.get('content_hash', ''),
                structural_hash=structural_fp.get('structural_hash', ''),
                semantic_hash=semantic_fp.get('semantic_hash', '') if semantic_fp else '',
                linguistic_fingerprint=linguistic_fp,
                metadata={
                    'content_length': len(content),
                    'word_count': len(content.split()),
                    'fingerprint_version': '1.0',
                    'generation_method': 'comprehensive',
                    'original_metadata': metadata,
                    'all_fingerprints': fingerprint_data
                },
                creator_id=metadata.get('creator_id'),
                platform_source=metadata.get('platform_source')
            )
            
            # Cache fingerprint if enabled
            if self.config.get('cache_fingerprints', True):
                self._cache_fingerprint(fingerprint)
            
            logger.info(f"Created fingerprint for content {content_id}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Failed to create fingerprint: {str(e)}")
            raise
    
    async def detect_similarity(self, fingerprint1: ContentFingerprint, fingerprint2: ContentFingerprint) -> SimilarityMatch:
        """Detect similarity between two content fingerprints"""        
        # Calculate different types of similarity
        similarities = {}
        
        # Hash similarity (exact match)
        hash_similarity = 1.0 if fingerprint1.content_hash == fingerprint2.content_hash else 0.0
        similarities['hash'] = hash_similarity
        
        # Structural similarity
        structural_similarity = await self._calculate_structural_similarity(fingerprint1, fingerprint2)
        similarities['structural'] = structural_similarity
        
        # Semantic similarity
        if fingerprint1.semantic_hash and fingerprint2.semantic_hash:
            semantic_similarity = await self._calculate_semantic_similarity(fingerprint1, fingerprint2)
            similarities['semantic'] = semantic_similarity
        else:
            semantic_similarity = 0.0
        
        # Linguistic similarity
        linguistic_similarity = await self._calculate_linguistic_similarity(fingerprint1, fingerprint2)
        similarities['linguistic'] = linguistic_similarity
        
        # N-gram similarity
        ngram_similarity = await self._calculate_ngram_similarity(fingerprint1, fingerprint2)
        similarities['ngram'] = ngram_similarity
        
        # Overall similarity (weighted average)
        weights = {
            'hash': 0.3,
            'structural': 0.2,
            'semantic': 0.2,
            'linguistic': 0.15,
            'ngram': 0.15
        }
        
        overall_similarity = sum(similarities[key] * weights[key] for key in weights.keys())
        
        # Determine match type
        match_type = self._determine_match_type(similarities)
        
        # Calculate confidence
        confidence = self._calculate_similarity_confidence(similarities)
        
        return SimilarityMatch(
            source_fingerprint=fingerprint1,
            target_fingerprint=fingerprint2,
            similarity_score=overall_similarity,
            match_type=match_type,
            matching_elements=similarities,
            confidence_level=confidence
        )
    
    async def scan_for_violations(self, new_fingerprint: ContentFingerprint, database_fingerprints: List[ContentFingerprint] = None) -> List[CopyrightViolation]:
        """Scan for potential copyright violations"""        violations = []
        
        # Use cached fingerprints if no database provided
        if database_fingerprints is None:
            database_fingerprints = list(self.fingerprint_database.values())
        
        # Compare against all fingerprints in database
        for existing_fingerprint in database_fingerprints:
            # Skip self-comparison
            if existing_fingerprint.content_id == new_fingerprint.content_id:
                continue
            
            # Skip if same creator (unless specified otherwise)
            if (existing_fingerprint.creator_id == new_fingerprint.creator_id and 
                existing_fingerprint.creator_id is not None):
                continue
            
            # Calculate similarity
            similarity_match = await self.detect_similarity(new_fingerprint, existing_fingerprint)
            
            # Check if similarity exceeds threshold
            if similarity_match.similarity_score >= self.similarity_threshold:
                violation = await self._analyze_potential_violation(similarity_match)
                if violation:
                    violations.append(violation)
        
        return violations
    
    async def _analyze_potential_violation(self, similarity_match: SimilarityMatch) -> Optional[CopyrightViolation]:
        """Analyze similarity match for potential copyright violation"""        
        # Determine violation type
        violation_type = self._determine_violation_type(similarity_match)
        
        if not violation_type:
            return None
        
        # Calculate severity
        severity = self._calculate_violation_severity(similarity_match)
        
        # Gather evidence
        evidence = self._gather_violation_evidence(similarity_match)
        
        # Generate recommendation
        recommendation = self._generate_violation_recommendation(violation_type, severity, similarity_match)
        
        violation_id = self._generate_violation_id(similarity_match)
        
        return CopyrightViolation(
            violation_id=violation_id,
            original_content=similarity_match.source_fingerprint,
            suspected_copy=similarity_match.target_fingerprint,
            violation_type=violation_type,
            severity=severity,
            evidence=evidence,
            recommended_action=recommendation,
            confidence_score=similarity_match.confidence_level
        )
    
    async def track_content_lineage(self, fingerprint: ContentFingerprint) -> Dict[str, Any]:
        """Track content lineage and derivation history"""        lineage = {
            'original_fingerprint': fingerprint,
            'derived_content': [],
            'similar_content': [],
            'version_history': []
        }
        
        # Find similar content that might be derived
        all_fingerprints = list(self.fingerprint_database.values())
        
        for other_fingerprint in all_fingerprints:
            if other_fingerprint.content_id == fingerprint.content_id:
                continue
            
            similarity_match = await self.detect_similarity(fingerprint, other_fingerprint)
            
            # High similarity might indicate derivation
            if similarity_match.similarity_score > 0.6:
                if similarity_match.similarity_score > 0.9:
                    # Very high similarity - likely derived content
                    lineage['derived_content'].append({
                        'fingerprint': other_fingerprint,
                        'similarity': similarity_match.similarity_score,
                        'relationship': 'derived'
                    })
                else:
                    # Moderate similarity - related content
                    lineage['similar_content'].append({
                        'fingerprint': other_fingerprint,
                        'similarity': similarity_match.similarity_score,
                        'relationship': 'similar'
                    })
        
        # Track version history if same creator
        same_creator_content = [
            fp for fp in all_fingerprints 
            if fp.creator_id == fingerprint.creator_id and fp.creator_id is not None
        ]
        
        for version_fp in same_creator_content:
            if version_fp.creation_timestamp < fingerprint.creation_timestamp:
                similarity_match = await self.detect_similarity(fingerprint, version_fp)
                if similarity_match.similarity_score > 0.5:
                    lineage['version_history'].append({
                        'fingerprint': version_fp,
                        'similarity': similarity_match.similarity_score,
                        'time_diff': fingerprint.creation_timestamp - version_fp.creation_timestamp
                    })
        
        return lineage
    
    def _generate_content_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate unique content ID"""        # Create deterministic ID based on content and metadata
        id_string = f"{content[:100]}{json.dumps(sorted(metadata.items()), sort_keys=True)}"
        return hashlib.sha256(id_string.encode()).hexdigest()[:16]
    
    def _cache_fingerprint(self, fingerprint: ContentFingerprint):
        """Cache fingerprint for future comparisons"""        self.fingerprint_database[fingerprint.content_id] = fingerprint
        
        # Manage cache size
        max_cache_size = self.config.get('max_cache_size', 10000)
        if len(self.fingerprint_database) > max_cache_size:
            # Remove oldest fingerprints
            sorted_fps = sorted(
                self.fingerprint_database.items(),
                key=lambda x: x[1].creation_timestamp
            )
            
            # Remove oldest 10%
            remove_count = max_cache_size // 10
            for i in range(remove_count):
                del self.fingerprint_database[sorted_fps[i][0]]
    
    async def _calculate_structural_similarity(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> float:
        """Calculate structural similarity between fingerprints"""        if not fp1.structural_hash or not fp2.structural_hash:
            return 0.0
        
        # Simple hash comparison
        if fp1.structural_hash == fp2.structural_hash:
            return 1.0
        
        # More sophisticated structural comparison could be implemented here
        return 0.0
    
    async def _calculate_semantic_similarity(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> float:
        """Calculate semantic similarity between fingerprints"""        if not fp1.semantic_hash or not fp2.semantic_hash:
            return 0.0
        
        # Simple hash comparison for now
        if fp1.semantic_hash == fp2.semantic_hash:
            return 1.0
        
        # Could implement vector-based semantic similarity here
        return 0.0
    
    async def _calculate_linguistic_similarity(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> float:
        """Calculate linguistic similarity between fingerprints"""        ling1 = fp1.linguistic_fingerprint
        ling2 = fp2.linguistic_fingerprint
        
        if not ling1 or not ling2:
            return 0.0
        
        similarities = []
        
        # Compare vocabulary overlap
        vocab1 = set(ling1.get('vocabulary', []))
        vocab2 = set(ling2.get('vocabulary', []))
        if vocab1 and vocab2:
            vocab_similarity = len(vocab1.intersection(vocab2)) / len(vocab1.union(vocab2))
            similarities.append(vocab_similarity)
        
        # Compare POS tag distributions
        pos1 = ling1.get('pos_distribution', {})
        pos2 = ling2.get('pos_distribution', {})
        if pos1 and pos2:
            pos_similarity = self._calculate_distribution_similarity(pos1, pos2)
            similarities.append(pos_similarity)
        
        # Compare sentence structure metrics
        struct1 = ling1.get('structure_metrics', {})
        struct2 = ling2.get('structure_metrics', {})
        if struct1 and struct2:
            struct_similarity = self._calculate_metrics_similarity(struct1, struct2)
            similarities.append(struct_similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    async def _calculate_ngram_similarity(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> float:
        """Calculate n-gram similarity between fingerprints"""        fp1_data = fp1.metadata.get('all_fingerprints', {}).get('ngram', {})
        fp2_data = fp2.metadata.get('all_fingerprints', {}).get('ngram', {})
        
        if not fp1_data or not fp2_data:
            return 0.0
        
        similarities = []
        
        # Compare different n-gram sizes
        for n in self.config.get('ngram_sizes', [2, 3, 4, 5]):
            ngrams1 = set(fp1_data.get(f'{n}grams', []))
            ngrams2 = set(fp2_data.get(f'{n}grams', []))
            
            if ngrams1 and ngrams2:
                intersection = len(ngrams1.intersection(ngrams2))
                union = len(ngrams1.union(ngrams2))
                similarity = intersection / union if union > 0 else 0.0
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _determine_match_type(self, similarities: Dict[str, float]) -> str:
        """Determine the type of match based on similarity scores"""        if similarities['hash'] == 1.0:
            return 'exact'
        elif similarities['structural'] > 0.9 and similarities['ngram'] > 0.8:
            return 'substantial'
        elif similarities['semantic'] > 0.7:
            return 'semantic'
        elif any(score > 0.5 for score in similarities.values()):
            return 'partial'
        else:
            return 'minimal'
    
    def _calculate_similarity_confidence(self, similarities: Dict[str, float]) -> float:
        """Calculate confidence in similarity assessment"""        # Higher confidence for multiple high similarity scores
        high_scores = [score for score in similarities.values() if score > 0.7]
        moderate_scores = [score for score in similarities.values() if 0.4 <= score <= 0.7]
        
        confidence = 0.5  # Base confidence
        
        # Boost for multiple high similarity scores
        confidence += len(high_scores) * 0.15
        
        # Boost for moderate scores
        confidence += len(moderate_scores) * 0.05
        
        # Boost for exact hash match
        if similarities.get('hash', 0) == 1.0:
            confidence = 1.0
        
        return min(1.0, confidence)
    
    def _determine_violation_type(self, similarity_match: SimilarityMatch) -> Optional[str]:
        """Determine the type of copyright violation"""        similarity = similarity_match.similarity_score
        match_type = similarity_match.match_type
        
        if match_type == 'exact' or similarity > 0.95:
            return 'plagiarism'
        elif match_type == 'substantial' or similarity > 0.8:
            return 'substantial_similarity'
        elif similarity > 0.7:
            return 'unauthorized_use'
        else:
            return None  # No violation
    
    def _calculate_violation_severity(self, similarity_match: SimilarityMatch) -> str:
        """Calculate severity of copyright violation"""        similarity = similarity_match.similarity_score
        
        if similarity > 0.9:
            return 'high'
        elif similarity > 0.75:
            return 'medium'
        else:
            return 'low'
    
    def _gather_violation_evidence(self, similarity_match: SimilarityMatch) -> Dict[str, Any]:
        """Gather evidence for copyright violation"""        return {
            'similarity_breakdown': similarity_match.matching_elements,
            'overall_similarity': similarity_match.similarity_score,
            'match_type': similarity_match.match_type,
            'confidence': similarity_match.confidence_level,
            'original_timestamp': similarity_match.source_fingerprint.creation_timestamp,
            'suspected_copy_timestamp': similarity_match.target_fingerprint.creation_timestamp,
            'time_difference': similarity_match.target_fingerprint.creation_timestamp - similarity_match.source_fingerprint.creation_timestamp
        }
    
    def _generate_violation_recommendation(self, violation_type: str, severity: str, similarity_match: SimilarityMatch) -> str:
        """Generate recommendation for handling violation"""        recommendations = {
            ('plagiarism', 'high'): 'Immediate takedown notice and legal action recommended',
            ('plagiarism', 'medium'): 'Send formal cease and desist notice',
            ('plagiarism', 'low'): 'Contact content creator for clarification',
            ('substantial_similarity', 'high'): 'Request content modification or removal',
            ('substantial_similarity', 'medium'): 'Negotiate licensing agreement',
            ('substantial_similarity', 'low'): 'Monitor for further violations',
            ('unauthorized_use', 'high'): 'Request proper attribution and licensing',
            ('unauthorized_use', 'medium'): 'Send attribution request',
            ('unauthorized_use', 'low'): 'Document violation for future reference'
        }
        
        return recommendations.get((violation_type, severity), 'Manual review required')
    
    def _generate_violation_id(self, similarity_match: SimilarityMatch) -> str:
        """Generate unique violation ID"""        id_string = f"{similarity_match.source_fingerprint.content_id}{similarity_match.target_fingerprint.content_id}{similarity_match.detected_at}"
        return hashlib.sha256(id_string.encode()).hexdigest()[:12]
    
    def _calculate_distribution_similarity(self, dist1: Dict[str, float], dist2: Dict[str, float]) -> float:
        """Calculate similarity between two distributions"""        all_keys = set(dist1.keys()).union(set(dist2.keys()))
        
        if not all_keys:
            return 0.0
        
        vec1 = [dist1.get(key, 0.0) for key in all_keys]
        vec2 = [dist2.get(key, 0.0) for key in all_keys]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _calculate_metrics_similarity(self, metrics1: Dict[str, float], metrics2: Dict[str, float]) -> float:
        """Calculate similarity between two sets of metrics"""        common_keys = set(metrics1.keys()).intersection(set(metrics2.keys()))
        
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            val1, val2 = metrics1[key], metrics2[key]
            if val1 == 0 and val2 == 0:
                similarities.append(1.0)
            elif val1 == 0 or val2 == 0:
                similarities.append(0.0)
            else:
                # Calculate relative similarity
                ratio = min(val1, val2) / max(val1, val2)
                similarities.append(ratio)
        
        return np.mean(similarities)

# Specific fingerprint generators
class HashFingerprintGenerator(FingerprintGenerator):
    """Generate cryptographic hash fingerprints"""    
    async def generate_fingerprint(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate hash-based fingerprint"""        algorithm = self.config.get('hash_algorithm', 'sha256')
        
        # Generate different types of hashes
        content_bytes = content.encode('utf-8')
        
        if algorithm == 'sha256':
            content_hash = hashlib.sha256(content_bytes).hexdigest()
        elif algorithm == 'md5':
            content_hash = hashlib.md5(content_bytes).hexdigest()
        else:
            content_hash = hashlib.sha256(content_bytes).hexdigest()
        
        # Generate normalized content hash (whitespace normalized)
        normalized_content = re.sub(r'\s+', ' ', content.strip())
        normalized_hash = hashlib.sha256(normalized_content.encode('utf-8')).hexdigest()
        
        return {
            'content_hash': content_hash,
            'normalized_hash': normalized_hash,
            'algorithm': algorithm,
            'content_length': len(content)
        }

class StructuralFingerprintGenerator(FingerprintGenerator):
    """Generate structural fingerprints based on content structure"""    
    async def generate_fingerprint(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate structure-based fingerprint"""        
        # Analyze content structure
        structure_features = self._extract_structure_features(content)
        
        # Create structural signature
        structure_signature = self._create_structure_signature(structure_features)
        
        # Generate structural hash
        structural_hash = hashlib.sha256(structure_signature.encode()).hexdigest()
        
        return {
            'structural_hash': structural_hash,
            'structure_features': structure_features,
            'structure_signature': structure_signature
        }
    
    def _extract_structure_features(self, content: str) -> Dict[str, Any]:
        """Extract structural features from content"""        lines = content.split('\n')
        sentences = content.split('.')
        paragraphs = content.split('\n\n')
        words = content.split()
        
        return {
            'line_count': len(lines),
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs),
            'word_count': len(words),
            'avg_sentence_length': len(words) / max(len(sentences), 1),
            'avg_paragraph_length': len(sentences) / max(len(paragraphs), 1),
            'punctuation_pattern': self._analyze_punctuation_pattern(content),
            'capitalization_pattern': self._analyze_capitalization_pattern(content)
        }
    
    def _create_structure_signature(self, features: Dict[str, Any]) -> str:
        """Create signature from structural features"""        # Create normalized signature
        signature_parts = [
            f"lines:{features['line_count']}",
            f"sentences:{features['sentence_count']}",
            f"paragraphs:{features['paragraph_count']}",
            f"avg_sent_len:{round(features['avg_sentence_length'], 1)}",
            f"punct_pattern:{features['punctuation_pattern']}",
            f"cap_pattern:{features['capitalization_pattern']}"
        ]
        
        return "|".join(signature_parts)
    
    def _analyze_punctuation_pattern(self, content: str) -> str:
        """Analyze punctuation patterns"""        punctuation_chars = '.,!?;:'
        pattern = ""
        
        for char in content[:100]:  # First 100 chars
            if char in punctuation_chars:
                pattern += char
            elif char.isspace():
                pattern += 'S'
            elif char.isalpha():
                pattern += 'W'
            elif char.isdigit():
                pattern += 'D'
        
        return pattern[:20]  # Limit pattern length
    
    def _analyze_capitalization_pattern(self, content: str) -> str:
        """Analyze capitalization patterns"""        pattern = ""
        
        for char in content[:50]:  # First 50 chars
            if char.isupper():
                pattern += 'U'
            elif char.islower():
                pattern += 'L'
            elif char.isspace():
                pattern += 'S'
            else:
                pattern += 'O'
        
        return pattern

class SemanticFingerprintGenerator(FingerprintGenerator):
    """Generate semantic fingerprints based on content meaning"""    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 2),
            stop_words='english'
        )
    
    async def generate_fingerprint(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate semantic fingerprint"""        
        try:
            # Generate TF-IDF vector
            tfidf_matrix = self.vectorizer.fit_transform([content])
            tfidf_vector = tfidf_matrix.toarray()[0]
            
            # Create semantic signature from top features
            feature_names = self.vectorizer.get_feature_names_out()
            top_indices = tfidf_vector.argsort()[-20:][::-1]  # Top 20 features
            
            semantic_features = [
                f"{feature_names[i]}:{round(tfidf_vector[i], 3)}"
                for i in top_indices if tfidf_vector[i] > 0
            ]
            
            semantic_signature = "|".join(semantic_features)
            semantic_hash = hashlib.sha256(semantic_signature.encode()).hexdigest()
            
            return {
                'semantic_hash': semantic_hash,
                'semantic_signature': semantic_signature,
                'top_features': semantic_features,
                'vector_norm': float(np.linalg.norm(tfidf_vector))
            }
            
        except Exception as e:
            logger.warning(f"Semantic fingerprint generation failed: {str(e)}")
            return {
                'semantic_hash': '',
                'error': str(e)
            }

class LinguisticFingerprintGenerator(FingerprintGenerator):
    """Generate linguistic fingerprints based on language patterns"""    
    async def generate_fingerprint(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate linguistic fingerprint"""        
        try:
            # Download required NLTK data if not present
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            
            try:
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                nltk.download('averaged_perceptron_tagger', quiet=True)
            
            # Tokenize and analyze
            tokens = word_tokenize(content.lower())
            
            # Extract linguistic features
            linguistic_features = {
                'vocabulary': list(set(tokens))[:100],  # Limit vocabulary size
                'vocabulary_richness': len(set(tokens)) / len(tokens) if tokens else 0,
                'avg_word_length': np.mean([len(word) for word in tokens]) if tokens else 0,
                'word_length_distribution': self._calculate_word_length_distribution(tokens),
                'structure_metrics': {
                    'sentence_count': len(content.split('.')),
                    'avg_sentence_length': len(tokens) / max(len(content.split('.')), 1),
                    'complexity_score': self._calculate_complexity_score(content)
                }
            }
            
            # Try POS tagging if available
            try:
                pos_tags = nltk.pos_tag(tokens)
                pos_distribution = self._calculate_pos_distribution(pos_tags)
                linguistic_features['pos_distribution'] = pos_distribution
            except Exception:
                logger.warning("POS tagging failed, skipping")
            
            return linguistic_features
            
        except Exception as e:
            logger.warning(f"Linguistic fingerprint generation failed: {str(e)}")
            return {
                'vocabulary': [],
                'error': str(e)
            }
    
    def _calculate_word_length_distribution(self, tokens: List[str]) -> Dict[str, float]:
        """Calculate distribution of word lengths"""        if not tokens:
            return {}
        
        length_counts = Counter(len(word) for word in tokens if word.isalpha())
        total_words = sum(length_counts.values())
        
        if total_words == 0:
            return {}
        
        return {
            str(length): count / total_words
            for length, count in length_counts.items()
        }
    
    def _calculate_pos_distribution(self, pos_tags: List[Tuple[str, str]]) -> Dict[str, float]:
        """Calculate part-of-speech distribution"""        if not pos_tags:
            return {}
        
        pos_counts = Counter(tag for word, tag in pos_tags)
        total_tags = sum(pos_counts.values())
        
        return {
            pos: count / total_tags
            for pos, count in pos_counts.items()
        }
    
    def _calculate_complexity_score(self, content: str) -> float:
        """Calculate content complexity score"""        sentences = content.split('.')
        words = content.split()
        
        if not sentences or not words:
            return 0.0
        
        # Simple complexity metrics
        avg_sentence_length = len(words) / len(sentences)
        
        # Longer sentences and more complex punctuation = higher complexity
        complex_punctuation = content.count(',') + content.count(';') + content.count(':')
        punctuation_density = complex_punctuation / len(words) if words else 0
        
        # Combine metrics
        complexity = (avg_sentence_length / 20) + (punctuation_density * 10)
        return min(1.0, complexity)

class NGramFingerprintGenerator(FingerprintGenerator):
    """Generate n-gram based fingerprints"""    
    async def generate_fingerprint(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate n-gram fingerprint"""        
        try:
            # Tokenize content
            tokens = word_tokenize(content.lower())
            
            fingerprint_data = {}
            
            # Generate n-grams for different values of n
            for n in self.config.get('ngram_sizes', [2, 3, 4, 5]):
                if len(tokens) >= n:
                    content_ngrams = list(ngrams(tokens, n))
                    # Convert tuples to strings and take most common
                    ngram_strings = [' '.join(ngram) for ngram in content_ngrams]
                    most_common = Counter(ngram_strings).most_common(50)  # Top 50 n-grams
                    
                    fingerprint_data[f'{n}grams'] = [ngram for ngram, count in most_common]
                    fingerprint_data[f'{n}gram_counts'] = dict(most_common)
            
            return fingerprint_data
            
        except Exception as e:
            logger.warning(f"N-gram fingerprint generation failed: {str(e)}")
            return {}

# Utility functions
async def create_content_fingerprint(content: str, creator_id: str = None, platform: str = None) -> ContentFingerprint:
    """Quick function to create a content fingerprint"""    fingerprinter = AdvancedContentFingerprinter()
    
    metadata = {}
    if creator_id:
        metadata['creator_id'] = creator_id
    if platform:
        metadata['platform_source'] = platform
    
    return await fingerprinter.create_comprehensive_fingerprint(content, metadata)

async def check_content_similarity(content1: str, content2: str) -> float:
    """Quick function to check similarity between two content pieces"""    fingerprinter = AdvancedContentFingerprinter()
    
    fp1 = await fingerprinter.create_comprehensive_fingerprint(content1)
    fp2 = await fingerprinter.create_comprehensive_fingerprint(content2)
    
    similarity_match = await fingerprinter.detect_similarity(fp1, fp2)
    return similarity_match.similarity_score

# Content protection system
class ContentProtectionSystem:
    """Comprehensive content protection and monitoring system"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.fingerprinter = AdvancedContentFingerprinter(config)
        self.protected_content = {}
        self.violation_alerts = []
        self.monitoring_active = True
    
    async def protect_content(self, content: str, creator_id: str, metadata: Dict[str, Any] = None) -> ContentFingerprint:
        """Add content to protection system"""        metadata = metadata or {}
        metadata['creator_id'] = creator_id
        metadata['protection_enabled'] = True
        metadata['protection_timestamp'] = datetime.utcnow()
        
        fingerprint = await self.fingerprinter.create_comprehensive_fingerprint(content, metadata)
        self.protected_content[fingerprint.content_id] = fingerprint
        
        logger.info(f"Content protected: {fingerprint.content_id} for creator {creator_id}")
        return fingerprint
    
    async def monitor_violations(self, new_content: str, source_metadata: Dict[str, Any] = None) -> List[CopyrightViolation]:
        """Monitor for violations against protected content"""        if not self.monitoring_active:
            return []
        
        # Create fingerprint for new content
        new_fingerprint = await self.fingerprinter.create_comprehensive_fingerprint(new_content, source_metadata or {})
        
        # Check against all protected content
        protected_fingerprints = list(self.protected_content.values())
        violations = await self.fingerprinter.scan_for_violations(new_fingerprint, protected_fingerprints)
        
        # Store violations for alerting
        self.violation_alerts.extend(violations)
        
        # Log violations
        for violation in violations:
            logger.warning(f"Potential copyright violation detected: {violation.violation_id}")
        
        return violations
    
    def get_protection_stats(self) -> Dict[str, Any]:
        """Get protection system statistics"""        return {
            'protected_content_count': len(self.protected_content),
            'total_violations_detected': len(self.violation_alerts),
            'monitoring_active': self.monitoring_active,
            'recent_violations': len([v for v in self.violation_alerts if v.detected_at > datetime.utcnow() - timedelta(days=7)])
        }
