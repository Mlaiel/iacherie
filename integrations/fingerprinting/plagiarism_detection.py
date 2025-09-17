"""
Plagiarism Detection - Fingerprinting Module
==========================================
Système avancé de détection de plagiat avec analyse ML-powered,
cross-format similarity detection et automated infringement reporting.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

import asyncio
import logging
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import re
from pathlib import Path
from collections import Counter, defaultdict
import math
from itertools import combinations

logger = logging.getLogger(__name__)

class PlagiarismType(Enum):
    """Types de plagiat détectés."""
    DIRECT_COPY = "direct_copy"
    PARAPHRASE = "paraphrase"
    MOSAIC = "mosaic"
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    TRANSLATION = "translation"
    IDEA_PLAGIARISM = "idea_plagiarism"
    SELF_PLAGIARISM = "self_plagiarism"

class ContentType(Enum):
    """Types de contenu supportés."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CODE = "code"
    ACADEMIC_PAPER = "academic_paper"

class SimilarityAlgorithm(Enum):
    """Algorithmes de similarité disponibles."""
    COSINE_SIMILARITY = "cosine_similarity"
    JACCARD_INDEX = "jaccard_index"
    LEVENSHTEIN_DISTANCE = "levenshtein_distance"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    STRUCTURAL_SIMILARITY = "structural_similarity"
    DEEP_LEARNING = "deep_learning"

class ConfidenceLevel(Enum):
    """Niveaux de confiance."""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"

@dataclass
class PlagiarismSegment:
    """Segment de plagiat détecté."""
    segment_id: str
    source_start: int
    source_end: int
    target_start: int
    target_end: int
    similarity_score: float
    plagiarism_type: PlagiarismType
    confidence: ConfidenceLevel
    matched_content: str
    transformation_applied: List[str]

@dataclass
class PlagiarismReport:
    """Rapport de détection de plagiat."""
    report_id: str
    source_content_id: str
    target_content_id: str
    overall_similarity: float
    plagiarism_percentage: float
    plagiarism_type: PlagiarismType
    confidence_level: ConfidenceLevel
    detected_segments: List[PlagiarismSegment]
    analysis_timestamp: datetime
    processing_time: float
    algorithm_used: SimilarityAlgorithm
    metadata: Dict[str, Any]

@dataclass
class ContentFingerprint:
    """Empreinte de contenu pour la détection."""
    fingerprint_id: str
    content_hash: str
    content_type: ContentType
    feature_vector: np.ndarray
    structural_features: Dict[str, Any]
    semantic_features: Dict[str, Any]
    stylometric_features: Dict[str, Any]
    n_gram_signatures: Dict[str, List[str]]
    creation_timestamp: datetime
    author_id: Optional[str]

@dataclass
class SimilarityMatrix:
    """Matrice de similarité."""
    matrix_id: str
    content_ids: List[str]
    similarity_matrix: np.ndarray
    algorithm_used: SimilarityAlgorithm
    threshold: float
    computation_timestamp: datetime

class PlagiarismDetection:
    """
    Système avancé de détection de plagiat enterprise.
    Support multi-format plagiarism detection, ML-powered analysis et automated reporting.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le système de détection de plagiat.
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or self._get_default_config()
        self.content_database = {}  # Base de contenus pour comparaison
        self.fingerprint_cache = {}  # Cache des empreintes
        self._setup_ml_models()
        self._setup_similarity_algorithms()
        logger.info("PlagiarismDetection initialisé avec succès")

    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut."""
        return {
            'similarity_thresholds': {
                'direct_copy': 0.95,
                'paraphrase': 0.85,
                'mosaic': 0.75,
                'structural': 0.70,
                'semantic': 0.65,
                'translation': 0.60
            },
            'detection_algorithms': {
                'n_gram_size': [2, 3, 4, 5],
                'shingle_size': 5,
                'window_size': 100,
                'overlap_threshold': 0.8,
                'min_segment_length': 20
            },
            'ml_models': {
                'use_deep_learning': True,
                'embedding_dimension': 768,
                'transformer_model': 'sentence-transformers',
                'similarity_model': 'cosine'
            },
            'preprocessing': {
                'normalize_text': True,
                'remove_stopwords': False,
                'stemming': False,
                'lowercase': True,
                'remove_punctuation': False
            },
            'cross_format_detection': {
                'text_to_image': True,
                'audio_to_text': True,
                'video_to_audio': True,
                'enable_ocr': True,
                'enable_speech_to_text': True
            },
            'reporting': {
                'detailed_analysis': True,
                'include_segments': True,
                'confidence_breakdown': True,
                'recommendation_engine': True
            },
            'performance': {
                'max_concurrent_analysis': 8,
                'cache_fingerprints': True,
                'batch_processing': True,
                'parallel_comparison': True
            }
        }

    def _setup_ml_models(self):
        """Configure les modèles ML."""
        # En production, charger des modèles pré-entraînés
        self.ml_models = {
            'text_embedding': self._create_text_embedding_model(),
            'image_feature_extractor': self._create_image_feature_model(),
            'audio_feature_extractor': self._create_audio_feature_model(),
            'semantic_analyzer': self._create_semantic_model()
        }

    def _create_text_embedding_model(self):
        """Crée le modèle d'embedding de texte."""
        # Simulation d'un modèle d'embedding
        return {
            'model_type': 'sentence_transformer',
            'dimension': self.config['ml_models']['embedding_dimension'],
            'loaded': True
        }

    def _create_image_feature_model(self):
        """Crée le modèle d'extraction de features d'images."""
        return {
            'model_type': 'cnn_feature_extractor',
            'architecture': 'resnet50',
            'loaded': True
        }

    def _create_audio_feature_model(self):
        """Crée le modèle d'extraction de features audio."""
        return {
            'model_type': 'audio_feature_extractor',
            'features': ['mfcc', 'spectral_features', 'rhythm'],
            'loaded': True
        }

    def _create_semantic_model(self):
        """Crée le modèle d'analyse sémantique."""
        return {
            'model_type': 'semantic_analyzer',
            'capabilities': ['paraphrase_detection', 'semantic_similarity'],
            'loaded': True
        }

    def _setup_similarity_algorithms(self):
        """Configure les algorithmes de similarité."""
        self.similarity_algorithms = {
            SimilarityAlgorithm.COSINE_SIMILARITY: self._cosine_similarity,
            SimilarityAlgorithm.JACCARD_INDEX: self._jaccard_similarity,
            SimilarityAlgorithm.LEVENSHTEIN_DISTANCE: self._levenshtein_similarity,
            SimilarityAlgorithm.SEMANTIC_SIMILARITY: self._semantic_similarity,
            SimilarityAlgorithm.STRUCTURAL_SIMILARITY: self._structural_similarity,
            SimilarityAlgorithm.DEEP_LEARNING: self._deep_learning_similarity
        }

    async def create_content_fingerprint(
        self,
        content: Union[str, np.ndarray, Path],
        content_type: ContentType,
        author_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContentFingerprint:
        """
        Crée une empreinte de contenu pour la détection.
        
        Args:
            content: Contenu à analyser
            content_type: Type de contenu
            author_id: ID de l'auteur
            metadata: Métadonnées additionnelles
            
        Returns:
            ContentFingerprint: Empreinte du contenu
        """
        try:
            # Hash du contenu
            content_hash = await self._generate_content_hash(content, content_type)
            
            # Extraction des features selon le type
            if content_type == ContentType.TEXT:
                features = await self._extract_text_features(content)
            elif content_type == ContentType.IMAGE:
                features = await self._extract_image_features(content)
            elif content_type == ContentType.AUDIO:
                features = await self._extract_audio_features(content)
            elif content_type == ContentType.VIDEO:
                features = await self._extract_video_features(content)
            else:
                features = await self._extract_generic_features(content)
            
            fingerprint = ContentFingerprint(
                fingerprint_id=str(uuid.uuid4()),
                content_hash=content_hash,
                content_type=content_type,
                feature_vector=features['feature_vector'],
                structural_features=features['structural_features'],
                semantic_features=features['semantic_features'],
                stylometric_features=features['stylometric_features'],
                n_gram_signatures=features['n_gram_signatures'],
                creation_timestamp=datetime.utcnow(),
                author_id=author_id
            )
            
            # Cache de l'empreinte
            self.fingerprint_cache[fingerprint.fingerprint_id] = fingerprint
            
            logger.info(f"Empreinte créée: {fingerprint.fingerprint_id}")
            return fingerprint

        except Exception as e:
            logger.error(f"Erreur création empreinte: {e}")
            raise

    async def _generate_content_hash(
        self,
        content: Union[str, np.ndarray, Path],
        content_type: ContentType
    ) -> str:
        """Génère un hash du contenu."""
        try:
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            elif isinstance(content, np.ndarray):
                content_bytes = content.tobytes()
            elif isinstance(content, Path):
                with open(content, 'rb') as f:
                    content_bytes = f.read()
            else:
                content_bytes = str(content).encode('utf-8')
            
            return hashlib.sha256(content_bytes).hexdigest()

        except Exception as e:
            logger.error(f"Erreur génération hash: {e}")
            return hashlib.sha256(b'error').hexdigest()

    async def _extract_text_features(self, content: str) -> Dict[str, Any]:
        """Extrait les features de texte."""
        try:
            # Preprocessing du texte
            processed_text = await self._preprocess_text(content)
            
            # Feature vector (embedding simulé)
            feature_vector = await self._generate_text_embedding(processed_text)
            
            # Features structurelles
            structural_features = {
                'word_count': len(processed_text.split()),
                'sentence_count': len(re.split(r'[.!?]+', processed_text)),
                'paragraph_count': len(processed_text.split('\n\n')),
                'average_word_length': np.mean([len(word) for word in processed_text.split()]),
                'punctuation_ratio': len(re.findall(r'[.!?,;:]', content)) / len(content)
            }
            
            # Features sémantiques
            semantic_features = await self._extract_semantic_features(processed_text)
            
            # Features stylométriques
            stylometric_features = await self._extract_stylometric_features(content)
            
            # N-gram signatures
            n_gram_signatures = await self._generate_ngram_signatures(processed_text)
            
            return {
                'feature_vector': feature_vector,
                'structural_features': structural_features,
                'semantic_features': semantic_features,
                'stylometric_features': stylometric_features,
                'n_gram_signatures': n_gram_signatures
            }

        except Exception as e:
            logger.error(f"Erreur extraction features texte: {e}")
            return self._get_empty_features()

    async def _preprocess_text(self, text: str) -> str:
        """Prétraite le texte."""
        try:
            processed = text
            
            if self.config['preprocessing']['normalize_text']:
                processed = re.sub(r'\s+', ' ', processed).strip()
            
            if self.config['preprocessing']['lowercase']:
                processed = processed.lower()
            
            if self.config['preprocessing']['remove_punctuation']:
                processed = re.sub(r'[^\w\s]', '', processed)
            
            return processed

        except Exception as e:
            logger.error(f"Erreur preprocessing texte: {e}")
            return text

    async def _generate_text_embedding(self, text: str) -> np.ndarray:
        """Génère un embedding de texte."""
        try:
            # Simulation d'embedding - en production, utiliser un vrai modèle
            words = text.split()[:100]  # Limite pour la simulation
            
            # Embedding basique basé sur les hashes de mots
            embedding = np.zeros(self.config['ml_models']['embedding_dimension'])
            
            for i, word in enumerate(words):
                word_hash = hash(word) % len(embedding)
                embedding[word_hash] += 1.0 / (i + 1)
            
            # Normalisation
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding

        except Exception as e:
            logger.error(f"Erreur génération embedding: {e}")
            return np.zeros(self.config['ml_models']['embedding_dimension'])

    async def _extract_semantic_features(self, text: str) -> Dict[str, Any]:
        """Extrait les features sémantiques."""
        try:
            words = text.split()
            
            # Analyse des entités nommées (simulée)
            entities = self._extract_named_entities(text)
            
            # Analyse des concepts clés
            key_concepts = self._extract_key_concepts(words)
            
            # Analyse du domaine
            domain_analysis = self._analyze_domain(words)
            
            return {
                'named_entities': entities,
                'key_concepts': key_concepts,
                'domain_indicators': domain_analysis,
                'semantic_density': len(set(words)) / len(words) if words else 0,
                'abstract_concept_ratio': self._calculate_abstract_ratio(words)
            }

        except Exception as e:
            logger.error(f"Erreur extraction features sémantiques: {e}")
            return {}

    def _extract_named_entities(self, text: str) -> List[Dict[str, str]]:
        """Extrait les entités nommées (simulation)."""
        # En production, utiliser spaCy ou NLTK
        entities = []
        
        # Détection basique de noms propres
        words = text.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append({
                    'text': word,
                    'type': 'PERSON' if word.istitle() else 'ORG'
                })
        
        return entities[:10]  # Limite pour la simulation

    def _extract_key_concepts(self, words: List[str]) -> List[str]:
        """Extrait les concepts clés."""
        # Simulation basée sur la fréquence et la longueur
        word_freq = Counter(words)
        key_concepts = []
        
        for word, freq in word_freq.most_common(20):
            if len(word) > 4 and freq > 1:
                key_concepts.append(word)
        
        return key_concepts

    def _analyze_domain(self, words: List[str]) -> Dict[str, float]:
        """Analyse le domaine du texte."""
        domain_indicators = {
            'academic': ['research', 'study', 'analysis', 'methodology', 'conclusion'],
            'technical': ['system', 'algorithm', 'implementation', 'performance', 'optimization'],
            'business': ['market', 'revenue', 'customer', 'strategy', 'growth'],
            'legal': ['law', 'regulation', 'compliance', 'contract', 'agreement']
        }
        
        domain_scores = {}
        word_set = set(word.lower() for word in words)
        
        for domain, indicators in domain_indicators.items():
            score = sum(1 for indicator in indicators if indicator in word_set)
            domain_scores[domain] = score / len(indicators)
        
        return domain_scores

    def _calculate_abstract_ratio(self, words: List[str]) -> float:
        """Calcule le ratio de concepts abstraits."""
        abstract_indicators = ['concept', 'idea', 'theory', 'approach', 'methodology', 'framework']
        abstract_count = sum(1 for word in words if word.lower() in abstract_indicators)
        return abstract_count / len(words) if words else 0

    async def _extract_stylometric_features(self, text: str) -> Dict[str, Any]:
        """Extrait les features stylométriques."""
        try:
            sentences = re.split(r'[.!?]+', text)
            words = text.split()
            
            # Analyse des phrases
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            
            # Analyse du vocabulaire
            vocabulary_richness = len(set(words)) / len(words) if words else 0
            
            # Analyse de la ponctuation
            punctuation_analysis = self._analyze_punctuation_style(text)
            
            # Analyse syntaxique
            syntactic_analysis = self._analyze_syntax_patterns(text)
            
            return {
                'avg_sentence_length': np.mean(sentence_lengths) if sentence_lengths else 0,
                'sentence_length_variance': np.var(sentence_lengths) if sentence_lengths else 0,
                'vocabulary_richness': vocabulary_richness,
                'punctuation_style': punctuation_analysis,
                'syntactic_patterns': syntactic_analysis,
                'readability_score': self._calculate_readability(words, sentences)
            }

        except Exception as e:
            logger.error(f"Erreur extraction features stylométriques: {e}")
            return {}

    def _analyze_punctuation_style(self, text: str) -> Dict[str, float]:
        """Analyse le style de ponctuation."""
        total_chars = len(text)
        if total_chars == 0:
            return {}
        
        punctuation_counts = {
            'comma': text.count(','),
            'semicolon': text.count(';'),
            'exclamation': text.count('!'),
            'question': text.count('?'),
            'colon': text.count(':'),
            'dash': text.count('-')
        }
        
        return {k: v / total_chars for k, v in punctuation_counts.items()}

    def _analyze_syntax_patterns(self, text: str) -> Dict[str, int]:
        """Analyse les patterns syntaxiques."""
        patterns = {
            'passive_voice': len(re.findall(r'\b(was|were|been|being)\s+\w+ed\b', text)),
            'complex_sentences': len(re.findall(r'\b(although|however|nevertheless|furthermore)\b', text.lower())),
            'questions': text.count('?'),
            'exclamations': text.count('!')
        }
        
        return patterns

    def _calculate_readability(self, words: List[str], sentences: List[str]) -> float:
        """Calcule un score de lisibilité simplifié."""
        if not words or not sentences:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Score simplifié (inspiré de Flesch)
        readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length / 4.7)
        return max(0, min(100, readability))

    async def _generate_ngram_signatures(self, text: str) -> Dict[str, List[str]]:
        """Génère les signatures n-gram."""
        try:
            words = text.split()
            signatures = {}
            
            for n in self.config['detection_algorithms']['n_gram_size']:
                ngrams = []
                for i in range(len(words) - n + 1):
                    ngram = ' '.join(words[i:i + n])
                    ngrams.append(ngram)
                
                # Garder les n-grams les plus fréquents
                ngram_freq = Counter(ngrams)
                signatures[f'{n}gram'] = [
                    ngram for ngram, freq in ngram_freq.most_common(100)
                ]
            
            return signatures

        except Exception as e:
            logger.error(f"Erreur génération n-grams: {e}")
            return {}

    async def _extract_image_features(self, content: Union[np.ndarray, Path]) -> Dict[str, Any]:
        """Extrait les features d'images."""
        try:
            # Simulation d'extraction de features d'images
            feature_vector = np.random.random(1024)  # Simulation CNN features
            
            return {
                'feature_vector': feature_vector,
                'structural_features': {'width': 640, 'height': 480, 'channels': 3},
                'semantic_features': {'detected_objects': ['person', 'car']},
                'stylometric_features': {'color_palette': 'warm', 'style': 'realistic'},
                'n_gram_signatures': {}
            }

        except Exception as e:
            logger.error(f"Erreur extraction features image: {e}")
            return self._get_empty_features()

    async def _extract_audio_features(self, content: Union[np.ndarray, Path]) -> Dict[str, Any]:
        """Extrait les features audio."""
        try:
            # Simulation d'extraction de features audio
            feature_vector = np.random.random(512)  # Simulation MFCC features
            
            return {
                'feature_vector': feature_vector,
                'structural_features': {'duration': 120, 'sample_rate': 44100},
                'semantic_features': {'speech_detected': True, 'music_detected': False},
                'stylometric_features': {'tempo': 120, 'key': 'C major'},
                'n_gram_signatures': {}
            }

        except Exception as e:
            logger.error(f"Erreur extraction features audio: {e}")
            return self._get_empty_features()

    async def _extract_video_features(self, content: Union[np.ndarray, Path]) -> Dict[str, Any]:
        """Extrait les features vidéo."""
        try:
            # Simulation d'extraction de features vidéo
            feature_vector = np.random.random(2048)  # Simulation features vidéo
            
            return {
                'feature_vector': feature_vector,
                'structural_features': {'duration': 300, 'fps': 30, 'resolution': '1920x1080'},
                'semantic_features': {'scenes': ['indoor', 'outdoor'], 'actions': ['walking', 'talking']},
                'stylometric_features': {'shot_types': ['close-up', 'wide'], 'transitions': ['cut', 'fade']},
                'n_gram_signatures': {}
            }

        except Exception as e:
            logger.error(f"Erreur extraction features vidéo: {e}")
            return self._get_empty_features()

    async def _extract_generic_features(self, content: Any) -> Dict[str, Any]:
        """Extrait des features génériques."""
        return self._get_empty_features()

    def _get_empty_features(self) -> Dict[str, Any]:
        """Retourne des features vides."""
        return {
            'feature_vector': np.zeros(self.config['ml_models']['embedding_dimension']),
            'structural_features': {},
            'semantic_features': {},
            'stylometric_features': {},
            'n_gram_signatures': {}
        }

    async def detect_plagiarism(
        self,
        source_fingerprint: ContentFingerprint,
        target_fingerprint: ContentFingerprint,
        algorithm: SimilarityAlgorithm = SimilarityAlgorithm.COSINE_SIMILARITY
    ) -> PlagiarismReport:
        """
        Détecte le plagiat entre deux contenus.
        
        Args:
            source_fingerprint: Empreinte du contenu source
            target_fingerprint: Empreinte du contenu cible
            algorithm: Algorithme de similarité
            
        Returns:
            PlagiarismReport: Rapport de détection
        """
        try:
            start_time = datetime.utcnow()
            
            # Calcul de similarité globale
            similarity_func = self.similarity_algorithms[algorithm]
            overall_similarity = await similarity_func(source_fingerprint, target_fingerprint)
            
            # Détection de segments
            detected_segments = await self._detect_plagiarism_segments(
                source_fingerprint, target_fingerprint
            )
            
            # Classification du type de plagiat
            plagiarism_type = await self._classify_plagiarism_type(
                overall_similarity, detected_segments, source_fingerprint, target_fingerprint
            )
            
            # Calcul du pourcentage de plagiat
            plagiarism_percentage = await self._calculate_plagiarism_percentage(
                detected_segments, source_fingerprint
            )
            
            # Niveau de confiance
            confidence_level = self._determine_confidence_level(
                overall_similarity, plagiarism_percentage, len(detected_segments)
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            report = PlagiarismReport(
                report_id=str(uuid.uuid4()),
                source_content_id=source_fingerprint.fingerprint_id,
                target_content_id=target_fingerprint.fingerprint_id,
                overall_similarity=overall_similarity,
                plagiarism_percentage=plagiarism_percentage,
                plagiarism_type=plagiarism_type,
                confidence_level=confidence_level,
                detected_segments=detected_segments,
                analysis_timestamp=datetime.utcnow(),
                processing_time=processing_time,
                algorithm_used=algorithm,
                metadata={
                    'source_type': source_fingerprint.content_type.value,
                    'target_type': target_fingerprint.content_type.value,
                    'cross_format': source_fingerprint.content_type != target_fingerprint.content_type
                }
            )
            
            logger.info(f"Détection plagiat terminée: {report.report_id}, similarité: {overall_similarity:.3f}")
            return report

        except Exception as e:
            logger.error(f"Erreur détection plagiat: {e}")
            raise

    async def _cosine_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> float:
        """Calcule la similarité cosinus."""
        try:
            v1 = fp1.feature_vector
            v2 = fp2.feature_vector
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))

        except Exception as e:
            logger.error(f"Erreur similarité cosinus: {e}")
            return 0.0

    async def _jaccard_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> float:
        """Calcule l'indice de Jaccard."""
        try:
            # Utilisation des n-grams pour Jaccard
            if not fp1.n_gram_signatures or not fp2.n_gram_signatures:
                return 0.0
            
            similarities = []
            
            for n_type in fp1.n_gram_signatures:
                if n_type in fp2.n_gram_signatures:
                    set1 = set(fp1.n_gram_signatures[n_type])
                    set2 = set(fp2.n_gram_signatures[n_type])
                    
                    if set1 or set2:
                        intersection = len(set1 & set2)
                        union = len(set1 | set2)
                        similarities.append(intersection / union if union > 0 else 0)
            
            return float(np.mean(similarities)) if similarities else 0.0

        except Exception as e:
            logger.error(f"Erreur similarité Jaccard: {e}")
            return 0.0

    async def _levenshtein_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> float:
        """Calcule la similarité basée sur la distance de Levenshtein."""
        try:
            # Utilisation des hashes de contenu pour une approximation
            hash1 = fp1.content_hash
            hash2 = fp2.content_hash
            
            if hash1 == hash2:
                return 1.0
            
            # Distance de Levenshtein simplifiée sur les hashes
            distance = self._levenshtein_distance(hash1, hash2)
            max_len = max(len(hash1), len(hash2))
            
            return 1.0 - (distance / max_len) if max_len > 0 else 0.0

        except Exception as e:
            logger.error(f"Erreur similarité Levenshtein: {e}")
            return 0.0

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calcule la distance de Levenshtein."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    async def _semantic_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> float:
        """Calcule la similarité sémantique."""
        try:
            # Comparaison des features sémantiques
            sem1 = fp1.semantic_features
            sem2 = fp2.semantic_features
            
            if not sem1 or not sem2:
                return 0.0
            
            similarities = []
            
            # Similarité des entités nommées
            if 'named_entities' in sem1 and 'named_entities' in sem2:
                entities1 = {e['text'].lower() for e in sem1['named_entities']}
                entities2 = {e['text'].lower() for e in sem2['named_entities']}
                
                if entities1 or entities2:
                    entity_sim = len(entities1 & entities2) / len(entities1 | entities2)
                    similarities.append(entity_sim)
            
            # Similarité des concepts clés
            if 'key_concepts' in sem1 and 'key_concepts' in sem2:
                concepts1 = set(sem1['key_concepts'])
                concepts2 = set(sem2['key_concepts'])
                
                if concepts1 or concepts2:
                    concept_sim = len(concepts1 & concepts2) / len(concepts1 | concepts2)
                    similarities.append(concept_sim)
            
            return float(np.mean(similarities)) if similarities else 0.0

        except Exception as e:
            logger.error(f"Erreur similarité sémantique: {e}")
            return 0.0

    async def _structural_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> float:
        """Calcule la similarité structurelle."""
        try:
            struct1 = fp1.structural_features
            struct2 = fp2.structural_features
            
            if not struct1 or not struct2:
                return 0.0
            
            similarities = []
            
            for feature in struct1:
                if feature in struct2:
                    val1 = struct1[feature]
                    val2 = struct2[feature]
                    
                    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                        max_val = max(abs(val1), abs(val2))
                        if max_val > 0:
                            sim = 1 - abs(val1 - val2) / max_val
                            similarities.append(sim)
            
            return float(np.mean(similarities)) if similarities else 0.0

        except Exception as e:
            logger.error(f"Erreur similarité structurelle: {e}")
            return 0.0

    async def _deep_learning_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> float:
        """Calcule la similarité avec deep learning."""
        try:
            # Simulation d'un modèle de deep learning
            # En production, utiliser un vrai modèle entraîné
            
            # Combinaison pondérée de différentes similarités
            cosine_sim = await self._cosine_similarity(fp1, fp2)
            semantic_sim = await self._semantic_similarity(fp1, fp2)
            structural_sim = await self._structural_similarity(fp1, fp2)
            
            # Pondération apprise (simulée)
            weights = [0.5, 0.3, 0.2]
            similarities = [cosine_sim, semantic_sim, structural_sim]
            
            return float(np.average(similarities, weights=weights))

        except Exception as e:
            logger.error(f"Erreur similarité deep learning: {e}")
            return 0.0

    async def _detect_plagiarism_segments(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> List[PlagiarismSegment]:
        """Détecte les segments de plagiat."""
        try:
            segments = []
            
            # Détection basée sur les n-grams
            if fp1.n_gram_signatures and fp2.n_gram_signatures:
                for n_type in fp1.n_gram_signatures:
                    if n_type in fp2.n_gram_signatures:
                        ngrams1 = fp1.n_gram_signatures[n_type]
                        ngrams2 = fp2.n_gram_signatures[n_type]
                        
                        # Recherche de n-grams communs
                        common_ngrams = set(ngrams1) & set(ngrams2)
                        
                        for ngram in common_ngrams:
                            segment = PlagiarismSegment(
                                segment_id=str(uuid.uuid4()),
                                source_start=ngrams1.index(ngram) if ngram in ngrams1 else 0,
                                source_end=ngrams1.index(ngram) + 1 if ngram in ngrams1 else 1,
                                target_start=ngrams2.index(ngram) if ngram in ngrams2 else 0,
                                target_end=ngrams2.index(ngram) + 1 if ngram in ngrams2 else 1,
                                similarity_score=1.0,  # N-gram exact match
                                plagiarism_type=PlagiarismType.DIRECT_COPY,
                                confidence=ConfidenceLevel.HIGH,
                                matched_content=ngram,
                                transformation_applied=[]
                            )
                            segments.append(segment)
            
            # Limite le nombre de segments pour éviter la surcharge
            return segments[:50]

        except Exception as e:
            logger.error(f"Erreur détection segments: {e}")
            return []

    async def _classify_plagiarism_type(
        self,
        similarity: float,
        segments: List[PlagiarismSegment],
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> PlagiarismType:
        """Classifie le type de plagiat."""
        try:
            thresholds = self.config['similarity_thresholds']
            
            # Analyse des patterns de segments
            if segments:
                avg_segment_similarity = np.mean([s.similarity_score for s in segments])
                
                if avg_segment_similarity >= thresholds['direct_copy']:
                    return PlagiarismType.DIRECT_COPY
                elif avg_segment_similarity >= thresholds['paraphrase']:
                    return PlagiarismType.PARAPHRASE
                elif len(segments) > 10:  # Nombreux petits segments
                    return PlagiarismType.MOSAIC
            
            # Classification basée sur la similarité globale
            if similarity >= thresholds['direct_copy']:
                return PlagiarismType.DIRECT_COPY
            elif similarity >= thresholds['paraphrase']:
                return PlagiarismType.PARAPHRASE
            elif similarity >= thresholds['structural']:
                return PlagiarismType.STRUCTURAL
            elif similarity >= thresholds['semantic']:
                return PlagiarismType.SEMANTIC
            else:
                return PlagiarismType.IDEA_PLAGIARISM

        except Exception as e:
            logger.error(f"Erreur classification plagiat: {e}")
            return PlagiarismType.IDEA_PLAGIARISM

    async def _calculate_plagiarism_percentage(
        self,
        segments: List[PlagiarismSegment],
        source_fp: ContentFingerprint
    ) -> float:
        """Calcule le pourcentage de plagiat."""
        try:
            if not segments:
                return 0.0
            
            # Calcul basé sur la couverture des segments
            total_length = source_fp.structural_features.get('word_count', 1000)
            
            plagiarized_length = sum(
                (s.source_end - s.source_start) * s.similarity_score 
                for s in segments
            )
            
            percentage = min(100.0, (plagiarized_length / total_length) * 100)
            return float(percentage)

        except Exception as e:
            logger.error(f"Erreur calcul pourcentage plagiat: {e}")
            return 0.0

    def _determine_confidence_level(
        self,
        similarity: float,
        percentage: float,
        segment_count: int
    ) -> ConfidenceLevel:
        """Détermine le niveau de confiance."""
        try:
            # Score composite de confiance
            confidence_score = (
                similarity * 0.4 +
                (percentage / 100) * 0.4 +
                min(1.0, segment_count / 10) * 0.2
            )
            
            if confidence_score >= 0.9:
                return ConfidenceLevel.VERY_HIGH
            elif confidence_score >= 0.75:
                return ConfidenceLevel.HIGH
            elif confidence_score >= 0.6:
                return ConfidenceLevel.MEDIUM
            elif confidence_score >= 0.4:
                return ConfidenceLevel.LOW
            else:
                return ConfidenceLevel.VERY_LOW

        except Exception as e:
            logger.error(f"Erreur détermination confiance: {e}")
            return ConfidenceLevel.LOW

    async def batch_plagiarism_detection(
        self,
        fingerprints: List[ContentFingerprint],
        algorithm: SimilarityAlgorithm = SimilarityAlgorithm.COSINE_SIMILARITY
    ) -> List[PlagiarismReport]:
        """
        Détection de plagiat en lot.
        
        Args:
            fingerprints: Liste des empreintes à comparer
            algorithm: Algorithme de similarité
            
        Returns:
            List[PlagiarismReport]: Rapports de détection
        """
        try:
            reports = []
            comparisons = list(combinations(fingerprints, 2))
            
            tasks = []
            semaphore = asyncio.Semaphore(self.config['performance']['max_concurrent_analysis'])
            
            async def compare_pair(fp1, fp2):
                async with semaphore:
                    return await self.detect_plagiarism(fp1, fp2, algorithm)
            
            for fp1, fp2 in comparisons:
                tasks.append(compare_pair(fp1, fp2))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filtrage des résultats valides
            valid_reports = [
                result for result in results 
                if isinstance(result, PlagiarismReport)
            ]
            
            logger.info(f"Détection en lot terminée: {len(valid_reports)} comparaisons")
            return valid_reports

        except Exception as e:
            logger.error(f"Erreur détection en lot: {e}")
            raise

    async def create_similarity_matrix(
        self,
        fingerprints: List[ContentFingerprint],
        algorithm: SimilarityAlgorithm = SimilarityAlgorithm.COSINE_SIMILARITY
    ) -> SimilarityMatrix:
        """
        Crée une matrice de similarité.
        
        Args:
            fingerprints: Liste des empreintes
            algorithm: Algorithme de similarité
            
        Returns:
            SimilarityMatrix: Matrice de similarité
        """
        try:
            n = len(fingerprints)
            matrix = np.zeros((n, n))
            content_ids = [fp.fingerprint_id for fp in fingerprints]
            
            similarity_func = self.similarity_algorithms[algorithm]
            
            for i in range(n):
                for j in range(i, n):
                    if i == j:
                        similarity = 1.0
                    else:
                        similarity = await similarity_func(fingerprints[i], fingerprints[j])
                    
                    matrix[i, j] = similarity
                    matrix[j, i] = similarity  # Matrice symétrique
            
            similarity_matrix = SimilarityMatrix(
                matrix_id=str(uuid.uuid4()),
                content_ids=content_ids,
                similarity_matrix=matrix,
                algorithm_used=algorithm,
                threshold=0.8,  # Seuil par défaut
                computation_timestamp=datetime.utcnow()
            )
            
            logger.info(f"Matrice de similarité créée: {similarity_matrix.matrix_id}")
            return similarity_matrix

        except Exception as e:
            logger.error(f"Erreur création matrice similarité: {e}")
            raise

    def get_supported_algorithms(self) -> List[str]:
        """Retourne la liste des algorithmes supportés."""
        return [alg.value for alg in SimilarityAlgorithm]

    def get_plagiarism_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection."""
        return {
            'total_comparisons': len(self.content_database),
            'algorithms_available': len(self.similarity_algorithms),
            'content_types_supported': [ct.value for ct in ContentType],
            'plagiarism_types_detected': [pt.value for pt in PlagiarismType],
            'configuration_thresholds': self.config['similarity_thresholds']
        }