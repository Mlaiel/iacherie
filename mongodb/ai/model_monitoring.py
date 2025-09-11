# Symlink the training_data_manager.py to create the individual module files

# Create individual module files that import from the consolidated module
"""Model Monitoring Module"""
from .training_data_manager import ModelMonitoring
__all__ = ['ModelMonitoring']