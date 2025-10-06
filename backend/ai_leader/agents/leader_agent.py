"""
Leader Agent - Main AI orchestrator
Learns from APIs and manages fallback strategies
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..models.api_capability import APICapability, CapabilityType
from ..models.training_data import TrainingData, TrainingExample
from .fallback_manager import FallbackManager

logger = logging.getLogger(__name__)


class LeaderAgent:
    """
    AI Leader Agent that learns from external APIs
    and gradually replaces them with internal capabilities
    """
    
    def __init__(self, storage_path: str = "./backend/ai_leader/storage"):
        self.storage_path = storage_path
        self.capabilities: Dict[str, APICapability] = {}
        self.training_data: Dict[str, TrainingData] = {}
        self.fallback_manager = FallbackManager()
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing capabilities
        self._load_capabilities()

        
        logger.info("AI Leader Agent initialized")
    
    def learn_from_api_call(
        self,
        capability_type: CapabilityType,
        api_provider: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> TrainingExample:
        """
        Learn from an external API call by storing it as training data
        
        Args:
            capability_type: Type of capability being demonstrated
            api_provider: Name of external API (e.g., "OpenAI", "Anthropic")

            input_data: Input sent to API
            output_data: Response from API
            metadata: Additional info (cost, response_time, etc.)

        
        Returns:
            TrainingExample: Stored training example
        """
        
        # Create training example

        example = TrainingExample(
            input_data=input_data,
            output_data=output_data,
            api_provider=api_provider,
            capability_type=capability_type,
            timestamp=datetime.now(),
            response_time_ms=metadata.get('response_time_ms', 0),
            cost=metadata.get('cost', 0),
            success=metadata.get('success', True),
            user_rating=metadata.get('user_rating'),
            user_feedback=metadata.get('user_feedback')
        )
        
        # Add to training data
        if capability_type not in self.training_data:
            self.training_data[capability_type] = TrainingData(
                capability_type=capability_type,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )

        
        self.training_data[capability_type].add_example(example)
        
        # Update capability if exists
        if capability_type in self.capabilities:
            capability = self.capabilities[capability_type]
            capability.training_samples += 1
            capability.total_requests += 1
            if example.success:
                capability.success_rate = (
                    (capability.success_rate * (capability.total_requests - 1) + 1.0)
                    / capability.total_requests
                )
        
        # Save training data
        self._save_training_data(capability_type)

        
        logger.info(f"Learned from {api_provider} for {capability_type}")
        return example
    
    def execute_capability(
        self,
        capability_type: CapabilityType,
        input_data: Dict[str, Any],
        prefer_internal: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a capability using internal model if available,
        otherwise fallback to external API
        
        Args:
            capability_type: Type of capability to execute
            input_data: Input parameters
            prefer_internal: Try internal model first if True
        
        Returns:
            Dict containing result and metadata
        """
        
        capability = self.capabilities.get(capability_type)
        
        # Try internal model first if available and preferred
        if prefer_internal and capability and capability.can_replace_api:
            try:
                result = self._execute_internal(capability, input_data)

                result['source'] = 'internal'
                result['cost_saved'] = capability.api_cost
                logger.info(f"Used internal model for {capability_type}")

                return result
            except Exception as e:
                logger.warning(f"Internal model failed: {e}, falling back to API")
        
        # Fallback to external API
        result = self.fallback_manager.execute_with_fallback(
            capability_type,
            input_data
        )
        
        # Learn from this API call
        if result.get('success'):
            self.learn_from_api_call(
                capability_type=capability_type,
                api_provider=result.get('provider', 'unknown'),
                input_data=input_data,
                output_data=result.get('data', {}),
                metadata={
                    'cost': result.get('cost', 0),
                    'response_time_ms': result.get('response_time_ms', 0),
                    'success': True
                }
            )

        
        result['source'] = 'external'
        return result
    
    def get_autonomy_status(self) -> Dict[str, Any]:
        """
        Get current autonomy level and statistics
        
        Returns:
            Dict with autonomy metrics
        """
        
        total_capabilities = len(CapabilityType)

        trained_capabilities = sum(
            1 for c in self.capabilities.values()
 
            if c.is_trained
        )

        replaceable_capabilities = sum(
            1 for c in self.capabilities.values()
 
            if c.can_replace_api
        )


        
        total_samples = sum(
            td.total_examples 
            for td in self.training_data.values()
        )


        
        total_cost_saved = sum(
            c.api_cost * c.total_requests 
            for c in self.capabilities.values()
 
            if c.can_replace_api
        )

        
        return {
            'autonomy_level': replaceable_capabilities / total_capabilities * 100,
            'total_capabilities': total_capabilities,
            'trained_capabilities': trained_capabilities,
            'replaceable_capabilities': replaceable_capabilities,
            'training_samples': total_samples,
            'cost_saved_usd': total_cost_saved,
            'capabilities': [
                {
                    'type': c.capability_type,
                    'name': c.name,
                    'trained': c.is_trained,
                    'can_replace': c.can_replace_api,
                    'accuracy': c.accuracy,
                    'samples': c.training_samples
                }
                for c in self.capabilities.values()
            ]
        }
    
    def register_capability(self, capability: APICapability):
        """
        Register a new capability to learn"""
        self.capabilities[capability.capability_type] = capability
        self._save_capability(capability)
        logger.info(f"Registered capability: {capability.name}")
    
    def _execute_internal(
        self,
        capability: APICapability,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute using internal trained model"""
        # This would load and run the actual trained model
        # For now, return placeholder
        return {
            'success': True,
            'data': {'result': 'Internal model result (placeholder)'},
            'cost': 0,
            'response_time_ms': capability.inference_time_ms
        }
    
    def _load_capabilities(self):
        """
        Load capabilities from storage"""
        capabilities_file = os.path.join(self.storage_path, 'capabilities.json')
        if os.path.exists(capabilities_file):
            try:
                with open(capabilities_file, 'r') as f:
                    data = json.load(f)

                    for cap_data in data.get('capabilities', []):
                        cap = APICapability(**cap_data)

                        self.capabilities[cap.capability_type] = cap
                logger.info(f"Loaded {len(self.capabilities)} capabilities")

            except Exception as e:
                logger.error(f"Failed to load capabilities: {e}")
    
    def _save_capability(self, capability: APICapability):
        """Save single capability to storage"""
        capabilities_file = os.path.join(self.storage_path, 'capabilities.json')
        
        # Load existing

        capabilities_list = []
        if os.path.exists(capabilities_file):
            with open(capabilities_file, 'r') as f:
                data = json.load(f)


                capabilities_list = data.get('capabilities', [])
        
        # Update or add

        updated = False
        for i, cap in enumerate(capabilities_list):
            if cap['capability_type'] == capability.capability_type:
                capabilities_list[i] = capability.model_dump()


                updated = True
                break
        
        if not updated:
            capabilities_list.append(capability.model_dump())
        
        # Save
        with open(capabilities_file, 'w') as f:
            json.dump({'capabilities': capabilities_list}, f, indent=2, default=str)
    
    def _save_training_data(self, capability_type: str):
        """
        Save training data for a capability"""
        data_file = os.path.join(
            self.storage_path,
            f'training_data_{capability_type}.json'
        )


        
        training_data = self.training_data.get(capability_type)
        if training_data:
            with open(data_file, 'w') as f:
                json.dump(training_data.model_dump(), f, indent=2, default=str)
