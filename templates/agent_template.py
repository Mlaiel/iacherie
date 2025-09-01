"""{{agent_name}} AI Agent Template
{{agent_description}}

Author: {{author_name}} ({{author_email}})
Copyright: (c) {{year}} {{author_name}}. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
from abc import ABC, abstractmethod

# AI Agent framework imports
from ai_agents.base_agent import BaseAgent, AgentConfig
from ai_agents.exceptions import AgentException
from ai_agents.memory import AgentMemory
from ai_agents.tools import ToolRegistry
from core.ai_providers import AIProvider
from monitoring.metrics import MetricsCollector
from utils.logger import get_logger

logger = get_logger(__name__)

class {{agent_name}}State(Enum):
    """Agent state enumeration."""
    IDLE = "idle"
    PROCESSING = "processing"
    LEARNING = "learning"
    ERROR = "error"

class {{agent_name}}Capability(Enum):
    """Agent capabilities enumeration."""
    # Define your agent's capabilities here
    CAPABILITY_1 = "capability_1"
    CAPABILITY_2 = "capability_2"
    CAPABILITY_3 = "capability_3"

@dataclass
class {{agent_name}}Config(AgentConfig):
    """Configuration for {{agent_name}} agent."""
    # Inherit base configuration and add agent-specific settings
    
    # AI Model Configuration
    model_name: str = "gpt-4"
    model_temperature: float = 0.7
    max_tokens: int = 2048
    
    # Agent Behavior
    reasoning_depth: int = 3
    memory_retention_days: int = 30
    learning_rate: float = 0.01
    
    # Performance Settings
    max_concurrent_tasks: int = 10
    response_timeout: int = 30
    retry_attempts: int = 3
    
    # Agent-specific configuration
    # Add your configuration parameters here
    specialized_parameter: str = "default_value"
    enable_advanced_reasoning: bool = True
    confidence_threshold: float = 0.8
    
    def validate(self) -> bool:
        """Validate agent configuration."""
        super().validate()
        
        if self.model_temperature < 0 or self.model_temperature > 2:
            raise ValueError("model_temperature must be between 0 and 2")
        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            raise ValueError("confidence_threshold must be between 0 and 1")
        
        return True

class {{agent_name}}Memory(AgentMemory):
    """Enhanced memory system for {{agent_name}} agent."""
    
    def __init__(self, retention_days: int = 30):
        super().__init__(retention_days)
        self.specialized_memory = {}
        self.learning_patterns = []
    
    async def store_learning_pattern(self, pattern: Dict[str, Any]):
        """Store a learning pattern for future reference."""
        pattern["timestamp"] = datetime.utcnow().isoformat()
        self.learning_patterns.append(pattern)
        
        # Keep only recent patterns
        if len(self.learning_patterns) > 1000:
            self.learning_patterns = self.learning_patterns[-1000:]
    
    async def get_relevant_patterns(self, context: str) -> List[Dict[str, Any]]:
        """Retrieve relevant learning patterns based on context."""
        # Implement pattern matching logic
        relevant_patterns = []
        for pattern in self.learning_patterns:
            if self._is_pattern_relevant(pattern, context):
                relevant_patterns.append(pattern)
        
        return relevant_patterns[-10:]  # Return most recent relevant patterns
    
    def _is_pattern_relevant(self, pattern: Dict[str, Any], context: str) -> bool:
        """Check if a learning pattern is relevant to the current context."""
        # Implement relevance scoring logic
        # This is a simple example - you can implement more sophisticated matching
        pattern_context = pattern.get("context", "")
        return context.lower() in pattern_context.lower()

class {{agent_name}}Tools:
    """Tool registry for {{agent_name}} agent."""
    
    def __init__(self):
        self.tools = ToolRegistry()
        self._register_tools()
    
    def _register_tools(self):
        """Register agent-specific tools."""
        # Register your agent's tools here
        self.tools.register("analyze_data", self.analyze_data)
        self.tools.register("generate_insights", self.generate_insights)
        self.tools.register("validate_results", self.validate_results)
    
    async def analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for data analysis."""
        # Implement data analysis logic
        return {
            "analysis_complete": True,
            "insights": ["insight1", "insight2"],
            "confidence": 0.9
        }
    
    async def generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Tool for generating insights."""
        # Implement insight generation logic
        return ["Generated insight 1", "Generated insight 2"]
    
    async def validate_results(self, results: Dict[str, Any]) -> bool:
        """Tool for result validation."""
        # Implement validation logic
        return True

class {{agent_name}}Agent(BaseAgent):
    """{{agent_description}}
    
    This AI agent specializes in:
    - Capability 1: Description
    - Capability 2: Description  
    - Capability 3: Description
    
    The agent uses advanced reasoning and learning capabilities to provide
    intelligent responses and adapt to user needs over time.
    """
    
    def __init__(self, config: {{agent_name}}Config):
        """Initialize the {{agent_name}} agent.
        
        Args:
            config: Agent configuration
        """
        super().__init__(config)
        self.config = config
        self.config.validate()
        
        # Agent state and metrics
        self.state = {{agent_name}}State.IDLE
        self.metrics = MetricsCollector(service_name="{{agent_name_lower}}_agent")
        
        # Initialize agent components
        self.memory = {{agent_name}}Memory(config.memory_retention_days)
        self.tools = {{agent_name}}Tools()
        self.ai_provider = AIProvider(
            model_name=config.model_name,
            temperature=config.model_temperature,
            max_tokens=config.max_tokens
        )
        
        # Agent-specific initialization
        self.capabilities = list({{agent_name}}Capability)
        self.conversation_context = []
        self.learning_buffer = []
        
        logger.info(f"{{agent_name}} agent initialized with {len(self.capabilities)} capabilities")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming request using AI reasoning.
        
        Args:
            request: Request containing message, context, and parameters
            
        Returns:
            Dict containing agent response and metadata
        """
        try:
            self.state = {{agent_name}}State.PROCESSING
            self.metrics.increment_counter("requests_processed")
            start_time = datetime.utcnow()
            
            # Extract request components
            message = request.get("message", "")
            context = request.get("context", {})
            parameters = request.get("parameters", {})
            
            # Validate request
            self._validate_request(request)
            
            # Retrieve relevant memory
            relevant_memory = await self.memory.get_relevant_context(message)
            relevant_patterns = await self.memory.get_relevant_patterns(message)
            
            # Build reasoning context
            reasoning_context = self._build_reasoning_context(
                message, context, relevant_memory, relevant_patterns
            )
            
            # Perform AI reasoning
            response = await self._perform_reasoning(reasoning_context, parameters)
            
            # Post-process response
            final_response = await self._post_process_response(response, context)
            
            # Update memory and learning
            await self._update_memory_and_learning(request, final_response)
            
            # Record metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.record_histogram("processing_time_seconds", processing_time)
            self.metrics.increment_counter("requests_successful")
            
            self.state = {{agent_name}}State.IDLE
            
            return {
                "success": True,
                "response": final_response,
                "confidence": final_response.get("confidence", 0.8),
                "processing_time_seconds": processing_time,
                "capabilities_used": final_response.get("capabilities_used", []),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            self.metrics.increment_counter("requests_failed")
            self.state = {{agent_name}}State.ERROR
            raise AgentException(f"Processing failed: {e}")
    
    def _validate_request(self, request: Dict[str, Any]):
        """Validate incoming request."""
        if not request.get("message"):
            raise ValueError("Request must contain a message")
        
        # Add agent-specific validation
        if len(request["message"]) > 10000:
            raise ValueError("Message too long (max 10000 characters)")
    
    def _build_reasoning_context(
        self, 
        message: str, 
        context: Dict[str, Any],
        relevant_memory: List[Dict[str, Any]],
        relevant_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build comprehensive context for AI reasoning."""
        return {
            "current_message": message,
            "user_context": context,
            "agent_capabilities": [cap.value for cap in self.capabilities],
            "relevant_memory": relevant_memory[-5:],  # Last 5 relevant memories
            "learned_patterns": relevant_patterns,
            "conversation_history": self.conversation_context[-3:],  # Last 3 exchanges
            "agent_config": {
                "reasoning_depth": self.config.reasoning_depth,
                "confidence_threshold": self.config.confidence_threshold,
                "enable_advanced_reasoning": self.config.enable_advanced_reasoning
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _perform_reasoning(
        self, 
        context: Dict[str, Any], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform AI-powered reasoning to generate response."""
        
        # Build system prompt
        system_prompt = self._build_system_prompt()
        
        # Build user prompt with context
        user_prompt = self._build_user_prompt(context, parameters)
        
        # Generate AI response
        ai_response = await self.ai_provider.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=self.config.model_temperature,
            max_tokens=self.config.max_tokens
        )
        
        # Parse and structure response
        structured_response = self._parse_ai_response(ai_response)
        
        # Apply agent-specific reasoning enhancements
        enhanced_response = await self._enhance_reasoning(structured_response, context)
        
        return enhanced_response
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the AI model."""
        return f"""
You are {{agent_name}}, an advanced AI agent specialized in {{agent_description_lower}}.

Your capabilities include:
{chr(10).join(f"- {cap.value.replace('_', ' ').title()}" for cap in self.capabilities)}

Guidelines:
1. Provide accurate, helpful, and contextually relevant responses
2. Use the provided context and memory to inform your responses
3. Indicate your confidence level in your responses
4. Suggest follow-up actions when appropriate
5. Learn from interactions to improve future responses

Response format:
- Provide your main response
- Include confidence score (0.0-1.0)
- List capabilities used
- Suggest next steps if applicable

Always be helpful, accurate, and honest about limitations.
        """
    
    def _build_user_prompt(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> str:
        """Build user prompt with full context."""
        return f"""
Current request: {context['current_message']}

Context information:
- User context: {json.dumps(context['user_context'], indent=2)}
- Relevant memory: {json.dumps(context['relevant_memory'], indent=2)}
- Learned patterns: {json.dumps(context['learned_patterns'], indent=2)}
- Conversation history: {json.dumps(context['conversation_history'], indent=2)}

Parameters: {json.dumps(parameters, indent=2)}

Please process this request using your specialized capabilities and provide a comprehensive response.
        """
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse and structure the AI response."""
        try:
            # Try to parse as JSON first
            if ai_response.strip().startswith('{'):
                return json.loads(ai_response)
        except json.JSONDecodeError:
            pass
        
        # Fallback to structured parsing
        return {
            "content": ai_response,
            "confidence": 0.8,  # Default confidence
            "capabilities_used": [{{agent_name}}Capability.CAPABILITY_1.value],
            "suggested_actions": []
        }
    
    async def _enhance_reasoning(
        self, 
        response: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply agent-specific reasoning enhancements."""
        
        # Apply confidence threshold
        if response.get("confidence", 0) < self.config.confidence_threshold:
            response["warning"] = "Low confidence response - consider requesting clarification"
        
        # Add agent-specific insights
        if self.config.enable_advanced_reasoning:
            insights = await self._generate_advanced_insights(response, context)
            response["advanced_insights"] = insights
        
        # Validate response using tools
        if self.tools:
            validation_result = await self.tools.tools.execute("validate_results", response)
            response["validation_passed"] = validation_result
        
        return response
    
    async def _generate_advanced_insights(
        self, 
        response: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate advanced insights using agent capabilities."""
        insights = []
        
        # Analyze patterns in the interaction
        if context.get("learned_patterns"):
            insights.append("Applied learned patterns from previous interactions")
        
        # Check for improvement opportunities
        if response.get("confidence", 0) < 0.9:
            insights.append("Response could be improved with additional context")
        
        # Add domain-specific insights
        insights.extend(await self._domain_specific_insights(response, context))
        
        return insights
    
    async def _domain_specific_insights(
        self, 
        response: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate domain-specific insights."""
        # Implement domain-specific insight generation
        # This should be customized based on your agent's specialization
        return [
            "Domain insight 1",
            "Domain insight 2"
        ]
    
    async def _post_process_response(
        self, 
        response: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Post-process the response before returning."""
        
        # Add metadata
        response["agent_name"] = "{{agent_name}}"
        response["agent_version"] = "1.0.0"
        response["processing_timestamp"] = datetime.utcnow().isoformat()
        
        # Format response for better readability
        if "content" in response:
            response["formatted_content"] = self._format_content(response["content"])
        
        # Add suggestions for follow-up
        response["suggested_follow_ups"] = await self._generate_follow_up_suggestions(response, context)
        
        return response
    
    def _format_content(self, content: str) -> str:
        """Format content for better presentation."""
        # Add any formatting logic specific to your agent
        return content
    
    async def _generate_follow_up_suggestions(
        self, 
        response: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate suggestions for follow-up interactions."""
        suggestions = []
        
        # Basic suggestions
        if response.get("confidence", 0) < 0.8:
            suggestions.append("Consider providing more specific details for better assistance")
        
        # Add domain-specific suggestions
        # Customize this based on your agent's specialization
        
        return suggestions
    
    async def _update_memory_and_learning(
        self, 
        request: Dict[str, Any], 
        response: Dict[str, Any]
    ):
        """Update agent memory and learning from the interaction."""
        
        # Store interaction in memory
        interaction = {
            "request": request,
            "response": response,
            "timestamp": datetime.utcnow().isoformat(),
            "success": response.get("success", False),
            "confidence": response.get("confidence", 0)
        }
        
        await self.memory.store_interaction(interaction)
        
        # Extract learning patterns
        if response.get("success") and response.get("confidence", 0) > 0.8:
            learning_pattern = {
                "context": request.get("message", ""),
                "successful_approach": response.get("capabilities_used", []),
                "confidence": response.get("confidence"),
                "effectiveness_score": 1.0
            }
            await self.memory.store_learning_pattern(learning_pattern)
        
        # Update conversation context
        self.conversation_context.append({
            "user_message": request.get("message", ""),
            "agent_response": response.get("content", ""),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep conversation context manageable
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]
    
    async def learn_from_feedback(self, feedback: Dict[str, Any]):
        """Learn from user feedback to improve future responses."""
        try:
            self.state = {{agent_name}}State.LEARNING
            
            # Process feedback
            feedback_score = feedback.get("score", 0)  # 0-5 scale
            feedback_text = feedback.get("text", "")
            interaction_id = feedback.get("interaction_id")
            
            # Update learning patterns based on feedback
            if feedback_score >= 4:  # Positive feedback
                # Reinforce successful patterns
                await self._reinforce_learning_patterns(interaction_id, 1.2)
            elif feedback_score <= 2:  # Negative feedback
                # Adjust patterns that led to poor outcomes
                await self._adjust_learning_patterns(interaction_id, 0.8)
            
            # Store feedback for future reference
            await self.memory.store_feedback(feedback)
            
            self.state = {{agent_name}}State.IDLE
            logger.info(f"Learned from feedback: score={feedback_score}")
            
        except Exception as e:
            logger.error(f"Learning from feedback failed: {e}")
            self.state = {{agent_name}}State.ERROR
    
    async def _reinforce_learning_patterns(self, interaction_id: str, multiplier: float):
        """Reinforce learning patterns that led to positive outcomes."""
        # Implement reinforcement learning logic
        pass
    
    async def _adjust_learning_patterns(self, interaction_id: str, multiplier: float):
        """Adjust learning patterns that led to negative outcomes."""
        # Implement pattern adjustment logic
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities."""
        return [cap.value for cap in self.capabilities]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            "agent_name": "{{agent_name}}",
            "state": self.state.value,
            "capabilities": self.get_capabilities(),
            "memory_size": len(self.memory.interactions),
            "conversation_length": len(self.conversation_context),
            "metrics": self.metrics.get_all_metrics(),
            "config": {
                "model_name": self.config.model_name,
                "temperature": self.config.model_temperature,
                "confidence_threshold": self.config.confidence_threshold
            },
            "timestamp": datetime.utcnow().isoformat()
        }

# Agent factory function
def create_{{agent_name_lower}}_agent(config: Optional[Dict[str, Any]] = None) -> {{agent_name}}Agent:
    """Create and configure a {{agent_name}} agent instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured {{agent_name}}Agent instance
    """
    if config is None:
        config = {}
    
    agent_config = {{agent_name}}Config(**config)
    return {{agent_name}}Agent(agent_config)

# Example usage
async def main():
    """Example usage of the {{agent_name}} agent."""
    try:
        # Create agent
        agent = create_{{agent_name_lower}}_agent({
            "model_temperature": 0.7,
            "confidence_threshold": 0.8,
            "enable_advanced_reasoning": True
        })
        
        # Process a request
        request = {
            "message": "Hello, I need help with analyzing some data.",
            "context": {
                "user_id": "user123",
                "session_id": "session456"
            },
            "parameters": {
                "analysis_type": "comprehensive"
            }
        }
        
        result = await agent.process_request(request)
        print(f"Agent response: {result}")
        
        # Get agent status
        status = agent.get_status()
        print(f"Agent status: {status}")
        
        # Provide feedback
        feedback = {
            "score": 5,
            "text": "Excellent analysis and insights!",
            "interaction_id": "interaction123"
        }
        await agent.learn_from_feedback(feedback)
        
    except Exception as e:
        logger.error(f"Agent example failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())