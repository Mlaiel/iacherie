#!/usr/bin/env python3
"""Script pour corriger les arguments level dans core/__init__.py"""

import re

# Lire le fichier
with open('/workspaces/Ainfluencer/core/__init__.py', 'r') as f:
    content = f.read()

# Remplacer toutes les occurrences de level=self.level.value par rien
content = re.sub(r'system_class\(level=self\.level\.value\)', 'system_class()', content)

# Écrire le fichier corrigé
with open('/workspaces/Ainfluencer/core/__init__.py', 'w') as f:
    f.write(content)

print("✅ Correction des arguments 'level' terminée")