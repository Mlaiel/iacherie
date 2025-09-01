"""{{agent_name}} AI Agent for Ainflue Platform
{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field

from ai.base_agent import BaseAIAgent
from ai.models import AIModelManager
from ai.prompts import PromptManager
from core.config import get_settings
from utils.exceptions import AIException


logger = logging.getLogger(__name__)
settings = get_settings()


class {{agent_name}}State(Enum):
    """States for {{agent_name}} agent"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class {{agent_name}}Task(BaseModel):
    """Task model for {{agent_name}} agent"""
    id: str = Field(..., description="Unique task identifier")
    input_data: Dict[str, Any] = Field(..., description="Input data for processing")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Processing parameters")
    priority: int = Field(default=1, description="Task priority (1-10)")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class {{agent_name}}Result(BaseModel):
    """Result model for {{agent_name}} agent"""
    task_id: str = Field(..., description="Task identifier")
    success: bool = Field(..., description="Whether the task succeeded")
    result_data: Optional[Dict[str, Any]] = Field(default=None, description="Result data")
    confidence: Optional[float] = Field(default=None, description="Confidence score (0-1)")
    processing_time: float = Field(..., description="Processing time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Agent Interface
class I{{agent_name}}Agent(ABC):
    """Interface for {{agent_name}} AI agent"""
    
    @abstractmethod
    async def process_task(self, task: {{agent_name}}Task) -> {{agent_name}}Result:
        """Process a task using AI capabilities"""
        pass
    
    @abstractmethod
    async def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train the agent with new data"""
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and metadata"""
        pass


# Agent Implementation
class {{agent_name}}Agent(BaseAIAgent, I{{agent_name}}Agent):
    """{{agent_name}} AI agent implementation"""
    
    def __init__(self, model_name: str = "default", **kwargs):
        super().__init__(agent_name="{{agent_name}}", **kwargs)
        self.model_name = model_name
        self.state = {{agent_name}}State.IDLE
        self.model_manager = AIModelManager()
        self.prompt_manager = PromptManager()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Agent-specific configuration
        self.config = {
            "max_tokens": 1000,
            "temperature": 0.7,
            "timeout": 30.0,
            "batch_size": 10
        }
        
        # Initialize model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the AI model"""
        try:
            self.model = self.model_manager.load_model(self.model_name)
            self.logger.info(f"{{agent_name}} agent initialized with model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize model: {str(e)}")
            raise AIException(f"Model initialization failed: {str(e)}")
    
    async def process_task(self, task: {{agent_name}}Task) -> {{agent_name}}Result:
        """Process a task using AI capabilities"""
        start_time = datetime.utcnow()
        self.state = {{agent_name}}State.PROCESSING
        
        try:
            self.logger.info(f"Processing task {task.id} with {{agent_name}} agent")
            
            # Validate input
            await self._validate_input(task)
            
            # Preprocess data
            processed_input = await self._preprocess_data(task.input_data)
            
            # Generate AI response
            ai_response = await self._generate_response(processed_input, task.parameters)
            
            # Postprocess results
            result_data = await self._postprocess_results(ai_response)
            
            # Calculate confidence
            confidence = await self._calculate_confidence(ai_response)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.state = {{agent_name}}State.COMPLETED
            
            return {{agent_name}}Result(
                task_id=task.id,
                success=True,
                result_data=result_data,
                confidence=confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.state = {{agent_name}}State.ERROR
            self.logger.error(f"Error processing task {task.id}: {str(e)}")
            
            return {{agent_name}}Result(
                task_id=task.id,
                success=False,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _validate_input(self, task: {{agent_name}}Task) -> None:
        """Validate task input data"""
        if not task.input_data:
            raise AIException("Input data is required")
        
        # Add specific validation logic here
        required_fields = ["text"]  # Example required fields
        for field in required_fields:
            if field not in task.input_data:
                raise AIException(f"Required field '{field}' missing from input data")
    
    async def _preprocess_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess input data for AI model"""
        processed_data = input_data.copy()
        
        # Add preprocessing logic here
        # Example: text cleaning, normalization, tokenization
        if "text" in processed_data:
            processed_data["text"] = self._clean_text(processed_data["text"])
        
        return processed_data
    
    async def _generate_response(self, input_data: Dict[str, Any], parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI response using the model"""
        try:
            # Get appropriate prompt template
            prompt = self.prompt_manager.get_prompt("{{agent_name_lower}}_processing", **input_data)
            
            # Configure model parameters
            model_params = {
                "max_tokens": parameters.get("max_tokens", self.config["max_tokens"]) if parameters else self.config["max_tokens"],
                "temperature": parameters.get("temperature", self.config["temperature"]) if parameters else self.config["temperature"]
            }
            
            # Generate response
            response = await self.model.generate(prompt, **model_params)
            
            return {
                "response": response,
                "prompt": prompt,
                "parameters": model_params
            }
            
        except Exception as e:
            raise AIException(f"AI generation failed: {str(e)}")
    
    async def _postprocess_results(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess AI results"""
        processed_results = {
            "output": ai_response.get("response"),
            "metadata": {
                "model": self.model_name,
                "prompt_length": len(ai_response.get("prompt", "")),
                "response_length": len(str(ai_response.get("response", "")))
            }
        }
        
        # Add postprocessing logic here
        # Example: result formatting, validation, filtering
        
        return processed_results
    
    async def _calculate_confidence(self, ai_response: Dict[str, Any]) -> float:
        """Calculate confidence score for the result"""
        # Add confidence calculation logic here
        # Example: based on model certainty, response coherence, etc.
        base_confidence = 0.8  # Default confidence
        
        # Adjust based on response quality
        response = ai_response.get("response", "")
        if len(response) < 10:
            base_confidence *= 0.5
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not isinstance(text, str):
            return str(text)
        
        # Basic text cleaning
        text = text.strip()
        text = " ".join(text.split())  # Normalize whitespace
        
        return text
    
    async def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train the agent with new data"""
        try:
            self.logger.info(f"Training {{agent_name}} agent with {len(training_data)} samples")
            
            # Add training logic here
            # Example: fine-tuning, updating embeddings, etc.
            
            self.logger.info("Training completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Training failed: {str(e)}")
            return False
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and metadata"""
        return {
            "name": "{{agent_name}}",
            "version": "1.0.0",
            "description": "{{agent_description}}",
            "model": self.model_name,
            "state": self.state.value,
            "capabilities": [
                "text_processing",
                "ai_generation",
                "batch_processing"
            ],
            "configuration": self.config,
            "supported_input_types": ["text", "json"],
            "supported_output_types": ["text", "json"],
            "max_input_size": 10000,  # characters
            "average_processing_time": 2.5  # seconds
        }


# Agent Factory
class {{agent_name}}AgentFactory:
    """Factory for creating {{agent_name}} agent instances"""
    
    _instances: Dict[str, {{agent_name}}Agent] = {}
    
    @classmethod
    def get_agent(cls, model_name: str = "default") -> {{agent_name}}Agent:
        """Get agent instance (singleton per model)"""
        if model_name not in cls._instances:
            cls._instances[model_name] = {{agent_name}}Agent(model_name=model_name)
        return cls._instances[model_name]
    
    @classmethod
    def create_agent(cls, model_name: str = "default", **kwargs) -> {{agent_name}}Agent:
        """Create new agent instance"""
        return {{agent_name}}Agent(model_name=model_name, **kwargs)


# Helper functions
async def create_{{agent_name_lower}}_agent(model_name: str = "default") -> {{agent_name}}Agent:
    """Dependency injection helper for {{agent_name}} agent"""
    return {{agent_name}}AgentFactory.get_agent(model_name)


# Agent configuration
{{agent_name_upper}}_AGENT_CONFIG = {
    "name": "{{agent_name}}",
    "version": "1.0.0",
    "description": "{{agent_description}}",
    "author": "{{author_name}}",
    "created": "{{created_date}}",
    "capabilities": ["ai_processing", "text_analysis", "content_generation"],
    "models": ["gpt-3.5-turbo", "gpt-4", "claude-3"],
    "default_model": "gpt-3.5-turbo"
}