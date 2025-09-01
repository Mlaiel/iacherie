#!/usr/bin/env python3
"""AI Agents Inventory Script
Comprehensive analysis of all implemented agents in the Ainflue platform

Author: GitHub Copilot Analysis
Purpose: CRITIQUE - AGENTS IA verification
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class AgentInfo:
    """
Information about an implemented agent"""
    name: str
    file_path: str
    directory: str
    class_name: str
    methods: List[str]
    line_count: int
    has_init: bool
    has_async_methods: bool
    imports: List[str]
    dependencies: List[str]
    implementation_quality: str  # "complete", "partial", "skeleton"

class AgentInventoryAnalyzer:
    """Analyzes all agent implementations in the repository"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.agents: Dict[str, AgentInfo] = {}
        self.target_agents = [
            "ContentStrategistAgent",
            "CollaborationMatcherAgent", 
            "ImageSpecialistAgent",
            "AudienceDeveloperAgent",
            "MusicProducerAgent"
        ]
        
    def analyze_all_agents(self) -> Dict[str, Any]:
        """Perform comprehensive analysis of all agents"""
        print("🔍 Starting comprehensive AI agents inventory...")
        
        # Scan both agent directories
        self._scan_directory(self.repo_path / "ai_engine" / "ai_agents")
        self._scan_directory(self.repo_path / "ai_agents")
        
        # Analyze findings
        results = {
            "scan_timestamp": datetime.now().isoformat(),
            "total_agents_found": len(self.agents),
            "target_agents_status": self._check_target_agents(),
            "agents_by_quality": self._categorize_by_quality(),
            "detailed_agents": {name: asdict(info) for name, info in self.agents.items()},
            "summary": self._generate_summary()
        }
        
        return results
        
    def _scan_directory(self, directory: Path):
        """Scan a directory for agent implementations"""
        if not directory.exists():
            print(f"⚠️  Directory not found: {directory}")
            return
            
        print(f"📂 Scanning directory: {directory}")
        
        for py_file in directory.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue
                
            try:
                self._analyze_python_file(py_file)
            except Exception as e:
                print(f"❌ Error analyzing {py_file}: {e}")
                
    def _analyze_python_file(self, file_path: Path):
        """Analyze a Python file for agent classes"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content)
            
            # Find agent classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                    agent_info = self._extract_agent_info(node, file_path, content)
                    if agent_info:
                        self.agents[agent_info.name] = agent_info
                        
        except Exception as e:
            print(f"⚠️  Could not parse {file_path}: {e}")
            
    def _extract_agent_info(self, class_node: ast.ClassDef, file_path: Path, content: str) -> AgentInfo:
        """Extract detailed information about an agent class"""
        
        # Get methods
        methods = []
        has_init = False
        has_async_methods = False
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                methods.append(node.name)
                if node.name == "__init__":
                    has_init = True
            elif isinstance(node, ast.AsyncFunctionDef):
                methods.append(f"async {node.name}")
                has_async_methods = True
                
        # Count lines (approximation)
        lines = content.split('\n')
        class_start = class_node.lineno - 1
        line_count = 0
        indent_level = None
        
        for i in range(class_start, len(lines)):
            line = lines[i]
            if line.strip():
                if indent_level is None and line.startswith('class'):
                    indent_level = len(line) - len(line.lstrip())
                elif indent_level is not None:
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= indent_level and line.strip() and not line.lstrip().startswith(('"""', "'''", '#')):
                        break
                line_count += 1
                
        # Extract imports
        imports = self._extract_imports(content)
        
        # Assess implementation quality
        quality = self._assess_implementation_quality(methods, line_count, content)
        
        return AgentInfo(
            name=class_node.name,
            file_path=str(file_path.relative_to(self.repo_path)),
            directory=str(file_path.parent.relative_to(self.repo_path)),
            class_name=class_node.name,
            methods=methods,
            line_count=line_count,
            has_init=has_init,
            has_async_methods=has_async_methods,
            imports=imports,
            dependencies=self._extract_dependencies(imports),
            implementation_quality=quality
        )
        
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from file content"""
        imports = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith(('import ', 'from ')):
                imports.append(line)
        return imports[:10]  # Limit to first 10 imports
        
    def _extract_dependencies(self, imports: List[str]) -> List[str]:
        """
Extract dependencies from imports"""
        dependencies = []
        for imp in imports:
            if 'agent' in imp.lower() or 'base' in imp.lower():
                dependencies.append(imp)
        return dependencies
        
    def _assess_implementation_quality(self, methods: List[str], line_count: int, content: str) -> str:
        """
Assess the quality/completeness of implementation"""
        
        # Count substantive methods (not just __init__, __str__, etc.)
        substantive_methods = [m for m in methods if not m.startswith('__') or m == '__init__']
        
        # Check for common patterns indicating real implementation
        has_docstrings = '"""' in content or "'''" in content
        has_logging = 'logging' in content.lower() or 'logger' in content.lower()
        has_error_handling = 'try:' in content or 'except' in content
        has_async_patterns = 'await' in content or 'async def' in content
        
        quality_score = 0
        
        # Line count scoring
        if line_count > 200:
            quality_score += 3
        elif line_count > 100:
            quality_score += 2
        elif line_count > 50:
            quality_score += 1
            
        # Method count scoring
        if len(substantive_methods) > 10:
            quality_score += 3
        elif len(substantive_methods) > 5:
            quality_score += 2
        elif len(substantive_methods) > 2:
            quality_score += 1
            
        # Implementation patterns scoring
        if has_docstrings:
            quality_score += 1
        if has_logging:
            quality_score += 1
        if has_error_handling:
            quality_score += 1
        if has_async_patterns:
            quality_score += 1
            
        # Determine quality level
        if quality_score >= 7:
            return "complete"
        elif quality_score >= 4:
            return "partial"
        else:
            return "skeleton"
            
    def _check_target_agents(self) -> Dict[str, Any]:
        """Check status of the 5 target agents"""
        target_status = {}
        
        for target in self.target_agents:
            if target in self.agents:
                agent = self.agents[target]
                target_status[target] = {
                    "found": True,
                    "file_path": agent.file_path,
                    "implementation_quality": agent.implementation_quality,
                    "line_count": agent.line_count,
                    "method_count": len(agent.methods),
                    "has_async": agent.has_async_methods
                }
            else:
                target_status[target] = {
                    "found": False,
                    "status": "NOT IMPLEMENTED"
                }
                
        return target_status
        
    def _categorize_by_quality(self) -> Dict[str, List[str]]:
        """Categorize agents by implementation quality"""
        categories = {
            "complete": [],
            "partial": [],
            "skeleton": []
        }
        
        for name, agent in self.agents.items():
            categories[agent.implementation_quality].append(name)
            
        return categories
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        total = len(self.agents)
        
        if total == 0:
            return {"error": "No agents found"}
            
        quality_counts = {quality: 0 for quality in ["complete", "partial", "skeleton"]}
        async_count = 0
        total_lines = 0
        
        for agent in self.agents.values():
            quality_counts[agent.implementation_quality] += 1
            if agent.has_async_methods:
                async_count += 1
            total_lines += agent.line_count
            
        return {
            "total_agents": total,
            "complete_implementations": quality_counts["complete"],
            "partial_implementations": quality_counts["partial"], 
            "skeleton_implementations": quality_counts["skeleton"],
            "agents_with_async": async_count,
            "average_lines_per_agent": round(total_lines / total, 1),
            "completion_rate": f"{round((quality_counts['complete'] / total) * 100, 1)}%"
        }

def main():
    """Main execution function"""
    repo_path = "/home/runner/work/Ainflue/Ainflue"
    
    analyzer = AgentInventoryAnalyzer(repo_path)
    results = analyzer.analyze_all_agents()
    
    # Save results
    output_file = Path(repo_path) / "AGENTS_INVENTORY_ANALYSIS.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    # Print summary
    print("\n" + "="*60)
    print("🤖 AI AGENTS INVENTORY SUMMARY")
    print("="*60)
    
    summary = results["summary"]
    if "error" not in summary:
        print(f"📊 Total Agents Found: {summary['total_agents']}")
        print(f"✅ Complete Implementations: {summary['complete_implementations']}")
        print(f"🔄 Partial Implementations: {summary['partial_implementations']}")
        print(f"💀 Skeleton Implementations: {summary['skeleton_implementations']}")
        print(f"⚡ Agents with Async Methods: {summary['agents_with_async']}")
        print(f"📏 Average Lines per Agent: {summary['average_lines_per_agent']}")
        print(f"📈 Completion Rate: {summary['completion_rate']}")
    
    print("\n🎯 TARGET AGENTS STATUS:")
    for agent_name, status in results["target_agents_status"].items():
        if status["found"]:
            print(f"✅ {agent_name}: {status['implementation_quality'].upper()} ({status['line_count']} lines)")
        else:
            print(f"❌ {agent_name}: NOT FOUND")
            
    print(f"\n📄 Detailed report saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    main()