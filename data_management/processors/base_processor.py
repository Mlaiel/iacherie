"""
🏗️ Base Processor - IA Influencer Agent Platform Enterprise
============================================================
Module: backend/data_management/processors/base_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER BASE PROCESSOR:
Input Data → Validation → Processing → Feature Extraction → 
Output Generation → Quality Check → Performance Monitoring
"""

from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
import logging
import time
from datetime import datetime, timezone

class BaseProcessor(ABC):
    """Processeur de base pour traitement de données"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.processing_stats = {
            "total_processed": 0,
            "total_errors": 0,
            "average_processing_time": 0.0,
            "last_processed_at": None
        }
    
    @abstractmethod
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Process input data"""
        raise NotImplementedError("Subclasses must implement process method")
    
    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        raise NotImplementedError("Subclasses must implement validate_input method")
    
    def process_with_stats(self, input_data: Any) -> Dict[str, Any]:
        """Traite avec collection de statistiques"""
        start_time = time.time()
        
        try:
            # Validation
            if not self.validate_input(input_data):
                raise ValueError("Invalid input data")
            
            # Traitement
            result = self.process(input_data)
            
            # Mise à jour stats
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=True)
            
            result["processing_stats"] = {
                "processing_time_ms": processing_time * 1000,
                "success": True,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=False)
            
            self.logger.error(f"Processing error: {e}")
            
            return {
                "error": str(e),
                "processing_stats": {
                    "processing_time_ms": processing_time * 1000,
                    "success": False,
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }
            }
    
    def _update_stats(self, processing_time: float, success: bool):
        """Met à jour les statistiques de traitement"""
        self.processing_stats["total_processed"] += 1
        if not success:
            self.processing_stats["total_errors"] += 1
        
        # Calcul moyenne mobile
        current_avg = self.processing_stats["average_processing_time"]
        total = self.processing_stats["total_processed"]
        self.processing_stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        self.processing_stats["last_processed_at"] = datetime.now(timezone.utc).isoformat()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de traitement"""
        return self.processing_stats.copy()
    
    def reset_stats(self):
        """Remet à zéro les statistiques"""
        self.processing_stats = {
            "total_processed": 0,
            "total_errors": 0,
            "average_processing_time": 0.0,
            "last_processed_at": None
        }

class AsyncBaseProcessor(ABC):
    """Processeur de base asynchrone"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.processing_stats = {
            "total_processed": 0,
            "total_errors": 0,
            "average_processing_time": 0.0,
            "last_processed_at": None
        }
    
    @abstractmethod
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Process input data asynchronously"""
        raise NotImplementedError("Subclasses must implement process method")
    
    @abstractmethod
    async def validate_input(self, input_data: Any) -> bool:
        """Validate input data asynchronously"""
        raise NotImplementedError("Subclasses must implement validate_input method")
    
    async def process_with_stats(self, input_data: Any) -> Dict[str, Any]:
        """Traite avec collection de statistiques de manière asynchrone"""
        start_time = time.time()
        
        try:
            if not await self.validate_input(input_data):
                raise ValueError("Invalid input data")
            
            result = await self.process(input_data)
            
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=True)
            
            result["processing_stats"] = {
                "processing_time_ms": processing_time * 1000,
                "success": True,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=False)
            
            self.logger.error(f"Async processing error: {e}")
            
            return {
                "error": str(e),
                "processing_stats": {
                    "processing_time_ms": processing_time * 1000,
                    "success": False,
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }
            }
    
    def _update_stats(self, processing_time: float, success: bool):
        """Met à jour les statistiques de traitement"""
        self.processing_stats["total_processed"] += 1
        if not success:
            self.processing_stats["total_errors"] += 1
        
        current_avg = self.processing_stats["average_processing_time"]
        total = self.processing_stats["total_processed"]
        self.processing_stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        self.processing_stats["last_processed_at"] = datetime.now(timezone.utc).isoformat()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de traitement"""
        return self.processing_stats.copy()
    
    def reset_stats(self):
        """Remet à zéro les statistiques"""
        self.processing_stats = {
            "total_processed": 0,
            "total_errors": 0,
            "average_processing_time": 0.0,
            "last_processed_at": None
        }
