"""Simple Agents Module
Basic AI agent implementations for content processing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from abc import ABC, abstractmethod
import hashlib
import json

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.initialized = False
        self.stats = {
            "requests_processed": 0,
            "success_count": 0,
            "error_count": 0,
            "last_request_time": None
        }
    
    async def initialize(self):
        """Initialize the agent."""
        logger.info(f"Initializing agent: {self.name} v{self.version}")
        self.initialized = True
    
    @abstractmethod
    async def process(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Process data through the agent."""
        pass
    
    def update_stats(self, success: bool = True):
        """Update agent statistics."""
        self.stats["requests_processed"] += 1
        self.stats["last_request_time"] = datetime.utcnow().isoformat()
        if success:
            self.stats["success_count"] += 1
        else:
            self.stats["error_count"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self.initialized,
            "stats": self.stats.copy()
        }


class BasicAgent(BaseAgent):
    """Basic multi-purpose agent."""
    
    def __init__(self):
        super().__init__("BasicAgent", "1.0.0")
    
    async def process(self, data: Any, operation: str = "analyze", **kwargs) -> Dict[str, Any]:
        """Process data with basic operations."""
        if not self.initialized:
            await self.initialize()
        
        try:
            if operation == "analyze":
                result = await self._analyze_content(data, **kwargs)
            elif operation == "classify":
                result = await self._classify_content(data, **kwargs)
            elif operation == "extract":
                result = await self._extract_features(data, **kwargs)
            else:
                result = {"error": f"Unknown operation: {operation}"}
            
            self.update_stats(success=True)
            return {
                "agent": self.name,
                "operation": operation,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.update_stats(success=False)
            logger.error(f"Error in {self.name}: {e}")
            return {
                "agent": self.name,
                "operation": operation,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _analyze_content(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Analyze content."""
        await asyncio.sleep(0.1)  # Simulate processing
        
        # Basic content analysis
        content_size = len(str(data)) if data else 0
        content_type = type(data).__name__
        
        return {
            "content_size": content_size,
            "content_type": content_type,
            "complexity_score": min(content_size / 1000, 10.0),
            "analysis_confidence": 0.85
        }
    
    async def _classify_content(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Classify content."""
        await asyncio.sleep(0.1)  # Simulate processing
        
        # Basic classification based on content characteristics
        if isinstance(data, str):
            if len(data) < 100:
                category = "short_text"
            elif len(data) < 1000:
                category = "medium_text"
            else:
                category = "long_text"
        elif isinstance(data, bytes):
            category = "binary_data"
        elif isinstance(data, dict):
            category = "structured_data"
        else:
            category = "unknown"
        
        return {
            "category": category,
            "confidence": 0.9,
            "subcategories": []
        }
    
    async def _extract_features(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Extract features from content."""
        await asyncio.sleep(0.1)  # Simulate processing
        
        features = {}
        
        if isinstance(data, str):
            features.update({
                "length": len(data),
                "word_count": len(data.split()) if data else 0,
                "has_uppercase": any(c.isupper() for c in data),
                "has_numbers": any(c.isdigit() for c in data),
                "hash": hashlib.md5(data.encode()).hexdigest()[:8]
            })
        elif isinstance(data, bytes):
            features.update({
                "size": len(data),
                "hash": hashlib.md5(data).hexdigest()[:8]
            })
        
        return features


class ContentProtectionAgent(BaseAgent):
    """Agent specialized in content protection."""
    
    def __init__(self):
        super().__init__("ContentProtectionAgent", "1.0.0")
    
    async def process(self, data: Any, protection_type: str = "fingerprint", **kwargs) -> Dict[str, Any]:
        """Process content for protection."""
        if not self.initialized:
            await self.initialize()
        
        try:
            if protection_type == "fingerprint":
                result = await self._generate_fingerprint(data, **kwargs)
            elif protection_type == "watermark":
                result = await self._apply_watermark(data, **kwargs)
            elif protection_type == "detect_violations":
                result = await self._detect_violations(data, **kwargs)
            else:
                result = {"error": f"Unknown protection type: {protection_type}"}
            
            self.update_stats(success=True)
            return {
                "agent": self.name,
                "protection_type": protection_type,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.update_stats(success=False)
            logger.error(f"Error in {self.name}: {e}")
            return {
                "agent": self.name,
                "protection_type": protection_type,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _generate_fingerprint(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Generate content fingerprint."""
        await asyncio.sleep(0.2)  # Simulate processing
        
        if isinstance(data, (str, bytes)):
            if isinstance(data, str):
                data = data.encode()
            
            # Generate multiple hash-based fingerprints
            md5_hash = hashlib.md5(data).hexdigest()
            sha256_hash = hashlib.sha256(data).hexdigest()
            
            return {
                "fingerprint_id": md5_hash[:16],
                "full_hash": sha256_hash,
                "algorithm": "hash_based",
                "confidence": 1.0,
                "generated_at": datetime.utcnow().isoformat()
            }
        
        return {"error": "Unsupported data type for fingerprinting"}
    
    async def _apply_watermark(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Apply watermark to content."""
        await asyncio.sleep(0.1)  # Simulate processing
        
        watermark_id = f"wm_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "watermark_applied": True,
            "watermark_id": watermark_id,
            "method": "digital_signature",
            "strength": "medium",
            "applied_at": datetime.utcnow().isoformat()
        }
    
    async def _detect_violations(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Detect content violations."""
        await asyncio.sleep(0.3)  # Simulate processing
        
        # Mock violation detection
        violations = []
        
        # Simple checks for demonstration
        if isinstance(data, str):
            if "copyright" in data.lower():
                violations.append({
                    "type": "copyright_mention",
                    "severity": "low",
                    "confidence": 0.7
                })
            if "pirated" in data.lower() or "illegal" in data.lower():
                violations.append({
                    "type": "illegal_content",
                    "severity": "high",
                    "confidence": 0.9
                })
        
        return {
            "violations_found": len(violations),
            "violations": violations,
            "scan_confidence": 0.85,
            "scanned_at": datetime.utcnow().isoformat()
        }


class MetadataAgent(BaseAgent):
    """Agent specialized in metadata extraction and enhancement."""
    
    def __init__(self):
        super().__init__("MetadataAgent", "1.0.0")
    
    async def process(self, data: Any, metadata_type: str = "extract", **kwargs) -> Dict[str, Any]:
        """Process metadata operations."""
        if not self.initialized:
            await self.initialize()
        
        try:
            if metadata_type == "extract":
                result = await self._extract_metadata(data, **kwargs)
            elif metadata_type == "enhance":
                result = await self._enhance_metadata(data, **kwargs)
            elif metadata_type == "validate":
                result = await self._validate_metadata(data, **kwargs)
            else:
                result = {"error": f"Unknown metadata type: {metadata_type}"}
            
            self.update_stats(success=True)
            return {
                "agent": self.name,
                "metadata_type": metadata_type,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.update_stats(success=False)
            logger.error(f"Error in {self.name}: {e}")
            return {
                "agent": self.name,
                "metadata_type": metadata_type,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _extract_metadata(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Extract metadata from content."""
        await asyncio.sleep(0.1)  # Simulate processing
        
        metadata = {
            "extraction_time": datetime.utcnow().isoformat(),
            "data_type": type(data).__name__,
            "extraction_method": "basic_analysis"
        }
        
        if isinstance(data, str):
            metadata.update({
                "char_count": len(data),
                "word_count": len(data.split()) if data else 0,
                "line_count": data.count('\n') + 1 if data else 0,
                "language_hints": self._detect_language_hints(data)
            })
        elif isinstance(data, bytes):
            metadata.update({
                "byte_size": len(data),
                "estimated_format": self._guess_format(data)
            })
        elif isinstance(data, dict):
            metadata.update({
                "key_count": len(data),
                "keys": list(data.keys()) if len(data) < 20 else list(data.keys())[:20]
            })
        
        return metadata
    
    async def _enhance_metadata(self, data: Any, existing_metadata: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Enhance existing metadata."""
        await asyncio.sleep(0.1)  # Simulate processing
        
        base_metadata = existing_metadata or {}
        
        # Add enhancement information
        enhanced = base_metadata.copy()
        enhanced.update({
            "enhanced_at": datetime.utcnow().isoformat(),
            "enhancement_version": self.version,
            "quality_score": self._calculate_quality_score(data),
            "tags": self._generate_tags(data),
            "processing_flags": {
                "needs_review": False,
                "high_quality": True,
                "complete": True
            }
        })
        
        return enhanced
    
    async def _validate_metadata(self, metadata: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Validate metadata completeness and accuracy."""
        await asyncio.sleep(0.1)  # Simulate processing
        
        required_fields = ["data_type", "extraction_time"]
        missing_fields = [field for field in required_fields if field not in metadata]
        
        validation_result = {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "field_count": len(metadata),
            "validation_time": datetime.utcnow().isoformat(),
            "suggestions": []
        }
        
        if missing_fields:
            validation_result["suggestions"].append("Add missing required fields")
        
        return validation_result
    
    def _detect_language_hints(self, text: str) -> List[str]:
        """Detect language hints in text."""
        hints = []
        if any(char in text for char in "àáâãäåæçèéêëìíîïñòóôõöøùúûüý"):
            hints.append("romance_language")
        if any(char in text for char in "äöüß"):
            hints.append("german")
        if any(char in text for char in "ñ¿¡"):
            hints.append("spanish")
        return hints
    
    def _guess_format(self, data: bytes) -> str:
        """Guess file format from binary data."""
        if len(data) < 4:
            return "unknown"
        
        header = data[:4]
        if header.startswith(b'\xff\xd8\xff'):
            return "jpeg"
        elif header.startswith(b'\x89PNG'):
            return "png"
        elif header.startswith(b'GIF8'):
            return "gif"
        elif header.startswith(b'%PDF'):
            return "pdf"
        else:
            return "binary"
    
    def _calculate_quality_score(self, data: Any) -> float:
        """Calculate content quality score."""
        if isinstance(data, str):
            if len(data) < 10:
                return 3.0
            elif len(data) < 100:
                return 6.0
            else:
                return 8.5
        elif isinstance(data, bytes):
            if len(data) < 1024:
                return 5.0
            else:
                return 7.5
        return 6.0
    
    def _generate_tags(self, data: Any) -> List[str]:
        """Generate content tags."""
        tags = []
        
        if isinstance(data, str):
            tags.append("text_content")
            if len(data) > 1000:
                tags.append("long_form")
            else:
                tags.append("short_form")
        elif isinstance(data, bytes):
            tags.append("binary_content")
            if len(data) > 1024 * 1024:  # 1MB
                tags.append("large_file")
        
        tags.append("processed")
        return tags


# Agent manager class
class SimpleAgentManager:
    """Manager for simple agents."""
    
    def __init__(self):
        self.agents = {}
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize default agents."""
        self.agents = {
            "basic": BasicAgent(),
            "protection": ContentProtectionAgent(),
            "metadata": MetadataAgent()
        }
    
    async def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get agent by name."""
        agent = self.agents.get(agent_name)
        if agent and not agent.initialized:
            await agent.initialize()
        return agent
    
    async def process_with_agent(self, agent_name: str, data: Any, **kwargs) -> Dict[str, Any]:
        """Process data with specified agent."""
        agent = await self.get_agent(agent_name)
        if not agent:
            return {"error": f"Agent '{agent_name}' not found"}
        
        return await agent.process(data, **kwargs)
    
    def list_agents(self) -> List[str]:
        """List available agents."""
        return list(self.agents.keys())
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all agents."""
        return {name: agent.get_stats() for name, agent in self.agents.items()}


# Global agent manager instance
_agent_manager = None


def get_agent_manager() -> SimpleAgentManager:
    """Get global agent manager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = SimpleAgentManager()
    return _agent_manager


# Convenience functions
async def process_basic(data: Any, operation: str = "analyze", **kwargs) -> Dict[str, Any]:
    """Process data with basic agent."""
    manager = get_agent_manager()
    return await manager.process_with_agent("basic", data, operation=operation, **kwargs)


async def protect_content(data: Any, protection_type: str = "fingerprint", **kwargs) -> Dict[str, Any]:
    """Protect content using protection agent."""
    manager = get_agent_manager()
    return await manager.process_with_agent("protection", data, protection_type=protection_type, **kwargs)


async def extract_metadata(data: Any, **kwargs) -> Dict[str, Any]:
    """Extract metadata using metadata agent."""
    manager = get_agent_manager()
    return await manager.process_with_agent("metadata", data, metadata_type="extract", **kwargs)


# Export main classes and functions
__all__ = [
    "BaseAgent",
    "BasicAgent", 
    "ContentProtectionAgent",
    "MetadataAgent",
    "SimpleAgentManager",
    "get_agent_manager",
    "process_basic",
    "protect_content",
    "extract_metadata"
]