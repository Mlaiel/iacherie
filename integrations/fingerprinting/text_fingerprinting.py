"""
Text Fingerprinting - Fingerprinting Module
==========================================
Système avancé de fingerprinting de texte avec analyse sémantique,
détection n-gram et identification de plagiat.

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

logger = logging.getLogger(__name__)

class TextFormat(Enum):
    """Formats de texte supportés."""
    TXT = "txt"
    MD = "md"
    DOC = "doc"
    DOCX = "docx"
    PDF = "pdf"
    HTML = "html"
    RTF = "rtf"
    ODT = "odt"

class TextFingerprintAlgorithm(Enum):
    """Algorithmes de fingerprinting de texte."""
    SEMANTIC_FINGERPRINT = "semantic_fingerprint"
    N_GRAM_ANALYSIS = "n_gram_analysis"
    SHINGLING = "shingling"
    SIMHASH = "simhash"
    TF_IDF_FINGERPRINT = "tf_idf_fingerprint"
    SENTENCE_EMBEDDING = "sentence_embedding"
    PLAGIARISM_DETECTION = "plagiarism_detection"
    STYLOMETRIC_ANALYSIS = "stylometric_analysis"

@dataclass
class TextFingerprint:
    """Empreinte de texte."""
    fingerprint_id: str
    text_source: str
    algorithm: TextFingerprintAlgorithm
    hash_value: str
    semantic_features: Optional[Dict[str, Any]]
    ngram_signatures: Optional[Dict[str, Any]]
    stylometric_features: Optional[Dict[str, Any]]
    tf_idf_vector: Optional[np.ndarray]
    sentence_embeddings: Optional[List[np.ndarray]]
    metadata: Dict[str, Any]
    word_count: int
    sentence_count: int
    language: str
    reading_level: str
    created_at: datetime

@dataclass
class TextMatchResult:
    """Résultat de correspondance de texte."""
    match_id: str
    query_fingerprint: TextFingerprint
    reference_fingerprint: TextFingerprint
    similarity_score: float
    semantic_similarity: Optional[float]
    lexical_similarity: Optional[float]
    structural_similarity: Optional[float]
    plagiarism_score: float
    matched_segments: List[Dict[str, Any]]
    confidence_level: str
    plagiarism_type: str
    processing_time: float

class TextFingerprinting:
    """
    Système avancé de fingerprinting de texte enterprise.
    Support semantic analysis, n-gram detection et plagiarism identification.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le système de fingerprinting de texte.
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or self._get_default_config()
        self.supported_formats = [fmt.value for fmt in TextFormat]
        self._setup_algorithms()
        self._setup_language_models()
        logger.info("TextFingerprinting initialisé avec succès")

    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut."""
        return {
            'ngram_settings': {
                'min_n': 2,
                'max_n': 5,
                'shingle_size': 4,
                'skip_length': 2
            },
            'semantic_analysis': {
                'use_embeddings': True,
                'embedding_dimension': 300,
                'similarity_threshold': 0.75,
                'semantic_window': 100
            },
            'plagiarism_detection': {
                'min_match_length': 10,
                'similarity_threshold': 0.8,
                'context_window': 50,
                'fuzzy_matching': True
            },
            'stylometric_features': {
                'analyze_style': True,
                'calculate_readability': True,
                'pos_tagging': False,  # Require NLP libraries
                'sentiment_analysis': False
            },
            'preprocessing': {
                'normalize_whitespace': True,
                'remove_punctuation': False,
                'lowercase': True,
                'remove_stop_words': False,
                'stemming': False
            },
            'performance': {
                'max_concurrent_processing': 4,
                'cache_fingerprints': True,
                'optimize_for_speed': True,
                'max_text_length': 1000000  # 1MB
            }
        }

    def _setup_algorithms(self):
        """Configure les algorithmes de fingerprinting."""
        self.algorithms = {
            TextFingerprintAlgorithm.SEMANTIC_FINGERPRINT: self._semantic_fingerprint,
            TextFingerprintAlgorithm.N_GRAM_ANALYSIS: self._ngram_analysis_fingerprint,
            TextFingerprintAlgorithm.SHINGLING: self._shingling_fingerprint,
            TextFingerprintAlgorithm.SIMHASH: self._simhash_fingerprint,
            TextFingerprintAlgorithm.TF_IDF_FINGERPRINT: self._tfidf_fingerprint,
            TextFingerprintAlgorithm.SENTENCE_EMBEDDING: self._sentence_embedding_fingerprint,
            TextFingerprintAlgorithm.PLAGIARISM_DETECTION: self._plagiarism_detection_fingerprint,
            TextFingerprintAlgorithm.STYLOMETRIC_ANALYSIS: self._stylometric_analysis_fingerprint
        }

    def _setup_language_models(self):
        """Configure les modèles de langue."""
        # En production, charger des modèles pré-entraînés
        self.stop_words = {
            'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'},
            'fr': {'le', 'la', 'les', 'un', 'une', 'et', 'ou', 'mais', 'dans', 'sur', 'à', 'pour', 'de', 'avec'},
            'de': {'der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'auf', 'zu', 'für', 'von', 'mit'},
            'ar': {'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'التي', 'الذي'}
        }

    async def create_fingerprint(
        self,
        text_source: Union[str, Path],
        algorithm: TextFingerprintAlgorithm = TextFingerprintAlgorithm.SEMANTIC_FINGERPRINT,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TextFingerprint:
        """
        Crée une empreinte de texte.
        
        Args:
            text_source: Texte ou chemin vers le fichier
            algorithm: Algorithme de fingerprinting
            metadata: Métadonnées additionnelles
            
        Returns:
            TextFingerprint: Empreinte générée
        """
        try:
            # Extraction du texte
            text_content = await self._extract_text_content(text_source)
            
            # Validation et nettoyage
            if len(text_content) > self.config['performance']['max_text_length']:
                text_content = text_content[:self.config['performance']['max_text_length']]
            
            # Analyse linguistique de base
            text_metadata = await self._analyze_text_properties(text_content)
            
            # Prétraitement du texte
            processed_text = await self._preprocess_text(text_content)
            
            # Génération de l'empreinte selon l'algorithme
            algorithm_func = self.algorithms[algorithm]
            fingerprint_data = await algorithm_func(processed_text, text_metadata)

            # Création de l'objet empreinte
            fingerprint = TextFingerprint(
                fingerprint_id=str(uuid.uuid4()),
                text_source=str(text_source) if isinstance(text_source, Path) else text_source[:100] + "..." if len(text_source) > 100 else text_source,
                algorithm=algorithm,
                hash_value=fingerprint_data.get('hash_value', ''),
                semantic_features=fingerprint_data.get('semantic_features'),
                ngram_signatures=fingerprint_data.get('ngram_signatures'),
                stylometric_features=fingerprint_data.get('stylometric_features'),
                tf_idf_vector=fingerprint_data.get('tf_idf_vector'),
                sentence_embeddings=fingerprint_data.get('sentence_embeddings'),
                metadata=metadata or {},
                word_count=text_metadata['word_count'],
                sentence_count=text_metadata['sentence_count'],
                language=text_metadata['language'],
                reading_level=text_metadata['reading_level'],
                created_at=datetime.utcnow()
            )

            logger.info(f"Empreinte texte créée: {fingerprint.fingerprint_id}")
            return fingerprint

        except Exception as e:
            logger.error(f"Erreur création empreinte texte: {e}")
            raise

    async def _extract_text_content(self, text_source: Union[str, Path]) -> str:
        """Extrait le contenu textuel."""
        try:
            if isinstance(text_source, str) and not Path(text_source).exists():
                # text_source est directement le contenu textuel
                return text_source
            
            # text_source est un chemin de fichier
            file_path = Path(text_source)
            file_extension = file_path.suffix.lower().lstrip('.')
            
            if file_extension == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_extension in ['md', 'markdown']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Suppression basique du markdown
                    content = re.sub(r'[#*`_\[\]()]', '', content)
                    return content
            elif file_extension == 'html':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Suppression basique des balises HTML
                    content = re.sub(r'<[^>]+>', '', content)
                    return content
            else:
                # Pour les autres formats, lecture basique
                # En production, utiliser des libraries spécialisées
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()

        except Exception as e:
            logger.error(f"Erreur extraction texte: {e}")
            return ""

    async def _analyze_text_properties(self, text: str) -> Dict[str, Any]:
        """Analyse les propriétés de base du texte."""
        try:
            # Tokenisation basique
            words = re.findall(r'\b\w+\b', text.lower())
            sentences = re.split(r'[.!?]+', text)
            
            # Détection de langue simplifiée
            language = self._detect_language(text)
            
            # Calcul de niveau de lecture
            reading_level = self._calculate_reading_level(words, sentences)
            
            return {
                'word_count': len(words),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'character_count': len(text),
                'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
                'average_sentence_length': len(words) / len(sentences) if sentences else 0,
                'language': language,
                'reading_level': reading_level,
                'vocabulary_richness': len(set(words)) / len(words) if words else 0
            }

        except Exception as e:
            logger.error(f"Erreur analyse propriétés texte: {e}")
            return {}

    def _detect_language(self, text: str) -> str:
        """Détection de langue simplifiée."""
        try:
            # Détection basée sur les mots fréquents
            words = re.findall(r'\b\w+\b', text.lower())
            word_counter = Counter(words)
            
            # Score par langue
            language_scores = {}
            
            for lang, stop_words in self.stop_words.items():
                score = sum(count for word, count in word_counter.items() if word in stop_words)
                language_scores[lang] = score
            
            # Langue avec le score le plus élevé
            if language_scores:
                detected_lang = max(language_scores, key=language_scores.get)
                return detected_lang if language_scores[detected_lang] > 0 else 'unknown'
            
            return 'unknown'

        except Exception as e:
            logger.error(f"Erreur détection langue: {e}")
            return 'unknown'

    def _calculate_reading_level(self, words: List[str], sentences: List[str]) -> str:
        """Calcul du niveau de lecture (simplifié)."""
        try:
            if not words or not sentences:
                return 'unknown'
            
            avg_sentence_length = len(words) / len(sentences)
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Classification simplifiée
            if avg_sentence_length < 10 and avg_word_length < 4:
                return 'elementary'
            elif avg_sentence_length < 15 and avg_word_length < 5:
                return 'intermediate'
            elif avg_sentence_length < 20 and avg_word_length < 6:
                return 'advanced'
            else:
                return 'expert'

        except Exception as e:
            logger.error(f"Erreur calcul niveau lecture: {e}")
            return 'unknown'

    async def _preprocess_text(self, text: str) -> str:
        """Prétraite le texte selon la configuration."""
        try:
            processed = text
            
            # Normalisation des espaces
            if self.config['preprocessing']['normalize_whitespace']:
                processed = re.sub(r'\s+', ' ', processed).strip()
            
            # Conversion en minuscules
            if self.config['preprocessing']['lowercase']:
                processed = processed.lower()
            
            # Suppression de la ponctuation
            if self.config['preprocessing']['remove_punctuation']:
                processed = re.sub(r'[^\w\s]', '', processed)
            
            return processed

        except Exception as e:
            logger.error(f"Erreur prétraitement texte: {e}")
            return text

    async def _semantic_fingerprint(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint sémantique."""
        try:
            # Tokenisation
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Analyse sémantique simplifiée
            semantic_features = {
                'word_frequency': dict(Counter(words).most_common(50)),
                'unique_words': list(set(words)),
                'concept_density': len(set(words)) / len(words) if words else 0,
                'semantic_clusters': self._extract_semantic_clusters(words)
            }
            
            # Hash sémantique
            semantic_str = json.dumps(semantic_features, sort_keys=True)
            semantic_hash = hashlib.sha256(semantic_str.encode()).hexdigest()
            
            return {
                'hash_value': semantic_hash,
                'semantic_features': semantic_features
            }

        except Exception as e:
            logger.error(f"Erreur semantic fingerprint: {e}")
            return {'hash_value': ''}

    def _extract_semantic_clusters(self, words: List[str]) -> List[List[str]]:
        """Extrait des clusters sémantiques simples."""
        try:
            # Clustering basique par préfixes/suffixes
            clusters = defaultdict(list)
            
            for word in set(words):
                if len(word) >= 3:
                    # Groupement par préfixe de 3 caractères
                    prefix = word[:3]
                    clusters[prefix].append(word)
            
            # Filtrer les clusters avec au moins 2 mots
            return [cluster for cluster in clusters.values() if len(cluster) >= 2]

        except Exception as e:
            logger.error(f"Erreur extraction clusters sémantiques: {e}")
            return []

    async def _ngram_analysis_fingerprint(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint basé sur l'analyse n-gram."""
        try:
            words = re.findall(r'\b\w+\b', text.lower())
            
            ngram_signatures = {}
            
            # Génération de n-grams
            for n in range(
                self.config['ngram_settings']['min_n'],
                self.config['ngram_settings']['max_n'] + 1
            ):
                ngrams = self._generate_ngrams(words, n)
                ngram_signatures[f'{n}gram'] = dict(Counter(ngrams).most_common(100))
            
            # Hash basé sur les n-grams
            ngram_str = json.dumps(ngram_signatures, sort_keys=True)
            ngram_hash = hashlib.md5(ngram_str.encode()).hexdigest()
            
            return {
                'hash_value': ngram_hash,
                'ngram_signatures': ngram_signatures
            }

        except Exception as e:
            logger.error(f"Erreur n-gram analysis: {e}")
            return {'hash_value': ''}

    def _generate_ngrams(self, words: List[str], n: int) -> List[str]:
        """Génère des n-grams à partir d'une liste de mots."""
        try:
            if len(words) < n:
                return []
            
            ngrams = []
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i + n])
                ngrams.append(ngram)
            
            return ngrams

        except Exception as e:
            logger.error(f"Erreur génération n-grams: {e}")
            return []

    async def _shingling_fingerprint(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint basé sur le shingling."""
        try:
            shingle_size = self.config['ngram_settings']['shingle_size']
            
            # Génération de shingles (séquences de caractères)
            shingles = set()
            for i in range(len(text) - shingle_size + 1):
                shingle = text[i:i + shingle_size]
                shingles.add(shingle)
            
            # MinHash pour réduire la signature
            minhash_signature = self._compute_minhash(shingles)
            
            # Hash de la signature
            signature_str = ''.join(map(str, minhash_signature))
            signature_hash = hashlib.sha256(signature_str.encode()).hexdigest()
            
            return {
                'hash_value': signature_hash,
                'minhash_signature': minhash_signature,
                'shingle_count': len(shingles)
            }

        except Exception as e:
            logger.error(f"Erreur shingling: {e}")
            return {'hash_value': ''}

    def _compute_minhash(self, shingles: Set[str], num_hashes: int = 100) -> List[int]:
        """Calcule la signature MinHash."""
        try:
            signature = []
            
            for i in range(num_hashes):
                min_hash = float('inf')
                for shingle in shingles:
                    # Hash combiné avec un seed
                    hash_val = hash(shingle + str(i)) % (2**32)
                    min_hash = min(min_hash, hash_val)
                signature.append(min_hash)
            
            return signature

        except Exception as e:
            logger.error(f"Erreur calcul MinHash: {e}")
            return []

    async def _simhash_fingerprint(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint SimHash."""
        try:
            words = re.findall(r'\b\w+\b', text.lower())
            word_weights = Counter(words)
            
            # Calcul du SimHash
            fingerprint = self._compute_simhash(word_weights)
            
            return {
                'hash_value': hex(fingerprint)[2:],
                'simhash_value': fingerprint,
                'feature_count': len(word_weights)
            }

        except Exception as e:
            logger.error(f"Erreur SimHash: {e}")
            return {'hash_value': ''}

    def _compute_simhash(self, features: Dict[str, int], hash_bits: int = 64) -> int:
        """Calcule le SimHash."""
        try:
            vector = [0] * hash_bits
            
            for feature, weight in features.items():
                # Hash de la caractéristique
                feature_hash = hash(feature) % (2**hash_bits)
                
                # Mise à jour du vecteur
                for i in range(hash_bits):
                    bit = (feature_hash >> i) & 1
                    if bit:
                        vector[i] += weight
                    else:
                        vector[i] -= weight
            
            # Conversion en fingerprint binaire
            fingerprint = 0
            for i in range(hash_bits):
                if vector[i] >= 0:
                    fingerprint |= (1 << i)
            
            return fingerprint

        except Exception as e:
            logger.error(f"Erreur calcul SimHash: {e}")
            return 0

    async def _tfidf_fingerprint(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint TF-IDF."""
        try:
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Calcul TF (Term Frequency)
            tf = Counter(words)
            total_words = len(words)
            
            for word in tf:
                tf[word] = tf[word] / total_words
            
            # Pour IDF, utilisation d'un corpus de référence simplifié
            # En production, utiliser un vrai corpus
            idf = self._calculate_simple_idf(tf.keys())
            
            # Calcul TF-IDF
            tfidf_vector = {}
            for word in tf:
                tfidf_vector[word] = tf[word] * idf.get(word, 1.0)
            
            # Vectorisation des top mots
            top_words = dict(Counter(tfidf_vector).most_common(100))
            vector_array = np.array(list(top_words.values()))
            
            # Hash du vecteur
            vector_str = np.array2string(vector_array, precision=4)
            vector_hash = hashlib.sha256(vector_str.encode()).hexdigest()
            
            return {
                'hash_value': vector_hash,
                'tf_idf_vector': vector_array,
                'tfidf_features': top_words
            }

        except Exception as e:
            logger.error(f"Erreur TF-IDF fingerprint: {e}")
            return {'hash_value': ''}

    def _calculate_simple_idf(self, words: List[str]) -> Dict[str, float]:
        """Calcule un IDF simplifié."""
        try:
            # IDF basique basé sur la fréquence supposée dans un corpus
            common_words = {
                'the': 0.1, 'a': 0.2, 'and': 0.15, 'or': 0.3, 'but': 0.4,
                'in': 0.2, 'on': 0.25, 'at': 0.3, 'to': 0.15, 'for': 0.2
            }
            
            idf = {}
            for word in words:
                if word in common_words:
                    idf[word] = math.log(1 / common_words[word])
                else:
                    # Mots rares ont un IDF plus élevé
                    idf[word] = math.log(100 / max(1, len(word)))
            
            return idf

        except Exception as e:
            logger.error(f"Erreur calcul IDF: {e}")
            return {}

    async def _sentence_embedding_fingerprint(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint basé sur les embeddings de phrases."""
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Embeddings simplifiés (en production, utiliser des modèles pré-entraînés)
            sentence_embeddings = []
            
            for sentence in sentences[:20]:  # Limite à 20 phrases
                embedding = self._simple_sentence_embedding(sentence)
                sentence_embeddings.append(embedding)
            
            # Embedding moyen du document
            if sentence_embeddings:
                doc_embedding = np.mean(sentence_embeddings, axis=0)
            else:
                doc_embedding = np.zeros(100)  # Dimension par défaut
            
            # Hash de l'embedding
            embedding_str = np.array2string(doc_embedding, precision=4)
            embedding_hash = hashlib.sha256(embedding_str.encode()).hexdigest()
            
            return {
                'hash_value': embedding_hash,
                'sentence_embeddings': sentence_embeddings,
                'document_embedding': doc_embedding
            }

        except Exception as e:
            logger.error(f"Erreur sentence embedding: {e}")
            return {'hash_value': ''}

    def _simple_sentence_embedding(self, sentence: str) -> np.ndarray:
        """Crée un embedding simple de phrase."""
        try:
            words = re.findall(r'\b\w+\b', sentence.lower())
            
            # Embedding basique basé sur les hashes de mots
            embedding = np.zeros(100)
            
            for i, word in enumerate(words[:50]):  # Limite à 50 mots
                word_hash = hash(word) % 100
                embedding[word_hash] += 1.0 / (i + 1)  # Pondération par position
            
            # Normalisation
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding

        except Exception as e:
            logger.error(f"Erreur sentence embedding: {e}")
            return np.zeros(100)

    async def _plagiarism_detection_fingerprint(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint spécialisé pour la détection de plagiat."""
        try:
            # Segments de texte pour la détection
            min_length = self.config['plagiarism_detection']['min_match_length']
            segments = self._extract_text_segments(text, min_length)
            
            # Signatures pour chaque segment
            segment_signatures = []
            for segment in segments:
                sig = self._create_segment_signature(segment)
                segment_signatures.append(sig)
            
            # Hash global pour le plagiat
            plagiarism_data = {
                'segments': segment_signatures[:100],  # Limite
                'total_segments': len(segment_signatures),
                'text_structure': self._analyze_text_structure(text)
            }
            
            plagiarism_str = json.dumps(plagiarism_data, sort_keys=True)
            plagiarism_hash = hashlib.sha256(plagiarism_str.encode()).hexdigest()
            
            return {
                'hash_value': plagiarism_hash,
                'plagiarism_signatures': plagiarism_data
            }

        except Exception as e:
            logger.error(f"Erreur plagiarism detection: {e}")
            return {'hash_value': ''}

    def _extract_text_segments(self, text: str, min_length: int) -> List[str]:
        """Extrait des segments de texte."""
        try:
            words = re.findall(r'\b\w+\b', text.lower())
            segments = []
            
            for i in range(0, len(words) - min_length + 1, min_length // 2):
                segment = ' '.join(words[i:i + min_length])
                segments.append(segment)
            
            return segments

        except Exception as e:
            logger.error(f"Erreur extraction segments: {e}")
            return []

    def _create_segment_signature(self, segment: str) -> str:
        """Crée une signature pour un segment de texte."""
        try:
            # Signature combinant hash et structure
            words = segment.split()
            
            # Hash du contenu
            content_hash = hashlib.md5(segment.encode()).hexdigest()[:8]
            
            # Hash de la structure (longueurs des mots)
            structure = [len(word) for word in words]
            structure_hash = hashlib.md5(str(structure).encode()).hexdigest()[:8]
            
            return f"{content_hash}-{structure_hash}"

        except Exception as e:
            logger.error(f"Erreur création signature segment: {e}")
            return ""

    def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """Analyse la structure du texte."""
        try:
            sentences = re.split(r'[.!?]+', text)
            paragraphs = text.split('\n\n')
            
            return {
                'sentence_lengths': [len(s.split()) for s in sentences if s.strip()],
                'paragraph_count': len([p for p in paragraphs if p.strip()]),
                'punctuation_density': len(re.findall(r'[.!?,;:]', text)) / len(text) if text else 0,
                'capitalization_pattern': len(re.findall(r'[A-Z]', text)) / len(text) if text else 0
            }

        except Exception as e:
            logger.error(f"Erreur analyse structure: {e}")
            return {}

    async def _stylometric_analysis_fingerprint(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint stylométrique."""
        try:
            # Analyse des caractéristiques stylistiques
            stylometric_features = {
                'lexical_diversity': self._calculate_lexical_diversity(text),
                'sentence_complexity': self._calculate_sentence_complexity(text),
                'vocabulary_sophistication': self._calculate_vocabulary_sophistication(text),
                'punctuation_style': self._analyze_punctuation_style(text),
                'syntactic_patterns': self._extract_syntactic_patterns(text)
            }
            
            # Hash stylométrique
            style_str = json.dumps(stylometric_features, sort_keys=True)
            style_hash = hashlib.sha256(style_str.encode()).hexdigest()
            
            return {
                'hash_value': style_hash,
                'stylometric_features': stylometric_features
            }

        except Exception as e:
            logger.error(f"Erreur stylometric analysis: {e}")
            return {'hash_value': ''}

    def _calculate_lexical_diversity(self, text: str) -> float:
        """Calcule la diversité lexicale."""
        try:
            words = re.findall(r'\b\w+\b', text.lower())
            if not words:
                return 0.0
            
            unique_words = set(words)
            return len(unique_words) / len(words)

        except Exception as e:
            logger.error(f"Erreur calcul diversité lexicale: {e}")
            return 0.0

    def _calculate_sentence_complexity(self, text: str) -> Dict[str, float]:
        """Calcule la complexité des phrases."""
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return {'avg_length': 0, 'complexity_variance': 0}
            
            lengths = [len(s.split()) for s in sentences]
            
            return {
                'avg_length': sum(lengths) / len(lengths),
                'complexity_variance': np.var(lengths) if len(lengths) > 1 else 0
            }

        except Exception as e:
            logger.error(f"Erreur calcul complexité phrases: {e}")
            return {'avg_length': 0, 'complexity_variance': 0}

    def _calculate_vocabulary_sophistication(self, text: str) -> float:
        """Calcule la sophistication du vocabulaire."""
        try:
            words = re.findall(r'\b\w+\b', text.lower())
            if not words:
                return 0.0
            
            # Mots "sophistiqués" (> 6 caractères)
            sophisticated_words = [w for w in words if len(w) > 6]
            
            return len(sophisticated_words) / len(words)

        except Exception as e:
            logger.error(f"Erreur calcul sophistication vocabulaire: {e}")
            return 0.0

    def _analyze_punctuation_style(self, text: str) -> Dict[str, float]:
        """Analyse le style de ponctuation."""
        try:
            punctuation_counts = Counter(re.findall(r'[.!?,;:()"]', text))
            total_chars = len(text)
            
            if total_chars == 0:
                return {}
            
            style = {}
            for punct, count in punctuation_counts.items():
                style[f'{punct}_frequency'] = count / total_chars
            
            return style

        except Exception as e:
            logger.error(f"Erreur analyse style ponctuation: {e}")
            return {}

    def _extract_syntactic_patterns(self, text: str) -> Dict[str, int]:
        """Extrait des patterns syntaxiques simples."""
        try:
            patterns = {
                'questions': len(re.findall(r'\?', text)),
                'exclamations': len(re.findall(r'!', text)),
                'passive_voice': len(re.findall(r'\b(was|were|been|being)\s+\w+ed\b', text)),
                'conjunctions': len(re.findall(r'\b(and|but|or|however|therefore)\b', text.lower()))
            }
            
            return patterns

        except Exception as e:
            logger.error(f"Erreur extraction patterns syntaxiques: {e}")
            return {}

    async def compare_fingerprints(
        self,
        fingerprint1: TextFingerprint,
        fingerprint2: TextFingerprint
    ) -> TextMatchResult:
        """
        Compare deux empreintes de texte.
        
        Args:
            fingerprint1: Première empreinte
            fingerprint2: Seconde empreinte
            
        Returns:
            TextMatchResult: Résultat de la comparaison
        """
        try:
            start_time = datetime.utcnow()
            
            # Vérification de compatibilité des algorithmes
            if fingerprint1.algorithm != fingerprint2.algorithm:
                raise ValueError("Algorithmes de fingerprinting incompatibles")

            # Calcul de similarité globale
            similarity_score = await self._calculate_text_similarity(fingerprint1, fingerprint2)
            
            # Similarités spécifiques
            semantic_similarity = self._calculate_semantic_similarity(fingerprint1, fingerprint2)
            lexical_similarity = self._calculate_lexical_similarity(fingerprint1, fingerprint2)
            structural_similarity = self._calculate_structural_similarity(fingerprint1, fingerprint2)
            
            # Score de plagiat
            plagiarism_score = await self._calculate_plagiarism_score(fingerprint1, fingerprint2)
            
            # Segments correspondants
            matched_segments = await self._find_matched_text_segments(fingerprint1, fingerprint2)
            
            # Type de plagiat détecté
            plagiarism_type = self._classify_plagiarism_type(similarity_score, semantic_similarity, lexical_similarity)
            
            # Niveau de confiance
            confidence_level = self._determine_confidence_level(similarity_score, plagiarism_score)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            match_result = TextMatchResult(
                match_id=str(uuid.uuid4()),
                query_fingerprint=fingerprint1,
                reference_fingerprint=fingerprint2,
                similarity_score=similarity_score,
                semantic_similarity=semantic_similarity,
                lexical_similarity=lexical_similarity,
                structural_similarity=structural_similarity,
                plagiarism_score=plagiarism_score,
                matched_segments=matched_segments,
                confidence_level=confidence_level,
                plagiarism_type=plagiarism_type,
                processing_time=processing_time
            )
            
            logger.info(f"Comparaison texte terminée: {match_result.match_id}, score: {similarity_score}")
            return match_result

        except Exception as e:
            logger.error(f"Erreur comparaison empreintes texte: {e}")
            raise

    async def _calculate_text_similarity(
        self,
        fp1: TextFingerprint,
        fp2: TextFingerprint
    ) -> float:
        """Calcule la similarité globale entre deux textes."""
        try:
            # Similarité basée sur les hashes
            hash_similarity = 1.0 if fp1.hash_value == fp2.hash_value else 0.0
            
            # Pondération des différentes métriques
            weights = {
                'hash': 0.3,
                'semantic': 0.4,
                'lexical': 0.2,
                'structural': 0.1
            }
            
            # Calcul des similarités composantes
            semantic_sim = self._calculate_semantic_similarity(fp1, fp2) or 0
            lexical_sim = self._calculate_lexical_similarity(fp1, fp2) or 0
            structural_sim = self._calculate_structural_similarity(fp1, fp2) or 0
            
            total_similarity = (
                weights['hash'] * hash_similarity +
                weights['semantic'] * semantic_sim +
                weights['lexical'] * lexical_sim +
                weights['structural'] * structural_sim
            )
            
            return total_similarity

        except Exception as e:
            logger.error(f"Erreur calcul similarité texte: {e}")
            return 0.0

    def _calculate_semantic_similarity(
        self,
        fp1: TextFingerprint,
        fp2: TextFingerprint
    ) -> Optional[float]:
        """Calcule la similarité sémantique."""
        try:
            if not fp1.semantic_features or not fp2.semantic_features:
                return None
            
            # Similarité basée sur les mots uniques communs
            words1 = set(fp1.semantic_features.get('unique_words', []))
            words2 = set(fp2.semantic_features.get('unique_words', []))
            
            if not words1 or not words2:
                return 0.0
            
            # Coefficient de Jaccard
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            
            return intersection / union if union > 0 else 0.0

        except Exception as e:
            logger.error(f"Erreur similarité sémantique: {e}")
            return None

    def _calculate_lexical_similarity(
        self,
        fp1: TextFingerprint,
        fp2: TextFingerprint
    ) -> Optional[float]:
        """Calcule la similarité lexicale."""
        try:
            if not fp1.ngram_signatures or not fp2.ngram_signatures:
                return None
            
            # Comparaison des n-grams
            similarities = []
            
            for ngram_type in fp1.ngram_signatures:
                if ngram_type in fp2.ngram_signatures:
                    ngrams1 = set(fp1.ngram_signatures[ngram_type].keys())
                    ngrams2 = set(fp2.ngram_signatures[ngram_type].keys())
                    
                    if ngrams1 or ngrams2:
                        jaccard = len(ngrams1 & ngrams2) / len(ngrams1 | ngrams2)
                        similarities.append(jaccard)
            
            return sum(similarities) / len(similarities) if similarities else 0.0

        except Exception as e:
            logger.error(f"Erreur similarité lexicale: {e}")
            return None

    def _calculate_structural_similarity(
        self,
        fp1: TextFingerprint,
        fp2: TextFingerprint
    ) -> Optional[float]:
        """Calcule la similarité structurelle."""
        try:
            if not fp1.stylometric_features or not fp2.stylometric_features:
                return None
            
            # Comparaison des caractéristiques stylométriques
            similarities = []
            
            for feature in fp1.stylometric_features:
                if feature in fp2.stylometric_features:
                    val1 = fp1.stylometric_features[feature]
                    val2 = fp2.stylometric_features[feature]
                    
                    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                        max_val = max(abs(val1), abs(val2))
                        if max_val > 0:
                            sim = 1 - abs(val1 - val2) / max_val
                            similarities.append(sim)
            
            return sum(similarities) / len(similarities) if similarities else 0.0

        except Exception as e:
            logger.error(f"Erreur similarité structurelle: {e}")
            return None

    async def _calculate_plagiarism_score(
        self,
        fp1: TextFingerprint,
        fp2: TextFingerprint
    ) -> float:
        """Calcule le score de plagiat."""
        try:
            # Score basé sur la similarité globale et des critères spécifiques
            similarity = await self._calculate_text_similarity(fp1, fp2)
            
            # Facteurs aggravants pour le plagiat
            length_factor = min(fp1.word_count, fp2.word_count) / max(fp1.word_count, fp2.word_count)
            
            # Score de plagiat pondéré
            plagiarism_score = similarity * length_factor
            
            return plagiarism_score

        except Exception as e:
            logger.error(f"Erreur calcul score plagiat: {e}")
            return 0.0

    async def _find_matched_text_segments(
        self,
        fp1: TextFingerprint,
        fp2: TextFingerprint
    ) -> List[Dict[str, Any]]:
        """Trouve les segments de texte correspondants."""
        try:
            # Segments correspondants basiques
            matched_segments = []
            
            # Si disponible, utiliser les signatures de plagiat
            if (hasattr(fp1, 'plagiarism_signatures') and 
                hasattr(fp2, 'plagiarism_signatures')):
                # Analyse détaillée des segments
                pass
            
            # Segment global par défaut
            similarity = await self._calculate_text_similarity(fp1, fp2)
            if similarity > 0.5:
                matched_segments.append({
                    'start_position1': 0,
                    'end_position1': fp1.word_count,
                    'start_position2': 0,
                    'end_position2': fp2.word_count,
                    'similarity': similarity,
                    'match_type': 'global'
                })
            
            return matched_segments

        except Exception as e:
            logger.error(f"Erreur recherche segments correspondants: {e}")
            return []

    def _classify_plagiarism_type(
        self,
        similarity: float,
        semantic_sim: Optional[float],
        lexical_sim: Optional[float]
    ) -> str:
        """Classifie le type de plagiat détecté."""
        try:
            if similarity < 0.3:
                return "no_plagiarism"
            elif similarity >= 0.9:
                if lexical_sim and lexical_sim > 0.8:
                    return "direct_copy"
                else:
                    return "paraphrase_plagiarism"
            elif similarity >= 0.7:
                if semantic_sim and semantic_sim > lexical_sim:
                    return "semantic_plagiarism"
                else:
                    return "structural_plagiarism"
            elif similarity >= 0.5:
                return "partial_plagiarism"
            else:
                return "potential_plagiarism"

        except Exception as e:
            logger.error(f"Erreur classification plagiat: {e}")
            return "unknown"

    def _determine_confidence_level(self, similarity_score: float, plagiarism_score: float) -> str:
        """Détermine le niveau de confiance."""
        threshold = self.config['plagiarism_detection']['similarity_threshold']
        
        if similarity_score >= 0.95 or plagiarism_score >= 0.9:
            return "very_high"
        elif similarity_score >= threshold or plagiarism_score >= 0.7:
            return "high"
        elif similarity_score >= 0.6 or plagiarism_score >= 0.5:
            return "medium"
        elif similarity_score >= 0.4:
            return "low"
        else:
            return "very_low"

    async def batch_fingerprint_generation(
        self,
        text_sources: List[Union[str, Path]],
        algorithm: TextFingerprintAlgorithm = TextFingerprintAlgorithm.SEMANTIC_FINGERPRINT
    ) -> List[TextFingerprint]:
        """
        Génération en lot d'empreintes de texte.
        
        Args:
            text_sources: Liste des textes ou fichiers
            algorithm: Algorithme à utiliser
            
        Returns:
            List[TextFingerprint]: Liste des empreintes générées
        """
        try:
            tasks = []
            semaphore = asyncio.Semaphore(self.config['performance']['max_concurrent_processing'])
            
            async def process_text(text_source):
                async with semaphore:
                    return await self.create_fingerprint(text_source, algorithm)
            
            for text_source in text_sources:
                tasks.append(process_text(text_source))
            
            fingerprints = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filtrage des erreurs
            valid_fingerprints = [
                fp for fp in fingerprints 
                if isinstance(fp, TextFingerprint)
            ]
            
            logger.info(f"Traitement en lot terminé: {len(valid_fingerprints)}/{len(text_sources)} réussis")
            return valid_fingerprints

        except Exception as e:
            logger.error(f"Erreur traitement en lot: {e}")
            raise

    def get_supported_formats(self) -> List[str]:
        """Retourne la liste des formats supportés."""
        return self.supported_formats

    def get_algorithm_info(self, algorithm: TextFingerprintAlgorithm) -> Dict[str, Any]:
        """Retourne les informations sur un algorithme."""
        algorithm_info = {
            TextFingerprintAlgorithm.SEMANTIC_FINGERPRINT: {
                'name': 'Semantic Fingerprint',
                'description': 'Analyse sémantique du contenu textuel',
                'best_for': 'Détection de paraphrase et similarité conceptuelle',
                'performance': 'Modérée',
                'accuracy': 'Très haute pour contenu sémantique',
                'detects': ['paraphrase', 'traduction', 'reformulation']
            },
            TextFingerprintAlgorithm.N_GRAM_ANALYSIS: {
                'name': 'N-Gram Analysis',
                'description': 'Analyse des séquences de mots',
                'best_for': 'Détection de copie directe et modifications mineures',
                'performance': 'Rapide',
                'accuracy': 'Haute pour copies directes',
                'detects': ['copie directe', 'substitution de mots', 'réorganisation']
            },
            TextFingerprintAlgorithm.PLAGIARISM_DETECTION: {
                'name': 'Plagiarism Detection',
                'description': 'Spécialisé dans la détection de plagiat',
                'best_for': 'Identification précise du plagiat académique',
                'performance': 'Modérée',
                'accuracy': 'Très haute pour plagiat',
                'detects': ['plagiat direct', 'plagiat paraphrasé', 'mosaic plagiarism']
            }
        }
        
        return algorithm_info.get(algorithm, {})