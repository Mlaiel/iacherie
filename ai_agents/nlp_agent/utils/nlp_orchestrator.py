"""NLP Orchestrator - Main Coordination Engine
===========================================

Central orchestration engine that coordinates all NLP processing tasks,
manages workflows, and provides unified interface for text processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import NLPAgentConfig, default_config, ProcessingMode
from .text_analyzer import TextAnalyzer, TextAnalysisResult
from .sentiment_engine import SentimentEngine, SentimentResult
from .language_detector import LanguageDetector, LanguageResult
from .content_classifier import ContentClassifier, ClassificationResult
from .semantic_processor import SemanticProcessor, SemanticResult
from .intent_recognizer import IntentRecognizer, IntentResult
from .entity_extractor import EntityExtractor, EntityResult
from .topic_modeler import TopicModeler, TopicResult
from .text_fingerprinter import TextFingerprinter, FingerprintResult
from .embeddings_engine import EmbeddingsEngine

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class ProcessingRequest:
    """Request object for text processing"""    text: Union[str, List[str]]
    request_id: Optional[str] = None
    language: Optional[str] = None
    processing_mode: ProcessingMode = ProcessingMode.BALANCED
    include_sentiment: bool = True
    include_language_detection: bool = True
    include_entities: bool = True
    include_topics: bool = False
    include_classification: bool = True
    include_intent: bool = False
    include_fingerprinting: bool = False
    include_embeddings: bool = False
    include_semantic: bool = False
    custom_options: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProcessingResult:
    """Comprehensive result from NLP processing"""    request_id: str
    text: str
    language: Optional[LanguageResult] = None
    sentiment: Optional[SentimentResult] = None
    entities: Optional[EntityResult] = None
    topics: Optional[TopicResult] = None
    classification: Optional[ClassificationResult] = None
    intent: Optional[IntentResult] = None
    fingerprint: Optional[FingerprintResult] = None
    embeddings: Optional[List[float]] = None
    semantic: Optional[SemanticResult] = None
    processing_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

class NLPOrchestrator:
    """    Main orchestration engine for coordinating NLP processing tasks.
    Manages workflows and provides unified interface for text processing.
    """    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """Initialize NLP Orchestrator"""        self.config = config or default_config
        self.components = {}
        self.executor = ThreadPoolExecutor(max_workers=self.config.performance.max_workers)
        self.processing_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_processing_time": 0.0,
            "total_processing_time": 0.0
        }
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all NLP components"""        try:
            # Core components
            self.components["text_analyzer"] = TextAnalyzer(self.config)
            self.components["embeddings_engine"] = EmbeddingsEngine(self.config)
            
            # Analysis components
            if self.config.enable_sentiment_analysis:
                self.components["sentiment_engine"] = SentimentEngine(self.config)
            
            if self.config.enable_language_detection:
                self.components["language_detector"] = LanguageDetector(self.config)
            
            if self.config.enable_entity_extraction:
                self.components["entity_extractor"] = EntityExtractor(self.config)
            
            # Advanced components
            self.components["content_classifier"] = ContentClassifier(self.config)
            self.components["semantic_processor"] = SemanticProcessor(self.config)
            self.components["intent_recognizer"] = IntentRecognizer(self.config)
            
            if self.config.enable_topic_modeling:
                self.components["topic_modeler"] = TopicModeler(self.config)
            
            if self.config.enable_text_fingerprinting:
                self.components["text_fingerprinter"] = TextFingerprinter(self.config)
            
            logger.info(f"Initialized {len(self.components)} NLP components")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP components: {e}")
            raise
    
    async def process_text(
        self,
        text: Union[str, List[str]],
        request_id: Optional[str] = None,
        **kwargs
    ) -> Union[ProcessingResult, List[ProcessingResult]]:
        """        Process text through the NLP pipeline
        
        Args:
            text: Text or list of texts to process
            request_id: Optional request identifier
            **kwargs: Additional processing options
        
        Returns:
            ProcessingResult or list of results
        """        start_time = time.time()
        
        # Handle single text vs batch
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        
        # Create processing request
        request = ProcessingRequest(
            text=text,
            request_id=request_id or self._generate_request_id(),
            **kwargs
        )
        
        try:
            # Process texts
            results = []
            for i, single_text in enumerate(texts):
                result = await self._process_single_text(
                    single_text,
                    f"{request.request_id}_{i}" if is_batch else request.request_id,
                    request
                )
                results.append(result)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_stats(len(texts), processing_time, success=True)
            
            # Return appropriate format
            return results if is_batch else results[0]
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(len(texts), processing_time, success=False)
            logger.error(f"Error processing text: {e}")
            raise
    
    async def _process_single_text(
        self,
        text: str,
        request_id: str,
        request: ProcessingRequest
    ) -> ProcessingResult:
        """Process a single text through the NLP pipeline"""        start_time = time.time()
        result = ProcessingResult(request_id=request_id, text=text)
        
        try:
            # Validate and preprocess text
            if not self._validate_text(text):
                result.errors.append("Invalid or empty text")
                return result
            
            # Prepare processing tasks based on request
            tasks = []
            
            # Language detection (usually first)
            if request.include_language_detection and "language_detector" in self.components:
                tasks.append(("language", self._detect_language(text)))
            
            # Basic text analysis
            tasks.append(("analysis", self._analyze_text(text)))
            
            # Sentiment analysis
            if request.include_sentiment and "sentiment_engine" in self.components:
                tasks.append(("sentiment", self._analyze_sentiment(text, request.language)))
            
            # Entity extraction
            if request.include_entities and "entity_extractor" in self.components:
                tasks.append(("entities", self._extract_entities(text, request.language)))
            
            # Content classification
            if request.include_classification:
                tasks.append(("classification", self._classify_content(text)))
            
            # Intent recognition
            if request.include_intent:
                tasks.append(("intent", self._recognize_intent(text)))
            
            # Embeddings generation
            if request.include_embeddings:
                tasks.append(("embeddings", self._generate_embeddings(text)))
            
            # Semantic processing
            if request.include_semantic:
                tasks.append(("semantic", self._process_semantics(text)))
            
            # Topic modeling
            if request.include_topics and "topic_modeler" in self.components:
                tasks.append(("topics", self._extract_topics([text])))
            
            # Text fingerprinting
            if request.include_fingerprinting and "text_fingerprinter" in self.components:
                tasks.append(("fingerprint", self._generate_fingerprint(text)))
            
            # Execute tasks concurrently
            task_results = await self._execute_tasks_concurrently(tasks)
            
            # Assign results
            for task_name, task_result in task_results.items():
                if task_result and not isinstance(task_result, Exception):
                    setattr(result, task_name, task_result)
                elif isinstance(task_result, Exception):
                    result.errors.append(f"Error in {task_name}: {str(task_result)}")
            
            # Calculate processing time
            result.processing_time = time.time() - start_time
            
            # Add metadata
            result.metadata = {
                "processing_mode": request.processing_mode.value,
                "components_used": list(task_results.keys()),
                "config_version": "2.0"
            }
            
            return result
            
        except Exception as e:
            result.errors.append(f"Processing error: {str(e)}")
            result.processing_time = time.time() - start_time
            logger.error(f"Error processing text {request_id}: {e}")
            return result
    
    async def _execute_tasks_concurrently(self, tasks: List[Tuple[str, Any]]) -> Dict[str, Any]:
        """Execute processing tasks concurrently"""        results = {}
        
        if self.config.performance.use_multiprocessing and len(tasks) > 1:
            # Use thread pool for concurrent execution
            futures = {}
            for task_name, task_coro in tasks:
                if asyncio.iscoroutine(task_coro):
                    futures[task_name] = task_coro
                else:
                    # Convert sync function to async
                    futures[task_name] = asyncio.create_task(
                        asyncio.get_event_loop().run_in_executor(None, lambda: task_coro)
                    )
            
            # Wait for all tasks to complete
            for task_name, future in futures.items():
                try:
                    results[task_name] = await future
                except Exception as e:
                    results[task_name] = e
                    logger.warning(f"Task {task_name} failed: {e}")
        else:
            # Sequential execution
            for task_name, task_func in tasks:
                try:
                    if asyncio.iscoroutine(task_func):
                        results[task_name] = await task_func
                    else:
                        results[task_name] = task_func
                except Exception as e:
                    results[task_name] = e
                    logger.warning(f"Task {task_name} failed: {e}")
        
        return results
    
    async def _detect_language(self, text: str) -> Optional[LanguageResult]:
        """Detect language of text"""        try:
            detector = self.components.get("language_detector")
            if detector:
                return await detector.detect_language(text)
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return None
    
    async def _analyze_text(self, text: str) -> Optional[TextAnalysisResult]:
        """Perform basic text analysis"""        try:
            analyzer = self.components.get("text_analyzer")
            if analyzer:
                return await analyzer.analyze(text)
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return None
    
    async def _analyze_sentiment(self, text: str, language: Optional[str] = None) -> Optional[SentimentResult]:
        """Analyze sentiment of text"""        try:
            sentiment_engine = self.components.get("sentiment_engine")
            if sentiment_engine:
                return await sentiment_engine.analyze_sentiment(text, language)
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return None
    
    async def _extract_entities(self, text: str, language: Optional[str] = None) -> Optional[EntityResult]:
        """Extract named entities from text"""        try:
            entity_extractor = self.components.get("entity_extractor")
            if entity_extractor:
                return await entity_extractor.extract_entities(text, language)
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return None
    
    async def _classify_content(self, text: str) -> Optional[ClassificationResult]:
        """Classify content categories"""        try:
            classifier = self.components.get("content_classifier")
            if classifier:
                return await classifier.classify(text)
        except Exception as e:
            logger.error(f"Content classification failed: {e}")
            return None
    
    async def _recognize_intent(self, text: str) -> Optional[IntentResult]:
        """Recognize user intent"""        try:
            intent_recognizer = self.components.get("intent_recognizer")
            if intent_recognizer:
                return await intent_recognizer.recognize_intent(text)
        except Exception as e:
            logger.error(f"Intent recognition failed: {e}")
            return None
    
    async def _generate_embeddings(self, text: str) -> Optional[List[float]]:
        """Generate text embeddings"""        try:
            embeddings_engine = self.components.get("embeddings_engine")
            if embeddings_engine:
                return await embeddings_engine.generate_embeddings(text)
        except Exception as e:
            logger.error(f"Embeddings generation failed: {e}")
            return None
    
    async def _process_semantics(self, text: str) -> Optional[SemanticResult]:
        """Process semantic information"""        try:
            semantic_processor = self.components.get("semantic_processor")
            if semantic_processor:
                return await semantic_processor.process(text)
        except Exception as e:
            logger.error(f"Semantic processing failed: {e}")
            return None
    
    async def _extract_topics(self, texts: List[str]) -> Optional[TopicResult]:
        """Extract topics from texts"""        try:
            topic_modeler = self.components.get("topic_modeler")
            if topic_modeler:
                return await topic_modeler.extract_topics(texts)
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return None
    
    async def _generate_fingerprint(self, text: str) -> Optional[FingerprintResult]:
        """Generate text fingerprint"""        try:
            fingerprinter = self.components.get("text_fingerprinter")
            if fingerprinter:
                return await fingerprinter.generate_fingerprint(text)
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {e}")
            return None
    
    def _validate_text(self, text: str) -> bool:
        """Validate input text"""        if not text or not isinstance(text, str):
            return False
        
        text_length = len(text.strip())
        if text_length < self.config.processing.min_text_length:
            return False
        
        if text_length > self.config.processing.max_text_length:
            return False
        
        return True
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""        import uuid
        return f"nlp_{uuid.uuid4().hex[:8]}"
    
    def _update_stats(self, num_texts: int, processing_time: float, success: bool):
        """Update processing statistics"""        self.processing_stats["total_requests"] += num_texts
        self.processing_stats["total_processing_time"] += processing_time
        
        if success:
            self.processing_stats["successful_requests"] += num_texts
        else:
            self.processing_stats["failed_requests"] += num_texts
        
        # Update average processing time
        total_requests = self.processing_stats["total_requests"]
        if total_requests > 0:
            self.processing_stats["average_processing_time"] = (
                self.processing_stats["total_processing_time"] / total_requests
            )
    
    async def batch_process(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        **kwargs
    ) -> List[ProcessingResult]:
        """        Process multiple texts in optimized batches
        
        Args:
            texts: List of texts to process
            batch_size: Optional batch size override
            **kwargs: Additional processing options
        
        Returns:
            List of processing results
        """        if not texts:
            return []
        
        batch_size = batch_size or self.config.processing.batch_size
        results = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = await self.process_text(batch, **kwargs)
            results.extend(batch_results)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""        return {
            **self.processing_stats,
            "components_loaded": len(self.components),
            "config_mode": self.config.processing.mode.value,
            "uptime": time.time() - getattr(self, "_start_time", time.time())
        }
    
    def get_component_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about loaded components"""        component_info = {}
        
        for name, component in self.components.items():
            component_info[name] = {
                "type": type(component).__name__,
                "initialized": True,
                "health_status": getattr(component, "health_status", "unknown")
            }
        
        return component_info
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "orchestrator": {
                "status": "healthy",
                "statistics": self.get_statistics(),
                "components": self.get_component_info()
            },
            "issues": []
        }
        
        # Check component health
        for name, component in self.components.items():
            if hasattr(component, 'health_check'):
                try:
                    component_health = component.health_check()
                    if component_health.get("status") != "healthy":
                        health["status"] = "degraded"
                        health["issues"].append(f"Component {name} unhealthy")
                except Exception as e:
                    health["status"] = "unhealthy"
                    health["issues"].append(f"Component {name} health check failed: {e}")
        
        return health
    
    def shutdown(self):
        """Shutdown the orchestrator and all components"""        logger.info("Shutting down NLP Orchestrator")
        
        # Shutdown components
        for name, component in self.components.items():
            try:
                if hasattr(component, 'shutdown'):
                    component.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down component {name}: {e}")
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("NLP Orchestrator shutdown complete")

# Async context manager support
class AsyncNLPOrchestrator:
    """Async context manager wrapper for NLP Orchestrator"""    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        self.config = config
        self.orchestrator = None
    
    async def __aenter__(self):
        self.orchestrator = NLPOrchestrator(self.config)
        return self.orchestrator
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.orchestrator:
            self.orchestrator.shutdown()
