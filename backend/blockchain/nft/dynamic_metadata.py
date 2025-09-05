"""Dynamic Metadata - IA-Influencer-Agent Platform

Dynamic NFT metadata system allowing real-time updates
and evolving NFT properties based on interactions.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MetadataUpdate:
    update_id: str
    token_id: str
    updated_fields: Dict[str, Any]
    updater_address: str
    update_reason: str
    updated_at: datetime
    previous_values: Dict[str, Any]

class DynamicMetadata:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metadata_updates: Dict[str, List[MetadataUpdate]] = {}
        self.current_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def update_metadata(
        self,
        token_id: str,
        updates: Dict[str, Any],
        updater_address: str,
        reason: str = "manual_update"
    ) -> MetadataUpdate:
        try:
            import uuid
            update_id = str(uuid.uuid4())
            
            # Get current metadata
            current = self.current_metadata.get(token_id, {})
            
            # Store previous values
            previous_values = {k: current.get(k) for k in updates.keys()}
            
            # Apply updates
            for key, value in updates.items():
                current[key] = value
            
            self.current_metadata[token_id] = current
            
            # Create update record
            metadata_update = MetadataUpdate(
                update_id=update_id,
                token_id=token_id,
                updated_fields=updates,
                updater_address=updater_address,
                update_reason=reason,
                updated_at=datetime.utcnow(),
                previous_values=previous_values
            )
            
            # Store update history
            if token_id not in self.metadata_updates:
                self.metadata_updates[token_id] = []
            
            self.metadata_updates[token_id].append(metadata_update)
            
            self.logger.info(f"Metadata updated for token: {token_id}")
            return metadata_update
            
        except Exception as e:
            self.logger.error(f"Metadata update failed: {e}")
            raise
    
    async def get_metadata_history(self, token_id: str) -> List[MetadataUpdate]:
        """Get complete metadata update history for token"""
        return self.metadata_updates.get(token_id, [])
    
    async def revert_metadata(
        self,
        token_id: str,
        update_id: str,
        reverter_address: str
    ) -> Optional[MetadataUpdate]:
        """Revert metadata to previous state"""
        try:
            updates = self.metadata_updates.get(token_id, [])
            target_update = None
            
            for update in updates:
                if update.update_id == update_id:
                    target_update = update
                    break
            
            if not target_update:
                raise ValueError(f"Update not found: {update_id}")
            
            # Revert to previous values
            revert_updates = target_update.previous_values
            
            return await self.update_metadata(
                token_id,
                revert_updates,
                reverter_address,
                f"revert_to_{update_id}"
            )
            
        except Exception as e:
            self.logger.error(f"Metadata revert failed: {e}")
            raise