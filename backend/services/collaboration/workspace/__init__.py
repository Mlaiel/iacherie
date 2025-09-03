"""Workspace Services Module

Collaborative workspace services for project management and real-time collaboration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .project_manager import ProjectManager
from .real_time_collab import RealTimeCollab
from .version_control import VersionControl

__all__ = ['ProjectManager', 'RealTimeCollab', 'VersionControl']