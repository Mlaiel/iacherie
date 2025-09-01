#!/usr/bin/env python3
"""Ainflue Platform Service Generator
Scaffolding tool to create new services from templates

Usage:
    python scripts/dev/generate_service.py <service_name> [options]

Example:
    python scripts/dev/generate_service.py ContentAnalysis --author "John Doe" --email "john@example.com"
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path


def generate_service(service_name: str, author_name: str, author_email: str, description: str):
    """Generate a new service from template"""
    
    # Calculate derived names
    service_name_lower = service_name.lower()
    service_name_upper = service_name.upper()
    created_date = datetime.now().strftime("%Y-%m-%d")
    
    # Template variables
    variables = {
        "service_name": service_name,
        "service_name_lower": service_name_lower,
        "service_name_upper": service_name_upper,
        "service_description": description,
        "author_name": author_name,
        "author_email": author_email,
        "created_date": created_date
    }
    
    # Paths
    project_root = Path(__file__).parent.parent.parent
    templates_dir = project_root / "templates" / "service"
    services_dir = project_root / "services"
    routes_dir = project_root / "api" / "routes"
    tests_dir = project_root / "tests" / "services"
    
    # Create directories
    services_dir.mkdir(exist_ok=True)
    routes_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)
    
    # Generate service file
    service_template = templates_dir / "service_template.py"
    service_output = services_dir / f"{service_name_lower}_service.py"
    
    if service_template.exists():
        with open(service_template, 'r') as f:
            content = f.read()
        
        # Replace template variables
        for key, value in variables.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        
        with open(service_output, 'w') as f:
            f.write(content)
        
        print(f"✅ Generated service: {service_output}")
    
    # Generate router file
    router_template = templates_dir / "router_template.py"
    router_output = routes_dir / f"{service_name_lower}_routes.py"
    
    if router_template.exists():
        with open(router_template, 'r') as f:
            content = f.read()
        
        # Replace template variables
        for key, value in variables.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        
        with open(router_output, 'w') as f:
            f.write(content)
        
        print(f"✅ Generated router: {router_output}")
    
    # Generate test file
    test_template = templates_dir / "test_template.py"
    test_output = tests_dir / f"test_{service_name_lower}_service.py"
    
    if test_template.exists():
        with open(test_template, 'r') as f:
            content = f.read()
        
        # Replace template variables
        for key, value in variables.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        
        with open(test_output, 'w') as f:
            f.write(content)
        
        print(f"✅ Generated tests: {test_output}")
    
    # Generate __init__.py files if they don't exist
    init_files = [
        services_dir / "__init__.py",
        routes_dir / "__init__.py",
        tests_dir / "__init__.py"
    ]
    
    for init_file in init_files:
        if not init_file.exists():
            with open(init_file, 'w') as f:
                f.write('"""Service module"""\n')
            print(f"✅ Generated: {init_file}")
    
    # Generate documentation
    docs_dir = project_root / "docs" / "services"
    docs_dir.mkdir(parents=True, exist_ok=True)
    doc_output = docs_dir / f"{service_name_lower}.md"
    
    doc_content = f"""# {service_name} Service

{description}

## Overview

The {service_name} service provides functionality for {description.lower()}.

## API Endpoints

### POST /{service_name_lower}/process

Process {service_name_lower} request.

**Request Body:**
```json
{{
  // Add request schema here
}}
```

**Response:**
```json
{{
  "success": true,
  "message": "{service_name} processed successfully",
  "data": {{
    // Response data here
  }},
  "timestamp": "2024-01-01T00:00:00Z"
}}
```

### GET /{service_name_lower}/health

Health check endpoint.

### GET /{service_name_lower}/info

Service information endpoint.

## Usage Example

```python
from services.{service_name_lower}_service import {service_name}Service, {service_name}Request

# Create service instance
service = {service_name}Service()

# Create request
request = {service_name}Request(
    # Add request parameters
)

# Process request
response = await service.process(request)
```

## Configuration

The service can be configured using the following environment variables:

- `{service_name_upper}_ENABLED`: Enable/disable the service (default: true)
- `{service_name_upper}_TIMEOUT`: Processing timeout in seconds (default: 30)

## Testing

Run tests for this service:

```bash
pytest tests/services/test_{service_name_lower}_service.py -v
```

## Author

{author_name} ({author_email})

## Created

{created_date}
"""
    
    with open(doc_output, 'w') as f:
        f.write(doc_content)
    
    print(f"✅ Generated documentation: {doc_output}")
    
    print(f"""
🎉 Service '{service_name}' generated successfully!

📁 Files created:
  - Service: services/{service_name_lower}_service.py
  - Router: api/routes/{service_name_lower}_routes.py
  - Tests: tests/services/test_{service_name_lower}_service.py
  - Docs: docs/services/{service_name_lower}.md

🔧 Next steps:
  1. Implement the service logic in the generated files
  2. Add the router to your main FastAPI app
  3. Update the request/response models
  4. Write comprehensive tests
  5. Update the documentation

💡 To add the router to your app:
```python
from api.routes.{service_name_lower}_routes import router as {service_name_lower}_router
app.include_router({service_name_lower}_router)
```
""")


def main():
    parser = argparse.ArgumentParser(description="Generate a new service from template")
    parser.add_argument("service_name", help="Name of the service (e.g., ContentAnalysis)")
    parser.add_argument("--author", default="Developer", help="Author name")
    parser.add_argument("--email", default="dev@ainflue.com", help="Author email")
    parser.add_argument("--description", help="Service description")
    
    args = parser.parse_args()
    
    # Validate service name
    if not args.service_name.isidentifier():
        print("❌ Service name must be a valid Python identifier")
        sys.exit(1)
    
    # Generate description if not provided
    if not args.description:
        args.description = f"Service for {args.service_name.lower()} operations"
    
    try:
        generate_service(
            service_name=args.service_name,
            author_name=args.author,
            author_email=args.email,
            description=args.description
        )
    except Exception as e:
        print(f"❌ Error generating service: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()