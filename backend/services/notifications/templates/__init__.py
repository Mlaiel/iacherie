"""Notification Templates Module

Service layer for managing notification templates.
Provides clean abstractions over the core template infrastructure.
"""

from .template_manager import TemplateManagerService

__all__ = [
    "TemplateManagerService"
]