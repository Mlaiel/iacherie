#!/usr/bin/env python3
"""🔴 CRITIQUE - AGENTS IA
Vérification implémentation réelle des agents trouvés

Script pour inventorier TOUS les agents réellement implémentés
et vérifier l'état des 5 agents critiques demandés.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import os
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
    """Information about an agent implementation"""    name: str
    file_path: str
    class_name: str
    line_count: int
    method_count: int
    import_status: str
    is_complete: bool
    methods: List[str]
    parent_class: str = ""
    description: str = ""

class AgentsInventory:
    """Complete inventory and verification of AI agents"""    
    def __init__(self):
        self.target_agents = [
            "ContentStrategistAgent",
            "CollaborationMatcherAgent", 
            "ImageSpecialistAgent",
            "AudienceDeveloperAgent",
            "MusicProducerAgent"
        ]
        self.all_agents = {}
        self.agent_files = []
        
    def find_agent_files(self) -> List[str]:
        """Find all Python files containing agents"""        agent_files = []
        
        # Search in ai_engine/ai_agents
        ai_agents_dir = Path("ai_engine/ai_agents")
        if ai_agents_dir.exists():
            for file in ai_agents_dir.glob("*.py"):
                if file.name != "__init__.py":
                    agent_files.append(str(file))
                    
        # Search in ai_agents directory
        ai_agents_legacy = Path("ai_agents")
        if ai_agents_legacy.exists():
            for subdir in ai_agents_legacy.iterdir():
                if subdir.is_dir():
                    for file in subdir.rglob("*.py"):
                        if "agent" in file.name.lower():
                            agent_files.append(str(file))
                            
        return agent_files
    
    def analyze_file(self, file_path: str) -> List[AgentInfo]:
        """Analyze a Python file for agent classes"""        agents = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST to find classes
            tree = ast.parse(content)
            lines = content.split('\n')
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    
                    # Check if it's an agent class
                    if "Agent" in class_name:
                        # Count methods
                        methods = []
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                methods.append(item.name)
                        
                        # Get parent class
                        parent_class = ""
                        if node.bases:
                            for base in node.bases:
                                if isinstance(base, ast.Name):
                                    parent_class = base.id
                                elif isinstance(base, ast.Attribute):
                                    parent_class = base.attr
                        
                        # Count lines for this class
                        start_line = node.lineno - 1
                        end_line = len(lines)
                        for next_node in tree.body:
                            if (isinstance(next_node, ast.ClassDef) and 
                                next_node.lineno > node.lineno):
                                end_line = next_node.lineno - 1
                                break
                        
                        line_count = end_line - start_line
                        
                        # Test import
                        import_status = self.test_import(file_path, class_name)
                        
                        agent_info = AgentInfo(
                            name=class_name,
                            file_path=file_path,
                            class_name=class_name,
                            line_count=line_count,
                            method_count=len(methods),
                            import_status=import_status,
                            is_complete=len(methods) > 5,  # Heuristic for completeness
                            methods=methods,
                            parent_class=parent_class
                        )
                        
                        agents.append(agent_info)
                        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return agents
    
    def test_import(self, file_path: str, class_name: str) -> str:
        """Test if agent class can be imported"""        try:
            # Convert file path to module path
            module_path = file_path.replace('/', '.').replace('.py', '')
            module = importlib.import_module(module_path)
            
            if hasattr(module, class_name):
                return "✅ SUCCESS"
            else:
                return "❌ CLASS_NOT_FOUND"
                
        except ImportError as e:
            return f"❌ IMPORT_ERROR: {str(e)[:50]}..."
        except Exception as e:
            return f"❌ ERROR: {str(e)[:50]}..."
    
    def run_inventory(self) -> Dict[str, Any]:
        """Run complete inventory of all agents"""        print("🔍 Scanning for AI agents...")
        
        # Find all agent files
        self.agent_files = self.find_agent_files()
        print(f"Found {len(self.agent_files)} potential agent files")
        
        # Analyze each file
        all_agents = []
        for file_path in self.agent_files:
            print(f"📄 Analyzing: {file_path}")
            agents = self.analyze_file(file_path)
            all_agents.extend(agents)
        
        # Organize results
        target_results = {}
        other_agents = []
        
        for agent in all_agents:
            if agent.name in self.target_agents:
                target_results[agent.name] = agent
            else:
                other_agents.append(agent)
        
        # Create summary
        summary = {
            "target_agents": target_results,
            "other_agents": other_agents,
            "total_agents": len(all_agents),
            "target_found": len(target_results),
            "target_success_rate": len(target_results) / len(self.target_agents) * 100,
            "scan_timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def generate_report(self, summary: Dict[str, Any]) -> str:
        """Generate detailed verification report"""        report = []
        report.append("# 🔴 CRITIQUE - AGENTS IA")
        report.append("## Vérification implémentation réelle des agents trouvés")
        report.append("")
        report.append(f"**Date de vérification**: {summary['scan_timestamp']}")
        report.append("")
        
        # Target agents analysis
        report.append("## 🎯 AGENTS CRITIQUES DEMANDÉS")
        report.append("")
        report.append("| Agent | Statut | Fichier | Lignes | Méthodes | Import |")
        report.append("|-------|--------|---------|--------|----------|--------|")
        
        for agent_name in self.target_agents:
            if agent_name in summary["target_agents"]:
                agent = summary["target_agents"][agent_name]
                status = "✅ TROUVÉ"
                file_name = Path(agent.file_path).name
                lines = agent.line_count
                methods = agent.method_count
                import_status = agent.import_status.split(':')[0]
                
                report.append(f"| **{agent_name}** | {status} | `{file_name}` | {lines} | {methods} | {import_status} |")
            else:
                report.append(f"| **{agent_name}** | ❌ NON TROUVÉ | - | - | - | - |")
        
        report.append("")
        report.append(f"**TAUX DE RÉUSSITE**: {summary['target_success_rate']:.1f}% ({summary['target_found']}/{len(self.target_agents)})")
        report.append("")
        
        # Complete inventory
        report.append("## 📊 INVENTAIRE COMPLET DES AGENTS")
        report.append("")
        report.append(f"**Total d'agents trouvés**: {summary['total_agents']}")
        report.append("")
        
        # Sort other agents by name
        other_agents = sorted(summary["other_agents"], key=lambda x: x.name)
        
        report.append("### Autres agents implémentés:")
        for i, agent in enumerate(other_agents, 1):
            status = "✅" if agent.is_complete else "⚠️"
            report.append(f"{i}. **{agent.name}** {status} ({agent.line_count} lignes, {agent.method_count} méthodes)")
        
        report.append("")
        
        # Detailed analysis of target agents
        report.append("## 🔍 ANALYSE DÉTAILLÉE DES AGENTS CRITIQUES")
        report.append("")
        
        for agent_name in self.target_agents:
            if agent_name in summary["target_agents"]:
                agent = summary["target_agents"][agent_name]
                report.append(f"### {agent_name}")
                report.append("")
                report.append(f"- **Fichier**: `{agent.file_path}`")
                report.append(f"- **Classe parente**: {agent.parent_class}")
                report.append(f"- **Lignes de code**: {agent.line_count}")
                report.append(f"- **Nombre de méthodes**: {agent.method_count}")
                report.append(f"- **Statut d'import**: {agent.import_status}")
                report.append(f"- **Implémentation**: {'✅ Complète' if agent.is_complete else '⚠️ Partielle'}")
                report.append("")
                report.append("**Méthodes principales**:")
                for method in agent.methods[:10]:  # Show first 10 methods
                    if not method.startswith('_'):
                        report.append(f"  - `{method}()`")
                if len(agent.methods) > 10:
                    report.append(f"  - ... et {len(agent.methods) - 10} autres méthodes")
                report.append("")
        
        return "\n".join(report)


def main():
    """Main execution function"""    print("🤖 AGENTS IA - VÉRIFICATION D'IMPLÉMENTATION")
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