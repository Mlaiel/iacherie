"""Violation Detection System
Advanced violation detection and analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""from typing import Dict, Any, List, Optional
from datetime import datetime

from ..core.logging import logger
from ..ai_engine.fingerprinting import fingerprint_engine
from ..ai_engine.vector_database import vector_database


class ViolationDetector:
    """Advanced violation detection using AI fingerprinting"""    
    def __init__(self):
        self.detection_algorithms = ["fingerprint", "visual", "audio", "text"]
        self.confidence_threshold = 0.85
    
    async def detect_violation(self, original_content: Dict[str, Any], 
                             suspected_content: Dict[str, Any]) -> Dict[str, Any]:
        """Detect if suspected content violates original content"""        try:
            content_type = original_content.get("content_type", "unknown")
            
            # Generate fingerprint for suspected content
            suspected_fingerprint = await fingerprint_engine.generate_fingerprint(
                content_type, suspected_content
            )
            
            # Compare with original fingerprint
            original_fingerprint = original_content.get("fingerprint_data", {})
            
            similarity_score = await fingerprint_engine.compare_fingerprints(
                original_fingerprint, suspected_fingerprint, content_type
            )
            
            # Determine if violation exists
            is_violation = similarity_score >= self.confidence_threshold
            
            violation_result = {
                "is_violation": is_violation,
                "similarity_score": similarity_score,
                "confidence_level": self._calculate_confidence(similarity_score),
                "detection_method": "ai_fingerprinting",
                "analysis_details": {
                    "content_type": content_type,
                    "fingerprint_comparison": {
                        "similarity_score": similarity_score,
                        "threshold": self.confidence_threshold
                    }
                },
                "detected_at": datetime.utcnow().isoformat()
            }
            
            return violation_result
            
        except Exception as e:
            logger.error(f"Violation detection failed: {str(e)}")
            return {
                "is_violation": False,
                "error": str(e),
                "detected_at": datetime.utcnow().isoformat()
            }
    
    def _calculate_confidence(self, similarity_score: float) -> str:
        """Calculate confidence level based on similarity score"""        if similarity_score >= 0.95:
            return "very_high"
        elif similarity_score >= 0.90:
            return "high"
        elif similarity_score >= 0.85:
            return "medium"
        elif similarity_score >= 0.80:
            return "low"
        else:
            return "very_low"


# Global violation detector instance
violation_detector = ViolationDetector()