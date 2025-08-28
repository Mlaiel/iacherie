# Import Mapping Guide

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
