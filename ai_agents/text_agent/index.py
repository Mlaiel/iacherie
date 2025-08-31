"""Text Agent Index - Main Entry Point for Text Processing System

Central index file providing unified access to all text processing components
and their advanced enterprise-grade capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone

from .text_agent import TextAgent, TextAgentManager, TextProcessingType
from .text_processor import TextProcessor, TextAnalyzer, ProcessingOptions
from .text_generator import AITextGenerator, ContentSynthesizer, GenerationConfig
from .nlp_engine import NLPEngine, SentimentAnalyzer, AnalysisType
from .language_detector import LanguageDetector, TranslationEngine

logger = logging.getLogger(__name__)

class TextAgentSystem:
    """    Unified Text Processing System providing enterprise-grade text analysis,
    generation, and processing capabilities for content creators.
    """    
    def __init__(self, num_agents: int = 3):
        """        Initialize the complete text processing system
        
        Args:
            num_agents: Number of text agent instances for load balancing
        """        self.agent_manager = TextAgentManager(num_agents)
        self.text_processor = TextProcessor()
        self.text_analyzer = TextAnalyzer()
        self.ai_generator = AITextGenerator()
        self.content_synthesizer = ContentSynthesizer()
        self.nlp_engine = NLPEngine()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.language_detector = LanguageDetector()
        self.translation_engine = TranslationEngine()
        
        # System statistics
        self.system_stats = {
            "total_requests": 0,
            "successful_operations": 0,
            "system_uptime": datetime.now(timezone.utc),
            "component_health": {}
        }
        
        logger.info("TextAgentSystem initialized with all components")
    
    async def analyze_text(
        self,
        text: str,
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Comprehensive text analysis using all available engines
        
        Args:
            text: Text to analyze
            analysis_options: Optional analysis configuration
            
        Returns:
            Dict containing comprehensive analysis results
        """        try:
            self.system_stats["total_requests"] += 1
            
            # Get available agent
            agent = self.agent_manager.get_next_agent()
            
            # Perform comprehensive analysis
            analysis_result = await agent.process_text(text, TextProcessingType.ANALYSIS)
            
            # Additional NLP analysis
            sentiment_result = await self.nlp_engine.analyze_sentiment(text)
            entities = await self.nlp_engine.extract_entities(text)
            
            # Language detection
            language_result = await self.language_detector.detect_language(text)
            
            # Combine results
            comprehensive_result = {
                "text_analysis": {
                    "text_id": analysis_result.text_id,
                    "language": analysis_result.language,
                    "word_count": analysis_result.word_count,
                    "quality_score": analysis_result.quality_score,
                    "readability_score": analysis_result.readability_score,
                    "fingerprint": analysis_result.fingerprint
                },
                "sentiment_analysis": {
                    "polarity": sentiment_result.polarity,
                    "subjectivity": sentiment_result.subjectivity,
                    "label": sentiment_result.label.value,
                    "emotions": sentiment_result.emotions
                },
                "language_detection": {
                    "detected_language": language_result.language,
                    "language_name": language_result.language_name,
                    "confidence": language_result.confidence
                },
                "entities": [
                    {
                        "text": entity.text,
                        "label": entity.label,
                        "confidence": entity.confidence
                    } for entity in entities
                ],
                "metadata": {
                    "processing_time": analysis_result.processing_time,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
            self.system_stats["successful_operations"] += 1
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return {"error": str(e)}
    
    async def generate_content(
        self,
        prompt: str,
        generation_config: Optional[GenerationConfig] = None
    ) -> Dict[str, Any]:
        """        Generate AI-powered content with quality assessment
        
        Args:
            prompt: Generation prompt
            generation_config: Optional generation configuration
            
        Returns:
            Dict containing generated content and metadata
        """        try:
            self.system_stats["total_requests"] += 1
            
            # Generate content
            generation_result = await self.ai_generator.generate_content(prompt, generation_config)
            
            # Analyze generated content
            analysis_result = await self.analyze_text(generation_result.generated_text)
            
            result = {
                "generation": {
                    "generation_id": generation_result.generation_id,
                    "prompt": generation_result.prompt,
                    "generated_text": generation_result.generated_text,
                    "quality_score": generation_result.quality_score,
                    "creativity_score": generation_result.creativity_score,
                    "relevance_score": generation_result.relevance_score,
                    "model_used": generation_result.model_used
                },
                "content_analysis": analysis_result,
                "metadata": {
                    "generation_time": generation_result.generation_time,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
            self.system_stats["successful_operations"] += 1
            return result
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {"error": str(e)}
    
    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Translate text with quality assessment and analysis
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            
        Returns:
            Dict containing translation results and analysis
        """        try:
            self.system_stats["total_requests"] += 1
            
            # Perform translation
            translation_result = await self.translation_engine.translate_text(
                text, target_language, source_language
            )
            
            # Analyze both source and translated text
            source_analysis = await self.analyze_text(text)
            translated_analysis = await self.analyze_text(translation_result.translated_text)
            
            result = {
                "translation": {
                    "source_text": translation_result.source_text,
                    "translated_text": translation_result.translated_text,
                    "source_language": translation_result.source_language,
                    "target_language": translation_result.target_language,
                    "translation_confidence": translation_result.translation_confidence,
                    "quality_assessment": translation_result.quality_assessment.value,
                    "translator_used": translation_result.translator_used
                },
                "source_analysis": source_analysis,
                "translated_analysis": translated_analysis,
                "metadata": {
                    "processing_time": translation_result.processing_time,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
            self.system_stats["successful_operations"] += 1
            return result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {"error": str(e)}
    
    async def detect_plagiarism(
        self,
        text: str,
        reference_texts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """        Detect plagiarism with comprehensive analysis
        
        Args:
            text: Text to check for plagiarism
            reference_texts: Optional reference texts to compare against
            
        Returns:
            Dict containing plagiarism detection results
        """        try:
            self.system_stats["total_requests"] += 1
            
            # Get available agent for plagiarism detection
            agent = self.agent_manager.get_next_agent()
            
            # Perform plagiarism detection
            plagiarism_result = await agent.detect_plagiarism(text, reference_texts)
            
            # Additional text analysis
            analysis_result = await self.analyze_text(text)
            
            result = {
                "plagiarism_detection": plagiarism_result,
                "text_analysis": analysis_result,
                "metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
            self.system_stats["successful_operations"] += 1
            return result
            
        except Exception as e:
            logger.error(f"Plagiarism detection failed: {e}")
            return {"error": str(e)}
    
    async def process_batch(
        self,
        texts: List[str],
        operation: str = "analyze"
    ) -> List[Dict[str, Any]]:
        """        Process multiple texts in batch with load balancing
        
        Args:
            texts: List of texts to process
            operation: Operation to perform ('analyze', 'generate', 'translate')
            
        Returns:
            List of processing results
        """        try:
            if operation == "analyze":
                results = []
                for text in texts:
                    result = await self.analyze_text(text)
                    results.append(result)
                return results
            else:
                # For other operations, use agent manager's batch processing
                if operation == "analyze":
                    return await self.agent_manager.process_text_batch(texts, TextProcessingType.ANALYSIS)
                else:
                    # Fallback to individual processing
                    results = []
                    for text in texts:
                        result = await self.analyze_text(text)
                        results.append(result)
                    return results
                    
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return [{"error": str(e)}]
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""        try:
            # Get component health
            agent_stats = await self.agent_manager.get_aggregate_stats()
            nlp_stats = self.nlp_engine.get_analysis_stats()
            detection_stats = self.language_detector.get_detection_stats()
            translation_stats = self.translation_engine.get_translation_stats()
            generation_stats = self.ai_generator.get_generation_stats()
            
            uptime = (datetime.now(timezone.utc) - self.system_stats["system_uptime"]).total_seconds()
            
            health_status = {
                "system_status": "healthy",
                "uptime_seconds": uptime,
                "total_requests": self.system_stats["total_requests"],
                "successful_operations": self.system_stats["successful_operations"],
                "success_rate": (
                    self.system_stats["successful_operations"] / 
                    max(1, self.system_stats["total_requests"])
                ),
                "components": {
                    "text_agents": agent_stats,
                    "nlp_engine": nlp_stats,
                    "language_detector": detection_stats,
                    "translation_engine": translation_stats,
                    "content_generator": generation_stats
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "system_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def shutdown(self):
        """Gracefully shutdown the text agent system"""        logger.info("Shutting down TextAgentSystem...")
        
        # Cleanup tasks can be added here
        # For now, just log the shutdown
        
        logger.info("TextAgentSystem shutdown complete")


# Convenience functions for direct access
async def analyze_text(text: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for text analysis"""    system = TextAgentSystem()
    return await system.analyze_text(text, kwargs)

async def generate_content(prompt: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for content generation"""    system = TextAgentSystem()
    config = GenerationConfig(**kwargs) if kwargs else None
    return await system.generate_content(prompt, config)

async def translate_text(text: str, target_language: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for text translation"""    system = TextAgentSystem()
    return await system.translate_text(text, target_language, **kwargs)

async def detect_plagiarism(text: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for plagiarism detection"""    system = TextAgentSystem()
    return await system.detect_plagiarism(text, **kwargs)

# Global system instance for singleton pattern
_global_system = None

def get_text_system() -> TextAgentSystem:
    """Get or create global text system instance"""    global _global_system
    if _global_system is None:
        _global_system = TextAgentSystem()
    return _global_system
