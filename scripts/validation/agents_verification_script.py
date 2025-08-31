#!/usr/bin/env python3
"""🔴 CRITIQUE - AGENTS IA.

Vérification implémentation réelle des agents trouvés

Script pour inventorier TOUS les agents réellement implémentés
et vérifier l'état des 5 agents critiques demandés.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import os
import sys
import ast
import inspect
import importlib
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
from dataclasses import dataclass
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, '.')

@dataclass
class AgentInfo:
    """Information about an agent implementation."""
    print("🤖 AGENTS IA - VÉRIFICATION D'IMPLÉMENTATION")
    print("=" * 50)
    
    inventory = AgentsInventory()
    summary = inventory.run_inventory()
    
    # Generate and save report
    report = inventory.generate_report(summary)
    
    # Save to file
    with open("AGENTS_VERIFICATION_FINAL_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    # Save JSON summary
    # Convert AgentInfo objects to dicts for JSON serialization
    json_summary = summary.copy()
    json_summary["target_agents"] = {
        name: {
            "name": agent.name,
            "file_path": agent.file_path,
            "line_count": agent.line_count,
            "method_count": agent.method_count,
            "import_status": agent.import_status,
            "is_complete": agent.is_complete,
            "methods": agent.methods,
            "parent_class": agent.parent_class
        }
        for name, agent in summary["target_agents"].items()
    }
    json_summary["other_agents"] = [
        {
            "name": agent.name,
            "file_path": agent.file_path,
            "line_count": agent.line_count,
            "method_count": agent.method_count,
            "import_status": agent.import_status,
            "is_complete": agent.is_complete,
            "methods": agent.methods,
            "parent_class": agent.parent_class
        }
        for agent in summary["other_agents"]
    ]
    
    with open("agents_verification_summary.json", "w", encoding="utf-8") as f:
        json.dump(json_summary, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 50)
    print("📋 RÉSULTATS DE LA VÉRIFICATION")
    print("=" * 50)
    print(f"✅ Agents critiques trouvés: {summary['target_found']}/{len(inventory.target_agents)}")
    print(f"📊 Total d'agents: {summary['total_agents']}")
    print(f"📄 Rapport sauvé: AGENTS_VERIFICATION_FINAL_REPORT.md")
    print(f"💾 Données JSON: agents_verification_summary.json")
    
    # Print target agents status
    print("\n🎯 STATUT DES AGENTS CRITIQUES:")
    for agent_name in inventory.target_agents:
        if agent_name in summary["target_agents"]:
            agent = summary["target_agents"][agent_name]
            print(f"   ✅ {agent_name}: {agent.method_count} méthodes, {agent.line_count} lignes")
        else:
            print(f"   ❌ {agent_name}: NON TROUVÉ")


if __name__ == "__main__":
    main()