#!/usr/bin/env python3
"""Professional File Reorganizer for AI Agents
Reorganizes ALL files into professional enterprise architecture

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Set
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProfessionalReorganizer:
    """Reorganizes files into professional enterprise structure"""    
    def __init__(self, base_path: str = "/workspaces/Ainflue/ai_agents"):
        self.base_path = Path(base_path)
        self.excluded_dirs = {'.git', '__pycache__', '.pytest_cache', 'legacy_migration'}
        self.excluded_files = {'__init__.py', 'base.py', 'index.py'}
        
    def analyze_module_files(self, module_dir: Path) -> Dict[str, List[Path]]:
        """Analyze all files in a module and categorize them"""        categories = {
            'managers': [],           # *manager.py files
            'adapters': [],          # *adapter.py files  
            'processors': [],        # *processor.py files
            'handlers': [],          # *handler.py files
            'analyzers': [],         # *analyzer.py files
            'collectors': [],        # *collector.py files
            'engines': [],           # *engine.py files
            'models': [],            # *model.py, *models.py
            'schemas': [],           # *schema.py, *schemas.py
            'configs': [],           # *config.py, *configs.py
            'utils': [],             # *util.py, *utils.py, *helper.py
            'intelligence': [],      # *intelligence.py, *ai.py, *ml.py
            'monitoring': [],        # *monitor.py, *metrics.py, *health.py
            'security': [],          # *security.py, *auth.py, *permission.py
            'storage': [],           # *storage.py, *database.py, *cache.py
            'networking': [],        # *client.py, *server.py, *api.py
            'misc': []               # Everything else
        }
        
        for file_path in module_dir.glob("*.py"):
            if file_path.name in self.excluded_files:
                continue
                
            filename = file_path.name.lower()
            
            # Categorize by filename patterns
            if re.search(r'manager\.py$', filename):
                categories['managers'].append(file_path)
            elif re.search(r'adapter\.py$', filename):
                categories['adapters'].append(file_path)
            elif re.search(r'processor\.py$', filename):
                categories['processors'].append(file_path)
            elif re.search(r'handler\.py$', filename):
                categories['handlers'].append(file_path)
            elif re.search(r'analyz[er]\.py$', filename):
                categories['analyzers'].append(file_path)
            elif re.search(r'collector\.py$', filename):
                categories['collectors'].append(file_path)
            elif re.search(r'engine\.py$', filename):
                categories['engines'].append(file_path)
            elif re.search(r'models?\.py$', filename):
                categories['models'].append(file_path)
            elif re.search(r'schemas?\.py$', filename):
                categories['schemas'].append(file_path)
            elif re.search(r'configs?\.py$', filename):
                categories['configs'].append(file_path)
            elif re.search(r'(util|utils|helper)\.py$', filename):
                categories['utils'].append(file_path)
            elif re.search(r'(intelligence|ai|ml)\.py$', filename):
                categories['intelligence'].append(file_path)
            elif re.search(r'(monitor|metrics|health)\.py$', filename):
                categories['monitoring'].append(file_path)
            elif re.search(r'(security|auth|permission)\.py$', filename):
                categories['security'].append(file_path)
            elif re.search(r'(storage|database|cache)\.py$', filename):
                categories['storage'].append(file_path)
            elif re.search(r'(client|server|api)\.py$', filename):
                categories['networking'].append(file_path)
            else:
                categories['misc'].append(file_path)
                
        return categories
    
    def create_professional_structure(self, module_dir: Path) -> Dict[str, Path]:
        """Create professional directory structure"""        directories = {}
        
        # Core directories
        for dir_name in ['core', 'intelligence', 'adapters', 'utils', 'models', 'config']:
            dir_path = module_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            directories[dir_name] = dir_path
            
            # Create __init__.py if not exists
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                with open(init_file, 'w') as f:
                    f.write(f'"""\\n{dir_name.title()} module initialization\\n"""\\n')
        
        return directories
    
    def reorganize_files(self, module_dir: Path, file_categories: Dict[str, List[Path]], directories: Dict[str, Path]):
        """Reorganize files into professional structure"""        
        # Mapping of file categories to target directories
        target_mapping = {
            'managers': 'core',
            'engines': 'core', 
            'processors': 'core',
            'handlers': 'core',
            'adapters': 'adapters',
            'analyzers': 'intelligence',
            'intelligence': 'intelligence',
            'collectors': 'intelligence',
            'models': 'models',
            'schemas': 'models',
            'configs': 'config',
            'utils': 'utils',
            'monitoring': 'utils',
            'security': 'utils',
            'storage': 'utils',
            'networking': 'utils'
        }
        
        moves_performed = []
        
        for category, files in file_categories.items():
            if not files:
                continue
                
            target_dir = target_mapping.get(category, 'utils')
            target_path = directories[target_dir]
            
            for file_path in files:
                try:
                    # Skip if already in target directory
                    if file_path.parent == target_path:
                        continue
                        
                    # Skip the new manager.py we created
                    if file_path.name == 'manager.py' and file_path.parent == module_dir:
                        continue
                    
                    # Generate new filename if needed
                    new_filename = self._generate_professional_filename(file_path.name, category)
                    new_path = target_path / new_filename
                    
                    # Handle name conflicts
                    counter = 1
                    while new_path.exists():
                        name_parts = new_filename.split('.')
                        name_parts[0] += f"_{counter}"
                        new_filename = '.'.join(name_parts)
                        new_path = target_path / new_filename
                        counter += 1
                    
                    # Move file
                    shutil.move(str(file_path), str(new_path))
                    moves_performed.append(f"{file_path.name} → {target_dir}/{new_filename}")
                    
                except Exception as e:
                    logger.error(f"Failed to move {file_path}: {e}")
        
        return moves_performed
    
    def _generate_professional_filename(self, filename: str, category: str) -> str:
        """Generate professional filename based on category"""        
        # Remove redundant suffixes and clean up
        name = filename.replace('.py', '')
        
        # Category-specific naming rules
        if category == 'managers':
            if not name.endswith('_manager'):
                name = f"{name}_manager"
        elif category == 'adapters':
            if not name.endswith('_adapter'):
                name = f"{name}_adapter"
        elif category == 'processors':
            if not name.endswith('_processor'):
                name = f"{name}_processor"
        elif category == 'handlers':
            if not name.endswith('_handler'):
                name = f"{name}_handler"
        elif category == 'analyzers':
            if not name.endswith('_analyzer'):
                name = f"{name}_analyzer"
        elif category == 'engines':
            if not name.endswith('_engine'):
                name = f"{name}_engine"
        elif category == 'models':
            if not name.endswith(('_model', '_models')):
                if 'model' not in name:
                    name = f"{name}_models"
        elif category == 'schemas':
            if not name.endswith(('_schema', '_schemas')):
                if 'schema' not in name:
                    name = f"{name}_schemas"
                    
        return f"{name}.py"
    
    def update_imports_in_files(self, module_dir: Path):
        """Update import statements to reflect new structure"""        # This would be a complex operation requiring AST parsing
        # For now, we'll create a mapping file for manual updates
        
        mapping_file = module_dir / "IMPORT_MAPPING.md"
        with open(mapping_file, 'w') as f:
            f.write("""# Import Mapping Guide

This file contains the mapping of old imports to new structure.
Update your imports according to this mapping:

## Old Structure → New Structure

### Core Components
- Direct imports → `from .core import *`

### Intelligence Components  
- AI/ML related → `from .intelligence import *`

### Adapters
- Platform integrations → `from .adapters import *`

### Models & Schemas
- Data models → `from .models import *`

### Utils & Helpers
- Utilities → `from .utils import *`

### Config
- Configuration → `from .config import *`

## Example Updates
```python
# Old
from .some_manager import SomeManager

# New  
from .core.some_manager import SomeManager

# Or use the main manager
from .manager import SomeModuleManager
```
""")
    
    def reorganize_single_module(self, module_name: str) -> Dict[str, any]:
        """Reorganize a single module"""        module_dir = self.base_path / module_name
        
        if not module_dir.is_dir():
            return {'success': False, 'error': 'Module not found'}
        
        logger.info(f"🔧 Reorganizing {module_name}...")
        
        try:
            # Analyze existing files
            file_categories = self.analyze_module_files(module_dir)
            
            # Create professional structure
            directories = self.create_professional_structure(module_dir)
            
            # Reorganize files
            moves_performed = self.reorganize_files(module_dir, file_categories, directories)
            
            # Update import mappings
            self.update_imports_in_files(module_dir)
            
            result = {
                'success': True,
                'module': module_name,
                'files_moved': len(moves_performed),
                'moves': moves_performed,
                'directories_created': list(directories.keys())
            }
            
            logger.info(f"✅ {module_name}: {len(moves_performed)} files reorganized")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to reorganize {module_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def reorganize_all_modules(self):
        """Reorganize all modules"""        logger.info("🚀 Starting Professional File Reorganization...")
        
        results = []
        total_moves = 0
        
        # Get all module directories
        for module_dir in self.base_path.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith('.'):
                continue
            if module_dir.name in self.excluded_dirs:
                continue
                
            result = self.reorganize_single_module(module_dir.name)
            results.append(result)
            
            if result['success']:
                total_moves += result['files_moved']
        
        # Summary
        successful = len([r for r in results if r['success']])
        failed = len([r for r in results if not r['success']])
        
        logger.info(f"🎉 Reorganization Complete!")
        logger.info(f"   ✅ Successful: {successful} modules")
        logger.info(f"   ❌ Failed: {failed} modules") 
        logger.info(f"   📁 Total files moved: {total_moves}")
        
        return results

if __name__ == "__main__":
    reorganizer = ProfessionalReorganizer()
    results = reorganizer.reorganize_all_modules()
    
    # Save detailed report
    import json
    with open("/workspaces/Ainflue/ai_agents/REORGANIZATION_REPORT.json", 'w') as f:
        json.dump(results, f, indent=2)
