#!/usr/bin/env python3
"""API Documentation Template - Automated API documentation generation"""

from typing import Dict, List, Any

class APIDocumentationTemplate:
    """API documentation generator"""
    
    def __init__(self, service_name: str, version: str = "1.0.0"):
        self.service_name = service_name
        self.version = version
        self.endpoints: List[Dict] = []
    
    def add_endpoint(self, method: str, path: str, description: str, parameters: List[Dict] = None):
        """Add API endpoint documentation"""
        endpoint = {
            "method": method.upper(),
            "path": path,
            "description": description,
            "parameters": parameters or []
        }
        self.endpoints.append(endpoint)
    
    def generate_markdown(self) -> str:
        """Generate Markdown documentation"""
        doc = f"# {self.service_name} API Documentation\n\n"
        doc += f"Version: {self.version}\n\n"
        doc += "## Endpoints\n\n"
        
        for endpoint in self.endpoints:
            doc += f"### {endpoint['method']} {endpoint['path']}\n\n"
            doc += f"{endpoint['description']}\n\n"
            
            if endpoint['parameters']:
                doc += "**Parameters:**\n"
                for param in endpoint['parameters']:
                    doc += f"- `{param['name']}` ({param['type']}): {param['description']}\n"
                doc += "\n"
        
        return doc