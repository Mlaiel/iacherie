"""
Ainflue Desktop Renderer - UI Components Index
Index and export for UI components

Author: Fahed Mlaiel (mlaiel@live.de) 
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# UI Components orchestration and export index
# Professional interface components registry

UI_COMPONENTS = {
    'professional_controls': 'professional_controls.js',
    'dashboard_layouts': 'dashboard_layouts.js', 
    'notification_system': 'notification_system.js',
    'modal_manager': 'modal_manager.js',
    'sidebar_navigation': 'sidebar_navigation.js',
    'header_controls': 'header_controls.js',
    'status_indicators': 'status_indicators.js',
    'responsive_utilities': 'responsive_utilities.js',
    'theme_manager': 'theme_manager.js'
}

STYLES = {
    'main': 'ui_components.styles.css'
}

def get_component_list():
    """Get list of available UI components"""
    return list(UI_COMPONENTS.keys())

def get_component_path(component_name):
    """Get path for specific component"""
    return UI_COMPONENTS.get(component_name)