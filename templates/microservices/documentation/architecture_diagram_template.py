#!/usr/bin/env python3
"""Architecture Diagram Template - System architecture documentation"""

class ArchitectureDiagramTemplate:
    """Architecture diagram generator"""
    
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.components = []
        self.connections = []
    
    def add_component(self, name: str, component_type: str, description: str):
        """Add system component"""
        self.components.append({
            "name": name,
            "type": component_type,
            "description": description
        })
    
    def add_connection(self, from_component: str, to_component: str, protocol: str):
        """Add connection between components"""
        self.connections.append({
            "from": from_component,
            "to": to_component,
            "protocol": protocol
        })
    
    def generate_mermaid_diagram(self) -> str:
        """Generate Mermaid diagram syntax"""
        diagram = "graph TD\n"
        
        for component in self.components:
            diagram += f"    {component['name']}[{component['name']}]\n"
        
        for connection in self.connections:
            diagram += f"    {connection['from']} --> {connection['to']}\n"
        
        return diagram