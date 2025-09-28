#!/bin/bash
# Script de correction automatique des imports aioredis pour Python 3.12
# Auteur: Expert DevOps multi-rôles

echo "🔧 Correction automatique des imports aioredis pour Python 3.12..."

# Trouver tous les fichiers Python avec import aioredis
files=$(find . -name "*.py" -exec grep -l "import aioredis" {} \; 2>/dev/null)

for file in $files; do
    echo "📝 Correction: $file"
    
    # Remplacer "import aioredis" par la version sécurisée
    sed -i 's/import aioredis/# Safe Redis import with Python 3.12 compatibility\
try:\
    import aioredis\
    REDIS_AVAILABLE = True\
except (ImportError, TypeError) as e:\
    # Handle Python 3.12 TimeoutError duplicate base class issue\
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE\
    import logging\
    logging.warning(f"Using Redis compatibility layer: {e}")/g' "$file"
done

echo "✅ Correction terminée pour $(echo "$files" | wc -l) fichiers"