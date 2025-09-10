"""
Scaling Infrastructure Module
================================
Enterprise scaling management for Ainflue platform

Author: Fahed Mlaiel <mlaiel@live.de>
Project: Ainflue - IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved
"""

from .horizontal_scaler import HorizontalscalerManager, get_horizontal_scaler_manager
from .vertical_scaler import VerticalscalerManager, get_vertical_scaler_manager
from .predictive_scaler import PredictivescalerManager, get_predictive_scaler_manager

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

__all__ = [
    "HorizontalscalerManager", "get_horizontal_scaler_manager", "VerticalscalerManager", "get_vertical_scaler_manager", "PredictivescalerManager", "get_predictive_scaler_manager"
]