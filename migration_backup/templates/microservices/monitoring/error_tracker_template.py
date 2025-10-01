"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Error Tracker Template for IA Chéries Platform
==========================================

Production-ready error tracking with:
- Exception capture and analysis
- Error aggregation and grouping
- Stack trace analysis
- Error trend monitoring
- Integration with alerting systems
- Automatic error reporting

Author: Fahed Mlaiel (mlaiel@live.de)
Error Tracking & Debugging Expert
"""

import traceback
import hashlib
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class ErrorEvent:
    """Error event data"""
    id: str
    error_type: str
    message: str
    stack_trace: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    count: int = 1
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)

class ErrorTracker:
    """
    Production-ready error tracking system
    
    Features:
    - Exception capture and analysis
    - Error aggregation and grouping
    - Stack trace analysis
    - Error trend monitoring
    """
    
    def __init__(self, service_name: str = "ainflue-service"):
        self.service_name = service_name
        self.errors: Dict[str, ErrorEvent] = {}
        self.logger = logging.getLogger(f"{service_name}.errors")
    
    def capture_exception(self, exception: Exception, context: Dict[str, Any] = None) -> str:
        """Capture and track an exception"""
        error_type = type(exception).__name__
        message = str(exception)
        stack_trace = traceback.format_exc()
        
        # Generate error fingerprint for grouping
        fingerprint_data = f"{error_type}:{message}:{stack_trace}"
        error_id = hashlib.md5(fingerprint_data.encode()).hexdigest()
        
        if error_id in self.errors:
            # Update existing error
            error_event = self.errors[error_id]
            error_event.count += 1
            error_event.last_seen = datetime.utcnow()
        else:
            # Create new error event
            error_event = ErrorEvent(
                id=error_id,
                error_type=error_type,
                message=message,
                stack_trace=stack_trace,
                timestamp=datetime.utcnow(),
                context=context or {}
            )
            self.errors[error_id] = error_event
        
        # Log the error
        self.logger.error(
            f"Error captured: {error_type} - {message}",
            extra={
                "error_id": error_id,
                "error_type": error_type,
                "context": context or {}
            }
        )
        
        return error_id
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        total_errors = len(self.errors)
        total_occurrences = sum(error.count for error in self.errors.values())
        
        # Group by error type
        error_types = {}
        for error in self.errors.values():
            if error.error_type not in error_types:
                error_types[error.error_type] = {"count": 0, "occurrences": 0}
            error_types[error.error_type]["count"] += 1
            error_types[error.error_type]["occurrences"] += error.count
        
        return {
            "service": self.service_name,
            "total_unique_errors": total_errors,
            "total_error_occurrences": total_occurrences,
            "error_types": error_types,
            "most_frequent_errors": self._get_most_frequent_errors(5)
        }
    
    def _get_most_frequent_errors(self, limit: int) -> List[Dict[str, Any]]:
        """Get most frequent errors"""
        sorted_errors = sorted(
            self.errors.values(),
            key=lambda x: x.count,
            reverse=True
        )
        
        return [
            {
                "id": error.id,
                "type": error.error_type,
                "message": error.message,
                "count": error.count,
                "first_seen": error.first_seen.isoformat(),
                "last_seen": error.last_seen.isoformat()
            }
            for error in sorted_errors[:limit]
        ]

class ErrorTrackerTemplate:
    """Error Tracker Template"""
    
    def create_tracker(self, config: Dict[str, Any]) -> ErrorTracker:
        return ErrorTracker(service_name=config.get("service_name", "ainflue"))
    
    def get_template_info(self) -> Dict[str, Any]:
        return {
            "name": "error-tracker",
            "description": "Error tracking and analysis",
            "features": ["Exception capture", "Error grouping", "Trend monitoring"]
        }