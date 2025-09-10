"""HuggingFace Integration - Comprehensive ML Model Hub Integration
===============================================================

Enterprise-grade integration with HuggingFace Hub for accessing thousands
of machine learning models, datasets, and spaces.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import base64
from typing import Dict, List, Optional, Any, Union, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
from io import BytesIO
import tempfile
import os

import httpx
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM,
    AutoModelForSequenceClassification, AutoModelForQuestionAnswering,
    pipeline, Pipeline
)
from datasets import load_dataset
from huggingface_hub import HfApi, HfFolder, Repository
from diffusers import StableDiffusionPipeline, DiffusionPipeline
import numpy as np
from PIL import Image


class HuggingFaceTask(Enum):
    """HuggingFace pipeline tasks."""
    TEXT_GENERATION = "text-generation"
    TEXT2TEXT_GENERATION = "text2text-generation"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    QUESTION_ANSWERING = "question-answering"
    TEXT_CLASSIFICATION = "text-classification"
    SENTIMENT_ANALYSIS = "sentiment-analysis"
    TOKEN_CLASSIFICATION = "token-classification"
    FEATURE_EXTRACTION = "feature-extraction"
    FILL_MASK = "fill-mask"
    IMAGE_CLASSIFICATION = "image-classification"
    IMAGE_GENERATION = "image-generation"
    OBJECT_DETECTION = "object-detection"
    IMAGE_SEGMENTATION = "image-segmentation"
    SPEECH_RECOGNITION = "automatic-speech-recognition"
    AUDIO_CLASSIFICATION = "audio-classification"
    TEXT_TO_SPEECH = "text-to-speech"
    ZERO_SHOT_CLASSIFICATION = "zero-shot-classification"


class ModelType(Enum):
    """Model deployment types."""
    TRANSFORMERS = "transformers"
    DIFFUSERS = "diffusers"
    CUSTOM = "custom"
    INFERENCE_API = "inference_api"


@dataclass
class ModelInfo:
    """Model information and metadata."""
    model_id: str
    task: Optional[HuggingFaceTask] = None
    model_type: ModelType = ModelType.TRANSFORMERS
    tags: List[str] = field(default_factory=list)
    downloads: int = 0
    likes: int = 0
    library_name: Optional[str] = None
    pipeline_tag: Optional[str] = None
    created_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceRequest:
    """Inference request configuration."""
    id: str
    model_id: str
    task: HuggingFaceTask
    inputs: Any
    parameters: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    use_cache: bool = True
    wait_for_model: bool = True


@dataclass
class InferenceResponse:
    """Inference response."""
    id: str
    request_id: str
    model_id: str
    task: str
    outputs: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0
    error: Optional[str] = None


class HuggingFaceIntegration:
    """Comprehensive HuggingFace integration."""
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.api_token = api_token
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize HuggingFace API
        self.hf_api = HfApi(token=api_token)
        if api_token:
            HfFolder.save_token(api_token)
        
        # HTTP client for Inference API
        self.inference_client = httpx.AsyncClient(
            base_url="https://api-inference.huggingface.co",
            headers={
                "Authorization": f"Bearer {api_token}" if api_token else None
            },
            timeout=300.0
        )
        
        # Model cache
        self.loaded_models: Dict[str, Any] = {}
        self.loaded_pipelines: Dict[str, Pipeline] = {}
        self.model_cache_limit = self.config.get('model_cache_limit', 5)
        
        # Device configuration
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        # Performance tracking
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_processing_time': 0.0,
            'model_usage': {},
            'task_usage': {},
            'memory_usage': 0.0
        }
        
        # Request history
        self.request_history: List[InferenceResponse] = []
        self.max_history = self.config.get('max_history', 1000)
        
    async def initialize(self):
        """Initialize the HuggingFace integration."""
        # Test API connectivity
        try:
            user_info = self.hf_api.whoami()
            self.logger.info(f"HuggingFace authenticated as: {user_info.get('name', 'unknown')}")
        except Exception as e:
            self.logger.warning(f"HuggingFace authentication failed: {e}")
        
        self.logger.info("HuggingFace integration initialized")
    
    async def search_models(
        self,
        task: Optional[HuggingFaceTask] = None,
        library: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 20,
        sort: str = "downloads"
    ) -> List[ModelInfo]:
        """Search for models in HuggingFace Hub."""
        try:
            # Build search filters
            filter_params = {}
            if task:
                filter_params['pipeline_tag'] = task.value
            if library:
                filter_params['library'] = library
            if language:
                filter_params['language'] = language
            
            # Search models
            models = self.hf_api.list_models(
                filter=filter_params,
                sort=sort,
                direction=-1,
                limit=limit
            )
            
            model_infos = []
            for model in models:
                model_info = ModelInfo(
                    model_id=model.modelId,
                    task=HuggingFaceTask(model.pipeline_tag) if model.pipeline_tag else None,
                    tags=model.tags or [],
                    downloads=model.downloads or 0,
                    likes=model.likes or 0,
                    library_name=getattr(model, 'library_name', None),
                    pipeline_tag=model.pipeline_tag,
                    created_at=model.createdAt,
                    last_modified=model.lastModified
                )
                model_infos.append(model_info)
            
            self.logger.info(f"Found {len(model_infos)} models")
            return model_infos
            
        except Exception as e:
            self.logger.error(f"Model search failed: {e}")
            return []
    
    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get detailed information about a specific model."""
        try:
            model_info = self.hf_api.model_info(model_id)
            
            return ModelInfo(
                model_id=model_info.modelId,
                task=HuggingFaceTask(model_info.pipeline_tag) if model_info.pipeline_tag else None,
                tags=model_info.tags or [],
                downloads=model_info.downloads or 0,
                likes=model_info.likes or 0,
                library_name=getattr(model_info, 'library_name', None),
                pipeline_tag=model_info.pipeline_tag,
                created_at=model_info.createdAt,
                last_modified=model_info.lastModified,
                metadata={
                    'siblings': [s.rfilename for s in model_info.siblings] if model_info.siblings else [],
                    'config': getattr(model_info, 'config', {})
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get model info for {model_id}: {e}")
            return None
    
    async def load_model(
        self,
        model_id: str,
        task: Optional[HuggingFaceTask] = None,
        use_cache: bool = True
    ) -> Pipeline:
        """Load a model for local inference."""
        cache_key = f"{model_id}:{task.value if task else 'auto'}"
        
        # Check cache
        if use_cache and cache_key in self.loaded_pipelines:
            self.metrics['cache_hits'] += 1
            return self.loaded_pipelines[cache_key]
        
        self.metrics['cache_misses'] += 1
        
        try:
            # Manage cache size
            if len(self.loaded_pipelines) >= self.model_cache_limit:
                # Remove least recently used model
                oldest_key = next(iter(self.loaded_pipelines))
                del self.loaded_pipelines[oldest_key]
                self.logger.info(f"Removed cached model: {oldest_key}")
            
            # Load pipeline
            if task:
                pipe = pipeline(
                    task=task.value,
                    model=model_id,
                    device=0 if torch.cuda.is_available() else -1,
                    torch_dtype=self.torch_dtype
                )
            else:
                pipe = pipeline(
                    model=model_id,
                    device=0 if torch.cuda.is_available() else -1,
                    torch_dtype=self.torch_dtype
                )
            
            # Cache the pipeline
            self.loaded_pipelines[cache_key] = pipe
            
            self.logger.info(f"Loaded model: {model_id}")
            return pipe
            
        except Exception as e:
            self.logger.error(f"Failed to load model {model_id}: {e}")
            raise
    
    async def inference_api(
        self,
        model_id: str,
        inputs: Any,
        task: Optional[HuggingFaceTask] = None,
        parameters: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> InferenceResponse:
        """Run inference using HuggingFace Inference API."""
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Prepare request payload
            payload = {"inputs": inputs}
            if parameters:
                payload["parameters"] = parameters
            if options:
                payload["options"] = options
            
            # Make API request
            url = f"/models/{model_id}"
            response = await self.inference_client.post(url, json=payload)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                outputs = response.json()
                
                inference_response = InferenceResponse(
                    id=str(uuid.uuid4()),
                    request_id=request_id,
                    model_id=model_id,
                    task=task.value if task else "unknown",
                    outputs=outputs,
                    processing_time=processing_time
                )
                
                await self._update_metrics(inference_response, True)
                return inference_response
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                raise Exception(f"API error {response.status_code}: {error_data}")
                
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_response = InferenceResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model_id=model_id,
                task=task.value if task else "unknown",
                outputs=None,
                error=str(e),
                processing_time=processing_time
            )
            
            await self._update_metrics(error_response, False)
            self.logger.error(f"Inference API failed: {e}")
            return error_response
    
    async def local_inference(
        self,
        model_id: str,
        inputs: Any,
        task: Optional[HuggingFaceTask] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> InferenceResponse:
        """Run inference using locally loaded model."""
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Load model if not cached
            pipe = await self.load_model(model_id, task)
            
            # Prepare inference parameters
            if parameters:
                outputs = pipe(inputs, **parameters)
            else:
                outputs = pipe(inputs)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            inference_response = InferenceResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model_id=model_id,
                task=task.value if task else pipe.task,
                outputs=outputs,
                metadata={'method': 'local'},
                processing_time=processing_time
            )
            
            await self._update_metrics(inference_response, True)
            return inference_response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_response = InferenceResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model_id=model_id,
                task=task.value if task else "unknown",
                outputs=None,
                error=str(e),
                processing_time=processing_time
            )
            
            await self._update_metrics(error_response, False)
            self.logger.error(f"Local inference failed: {e}")
            return error_response
    
    async def text_generation(
        self,
        model_id: str,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: float = 1.0,
        top_p: float = 1.0,
        top_k: Optional[int] = None,
        num_return_sequences: int = 1,
        use_local: bool = False
    ) -> InferenceResponse:
        """Generate text using language models."""
        parameters = {
            "temperature": temperature,
            "top_p": top_p,
            "num_return_sequences": num_return_sequences
        }
        
        if max_length:
            parameters["max_length"] = max_length
        if top_k:
            parameters["top_k"] = top_k
        
        if use_local:
            return await self.local_inference(
                model_id=model_id,
                inputs=prompt,
                task=HuggingFaceTask.TEXT_GENERATION,
                parameters=parameters
            )
        else:
            return await self.inference_api(
                model_id=model_id,
                inputs=prompt,
                task=HuggingFaceTask.TEXT_GENERATION,
                parameters=parameters
            )
    
    async def text_classification(
        self,
        model_id: str,
        text: str,
        use_local: bool = False
    ) -> InferenceResponse:
        """Classify text using classification models."""
        if use_local:
            return await self.local_inference(
                model_id=model_id,
                inputs=text,
                task=HuggingFaceTask.TEXT_CLASSIFICATION
            )
        else:
            return await self.inference_api(
                model_id=model_id,
                inputs=text,
                task=HuggingFaceTask.TEXT_CLASSIFICATION
            )
    
    async def sentiment_analysis(
        self,
        text: str,
        model_id: str = "cardiffnlp/twitter-roberta-base-sentiment-latest",
        use_local: bool = False
    ) -> InferenceResponse:
        """Analyze sentiment of text."""
        return await self.text_classification(model_id, text, use_local)
    
    async def summarization(
        self,
        model_id: str,
        text: str,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        use_local: bool = False
    ) -> InferenceResponse:
        """Summarize text using summarization models."""
        parameters = {}
        if max_length:
            parameters["max_length"] = max_length
        if min_length:
            parameters["min_length"] = min_length
        
        if use_local:
            return await self.local_inference(
                model_id=model_id,
                inputs=text,
                task=HuggingFaceTask.SUMMARIZATION,
                parameters=parameters
            )
        else:
            return await self.inference_api(
                model_id=model_id,
                inputs=text,
                task=HuggingFaceTask.SUMMARIZATION,
                parameters=parameters
            )
    
    async def question_answering(
        self,
        model_id: str,
        question: str,
        context: str,
        use_local: bool = False
    ) -> InferenceResponse:
        """Answer questions based on context."""
        inputs = {
            "question": question,
            "context": context
        }
        
        if use_local:
            return await self.local_inference(
                model_id=model_id,
                inputs=inputs,
                task=HuggingFaceTask.QUESTION_ANSWERING
            )
        else:
            return await self.inference_api(
                model_id=model_id,
                inputs=inputs,
                task=HuggingFaceTask.QUESTION_ANSWERING
            )
    
    async def translation(
        self,
        model_id: str,
        text: str,
        use_local: bool = False
    ) -> InferenceResponse:
        """Translate text using translation models."""
        if use_local:
            return await self.local_inference(
                model_id=model_id,
                inputs=text,
                task=HuggingFaceTask.TRANSLATION
            )
        else:
            return await self.inference_api(
                model_id=model_id,
                inputs=text,
                task=HuggingFaceTask.TRANSLATION
            )
    
    async def image_classification(
        self,
        model_id: str,
        image: Union[str, bytes, Image.Image],
        use_local: bool = False
    ) -> InferenceResponse:
        """Classify images using vision models."""
        # Handle different image input types
        if isinstance(image, str):
            # Assume it's a base64 encoded image or URL
            if image.startswith('data:'):
                image_data = base64.b64decode(image.split(',')[1])
            else:
                # Assume it's a URL or file path
                async with httpx.AsyncClient() as client:
                    response = await client.get(image)
                    image_data = response.content
        elif isinstance(image, bytes):
            image_data = image
        elif isinstance(image, Image.Image):
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            image_data = buffer.getvalue()
        else:
            raise ValueError("Unsupported image type")
        
        if use_local:
            # For local inference, we need to convert bytes to PIL Image
            image_pil = Image.open(BytesIO(image_data))
            return await self.local_inference(
                model_id=model_id,
                inputs=image_pil,
                task=HuggingFaceTask.IMAGE_CLASSIFICATION
            )
        else:
            # For API, send as base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            return await self.inference_api(
                model_id=model_id,
                inputs=image_b64,
                task=HuggingFaceTask.IMAGE_CLASSIFICATION
            )
    
    async def feature_extraction(
        self,
        model_id: str,
        text: str,
        use_local: bool = False
    ) -> InferenceResponse:
        """Extract features/embeddings from text."""
        if use_local:
            return await self.local_inference(
                model_id=model_id,
                inputs=text,
                task=HuggingFaceTask.FEATURE_EXTRACTION
            )
        else:
            return await self.inference_api(
                model_id=model_id,
                inputs=text,
                task=HuggingFaceTask.FEATURE_EXTRACTION
            )
    
    async def load_dataset(
        self,
        dataset_name: str,
        config_name: Optional[str] = None,
        split: Optional[str] = None,
        streaming: bool = False
    ) -> Any:
        """Load dataset from HuggingFace Hub."""
        try:
            dataset = load_dataset(
                dataset_name,
                config_name,
                split=split,
                streaming=streaming
            )
            
            self.logger.info(f"Loaded dataset: {dataset_name}")
            return dataset
            
        except Exception as e:
            self.logger.error(f"Failed to load dataset {dataset_name}: {e}")
            raise
    
    async def _update_metrics(self, response: InferenceResponse, success: bool):
        """Update integration metrics."""
        self.metrics['total_requests'] += 1
        
        if success:
            self.metrics['successful_requests'] += 1
            
            # Update model usage
            if response.model_id not in self.metrics['model_usage']:
                self.metrics['model_usage'][response.model_id] = 0
            self.metrics['model_usage'][response.model_id] += 1
            
            # Update task usage
            if response.task not in self.metrics['task_usage']:
                self.metrics['task_usage'][response.task] = 0
            self.metrics['task_usage'][response.task] += 1
            
        else:
            self.metrics['failed_requests'] += 1
        
        # Update average processing time
        total_requests = self.metrics['total_requests']
        current_avg = self.metrics['average_processing_time']
        self.metrics['average_processing_time'] = (
            (current_avg * (total_requests - 1) + response.processing_time) / total_requests
        )
        
        # Add to history
        self.request_history.append(response)
        if len(self.request_history) > self.max_history:
            self.request_history.pop(0)
        
        # Update memory usage if CUDA is available
        if torch.cuda.is_available():
            self.metrics['memory_usage'] = torch.cuda.memory_allocated() / 1024**3  # GB
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get integration metrics."""
        return {
            'requests': {
                'total': self.metrics['total_requests'],
                'successful': self.metrics['successful_requests'],
                'failed': self.metrics['failed_requests'],
                'success_rate': (
                    self.metrics['successful_requests'] / max(self.metrics['total_requests'], 1)
                ) * 100
            },
            'performance': {
                'average_processing_time': self.metrics['average_processing_time'],
                'cache_hit_rate': (
                    self.metrics['cache_hits'] / max(self.metrics['cache_hits'] + self.metrics['cache_misses'], 1)
                ) * 100
            },
            'usage': {
                'model_usage': self.metrics['model_usage'],
                'task_usage': self.metrics['task_usage']
            },
            'resources': {
                'loaded_models': len(self.loaded_pipelines),
                'memory_usage_gb': self.metrics['memory_usage'],
                'device': str(self.device)
            }
        }
    
    async def clear_cache(self):
        """Clear model cache to free memory."""
        self.loaded_pipelines.clear()
        self.loaded_models.clear()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.logger.info("Model cache cleared")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            # Test model search
            models = await self.search_models(limit=1)
            
            # Test inference API with a simple model
            test_response = await self.inference_api(
                model_id="distilbert-base-uncased-finetuned-sst-2-english",
                inputs="This is a test",
                task=HuggingFaceTask.TEXT_CLASSIFICATION
            )
            
            return {
                'status': 'healthy',
                'api_accessible': test_response.error is None,
                'models_searchable': len(models) > 0,
                'device': str(self.device),
                'memory_usage_gb': self.metrics['memory_usage'],
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        await self.clear_cache()
        await self.inference_client.aclose()


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize HuggingFace integration
        hf = HuggingFaceIntegration(
            api_token="your-huggingface-token"
        )
        
        await hf.initialize()
        
        # Search for models
        models = await hf.search_models(
            task=HuggingFaceTask.TEXT_CLASSIFICATION,
            limit=5
        )
        print(f"Found {len(models)} classification models")
        
        # Test sentiment analysis
        response = await hf.sentiment_analysis("I love this product!")
        print(f"Sentiment: {response.outputs}")
        
        # Test text generation
        response = await hf.text_generation(
            model_id="gpt2",
            prompt="The future of AI is",
            max_length=50
        )
        print(f"Generated text: {response.outputs}")
        
        # Get metrics
        metrics = hf.get_metrics()
        print(f"Metrics: {json.dumps(metrics, indent=2)}")
        
        await hf.cleanup()
    
    # asyncio.run(main())