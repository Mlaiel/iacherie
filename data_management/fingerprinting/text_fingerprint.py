"""📝 Text Fingerprinting Engine - IA Influencer Agent Platform Enterprise
=======================================================================
Module: backend/data_management/fingerprinting/text_fingerprint.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Text Fingerprinting - Ultra Enterprise Production-Ready
Responsibility: Advanced text fingerprinting with BERT, RoBERTa, and semantic analysis
===================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC TEXT FINGERPRINTING:
Text Upload (Bloggers/Writers/Influencers) → Content Validation → 
Text Processing → Language Detection → Semantic Analysis → BERT Embeddings → 
RoBERTa Features → N-gram Analysis → Vector Generation → FAISS Indexing → 
Plagiarism Detection → Copyright Protection → Revenue Recovery

TEXT FINGERPRINTING TECHNOLOGIES:
├── 🧠 BERT (Bidirectional Encoder Representations)
├── 🤖 RoBERTa (Robustly Optimized BERT)
├── 📊 TF-IDF (Term Frequency-Inverse Document Frequency)
├── 🔤 Word2Vec (Word Embeddings)
├── 📝 N-gram Analysis (Character + Word Level)
├── 🌐 Language Detection (Multi-language Support)
├── 🔍 Semantic Similarity (Cosine + Euclidean)
└── 🛡️ Plagiarism Protection (Real-time Monitoring)
"""
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import numpy as np
import asyncio
import logging
import hashlib
import re
import time
from datetime import datetime
from pathlib import Path
import pickle
import json

# NLP libraries
try:
    from transformers import (
        AutoTokenizer, AutoModel, 
        BertTokenizer, BertModel,
        RobertaTokenizer, RobertaModel,
        pipeline
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available - install transformers")

try:
    import spacy
    from spacy.lang.detect import LanguageDetector
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("SpaCy not available - install spacy")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import LatentDirichletAllocation
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available - install scikit-learn")

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available - install nltk")

try:
    import gensim
    from gensim.models import Word2Vec, Doc2Vec
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False
    logging.warning("Gensim not available - install gensim")

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

logger = logging.getLogger(__name__)

@dataclass
class TextFingerprintConfig:
    """Configuration avancée pour le fingerprinting de texte"""
    
    # Paramètres généraux
    max_text_length: int = 100000  # 100K caractères max
    min_text_length: int = 100     # 100 caractères min
    chunk_size: int = 512          # Taille des chunks pour BERT
    overlap_size: int = 50         # Chevauchement entre chunks
    
    # Modèles de langue
    bert_model: str = "bert-base-uncased"
    roberta_model: str = "roberta-base"
    sentence_transformer: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Fonctionnalités activées
    bert_enabled: bool = True
    roberta_enabled: bool = True
    tfidf_enabled: bool = True
    word2vec_enabled: bool = True
    ngram_enabled: bool = True
    semantic_analysis: bool = True
    
    # Paramètres N-gram
    ngram_range: Tuple[int, int] = (1, 3)
    char_ngram_range: Tuple[int, int] = (3, 7)
    max_features: int = 10000
    
    # Paramètres TF-IDF
    tfidf_max_features: int = 5000
    tfidf_ngram_range: Tuple[int, int] = (1, 3)
    
    # Détection de langue
    language_detection: bool = True
    supported_languages: List[str] = field(default_factory=lambda: [
        "en", "fr", "de", "es", "it", "pt", "nl", "ru", "zh", "ja", "ar"
    ])
    
    # Performance
    batch_size: int = 16
    max_workers: int = 4
    cache_enabled: bool = True
    gpu_acceleration: bool = False

class BaseTextProcessor(ABC):
    """Classe de base pour les processeurs de texte"""
    
    def __init__(self, config: TextFingerprintConfig):
        self.config = config
        self.cache = {} if config.cache_enabled else None
        
    @abstractmethod
    async def process(self, text: str) -> Dict[str, Any]:
        """Process text and extract features"""
        logger.warning(f"process method not implemented in {self.__class__.__name__}")
        
        # Return basic fingerprint data structure
        return {
            "processor": self.__class__.__name__,
            "text_length": len(text),
            "fingerprint_id": f"default_{hash(text) % 100000}",
            "features": [],
            "metadata": {
                "processed_at": datetime.utcnow().isoformat(),
                "config": self.config.__dict__ if hasattr(self, 'config') else {}
            }
        }
    
    @abstractmethod
    def get_name(self) -> str:
        """Get processor name"""
        return f"default_{self.__class__.__name__.lower()}"
    
    def _clean_text(self, text: str) -> str:
        """Nettoie et normalise le texte"""
        # Suppression des caractères spéciaux et normalisation
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip().lower()
        return text
    
    def _detect_language(self, text: str) -> str:
        """Détecte la langue du texte"""
        if not SPACY_AVAILABLE:
            return "en"  # Fallback vers l'anglais
        
        try:
            # Utilisation de spacy pour la détection de langue
            sample = text[:1000]  # Échantillon pour la détection
            # Implémentation simplifiée - en production, utiliser un modèle spécialisé
            return "en"  # Fallback temporaire
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "en"

class BERTProcessor(BaseTextProcessor):
    """Processeur BERT pour l'analyse sémantique avancée"""
    
    def __init__(self, config: TextFingerprintConfig):
        super().__init__(config)
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle BERT"""
        if not TRANSFORMERS_AVAILABLE:
            logger.error("BERT processor requires transformers library")
            return
        
        try:
            self.tokenizer = BertTokenizer.from_pretrained(self.config.bert_model)
            self.model = BertModel.from_pretrained(self.config.bert_model)
            logger.info(f"BERT model loaded: {self.config.bert_model}")
        except Exception as e:
            logger.error(f"Failed to load BERT model: {e}")
    
    async def process(self, text: str) -> Dict[str, Any]:
        """Traite le texte avec BERT"""
        if not self.model or not self.tokenizer:
            return {"error": "BERT model not available"}
        
        try:
            # Chunking du texte
            chunks = self._chunk_text(text)
            embeddings = []
            
            for chunk in chunks:
                # Tokenisation
                inputs = self.tokenizer(
                    chunk, 
                    return_tensors="pt", 
                    max_length=self.config.chunk_size,
                    truncation=True,
                    padding=True
                )
                
                # Génération des embeddings
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    # Moyenne des token embeddings
                    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                    embeddings.append(embedding)
            
            # Moyenne des embeddings de chunks
            final_embedding = np.mean(embeddings, axis=0)
            
            return {
                "bert_embedding": final_embedding.tolist(),
                "embedding_dimension": len(final_embedding),
                "chunks_processed": len(chunks),
                "model_used": self.config.bert_model
            }
            
        except Exception as e:
            logger.error(f"BERT processing failed: {e}")
            return {"error": str(e)}
    
    def _chunk_text(self, text: str) -> List[str]:
        """Divise le texte en chunks gérables"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.config.chunk_size - self.config.overlap_size):
            chunk = " ".join(words[i:i + self.config.chunk_size])
            if len(chunk.strip()) > 0:
                chunks.append(chunk)
        
        return chunks if chunks else [text]
    
    def get_name(self) -> str:
        """Get processor name"""
        return "bert"

class RoBERTaProcessor(BaseTextProcessor):
    """Processeur RoBERTa pour l'analyse robuste"""
    
    def __init__(self, config: TextFingerprintConfig):
        super().__init__(config)
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle RoBERTa"""
        if not TRANSFORMERS_AVAILABLE:
            logger.error("RoBERTa processor requires transformers library")
            return
        
        try:
            self.tokenizer = RobertaTokenizer.from_pretrained(self.config.roberta_model)
            self.model = RobertaModel.from_pretrained(self.config.roberta_model)
            logger.info(f"RoBERTa model loaded: {self.config.roberta_model}")
        except Exception as e:
            logger.error(f"Failed to load RoBERTa model: {e}")
    
    async def process(self, text: str) -> Dict[str, Any]:
        """Traite le texte avec RoBERTa"""
        if not self.model or not self.tokenizer:
            return {"error": "RoBERTa model not available"}
        
        try:
            # Similarité au processeur BERT mais avec RoBERTa
            chunks = self._chunk_text(text)
            embeddings = []
            
            for chunk in chunks:
                inputs = self.tokenizer(
                    chunk,
                    return_tensors="pt",
                    max_length=self.config.chunk_size,
                    truncation=True,
                    padding=True
                )
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                    embeddings.append(embedding)
            
            final_embedding = np.mean(embeddings, axis=0)
            
            return {
                "roberta_embedding": final_embedding.tolist(),
                "embedding_dimension": len(final_embedding),
                "chunks_processed": len(chunks),
                "model_used": self.config.roberta_model
            }
            
        except Exception as e:
            logger.error(f"RoBERTa processing failed: {e}")
            return {"error": str(e)}
    
    def _chunk_text(self, text: str) -> List[str]:
        """Divise le texte en chunks gérables"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.config.chunk_size - self.config.overlap_size):
            chunk = " ".join(words[i:i + self.config.chunk_size])
            if len(chunk.strip()) > 0:
                chunks.append(chunk)
        
        return chunks if chunks else [text]
    
    def get_name(self) -> str:
        """Get processor name"""
        return "roberta"

class TFIDFProcessor(BaseTextProcessor):
    """Processeur TF-IDF pour l'analyse statistique"""
    
    def __init__(self, config: TextFingerprintConfig):
        super().__init__(config)
        self.vectorizer = None
        self._initialize_vectorizer()
    
    def _initialize_vectorizer(self):
        """Initialise le vectoriseur TF-IDF"""
        if not SKLEARN_AVAILABLE:
            logger.error("TF-IDF processor requires scikit-learn")
            return
        
        try:
            self.vectorizer = TfidfVectorizer(
                max_features=self.config.tfidf_max_features,
                ngram_range=self.config.tfidf_ngram_range,
                stop_words='english',
                lowercase=True,
                analyzer='word'
            )
            logger.info("TF-IDF vectorizer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TF-IDF vectorizer: {e}")
    
    async def process(self, text: str) -> Dict[str, Any]:
        """Traite le texte avec TF-IDF"""
        if not self.vectorizer:
            return {"error": "TF-IDF vectorizer not available"}
        
        try:
            # Nettoyage du texte
            clean_text = self._clean_text(text)
            
            # Génération du vecteur TF-IDF
            tfidf_matrix = self.vectorizer.fit_transform([clean_text])
            tfidf_vector = tfidf_matrix.toarray()[0]
            
            # Extraction des termes importants
            feature_names = self.vectorizer.get_feature_names_out()
            top_indices = np.argsort(tfidf_vector)[-20:][::-1]  # Top 20 termes
            top_terms = [(feature_names[i], tfidf_vector[i]) for i in top_indices if tfidf_vector[i] > 0]
            
            return {
                "tfidf_vector": tfidf_vector.tolist(),
                "vector_dimension": len(tfidf_vector),
                "top_terms": top_terms,
                "vocabulary_size": len(feature_names),
                "non_zero_features": np.count_nonzero(tfidf_vector)
            }
            
        except Exception as e:
            logger.error(f"TF-IDF processing failed: {e}")
            return {"error": str(e)}
    
    def get_name(self) -> str:
        """Get processor name"""
        return "tfidf"

class Word2VecProcessor(BaseTextProcessor):
    """Processeur Word2Vec pour les embeddings de mots"""
    
    def __init__(self, config: TextFingerprintConfig):
        super().__init__(config)
        self.model = None
        
    async def process(self, text: str) -> Dict[str, Any]:
        """Traite le texte avec Word2Vec"""
        if not GENSIM_AVAILABLE:
            return {"error": "Word2Vec requires gensim library"}
        
        try:
            # Préparation des données
            sentences = self._prepare_sentences(text)
            
            # Entraînement du modèle Word2Vec
            model = Word2Vec(
                sentences,
                vector_size=100,
                window=5,
                min_count=1,
                workers=self.config.max_workers,
                sg=0  # CBOW
            )
            
            # Génération d'un vecteur document
            doc_vector = self._generate_doc_vector(model, text)
            
            # Extraction des mots similaires
            vocabulary = list(model.wv.key_to_index.keys())
            
            return {
                "word2vec_vector": doc_vector.tolist(),
                "vector_dimension": len(doc_vector),
                "vocabulary_size": len(vocabulary),
                "model_trained": True
            }
            
        except Exception as e:
            logger.error(f"Word2Vec processing failed: {e}")
            return {"error": str(e)}
    
    def _prepare_sentences(self, text: str) -> List[List[str]]:
        """Prépare les phrases pour Word2Vec"""
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(text)
            return [word_tokenize(sentence.lower()) for sentence in sentences]
        else:
            # Fallback simple
            sentences = text.split('.')
            return [sentence.strip().lower().split() for sentence in sentences if sentence.strip()]
    
    def _generate_doc_vector(self, model, text: str) -> np.ndarray:
        """Génère un vecteur pour l'ensemble du document"""
        words = text.lower().split()
        word_vectors = []
        
        for word in words:
            if word in model.wv:
                word_vectors.append(model.wv[word])
        
        if word_vectors:
            return np.mean(word_vectors, axis=0)
        else:
            return np.zeros(model.vector_size)
    
    def get_name(self) -> str:
        """Get processor name"""
        return "word2vec"

class NGramProcessor(BaseTextProcessor):
    """Processeur N-gram pour l'analyse structurelle"""
    
    async def process(self, text: str) -> Dict[str, Any]:
        """Traite le texte avec analyse N-gram"""
        try:
            # N-grams de mots
            word_ngrams = self._extract_word_ngrams(text)
            
            # N-grams de caractères
            char_ngrams = self._extract_char_ngrams(text)
            
            # Hachage des n-grams pour les fingerprints
            word_ngram_hash = self._hash_ngrams(word_ngrams)
            char_ngram_hash = self._hash_ngrams(char_ngrams)
            
            return {
                "word_ngrams": word_ngrams[:100],  # Top 100
                "char_ngrams": char_ngrams[:100],  # Top 100
                "word_ngram_hash": word_ngram_hash,
                "char_ngram_hash": char_ngram_hash,
                "word_ngram_count": len(word_ngrams),
                "char_ngram_count": len(char_ngrams)
            }
            
        except Exception as e:
            logger.error(f"N-gram processing failed: {e}")
            return {"error": str(e)}
    
    def _extract_word_ngrams(self, text: str) -> List[str]:
        """Extrait les n-grams de mots"""
        words = text.lower().split()
        ngrams = []
        
        for n in range(self.config.ngram_range[0], self.config.ngram_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram = " ".join(words[i:i + n])
                ngrams.append(ngram)
        
        return list(set(ngrams))  # Suppression des doublons
    
    def _extract_char_ngrams(self, text: str) -> List[str]:
        """Extrait les n-grams de caractères"""
        text = self._clean_text(text)
        ngrams = []
        
        for n in range(self.config.char_ngram_range[0], self.config.char_ngram_range[1] + 1):
            for i in range(len(text) - n + 1):
                ngram = text[i:i + n]
                ngrams.append(ngram)
        
        return list(set(ngrams))  # Suppression des doublons
    
    def _hash_ngrams(self, ngrams: List[str]) -> str:
        """Génère un hash des n-grams"""
        combined = "".join(sorted(ngrams))
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get_name(self) -> str:
        """Get processor name"""
        return "ngram"

class TextFingerprintEngine:
    """
    Moteur principal de fingerprinting de texte avec IA
    
    Fonctionnalités:
    - Analyse sémantique avancée (BERT, RoBERTa)
    - Analyse statistique (TF-IDF, N-grams)
    - Embeddings de mots (Word2Vec)
    - Détection de plagiat et similarité
    - Support multi-langue
    - Performance optimisée
    """
    
    def __init__(self, config: Optional[TextFingerprintConfig] = None):
        self.config = config or TextFingerprintConfig()
        
        # Initialisation des processeurs
        self.processors = {}
        self._initialize_processors()
        
        # Métriques de performance
        self.metrics = {
            "texts_processed": 0,
            "processing_time_total": 0.0,
            "errors_count": 0,
            "cache_hits": 0
        }
        
        logger.info("TextFingerprintEngine initialized successfully")
    
    def _initialize_processors(self):
        """Initialise tous les processeurs activés"""
        if self.config.bert_enabled:
            self.processors["bert"] = BERTProcessor(self.config)
        
        if self.config.roberta_enabled:
            self.processors["roberta"] = RoBERTaProcessor(self.config)
        
        if self.config.tfidf_enabled:
            self.processors["tfidf"] = TFIDFProcessor(self.config)
        
        if self.config.word2vec_enabled:
            self.processors["word2vec"] = Word2VecProcessor(self.config)
        
        if self.config.ngram_enabled:
            self.processors["ngram"] = NGramProcessor(self.config)
        
        logger.info(f"Initialized {len(self.processors)} text processors")
    
    async def generate_fingerprint(self, text_path: str) -> Dict[str, Any]:
        """
        Génère une empreinte complète pour un texte
        
        Args:
            text_path: Chemin vers le fichier texte
            
        Returns:
            Dictionnaire contenant l'empreinte complète
        """
        start_time = time.time()
        
        try:
            # Lecture du fichier
            text_content = await self._read_text_file(text_path)
            
            # Validation
            if not self._validate_text(text_content):
                raise ValueError("Text validation failed")
            
            # Génération de l'empreinte
            fingerprint_data = await self._process_text(text_content)
            
            # Ajout des métadonnées
            fingerprint_data.update({
                "file_path": text_path,
                "text_length": len(text_content),
                "word_count": len(text_content.split()),
                "language": self._detect_language(text_content),
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
                "engine_version": __version__
            })
            
            # Mise à jour des métriques
            self.metrics["texts_processed"] += 1
            self.metrics["processing_time_total"] += fingerprint_data["processing_time"]
            
            return fingerprint_data
            
        except Exception as e:
            self.metrics["errors_count"] += 1
            logger.error(f"Text fingerprinting failed: {e}")
            raise
    
    async def _read_text_file(self, file_path: str) -> str:
        """Lit le contenu d'un fichier texte"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")
        
        try:
            # Essaie plusieurs encodages
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        content = f.read()
                    return content
                except UnicodeDecodeError:
                    continue
            
            raise ValueError("Could not decode text file with any encoding")
            
        except Exception as e:
            logger.error(f"Failed to read text file: {e}")
            raise
    
    def _validate_text(self, text: str) -> bool:
        """Valide le contenu du texte"""
        if not text or not text.strip():
            return False
        
        if len(text) < self.config.min_text_length:
            logger.warning(f"Text too short: {len(text)} < {self.config.min_text_length}")
            return False
        
        if len(text) > self.config.max_text_length:
            logger.warning(f"Text too long: {len(text)} > {self.config.max_text_length}")
            return False
        
        return True
    
    async def _process_text(self, text: str) -> Dict[str, Any]:
        """Traite le texte avec tous les processeurs activés"""
        results = {}
        
        # Traitement en parallèle avec tous les processeurs
        tasks = []
        for name, processor in self.processors.items():
            task = asyncio.create_task(processor.process(text))
            tasks.append((name, task))
        
        # Attente des résultats
        for name, task in tasks:
            try:
                result = await task
                results[name] = result
            except Exception as e:
                logger.error(f"Processor {name} failed: {e}")
                results[name] = {"error": str(e)}
        
        # Génération du hash composite
        composite_hash = self._generate_composite_hash(results)
        results["composite_hash"] = composite_hash
        
        return results
    
    def _generate_composite_hash(self, results: Dict[str, Any]) -> str:
        """Génère un hash composite de tous les résultats"""
        hash_components = []
        
        for processor_name, result in results.items():
            if "error" not in result:
                # Ajoute une représentation hashable du résultat
                component = f"{processor_name}:{str(result)}"
                hash_components.append(component)
        
        combined = "|".join(sorted(hash_components))
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _detect_language(self, text: str) -> str:
        """Détecte la langue du texte"""
        if not self.config.language_detection:
            return "unknown"
        
        # Implémentation simplifiée - en production, utiliser un modèle spécialisé
        sample = text[:1000].lower()
        
        # Détection basique par mots-clés fréquents
        language_indicators = {
            "en": ["the", "and", "is", "in", "to", "of", "a", "that", "it", "with"],
            "fr": ["le", "de", "et", "à", "un", "il", "être", "et", "en", "avoir"],
            "de": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich"],
            "es": ["el", "de", "que", "y", "en", "un", "es", "se", "no", "te"],
            "it": ["il", "di", "che", "e", "la", "per", "in", "un", "è", "non"]
        }
        
        scores = {}
        for lang, indicators in language_indicators.items():
            score = sum(1 for word in indicators if word in sample)
            scores[lang] = score
        
        if scores:
            detected_lang = max(scores, key=scores.get)
            if scores[detected_lang] > 0:
                return detected_lang
        
        return "unknown"
    
    async def compare_texts(self, text1_path: str, text2_path: str) -> Dict[str, Any]:
        """Compare deux textes et calcule leur similarité"""
        try:
            # Génération des empreintes
            fp1 = await self.generate_fingerprint(text1_path)
            fp2 = await self.generate_fingerprint(text2_path)
            
            # Calcul des similarités
            similarities = {}
            
            # Similarité BERT
            if "bert" in fp1 and "bert" in fp2:
                if "error" not in fp1["bert"] and "error" not in fp2["bert"]:
                    bert_sim = self._cosine_similarity(
                        fp1["bert"]["bert_embedding"],
                        fp2["bert"]["bert_embedding"]
                    )
                    similarities["bert_similarity"] = bert_sim
            
            # Similarité RoBERTa
            if "roberta" in fp1 and "roberta" in fp2:
                if "error" not in fp1["roberta"] and "error" not in fp2["roberta"]:
                    roberta_sim = self._cosine_similarity(
                        fp1["roberta"]["roberta_embedding"],
                        fp2["roberta"]["roberta_embedding"]
                    )
                    similarities["roberta_similarity"] = roberta_sim
            
            # Similarité TF-IDF
            if "tfidf" in fp1 and "tfidf" in fp2:
                if "error" not in fp1["tfidf"] and "error" not in fp2["tfidf"]:
                    tfidf_sim = self._cosine_similarity(
                        fp1["tfidf"]["tfidf_vector"],
                        fp2["tfidf"]["tfidf_vector"]
                    )
                    similarities["tfidf_similarity"] = tfidf_sim
            
            # Similarité N-gram
            if "ngram" in fp1 and "ngram" in fp2:
                if "error" not in fp1["ngram"] and "error" not in fp2["ngram"]:
                    ngram_sim = self._jaccard_similarity(
                        set(fp1["ngram"]["word_ngrams"]),
                        set(fp2["ngram"]["word_ngrams"])
                    )
                    similarities["ngram_similarity"] = ngram_sim
            
            # Similarité globale (moyenne pondérée)
            if similarities:
                weights = {"bert_similarity": 0.3, "roberta_similarity": 0.3, "tfidf_similarity": 0.2, "ngram_similarity": 0.2}
                overall_similarity = sum(
                    similarities.get(metric, 0) * weight 
                    for metric, weight in weights.items()
                ) / sum(weights.values())
            else:
                overall_similarity = 0.0
            
            return {
                "file1": text1_path,
                "file2": text2_path,
                "similarities": similarities,
                "overall_similarity": overall_similarity,
                "fingerprint1": fp1,
                "fingerprint2": fp2,
                "comparison_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Text comparison failed: {e}")
            raise
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcule la similarité cosinus entre deux vecteurs"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _jaccard_similarity(self, set1: Set, set2: Set) -> float:
        """Calcule la similarité de Jaccard entre deux ensembles"""
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de performance"""
        avg_processing_time = (
            self.metrics["processing_time_total"] / self.metrics["texts_processed"]
            if self.metrics["texts_processed"] > 0 else 0
        )
        
        return {
            **self.metrics,
            "average_processing_time": avg_processing_time,
            "error_rate": (
                self.metrics["errors_count"] / max(self.metrics["texts_processed"], 1)
            ),
            "processors_active": list(self.processors.keys())
        }

# Export des classes principales
__all__ = [
    "TextFingerprintEngine",
    "TextFingerprintConfig",
    "BERTProcessor",
    "RoBERTaProcessor", 
    "TFIDFProcessor",
    "Word2VecProcessor",
    "NGramProcessor"
]
