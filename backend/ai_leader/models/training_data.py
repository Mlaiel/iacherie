"""
Training Data Models
Stores examples from external API calls for training
"""

from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel


class TrainingExample(BaseModel):
    """
        Single training example from API call"""
    
    # Input/Output
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    
    # Metadata
    api_provider: str
    capability_type: str
    timestamp: datetime
    
    # Quality metrics
    response_time_ms: float
    cost: float
    success: bool
    
    # Optional feedback
    user_rating: Optional[float] = None
    user_feedback: Optional[str] = None


class TrainingData(BaseModel):
    """
        Collection of training examples for a capability"""
    
    capability_type: str
    examples: list[TrainingExample] = []
    
    # Statistics
    total_examples: int = 0
    total_cost: float = 0.0
    avg_quality: float = 0.0
    
    # Dataset info
    created_at: datetime
    last_updated: datetime
    dataset_version: str = "1.0"
    
    def add_example(self, example: TrainingExample):
        """Add training example and update statistics"""
        self.examples.append(example)
        self.total_examples += 1
        self.total_cost += example.cost
        self.last_updated = datetime.now()
        
        # Update average quality
        if example.user_rating:
            ratings = [e.user_rating for e in self.examples if e.user_rating]
            self.avg_quality = sum(ratings) / len(ratings)
