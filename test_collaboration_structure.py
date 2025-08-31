#!/usr/bin/env python3
"""
Simple test to verify collaboration agents exist and have proper structure

This bypasses import issues by directly checking file structure and basic functionality.
"""

import os
import importlib.util

def load_module_from_file(module_name, file_path):
    """Load a module directly from file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_agent_structure(agent_name):
    """Test if an agent has proper structure"""
    base_path = f"/home/runner/work/Ainflue/Ainflue/ai_agents/{agent_name}"
    
    # Check required files exist
    required_files = [
        f"{base_path}/__init__.py",
        f"{base_path}/manager.py",
        f"{base_path}/core",
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            return False, f"Missing {file_path}"
    
    try:
        # Try to load the manager module
        manager_path = f"{base_path}/manager.py"
        manager_module = load_module_from_file(f"{agent_name}_manager", manager_path)
        
        # Look for a manager class
        manager_class_name = ''.join(word.capitalize() for word in agent_name.split('_')) + 'Manager'
        if hasattr(manager_module, manager_class_name):
            return True, f"Found {manager_class_name}"
        else:
            return False, f"Missing {manager_class_name} class"
            
    except Exception as e:
        return False, f"Import error: {str(e)[:50]}"

def main():
    """Test all collaboration agents"""
    collaboration_agents = [
        ('collaboration_agent', 'IA matching avancé'),
        ('marketplace_agent', 'Place de marché complète'),
        ('project_management_agent', 'Gestion projets IA'),
        ('communication_agent', 'Chat/video intégré'),
        ('file_sharing_agent', 'Partage sécurisé'),
        ('version_control_agent', 'Git-like pour créatifs'),
        ('quality_assurance_agent', 'QA automatisée'),
        ('contract_generation_agent', 'Contrats intelligents'),
        ('dispute_resolution_agent', 'Résolution IA'),
        ('skill_matching_agent', 'Compétences matching'),
        ('timeline_management_agent', 'Planning optimal'),
        ('revenue_sharing_agent', 'Partage équitable')
    ]
    
    print("COLLABORATION AGENTS STRUCTURE TEST")
    print("=" * 50)
    
    success_count = 0
    
    for i, (agent_name, description) in enumerate(collaboration_agents, 1):
        success, message = test_agent_structure(agent_name)
        status = "✓" if success else "✗"
        
        print(f"{i:2d}. {status} {agent_name}")
        print(f"     {description}")
        print(f"     {message}")
        print()
        
        if success:
            success_count += 1
    
    print("=" * 50)
    print(f"RESULT: {success_count}/{len(collaboration_agents)} agents have proper structure")
    
    return success_count == len(collaboration_agents)

if __name__ == "__main__":
    main()