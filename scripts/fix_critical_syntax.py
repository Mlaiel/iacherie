#!/usr/bin/env python3
"""
Script de correction ciblée pour les erreurs de docstrings
Focus sur les patterns les plus courants
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def fix_docstring_syntax(file_path: Path) -> bool:
    """Corrige les erreurs de syntaxe de docstrings dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: Docstring suivie directement par du code (le plus courant)
        # Trouve: """docstring"""    code = value
        # Remplace par: """docstring"""
        #               code = value
        pattern1 = r'("""[^"]*?""")(\s*)([A-Za-z_][A-Za-z0-9_]*\s*[=:])'
        content = re.sub(pattern1, r'\1\n        \3', content)
        
        # Pattern 2: Pour les méthodes et fonctions
        pattern2 = r'("""[^"]*?""")(\s*)(pass|return|if|for|while|try|with)'
        content = re.sub(pattern2, r'\1\n        \2', content)
        
        # Pattern 3: Pour les classes 
        pattern3 = r'("""[^"]*?""")(\s*)(@\w+|class|def)'
        content = re.sub(pattern3, r'\1\n    \3', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Corrige les fichiers les plus critiques"""
    critical_files = [
        "data_management/validation/__init__.py",
        "data_management/transformers/__init__.py", 
        "data_management/fingerprinting/__init__.py",
        "data_management/seeds/__init__.py",
        "data_management/backups/__init__.py",
        "crawlers/__init__.py",
        "config/__init__.py",
        "business/__init__.py"
    ]
    
    root = Path("/home/runner/work/Ainflue/Ainflue")
    
    fixed_count = 0
    for file_rel_path in critical_files:
        file_path = root / file_rel_path
        if file_path.exists():
            if fix_docstring_syntax(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n📊 Fixed {fixed_count} files")


if __name__ == "__main__":
    main()