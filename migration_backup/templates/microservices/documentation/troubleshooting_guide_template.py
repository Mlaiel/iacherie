#!/usr/bin/env python3
"""Troubleshooting Guide Template - Service troubleshooting documentation"""

class TroubleshootingGuideTemplate:
    """Troubleshooting guide generator"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.issues = []
    
    def add_issue(self, symptom: str, cause: str, solution: str):
        """Add troubleshooting issue"""
        self.issues.append({
            "symptom": symptom,
            "cause": cause,
            "solution": solution
        })
    
    def generate_guide(self) -> str:
        """Generate troubleshooting guide"""
        guide = f"# {self.service_name} Troubleshooting Guide\n\n"
        
        for issue in self.issues:
            guide += f"## Issue: {issue['symptom']}\n\n"
            guide += f"**Cause:** {issue['cause']}\n\n"
            guide += f"**Solution:** {issue['solution']}\n\n"
            guide += "---\n\n"
        
        return guide