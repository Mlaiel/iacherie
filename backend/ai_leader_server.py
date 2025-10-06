"""
AI Leader API Server
FastAPI server exposing AI Leader Agent endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from backend.ai_leader.agents.leader_agent import LeaderAgent
from backend.ai_leader.models.api_capability import APICapability, CapabilityType
from backend.ai_leader.trainers.capability_trainer import CapabilityTrainer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Leader API",
    description="Autonomous AI that learns from external APIs",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Leader Agent
leader_agent = LeaderAgent()
capability_trainer = CapabilityTrainer()


# Request/Response Models
class ExecuteCapabilityRequest(BaseModel):
    capability_type: CapabilityType
    input_data: Dict[str, Any]
    prefer_internal: bool = True


class TrainCapabilityRequest(BaseModel):
    capability_type: CapabilityType
    training_config: Optional[Dict[str, Any]] = None


# Routes
@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "AI Leader Agent",
        "version": "1.0.0"
    }


@app.get("/api/leader/status")
async def get_status():
    """Get AI Leader autonomy status"""
    try:
        status = leader_agent.get_autonomy_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/leader/execute")
async def execute_capability(request: ExecuteCapabilityRequest):
    """
    Execute a capability using AI Leader
    Will use internal model if available, otherwise fallback to external API
    """
    try:
        result = leader_agent.execute_capability(
            capability_type=request.capability_type,
            input_data=request.input_data,
            prefer_internal=request.prefer_internal
        )

        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Error executing capability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/leader/train")
async def train_capability(request: TrainCapabilityRequest):
    """
    Start training a capability
    Requires sufficient training data collected from API calls
    """
    try:
        # Get capability and training data

        capability = leader_agent.capabilities.get(request.capability_type)

        training_data = leader_agent.training_data.get(request.capability_type)

        
        if not capability:
            raise HTTPException(
                status_code=404,
                detail=f"Capability {request.capability_type} not registered"
            )

        
        if not training_data:
            raise HTTPException(
                status_code=400,
                detail="No training data available for this capability"
            )
        
        # Start training

        result = capability_trainer.start_training(
            capability=capability,
            training_data=training_data,
            training_config=request.training_config
        )

        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leader/training/{job_id}")
async def get_training_status(job_id: str):
    """Get status of a training job"""
    try:
        status = capability_trainer.get_training_status(job_id)

        
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Training job {job_id} not found"
            )

        
        return {
            "success": True,
            "data": status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting training status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leader/providers/health")
async def get_provider_health():
    """Get health status of external API providers"""
    try:
        health = leader_agent.fallback_manager.get_provider_health()

        
        return {
            "success": True,
            "data": health
        }
    except Exception as e:
        logger.error(f"Error getting provider health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/leader/capabilities/register")
async def register_capability(capability: APICapability):
    """Register a new capability for the AI to learn"""
    try:
        leader_agent.register_capability(capability)

        
        return {
            "success": True,
            "message": f"Capability {capability.name} registered successfully"
        }
    except Exception as e:
        logger.error(f"Error registering capability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leader/capabilities")
async def list_capabilities():
    """List all registered capabilities"""
    try:
        capabilities = [
            {
                "type": cap.capability_type,
                "name": cap.name,
                "description": cap.description,
                "is_trained": cap.is_trained,
                "can_replace_api": cap.can_replace_api,
                "training_samples": cap.training_samples,
                "accuracy": cap.accuracy,
                "original_api": cap.original_api
            }
            for cap in leader_agent.capabilities.values()
        ]
        
        return {
            "success": True,
            "data": capabilities
        }
    except Exception as e:
        logger.error(f"Error listing capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    # Initialize some example capabilities on startup
    example_capabilities = [
        APICapability(
            capability_type=CapabilityType.TEXT_GENERATION,
            name="Text Generation",
            description="Generate human-like text responses",
            original_api="OpenAI GPT-4",
            api_cost=0.03
        ),
        APICapability(
            capability_type=CapabilityType.IMAGE_GENERATION,
            name="Image Generation",
            description="Generate images from text prompts",
            original_api="DALL-E 3",
            api_cost=0.04
        ),
        APICapability(
            capability_type=CapabilityType.VIDEO_GENERATION,
            name="Video Generation",
            description="Generate videos from text or images",
            original_api="RunwayML Gen-3",
            api_cost=1.0
        )
    ]
    
    for cap in example_capabilities:
        leader_agent.register_capability(cap)
    
    logger.info("AI Leader API Server starting...")
    logger.info("Registered 3 example capabilities")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
