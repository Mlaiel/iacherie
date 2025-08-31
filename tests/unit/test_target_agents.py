# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""Quick verification test for the 5 target agents
Tests that they can be imported and instantiated correctly
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from ai_engine.ai_agents.base_agent import AgentConfiguration, AgentCapability

def test_agent_imports():
    """Test that all target agents can be imported"""    results = {}
    
    # Test ContentStrategistAgent
    try:
        from ai_engine.ai_agents.content_strategy_agents import ContentStrategistAgent
        results['ContentStrategistAgent'] = {'import': True, 'error': None}
    except Exception as e:
        results['ContentStrategistAgent'] = {'import': False, 'error': str(e)}
    
    # Test CollaborationMatcherAgent
    try:
        from ai_engine.ai_agents.collaboration_agents import CollaborationMatcherAgent
        results['CollaborationMatcherAgent'] = {'import': True, 'error': None}
    except Exception as e:
        results['CollaborationMatcherAgent'] = {'import': False, 'error': str(e)}
    
    # Test ImageSpecialistAgent
    try:
        from ai_engine.ai_agents.image_specialist import ImageSpecialistAgent
        results['ImageSpecialistAgent'] = {'import': True, 'error': None}
    except Exception as e:
        results['ImageSpecialistAgent'] = {'import': False, 'error': str(e)}
    
    # Test AudienceDeveloperAgent
    try:
        from ai_engine.ai_agents.audience_development_agents import AudienceDeveloperAgent
        results['AudienceDeveloperAgent'] = {'import': True, 'error': None}
    except Exception as e:
        results['AudienceDeveloperAgent'] = {'import': False, 'error': str(e)}
    
    # Test MusicProducerAgent
    try:
        from ai_engine.ai_agents.music_producer import MusicProducerAgent
        results['MusicProducerAgent'] = {'import': True, 'error': None}
    except Exception as e:
        results['MusicProducerAgent'] = {'import': False, 'error': str(e)}
    
    return results

def test_agent_instantiation():
    """Test that agents can be instantiated"""    results = {}
    
    # Create a basic config
    config = AgentConfiguration(
        agent_id="test_agent",
        agent_name="Test Agent",
        capabilities={AgentCapability.PERFORMANCE_ANALYSIS}
    )
    
    # Test each agent
    agents_to_test = [
        ('ContentStrategistAgent', 'ai_engine.ai_agents.content_strategy_agents'),
        ('CollaborationMatcherAgent', 'ai_engine.ai_agents.collaboration_agents'),
        ('ImageSpecialistAgent', 'ai_engine.ai_agents.image_specialist'),
        ('AudienceDeveloperAgent', 'ai_engine.ai_agents.audience_development_agents'),
        ('MusicProducerAgent', 'ai_engine.ai_agents.music_producer')
    ]
    
    for agent_name, module_path in agents_to_test:
        try:
            module = __import__(module_path, fromlist=[agent_name])
            agent_class = getattr(module, agent_name)
            
            # Try to instantiate
            agent = agent_class(config)
            results[agent_name] = {
                'instantiate': True, 
                'has_init': hasattr(agent, '__init__'),
                'has_name': hasattr(agent, 'name'),
                'error': None
            }
        except Exception as e:
            results[agent_name] = {'instantiate': False, 'error': str(e)}
    
    return results

def main():
    print("🧪 Testing Target AI Agents Implementation...")
    print("=" * 60)
    
    # Test imports
    print("\n📦 Testing Imports:")
    import_results = test_agent_imports()
    for agent, result in import_results.items():
        status = "✅ PASS" if result['import'] else "❌ FAIL"
        print(f"  {status} {agent}")
        if not result['import']:
            print(f"      Error: {result['error']}")
    
    # Test instantiation
    print("\n🏗️  Testing Instantiation:")
    instance_results = test_agent_instantiation()
    for agent, result in instance_results.items():
        if 'instantiate' in result:
            status = "✅ PASS" if result['instantiate'] else "❌ FAIL"
            print(f"  {status} {agent}")
            if not result['instantiate']:
                print(f"      Error: {result['error']}")
        else:
            print(f"  ⚠️  SKIP {agent} (import failed)")
    
    # Summary
    import_count = sum(1 for r in import_results.values() if r['import'])
    instance_count = sum(1 for r in instance_results.values() if r.get('instantiate', False))
    
    print(f"\n📊 Summary:")
    print(f"  Imports Successful: {import_count}/5")
    print(f"  Instantiation Successful: {instance_count}/5")
    
    if import_count == 5 and instance_count == 5:
        print("  🎉 ALL TARGET AGENTS VERIFIED!")
        return True
    else:
        print("  ⚠️  Some agents have issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)