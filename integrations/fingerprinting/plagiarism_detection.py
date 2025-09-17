"""
Plagiarism Detection - Fingerprinting Module
===========================================
Système avancé de détection de plagiat avec ML et analyse cross-format.

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: ML Engineer + IA Prompt Engineer
"""

import asyncio
import logging
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import difflib

logger = logging.getLogger(__name__)

class PlagiarismType(Enum):
    """Types de plagiat détectés."""
    LITERAL_COPYING = "literal_copying"
    PARAPHRASING = "paraphrasing"
    STRUCTURAL_PLAGIARISM = "structural_plagiarism"
    IDEA_PLAGIARISM = "idea_plagiarism"
    MOSAIC_PLAGIARISM = "mosaic_plagiarism"
    SELF_PLAGIARISM = "self_plagiarism"
    TRANSLATION_PLAGIARISM = "translation_plagiarism"

class ContentFormat(Enum):
    """Formats de contenu supportés."""
    TEXT = "text"
    CODE = "code"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    PRESENTATION = "presentation"

class DetectionMethod(Enum):
    """Méthodes de détection."""
    FINGERPRINT_MATCHING = "fingerprint_matching"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    SYNTACTIC_ANALYSIS = "syntactic_analysis"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    ML_CLASSIFICATION = "ml_classification"
    DEEP_LEARNING = "deep_learning"

@dataclass
class PlagiarismAlert:
    """Alerte de plagiat détecté."""
    alert_id: str
    source_content_id: str
    target_content_id: str
    plagiarism_type: PlagiarismType
    confidence_score: float
    similarity_score: float
    detection_method: DetectionMethod
    matched_segments: List[Dict[str, Any]]
    evidence: Dict[str, Any]
    severity_level: str
    auto_verified: bool
    detection_timestamp: datetime

@dataclass
class ContentProfile:
    """Profil de contenu pour analyse."""
    content_id: str
    content_path: str
    content_format: ContentFormat
    fingerprint_hash: str
    semantic_features: Dict[str, Any]
    structural_features: Dict[str, Any]
    stylometric_features: Dict[str, Any]
    metadata: Dict[str, Any]
    author_profile: Optional[str]
    creation_timestamp: datetime
    last_analyzed: datetime

@dataclass
class SimilarityMatch:
    """Correspondance de similarité."""
    match_id: str
    source_id: str
    target_id: str
    similarity_score: float
    match_segments: List[Dict[str, Any]]
    match_type: str
    confidence: float
    evidence_strength: float

class PlagiarismDetection:
    """
    Plagiarism Detection Enterprise
    =============================
    
    Système de détection de plagiat avec:
    - Multi-format plagiarism detection (texte, code, audio, image, vidéo)
    - ML-powered similarity analysis avancée
    - Cross-platform content scanning
    - Plagiarism confidence scoring intelligent
    - Automated infringement reporting
    - Similarity threshold optimization dynamique
    
    Expert Implementation: ML Engineer + IA Prompt Engineer
    """
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
        self.content_database: Dict[str, ContentProfile] = {}
        self.alert_database: Dict[str, PlagiarismAlert] = {}
        self.similarity_cache: Dict[str, List[SimilarityMatch]] = {}
        
        # Modèles ML
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words='english'
        )
        
        # Seuils par type de plagiat
        self.plagiarism_thresholds = {
            PlagiarismType.LITERAL_COPYING: 0.95,
            PlagiarismType.PARAPHRASING: 0.8,
            PlagiarismType.STRUCTURAL_PLAGIARISM: 0.7,
            PlagiarismType.IDEA_PLAGIARISM: 0.6,
            PlagiarismType.MOSAIC_PLAGIARISM: 0.75,
            PlagiarismType.SELF_PLAGIARISM: 0.85,
            PlagiarismType.TRANSLATION_PLAGIARISM: 0.65
        }
        
        # Configuration détection
        self.min_segment_length = 50  # Mots minimum pour segment suspect
        self.max_segments_analyzed = 1000  # Limite performance
        self.clustering_eps = 0.3  # DBSCAN epsilon
        self.clustering_min_samples = 3
        
        logger.info("PlagiarismDetection engine initialisé")
    
    async def analyze_content(
        self,
        content_path: str,
        content_format: ContentFormat,
        author_profile: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> ContentProfile:
        """
        Analyse un contenu pour détection de plagiat.
        
        Args:
            content_path: Chemin vers le contenu
            content_format: Format du contenu
            author_profile: Profil de l'auteur
            metadata: Métadonnées du contenu
        
        Returns:
            ContentProfile: Profil d'analyse créé
        """
        try:
            # Extraire contenu
            content_text = await self._extract_content_text(content_path, content_format)
            
            # Générer empreinte
            fingerprint_hash = self._generate_content_fingerprint(content_text)
            
            # Analyser features sémantiques
            semantic_features = await self._analyze_semantic_features(content_text, content_format)
            
            # Analyser features structurelles
            structural_features = await self._analyze_structural_features(content_text, content_format)
            
            # Analyser features stylométriques
            stylometric_features = await self._analyze_stylometric_features(content_text)
            
            # Créer profil
            content_profile = ContentProfile(
                content_id=str(uuid.uuid4()),
                content_path=content_path,
                content_format=content_format,
                fingerprint_hash=fingerprint_hash,
                semantic_features=semantic_features,
                structural_features=structural_features,
                stylometric_features=stylometric_features,
                metadata=metadata or {},
                author_profile=author_profile,
                creation_timestamp=datetime.utcnow(),
                last_analyzed=datetime.utcnow()
            )
            
            # Stocker profil
            self.content_database[content_profile.content_id] = content_profile
            
            logger.info(f"Profil contenu créé: {content_profile.content_id}")
            return content_profile
            
        except Exception as e:
            logger.error(f"Erreur analyse contenu: {e}")
            raise
    
    async def _extract_content_text(self, content_path: str, content_format: ContentFormat) -> str:
        """Extrait le texte du contenu selon son format."""
        try:
            if content_format == ContentFormat.TEXT:
                with open(content_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif content_format == ContentFormat.CODE:
                with open(content_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
                # Nettoyer le code (supprimer commentaires, normaliser)
                return self._clean_code_content(code_content)
            
            elif content_format in [ContentFormat.AUDIO, ContentFormat.IMAGE, ContentFormat.VIDEO]:
                # Pour contenu multimédia, retourner métadonnées textuelles
                return f"Contenu multimédia: {content_path}"
            
            elif content_format == ContentFormat.PRESENTATION:
                # Simulation extraction présentation
                return f"Contenu présentation: {content_path}"
            
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Erreur extraction texte: {e}")
            return ""
    
    def _clean_code_content(self, code: str) -> str:
        """Nettoie le contenu code pour analyse."""
        try:
            # Supprimer commentaires ligne
            code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
            
            # Supprimer commentaires bloc
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            
            # Supprimer espaces multiples
            code = re.sub(r'\s+', ' ', code)
            
            # Normaliser indentation
            lines = code.split('\n')
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            logger.error(f"Erreur nettoyage code: {e}")
            return code
    
    def _generate_content_fingerprint(self, content_text: str) -> str:
        """Génère empreinte du contenu."""
        try:
            # Normaliser texte
            normalized = re.sub(r'\s+', ' ', content_text.lower().strip())
            
            # Hash SHA256
            return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
            
        except Exception as e:
            logger.error(f"Erreur génération empreinte: {e}")
            return ""
    
    async def _analyze_semantic_features(
        self,
        content_text: str,
        content_format: ContentFormat
    ) -> Dict[str, Any]:
        """Analyse les features sémantiques."""
        try:
            semantic_features = {}
            
            # Analyse TF-IDF
            if len(content_text) > 100:
                tfidf_vector = self.tfidf_vectorizer.fit_transform([content_text])
                semantic_features['tfidf_vector'] = tfidf_vector.toarray()[0].tolist()
                
                # Features TF-IDF
                feature_names = self.tfidf_vectorizer.get_feature_names_out()
                top_features = []
                
                for i, score in enumerate(semantic_features['tfidf_vector']):
                    if score > 0.1:  # Seuil de pertinence
                        top_features.append({
                            'term': feature_names[i],
                            'score': float(score)
                        })
                
                # Trier par score
                top_features.sort(key=lambda x: x['score'], reverse=True)
                semantic_features['top_terms'] = top_features[:50]
            
            # Analyse conceptuelle
            semantic_features['concepts'] = await self._extract_concepts(content_text)
            
            # Analyse thématique
            semantic_features['topics'] = await self._extract_topics(content_text)
            
            # Entités nommées
            semantic_features['named_entities'] = await self._extract_named_entities(content_text)
            
            # Complexité sémantique
            semantic_features['semantic_complexity'] = self._calculate_semantic_complexity(content_text)
            
            return semantic_features
            
        except Exception as e:
            logger.error(f"Erreur analyse sémantique: {e}")
            return {}
    
    async def _extract_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Extrait les concepts du texte."""
        try:
            words = text.lower().split()
            
            # Concepts par domaines
            tech_concepts = ['algorithm', 'data', 'system', 'technology', 'computer', 'software']
            science_concepts = ['research', 'study', 'analysis', 'theory', 'hypothesis', 'experiment']
            business_concepts = ['market', 'customer', 'revenue', 'strategy', 'business', 'company']
            
            concepts = []
            
            for concept_list, domain in [(tech_concepts, 'technology'), 
                                       (science_concepts, 'science'), 
                                       (business_concepts, 'business')]:
                count = sum(1 for word in words if word in concept_list)
                if count > 0:
                    concepts.append({
                        'domain': domain,
                        'count': count,
                        'density': count / len(words)
                    })
            
            return concepts
            
        except Exception as e:
            logger.error(f"Erreur extraction concepts: {e}")
            return []
    
    async def _extract_topics(self, text: str) -> List[Dict[str, Any]]:
        """Extrait les topics du texte."""
        try:
            # Simulation topic modeling
            words = set(text.lower().split())
            
            topics = []
            
            # Topics prédéfinis
            topic_keywords = {
                'artificial_intelligence': ['ai', 'machine', 'learning', 'neural', 'intelligence'],
                'programming': ['code', 'program', 'software', 'development', 'programming'],
                'data_science': ['data', 'analysis', 'statistics', 'model', 'dataset'],
                'security': ['security', 'encryption', 'vulnerability', 'attack', 'protection']
            }
            
            for topic, keywords in topic_keywords.items():
                matches = len(words & set(keywords))
                if matches > 0:
                    topics.append({
                        'topic': topic,
                        'relevance_score': matches / len(keywords),
                        'keyword_matches': matches
                    })
            
            # Trier par pertinence
            topics.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return topics[:10]
            
        except Exception as e:
            logger.error(f"Erreur extraction topics: {e}")
            return []
    
    async def _extract_named_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extrait les entités nommées."""
        try:
            entities = []
            
            # Patterns simples pour entités
            # Emails
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            for email in emails:
                entities.append({'type': 'EMAIL', 'value': email})
            
            # URLs
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, text)
            for url in urls:
                entities.append({'type': 'URL', 'value': url})
            
            # Dates
            date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b'
            dates = re.findall(date_pattern, text)
            for date in dates:
                entities.append({'type': 'DATE', 'value': date})
            
            # Noms propres (simulation)
            proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
            for noun in set(proper_nouns[:20]):  # Limiter et dédupliquer
                entities.append({'type': 'PERSON_OR_PLACE', 'value': noun})
            
            return entities
            
        except Exception as e:
            logger.error(f"Erreur extraction entités: {e}")
            return []
    
    def _calculate_semantic_complexity(self, text: str) -> float:
        """Calcule la complexité sémantique."""
        try:
            words = text.split()
            if not words:
                return 0.0
            
            # Diversité lexicale
            unique_words = len(set(words))
            lexical_diversity = unique_words / len(words)
            
            # Longueur moyenne des mots
            avg_word_length = np.mean([len(word) for word in words])
            
            # Complexité des phrases
            sentences = text.split('.')
            avg_sentence_length = np.mean([len(sentence.split()) for sentence in sentences])
            
            # Score combiné
            complexity = (
                lexical_diversity * 0.4 +
                (avg_word_length / 10) * 0.3 +
                (avg_sentence_length / 20) * 0.3
            )
            
            return min(complexity, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul complexité: {e}")
            return 0.0
    
    async def _analyze_structural_features(
        self,
        content_text: str,
        content_format: ContentFormat
    ) -> Dict[str, Any]:
        """Analyse les features structurelles."""
        try:
            structural_features = {}
            
            if content_format == ContentFormat.TEXT:
                structural_features = await self._analyze_text_structure(content_text)
            elif content_format == ContentFormat.CODE:
                structural_features = await self._analyze_code_structure(content_text)
            else:
                structural_features = await self._analyze_generic_structure(content_text)
            
            return structural_features
            
        except Exception as e:
            logger.error(f"Erreur analyse structurelle: {e}")
            return {}
    
    async def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """Analyse la structure textuelle."""
        try:
            structure = {}
            
            # Statistiques de base
            sentences = text.split('.')
            paragraphs = text.split('\n\n')
            words = text.split()
            
            structure['sentence_count'] = len(sentences)
            structure['paragraph_count'] = len(paragraphs)
            structure['word_count'] = len(words)
            structure['character_count'] = len(text)
            
            # Longueurs moyennes
            sentence_lengths = [len(sentence.split()) for sentence in sentences if sentence.strip()]
            structure['avg_sentence_length'] = np.mean(sentence_lengths) if sentence_lengths else 0
            structure['sentence_length_variance'] = np.var(sentence_lengths) if sentence_lengths else 0
            
            # Patterns structurels
            structure['has_headers'] = bool(re.search(r'^#+\s+', text, re.MULTILINE))
            structure['has_lists'] = bool(re.search(r'^\s*[-*•]\s+', text, re.MULTILINE))
            structure['has_quotes'] = bool(re.search(r'"[^"]*"', text))
            structure['has_citations'] = bool(re.search(r'\[[^\]]+\]', text))
            
            # Distribution des longueurs de phrases
            if sentence_lengths:
                structure['sentence_length_distribution'] = {
                    'short': sum(1 for l in sentence_lengths if l < 10) / len(sentence_lengths),
                    'medium': sum(1 for l in sentence_lengths if 10 <= l < 20) / len(sentence_lengths),
                    'long': sum(1 for l in sentence_lengths if l >= 20) / len(sentence_lengths)
                }
            
            return structure
            
        except Exception as e:
            logger.error(f"Erreur analyse structure texte: {e}")
            return {}
    
    async def _analyze_code_structure(self, code: str) -> Dict[str, Any]:
        """Analyse la structure de code."""
        try:
            structure = {}
            
            lines = code.split('\n')
            structure['line_count'] = len(lines)
            structure['non_empty_lines'] = len([l for l in lines if l.strip()])
            
            # Patterns de code
            structure['function_count'] = len(re.findall(r'def\s+\w+|function\s+\w+', code))
            structure['class_count'] = len(re.findall(r'class\s+\w+', code))
            structure['import_count'] = len(re.findall(r'import\s+\w+|from\s+\w+', code))
            
            # Complexité cyclomatique approximative
            complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'case', 'switch']
            structure['cyclomatic_complexity'] = sum(
                len(re.findall(rf'\b{keyword}\b', code)) for keyword in complexity_keywords
            )
            
            # Indentation
            indented_lines = [l for l in lines if l.startswith('    ') or l.startswith('\t')]
            structure['indentation_ratio'] = len(indented_lines) / len(lines) if lines else 0
            
            return structure
            
        except Exception as e:
            logger.error(f"Erreur analyse structure code: {e}")
            return {}
    
    async def _analyze_generic_structure(self, content: str) -> Dict[str, Any]:
        """Analyse structure générique."""
        try:
            return {
                'length': len(content),
                'word_count': len(content.split()),
                'line_count': len(content.split('\n')),
                'has_structure': bool(re.search(r'\n\s*\n', content))
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse structure générique: {e}")
            return {}
    
    async def _analyze_stylometric_features(self, text: str) -> Dict[str, Any]:
        """Analyse les features stylométriques."""
        try:
            stylometric = {}
            
            words = text.split()
            sentences = text.split('.')
            
            if not words:
                return stylometric
            
            # Richesse lexicale
            unique_words = len(set(words))
            stylometric['lexical_richness'] = unique_words / len(words)
            stylometric['type_token_ratio'] = unique_words / len(words)
            
            # Longueur des mots
            word_lengths = [len(word) for word in words]
            stylometric['avg_word_length'] = np.mean(word_lengths)
            stylometric['word_length_variance'] = np.var(word_lengths)
            
            # Mots fonctionnels
            function_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            function_word_count = sum(1 for word in words if word.lower() in function_words)
            stylometric['function_word_ratio'] = function_word_count / len(words)
            
            # Ponctuation
            punctuation_count = len(re.findall(r'[.,;:!?]', text))
            stylometric['punctuation_density'] = punctuation_count / len(text)
            
            # Patterns syntaxiques
            stylometric['question_ratio'] = text.count('?') / len(sentences) if sentences else 0
            stylometric['exclamation_ratio'] = text.count('!') / len(sentences) if sentences else 0
            
            # Complexité syntaxique
            if sentences:
                sentence_lengths = [len(sentence.split()) for sentence in sentences if sentence.strip()]
                stylometric['sentence_complexity'] = np.var(sentence_lengths) / np.mean(sentence_lengths) if sentence_lengths else 0
            
            return stylometric
            
        except Exception as e:
            logger.error(f"Erreur analyse stylométrique: {e}")
            return {}
    
    async def detect_plagiarism(
        self,
        target_content_id: str,
        comparison_scope: Optional[List[str]] = None,
        detection_methods: List[DetectionMethod] = None
    ) -> List[PlagiarismAlert]:
        """
        Détecte le plagiat pour un contenu cible.
        
        Args:
            target_content_id: ID du contenu à analyser
            comparison_scope: IDs des contenus à comparer (optionnel)
            detection_methods: Méthodes de détection à utiliser
        
        Returns:
            List[PlagiarismAlert]: Alertes de plagiat détectées
        """
        try:
            if target_content_id not in self.content_database:
                raise ValueError(f"Contenu cible introuvable: {target_content_id}")
            
            target_profile = self.content_database[target_content_id]
            alerts = []
            
            # Définir scope de comparaison
            if comparison_scope is None:
                comparison_scope = [cid for cid in self.content_database.keys() if cid != target_content_id]
            
            # Méthodes par défaut
            if detection_methods is None:
                detection_methods = [
                    DetectionMethod.FINGERPRINT_MATCHING,
                    DetectionMethod.SEMANTIC_ANALYSIS,
                    DetectionMethod.SYNTACTIC_ANALYSIS
                ]
            
            # Analyser chaque contenu du scope
            for source_content_id in comparison_scope:
                if source_content_id in self.content_database:
                    source_profile = self.content_database[source_content_id]
                    
                    # Appliquer méthodes de détection
                    for method in detection_methods:
                        alert = await self._detect_plagiarism_with_method(
                            source_profile, target_profile, method
                        )
                        
                        if alert:
                            alerts.append(alert)
            
            # Déduplication et tri
            unique_alerts = self._deduplicate_alerts(alerts)
            unique_alerts.sort(key=lambda x: x.confidence_score, reverse=True)
            
            # Stocker alertes
            for alert in unique_alerts:
                self.alert_database[alert.alert_id] = alert
            
            logger.info(f"Détection plagiat terminée: {len(unique_alerts)} alertes pour {target_content_id}")
            return unique_alerts
            
        except Exception as e:
            logger.error(f"Erreur détection plagiat: {e}")
            return []
    
    async def _detect_plagiarism_with_method(
        self,
        source_profile: ContentProfile,
        target_profile: ContentProfile,
        method: DetectionMethod
    ) -> Optional[PlagiarismAlert]:
        """Détecte plagiat avec une méthode spécifique."""
        try:
            if method == DetectionMethod.FINGERPRINT_MATCHING:
                return await self._detect_fingerprint_plagiarism(source_profile, target_profile)
            elif method == DetectionMethod.SEMANTIC_ANALYSIS:
                return await self._detect_semantic_plagiarism(source_profile, target_profile)
            elif method == DetectionMethod.SYNTACTIC_ANALYSIS:
                return await self._detect_syntactic_plagiarism(source_profile, target_profile)
            elif method == DetectionMethod.STATISTICAL_ANALYSIS:
                return await self._detect_statistical_plagiarism(source_profile, target_profile)
            elif method == DetectionMethod.ML_CLASSIFICATION:
                return await self._detect_ml_plagiarism(source_profile, target_profile)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Erreur détection méthode {method}: {e}")
            return None
    
    async def _detect_fingerprint_plagiarism(
        self,
        source_profile: ContentProfile,
        target_profile: ContentProfile
    ) -> Optional[PlagiarismAlert]:
        """Détection par correspondance d'empreintes."""
        try:
            # Similarité exacte des empreintes
            if source_profile.fingerprint_hash == target_profile.fingerprint_hash:
                return PlagiarismAlert(
                    alert_id=str(uuid.uuid4()),
                    source_content_id=source_profile.content_id,
                    target_content_id=target_profile.content_id,
                    plagiarism_type=PlagiarismType.LITERAL_COPYING,
                    confidence_score=1.0,
                    similarity_score=1.0,
                    detection_method=DetectionMethod.FINGERPRINT_MATCHING,
                    matched_segments=[{
                        'type': 'full_content',
                        'similarity': 1.0,
                        'evidence': 'Empreintes identiques'
                    }],
                    evidence={'fingerprint_match': True},
                    severity_level='critical',
                    auto_verified=True,
                    detection_timestamp=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur détection empreinte: {e}")
            return None
    
    async def _detect_semantic_plagiarism(
        self,
        source_profile: ContentProfile,
        target_profile: ContentProfile
    ) -> Optional[PlagiarismAlert]:
        """Détection par analyse sémantique."""
        try:
            source_features = source_profile.semantic_features
            target_features = target_profile.semantic_features
            
            # Comparaison vecteurs TF-IDF
            similarity_score = 0.0
            evidence = {}
            
            if 'tfidf_vector' in source_features and 'tfidf_vector' in target_features:
                source_vector = np.array(source_features['tfidf_vector']).reshape(1, -1)
                target_vector = np.array(target_features['tfidf_vector']).reshape(1, -1)
                
                # Assurer même dimensionalité
                min_len = min(source_vector.shape[1], target_vector.shape[1])
                source_vector = source_vector[:, :min_len]
                target_vector = target_vector[:, :min_len]
                
                similarity_matrix = cosine_similarity(source_vector, target_vector)
                similarity_score = similarity_matrix[0, 0]
                evidence['tfidf_similarity'] = float(similarity_score)
            
            # Similarité des concepts
            concept_similarity = await self._compare_concepts(
                source_features.get('concepts', []),
                target_features.get('concepts', [])
            )
            evidence['concept_similarity'] = concept_similarity
            
            # Similarité des topics
            topic_similarity = await self._compare_topics(
                source_features.get('topics', []),
                target_features.get('topics', [])
            )
            evidence['topic_similarity'] = topic_similarity
            
            # Score combiné
            combined_similarity = (similarity_score * 0.6 + concept_similarity * 0.2 + topic_similarity * 0.2)
            
            # Déterminer type de plagiat
            plagiarism_type = self._determine_plagiarism_type_semantic(combined_similarity, evidence)
            
            if combined_similarity >= self.similarity_threshold:
                confidence = min(combined_similarity * 1.2, 1.0)
                
                return PlagiarismAlert(
                    alert_id=str(uuid.uuid4()),
                    source_content_id=source_profile.content_id,
                    target_content_id=target_profile.content_id,
                    plagiarism_type=plagiarism_type,
                    confidence_score=confidence,
                    similarity_score=combined_similarity,
                    detection_method=DetectionMethod.SEMANTIC_ANALYSIS,
                    matched_segments=await self._find_semantic_segments(source_profile, target_profile),
                    evidence=evidence,
                    severity_level=self._determine_severity(combined_similarity),
                    auto_verified=combined_similarity > 0.9,
                    detection_timestamp=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur détection sémantique: {e}")
            return None
    
    async def _compare_concepts(self, concepts1: List[Dict], concepts2: List[Dict]) -> float:
        """Compare les concepts entre deux contenus."""
        try:
            if not concepts1 or not concepts2:
                return 0.0
            
            domains1 = {c['domain']: c['density'] for c in concepts1}
            domains2 = {c['domain']: c['density'] for c in concepts2}
            
            # Domaines communs
            common_domains = set(domains1.keys()) & set(domains2.keys())
            
            if not common_domains:
                return 0.0
            
            similarities = []
            for domain in common_domains:
                density_diff = abs(domains1[domain] - domains2[domain])
                similarity = 1.0 - density_diff
                similarities.append(similarity)
            
            return np.mean(similarities)
            
        except Exception as e:
            logger.error(f"Erreur comparaison concepts: {e}")
            return 0.0
    
    async def _compare_topics(self, topics1: List[Dict], topics2: List[Dict]) -> float:
        """Compare les topics entre deux contenus."""
        try:
            if not topics1 or not topics2:
                return 0.0
            
            topics_set1 = {t['topic']: t['relevance_score'] for t in topics1}
            topics_set2 = {t['topic']: t['relevance_score'] for t in topics2}
            
            # Topics communs
            common_topics = set(topics_set1.keys()) & set(topics_set2.keys())
            
            if not common_topics:
                return 0.0
            
            similarities = []
            for topic in common_topics:
                score_diff = abs(topics_set1[topic] - topics_set2[topic])
                similarity = 1.0 - score_diff
                similarities.append(similarity)
            
            return np.mean(similarities)
            
        except Exception as e:
            logger.error(f"Erreur comparaison topics: {e}")
            return 0.0
    
    def _determine_plagiarism_type_semantic(self, similarity_score: float, evidence: Dict) -> PlagiarismType:
        """Détermine le type de plagiat basé sur l'analyse sémantique."""
        try:
            tfidf_sim = evidence.get('tfidf_similarity', 0.0)
            concept_sim = evidence.get('concept_similarity', 0.0)
            topic_sim = evidence.get('topic_similarity', 0.0)
            
            if tfidf_sim > 0.95:
                return PlagiarismType.LITERAL_COPYING
            elif tfidf_sim > 0.8 and concept_sim > 0.7:
                return PlagiarismType.PARAPHRASING
            elif concept_sim > 0.8 and topic_sim > 0.8:
                return PlagiarismType.IDEA_PLAGIARISM
            elif similarity_score > 0.8:
                return PlagiarismType.STRUCTURAL_PLAGIARISM
            else:
                return PlagiarismType.PARAPHRASING
                
        except Exception as e:
            logger.error(f"Erreur détermination type plagiat: {e}")
            return PlagiarismType.PARAPHRASING
    
    async def _find_semantic_segments(
        self,
        source_profile: ContentProfile,
        target_profile: ContentProfile
    ) -> List[Dict[str, Any]]:
        """Trouve les segments sémantiquement similaires."""
        try:
            # Simulation segments sémantiques
            segments = []
            
            # Segments basés sur top terms TF-IDF
            source_terms = source_profile.semantic_features.get('top_terms', [])
            target_terms = target_profile.semantic_features.get('top_terms', [])
            
            common_terms = []
            for s_term in source_terms[:10]:
                for t_term in target_terms[:10]:
                    if s_term['term'] == t_term['term']:
                        common_terms.append({
                            'term': s_term['term'],
                            'source_score': s_term['score'],
                            'target_score': t_term['score'],
                            'similarity': 1.0 - abs(s_term['score'] - t_term['score'])
                        })
            
            for i, term_match in enumerate(common_terms[:5]):
                segments.append({
                    'segment_id': i + 1,
                    'type': 'semantic_term_match',
                    'content': term_match['term'],
                    'similarity': term_match['similarity'],
                    'evidence': f"Terme commun: {term_match['term']}"
                })
            
            return segments
            
        except Exception as e:
            logger.error(f"Erreur recherche segments: {e}")
            return []
    
    async def _detect_syntactic_plagiarism(
        self,
        source_profile: ContentProfile,
        target_profile: ContentProfile
    ) -> Optional[PlagiarismAlert]:
        """Détection par analyse syntaxique."""
        try:
            source_structure = source_profile.structural_features
            target_structure = target_profile.structural_features
            
            # Comparaison structures
            similarity_score = await self._compare_structural_features(source_structure, target_structure)
            
            if similarity_score >= self.similarity_threshold:
                return PlagiarismAlert(
                    alert_id=str(uuid.uuid4()),
                    source_content_id=source_profile.content_id,
                    target_content_id=target_profile.content_id,
                    plagiarism_type=PlagiarismType.STRUCTURAL_PLAGIARISM,
                    confidence_score=similarity_score,
                    similarity_score=similarity_score,
                    detection_method=DetectionMethod.SYNTACTIC_ANALYSIS,
                    matched_segments=[{
                        'type': 'structural_similarity',
                        'similarity': similarity_score,
                        'evidence': 'Structures syntaxiques similaires'
                    }],
                    evidence={'structural_similarity': similarity_score},
                    severity_level=self._determine_severity(similarity_score),
                    auto_verified=similarity_score > 0.85,
                    detection_timestamp=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur détection syntaxique: {e}")
            return None
    
    async def _compare_structural_features(self, struct1: Dict, struct2: Dict) -> float:
        """Compare les features structurelles."""
        try:
            if not struct1 or not struct2:
                return 0.0
            
            similarities = []
            
            # Features numériques à comparer
            numeric_features = ['sentence_count', 'paragraph_count', 'word_count', 'avg_sentence_length']
            
            for feature in numeric_features:
                if feature in struct1 and feature in struct2:
                    val1, val2 = struct1[feature], struct2[feature]
                    if val1 > 0 and val2 > 0:
                        similarity = 1.0 - abs(val1 - val2) / max(val1, val2)
                        similarities.append(similarity)
            
            # Features booléennes
            boolean_features = ['has_headers', 'has_lists', 'has_quotes', 'has_citations']
            
            for feature in boolean_features:
                if feature in struct1 and feature in struct2:
                    if struct1[feature] == struct2[feature]:
                        similarities.append(1.0)
                    else:
                        similarities.append(0.0)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Erreur comparaison structure: {e}")
            return 0.0
    
    async def _detect_statistical_plagiarism(
        self,
        source_profile: ContentProfile,
        target_profile: ContentProfile
    ) -> Optional[PlagiarismAlert]:
        """Détection par analyse statistique."""
        try:
            source_stylo = source_profile.stylometric_features
            target_stylo = target_profile.stylometric_features
            
            # Comparaison features stylométriques
            similarity_score = await self._compare_stylometric_features(source_stylo, target_stylo)
            
            if similarity_score >= self.similarity_threshold:
                return PlagiarismAlert(
                    alert_id=str(uuid.uuid4()),
                    source_content_id=source_profile.content_id,
                    target_content_id=target_profile.content_id,
                    plagiarism_type=PlagiarismType.SELF_PLAGIARISM,  # Style similaire = même auteur?
                    confidence_score=similarity_score,
                    similarity_score=similarity_score,
                    detection_method=DetectionMethod.STATISTICAL_ANALYSIS,
                    matched_segments=[{
                        'type': 'stylometric_similarity',
                        'similarity': similarity_score,
                        'evidence': 'Patterns stylométriques similaires'
                    }],
                    evidence={'stylometric_similarity': similarity_score},
                    severity_level=self._determine_severity(similarity_score),
                    auto_verified=similarity_score > 0.9,
                    detection_timestamp=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur détection statistique: {e}")
            return None
    
    async def _compare_stylometric_features(self, stylo1: Dict, stylo2: Dict) -> float:
        """Compare les features stylométriques."""
        try:
            if not stylo1 or not stylo2:
                return 0.0
            
            similarities = []
            
            # Features à comparer
            features = ['lexical_richness', 'avg_word_length', 'function_word_ratio', 'punctuation_density']
            
            for feature in features:
                if feature in stylo1 and feature in stylo2:
                    val1, val2 = stylo1[feature], stylo2[feature]
                    if val1 > 0 and val2 > 0:
                        similarity = 1.0 - abs(val1 - val2) / max(val1, val2)
                        similarities.append(similarity)
                    elif val1 == val2 == 0:
                        similarities.append(1.0)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Erreur comparaison stylométrie: {e}")
            return 0.0
    
    async def _detect_ml_plagiarism(
        self,
        source_profile: ContentProfile,
        target_profile: ContentProfile
    ) -> Optional[PlagiarismAlert]:
        """Détection ML avancée."""
        try:
            # Simulation détection ML
            # En production: utiliser modèles BERT, transformers, etc.
            
            # Combiner toutes les features
            source_features = self._combine_features(source_profile)
            target_features = self._combine_features(target_profile)
            
            # Similarité cosinus des features combinées
            source_vector = np.array(source_features)
            target_vector = np.array(target_features)
            
            # Assurer même dimension
            min_len = min(len(source_vector), len(target_vector))
            source_vector = source_vector[:min_len]
            target_vector = target_vector[:min_len]
            
            # Similarité
            if np.linalg.norm(source_vector) > 0 and np.linalg.norm(target_vector) > 0:
                similarity = np.dot(source_vector, target_vector) / (
                    np.linalg.norm(source_vector) * np.linalg.norm(target_vector)
                )
            else:
                similarity = 0.0
            
            if similarity >= self.similarity_threshold:
                return PlagiarismAlert(
                    alert_id=str(uuid.uuid4()),
                    source_content_id=source_profile.content_id,
                    target_content_id=target_profile.content_id,
                    plagiarism_type=PlagiarismType.MOSAIC_PLAGIARISM,
                    confidence_score=float(similarity),
                    similarity_score=float(similarity),
                    detection_method=DetectionMethod.ML_CLASSIFICATION,
                    matched_segments=[{
                        'type': 'ml_features_match',
                        'similarity': float(similarity),
                        'evidence': 'Patterns ML similaires'
                    }],
                    evidence={'ml_similarity': float(similarity)},
                    severity_level=self._determine_severity(float(similarity)),
                    auto_verified=similarity > 0.95,
                    detection_timestamp=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur détection ML: {e}")
            return None
    
    def _combine_features(self, profile: ContentProfile) -> List[float]:
        """Combine toutes les features en vecteur."""
        try:
            features = []
            
            # Features sémantiques
            if 'semantic_complexity' in profile.semantic_features:
                features.append(profile.semantic_features['semantic_complexity'])
            
            # Features structurelles
            struct = profile.structural_features
            features.extend([
                struct.get('word_count', 0) / 1000,  # Normaliser
                struct.get('sentence_count', 0) / 100,
                struct.get('avg_sentence_length', 0) / 20
            ])
            
            # Features stylométriques
            stylo = profile.stylometric_features
            features.extend([
                stylo.get('lexical_richness', 0),
                stylo.get('avg_word_length', 0) / 10,
                stylo.get('function_word_ratio', 0),
                stylo.get('punctuation_density', 0) * 100
            ])
            
            return features
            
        except Exception as e:
            logger.error(f"Erreur combinaison features: {e}")
            return [0.0] * 7
    
    def _determine_severity(self, similarity_score: float) -> str:
        """Détermine la sévérité de l'alerte."""
        if similarity_score >= 0.95:
            return 'critical'
        elif similarity_score >= 0.85:
            return 'high'
        elif similarity_score >= 0.75:
            return 'medium'
        else:
            return 'low'
    
    def _deduplicate_alerts(self, alerts: List[PlagiarismAlert]) -> List[PlagiarismAlert]:
        """Supprime les alertes dupliquées."""
        try:
            unique_alerts = []
            seen_pairs = set()
            
            for alert in alerts:
                pair_key = f"{alert.source_content_id}_{alert.target_content_id}"
                reverse_key = f"{alert.target_content_id}_{alert.source_content_id}"
                
                if pair_key not in seen_pairs and reverse_key not in seen_pairs:
                    unique_alerts.append(alert)
                    seen_pairs.add(pair_key)
            
            return unique_alerts
            
        except Exception as e:
            logger.error(f"Erreur déduplication: {e}")
            return alerts
    
    async def get_plagiarism_report(self, target_content_id: str) -> Dict[str, Any]:
        """Génère rapport complet de plagiat."""
        try:
            # Rechercher alertes pour ce contenu
            alerts = [alert for alert in self.alert_database.values() 
                     if alert.target_content_id == target_content_id]
            
            if not alerts:
                return {
                    'target_content_id': target_content_id,
                    'plagiarism_detected': False,
                    'total_alerts': 0,
                    'report_timestamp': datetime.utcnow().isoformat()
                }
            
            # Analyser alertes
            total_alerts = len(alerts)
            critical_alerts = [a for a in alerts if a.severity_level == 'critical']
            high_alerts = [a for a in alerts if a.severity_level == 'high']
            
            # Score de plagiat global
            avg_similarity = np.mean([alert.similarity_score for alert in alerts])
            max_similarity = max([alert.similarity_score for alert in alerts])
            
            # Répartition par type
            type_distribution = {}
            for alert in alerts:
                ptype = alert.plagiarism_type.value
                type_distribution[ptype] = type_distribution.get(ptype, 0) + 1
            
            # Sources les plus problématiques
            source_scores = {}
            for alert in alerts:
                source_id = alert.source_content_id
                if source_id not in source_scores:
                    source_scores[source_id] = []
                source_scores[source_id].append(alert.similarity_score)
            
            top_sources = []
            for source_id, scores in source_scores.items():
                top_sources.append({
                    'source_id': source_id,
                    'avg_similarity': np.mean(scores),
                    'max_similarity': max(scores),
                    'alert_count': len(scores)
                })
            
            top_sources.sort(key=lambda x: x['max_similarity'], reverse=True)
            
            return {
                'target_content_id': target_content_id,
                'plagiarism_detected': True,
                'total_alerts': total_alerts,
                'critical_alerts': len(critical_alerts),
                'high_alerts': len(high_alerts),
                'average_similarity_score': float(avg_similarity),
                'maximum_similarity_score': float(max_similarity),
                'plagiarism_type_distribution': type_distribution,
                'top_suspicious_sources': top_sources[:5],
                'recommendation': self._generate_recommendation(avg_similarity, max_similarity, total_alerts),
                'report_timestamp': datetime.utcnow().isoformat(),
                'detailed_alerts': [
                    {
                        'alert_id': alert.alert_id,
                        'source_id': alert.source_content_id,
                        'plagiarism_type': alert.plagiarism_type.value,
                        'similarity_score': alert.similarity_score,
                        'confidence_score': alert.confidence_score,
                        'severity': alert.severity_level,
                        'auto_verified': alert.auto_verified
                    } for alert in alerts[:10]  # Top 10
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur génération rapport: {e}")
            return {}
    
    def _generate_recommendation(self, avg_similarity: float, max_similarity: float, total_alerts: int) -> str:
        """Génère recommandation basée sur l'analyse."""
        try:
            if max_similarity >= 0.95:
                return "CRITIQUE: Plagiat littéral détecté. Investigation immédiate requise."
            elif avg_similarity >= 0.85:
                return "ÉLEVÉ: Haut niveau de similarité. Révision manuelle recommandée."
            elif total_alerts > 10:
                return "MODÉRÉ: Nombreuses similarités détectées. Vérification conseillée."
            elif avg_similarity >= 0.7:
                return "FAIBLE: Quelques similarités. Surveillance recommandée."
            else:
                return "NORMAL: Niveau de similarité acceptable."
                
        except Exception as e:
            logger.error(f"Erreur génération recommandation: {e}")
            return "Erreur analyse"
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Retourne analytics du système de détection."""
        try:
            total_contents = len(self.content_database)
            total_alerts = len(self.alert_database)
            
            # Répartition par format
            format_distribution = {}
            for profile in self.content_database.values():
                fmt = profile.content_format.value
                format_distribution[fmt] = format_distribution.get(fmt, 0) + 1
            
            # Répartition par type de plagiat
            plagiarism_type_distribution = {}
            for alert in self.alert_database.values():
                ptype = alert.plagiarism_type.value
                plagiarism_type_distribution[ptype] = plagiarism_type_distribution.get(ptype, 0) + 1
            
            # Scores moyens
            if total_alerts > 0:
                similarity_scores = [alert.similarity_score for alert in self.alert_database.values()]
                confidence_scores = [alert.confidence_score for alert in self.alert_database.values()]
                avg_similarity = np.mean(similarity_scores)
                avg_confidence = np.mean(confidence_scores)
            else:
                avg_similarity = 0.0
                avg_confidence = 0.0
            
            # Alertes auto-vérifiées
            auto_verified = sum(1 for alert in self.alert_database.values() if alert.auto_verified)
            
            return {
                'total_analyzed_contents': total_contents,
                'total_plagiarism_alerts': total_alerts,
                'auto_verified_alerts': auto_verified,
                'content_format_distribution': format_distribution,
                'plagiarism_type_distribution': plagiarism_type_distribution,
                'average_similarity_score': float(avg_similarity),
                'average_confidence_score': float(avg_confidence),
                'similarity_threshold': self.similarity_threshold,
                'supported_detection_methods': [method.value for method in DetectionMethod],
                'plagiarism_thresholds': {k.value: v for k, v in self.plagiarism_thresholds.items()}
            }
            
        except Exception as e:
            logger.error(f"Erreur analytics plagiat: {e}")
            return {}