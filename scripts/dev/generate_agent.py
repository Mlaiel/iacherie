#!/usr/bin/env python3
"""Ainflue Platform AI Agent Generator
Scaffolding tool to create new AI agents from templates

Usage:
    python scripts/dev/generate_agent.py <agent_name> [options]

Example:
    python scripts/dev/generate_agent.py ContentAnalyzer --author "John Doe" --email "john@example.com"
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path


def generate_agent(agent_name: str, author_name: str, author_email: str, description: str):
    """Generate a new AI agent from template"""
    
    # Calculate derived names
    agent_name_lower = agent_name.lower()
    agent_name_upper = agent_name.upper()
    created_date = datetime.now().strftime("%Y-%m-%d")
    
    # Template variables
    variables = {
        "agent_name": agent_name,
        "agent_name_lower": agent_name_lower,
        "agent_name_upper": agent_name_upper,
        "agent_description": description,
        "author_name": author_name,
        "author_email": author_email,
        "created_date": created_date
    }
    
    # Paths
    project_root = Path(__file__).parent.parent.parent
    templates_dir = project_root / "templates" / "ai_agent"
    agents_dir = project_root / "ai_agents"
    tests_dir = project_root / "tests" / "ai_agents"
    
    # Create directories
    agents_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)
    
    # Generate agent file
    agent_template = templates_dir / "agent_template.py"
    agent_output = agents_dir / f"{agent_name_lower}_agent.py"
    
    if agent_template.exists():
        with open(agent_template, 'r') as f:
            content = f.read()
        
        # Replace template variables
        for key, value in variables.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        
        with open(agent_output, 'w') as f:
            f.write(content)
        
        print(f"✅ Generated agent: {agent_output}")
    
    # Generate test file
    test_content = f'''"""Tests for {agent_name} AI Agent
Comprehensive test suite for {agent_name} agent functionality

Author: {author_name} ({author_email})
Created: {created_date}
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from ai_agents.{agent_name_lower}_agent import (
    {agent_name}Agent,
    {agent_name}Task,
    {agent_name}Result,
    {agent_name}State,
    {agent_name}AgentFactory
)


class Test{agent_name}Agent:
    """Test suite for {agent_name} agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        return {agent_name}Agent()
    
    @pytest.fixture
    def sample_task(self):
        """Create sample task for testing"""
        return {agent_name}Task(
            id="test-task-001",
            input_data={{"text": "Sample text for processing"}},
            parameters={{"temperature": 0.5}}
        )
    
    @pytest.mark.asyncio
    async def test_process_task_success(self, agent, sample_task):
        """Test successful task processing"""
        # Act
        result = await agent.process_task(sample_task)
        
        # Assert
        assert isinstance(result, {agent_name}Result)
        assert result.task_id == sample_task.id
        assert result.success is True
        assert result.result_data is not None
        assert result.confidence is not None
        assert 0.0 <= result.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_process_task_invalid_input(self, agent):
        """Test processing with invalid input"""
        # Arrange
        invalid_task = {agent_name}Task(
            id="test-task-002",
            input_data={{}}  # Empty input
        )
        
        # Act
        result = await agent.process_task(invalid_task)
        
        # Assert
        assert result.success is False
        assert result.error_message is not None
    
    @pytest.mark.asyncio
    async def test_validate_input_valid(self, agent, sample_task):
        """Test input validation with valid data"""
        # Act & Assert - should not raise exception
        await agent._validate_input(sample_task)
    
    @pytest.mark.asyncio
    async def test_validate_input_invalid(self, agent):
        """Test input validation with invalid data"""
        # Arrange
        invalid_task = {agent_name}Task(
            id="test-task-003",
            input_data={{}}
        )
        
        # Act & Assert
        with pytest.raises(Exception):
            await agent._validate_input(invalid_task)
    
    @pytest.mark.asyncio
    async def test_preprocess_data(self, agent):
        """Test data preprocessing"""
        # Arrange
        input_data = {{"text": "  Test text with  extra spaces  "}}
        
        # Act
        processed = await agent._preprocess_data(input_data)
        
        # Assert
        assert "text" in processed
        assert processed["text"] == "Test text with extra spaces"
    
    @pytest.mark.asyncio
    async def test_calculate_confidence(self, agent):
        """Test confidence calculation"""
        # Arrange
        ai_response = {{"response": "Valid response with good content"}}
        
        # Act
        confidence = await agent._calculate_confidence(ai_response)
        
        # Assert
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_get_capabilities(self, agent):
        """Test agent capabilities"""
        # Act
        capabilities = await agent.get_capabilities()
        
        # Assert
        assert "name" in capabilities
        assert capabilities["name"] == "{agent_name}"
        assert "version" in capabilities
        assert "capabilities" in capabilities
        assert isinstance(capabilities["capabilities"], list)
    
    def test_clean_text(self, agent):
        """Test text cleaning functionality"""
        # Arrange
        dirty_text = "  Text  with   extra   spaces  \\n\\n  "
        
        # Act
        cleaned = agent._clean_text(dirty_text)
        
        # Assert
        assert cleaned == "Text with extra spaces"


class Test{agent_name}AgentFactory:
    """Test suite for {agent_name} agent factory"""
    
    def test_get_agent_singleton(self):
        """Test that factory returns singleton instance"""
        # Act
        agent1 = {agent_name}AgentFactory.get_agent()
        agent2 = {agent_name}AgentFactory.get_agent()
        
        # Assert
        assert agent1 is agent2
        assert isinstance(agent1, {agent_name}Agent)
    
    def test_create_agent_new_instance(self):
        """Test creating new agent instances"""
        # Act
        agent1 = {agent_name}AgentFactory.create_agent()
        agent2 = {agent_name}AgentFactory.create_agent()
        
        # Assert
        assert agent1 is not agent2
        assert isinstance(agent1, {agent_name}Agent)
        assert isinstance(agent2, {agent_name}Agent)


# Performance tests
@pytest.mark.performance
class Test{agent_name}Performance:
    """Performance tests for {agent_name} agent"""
    
    @pytest.mark.asyncio
    async def test_processing_performance(self, benchmark):
        """Benchmark agent processing performance"""
        # Arrange
        agent = {agent_name}Agent()
        task = {agent_name}Task(
            id="perf-test-001",
            input_data={{"text": "Performance test input"}}
        )
        
        # Act & Assert
        result = await benchmark(agent.process_task, task)
        assert result.success is True


# Integration tests
@pytest.mark.integration
class Test{agent_name}Integration:
    """Integration tests for {agent_name} agent"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # Arrange
        agent = {agent_name}Agent()
        task = {agent_name}Task(
            id="integration-test-001",
            input_data={{"text": "Integration test content"}},
            parameters={{"temperature": 0.3}}
        )
        
        # Act
        result = await agent.process_task(task)
        
        # Assert
        assert result.success is True
        assert result.result_data is not None
        assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_training_workflow(self):
        """Test training functionality"""
        # Arrange
        agent = {agent_name}Agent()
        training_data = [
            {{"input": "Sample input 1", "output": "Sample output 1"}},
            {{"input": "Sample input 2", "output": "Sample output 2"}}
        ]
        
        # Act
        success = await agent.train(training_data)
        
        # Assert
        assert success is True
'''
    
    test_output = tests_dir / f"test_{agent_name_lower}_agent.py"
    with open(test_output, 'w') as f:
        f.write(test_content)
    
    print(f"✅ Generated tests: {test_output}")
    
    # Generate __init__.py files if they don't exist
    init_files = [
        agents_dir / "__init__.py",
        tests_dir / "__init__.py"
    ]
    
    for init_file in init_files:
        if not init_file.exists():
            with open(init_file, 'w') as f:
                f.write('"""AI Agents module"""\n')
            print(f"✅ Generated: {init_file}")
    
    # Generate documentation
    docs_dir = project_root / "docs" / "ai_agents"
    docs_dir.mkdir(parents=True, exist_ok=True)
    doc_output = docs_dir / f"{agent_name_lower}.md"
    
    doc_content = f"""# {agent_name} AI Agent

{description}

## Overview

The {agent_name} agent provides AI-powered functionality for {description.lower()}.

## Features

- Intelligent text processing
- Configurable AI models
- Confidence scoring
- Batch processing support
- Training capabilities

## Usage Example

```python
from ai_agents.{agent_name_lower}_agent import {agent_name}Agent, {agent_name}Task

# Create agent instance
agent = {agent_name}Agent(model_name="gpt-3.5-turbo")

# Create task
task = {agent_name}Task(
    id="task-001",
    input_data={{"text": "Your input text here"}},
    parameters={{"temperature": 0.7}}
)

# Process task
result = await agent.process_task(task)

if result.success:
    print(f"Result: {{result.result_data}}")
    print(f"Confidence: {{result.confidence}}")
else:
    print(f"Error: {{result.error_message}}")
```

## Configuration

The agent supports the following configuration options:

- `model_name`: AI model to use (default: "default")
- `max_tokens`: Maximum tokens for generation (default: 1000)
- `temperature`: Creativity level 0-1 (default: 0.7)
- `timeout`: Processing timeout in seconds (default: 30)

## Task Model

```python
class {agent_name}Task(BaseModel):
    id: str                                    # Unique task identifier
    input_data: Dict[str, Any]                # Input data for processing
    parameters: Optional[Dict[str, Any]]      # Processing parameters
    priority: int = 1                         # Task priority (1-10)
    created_at: datetime                      # Task creation time
```

## Result Model

```python
class {agent_name}Result(BaseModel):
    task_id: str                              # Task identifier
    success: bool                             # Whether task succeeded
    result_data: Optional[Dict[str, Any]]     # Result data
    confidence: Optional[float]               # Confidence score (0-1)
    processing_time: float                    # Processing time in seconds
    error_message: Optional[str]              # Error message if failed
    timestamp: datetime                       # Result timestamp
```

## Testing

Run tests for this agent:

```bash
pytest tests/ai_agents/test_{agent_name_lower}_agent.py -v
```

## Training

The agent supports training with custom data:

```python
training_data = [
    {{"input": "Training input 1", "output": "Expected output 1"}},
    {{"input": "Training input 2", "output": "Expected output 2"}}
]

success = await agent.train(training_data)
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
🎉 AI Agent '{agent_name}' generated successfully!

📁 Files created:
  - Agent: ai_agents/{agent_name_lower}_agent.py
  - Tests: tests/ai_agents/test_{agent_name_lower}_agent.py
  - Docs: docs/ai_agents/{agent_name_lower}.md

🔧 Next steps:
  1. Implement the agent logic in the generated files
  2. Configure the AI model and prompts
  3. Update the processing methods
  4. Write comprehensive tests
  5. Train the agent with your data

💡 To use the agent:
```python
from ai_agents.{agent_name_lower}_agent import {agent_name}Agent
agent = {agent_name}Agent()
```
""")


def main():
    parser = argparse.ArgumentParser(description="Generate a new AI agent from template")
    parser.add_argument("agent_name", help="Name of the agent (e.g., ContentAnalyzer)")
    parser.add_argument("--author", default="Developer", help="Author name")
    parser.add_argument("--email", default="dev@ainflue.com", help="Author email")
    parser.add_argument("--description", help="Agent description")
    
    args = parser.parse_args()
    
    # Validate agent name
    if not args.agent_name.isidentifier():
        print("❌ Agent name must be a valid Python identifier")
        sys.exit(1)
    
    # Generate description if not provided
    if not args.description:
        args.description = f"AI agent for {args.agent_name.lower()} operations"
    
    try:
        generate_agent(
            agent_name=args.agent_name,
            author_name=args.author,
            author_email=args.email,
            description=args.description
        )
    except Exception as e:
        print(f"❌ Error generating agent: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()