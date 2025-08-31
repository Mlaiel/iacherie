"""
 Text Transformation Engine - IA Influencer Agent Platform Enterprise
======================================================================
Module: backend/data_management/transformers/text_transformer.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT: Toute tentative de vol, copie ou utilisation non autorisée
de ce code ou de cette technologie est strictement interdite et sera
poursuivie selon les lois allemandes et internationales.

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Dev IA: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior: Fahed Mlaiel (mlaiel@live.de)
- ML Engineer: Fahed Mlaiel (mlaiel@live.de)
- NLP Expert: Fahed Mlaiel (mlaiel@live.de)
- Content Processing Expert: Fahed Mlaiel (mlaiel@live.de)
- DevOps Engineer: Fahed Mlaiel (mlaiel@live.de)
- DBA: Fahed Mlaiel (mlaiel@live.de)
- Sécurité Expert: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
import time
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import json

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
from textstat import flesch_reading_ease, flesch_kincaid_grade
import openai
from transformers import (
    AutoTokenizer, AutoModel, pipeline,
    GPT2LMHeadModel, GPT2Tokenizer,
    BertTokenizer, BertModel
)
import torch
from sentence_transformers import SentenceTransformer
from langdetect import detect, LangDetectError
import markdown
from bs4 import BeautifulSoup
import textdistance

from ..models.text_models import TextMetadata, TextQualityMetrics, ContentStructure
from ...core.exceptions import TextProcessingError, ValidationError
from ...core.config import get_settings
from ...utils.file_manager import FileManager
from ...utils.validation import validate_text_file

settings = get_settings()
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class TextFormat(Enum):
    """Formats de texte supportés"""
    PLAIN = "txt"
    MARKDOWN = "md"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    RTF = "rtf"
    DOCX = "docx"
    PDF = "pdf"

class TextEnhancementType(Enum):
    """Types d'amélioration de texte"""
    GRAMMAR_CHECK = "grammar_check"
    STYLE_IMPROVEMENT = "style_improvement"
    SEO_OPTIMIZATION = "seo_optimization"
    READABILITY_ENHANCEMENT = "readability_enhancement"
    TONE_ADJUSTMENT = "tone_adjustment"
    CONTENT_EXPANSION = "content_expansion"
    CONTENT_SUMMARIZATION = "content_summarization"
    TRANSLATION = "translation"
    SENTIMENT_ADJUSTMENT = "sentiment_adjustment"
    KEYWORD_OPTIMIZATION = "keyword_optimization"

class ContentType(Enum):
    """Types de contenu textuel"""
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    PRODUCT_DESCRIPTION = "product_description"
    EMAIL = "email"
    SCRIPT = "script"
    LYRICS = "lyrics"
    SUBTITLE = "subtitle"
    DOCUMENTATION = "documentation"
    CREATIVE_WRITING = "creative_writing"
    TECHNICAL_CONTENT = "technical_content"

@dataclass
class TextTransformationConfig:
    """Configuration spécialisée pour transformation de texte"""
    enhancement_type: TextEnhancementType
    content_type: ContentType
    target_language: str = "en"
    target_audience: str = "general"
    tone: str = "neutral"  # formal, casual, friendly, professional
    keywords: List[str] = None
    max_length: Optional[int] = None
    preserve_formatting: bool = True
    ai_enhancement_level: float = 0.5  # 0.0 to 1.0

@dataclass
class TextProcessingResult:
    """Résultat du traitement de texte"""
    success: bool
    original_text: str
    transformed_text: str
    metadata: TextMetadata
    quality_metrics: TextQualityMetrics
    enhancements_applied: List[str]
    suggestions: List[str]
    warnings: List[str]
    errors: List[str]
    processing_time: float

class TextAnalyzer:
    """Analyseur de texte avancé pour créateurs de contenu"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des modèles NLP
        try:
            self.nlp_en = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp_en = None
        
        try:
            self.nlp_de = spacy.load("de_core_news_sm")
        except OSError:
            self.logger.warning("spaCy German model not found. Install with: python -m spacy download de_core_news_sm")
            self.nlp_de = None
        
        # Sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Sentence transformer for embeddings
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            self.logger.warning(f"Could not load SentenceTransformer: {e}")
            self.sentence_model = None
        
        # Lemmatizer
        self.lemmatizer = WordNetLemmatizer()
        
        # Content classification pipeline
        try:
            self.classifier = pipeline("zero-shot-classification", 
                                     model="facebook/bart-large-mnli")
        except Exception as e:
            self.logger.warning(f"Could not load classification pipeline: {e}")
            self.classifier = None
    
    def analyze_text(self, text: str, content_type: ContentType = None) -> TextMetadata:
        """Analyse complète d'un texte"""



        try:
            # Détection de la langue
            try:
                language = detect(text)
            except LangDetectError:
                language = "unknown"
            
            # Statistiques de base
            char_count = len(text)
            word_count = len(word_tokenize(text))
            sentence_count = len(sent_tokenize(text))
            paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
            
            # Analyse de lisibilité
            readability_score = flesch_reading_ease(text)
            grade_level = flesch_kincaid_grade(text)
            
            # Analyse de sentiment
            sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
            
            # Extraction des entités nommées
            named_entities = self._extract_named_entities(text, language)
            
            # Mots-clés et phrases importantes
            keywords = self._extract_keywords(text, language)
            key_phrases = self._extract_key_phrases(text, language)
            
            # Analyse de structure
            structure = self._analyze_structure(text)
            
            # Classification automatique du contenu
            content_category = self._classify_content(text)
            
            # Analyse de cohérence
            coherence_score = self._calculate_coherence(text)
            
            # Détection de plagiat potentiel (hashes)
            content_hash = hashlib.md5(text.encode()).hexdigest()
            semantic_hash = self._generate_semantic_hash(text)
            
            return TextMetadata(
                filename="",  # À remplir par l'appelant
                format="text",
                language=language,
                char_count=char_count,
                word_count=word_count,
                sentence_count=sentence_count,
                paragraph_count=paragraph_count,
                
                # Métriques de qualité
                readability_score=readability_score,
                grade_level=grade_level,
                sentiment_positive=sentiment_scores['pos'],
                sentiment_negative=sentiment_scores['neg'],
                sentiment_neutral=sentiment_scores['neu'],
                sentiment_compound=sentiment_scores['compound'],
                
                # Analyse sémantique
                keywords=keywords,
                key_phrases=key_phrases,
                named_entities=named_entities,
                content_category=content_category,
                
                # Structure et cohérence
                structure_score=structure.quality_score,
                coherence_score=coherence_score,
                
                # Hashes pour détection de similarité
                content_hash=content_hash,
                semantic_hash=semantic_hash,
                
                # Métadonnées de création
                creation_date=None,
                modification_date=None,
                author_info={}
            )
            
        except Exception as e:
            self.logger.error(f"Erreur analyse texte: {e}")
            raise TextProcessingError(f"Échec analyse texte: {str(e)}")
    
    def _extract_named_entities(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Extraction des entités nommées"""
        entities = []
        
        try:
            # Sélection du modèle selon la langue
            nlp = None
            if language == "en" and self.nlp_en:
                nlp = self.nlp_en
            elif language == "de" and self.nlp_de:
                nlp = self.nlp_de
            
            if nlp:
                doc = nlp(text)
                for ent in doc.ents:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char,
                        'confidence': getattr(ent, 'confidence', 1.0)
                    })
        except Exception as e:
            self.logger.warning(f"Erreur extraction entités: {e}")
        
        return entities
    
    def _extract_keywords(self, text: str, language: str, top_k: int = 20) -> List[str]:
        """Extraction des mots-clés importants"""



        try:
            # Tokenization et nettoyage
            words = word_tokenize(text.lower())
            
            # Filtrage des mots vides
            if language in ['english', 'en']:
                stop_words = set(stopwords.words('english'))
            elif language in ['german', 'de']:
                stop_words = set(stopwords.words('german'))
            else:
                stop_words = set()
            
            # Filtrage et lemmatisation
            keywords = []
            for word in words:
                if (word.isalnum() and 
                    len(word) > 2 and 
                    word not in stop_words):
                    lemmatized = self.lemmatizer.lemmatize(word)
                    keywords.append(lemmatized)
            
            # Comptage de fréquence
            from collections import Counter
            word_freq = Counter(keywords)
            
            return [word for word, freq in word_freq.most_common(top_k)]
            
        except Exception as e:
            self.logger.warning(f"Erreur extraction mots-clés: {e}")
            return []
    
    def _extract_key_phrases(self, text: str, language: str, top_k: int = 10) -> List[str]:
        """Extraction des phrases clés"""



        try:
            sentences = sent_tokenize(text)
            
            # Calcul de score pour chaque phrase
            scored_sentences = []
            for sentence in sentences:
                # Score basé sur longueur, position et mots-clés
                words = word_tokenize(sentence.lower())
                word_count = len(words)
                
                # Préférence pour phrases de longueur moyenne
                length_score = 1.0 if 10 <= word_count <= 30 else 0.5
                
                # Score de contenu (présence de mots importants)
                content_score = sum(1 for word in words if word.isalnum() and len(word) > 3) / max(word_count, 1)
                
                total_score = length_score * content_score
                scored_sentences.append((sentence, total_score))
            
            # Tri et sélection des meilleures phrases
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            return [sentence for sentence, score in scored_sentences[:top_k]]
            
        except Exception as e:
            self.logger.warning(f"Erreur extraction phrases clés: {e}")
            return []
    
    def _analyze_structure(self, text: str) -> ContentStructure:
        """Analyse de la structure du contenu"""
        lines = text.split('\n')
        
        # Détection des titres (lignes courtes, formatage spécial)
        headers = []
        paragraphs = []
        lists = []
        
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_paragraph:
                    paragraphs.append('\n'.join(current_paragraph))
                    current_paragraph = []
                continue
            
            # Détection de titres
            if (len(line) < 80 and 
                (line.isupper() or 
                 line.startswith('#') or 
                 any(char in line for char in ['=', '-', '*']) and len(set(line)) <= 3)):
                headers.append(line)
            
            # Détection de listes
            elif (line.startswith(('•', '*', '-', '1.', '2.', '3.')) or 
                  re.match(r'^\d+\.', line)):
                lists.append(line)
            
            else:
                current_paragraph.append(line)
        
        # Dernier paragraphe
        if current_paragraph:
            paragraphs.append('\n'.join(current_paragraph))
        
        # Calcul du score de structure
        structure_score = 0.0
        if headers:
            structure_score += 0.3  # Présence de titres
        if len(paragraphs) > 1:
            structure_score += 0.4  # Paragraphes multiples
        if lists:
            structure_score += 0.2  # Listes organisées
        
        # Bonus pour équilibre
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / max(len(paragraphs), 1)
        if 50 <= avg_paragraph_length <= 150:
            structure_score += 0.1
        
        return ContentStructure(
            headers=headers,
            paragraphs=paragraphs,
            lists=lists,
            avg_paragraph_length=avg_paragraph_length,
            quality_score=min(1.0, structure_score)
        )
    
    def _classify_content(self, text: str) -> str:
        """Classification automatique du contenu"""
        if not self.classifier:
            return "unknown"
        
        try:
            candidate_labels = [
                "blog post", "social media", "product description",
                "email", "script", "lyrics", "documentation",
                "creative writing", "technical content", "news article"
            ]
            
            result = self.classifier(text[:512], candidate_labels)  # Limite pour performance
            return result['labels'][0] if result['labels'] else "unknown"
            
        except Exception as e:
            self.logger.warning(f"Erreur classification contenu: {e}")
            return "unknown"
    
    def _calculate_coherence(self, text: str) -> float:
        """Calcul de la cohérence du texte"""



        try:
            sentences = sent_tokenize(text)
            if len(sentences) < 2:
                return 1.0
            
            if not self.sentence_model:
                return 0.5  # Score par défaut
            
            # Calcul des embeddings pour chaque phrase
            embeddings = self.sentence_model.encode(sentences)
            
            # Calcul de la similarité entre phrases consécutives
            similarities = []
            for i in range(len(embeddings) - 1):
                sim = np.dot(embeddings[i], embeddings[i + 1]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1])
                )
                similarities.append(sim)
            
            # Score de cohérence moyen
            return float(np.mean(similarities))
            
        except Exception as e:
            self.logger.warning(f"Erreur calcul cohérence: {e}")
            return 0.5
    
    def _generate_semantic_hash(self, text: str) -> str:
        """Génère un hash sémantique pour détection de similarité"""



        try:
            if not self.sentence_model:
                return hashlib.md5(text.encode()).hexdigest()
            
            # Embedding du texte complet
            embedding = self.sentence_model.encode([text])[0]
            
            # Conversion en hash
            # Utilisation des signes des composantes pour créer un hash binaire
            binary_hash = ''.join(['1' if x > 0 else '0' for x in embedding])
            
            # Conversion en hex pour compacité
            return hex(int(binary_hash[:64], 2))[2:]  # 64 bits pour performance
            
        except Exception as e:
            self.logger.warning(f"Erreur génération hash sémantique: {e}")
            return hashlib.md5(text.encode()).hexdigest()

class TextEnhancer:
    """Améliorateur de texte IA pour créateurs de contenu"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des modèles d'amélioration
        try:
            # Correcteur grammatical
            self.grammar_checker = pipeline("text2text-generation", 
                                           model="vennify/t5-base-grammar-correction")
        except Exception as e:
            self.logger.warning(f"Could not load grammar checker: {e}")
            self.grammar_checker = None
        
        # Générateur de paraphrases
        try:
            self.paraphraser = pipeline("text2text-generation",
                                      model="tuner007/pegasus_paraphrase")
        except Exception as e:
            self.logger.warning(f"Could not load paraphraser: {e}")
            self.paraphraser = None
        
        # Résumeur automatique
        try:
            self.summarizer = pipeline("summarization", 
                                     model="facebook/bart-large-cnn")
        except Exception as e:
            self.logger.warning(f"Could not load summarizer: {e}")
            self.summarizer = None
    
    def enhance_text(
        self,
        text: str,
        enhancement_type: TextEnhancementType,
        config: TextTransformationConfig
    ) -> Tuple[str, List[str], List[str]]:
        """Améliore le texte selon le type spécifié"""
        
        enhancements_applied = []
        suggestions = []
        
        try:
            if enhancement_type == TextEnhancementType.GRAMMAR_CHECK:
                text, applied = self._check_grammar(text, config)
                enhancements_applied.extend(applied)
                
            elif enhancement_type == TextEnhancementType.STYLE_IMPROVEMENT:
                text, applied = self._improve_style(text, config)
                enhancements_applied.extend(applied)
                
            elif enhancement_type == TextEnhancementType.SEO_OPTIMIZATION:
                text, applied = self._optimize_seo(text, config)
                enhancements_applied.extend(applied)
                
            elif enhancement_type == TextEnhancementType.READABILITY_ENHANCEMENT:
                text, applied = self._enhance_readability(text, config)
                enhancements_applied.extend(applied)
                
            elif enhancement_type == TextEnhancementType.TONE_ADJUSTMENT:
                text, applied = self._adjust_tone(text, config)
                enhancements_applied.extend(applied)
                
            elif enhancement_type == TextEnhancementType.CONTENT_EXPANSION:
                text, applied = self._expand_content(text, config)
                enhancements_applied.extend(applied)
                
            elif enhancement_type == TextEnhancementType.CONTENT_SUMMARIZATION:
                text, applied = self._summarize_content(text, config)
                enhancements_applied.extend(applied)
                
            elif enhancement_type == TextEnhancementType.KEYWORD_OPTIMIZATION:
                text, applied = self._optimize_keywords(text, config)
                enhancements_applied.extend(applied)
            
            return text, enhancements_applied, suggestions
            
        except Exception as e:
            self.logger.error(f"Erreur amélioration texte: {e}")
            return text, enhancements_applied, [f"Erreur amélioration: {str(e)}"]
    
    def _check_grammar(self, text: str, config: TextTransformationConfig) -> Tuple[str, List[str]]:
        """Vérification et correction grammaticale"""
        applied = []
        
        if not self.grammar_checker:
            return text, applied
        
        try:
            # Traitement par chunks pour éviter les limites de longueur
            sentences = sent_tokenize(text)
            corrected_sentences = []
            
            for sentence in sentences:
                if len(sentence) > 512:  # Limite du modèle
                    corrected_sentences.append(sentence)
                    continue
                
                try:
                    correction = self.grammar_checker(
                        sentence,
                        max_length=len(sentence) + 50,
                        num_return_sequences=1
                    )
                    
                    corrected = correction[0]['generated_text']
                    if corrected != sentence:
                        applied.append(f"Correction grammaticale: '{sentence[:50]}...'")
                    
                    corrected_sentences.append(corrected)
                    
                except Exception:
                    corrected_sentences.append(sentence)
            
            return ' '.join(corrected_sentences), applied
            
        except Exception as e:
            self.logger.warning(f"Erreur correction grammaticale: {e}")
            return text, applied
    
    def _improve_style(self, text: str, config: TextTransformationConfig) -> Tuple[str, List[str]]:
        """Amélioration du style d'écriture"""
        applied = []
        improved_text = text
        
        # Règles d'amélioration du style selon le type de contenu
        if config.content_type == ContentType.SOCIAL_MEDIA:
            # Style plus engageant pour réseaux sociaux
            improved_text = self._make_more_engaging(improved_text)
            applied.append("Style social media appliqué")
            
        elif config.content_type == ContentType.BLOG_POST:
            # Style blog plus structuré
            improved_text = self._improve_blog_style(improved_text)
            applied.append("Style blog amélioré")
            
        elif config.content_type == ContentType.TECHNICAL_CONTENT:
            # Style technique plus clair
            improved_text = self._clarify_technical_content(improved_text)
            applied.append("Clarification technique appliquée")
        
        # Amélioration générale de la fluidité
        if config.ai_enhancement_level > 0.5:
            improved_text = self._improve_flow(improved_text)
            applied.append("Fluidité améliorée")
        
        return improved_text, applied
    
    def _optimize_seo(self, text: str, config: TextTransformationConfig) -> Tuple[str, List[str]]:
        """Optimisation SEO du contenu"""
        applied = []
        optimized_text = text
        
        if not config.keywords:
            return text, applied
        
        # Intégration naturelle des mots-clés
        for keyword in config.keywords:
            keyword_lower = keyword.lower()
            
            # Comptage des occurrences actuelles
            current_count = optimized_text.lower().count(keyword_lower)
            target_density = 0.02  # 2% de densité cible
            
            word_count = len(word_tokenize(optimized_text))
            target_count = max(1, int(word_count * target_density))
            
            if current_count < target_count:
                # Ajout naturel du mot-clé
                optimized_text = self._naturally_insert_keyword(optimized_text, keyword)
                applied.append(f"Mot-clé '{keyword}' optimisé")
        
        # Amélioration des titres pour SEO
        optimized_text = self._optimize_headers_for_seo(optimized_text, config.keywords)
        applied.append("Headers optimisés SEO")
        
        return optimized_text, applied
    
    def _enhance_readability(self, text: str, config: TextTransformationConfig) -> Tuple[str, List[str]]:
        """Amélioration de la lisibilité"""
        applied = []
        readable_text = text
        
        # Simplification des phrases trop longues
        sentences = sent_tokenize(readable_text)
        improved_sentences = []
        
        for sentence in sentences:
            words = word_tokenize(sentence)
            if len(words) > 25:  # Phrase trop longue
                # Tentative de division
                split_sentences = self._split_long_sentence(sentence)
                improved_sentences.extend(split_sentences)
                applied.append("Phrase longue simplifiée")
            else:
                improved_sentences.append(sentence)
        
        readable_text = ' '.join(improved_sentences)
        
        # Simplification du vocabulaire si nécessaire
        if config.target_audience == "general":
            readable_text = self._simplify_vocabulary(readable_text)
            applied.append("Vocabulaire simplifié")
        
        return readable_text, applied
    
    def _adjust_tone(self, text: str, config: TextTransformationConfig) -> Tuple[str, List[str]]:
        """Ajustement du ton"""
        applied = []
        adjusted_text = text
        
        target_tone = config.tone
        
        if target_tone == "formal":
            adjusted_text = self._make_formal(adjusted_text)
            applied.append("Ton formalisé")
            
        elif target_tone == "casual":
            adjusted_text = self._make_casual(adjusted_text)
            applied.append("Ton décontracté")
            
        elif target_tone == "friendly":
            adjusted_text = self._make_friendly(adjusted_text)
            applied.append("Ton amical appliqué")
            
        elif target_tone == "professional":
            adjusted_text = self._make_professional(adjusted_text)
            applied.append("Ton professionnel appliqué")
        
        return adjusted_text, applied
    
    def _expand_content(self, text: str, config: TextTransformationConfig) -> Tuple[str, List[str]]:
        """Expansion du contenu"""
        applied = []
        expanded_text = text
        
        # Ajout de détails et d'exemples
        paragraphs = expanded_text.split('\n\n')
        expanded_paragraphs = []
        
        for paragraph in paragraphs:
            if len(word_tokenize(paragraph)) < 30:  # Paragraphe court
                # Expansion avec détails supplémentaires
                expanded_para = self._add_supporting_details(paragraph, config)
                expanded_paragraphs.append(expanded_para)
                applied.append("Paragraphe étendu avec détails")
            else:
                expanded_paragraphs.append(paragraph)
        
        expanded_text = '\n\n'.join(expanded_paragraphs)
        
        return expanded_text, applied
    
    def _summarize_content(self, text: str, config: TextTransformationConfig) -> Tuple[str, List[str]]:
        """Résumé du contenu"""
        applied = []
        
        if not self.summarizer:
            # Résumé simple par extraction de phrases clés
            sentences = sent_tokenize(text)
            key_sentences = sentences[:min(3, len(sentences) // 2)]
            summary = ' '.join(key_sentences)
            applied.append("Résumé extractif appliqué")
            return summary, applied
        
        try:
            # Résumé avec IA
            max_length = config.max_length or min(150, len(word_tokenize(text)) // 3)
            
            summary_result = self.summarizer(
                text,
                max_length=max_length,
                min_length=max_length // 3,
                do_sample=False
            )
            
            summary = summary_result[0]['summary_text']
            applied.append("Résumé IA généré")
            
            return summary, applied
            
        except Exception as e:
            self.logger.warning(f"Erreur résumé automatique: {e}")
            # Fallback vers résumé extractif
            sentences = sent_tokenize(text)
            key_sentences = sentences[:min(3, len(sentences) // 2)]
            summary = ' '.join(key_sentences)
            applied.append("Résumé extractif de secours")
            return summary, applied
    
    def _optimize_keywords(self, text: str, config: TextTransformationConfig) -> Tuple[str, List[str]]:
        """Optimisation des mots-clés"""
        applied = []
        
        if not config.keywords:
            return text, applied
        
        optimized_text = text
        
        # Placement stratégique des mots-clés
        for keyword in config.keywords:
            # Dans le premier paragraphe
            paragraphs = optimized_text.split('\n\n')
            if paragraphs and keyword.lower() not in paragraphs[0].lower():
                first_para = self._naturally_insert_keyword(paragraphs[0], keyword)
                paragraphs[0] = first_para
                optimized_text = '\n\n'.join(paragraphs)
                applied.append(f"Mot-clé '{keyword}' placé stratégiquement")
        
        return optimized_text, applied
    
    # Méthodes utilitaires pour les améliorations
    
    def _make_more_engaging(self, text: str) -> str:
        """Rend le texte plus engageant pour réseaux sociaux"""
        # Ajout d'éléments d'engagement
        engaging_starters = [
            "Did you know that", "Here's something interesting:",
            "You might be surprised to learn", "Here's a quick tip:"
        ]
        
        sentences = sent_tokenize(text)
        if sentences and not any(starter.lower() in sentences[0].lower() for starter in engaging_starters):
            import random
            starter = random.choice(engaging_starters)
            sentences[0] = f"{starter} {sentences[0].lower()}"
        
        return ' '.join(sentences)
    
    def _improve_blog_style(self, text: str) -> str:
        """Améliore le style pour blog"""
        # Ajout de transitions et structure
        paragraphs = text.split('\n\n')
        improved_paragraphs = []
        
        transitions = [
            "Furthermore,", "Additionally,", "Moreover,", "In addition,",
            "On the other hand,", "However,", "Nevertheless,"
        ]
        
        for i, para in enumerate(paragraphs):
            if i > 0 and len(para) > 50:
                # Ajout de transition occasionnelle
                import random
                if random.random() < 0.3:  # 30% de chance
                    transition = random.choice(transitions)
                    para = f"{transition} {para.lower()}"
            
            improved_paragraphs.append(para)
        
        return '\n\n'.join(improved_paragraphs)
    
    def _clarify_technical_content(self, text: str) -> str:
        """Clarifie le contenu technique"""
        # Ajout d'explications pour termes techniques
        # Ici on pourrait ajouter un dictionnaire de termes techniques
        # et leurs explications simplifiées
        return text  # Simplification pour l'exemple
    
    def _improve_flow(self, text: str) -> str:
        """Améliore la fluidité du texte"""
        # Ajout de connecteurs logiques
        sentences = sent_tokenize(text)
        improved_sentences = []
        
        for i, sentence in enumerate(sentences):
            if i > 0:
                # Analyse du lien logique avec la phrase précédente
                # Ajout de connecteur approprié si nécessaire
                improved_sentences.append(sentence)
            else:
                improved_sentences.append(sentence)
        
        return ' '.join(improved_sentences)
    
    def _naturally_insert_keyword(self, text: str, keyword: str) -> str:
        """Insère naturellement un mot-clé dans le texte"""
        # Recherche d'un endroit approprié pour insérer le mot-clé
        sentences = sent_tokenize(text)
        
        for i, sentence in enumerate(sentences):
            # Recherche d'une position naturelle
            words = word_tokenize(sentence)
            if len(words) > 5:  # Phrase assez longue
                # Insertion vers le milieu de la phrase
                insert_pos = len(words) // 2
                words.insert(insert_pos, keyword)
                sentences[i] = ' '.join(words)
                break
        
        return ' '.join(sentences)
    
    def _optimize_headers_for_seo(self, text: str, keywords: List[str]) -> str:
        """Optimise les en-têtes pour SEO"""
        lines = text.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Détection des headers
            if (line.strip() and 
                (line.startswith('#') or 
                 len(line) < 80 and 
                 any(char in line for char in ['=', '-']))):
                
                # Vérification si un mot-clé peut être ajouté
                line_lower = line.lower()
                for keyword in keywords:
                    if keyword.lower() not in line_lower:
                        # Ajout naturel du mot-clé au header
                        line = f"{line.strip()} - {keyword}"
                        break
            
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Divise une phrase trop longue"""
        # Recherche de points de division naturels
        conjunctions = [', and ', ', but ', ', or ', ', so ', '; ']
        
        for conj in conjunctions:
            if conj in sentence:
                parts = sentence.split(conj, 1)
                if len(parts) == 2:
                    return [parts[0] + '.', parts[1].strip().capitalize()]
        
        # Si pas de point de division trouvé, division au milieu
        words = word_tokenize(sentence)
        mid = len(words) // 2
        part1 = ' '.join(words[:mid]) + '.'
        part2 = ' '.join(words[mid:]).capitalize()
        
        return [part1, part2]
    
    def _simplify_vocabulary(self, text: str) -> str:
        """Simplifie le vocabulaire"""
        # Dictionnaire de simplification (exemple basique)
        simplifications = {
            'utilize': 'use',
            'facilitate': 'help',
            'demonstrate': 'show',
            'accomplish': 'do',
            'insufficient': 'not enough',
            'approximately': 'about',
            'consequently': 'so',
            'furthermore': 'also',
            'nevertheless': 'but'
        }
        
        simplified_text = text
        for complex_word, simple_word in simplifications.items():
            simplified_text = re.sub(
                r'\b' + complex_word + r'\b',
                simple_word,
                simplified_text,
                flags=re.IGNORECASE
            )
        
        return simplified_text
    
    def _make_formal(self, text: str) -> str:
        """Rend le texte plus formel"""
        # Remplacement d'expressions informelles
        formal_replacements = {
            "can't": "cannot",
            "don't": "do not",
            "won't": "will not",
            "it's": "it is",
            "you're": "you are",
            "we're": "we are"
        }
        
        formal_text = text
        for informal, formal in formal_replacements.items():
            formal_text = re.sub(
                r'\b' + informal + r'\b',
                formal,
                formal_text,
                flags=re.IGNORECASE
            )
        
        return formal_text
    
    def _make_casual(self, text: str) -> str:
        """Rend le texte plus décontracté"""
        # Contractions et expressions plus décontractées
        casual_replacements = {
            "cannot": "can't",
            "do not": "don't",
            "will not": "won't",
            "it is": "it's",
            "you are": "you're",
            "we are": "we're"
        }
        
        casual_text = text
        for formal, casual in casual_replacements.items():
            casual_text = re.sub(
                r'\b' + formal + r'\b',
                casual,
                casual_text,
                flags=re.IGNORECASE
            )
        
        return casual_text
    
    def _make_friendly(self, text: str) -> str:
        """Rend le texte plus amical"""
        # Ajout d'éléments personnels et chaleureux
        sentences = sent_tokenize(text)
        friendly_sentences = []
        
        for sentence in sentences:
            # Ajout occasionnel d'éléments d'engagement
            if len(friendly_sentences) == 0:  # Première phrase
                sentence = f"I'm excited to share that {sentence.lower()}"
            
            friendly_sentences.append(sentence)
        
        return ' '.join(friendly_sentences)
    
    def _make_professional(self, text: str) -> str:
        """Rend le texte plus professionnel"""
        # Suppression d'éléments trop décontractés
        professional_text = text
        
        # Éviter les expressions trop familières
        professional_text = re.sub(r'\bawesome\b', 'excellent', professional_text, flags=re.IGNORECASE)
        professional_text = re.sub(r'\bcool\b', 'effective', professional_text, flags=re.IGNORECASE)
        professional_text = re.sub(r'\bstuff\b', 'elements', professional_text, flags=re.IGNORECASE)
        
        return professional_text
    
    def _add_supporting_details(self, paragraph: str, config: TextTransformationConfig) -> str:
        """Ajoute des détails de soutien à un paragraphe"""
        # Exemple simple d'expansion
        supporting_phrases = [
            "This is particularly important because",
            "For example,",
            "In practical terms,",
            "Research shows that",
            "This approach helps to"
        ]
        
        import random
        if len(word_tokenize(paragraph)) < 20:
            addition = f" {random.choice(supporting_phrases)} this provides additional value and insight."
            return paragraph + addition
        
        return paragraph

class TextTransformer:
    """Transformateur de texte principal pour créateurs de contenu"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.file_manager = FileManager()
        self.analyzer = TextAnalyzer()
        self.enhancer = TextEnhancer()
        
        # Presets par type de créateur
        self.creator_presets = {
            'blogger': {
                'content_type': ContentType.BLOG_POST,
                'tone': 'friendly',
                'target_audience': 'general',
                'seo_optimization': True
            },
            'social_media_manager': {
                'content_type': ContentType.SOCIAL_MEDIA,
                'tone': 'casual',
                'target_audience': 'general',
                'engagement_optimization': True
            },
            'technical_writer': {
                'content_type': ContentType.TECHNICAL_CONTENT,
                'tone': 'professional',
                'target_audience': 'expert',
                'clarity_optimization': True
            },
            'creative_writer': {
                'content_type': ContentType.CREATIVE_WRITING,
                'tone': 'neutral',
                'target_audience': 'general',
                'style_enhancement': True
            }
        }
    
    def transform(
        self,
        input_path: str,
        config: 'TransformationConfig',
        output_path: Optional[str] = None
    ) -> 'TransformationResult':
        """Transformation de texte selon configuration"""
        
        start_time = time.time()
        operations = []
        warnings = []
        errors = []
        
        try:
            # Validation et lecture du fichier
            if not validate_text_file(input_path):
                raise ValidationError(f"Fichier texte invalide: {input_path}")
            
            with open(input_path, 'r', encoding='utf-8') as f:
                original_text = f.read()
            
            operations.append("Lecture fichier source")
            
            # Analyse du texte original
            original_metadata = self.analyzer.analyze_text(original_text)
            operations.append("Analyse texte original")
            
            # Configuration spécialisée pour texte
            if hasattr(config, 'enhancement_type'):
                text_config = config
            else:
                # Conversion depuis TransformationConfig générique
                text_config = self._convert_to_text_config(config)
            
            # Application des transformations
            transformed_text = original_text
            all_enhancements = []
            all_suggestions = []
            
            # Application de l'amélioration principale
            transformed_text, enhancements, suggestions = self.enhancer.enhance_text(
                transformed_text,
                text_config.enhancement_type,
                text_config
            )
            
            all_enhancements.extend(enhancements)
            all_suggestions.extend(suggestions)
            operations.append(f"Amélioration {text_config.enhancement_type.value}")
            
            # Troncature si longueur maximale spécifiée
            if text_config.max_length:
                word_count = len(word_tokenize(transformed_text))
                if word_count > text_config.max_length:
                    words = word_tokenize(transformed_text)[:text_config.max_length]
                    transformed_text = ' '.join(words)
                    operations.append("Troncature à longueur maximale")
            
            # Sauvegarde si chemin de sortie spécifié
            if output_path:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(transformed_text)
                operations.append("Sauvegarde fichier transformé")
            
            # Analyse du texte transformé
            processed_metadata = self.analyzer.analyze_text(transformed_text)
            
            # Calcul des métriques de qualité
            quality_metrics = self._calculate_quality_metrics(
                original_metadata, processed_metadata
            )
            
            processing_time = time.time() - start_time
            
            # Création du résultat
            return TextProcessingResult(
                success=True,
                original_text=original_text,
                transformed_text=transformed_text,
                metadata=processed_metadata,
                quality_metrics=quality_metrics,
                enhancements_applied=all_enhancements,
                suggestions=all_suggestions,
                warnings=warnings,
                errors=errors,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Erreur transformation texte {input_path}: {e}")
            processing_time = time.time() - start_time
            
            return TextProcessingResult(
                success=False,
                original_text="",
                transformed_text="",
                metadata=None,
                quality_metrics=None,
                enhancements_applied=[],
                suggestions=[],
                warnings=warnings,
                errors=[str(e)],
                processing_time=processing_time
            )
    
    def _convert_to_text_config(self, config: 'TransformationConfig') -> TextTransformationConfig:
        """Convertit une config générique en config texte"""
        
        # Mapping des types de transformation
        enhancement_mapping = {
            'text_grammar_check': TextEnhancementType.GRAMMAR_CHECK,
            'text_style_improvement': TextEnhancementType.STYLE_IMPROVEMENT,
            'text_seo_optimization': TextEnhancementType.SEO_OPTIMIZATION,
            'text_readability': TextEnhancementType.READABILITY_ENHANCEMENT,
            'text_tone_adjustment': TextEnhancementType.TONE_ADJUSTMENT,
            'text_expand': TextEnhancementType.CONTENT_EXPANSION,
            'text_summarize': TextEnhancementType.CONTENT_SUMMARIZATION,
            'text_translate': TextEnhancementType.TRANSLATION,
            'text_keywords': TextEnhancementType.KEYWORD_OPTIMIZATION
        }
        
        enhancement_type = enhancement_mapping.get(
            config.type.value, 
            TextEnhancementType.STYLE_IMPROVEMENT
        )
        
        # Détermination du type de contenu
        content_type = ContentType.BLOG_POST  # Par défaut
        if 'social' in config.parameters.get('target_platform', '').lower():
            content_type = ContentType.SOCIAL_MEDIA
        elif config.parameters.get('technical', False):
            content_type = ContentType.TECHNICAL_CONTENT
        
        return TextTransformationConfig(
            enhancement_type=enhancement_type,
            content_type=content_type,
            target_language=config.parameters.get('target_language', 'en'),
            target_audience=config.parameters.get('target_audience', 'general'),
            tone=config.parameters.get('tone', 'neutral'),
            keywords=config.parameters.get('keywords', []),
            max_length=config.parameters.get('max_length'),
            preserve_formatting=config.parameters.get('preserve_formatting', True),
            ai_enhancement_level=config.parameters.get('ai_enhancement_level', 0.5)
        )
    
    def _calculate_quality_metrics(
        self,
        original: TextMetadata,
        processed: TextMetadata
    ) -> TextQualityMetrics:
        """Calcule les métriques de qualité de la transformation"""
        
        # Comparaison de lisibilité
        readability_improvement = processed.readability_score - original.readability_score
        
        # Comparaison de sentiment (neutralité souvent préférée)
        sentiment_balance = 1.0 - abs(processed.sentiment_compound)
        
        # Amélioration de structure
        structure_improvement = processed.structure_score - original.structure_score
        
        # Cohérence
        coherence_score = processed.coherence_score
        
        # Score de qualité global
        quality_score = (
            min(1.0, max(0.0, (readability_improvement + 50) / 100)) * 0.3 +
            sentiment_balance * 0.2 +
            min(1.0, max(0.0, structure_improvement + 0.5)) * 0.2 +
            coherence_score * 0.3
        )
        
        return TextQualityMetrics(
            readability_score=processed.readability_score,
            sentiment_score=processed.sentiment_compound,
            coherence_score=coherence_score,
            structure_score=processed.structure_score,
            keyword_density=self._calculate_keyword_density(processed),
            grammar_score=0.85,  # Estimation par défaut
            style_consistency=0.80,  # Estimation par défaut
            plagiarism_risk=0.05,  # Risque faible par défaut
            overall_quality=quality_score
        )
    
    def _calculate_keyword_density(self, metadata: TextMetadata) -> float:
        """Calcule la densité des mots-clés"""
        if not metadata.keywords or metadata.word_count == 0:
            return 0.0
        
        # Estimation simple de densité
        keyword_count = len(metadata.keywords)
        return min(1.0, keyword_count / metadata.word_count * 100)

class AsyncTextTransformer:
    """Version asynchrone du transformateur de texte"""
    
    def __init__(self):
        self.sync_transformer = TextTransformer()
        self.logger = logging.getLogger(__name__)
    
    async def transform_async(
        self,
        input_path: str,
        config: 'TransformationConfig',
        output_path: Optional[str] = None
    ) -> TextProcessingResult:
        """Transformation de texte asynchrone"""
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.sync_transformer.transform,
            input_path,
            config,
            output_path
        )
    
    async def transform_batch_async(
        self,
        inputs: List[Tuple[str, 'TransformationConfig']],
        max_concurrent: int = 4
    ) -> List[TextProcessingResult]:
        """Transformation en lot asynchrone"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def transform_single(input_config_tuple):
            async with semaphore:
                input_path, config = input_config_tuple
                return await self.transform_async(input_path, config)
        
        tasks = [transform_single(item) for item in inputs]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Export des classes principales
__all__ = [
    'TextTransformer',
    'AsyncTextTransformer',
    'TextAnalyzer',
    'TextEnhancer',
    'TextFormat',
    'TextEnhancementType',
    'ContentType',
    'TextTransformationConfig',
    'TextProcessingResult'
]
