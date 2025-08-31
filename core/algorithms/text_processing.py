"""Text Processing Engine - Advanced Natural Language Processing
===========================================================

Professional text processing engine for content creators providing:
- Natural Language Understanding & Analysis
- Sentiment Analysis & Emotion Detection
- Topic Modeling & Classification
- Text Similarity & Semantic Search
- Content Generation & Enhancement
- Language Detection & Translation
- Named Entity Recognition (NER)
- Text Summarization & Key Phrase Extraction
- SEO Content Optimization
- Copyright & Plagiarism Detection

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use strictly prohibited
"""import re
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass
import torch
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    pipeline, BertTokenizer, BertModel, RobertaTokenizer, RobertaModel,
    T5Tokenizer, T5ForConditionalGeneration
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import spacy
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import hashlib
from collections import Counter
import langdetect

logger = logging.getLogger(__name__)

@dataclass
class TextFeatures:
    """Comprehensive text feature representation"""    linguistic_features: Dict[str, Any]
    semantic_features: Dict[str, np.ndarray]
    sentiment_features: Dict[str, float]
    structural_features: Dict[str, int]
    quality_metrics: Dict[str, float]
    fingerprint: str
    metadata: Dict[str, Any]

@dataclass
class NamedEntity:
    """Named entity representation"""    text: str
    label: str
    start: int
    end: int
    confidence: float

@dataclass
class SentimentResult:
    """Sentiment analysis result"""    polarity: float
    subjectivity: float
    emotion_scores: Dict[str, float]
    confidence: float

class TextProcessingEngine:
    """    Industrial-grade text processing engine for content creators
    """    
    def __init__(self, language: str = 'en'):
        self.language = language
        
        # Initialize models
        self._initialize_models()
        
        # Initialize NLP libraries
        self._initialize_nlp_libraries()
        
        # Initialize vectorizers
        self._initialize_vectorizers()
        
        logger.info("TextProcessingEngine initialized successfully")
    
    def _initialize_models(self) -> None:
        """Initialize transformer models"""        try:
            # BERT for general text understanding
            self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.bert_model = BertModel.from_pretrained('bert-base-uncased')
            
            # RoBERTa for enhanced understanding
            self.roberta_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
            self.roberta_model = RobertaModel.from_pretrained('roberta-base')
            
            # T5 for text generation
            self.t5_tokenizer = T5Tokenizer.from_pretrained('t5-small')
            self.t5_model = T5ForConditionalGeneration.from_pretrained('t5-small')
            
            # Sentiment analysis pipeline
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Emotion analysis pipeline
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            
            # Text summarization pipeline
            self.summarization_pipeline = pipeline(
                "summarization",
                model="facebook/bart-large-cnn"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize transformer models: {e}")
            raise
    
    def _initialize_nlp_libraries(self) -> None:
        """Initialize NLP libraries"""        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            # Initialize NLTK components
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
            
            # Load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, some features may be limited")
                self.nlp = None
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP libraries: {e}")
            raise
    
    def _initialize_vectorizers(self) -> None:
        """Initialize text vectorizers"""        try:
            # TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            
            # LDA for topic modeling
            self.lda_model = LatentDirichletAllocation(
                n_components=10,
                random_state=42
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize vectorizers: {e}")
            raise
    
    def process(self, text_data: Union[str, List[str]], 
                config: Dict[str, Any]) -> Dict[str, Any]:
        """        Comprehensive text processing pipeline
        
        Args:
            text_data: Text string or list of text strings
            config: Processing configuration parameters
            
        Returns:
            Complete text analysis results
        """        try:
            # Normalize input
            if isinstance(text_data, str):
                texts = [text_data]
            else:
                texts = text_data
            
            results = []
            
            for text in texts:
                # Preprocess text
                cleaned_text = self._preprocess_text(text, config)
                
                # Extract comprehensive features
                features = self._extract_text_features(cleaned_text, config)
                
                # Perform sentiment analysis
                sentiment = self._analyze_sentiment(cleaned_text, config)
                
                # Extract named entities
                entities = self._extract_named_entities(cleaned_text, config)
                
                # Generate text embeddings
                embeddings = self._generate_embeddings(cleaned_text, config)
                
                # Analyze text quality
                quality_metrics = self._analyze_text_quality(cleaned_text)
                
                # Generate text fingerprint
                fingerprint = self._generate_text_fingerprint(cleaned_text)
                
                # Topic modeling
                topics = self._extract_topics(cleaned_text, config)
                
                # Text enhancement suggestions
                enhancements = self._suggest_enhancements(cleaned_text, config)
                
                # SEO analysis
                seo_analysis = self._analyze_seo_factors(cleaned_text, config)
                
                # Extract metadata
                metadata = self._extract_text_metadata(text, cleaned_text)
                
                result = {
                    'original_text': text,
                    'cleaned_text': cleaned_text,
                    'features': features,
                    'sentiment': sentiment,
                    'entities': entities,
                    'embeddings': embeddings,
                    'quality_metrics': quality_metrics,
                    'fingerprint': fingerprint,
                    'topics': topics,
                    'enhancements': enhancements,
                    'seo_analysis': seo_analysis,
                    'metadata': metadata,
                    'processing_config': config
                }
                
                results.append(result)
            
            # Return single result if single input, otherwise list
            return results[0] if len(results) == 1 else results
            
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            raise
    
    def _preprocess_text(self, text: str, config: Dict[str, Any]) -> str:
        """Preprocess text for analysis"""        try:
            # Remove special characters if requested
            if config.get('remove_special_chars', False):
                text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
            
            # Convert to lowercase if requested
            if config.get('lowercase', True):
                text = text.lower()
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Remove URLs
            if config.get('remove_urls', True):
                text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            
            # Remove email addresses
            if config.get('remove_emails', True):
                text = re.sub(r'\S+@\S+', '', text)
            
            # Remove extra spaces after cleaning
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
            
        except Exception as e:
            logger.error(f"Text preprocessing failed: {e}")
            return text
    
    def _extract_text_features(self, text: str, config: Dict[str, Any]) -> TextFeatures:
        """Extract comprehensive text features"""        try:
            # Linguistic features
            linguistic_features = self._extract_linguistic_features(text)
            
            # Semantic features
            semantic_features = self._extract_semantic_features(text, config)
            
            # Sentiment features
            sentiment_features = self._extract_sentiment_features(text)
            
            # Structural features
            structural_features = self._extract_structural_features(text)
            
            # Quality metrics
            quality_metrics = self._extract_quality_metrics(text)
            
            # Fingerprint
            fingerprint = self._generate_text_fingerprint(text)
            
            # Metadata
            metadata = {
                'character_count': len(text),
                'word_count': len(text.split()),
                'sentence_count': len(sent_tokenize(text))
            }
            
            return TextFeatures(
                linguistic_features=linguistic_features,
                semantic_features=semantic_features,
                sentiment_features=sentiment_features,
                structural_features=structural_features,
                quality_metrics=quality_metrics,
                fingerprint=fingerprint,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Text feature extraction failed: {e}")
            raise
    
    def _extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features"""        features = {}
        
        # Tokenize
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        
        # Basic statistics
        features['word_count'] = len(words)
        features['sentence_count'] = len(sentences)
        features['character_count'] = len(text)
        features['avg_word_length'] = np.mean([len(word) for word in words]) if words else 0
        features['avg_sentence_length'] = np.mean([len(word_tokenize(sent)) for sent in sentences]) if sentences else 0
        
        # Vocabulary richness
        unique_words = set(words)
        features['vocabulary_size'] = len(unique_words)
        features['type_token_ratio'] = len(unique_words) / len(words) if words else 0
        
        # POS tagging
        if self.nlp:
            doc = self.nlp(text)
            pos_counts = Counter([token.pos_ for token in doc])
            features['pos_distribution'] = dict(pos_counts)
        
        # Readability metrics
        features.update(self._calculate_readability_metrics(text, words, sentences))
        
        return features
    
    def _extract_semantic_features(self, text: str, config: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Extract semantic features using embeddings"""        features = {}
        
        # BERT embeddings
        if config.get('extract_bert_embeddings', True):
            features['bert_embedding'] = self._get_bert_embedding(text)
        
        # RoBERTa embeddings
        if config.get('extract_roberta_embeddings', False):
            features['roberta_embedding'] = self._get_roberta_embedding(text)
        
        # TF-IDF features
        if config.get('extract_tfidf', True):
            features['tfidf_features'] = self._get_tfidf_features(text)
        
        return features
    
    def _extract_sentiment_features(self, text: str) -> Dict[str, float]:
        """Extract sentiment-related features"""        features = {}
        
        # TextBlob sentiment
        blob = TextBlob(text)
        features['polarity'] = blob.sentiment.polarity
        features['subjectivity'] = blob.sentiment.subjectivity
        
        # Advanced sentiment using transformers
        try:
            sentiment_results = self.sentiment_pipeline(text)
            for result in sentiment_results[0]:
                features[f"sentiment_{result['label'].lower()}"] = result['score']
        except Exception as e:
            logger.warning(f"Advanced sentiment analysis failed: {e}")
        
        # Emotion analysis
        try:
            emotion_results = self.emotion_pipeline(text)
            for result in emotion_results[0]:
                features[f"emotion_{result['label'].lower()}"] = result['score']
        except Exception as e:
            logger.warning(f"Emotion analysis failed: {e}")
        
        return features
    
    def _extract_structural_features(self, text: str) -> Dict[str, int]:
        """Extract structural features"""        features = {}
        
        # Count different types of punctuation
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['comma_count'] = text.count(',')
        features['period_count'] = text.count('.')
        features['semicolon_count'] = text.count(';')
        features['colon_count'] = text.count(':')
        
        # Count uppercase words
        words = text.split()
        features['uppercase_word_count'] = sum(1 for word in words if word.isupper())
        features['capitalized_word_count'] = sum(1 for word in words if word.istitle())
        
        # Count numbers
        features['number_count'] = len(re.findall(r'\d+', text))
        
        # Count special characters
        features['special_char_count'] = len(re.findall(r'[^a-zA-Z0-9\s]', text))
        
        return features
    
    def _extract_quality_metrics(self, text: str) -> Dict[str, float]:
        """Extract text quality metrics"""        metrics = {}
        
        # Grammar and spelling (simplified)
        blob = TextBlob(text)
        try:
            corrected = blob.correct()
            metrics['spelling_accuracy'] = 1.0 - (len(str(blob)) - len(str(corrected))) / len(str(blob))
        except:
            metrics['spelling_accuracy'] = 1.0
        
        # Coherence (based on sentence similarity)
        sentences = sent_tokenize(text)
        if len(sentences) > 1:
            metrics['coherence_score'] = self._calculate_coherence(sentences)
        else:
            metrics['coherence_score'] = 1.0
        
        # Completeness (based on sentence structure)
        metrics['completeness_score'] = self._calculate_completeness(text)
        
        # Clarity (based on readability)
        metrics['clarity_score'] = self._calculate_clarity(text)
        
        return metrics
    
    def _calculate_readability_metrics(self, text: str, words: List[str], sentences: List[str]) -> Dict[str, float]:
        """Calculate readability metrics"""        metrics = {}
        
        if not words or not sentences:
            return {'flesch_reading_ease': 0, 'flesch_kincaid_grade': 0}
        
        # Count syllables (approximation)
        def count_syllables(word):
            word = word.lower()
            vowels = 'aeiouy'
            syllable_count = 0
            previous_char_was_vowel = False
            
            for char in word:
                if char in vowels:
                    if not previous_char_was_vowel:
                        syllable_count += 1
                    previous_char_was_vowel = True
                else:
                    previous_char_was_vowel = False
            
            # Handle silent 'e'
            if word.endswith('e') and syllable_count > 1:
                syllable_count -= 1
            
            return max(1, syllable_count)
        
        total_syllables = sum(count_syllables(word) for word in words)
        total_words = len(words)
        total_sentences = len(sentences)
        
        # Flesch Reading Ease
        if total_sentences > 0 and total_words > 0:
            metrics['flesch_reading_ease'] = 206.835 - (1.015 * (total_words / total_sentences)) - (84.6 * (total_syllables / total_words))
            
            # Flesch-Kincaid Grade Level
            metrics['flesch_kincaid_grade'] = (0.39 * (total_words / total_sentences)) + (11.8 * (total_syllables / total_words)) - 15.59
        else:
            metrics['flesch_reading_ease'] = 0
            metrics['flesch_kincaid_grade'] = 0
        
        return metrics
    
    def _get_bert_embedding(self, text: str) -> np.ndarray:
        """Get BERT embedding for text"""        try:
            inputs = self.bert_tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                # Use CLS token embedding
                embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"BERT embedding failed: {e}")
            return np.zeros(768)  # Default BERT embedding size
    
    def _get_roberta_embedding(self, text: str) -> np.ndarray:
        """Get RoBERTa embedding for text"""        try:
            inputs = self.roberta_tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.roberta_model(**inputs)
                # Use CLS token embedding
                embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"RoBERTa embedding failed: {e}")
            return np.zeros(768)  # Default RoBERTa embedding size
    
    def _get_tfidf_features(self, text: str) -> np.ndarray:
        """Get TF-IDF features for text"""        try:
            # Fit and transform single text
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            return tfidf_matrix.toarray().flatten()
            
        except Exception as e:
            logger.error(f"TF-IDF feature extraction failed: {e}")
            return np.zeros(1000)  # Default size
    
    def _analyze_sentiment(self, text: str, config: Dict[str, Any]) -> SentimentResult:
        """Comprehensive sentiment analysis"""        try:
            # TextBlob sentiment
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Advanced sentiment
            emotion_scores = {}
            confidence = 0.5
            
            try:
                # Get emotion scores
                emotion_results = self.emotion_pipeline(text)
                for result in emotion_results[0]:
                    emotion_scores[result['label']] = result['score']
                
                # Get overall confidence
                confidence = max(result['score'] for result in emotion_results[0])
                
            except Exception as e:
                logger.warning(f"Advanced sentiment analysis failed: {e}")
            
            return SentimentResult(
                polarity=polarity,
                subjectivity=subjectivity,
                emotion_scores=emotion_scores,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return SentimentResult(polarity=0.0, subjectivity=0.0, emotion_scores={}, confidence=0.0)
    
    def _extract_named_entities(self, text: str, config: Dict[str, Any]) -> List[NamedEntity]:
        """Extract named entities"""        entities = []
        
        if not self.nlp or not config.get('extract_entities', True):
            return entities
        
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                entities.append(NamedEntity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=1.0  # spaCy doesn't provide confidence by default
                ))
            
        except Exception as e:
            logger.error(f"Named entity extraction failed: {e}")
        
        return entities
    
    def _generate_embeddings(self, text: str, config: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Generate various text embeddings"""        embeddings = {}
        
        if config.get('generate_bert_embedding', True):
            embeddings['bert'] = self._get_bert_embedding(text)
        
        if config.get('generate_roberta_embedding', False):
            embeddings['roberta'] = self._get_roberta_embedding(text)
        
        return embeddings
    
    def _analyze_text_quality(self, text: str) -> Dict[str, float]:
        """Analyze overall text quality"""        quality_metrics = {}
        
        # Readability
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        readability = self._calculate_readability_metrics(text, words, sentences)
        quality_metrics.update(readability)
        
        # Grammar quality (simplified)
        blob = TextBlob(text)
        try:
            corrected = str(blob.correct())
            grammar_score = 1.0 - (abs(len(text) - len(corrected)) / len(text))
            quality_metrics['grammar_quality'] = max(0.0, grammar_score)
        except:
            quality_metrics['grammar_quality'] = 0.8  # Default score
        
        # Coherence
        if len(sentences) > 1:
            quality_metrics['coherence'] = self._calculate_coherence(sentences)
        else:
            quality_metrics['coherence'] = 1.0
        
        # Completeness
        quality_metrics['completeness'] = self._calculate_completeness(text)
        
        # Overall quality score
        quality_metrics['overall_quality'] = np.mean([
            quality_metrics.get('grammar_quality', 0.5),
            quality_metrics.get('coherence', 0.5),
            quality_metrics.get('completeness', 0.5),
            min(quality_metrics.get('flesch_reading_ease', 50) / 100, 1.0)
        ])
        
        return quality_metrics
    
    def _calculate_coherence(self, sentences: List[str]) -> float:
        """Calculate text coherence based on sentence similarity"""        try:
            if len(sentences) < 2:
                return 1.0
            
            # Get embeddings for each sentence
            sentence_embeddings = []
            for sentence in sentences:
                embedding = self._get_bert_embedding(sentence)
                sentence_embeddings.append(embedding)
            
            # Calculate pairwise similarities
            similarities = []
            for i in range(len(sentence_embeddings) - 1):
                similarity = cosine_similarity(
                    [sentence_embeddings[i]], 
                    [sentence_embeddings[i + 1]]
                )[0][0]
                similarities.append(similarity)
            
            # Return average similarity
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Coherence calculation failed: {e}")
            return 0.5
    
    def _calculate_completeness(self, text: str) -> float:
        """Calculate text completeness based on structure"""        try:
            sentences = sent_tokenize(text)
            if not sentences:
                return 0.0
            
            # Check for complete sentences (end with punctuation)
            complete_sentences = sum(1 for sent in sentences if sent.strip().endswith(('.', '!', '?')))
            completeness_ratio = complete_sentences / len(sentences)
            
            # Check for reasonable sentence length
            avg_sentence_length = np.mean([len(word_tokenize(sent)) for sent in sentences])
            length_score = min(avg_sentence_length / 15, 1.0)  # Optimal around 15 words
            
            # Combined completeness score
            return (completeness_ratio * 0.7 + length_score * 0.3)
            
        except Exception as e:
            logger.error(f"Completeness calculation failed: {e}")
            return 0.5
    
    def _calculate_clarity(self, text: str) -> float:
        """Calculate text clarity score"""        try:
            words = word_tokenize(text)
            sentences = sent_tokenize(text)
            
            if not words or not sentences:
                return 0.0
            
            # Average word length (shorter words are clearer)
            avg_word_length = np.mean([len(word) for word in words])
            word_clarity = max(0, 1.0 - (avg_word_length - 5) / 10)  # Optimal around 5 chars
            
            # Average sentence length (shorter sentences are clearer)
            avg_sentence_length = np.mean([len(word_tokenize(sent)) for sent in sentences])
            sentence_clarity = max(0, 1.0 - (avg_sentence_length - 15) / 20)  # Optimal around 15 words
            
            # Vocabulary complexity (lower is clearer)
            unique_words = set(word.lower() for word in words if word.isalpha())
            common_words = unique_words.intersection(self.stop_words)
            complexity_ratio = len(common_words) / len(unique_words) if unique_words else 0
            vocabulary_clarity = complexity_ratio
            
            # Combined clarity score
            return (word_clarity * 0.3 + sentence_clarity * 0.4 + vocabulary_clarity * 0.3)
            
        except Exception as e:
            logger.error(f"Clarity calculation failed: {e}")
            return 0.5
    
    def _generate_text_fingerprint(self, text: str) -> str:
        """Generate text fingerprint for similarity matching"""        try:
            # Normalize text
            normalized_text = re.sub(r'\s+', ' ', text.lower().strip())
            
            # Create hash-based fingerprint
            text_hash = hashlib.md5(normalized_text.encode()).hexdigest()
            
            # Create content-based fingerprint
            words = word_tokenize(normalized_text)
            word_freq = Counter(words)
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            content_signature = ''.join([word for word, _ in top_words])
            content_hash = hashlib.md5(content_signature.encode()).hexdigest()
            
            # Combine hashes
            combined_fingerprint = f"{text_hash[:16]}{content_hash[:16]}"
            
            return combined_fingerprint
            
        except Exception as e:
            logger.error(f"Text fingerprint generation failed: {e}")
            return hashlib.md5(text.encode()).hexdigest()
    
    def _extract_topics(self, text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract topics from text using LDA"""        try:
            if not config.get('extract_topics', True):
                return {}
            
            # Prepare text for topic modeling
            sentences = sent_tokenize(text)
            if len(sentences) < 2:
                return {'topics': [], 'topic_distribution': []}
            
            # Vectorize text
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(sentences)
            
            # Fit LDA model
            lda = LatentDirichletAllocation(n_components=min(5, len(sentences)), random_state=42)
            topic_distribution = lda.fit_transform(tfidf_matrix)
            
            # Extract topics
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(lda.components_):
                top_words_idx = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]
                topics.append({
                    'topic_id': topic_idx,
                    'words': top_words,
                    'weights': topic[top_words_idx].tolist()
                })
            
            return {
                'topics': topics,
                'topic_distribution': topic_distribution.tolist(),
                'dominant_topic': int(np.argmax(np.mean(topic_distribution, axis=0)))
            }
            
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return {}
    
    def _suggest_enhancements(self, text: str, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Suggest text enhancements"""        suggestions = {
            'grammar': [],
            'style': [],
            'readability': [],
            'seo': []
        }
        
        try:
            if not config.get('suggest_enhancements', True):
                return suggestions
            
            words = word_tokenize(text)
            sentences = sent_tokenize(text)
            
            # Grammar suggestions
            blob = TextBlob(text)
            corrected = str(blob.correct())
            if corrected != text:
                suggestions['grammar'].append("Consider checking spelling and grammar")
            
            # Style suggestions
            if len(sentences) > 0:
                avg_sentence_length = np.mean([len(word_tokenize(sent)) for sent in sentences])
                if avg_sentence_length > 25:
                    suggestions['style'].append("Consider breaking up long sentences for better readability")
                elif avg_sentence_length < 8:
                    suggestions['style'].append("Consider combining short sentences for better flow")
            
            # Readability suggestions
            readability = self._calculate_readability_metrics(text, words, sentences)
            if readability.get('flesch_reading_ease', 50) < 30:
                suggestions['readability'].append("Text may be difficult to read - consider simplifying")
            
            # SEO suggestions
            if len(words) < 100:
                suggestions['seo'].append("Consider adding more content for better SEO")
            
            word_freq = Counter(word.lower() for word in words if word.isalpha())
            if len(word_freq) > 0:
                most_common = word_freq.most_common(1)[0]
                if most_common[1] / len(words) > 0.05:
                    suggestions['seo'].append(f"Word '{most_common[0]}' may be overused")
            
        except Exception as e:
            logger.error(f"Enhancement suggestion failed: {e}")
        
        return suggestions
    
    def _analyze_seo_factors(self, text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze SEO factors in text"""        seo_analysis = {}
        
        try:
            if not config.get('analyze_seo', True):
                return seo_analysis
            
            words = word_tokenize(text)
            sentences = sent_tokenize(text)
            
            # Content length
            seo_analysis['word_count'] = len(words)
            seo_analysis['character_count'] = len(text)
            
            # Keyword density
            word_freq = Counter(word.lower() for word in words if word.isalpha() and len(word) > 3)
            total_meaningful_words = sum(word_freq.values())
            
            keyword_density = {}
            for word, count in word_freq.most_common(10):
                density = (count / total_meaningful_words) * 100 if total_meaningful_words > 0 else 0
                keyword_density[word] = {
                    'count': count,
                    'density_percent': round(density, 2)
                }
            
            seo_analysis['keyword_density'] = keyword_density
            
            # Readability score
            readability = self._calculate_readability_metrics(text, words, sentences)
            seo_analysis['readability_score'] = readability.get('flesch_reading_ease', 0)
            
            # Content structure
            seo_analysis['sentence_count'] = len(sentences)
            seo_analysis['avg_sentence_length'] = np.mean([len(word_tokenize(sent)) for sent in sentences]) if sentences else 0
            
            # SEO recommendations
            recommendations = []
            
            if len(words) < 300:
                recommendations.append("Consider adding more content (minimum 300 words recommended)")
            
            if seo_analysis['readability_score'] < 60:
                recommendations.append("Consider improving readability for better SEO")
            
            # Check for keyword stuffing
            for word, data in keyword_density.items():
                if data['density_percent'] > 3:
                    recommendations.append(f"Keyword '{word}' may be overused ({data['density_percent']}%)")
            
            seo_analysis['recommendations'] = recommendations
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
        
        return seo_analysis
    
    def _extract_text_metadata(self, original_text: str, cleaned_text: str) -> Dict[str, Any]:
        """Extract text metadata"""        metadata = {}
        
        try:
            # Language detection
            try:
                detected_lang = langdetect.detect(original_text)
                metadata['detected_language'] = detected_lang
            except:
                metadata['detected_language'] = 'unknown'
            
            # Text statistics
            metadata['original_length'] = len(original_text)
            metadata['cleaned_length'] = len(cleaned_text)
            metadata['compression_ratio'] = len(cleaned_text) / len(original_text) if len(original_text) > 0 else 0
            
            # Content type estimation
            if re.search(r'[.!?]\s*$', original_text.strip()):
                metadata['content_type'] = 'complete_text'
            elif len(original_text.split()) < 20:
                metadata['content_type'] = 'short_text'
            else:
                metadata['content_type'] = 'long_text'
            
            # Complexity estimation
            words = word_tokenize(cleaned_text)
            avg_word_length = np.mean([len(word) for word in words]) if words else 0
            
            if avg_word_length < 4:
                metadata['complexity'] = 'simple'
            elif avg_word_length < 6:
                metadata['complexity'] = 'moderate'
            else:
                metadata['complexity'] = 'complex'
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
        
        return metadata
    
    def calculate_similarity(self, text1: str, text2: str, method: str = 'semantic') -> float:
        """Calculate similarity between two texts"""        try:
            if method == 'semantic':
                # Use BERT embeddings for semantic similarity
                embedding1 = self._get_bert_embedding(text1)
                embedding2 = self._get_bert_embedding(text2)
                
                # Calculate cosine similarity
                similarity = cosine_similarity([embedding1], [embedding2])[0][0]
                return float(similarity)
                
            elif method == 'lexical':
                # Use TF-IDF for lexical similarity
                vectorizer = TfidfVectorizer()
                tfidf_matrix = vectorizer.fit_transform([text1, text2])
                similarity = cosine_similarity(tfidf_matrix)[0][1]
                return float(similarity)
                
            elif method == 'fingerprint':
                # Use fingerprint comparison
                fingerprint1 = self._generate_text_fingerprint(text1)
                fingerprint2 = self._generate_text_fingerprint(text2)
                
                # Calculate character-level similarity
                common_chars = sum(1 for c1, c2 in zip(fingerprint1, fingerprint2) if c1 == c2)
                similarity = common_chars / max(len(fingerprint1), len(fingerprint2))
                return float(similarity)
            
            else:
                raise ValueError(f"Unknown similarity method: {method}")
                
        except Exception as e:
            logger.error(f"Text similarity calculation failed: {e}")
            return 0.0
    
    def generate_summary(self, text: str, max_length: int = 150) -> str:
        """Generate text summary"""        try:
            if len(text.split()) < 50:
                return text  # Too short to summarize
            
            # Use BART for summarization
            summary = self.summarization_pipeline(text, max_length=max_length, min_length=30)
            return summary[0]['summary_text']
            
        except Exception as e:
            logger.error(f"Text summarization failed: {e}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def detect_plagiarism(self, text: str, reference_texts: List[str], 
                         threshold: float = 0.8) -> Dict[str, Any]:
        """Detect potential plagiarism"""        try:
            plagiarism_results = {
                'is_plagiarized': False,
                'max_similarity': 0.0,
                'similar_texts': [],
                'similarity_scores': []
            }
            
            for i, ref_text in enumerate(reference_texts):
                similarity = self.calculate_similarity(text, ref_text, method='semantic')
                plagiarism_results['similarity_scores'].append(similarity)
                
                if similarity > threshold:
                    plagiarism_results['is_plagiarized'] = True
                    plagiarism_results['similar_texts'].append({
                        'index': i,
                        'similarity': similarity,
                        'text_preview': ref_text[:100] + "..." if len(ref_text) > 100 else ref_text
                    })
                
                if similarity > plagiarism_results['max_similarity']:
                    plagiarism_results['max_similarity'] = similarity
            
            return plagiarism_results
            
        except Exception as e:
            logger.error(f"Plagiarism detection failed: {e}")
            return {'is_plagiarized': False, 'max_similarity': 0.0}
    
    def enhance_text_for_seo(self, text: str, target_keywords: List[str] = None) -> str:
        """Enhance text for SEO optimization"""        try:
            enhanced_text = text
            
            if target_keywords:
                # Simple keyword optimization
                words = enhanced_text.split()
                total_words = len(words)
                
                for keyword in target_keywords:
                    keyword_count = enhanced_text.lower().count(keyword.lower())
                    target_density = 0.02  # 2% density
                    target_count = int(total_words * target_density)
                    
                    if keyword_count < target_count:
                        # Add keyword naturally (this is a simplified approach)
                        sentences = sent_tokenize(enhanced_text)
                        if sentences:
                            # Add keyword to first sentence if it doesn't exist
                            first_sentence = sentences[0]
                            if keyword.lower() not in first_sentence.lower():
                                sentences[0] = f"{first_sentence.rstrip('.')} related to {keyword}."
                                enhanced_text = ' '.join(sentences)
            
            return enhanced_text
            
        except Exception as e:
            logger.error(f"SEO enhancement failed: {e}")
            return text
