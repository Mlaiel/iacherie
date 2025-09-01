"""🏗️ Base Processor - IA Influencer Agent Platform Enterprise
============================================================
Module: backend/data_management/processors/base_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
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
    """
Processeur de base pour traitement de données"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.processing_stats = {
            "total_processed": 0,
            "total_errors": 0,
            "average_processing_time": 0.0,
            "last_processed_at": None
        }
    
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Process input data - base implementation"""
        try:
            self.logger.info(f"Processing data with {self.__class__.__name__}")
            
            # Base implementation that returns processed data structure
            # Subclasses should override this with specific processing logic
            result = {
                'status': 'processed',
                'processor': self.__class__.__name__,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'input_type': type(input_data).__name__,
                'output': input_data  # Pass-through by default
            }
            
            self.logger.info(f"Data processed successfully by {self.__class__.__name__}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in {self.__class__.__name__}.process: {str(e)}")
            return {
                'status': 'error',
                'processor': self.__class__.__name__,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data - base implementation"""
        try:
            self.logger.debug(f"Validating input data in {self.__class__.__name__}")
            
            # Basic validation - check if data is not None
            # Subclasses should override this with specific validation logic
            if input_data is None:
                self.logger.warning("Input data is None")
                return False
            
            # Basic type validation
            if isinstance(input_data, (str, dict, list, int, float, bool, bytes)):
                self.logger.debug(f"Input data validation passed for type: {type(input_data).__name__}")
                return True
            
            # Default to True for any other object types
            self.logger.debug(f"Input data validation passed for custom type: {type(input_data).__name__}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating input data: {str(e)}")
            return False
    
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
        """
Remet à zéro les statistiques"""
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
    
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Process input data asynchronously - base implementation"""
        try:
            self.logger.info(f"Async processing data with {self.__class__.__name__}")
            
            # Base async implementation that returns processed data structure
            # Subclasses should override this with specific async processing logic
            result = {
                'status': 'processed',
                'processor': self.__class__.__name__,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'input_type': type(input_data).__name__,
                'output': input_data,  # Pass-through by default
                'async': True
            }
            
            self.logger.info(f"Data processed asynchronously by {self.__class__.__name__}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in async {self.__class__.__name__}.process: {str(e)}")
            return {
                'status': 'error',
                'processor': self.__class__.__name__,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'async': True
            }
    
    async def validate_input(self, input_data: Any) -> bool:
        """Validate input data asynchronously - base implementation"""
        try:
            self.logger.debug(f"Async validating input data in {self.__class__.__name__}")
            
            # Basic async validation - check if data is not None
            # Subclasses should override this with specific async validation logic
            if input_data is None:
                self.logger.warning("Async input data is None")
                return False
            
            # Basic type validation
            if isinstance(input_data, (str, dict, list, int, float, bool, bytes)):
                self.logger.debug(f"Async input data validation passed for type: {type(input_data).__name__}")
                return True
            
            # Default to True for any other object types
            self.logger.debug(f"Async input data validation passed for custom type: {type(input_data).__name__}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in async input data validation: {str(e)}")
            return False
    
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
        """
Remet à zéro les statistiques"""
        self.processing_stats = {
            "total_processed": 0,
            "total_errors": 0,
            "average_processing_time": 0.0,
            "last_processed_at": None
        }
