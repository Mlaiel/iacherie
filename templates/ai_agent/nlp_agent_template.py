"""{{agent_name}} Natural Language Processing Agent for Ainflue Platform
import asyncio

{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field, validator
import spacy
from transformers import AutoTokenizer, AutoModel, pipeline
import torch
from textblob import TextBlob

from ai.base_agent import BaseAIAgent
from ai.models import NLPModelManager
from core.config import get_settings
from utils.exceptions import NLPException
from monitoring.nlp_metrics import NLPMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class NLPTaskType(Enum):
    """NLP task types"""
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TEXT_CLASSIFICATION = "text_classification"
    NAMED_ENTITY_RECOGNITION = "named_entity_recognition"
    TEXT_SUMMARIZATION = "text_summarization"
    LANGUAGE_DETECTION = "language_detection"
    KEYWORD_EXTRACTION = "keyword_extraction"
    TEXT_GENERATION = "text_generation"
    QUESTION_ANSWERING = "question_answering"
    TRANSLATION = "translation"
    SIMILARITY_SEARCH = "similarity_search"


class NLPModel(Enum):
    """Available NLP models"""
    BERT = "bert-base-uncased"
    ROBERTA = "roberta-base"
    DISTILBERT = "distilbert-base-uncased"
    GPT2 = "gpt2"
    T5 = "t5-small"
    XLNET = "xlnet-base-cased"
    SPACY_EN = "en_core_web_sm"
    SPACY_MULTI = "xx_ent_wiki_sm"


class NLPTask(BaseModel):
    """NLP processing task"""
    id: str = Field(..., description="Unique task identifier")
    text: Union[str, List[str]] = Field(..., description="Text or list of texts to process")
    task_type: NLPTaskType = Field(..., description="Type of NLP task")
    model: Optional[NLPModel] = Field(default=None, description="Specific model to use")
    language: Optional[str] = Field(default="en", description="Text language")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Task-specific parameters")
    batch_size: Optional[int] = Field(default=32, description="Batch size for processing")
    max_length: Optional[int] = Field(default=512, description="Maximum text length")
    priority: int = Field(default=1, description="Task priority (1-10)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('text')
    def validate_text(cls, v) -> None:
        if isinstance(v, str) and not v.strip():
            raise ValueError('Text cannot be empty')
        if isinstance(v, list) and not v:
            raise ValueError('Text list cannot be empty')
        return v


class NLPResult(BaseModel):
    """NLP processing result"""
    task_id: str = Field(..., description="Task identifier")
    success: bool = Field(..., description="Whether the task succeeded")
    results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Processing results")
    confidence_scores: Optional[List[float]] = Field(default=None, description="Confidence scores")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    model_used: Optional[str] = Field(default=None, description="Model used for processing")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class {{agent_name}}NLPAgent(BaseAIAgent):
    """{{agent_description}}
    
    This NLP agent provides comprehensive natural language processing capabilities including:
    - Sentiment analysis and emotion detection
    - Text classification and categorization
    - Named entity recognition and extraction
    - Text summarization and generation
    - Language detection and translation
    - Keyword and key phrase extraction
    - Question answering systems
    - Text similarity and semantic search
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.model_manager = NLPModelManager()
        self.metrics_collector = NLPMetricsCollector()
        self.loaded_models: Dict[str, Any] = {}
        self.pipelines: Dict[str, Any] = {}
        self.spacy_models: Dict[str, Any] = {}
        
        # Initialize default models
        self._initialize_default_models()
    
    def _initialize_default_models(self) -> None:
        """Initialize default NLP models"""
        try:
            # Load spaCy model for basic NLP tasks
            if not spacy.util.is_package("en_core_web_sm"):
                logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            else:
                self.spacy_models["en"] = spacy.load("en_core_web_sm")
            
        except Exception as e:
            logger.warning(f"Failed to initialize default models: {str(e)}")
    
    async def process(self, task: NLPTask) -> NLPResult:
        """Process NLP task"""
        try:
            logger.info(f"Starting NLP task: {task.id} - {task.task_type.value}")
            start_time = datetime.utcnow()
            
            # Route to specific handler based on task type
            if task.task_type == NLPTaskType.SENTIMENT_ANALYSIS:
                results = await self._analyze_sentiment(task)
            elif task.task_type == NLPTaskType.TEXT_CLASSIFICATION:
                results = await self._classify_text(task)
            elif task.task_type == NLPTaskType.NAMED_ENTITY_RECOGNITION:
                results = await self._extract_entities(task)
            elif task.task_type == NLPTaskType.TEXT_SUMMARIZATION:
                results = await self._summarize_text(task)
            elif task.task_type == NLPTaskType.LANGUAGE_DETECTION:
                results = await self._detect_language(task)
            elif task.task_type == NLPTaskType.KEYWORD_EXTRACTION:
                results = await self._extract_keywords(task)
            elif task.task_type == NLPTaskType.TEXT_GENERATION:
                results = await self._generate_text(task)
            elif task.task_type == NLPTaskType.QUESTION_ANSWERING:
                results = await self._answer_questions(task)
            elif task.task_type == NLPTaskType.TRANSLATION:
                results = await self._translate_text(task)
            elif task.task_type == NLPTaskType.SIMILARITY_SEARCH:
                results = await self._compute_similarity(task)
            else:
                raise NLPException(f"Unsupported task type: {task.task_type}")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Collect metrics
            await self.metrics_collector.record_processing_metrics(
                task_type=task.task_type.value,
                num_texts=len(task.text) if isinstance(task.text, list) else 1,
                execution_time=execution_time,
                success=True
            )
            
            return NLPResult(
                task_id=task.id,
                success=True,
                results=results["results"],
                confidence_scores=results.get("confidence_scores"),
                metadata=results.get("metadata"),
                execution_time=execution_time,
                model_used=results.get("model_used")
            )
            
        except Exception as e:
            logger.error(f"NLP processing failed for task {task.id}: {str(e)}")
            await self.metrics_collector.record_processing_metrics(
                task_type=task.task_type.value,
                num_texts=len(task.text) if isinstance(task.text, list) else 1,
                execution_time=0,
                success=False
            )
            return NLPResult(
                task_id=task.id,
                success=False,
                error_message=str(e)
            )
    
    async def _analyze_sentiment(self, task: NLPTask) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        texts = [task.text] if isinstance(task.text, str) else task.text
        
        # Use Transformers pipeline for sentiment analysis
        if "sentiment" not in self.pipelines:
            self.pipelines["sentiment"] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
        
        sentiment_pipeline = self.pipelines["sentiment"]
        
        results = []
        confidence_scores = []
        
        for text in texts:
            # Truncate text if too long
            if len(text) > task.max_length:
                text = text[:task.max_length]
            
            result = sentiment_pipeline(text)
            
            # Also use TextBlob for additional sentiment metrics
            blob = TextBlob(text)
            
            sentiment_result = {
                "text": text,
                "label": result[0]["label"],
                "score": result[0]["score"],
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity,
                "emotion": self._detect_emotion(text)
            }
            
            results.append(sentiment_result)
            confidence_scores.append(result[0]["score"])
        
        return {
            "results": results,
            "confidence_scores": confidence_scores,
            "model_used": "cardiffnlp/twitter-roberta-base-sentiment-latest"
        }
    
    async def _classify_text(self, task: NLPTask) -> Dict[str, Any]:
        """Classify text into categories"""
        texts = [task.text] if isinstance(task.text, str) else task.text
        
        # Use zero-shot classification for flexibility
        if "classification" not in self.pipelines:
            self.pipelines["classification"] = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
        
        classifier = self.pipelines["classification"]
        
        # Get candidate labels from parameters
        candidate_labels = task.parameters.get("labels", [
            "technology", "business", "entertainment", "sports", "politics", 
            "health", "science", "education", "travel", "food"
        ])
        
        results = []
        confidence_scores = []
        
        for text in texts:
            if len(text) > task.max_length:
                text = text[:task.max_length]
            
            result = classifier(text, candidate_labels)
            
            classification_result = {
                "text": text,
                "predictions": [
                    {"label": label, "score": score}
                    for label, score in zip(result["labels"], result["scores"])
                ],
                "top_label": result["labels"][0],
                "top_score": result["scores"][0]
            }
            
            results.append(classification_result)
            confidence_scores.append(result["scores"][0])
        
        return {
            "results": results,
            "confidence_scores": confidence_scores,
            "model_used": "facebook/bart-large-mnli"
        }
    
    async def _extract_entities(self, task: NLPTask) -> Dict[str, Any]:
        """Extract named entities from text"""
        texts = [task.text] if isinstance(task.text, str) else task.text
        
        # Use spaCy for NER
        if task.language not in self.spacy_models:
            if task.language == "en" and "en" not in self.spacy_models:
                self.spacy_models["en"] = spacy.load("en_core_web_sm")
            else:
                # Fallback to English model
                self.spacy_models[task.language] = self.spacy_models.get("en")
        
        nlp = self.spacy_models.get(task.language)
        if not nlp:
            raise NLPException(f"No NLP model available for language: {task.language}")
        
        results = []
        confidence_scores = []
        
        for text in texts:
            doc = nlp(text)
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "description": spacy.explain(ent.label_)
                })
            
            # Extract additional information
            tokens = []
            for token in doc:
                if not token.is_space:
                    tokens.append({
                        "text": token.text,
                        "lemma": token.lemma_,
                        "pos": token.pos_,
                        "is_alpha": token.is_alpha,
                        "is_stop": token.is_stop
                    })
            
            entity_result = {
                "text": text,
                "entities": entities,
                "tokens": tokens,
                "sentences": [sent.text for sent in doc.sents]
            }
            
            results.append(entity_result)
            confidence_scores.append(1.0)  # spaCy doesn't provide confidence scores
        
        return {
            "results": results,
            "confidence_scores": confidence_scores,
            "model_used": f"spacy-{task.language}"
        }
    
    async def _summarize_text(self, task: NLPTask) -> Dict[str, Any]:
        """Summarize text"""
        texts = [task.text] if isinstance(task.text, str) else task.text
        
        # Use T5 for summarization
        if "summarization" not in self.pipelines:
            self.pipelines["summarization"] = pipeline(
                "summarization",
                model="t5-small",
                tokenizer="t5-small"
            )
        
        summarizer = self.pipelines["summarization"]
        
        results = []
        confidence_scores = []
        
        for text in texts:
            # T5 requires specific format
            input_text = f"summarize: {text}"
            
            # Adjust max_length based on input length
            max_length = min(task.parameters.get("max_length", 150), len(text.split()) // 2)
            min_length = task.parameters.get("min_length", 30)
            
            try:
                summary = summarizer(
                    input_text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                
                summary_result = {
                    "text": text,
                    "summary": summary[0]["summary_text"],
                    "compression_ratio": len(summary[0]["summary_text"]) / len(text),
                    "original_length": len(text),
                    "summary_length": len(summary[0]["summary_text"])
                }
                
                results.append(summary_result)
                confidence_scores.append(0.8)  # Default confidence for summarization
                
            except Exception as e:
                logger.warning(f"Summarization failed for text: {str(e)}")
                summary_result = {
                    "text": text,
                    "summary": text[:max_length] + "...",
                    "error": str(e)
                }
                results.append(summary_result)
                confidence_scores.append(0.3)
        
        return {
            "results": results,
            "confidence_scores": confidence_scores,
            "model_used": "t5-small"
        }
    
    async def _detect_language(self, task: NLPTask) -> Dict[str, Any]:
        """Detect language of text"""
        from langdetect import detect, detect_langs
        
        texts = [task.text] if isinstance(task.text, str) else task.text
        
        results = []
        confidence_scores = []
        
        for text in texts:
            try:
                # Primary language detection
                primary_lang = detect(text)
                
                # Get all language probabilities
                lang_probs = detect_langs(text)
                
                language_result = {
                    "text": text,
                    "detected_language": primary_lang,
                    "language_probabilities": [
                        {"language": str(lang).split(":")[0], "probability": float(str(lang).split(":")[1])}
                        for lang in lang_probs
                    ],
                    "confidence": float(str(lang_probs[0]).split(":")[1])
                }
                
                results.append(language_result)
                confidence_scores.append(language_result["confidence"])
                
            except Exception as e:
                logger.warning(f"Language detection failed for text: {str(e)}")
                results.append({
                    "text": text,
                    "detected_language": "unknown",
                    "error": str(e)
                })
                confidence_scores.append(0.0)
        
        return {
            "results": results,
            "confidence_scores": confidence_scores,
            "model_used": "langdetect"
        }
    
    async def _extract_keywords(self, task: NLPTask) -> Dict[str, Any]:
        """Extract keywords and key phrases from text"""
        from collections import Counter
        import re
        
        texts = [task.text] if isinstance(task.text, str) else task.text
        
        # Use spaCy for keyword extraction
        nlp = self.spacy_models.get(task.language, self.spacy_models.get("en"))
        if not nlp:
            raise NLPException(f"No NLP model available for language: {task.language}")
        
        results = []
        confidence_scores = []
        
        for text in texts:
            doc = nlp(text)
            
            # Extract meaningful tokens (excluding stop words, punctuation)
            keywords = []
            for token in doc:
                if (token.is_alpha and not token.is_stop and 
                    len(token.text) > 2 and token.pos_ in ["NOUN", "ADJ", "VERB"]):
                    keywords.append(token.lemma_.lower())
            
            # Count frequency
            keyword_freq = Counter(keywords)
            top_keywords = keyword_freq.most_common(task.parameters.get("top_k", 10))
            
            # Extract named entities as important phrases
            entities = [ent.text for ent in doc.ents]
            
            # Extract noun phrases
            noun_phrases = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1]
            
            keyword_result = {
                "text": text,
                "keywords": [{"word": word, "frequency": freq} for word, freq in top_keywords],
                "entities": entities,
                "noun_phrases": noun_phrases[:10],  # Top 10 noun phrases
                "total_tokens": len([token for token in doc if token.is_alpha]),
                "unique_keywords": len(keyword_freq)
            }
            
            results.append(keyword_result)
            confidence_scores.append(0.9)  # High confidence for keyword extraction
        
        return {
            "results": results,
            "confidence_scores": confidence_scores,
            "model_used": f"spacy-{task.language}"
        }
    
    async def _generate_text(self, task: NLPTask) -> Dict[str, Any]:
        """Generate text based on prompts"""
        prompts = [task.text] if isinstance(task.text, str) else task.text
        
        # Use GPT-2 for text generation
        if "generation" not in self.pipelines:
            self.pipelines["generation"] = pipeline(
                "text-generation",
                model="gpt2",
                tokenizer="gpt2"
            )
        
        generator = self.pipelines["generation"]
        
        results = []
        confidence_scores = []
        
        for prompt in prompts:
            try:
                generated = generator(
                    prompt,
                    max_length=task.parameters.get("max_length", 100),
                    num_return_sequences=task.parameters.get("num_sequences", 1),
                    temperature=task.parameters.get("temperature", 0.7),
                    do_sample=True,
                    pad_token_id=generator.tokenizer.eos_token_id
                )
                
                generation_result = {
                    "prompt": prompt,
                    "generated_texts": [item["generated_text"] for item in generated],
                    "parameters": {
                        "max_length": task.parameters.get("max_length", 100),
                        "temperature": task.parameters.get("temperature", 0.7),
                        "num_sequences": task.parameters.get("num_sequences", 1)
                    }
                }
                
                results.append(generation_result)
                confidence_scores.append(0.7)  # Moderate confidence for generation
                
            except Exception as e:
                logger.warning(f"Text generation failed for prompt: {str(e)}")
                results.append({
                    "prompt": prompt,
                    "error": str(e)
                })
                confidence_scores.append(0.0)
        
        return {
            "results": results,
            "confidence_scores": confidence_scores,
            "model_used": "gpt2"
        }
    
    async def _answer_questions(self, task: NLPTask) -> Dict[str, Any]:
        """Answer questions based on context"""
        # Expecting format: {"question": "...", "context": "..."}
        if not isinstance(task.parameters, dict) or "context" not in task.parameters:
            raise NLPException("Question answering requires 'context' in parameters")
        
        context = task.parameters["context"]
        questions = [task.text] if isinstance(task.text, str) else task.text
        
        # Use BERT for question answering
        if "qa" not in self.pipelines:
            self.pipelines["qa"] = pipeline(
                "question-answering",
                model="distilbert-base-cased-distilled-squad",
                tokenizer="distilbert-base-cased-distilled-squad"
            )
        
        qa_pipeline = self.pipelines["qa"]
        
        results = []
        confidence_scores = []
        
        for question in questions:
            try:
                answer = qa_pipeline(question=question, context=context)
                
                qa_result = {
                    "question": question,
                    "context": context,
                    "answer": answer["answer"],
                    "confidence": answer["score"],
                    "start": answer["start"],
                    "end": answer["end"]
                }
                
                results.append(qa_result)
                confidence_scores.append(answer["score"])
                
            except Exception as e:
                logger.warning(f"Question answering failed: {str(e)}")
                results.append({
                    "question": question,
                    "context": context,
                    "error": str(e)
                })
                confidence_scores.append(0.0)
        
        return {
            "results": results,
            "confidence_scores": confidence_scores,
            "model_used": "distilbert-base-cased-distilled-squad"
        }
    
    async def _translate_text(self, task: NLPTask) -> Dict[str, Any]:
        """Translate text between languages"""
        texts = [task.text] if isinstance(task.text, str) else task.text
        
        target_language = task.parameters.get("target_language", "en")
        source_language = task.language or "auto"
        
        # Use transformers for translation
        model_name = f"Helsinki-NLP/opus-mt-{source_language}-{target_language}"
        
        if "translation" not in self.pipelines:
            try:
                self.pipelines["translation"] = pipeline(
                    "translation",
                    model=model_name
                )
            except Exception:
                # Fallback to a general translation model
                self.pipelines["translation"] = pipeline(
                    "translation_en_to_fr"  # Example fallback
                )
        
        translator = self.pipelines["translation"]
        
        results = []
        confidence_scores = []
        
        for text in texts:
            try:
                translation = translator(text)
                
                translation_result = {
                    "original_text": text,
                    "translated_text": translation[0]["translation_text"],
                    "source_language": source_language,
                    "target_language": target_language,
                    "confidence": translation[0].get("score", 0.8)
                }
                
                results.append(translation_result)
                confidence_scores.append(translation[0].get("score", 0.8))
                
            except Exception as e:
                logger.warning(f"Translation failed: {str(e)}")
                results.append({
                    "original_text": text,
                    "error": str(e)
                })
                confidence_scores.append(0.0)
        
        return {
            "results": results,
            "confidence_scores": confidence_scores,
            "model_used": model_name
        }
    
    async def _compute_similarity(self, task: NLPTask) -> Dict[str, Any]:
        """Compute text similarity"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        if not isinstance(task.text, list) or len(task.text) < 2:
            raise NLPException("Similarity computation requires at least 2 texts")
        
        texts = task.text
        
        # Use TF-IDF + cosine similarity for basic similarity
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            results = []
            
            # Pairwise similarities
            for i in range(len(texts)):
                for j in range(i + 1, len(texts)):
                    similarity_result = {
                        "text1": texts[i],
                        "text2": texts[j],
                        "similarity_score": float(similarity_matrix[i][j]),
                        "pair_index": [i, j]
                    }
                    results.append(similarity_result)
            
            # Overall statistics
            metadata = {
                "num_texts": len(texts),
                "avg_similarity": float(np.mean(similarity_matrix[np.triu_indices(len(texts), k=1)])),
                "max_similarity": float(np.max(similarity_matrix[np.triu_indices(len(texts), k=1)])),
                "min_similarity": float(np.min(similarity_matrix[np.triu_indices(len(texts), k=1)]))
            }
            
            return {
                "results": results,
                "confidence_scores": [1.0] * len(results),
                "metadata": metadata,
                "model_used": "tfidf-cosine"
            }
            
        except Exception as e:
            logger.error(f"Similarity computation failed: {str(e)}")
            raise NLPException(f"Similarity computation failed: {str(e)}")
    
    def _detect_emotion(self, text: str) -> Dict[str, float]:
        """Detect emotions in text using rule-based approach"""
        emotion_keywords = {
            "joy": ["happy", "joy", "excited", "delighted", "cheerful", "elated"],
            "anger": ["angry", "furious", "mad", "irritated", "annoyed", "rage"],
            "sadness": ["sad", "depressed", "down", "unhappy", "melancholy", "sorrow"],
            "fear": ["afraid", "scared", "terrified", "anxious", "worried", "fearful"],
            "surprise": ["surprised", "amazed", "astonished", "shocked", "stunned"],
            "disgust": ["disgusted", "revolted", "repulsed", "sickened", "nauseated"]
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = score / len(keywords)
        
        return emotion_scores
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "loaded_models": list(self.loaded_models.keys()),
            "available_pipelines": list(self.pipelines.keys()),
            "spacy_models": list(self.spacy_models.keys()),
            "supported_tasks": [task.value for task in NLPTaskType],
            "supported_models": [model.value for model in NLPModel]
        }
    
    async def clear_cache(self) -> None:
        """Clear model cache to free memory"""
        self.loaded_models.clear()
        self.pipelines.clear()
        # Keep spaCy models as they're lighter
        logger.info("Model cache cleared")

# File has syntax issues - needs manual review