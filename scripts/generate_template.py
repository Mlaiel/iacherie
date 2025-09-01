#!/usr/bin/env python3
"""
Template Generator for Ainflue Platform
Generates new services and AI agents from templates with proper naming and structure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()

class TemplateGenerator:
    """Generator for creating new services and agents from templates."""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.year = datetime.now().year
        
    def generate_service(self, service_name: str, config: Dict[str, Any]) -> bool:
        """Generate a new service from template.
        
        Args:
            service_name: Name of the service (e.g., "ContentAnalysis")
            config: Configuration dictionary with author info, description, etc.
            
        Returns:
            bool: True if generation successful
        """
        try:
            console.print(f"🏗️ Generating service: {service_name}", style="blue")
            
            # Prepare template variables
            variables = self._prepare_service_variables(service_name, config)
            
            # Read template
            template_path = self.templates_dir / "service_template.py"
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            # Replace variables
            generated_content = self._replace_variables(template_content, variables)
            
            # Create output directory
            output_dir = Path("services") / service_name.lower()
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Write service file
            service_file = output_dir / f"{service_name.lower()}_service.py"
            with open(service_file, 'w') as f:
                f.write(generated_content)
            
            # Create additional files
            self._create_service_files(output_dir, service_name, variables)
            
            console.print(f"✅ Service generated successfully at: {output_dir}", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to generate service: {e}", style="red")
            return False
    
    def generate_agent(self, agent_name: str, config: Dict[str, Any]) -> bool:
        """Generate a new AI agent from template.
        
        Args:
            agent_name: Name of the agent (e.g., "ContentAnalysis")
            config: Configuration dictionary with author info, description, etc.
            
        Returns:
            bool: True if generation successful
        """
        try:
            console.print(f"🤖 Generating AI agent: {agent_name}", style="blue")
            
            # Prepare template variables
            variables = self._prepare_agent_variables(agent_name, config)
            
            # Read template
            template_path = self.templates_dir / "agent_template.py"
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            # Replace variables
            generated_content = self._replace_variables(template_content, variables)
            
            # Create output directory
            output_dir = Path("ai_agents") / f"{agent_name.lower()}_agent"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Write agent file
            agent_file = output_dir / f"{agent_name.lower()}_agent.py"
            with open(agent_file, 'w') as f:
                f.write(generated_content)
            
            # Create additional files
            self._create_agent_files(output_dir, agent_name, variables)
            
            console.print(f"✅ Agent generated successfully at: {output_dir}", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to generate agent: {e}", style="red")
            return False
    
    def _prepare_service_variables(self, service_name: str, config: Dict[str, Any]) -> Dict[str, str]:
        """Prepare variables for service template replacement."""
        return {
            "service_name": service_name,
            "service_name_lower": service_name.lower(),
            "service_description": config.get("description", f"{service_name} service"),
            "author_name": config.get("author_name", "Developer"),
            "author_email": config.get("author_email", "developer@example.com"),
            "year": str(self.year)
        }
    
    def _prepare_agent_variables(self, agent_name: str, config: Dict[str, Any]) -> Dict[str, str]:
        """Prepare variables for agent template replacement."""
        return {
            "agent_name": agent_name,
            "agent_name_lower": agent_name.lower(),
            "agent_description": config.get("description", f"{agent_name} AI agent"),
            "agent_description_lower": config.get("description", f"{agent_name} AI agent").lower(),
            "author_name": config.get("author_name", "Developer"),
            "author_email": config.get("author_email", "developer@example.com"),
            "year": str(self.year)
        }
    
    def _replace_variables(self, content: str, variables: Dict[str, str]) -> str:
        """Replace template variables in content."""
        for var_name, var_value in variables.items():
            placeholder = "{{" + var_name + "}}"
            content = content.replace(placeholder, var_value)
        return content
    
    def _create_service_files(self, output_dir: Path, service_name: str, variables: Dict[str, str]):
        """Create additional files for the service."""
        
        # Create __init__.py
        init_content = f'''"""
{service_name} Service Package
{variables["service_description"]}

Author: {variables["author_name"]} ({variables["author_email"]})
"""

from .{service_name.lower()}_service import {service_name}Service, create_{service_name.lower()}_service

__all__ = ["{service_name}Service", "create_{service_name.lower()}_service"]
'''
        with open(output_dir / "__init__.py", 'w') as f:
            f.write(init_content)
        
        # Create README.md
        readme_content = f'''# {service_name} Service

{variables["service_description"]}

## Features

- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## Usage

```python
from services.{service_name.lower()} import create_{service_name.lower()}_service

# Create service
service = create_{service_name.lower()}_service({{
    "max_concurrent_requests": 50,
    "timeout_seconds": 30
}})

# Start service
await service.start()

# Process request
result = await service.process_request({{
    "field1": "value1",
    "field2": "value2"
}})

# Stop service
await service.stop()
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| max_concurrent_requests | int | 100 | Maximum concurrent requests |
| timeout_seconds | int | 30 | Request timeout |
| retry_attempts | int | 3 | Number of retry attempts |

## Health Check

The service provides health check endpoints:

- `/health` - Basic health status
- `/metrics` - Service metrics

## Author

{variables["author_name"]} ({variables["author_email"]})
'''
        with open(output_dir / "README.md", 'w') as f:
            f.write(readme_content)
        
        # Create tests directory
        tests_dir = output_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # Create test file
        test_content = f'''"""
Tests for {service_name} Service
"""

import pytest
import asyncio
from services.{service_name.lower()} import create_{service_name.lower()}_service

class Test{service_name}Service:
    """Test cases for {service_name} service."""
    
    @pytest.fixture
    async def service(self):
        """Create test service instance."""
        service = create_{service_name.lower()}_service({{
            "max_concurrent_requests": 10,
            "timeout_seconds": 5
        }})
        await service.start()
        yield service
        await service.stop()
    
    async def test_service_creation(self):
        """Test service creation."""
        service = create_{service_name.lower()}_service()
        assert service is not None
        assert service.config.max_concurrent_requests == 100
    
    async def test_service_start_stop(self, service):
        """Test service start and stop."""
        # Service should be running from fixture
        health = await service.health_check()
        assert health["healthy"] is True
    
    async def test_process_request(self, service):
        """Test request processing."""
        request_data = {{
            "field1": "test_value1",
            "field2": "test_value2"
        }}
        
        result = await service.process_request(request_data)
        assert result["success"] is True
        assert "result" in result
        assert "processing_time_seconds" in result
    
    async def test_health_check(self, service):
        """Test health check functionality."""
        health = await service.health_check()
        assert "service" in health
        assert "status" in health
        assert "healthy" in health
        assert health["service"] == "{service_name}"
    
    async def test_metrics(self, service):
        """Test metrics collection."""
        metrics = service.get_metrics()
        assert "service" in metrics
        assert "metrics" in metrics
        assert metrics["service"] == "{service_name}"
'''
        with open(tests_dir / f"test_{service_name.lower()}_service.py", 'w') as f:
            f.write(test_content)
    
    def _create_agent_files(self, output_dir: Path, agent_name: str, variables: Dict[str, str]):
        """Create additional files for the AI agent."""
        
        # Create __init__.py
        init_content = f'''"""
{agent_name} AI Agent Package
{variables["agent_description"]}

Author: {variables["author_name"]} ({variables["author_email"]})
"""

from .{agent_name.lower()}_agent import {agent_name}Agent, create_{agent_name.lower()}_agent

__all__ = ["{agent_name}Agent", "create_{agent_name.lower()}_agent"]
'''
        with open(output_dir / "__init__.py", 'w') as f:
            f.write(init_content)
        
        # Create README.md
        readme_content = f'''# {agent_name} AI Agent

{variables["agent_description"]}

## Capabilities

- Capability 1: Description
- Capability 2: Description
- Capability 3: Description

## Usage

```python
from ai_agents.{agent_name.lower()}_agent import create_{agent_name.lower()}_agent

# Create agent
agent = create_{agent_name.lower()}_agent({{
    "model_temperature": 0.7,
    "confidence_threshold": 0.8,
    "enable_advanced_reasoning": True
}})

# Process request
request = {{
    "message": "Your request message here",
    "context": {{"user_id": "123"}},
    "parameters": {{"param1": "value1"}}
}}

result = await agent.process_request(request)
print(result["response"])

# Provide feedback for learning
feedback = {{
    "score": 5,
    "text": "Great response!",
    "interaction_id": "interaction123"
}}
await agent.learn_from_feedback(feedback)
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| model_name | str | gpt-4 | AI model to use |
| model_temperature | float | 0.7 | Response creativity (0-2) |
| confidence_threshold | float | 0.8 | Minimum confidence for responses |
| max_concurrent_tasks | int | 10 | Maximum concurrent processing |
| memory_retention_days | int | 30 | How long to retain memory |

## Memory and Learning

The agent includes:
- **Conversation Memory**: Remembers context from recent interactions
- **Learning Patterns**: Adapts based on feedback and successful interactions
- **Context Awareness**: Uses relevant past experiences to improve responses

## Monitoring

The agent provides comprehensive monitoring:

```python
# Get agent status
status = agent.get_status()
print(status)

# Get capabilities
capabilities = agent.get_capabilities()
print(capabilities)
```

## Author

{variables["author_name"]} ({variables["author_email"]})
'''
        with open(output_dir / "README.md", 'w') as f:
            f.write(readme_content)
        
        # Create tests directory
        tests_dir = output_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # Create test file
        test_content = f'''"""
Tests for {agent_name} AI Agent
"""

import pytest
import asyncio
from ai_agents.{agent_name.lower()}_agent import create_{agent_name.lower()}_agent

class Test{agent_name}Agent:
    """Test cases for {agent_name} agent."""
    
    @pytest.fixture
    def agent(self):
        """Create test agent instance."""
        return create_{agent_name.lower()}_agent({{
            "model_temperature": 0.5,
            "confidence_threshold": 0.7
        }})
    
    def test_agent_creation(self, agent):
        """Test agent creation."""
        assert agent is not None
        assert agent.config.model_temperature == 0.5
        assert agent.config.confidence_threshold == 0.7
    
    def test_agent_capabilities(self, agent):
        """Test agent capabilities."""
        capabilities = agent.get_capabilities()
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
    
    async def test_process_request(self, agent):
        """Test request processing."""
        request = {{
            "message": "Hello, please help me analyze this data.",
            "context": {{"user_id": "test_user"}},
            "parameters": {{"analysis_type": "basic"}}
        }}
        
        result = await agent.process_request(request)
        assert result["success"] is True
        assert "response" in result
        assert "confidence" in result
        assert "processing_time_seconds" in result
    
    async def test_learning_from_feedback(self, agent):
        """Test learning from feedback."""
        feedback = {{
            "score": 4,
            "text": "Good response",
            "interaction_id": "test_interaction"
        }}
        
        # Should not raise exception
        await agent.learn_from_feedback(feedback)
    
    def test_agent_status(self, agent):
        """Test agent status reporting."""
        status = agent.get_status()
        assert "agent_name" in status
        assert "state" in status
        assert "capabilities" in status
        assert status["agent_name"] == "{agent_name}"
    
    async def test_request_validation(self, agent):
        """Test request validation."""
        invalid_request = {{}}  # Empty request
        
        with pytest.raises(Exception):
            await agent.process_request(invalid_request)
'''
        with open(tests_dir / f"test_{agent_name.lower()}_agent.py", 'w') as f:
            f.write(test_content)
        
        # Create config directory
        config_dir = output_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Create configuration file
        config_content = f'''"""
Configuration for {agent_name} Agent
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class {agent_name}DefaultConfig:
    """Default configuration for {agent_name} agent."""
    
    # AI Model settings
    model_name: str = "gpt-4"
    model_temperature: float = 0.7
    max_tokens: int = 2048
    
    # Agent behavior
    reasoning_depth: int = 3
    confidence_threshold: float = 0.8
    enable_advanced_reasoning: bool = True
    
    # Performance
    max_concurrent_tasks: int = 10
    response_timeout: int = 30
    memory_retention_days: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {{
            "model_name": self.model_name,
            "model_temperature": self.model_temperature,
            "max_tokens": self.max_tokens,
            "reasoning_depth": self.reasoning_depth,
            "confidence_threshold": self.confidence_threshold,
            "enable_advanced_reasoning": self.enable_advanced_reasoning,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "response_timeout": self.response_timeout,
            "memory_retention_days": self.memory_retention_days
        }}

# Default configuration instance
default_config = {agent_name}DefaultConfig()
'''
        with open(config_dir / "default_config.py", 'w') as f:
            f.write(config_content)

def interactive_service_generator():
    """Interactive service generator with prompts."""
    console.print(Panel.fit(
        Text("🏗️ Ainflue Service Generator", justify="center", style="bold blue"),
        title="Development Tools",
        border_style="blue"
    ))
    
    # Get service information
    service_name = Prompt.ask("Service name (e.g., ContentAnalysis)")
    description = Prompt.ask("Service description", default=f"{service_name} service for Ainflue platform")
    author_name = Prompt.ask("Author name", default="Developer")
    author_email = Prompt.ask("Author email", default="developer@example.com")
    
    # Validate service name
    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', service_name):
        console.print("❌ Service name must start with uppercase letter and contain only letters/numbers", style="red")
        return False
    
    # Show summary
    console.print(f"\n📋 Service Summary:")
    console.print(f"Name: {service_name}")
    console.print(f"Description: {description}")
    console.print(f"Author: {author_name} ({author_email})")
    
    if not Confirm.ask("\nGenerate service?"):
        return False
    
    # Generate service
    generator = TemplateGenerator()
    config = {
        "description": description,
        "author_name": author_name,
        "author_email": author_email
    }
    
    return generator.generate_service(service_name, config)

def interactive_agent_generator():
    """Interactive agent generator with prompts."""
    console.print(Panel.fit(
        Text("🤖 Ainflue AI Agent Generator", justify="center", style="bold green"),
        title="Development Tools",
        border_style="green"
    ))
    
    # Get agent information
    agent_name = Prompt.ask("Agent name (e.g., ContentAnalysis)")
    description = Prompt.ask("Agent description", default=f"{agent_name} AI agent for intelligent processing")
    author_name = Prompt.ask("Author name", default="Developer")
    author_email = Prompt.ask("Author email", default="developer@example.com")
    
    # Validate agent name
    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', agent_name):
        console.print("❌ Agent name must start with uppercase letter and contain only letters/numbers", style="red")
        return False
    
    # Show summary
    console.print(f"\n📋 Agent Summary:")
    console.print(f"Name: {agent_name}")
    console.print(f"Description: {description}")
    console.print(f"Author: {author_name} ({author_email})")
    
    if not Confirm.ask("\nGenerate agent?"):
        return False
    
    # Generate agent
    generator = TemplateGenerator()
    config = {
        "description": description,
        "author_name": author_name,
        "author_email": author_email
    }
    
    return generator.generate_agent(agent_name, config)

def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(description="Generate new services and AI agents for Ainflue platform")
    parser.add_argument("type", choices=["service", "agent"], help="Type of component to generate")
    parser.add_argument("--name", help="Component name")
    parser.add_argument("--description", help="Component description")
    parser.add_argument("--author-name", help="Author name")
    parser.add_argument("--author-email", help="Author email")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive or not args.name:
        # Interactive mode
        if args.type == "service":
            success = interactive_service_generator()
        else:
            success = interactive_agent_generator()
    else:
        # Command line mode
        generator = TemplateGenerator()
        config = {
            "description": args.description or f"{args.name} {args.type}",
            "author_name": args.author_name or "Developer",
            "author_email": args.author_email or "developer@example.com"
        }
        
        if args.type == "service":
            success = generator.generate_service(args.name, config)
        else:
            success = generator.generate_agent(args.name, config)
    
    if success:
        console.print("\n🎉 Component generated successfully!", style="bold green")
        console.print("\n📝 Next steps:")
        console.print("1. Review the generated code")
        console.print("2. Customize the business logic")
        console.print("3. Add specific configuration")
        console.print("4. Write comprehensive tests")
        console.print("5. Update documentation")
    else:
        console.print("\n❌ Generation failed!", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main()