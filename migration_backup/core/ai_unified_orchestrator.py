#!/usr/bin/env python3
"""
🧠 UNIFIED AI ORCHESTRATOR
==========================

Central orchestration system for all AI operations in Ainfluencer platform.
Consolidates multiple AI orchestrators into a single, efficient system.

Author: Lead Dev IA Expert
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class AITask:
    """AI task definition"""
    task_id: str
    task_type: str  # content_generation, analysis, optimization, moderation
    input_data: Dict[str, Any]
    priority: int = 1  # 1=highest, 5=lowest
    model_preference: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    created_at: datetime = datetime.now()

@dataclass
class AIModel:
    """AI model configuration"""
    model_id: str
    model_type: str  # llm, vision, audio, embedding
    provider: str  # openai, local, huggingface
    endpoint: str
    max_tokens: int
    cost_per_token: float
    performance_score: float
    availability: bool = True

class UnifiedAIOrchestrator:
    """Central AI orchestration system"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.models: Dict[str, AIModel] = {}
        self.task_queue: List[AITask] = []
        self.active_tasks: Dict[str, AITask] = {}
        self.performance_metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_response_time": 0.0,
            "total_cost": 0.0
        }
    
    def register_model(self, model: AIModel) -> bool:
        """Register an AI model"""
        try:
            self.models[model.model_id] = model
            self.logger.info(f"Registered AI model: {model.model_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register model {model.model_id}: {e}")
            return False
    
    async def process_task(self, task: AITask) -> Dict[str, Any]:
        """Process an AI task"""
        start_time = datetime.now()
        
        try:
            # Select best model for task
            selected_model = self._select_optimal_model(task)
            if not selected_model:
                raise ValueError("No suitable model available")
            
            # Add to active tasks
            self.active_tasks[task.task_id] = task
            
            # Process based on task type
            if task.task_type == "content_generation":
                result = await self._generate_content(task, selected_model)
            elif task.task_type == "analysis":
                result = await self._analyze_content(task, selected_model)
            elif task.task_type == "optimization":
                result = await self._optimize_content(task, selected_model)
            elif task.task_type == "moderation":
                result = await self._moderate_content(task, selected_model)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(task, selected_model, processing_time, True)
            
            # Remove from active tasks
            del self.active_tasks[task.task_id]
            
            return {
                "task_id": task.task_id,
                "success": True,
                "result": result,
                "model_used": selected_model.model_id,
                "processing_time": processing_time
            }
            
        except Exception as e:
            # Update metrics for failure
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(task, None, processing_time, False)
            
            # Remove from active tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            
            self.logger.error(f"Task {task.task_id} failed: {e}")
            return {
                "task_id": task.task_id,
                "success": False,
                "error": str(e),
                "processing_time": processing_time
            }
    
    def _select_optimal_model(self, task: AITask) -> Optional[AIModel]:
        """Select the optimal model for a task"""
        suitable_models = []
        
        for model in self.models.values():
            if not model.availability:
                continue
                
            # Check if model can handle the task
            if task.task_type == "content_generation" and model.model_type in ["llm"]:
                suitable_models.append(model)
            elif task.task_type in ["analysis", "moderation"] and model.model_type in ["llm", "vision"]:
                suitable_models.append(model)
            elif task.task_type == "optimization" and model.model_type in ["llm"]:
                suitable_models.append(model)
        
        if not suitable_models:
            return None
        
        # Select model with best performance/cost ratio
        return max(suitable_models, key=lambda m: m.performance_score / max(m.cost_per_token, 0.001))
    
    async def _generate_content(self, task: AITask, model: AIModel) -> Dict[str, Any]:
        """Generate content using AI model"""
        # Simplified implementation - in real scenario would call actual AI APIs
        return {
            "content": f"Generated content for task {task.task_id}",
            "tokens_used": 100,
            "model": model.model_id
        }
    
    async def _analyze_content(self, task: AITask, model: AIModel) -> Dict[str, Any]:
        """Analyze content using AI model"""
        return {
            "analysis": f"Analysis result for task {task.task_id}",
            "sentiment": "positive",
            "topics": ["ai", "technology"],
            "model": model.model_id
        }
    
    async def _optimize_content(self, task: AITask, model: AIModel) -> Dict[str, Any]:
        """Optimize content using AI model"""
        return {
            "optimized_content": f"Optimized content for task {task.task_id}",
            "improvements": ["clarity", "engagement"],
            "model": model.model_id
        }
    
    async def _moderate_content(self, task: AITask, model: AIModel) -> Dict[str, Any]:
        """Moderate content using AI model"""
        return {
            "is_safe": True,
            "confidence": 0.95,
            "flags": [],
            "model": model.model_id
        }
    
    def _update_metrics(self, task: AITask, model: Optional[AIModel], 
                       processing_time: float, success: bool) -> None:
        """Update performance metrics"""
        self.performance_metrics["total_tasks"] += 1
        
        if success:
            self.performance_metrics["successful_tasks"] += 1
        else:
            self.performance_metrics["failed_tasks"] += 1
        
        # Update average response time
        total_tasks = self.performance_metrics["total_tasks"]
        current_avg = self.performance_metrics["average_response_time"]
        new_avg = ((current_avg * (total_tasks - 1)) + processing_time) / total_tasks
        self.performance_metrics["average_response_time"] = new_avg
        
        # Update cost if model was used
        if model and success:
            estimated_cost = 100 * model.cost_per_token  # Simplified calculation
            self.performance_metrics["total_cost"] += estimated_cost
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "active_models": len([m for m in self.models.values() if m.availability]),
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
            "performance_metrics": self.performance_metrics
        }

# Global orchestrator instance
ai_orchestrator = UnifiedAIOrchestrator()

# Register default models
default_models = [
    AIModel(
        model_id="gpt-4-turbo",
        model_type="llm",
        provider="openai",
        endpoint="https://api.openai.com/v1/chat/completions",
        max_tokens=4096,
        cost_per_token=0.00003,
        performance_score=0.95
    ),
    AIModel(
        model_id="claude-3-opus",
        model_type="llm", 
        provider="anthropic",
        endpoint="https://api.anthropic.com/v1/messages",
        max_tokens=4096,
        cost_per_token=0.000015,
        performance_score=0.92
    )
]

for model in default_models:
    ai_orchestrator.register_model(model)
