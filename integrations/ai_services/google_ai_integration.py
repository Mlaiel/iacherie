"""Google AI Platform Integration - Advanced Google AI Services
============================================================

Comprehensive integration with Google AI Platform including Vertex AI, 
PaLM API, Bard, Gemini, and other Google AI services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import base64
import hashlib

import aiohttp
import aiofiles
from google.cloud import aiplatform
from google.auth import default
from google.oauth2 import service_account
import google.generativeai as genai
from google.cloud import automl
from google.cloud import translate_v2 as translate
from google.cloud import vision
from google.cloud import speech
from google.cloud import texttospeech

logger = logging.getLogger(__name__)

class GoogleAIService(Enum):
    """Google AI service types."""
    VERTEX_AI = "vertex_ai"
    PALM_API = "palm_api"
    GEMINI = "gemini"
    BARD = "bard"
    AUTOML = "automl"
    TRANSLATE = "translate"
    VISION = "vision"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    NATURAL_LANGUAGE = "natural_language"

class ModelType(Enum):
    """AI model types."""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    CHAT = "chat"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    SPEECH_RECOGNITION = "speech_recognition"
    SPEECH_SYNTHESIS = "speech_synthesis"
    TRANSLATION = "translation"
    CLASSIFICATION = "classification"

@dataclass
class GoogleAIRequest:
    """Google AI API request."""
    service: GoogleAIService
    model: str
    prompt: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: f"req_{int(time.time() * 1000)}")
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Additional options
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    
    # Multimodal support
    images: List[str] = field(default_factory=list)  # Base64 encoded images
    audio: Optional[str] = None  # Base64 encoded audio
    
    # Safety and filtering
    safety_settings: Dict[str, Any] = field(default_factory=dict)
    content_filter: bool = True

@dataclass
class GoogleAIResponse:
    """Google AI API response."""
    request_id: str
    service: GoogleAIService
    model: str
    
    # Response content
    text: Optional[str] = None
    candidates: List[Dict[str, Any]] = field(default_factory=list)
    
    # Usage statistics
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # Response metadata
    finish_reason: Optional[str] = None
    safety_ratings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Performance metrics
    latency_ms: Optional[float] = None
    cost_estimate: Optional[float] = None
    
    # Error handling
    error: Optional[str] = None
    error_code: Optional[str] = None
    
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class GoogleAIConfiguration:
    """Google AI integration configuration."""
    # Authentication
    project_id: str
    location: str = "us-central1"
    credentials_file: Optional[str] = None
    api_key: Optional[str] = None
    
    # Service endpoints
    vertex_ai_endpoint: Optional[str] = None
    palm_api_endpoint: str = "https://generativelanguage.googleapis.com"
    
    # Default parameters
    default_model: str = "text-bison"
    default_temperature: float = 0.7
    default_max_tokens: int = 1024
    
    # Rate limiting
    requests_per_minute: int = 60
    requests_per_day: int = 1000
    
    # Safety settings
    enable_safety_filters: bool = True
    safety_threshold: str = "BLOCK_MEDIUM_AND_ABOVE"
    
    # Performance settings
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # Cost management
    monthly_budget_usd: Optional[float] = None
    cost_alerts_enabled: bool = True

class GoogleAIIntegration:
    """Comprehensive Google AI Platform integration."""
    
    def __init__(self, config: GoogleAIConfiguration):
        self.config = config
        self.session = None
        self.credentials = None
        
        # Service clients
        self.vertex_client = None
        self.automl_client = None
        self.translate_client = None
        self.vision_client = None
        self.speech_client = None
        self.tts_client = None
        
        # Usage tracking
        self.request_count = 0
        self.token_usage = 0
        self.cost_tracking = 0.0
        self.last_reset = datetime.utcnow()
        
        # Performance monitoring
        self.response_times = []
        self.error_count = 0
        
        logger.info("Google AI Integration initialized")

    async def initialize(self) -> None:
        """Initialize Google AI integration."""
        try:
            # Setup authentication
            await self._setup_authentication()
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds),
                headers={
                    'User-Agent': 'Ainflue-GoogleAI/1.0',
                    'Content-Type': 'application/json'
                }
            )
            
            # Initialize Google AI services
            await self._initialize_services()
            
            # Setup usage monitoring
            await self._setup_monitoring()
            
            logger.info("Google AI integration initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google AI integration: {e}")
            raise

    async def _setup_authentication(self) -> None:
        """Setup Google Cloud authentication."""
        try:
            if self.config.credentials_file:
                # Use service account file
                self.credentials = service_account.Credentials.from_service_account_file(
                    self.config.credentials_file
                )
            else:
                # Use default credentials
                self.credentials, project = default()
                
            # Initialize AI Platform
            aiplatform.init(
                project=self.config.project_id,
                location=self.config.location,
                credentials=self.credentials
            )
            
            # Configure Generative AI
            if self.config.api_key:
                genai.configure(api_key=self.config.api_key)
                
        except Exception as e:
            logger.error(f"Authentication setup failed: {e}")
            raise

    async def _initialize_services(self) -> None:
        """Initialize Google AI service clients."""
        try:
            # Vertex AI client
            self.vertex_client = aiplatform.gapic.PredictionServiceClient(
                credentials=self.credentials
            )
            
            # AutoML client
            self.automl_client = automl.AutoMlClient(credentials=self.credentials)
            
            # Translation client
            self.translate_client = translate.Client(credentials=self.credentials)
            
            # Vision client
            self.vision_client = vision.ImageAnnotatorClient(credentials=self.credentials)
            
            # Speech clients
            self.speech_client = speech.SpeechClient(credentials=self.credentials)
            self.tts_client = texttospeech.TextToSpeechClient(credentials=self.credentials)
            
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            raise

    async def _setup_monitoring(self) -> None:
        """Setup usage monitoring and cost tracking."""
        # This would setup monitoring dashboards, alerts, etc.
        pass

    async def generate_text(
        self,
        prompt: str,
        model: str = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> GoogleAIResponse:
        """Generate text using Google AI models."""
        request = GoogleAIRequest(
            service=GoogleAIService.VERTEX_AI,
            model=model or self.config.default_model,
            prompt=prompt,
            max_tokens=max_tokens or self.config.default_max_tokens,
            temperature=temperature or self.config.default_temperature,
            parameters=kwargs
        )
        
        return await self._execute_request(request)

    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        model: str = "code-bison",
        **kwargs
    ) -> GoogleAIResponse:
        """Generate code using Google AI code models."""
        enhanced_prompt = f"Generate {language} code for: {prompt}"
        
        request = GoogleAIRequest(
            service=GoogleAIService.VERTEX_AI,
            model=model,
            prompt=enhanced_prompt,
            parameters={
                'language': language,
                **kwargs
            }
        )
        
        return await self._execute_request(request)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "chat-bison",
        **kwargs
    ) -> GoogleAIResponse:
        """Chat completion using Google AI chat models."""
        # Convert messages to Google AI format
        prompt = self._format_chat_prompt(messages)
        
        request = GoogleAIRequest(
            service=GoogleAIService.VERTEX_AI,
            model=model,
            prompt=prompt,
            parameters={
                'messages': messages,
                **kwargs
            }
        )
        
        return await self._execute_request(request)

    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "textembedding-gecko",
        **kwargs
    ) -> GoogleAIResponse:
        """Generate embeddings using Google AI embedding models."""
        request = GoogleAIRequest(
            service=GoogleAIService.VERTEX_AI,
            model=model,
            prompt="",  # Not used for embeddings
            parameters={
                'texts': texts,
                'task_type': kwargs.get('task_type', 'RETRIEVAL_DOCUMENT'),
                **kwargs
            }
        )
        
        return await self._execute_embeddings_request(request)

    async def analyze_image(
        self,
        image_data: str,  # Base64 encoded
        prompt: str = "Describe this image",
        model: str = "imagetext",
        **kwargs
    ) -> GoogleAIResponse:
        """Analyze images using Google Vision AI."""
        request = GoogleAIRequest(
            service=GoogleAIService.VISION,
            model=model,
            prompt=prompt,
            images=[image_data],
            parameters=kwargs
        )
        
        return await self._execute_vision_request(request)

    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = None,
        **kwargs
    ) -> GoogleAIResponse:
        """Translate text using Google Translate."""
        request = GoogleAIRequest(
            service=GoogleAIService.TRANSLATE,
            model="translate",
            prompt=text,
            parameters={
                'target_language': target_language,
                'source_language': source_language,
                **kwargs
            }
        )
        
        return await self._execute_translate_request(request)

    async def speech_to_text(
        self,
        audio_data: str,  # Base64 encoded
        language_code: str = "en-US",
        **kwargs
    ) -> GoogleAIResponse:
        """Convert speech to text using Google Speech-to-Text."""
        request = GoogleAIRequest(
            service=GoogleAIService.SPEECH_TO_TEXT,
            model="speech-to-text",
            prompt="",
            audio=audio_data,
            parameters={
                'language_code': language_code,
                **kwargs
            }
        )
        
        return await self._execute_speech_request(request)

    async def text_to_speech(
        self,
        text: str,
        language_code: str = "en-US",
        voice_name: str = None,
        **kwargs
    ) -> GoogleAIResponse:
        """Convert text to speech using Google Text-to-Speech."""
        request = GoogleAIRequest(
            service=GoogleAIService.TEXT_TO_SPEECH,
            model="text-to-speech",
            prompt=text,
            parameters={
                'language_code': language_code,
                'voice_name': voice_name,
                **kwargs
            }
        )
        
        return await self._execute_tts_request(request)

    async def _execute_request(self, request: GoogleAIRequest) -> GoogleAIResponse:
        """Execute a Google AI API request."""
        start_time = time.time()
        
        try:
            # Check rate limits
            await self._check_rate_limits()
            
            # Execute based on service type
            if request.service == GoogleAIService.VERTEX_AI:
                response = await self._execute_vertex_request(request)
            elif request.service == GoogleAIService.PALM_API:
                response = await self._execute_palm_request(request)
            elif request.service == GoogleAIService.GEMINI:
                response = await self._execute_gemini_request(request)
            else:
                raise ValueError(f"Unsupported service: {request.service}")
                
            # Calculate latency
            response.latency_ms = (time.time() - start_time) * 1000
            
            # Update usage tracking
            await self._update_usage_tracking(request, response)
            
            # Monitor performance
            self.response_times.append(response.latency_ms)
            if len(self.response_times) > 100:
                self.response_times.pop(0)
                
            return response
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Google AI request failed: {e}")
            
            return GoogleAIResponse(
                request_id=request.request_id,
                service=request.service,
                model=request.model,
                error=str(e),
                error_code="execution_error",
                latency_ms=(time.time() - start_time) * 1000
            )

    async def _execute_vertex_request(self, request: GoogleAIRequest) -> GoogleAIResponse:
        """Execute Vertex AI request."""
        try:
            # Prepare parameters
            parameters = {
                "temperature": request.temperature or self.config.default_temperature,
                "maxOutputTokens": request.max_tokens or self.config.default_max_tokens,
                "topP": request.top_p or 0.8,
                "topK": request.top_k or 40
            }
            
            # Create instances
            instances = [{"prompt": request.prompt}]
            
            # Make prediction request
            endpoint = f"projects/{self.config.project_id}/locations/{self.config.location}/publishers/google/models/{request.model}"
            
            prediction_request = {
                "instances": instances,
                "parameters": parameters
            }
            
            # This would use the actual Vertex AI client
            # For now, we'll simulate a response
            simulated_response = {
                "predictions": [{
                    "content": f"Generated response for: {request.prompt[:50]}...",
                    "safetyAttributes": {
                        "categories": [],
                        "blocked": False
                    }
                }],
                "metadata": {
                    "tokenMetadata": {
                        "inputTokenCount": {"totalTokens": len(request.prompt.split())},
                        "outputTokenCount": {"totalTokens": 50}
                    }
                }
            }
            
            # Parse response
            prediction = simulated_response["predictions"][0]
            token_metadata = simulated_response.get("metadata", {}).get("tokenMetadata", {})
            
            return GoogleAIResponse(
                request_id=request.request_id,
                service=request.service,
                model=request.model,
                text=prediction.get("content"),
                candidates=[prediction],
                prompt_tokens=token_metadata.get("inputTokenCount", {}).get("totalTokens", 0),
                completion_tokens=token_metadata.get("outputTokenCount", {}).get("totalTokens", 0),
                total_tokens=token_metadata.get("inputTokenCount", {}).get("totalTokens", 0) + 
                           token_metadata.get("outputTokenCount", {}).get("totalTokens", 0),
                safety_ratings=prediction.get("safetyAttributes", {}).get("categories", []),
                finish_reason="STOP"
            )
            
        except Exception as e:
            logger.error(f"Vertex AI request failed: {e}")
            raise

    async def _execute_palm_request(self, request: GoogleAIRequest) -> GoogleAIResponse:
        """Execute PaLM API request."""
        try:
            if not self.config.api_key:
                raise ValueError("API key required for PaLM API")
                
            url = f"{self.config.palm_api_endpoint}/v1beta/models/{request.model}:generateText"
            
            payload = {
                "prompt": {"text": request.prompt},
                "temperature": request.temperature or self.config.default_temperature,
                "candidateCount": 1,
                "maxOutputTokens": request.max_tokens or self.config.default_max_tokens,
                "topP": request.top_p or 0.8,
                "topK": request.top_k or 40
            }
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    candidates = data.get("candidates", [])
                    if candidates:
                        candidate = candidates[0]
                        return GoogleAIResponse(
                            request_id=request.request_id,
                            service=request.service,
                            model=request.model,
                            text=candidate.get("output"),
                            candidates=candidates,
                            finish_reason=candidate.get("finishReason"),
                            safety_ratings=candidate.get("safetyRatings", [])
                        )
                    else:
                        return GoogleAIResponse(
                            request_id=request.request_id,
                            service=request.service,
                            model=request.model,
                            error="No candidates generated",
                            error_code="no_output"
                        )
                else:
                    error_text = await response.text()
                    raise Exception(f"API request failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"PaLM API request failed: {e}")
            raise

    async def _execute_gemini_request(self, request: GoogleAIRequest) -> GoogleAIResponse:
        """Execute Gemini API request."""
        try:
            # Use the generative AI client
            model = genai.GenerativeModel(request.model)
            
            # Prepare content
            content = [request.prompt]
            
            # Add images if provided
            if request.images:
                for image_data in request.images:
                    # Decode base64 image
                    image_bytes = base64.b64decode(image_data)
                    content.append(image_bytes)
                    
            # Generate content
            response = model.generate_content(
                content,
                generation_config=genai.types.GenerationConfig(
                    temperature=request.temperature or self.config.default_temperature,
                    max_output_tokens=request.max_tokens or self.config.default_max_tokens,
                    top_p=request.top_p or 0.8,
                    top_k=request.top_k or 40
                )
            )
            
            return GoogleAIResponse(
                request_id=request.request_id,
                service=request.service,
                model=request.model,
                text=response.text,
                candidates=[{"content": response.text}],
                finish_reason="STOP" if response.text else "SAFETY",
                prompt_tokens=response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                completion_tokens=response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                total_tokens=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            )
            
        except Exception as e:
            logger.error(f"Gemini request failed: {e}")
            raise

    async def _execute_embeddings_request(self, request: GoogleAIRequest) -> GoogleAIResponse:
        """Execute embeddings request."""
        try:
            # This would use the actual embeddings API
            # For now, simulate embeddings
            texts = request.parameters.get('texts', [])
            
            embeddings = []
            for text in texts:
                # Simulate embedding (normally would be actual API call)
                embedding = [0.1] * 768  # Typical embedding dimension
                embeddings.append(embedding)
                
            return GoogleAIResponse(
                request_id=request.request_id,
                service=request.service,
                model=request.model,
                candidates=[{"embeddings": embeddings}],
                prompt_tokens=sum(len(text.split()) for text in texts),
                completion_tokens=0,
                total_tokens=sum(len(text.split()) for text in texts)
            )
            
        except Exception as e:
            logger.error(f"Embeddings request failed: {e}")
            raise

    async def _execute_vision_request(self, request: GoogleAIRequest) -> GoogleAIResponse:
        """Execute Google Vision API request."""
        try:
            if not request.images:
                raise ValueError("No images provided for vision analysis")
                
            # Decode the first image
            image_data = base64.b64decode(request.images[0])
            
            # Create vision image object
            from google.cloud.vision import Image
            image = Image(content=image_data)
            
            # Perform analysis based on request
            if "text" in request.model.lower():
                response = self.vision_client.text_detection(image=image)
                annotations = response.text_annotations
                description = annotations[0].description if annotations else "No text detected"
            else:
                response = self.vision_client.label_detection(image=image)
                labels = response.label_annotations
                description = ", ".join([label.description for label in labels[:5]])
                
            return GoogleAIResponse(
                request_id=request.request_id,
                service=request.service,
                model=request.model,
                text=description,
                candidates=[{"description": description}]
            )
            
        except Exception as e:
            logger.error(f"Vision request failed: {e}")
            raise

    async def _execute_translate_request(self, request: GoogleAIRequest) -> GoogleAIResponse:
        """Execute Google Translate request."""
        try:
            target_language = request.parameters.get('target_language')
            source_language = request.parameters.get('source_language')
            
            # Perform translation
            result = self.translate_client.translate(
                request.prompt,
                target_language=target_language,
                source_language=source_language
            )
            
            return GoogleAIResponse(
                request_id=request.request_id,
                service=request.service,
                model=request.model,
                text=result['translatedText'],
                candidates=[{
                    "translatedText": result['translatedText'],
                    "detectedSourceLanguage": result.get('detectedSourceLanguage')
                }]
            )
            
        except Exception as e:
            logger.error(f"Translation request failed: {e}")
            raise

    async def _execute_speech_request(self, request: GoogleAIRequest) -> GoogleAIResponse:
        """Execute Google Speech-to-Text request."""
        try:
            # Decode audio data
            audio_data = base64.b64decode(request.audio)
            
            # Configure audio
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=request.parameters.get('language_code', 'en-US')
            )
            
            # Perform recognition
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # Extract transcript
            transcript = ""
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                
            return GoogleAIResponse(
                request_id=request.request_id,
                service=request.service,
                model=request.model,
                text=transcript,
                candidates=[{"transcript": transcript}]
            )
            
        except Exception as e:
            logger.error(f"Speech-to-text request failed: {e}")
            raise

    async def _execute_tts_request(self, request: GoogleAIRequest) -> GoogleAIResponse:
        """Execute Google Text-to-Speech request."""
        try:
            # Configure synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=request.prompt)
            
            # Configure voice
            voice = texttospeech.VoiceSelectionParams(
                language_code=request.parameters.get('language_code', 'en-US'),
                name=request.parameters.get('voice_name'),
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # Configure audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            # Perform synthesis
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Encode audio content
            audio_b64 = base64.b64encode(response.audio_content).decode()
            
            return GoogleAIResponse(
                request_id=request.request_id,
                service=request.service,
                model=request.model,
                text=audio_b64,  # Return base64 encoded audio
                candidates=[{"audio_content": audio_b64}]
            )
            
        except Exception as e:
            logger.error(f"Text-to-speech request failed: {e}")
            raise

    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages for Google AI models."""
        formatted_messages = []
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            formatted_messages.append(f"{role}: {content}")
        return "\n".join(formatted_messages)

    async def _check_rate_limits(self) -> None:
        """Check and enforce rate limits."""
        now = datetime.utcnow()
        
        # Reset counters if needed
        if (now - self.last_reset).total_seconds() >= 60:
            self.request_count = 0
            self.last_reset = now
            
        # Check rate limits
        if self.request_count >= self.config.requests_per_minute:
            wait_time = 60 - (now - self.last_reset).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.last_reset = datetime.utcnow()
                
        self.request_count += 1

    async def _update_usage_tracking(
        self,
        request: GoogleAIRequest,
        response: GoogleAIResponse
    ) -> None:
        """Update usage tracking and cost estimation."""
        # Track token usage
        self.token_usage += response.total_tokens
        
        # Estimate costs (simplified pricing)
        cost_per_token = 0.0001  # Example pricing
        estimated_cost = response.total_tokens * cost_per_token
        response.cost_estimate = estimated_cost
        self.cost_tracking += estimated_cost
        
        # Check budget alerts
        if (self.config.monthly_budget_usd and 
            self.cost_tracking > self.config.monthly_budget_usd * 0.8):
            logger.warning(f"Approaching monthly budget limit: ${self.cost_tracking:.2f}")

    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "request_count": self.request_count,
            "token_usage": self.token_usage,
            "cost_tracking": self.cost_tracking,
            "error_count": self.error_count,
            "avg_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            "last_reset": self.last_reset.isoformat()
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        health = {
            "status": "healthy",
            "services": {},
            "usage": await self.get_usage_statistics(),
            "issues": []
        }
        
        # Check service availability
        try:
            # Test basic connectivity
            if self.session:
                health["services"]["http_session"] = "available"
            else:
                health["services"]["http_session"] = "unavailable"
                health["issues"].append("HTTP session not initialized")
                health["status"] = "degraded"
                
            # Check authentication
            if self.credentials:
                health["services"]["authentication"] = "valid"
            else:
                health["services"]["authentication"] = "invalid"
                health["issues"].append("Authentication not configured")
                health["status"] = "degraded"
                
        except Exception as e:
            health["issues"].append(f"Health check error: {e}")
            health["status"] = "unhealthy"
            
        return health

    async def shutdown(self) -> None:
        """Shutdown Google AI integration."""
        logger.info("Shutting down Google AI integration...")
        
        if self.session:
            await self.session.close()
            
        logger.info("Google AI integration shutdown completed")

    def __repr__(self) -> str:
        return f"GoogleAIIntegration(project={self.config.project_id}, requests={self.request_count})"


# Export main classes
__all__ = [
    "GoogleAIIntegration",
    "GoogleAIConfiguration",
    "GoogleAIRequest", 
    "GoogleAIResponse",
    "GoogleAIService",
    "ModelType"
]