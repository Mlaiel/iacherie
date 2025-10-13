import os
import re

files = [
    'models/consultation.py',
    'models/prescription.py',
    'models/medical_record.py',
    'models/medical_document.py',
    'models/community.py',
    'models/solidarity.py'
]

for filepath in files:
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Add ConfigDict import if not present
    if 'from pydantic import' in content and 'ConfigDict' not in content:
        content = re.sub(
            r'(from pydantic import [^)]+)',
            lambda m: m.group(1) + ', ConfigDict' if ')' not in m.group(1) else m.group(1).replace(')', ', ConfigDict)'),
            content
        )
    
    # Replace class Config with model_config
    content = re.sub(
        r'\n    class Config:\n        from_attributes = True\n',
        '\n    model_config = ConfigDict(from_attributes=True)\n',
        content
    )
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Fixed: {filepath}")

print("\nDone!")
