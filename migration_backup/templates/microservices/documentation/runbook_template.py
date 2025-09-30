#!/usr/bin/env python3
"""Runbook Template - Operational runbooks for service management"""

class RunbookTemplate:
    """Operational runbook generator"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.procedures = []
    
    def add_procedure(self, title: str, description: str, steps: list):
        """Add operational procedure"""
        self.procedures.append({
            "title": title,
            "description": description,
            "steps": steps
        })
    
    def generate_runbook(self) -> str:
        """Generate runbook documentation"""
        runbook = f"# {self.service_name} Operational Runbook\n\n"
        
        for procedure in self.procedures:
            runbook += f"## {procedure['title']}\n\n"
            runbook += f"{procedure['description']}\n\n"
            runbook += "### Steps:\n\n"
            
            for i, step in enumerate(procedure['steps'], 1):
                runbook += f"{i}. {step}\n"
            runbook += "\n"
        
        return runbook