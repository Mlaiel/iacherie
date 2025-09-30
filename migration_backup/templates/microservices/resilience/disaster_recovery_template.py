#!/usr/bin/env python3
"""Disaster Recovery Template - Disaster recovery and backup strategies"""

import asyncio
from typing import Dict, List

class DisasterRecoveryTemplate:
    """Disaster recovery planning and execution"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.backup_locations: List[str] = []
        self.recovery_procedures: Dict[str, Callable] = {}
    
    def add_backup_location(self, location: str):
        """Add backup location"""
        self.backup_locations.append(location)
    
    def register_recovery_procedure(self, disaster_type: str, procedure: Callable):
        """Register recovery procedure for disaster type"""
        self.recovery_procedures[disaster_type] = procedure
    
    async def execute_recovery(self, disaster_type: str) -> bool:
        """Execute disaster recovery procedure"""
        procedure = self.recovery_procedures.get(disaster_type)
        
        if not procedure:
            print(f"No recovery procedure for {disaster_type}")
            return False
        
        try:
            if asyncio.iscoroutinefunction(procedure):
                await procedure()
            else:
                procedure()
            print(f"✅ Recovery completed for {disaster_type}")
            return True
        except Exception as e:
            print(f"❌ Recovery failed: {e}")
            return False