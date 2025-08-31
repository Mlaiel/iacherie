"""Version Control Core Components

Core engine and processing components for version control operations.
"""

from .version_control_engine import (
    VersionControlEngine,
    VersionControlJob,
    VersionControlResult
)

__all__ = [
    'VersionControlEngine',
    'VersionControlJob', 
    'VersionControlResult'
]