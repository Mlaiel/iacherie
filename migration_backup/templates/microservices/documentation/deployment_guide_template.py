#!/usr/bin/env python3
"""Deployment Guide Template - Service deployment documentation"""

class DeploymentGuideTemplate:
    """Deployment guide generator"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.environments = {}
    
    def add_environment(self, env_name: str, requirements: list, steps: list):
        """Add deployment environment"""
        self.environments[env_name] = {
            "requirements": requirements,
            "steps": steps
        }
    
    def generate_guide(self) -> str:
        """Generate deployment guide"""
        guide = f"# {self.service_name} Deployment Guide\n\n"
        
        for env_name, config in self.environments.items():
            guide += f"## {env_name} Environment\n\n"
            
            guide += "### Requirements:\n"
            for req in config['requirements']:
                guide += f"- {req}\n"
            guide += "\n"
            
            guide += "### Deployment Steps:\n"
            for i, step in enumerate(config['steps'], 1):
                guide += f"{i}. {step}\n"
            guide += "\n"
        
        return guide