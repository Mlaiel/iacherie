"""🛠️ Compatibility Fallbacks for Optional Dependencies
========================================================

This module provides fallback implementations for optional dependencies
to ensure the protection module can load even when some packages are missing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# PANDAS FALLBACK
# ============================================================================

class DataFrameFallback:
    """Simple fallback for pandas DataFrame"""
    
    def __init__(self, data=None, columns=None) -> None:
        if data is None:
            data = []
        if isinstance(data, dict):
            self.data = data
            self.columns = list(data.keys()) if columns is None else columns
        elif isinstance(data, list):
            self.data = {}
            self.columns = columns or []
            if data and isinstance(data[0], dict):
                self.columns = list(data[0].keys())
                for i, row in enumerate(data):
                    for col, val in row.items():
                        if col not in self.data:
                            self.data[col] = {}
                        self.data[col][i] = val
        else:
            self.data = {}
            self.columns = []
    
    def to_dict(self, orient='records') -> None:
        if orient == 'records':
            records = []
            if not self.data:
                return records
            max_len = max(len(col_data) for col_data in self.data.values()) if self.data else 0
            for i in range(max_len):
                record = {}
                for col in self.columns:
                    if col in self.data and i in self.data[col]:
                        record[col] = self.data[col][i]
                    else:
                        record[col] = None
                records.append(record)
            return records
        return self.data
    
    def to_json(self, orient='records') -> None:
        import json
        return json.dumps(self.to_dict(orient))
    
    def __getitem__(self, key) -> None:
        return self.data.get(key, {})
    
    def __len__(self) -> None:
        return max(len(col_data) for col_data in self.data.values()) if self.data else 0

class PandasFallback:
    """Simple fallback for pandas module"""
    
    def DataFrame(self, *args, **kwargs) -> None:
        return DataFrameFallback(*args, **kwargs)
    
    def read_csv(self, *args, **kwargs) -> None:
        return DataFrameFallback()
    
    def read_json(self, *args, **kwargs) -> None:
        return DataFrameFallback()

# ============================================================================
# PLOTLY FALLBACK
# ============================================================================

class PlotlyFallback:
    """Simple fallback for plotly"""
    
    class graph_objects:
    """graph_objects: class implementation"""
        class Figure:
    """Figure: class implementation"""
            def __init__(self, *args, **kwargs) -> None:
                self.data = []
                self.layout = {}
            
            def add_trace(self, trace) -> None:
                self.data.append(trace)
            
            def update_layout(self, **kwargs) -> None:
                self.layout.update(kwargs)
            
            def to_json(self) -> None:
                import json
                return json.dumps({
                    'data': self.data,
                    'layout': self.layout
                })
            
            def to_html(self) -> None:
                return "<div>Chart placeholder - plotly not available</div>"
        
        class Scatter:
    """Scatter: class implementation"""
            def __init__(self, **kwargs) -> None:
                self.data = kwargs
        
        class Bar:
    """Bar: class implementation"""
            def __init__(self, **kwargs) -> None:
                self.data = kwargs
        
        class Pie:
    """Pie: class implementation"""
            def __init__(self, **kwargs) -> None:
                self.data = kwargs

# ============================================================================
# MATPLOTLIB FALLBACK
# ============================================================================

class MatplotlibFallback:
    """Simple fallback for matplotlib"""
    
    class pyplot:
    """pyplot: class implementation"""
        @staticmethod
        def figure(*args, **kwargs) -> None:
            pass
        
        @staticmethod
        def plot(*args, **kwargs) -> None:
            pass
        
        @staticmethod
        def bar(*args, **kwargs) -> None:
            pass
        
        @staticmethod
        def pie(*args, **kwargs) -> None:
            pass
        
        @staticmethod
        def title(*args, **kwargs) -> None:
            pass
        
        @staticmethod
        def xlabel(*args, **kwargs) -> None:
            pass
        
        @staticmethod
        def ylabel(*args, **kwargs) -> None:
            pass
        
        @staticmethod
        def legend(*args, **kwargs) -> None:
            pass
        
        @staticmethod
        def savefig(*args, **kwargs) -> None:
            pass
        
        @staticmethod
        def show() -> None:
            pass
        
        @staticmethod
        def close() -> None:
            pass

# ============================================================================
# SEABORN FALLBACK
# ============================================================================

class SeabornFallback:
    """Simple fallback for seaborn"""
    
    @staticmethod
    def heatmap(*args, **kwargs) -> None:
        pass
    
    @staticmethod
    def set_style(*args, **kwargs) -> None:
        pass
    
    @staticmethod
    def set_palette(*args, **kwargs) -> None:
        pass

# ============================================================================
# REPORTLAB FALLBACK
# ============================================================================

class ReportLabFallback:
    """Simple fallback for reportlab"""
    
    class pdfgen:
    """pdfgen: class implementation"""
        class canvas:
    """canvas: class implementation"""
            class Canvas:
    """Canvas: class implementation"""
                def __init__(self, *args, **kwargs) -> None:
                    pass
                
                def drawString(self, *args, **kwargs) -> None:
                    pass
                
                def showPage(self) -> None:
                    pass
                
                def save(self) -> None:
                    pass
    
    class lib:
    """lib: class implementation"""
        class pagesizes:
    """pagesizes: class implementation"""
            A4 = (595.276, 841.89)
            letter = (612, 792)

# ============================================================================
# DEPENDENCY LOADER WITH FALLBACKS
# ============================================================================

def load_pandas() -> None:
    """Load pandas with fallback"""
    try:
        import pandas as pd
        logger.debug("pandas loaded successfully")
        return pd, True
    except ImportError:
        logger.warning("pandas not available, using fallback")
        return PandasFallback(), False

def load_plotly() -> None:
    """Load plotly with fallback"""
    try:
        import plotly
        logger.debug("plotly loaded successfully")
        return plotly, True
    except ImportError:
        logger.warning("plotly not available, using fallback")
        return PlotlyFallback(), False

def load_matplotlib() -> None:
    """Load matplotlib with fallback"""
    try:
        import matplotlib
        logger.debug("matplotlib loaded successfully")
        return matplotlib, True
    except ImportError:
        logger.warning("matplotlib not available, using fallback")
        return MatplotlibFallback(), False

def load_seaborn() -> None:
    """Load seaborn with fallback"""
    try:
        import seaborn
        logger.debug("seaborn loaded successfully")
        return seaborn, True
    except ImportError:
        logger.warning("seaborn not available, using fallback")
        return SeabornFallback(), False

def load_reportlab() -> None:
    """Load reportlab with fallback"""
    try:
        import reportlab
        logger.debug("reportlab loaded successfully")
        return reportlab, True
    except ImportError:
        logger.warning("reportlab not available, using fallback")
        return ReportLabFallback(), False

# ============================================================================
# EXPORT ALL FALLBACKS
# ============================================================================

# Load with fallbacks
pd, PANDAS_AVAILABLE = load_pandas()
plotly, PLOTLY_AVAILABLE = load_plotly()
matplotlib, MATPLOTLIB_AVAILABLE = load_matplotlib()
seaborn, SEABORN_AVAILABLE = load_seaborn()
reportlab, REPORTLAB_AVAILABLE = load_reportlab()

# Export compatibility info
__all__ = [
    'pd', 'PANDAS_AVAILABLE',
    'plotly', 'PLOTLY_AVAILABLE', 
    'matplotlib', 'MATPLOTLIB_AVAILABLE',
    'seaborn', 'SEABORN_AVAILABLE',
    'reportlab', 'REPORTLAB_AVAILABLE',
    'DataFrameFallback', 'PandasFallback',
    'PlotlyFallback', 'MatplotlibFallback',
    'SeabornFallback', 'ReportLabFallback'
]