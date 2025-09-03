#!/usr/bin/env python3
"""Fix numpy dependencies in distribution module"""

import os
import re

def fix_numpy_dependencies():
    """Replace numpy dependencies with vanilla Python equivalents"""
    
    distribution_dir = "distribution"
    
    # Replacements map
    replacements = [
        (r'np\.mean\(([^)]+)\)', r'safe_mean(\1)'),
        (r'np\.random\.uniform\(([^)]+)\)', r'safe_random_uniform(\1)'),
        (r'np\.sqrt\(([^)]+)\)', r'math.sqrt(\1)'),
        (r'np\.abs\(([^)]+)\)', r'abs(\1)'),
        (r'np\.max\(([^)]+)\)', r'max(\1)'),
        (r'np\.min\(([^)]+)\)', r'min(\1)'),
        (r'np\.sum\(([^)]+)\)', r'sum(\1)'),
        (r'np\.ndarray', r'list'),
    ]
    
    # Utility functions to add
    utility_functions = '''
def safe_mean(values):
    """Calculate mean safely without numpy"""
    if not values:
        return 0.0
    return sum(values) / len(values)

def safe_random_uniform(low, high):
    """Generate random uniform value without numpy"""
    import random
    return random.uniform(low, high)

def safe_sqrt(value):
    """Calculate square root safely"""
    import math
    return math.sqrt(max(0, value))
'''
    
    for filename in os.listdir(distribution_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(distribution_dir, filename)
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Skip if no numpy usage
            if 'np.' not in content:
                continue
                
            # Add utility functions if numpy is used
            if 'def safe_mean(' not in content and 'np.' in content:
                # Find import section and add utilities
                import_end = content.find('\nlogger = logging.getLogger(__name__)')
                if import_end != -1:
                    content = content[:import_end] + '\n' + utility_functions + content[import_end:]
            
            # Apply replacements
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            
            # Fix specific numpy array issues
            content = content.replace('np.ndarray', 'list')
            content = content.replace(': np.ndarray', ': list')
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            print(f"Fixed numpy dependencies in {filename}")

if __name__ == "__main__":
    fix_numpy_dependencies()
    print("All numpy dependencies fixed!")