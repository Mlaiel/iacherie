"""Anthropic Integration - Claude AI API Integration
===============================================

Enterprise integration for Anthropic's Claude AI models with advanced
conversation management and safety features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import httpx


class ClaudeModel(Enum):
    """Claude model types."""
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_2_1 = "claude-2.1"
    CLAUDE_2_0 = "claude-2.0"
    CLAUDE_INSTANT_1_2 = "claude-instant-1.2"


class MessageRole(Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ClaudeMessage:
    """Claude conversation message."""
    role: MessageRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClaudeRequest:
    """Claude API request configuration."""
    id: str
    model: ClaudeModel
    messages: List[ClaudeMessage]
    max_tokens: int = 4096
    temperature: float = 1.0
    top_p: float = 1.0
    top_k: int = 40
    stop_sequences: Optional[List[str]] = None
    stream: bool = False
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClaudeResponse:
    """Claude API response."""
    id: str
    request_id: str
    model: str
    content: str
    usage: Dict[str, int] = field(default_factory=dict)
    stop_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0
    error: Optional[str] = None


class AnthropicIntegration:
    """Comprehensive Anthropic Claude integration."""
    
    def __init__(
        self,
        api_key -> None: str,
        config -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        self.api_key = api_key
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # API configuration
        self.base_url = "https://api.anthropic.com"
        self.api_version = "2023-06-01"
        
        # HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "anthropic-version": self.api_version,
                "Content-Type": "application/json"
            },
            timeout=300.0
        )
        
        # Request tracking
        self.request_count = 0
        self.token_usage = {
            'input_tokens': 0,
            'output_tokens': 0,
            'total_tokens': 0
        }
        
        # Conversation management
        self.active_conversations: Dict[str, List[ClaudeMessage]] = {}
        self.conversation_limits = {
            'max_messages': self.config.get('max_messages_per_conversation', 100),
            'max_tokens_per_conversation': self.config.get('max_tokens_per_conversation', 200000)
        }
        
        # Safety and content filtering
        self.safety_enabled = self.config.get('safety_enabled', True)
        self.content_filters = self.config.get('content_filters', [])
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'model_usage': {},
            'conversation_count': 0,
            'safety_blocks': 0
        }
        
        # Request history
        self.request_history: List[ClaudeResponse] = []
        self.max_history = self.config.get('max_history', 1000)
        
    async def initialize(self) -> None:
        """Initialize the Anthropic integration."""
        # Test API connectivity
        await self._test_connection()
        
        self.logger.info("Anthropic integration initialized")
    
    async def _test_connection(self) -> None:
        """Test API connection."""
        try:
            response = await self.client.get("/v1/models")
            if response.status_code == 200:
                self.logger.info("Anthropic API connection successful")
            else:
                self.logger.warning(f"Anthropic API test returned status: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Anthropic API: {e}")
    
    async def create_conversation(self, conversation_id: Optional[str] = None) -> str:
        """Create a new conversation."""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        self.active_conversations[conversation_id] = []
        self.metrics['conversation_count'] += 1
        
        self.logger.info(f"Created conversation: {conversation_id}")
        return conversation_id
    
    async def add_message_to_conversation(
        self,
        conversation_id -> None: str,
        message -> None: ClaudeMessage
    ) -> None:
        """Add message to conversation."""
        if conversation_id not in self.active_conversations:
            await self.create_conversation(conversation_id)
        
        conversation = self.active_conversations[conversation_id]
        
        # Check conversation limits
        if len(conversation) >= self.conversation_limits['max_messages']:
            # Remove oldest messages
            conversation = conversation[-(self.conversation_limits['max_messages'] - 1):]
            self.active_conversations[conversation_id] = conversation
        
        conversation.append(message)
    
    async def send_message(
        self,
        messages: Union[List[ClaudeMessage], str],
        model: ClaudeModel = ClaudeModel.CLAUDE_3_SONNET,
        conversation_id: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        stream: bool = False,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Union[ClaudeResponse, AsyncGenerator[ClaudeResponse, None]]:
        """Send message to Claude."""
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Handle string input
            if isinstance(messages, str):
                messages = [ClaudeMessage(role=MessageRole.USER, content=messages)]
            
            # Handle conversation context
            if conversation_id:
                if conversation_id not in self.active_conversations:
                    await self.create_conversation(conversation_id)
                
                # Add new messages to conversation
                for message in messages:
                    await self.add_message_to_conversation(conversation_id, message)
                
                # Use full conversation as context
                all_messages = self.active_conversations[conversation_id]
            else:
                all_messages = messages
            
            # Apply safety filters
            if self.safety_enabled:
                for message in all_messages:
                    if await self._check_safety(message.content):
                        self.metrics['safety_blocks'] += 1
                        raise ValueError("Content violates safety guidelines")
            
            # Prepare API request
            api_messages = []
            for msg in all_messages:
                api_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
            
            request_data = {
                "model": model.value,
                "messages": api_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": stream
            }
            
            if system_prompt:
                request_data["system"] = system_prompt
            
            # Add additional parameters
            for key, value in kwargs.items():
                if key in ['top_p', 'top_k', 'stop_sequences']:
                    request_data[key] = value
            
            # Make API request
            if stream:
                return self._handle_streaming_response(
                    request_id, model, start_time, request_data, conversation_id
                )
            else:
                response = await self.client.post("/v1/messages", json=request_data)
                response_data = response.json()
                
                if response.status_code != 200:
                    raise Exception(f"API error: {response_data}")
                
                # Process response
                processing_time = (datetime.now() - start_time).total_seconds()
                
                claude_response = ClaudeResponse(
                    id=response_data.get("id", str(uuid.uuid4())),
                    request_id=request_id,
                    model=response_data.get("model", model.value),
                    content=response_data["content"][0]["text"],
                    usage={
                        'input_tokens': response_data.get("usage", {}).get("input_tokens", 0),
                        'output_tokens': response_data.get("usage", {}).get("output_tokens", 0),
                        'total_tokens': (
                            response_data.get("usage", {}).get("input_tokens", 0) +
                            response_data.get("usage", {}).get("output_tokens", 0)
                        )
                    },
                    stop_reason=response_data.get("stop_reason"),
                    processing_time=processing_time
                )
                
                # Add assistant response to conversation
                if conversation_id:
                    assistant_message = ClaudeMessage(
                        role=MessageRole.ASSISTANT,
                        content=claude_response.content
                    )
                    await self.add_message_to_conversation(conversation_id, assistant_message)
                
                # Update metrics
                await self._update_metrics(claude_response, True)
                
                return claude_response
                
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_response = ClaudeResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content="",
                error=str(e),
                processing_time=processing_time
            )
            
            await self._update_metrics(error_response, False)
            self.logger.error(f"Claude message failed: {e}")
            return error_response
    
    async def _handle_streaming_response(
        self,
        request_id: str,
        model: ClaudeModel,
        start_time: datetime,
        request_data: Dict[str, Any],
        conversation_id: Optional[str]
    ) -> AsyncGenerator[ClaudeResponse, None]:
        """Handle streaming response."""
        try:
            response = await self.client.post("/v1/messages", json=request_data)
            
            if response.status_code != 200:
                error_data = response.json()
                raise Exception(f"API error: {error_data}")
            
            content_chunks = []
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        
                        if data.get("type") == "content_block_delta":
                            content_chunk = data.get("delta", {}).get("text", "")
                            if content_chunk:
                                content_chunks.append(content_chunk)
                                
                                # Yield partial response
                                yield ClaudeResponse(
                                    id=data.get("id", str(uuid.uuid4())),
                                    request_id=request_id,
                                    model=model.value,
                                    content=content_chunk,
                                    metadata={'partial': True}
                                )
                        
                        elif data.get("type") == "message_stop":
                            # Final response
                            complete_content = ''.join(content_chunks)
                            processing_time = (datetime.now() - start_time).total_seconds()
                            
                            final_response = ClaudeResponse(
                                id=data.get("id", str(uuid.uuid4())),
                                request_id=request_id,
                                model=model.value,
                                content=complete_content,
                                usage=data.get("usage", {}),
                                processing_time=processing_time,
                                metadata={'partial': False, 'streaming': True}
                            )
                            
                            # Add to conversation
                            if conversation_id:
                                assistant_message = ClaudeMessage(
                                    role=MessageRole.ASSISTANT,
                                    content=complete_content
                                )
                                await self.add_message_to_conversation(conversation_id, assistant_message)
                            
                            await self._update_metrics(final_response, True)
                            yield final_response
                            
                    except json.JSONDecodeError:
                        continue
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_response = ClaudeResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content="",
                error=str(e),
                processing_time=processing_time
            )
            
            await self._update_metrics(error_response, False)
            yield error_response
    
    async def _check_safety(self, content: str) -> bool:
        """Check content against safety guidelines."""
        # Basic safety checks
        unsafe_patterns = [
            r'\b(how to make.*(bomb|explosive|weapon))\b',
            r'\b(illegal.*(drug|activity))\b',
            r'\b(hack|hacking|exploit)\b'
        ]
        
        import re
        for pattern in unsafe_patterns:
            if re.search(pattern, content.lower()):
                return True
        
        # Custom content filters
        for filter_func in self.content_filters:
            if await filter_func(content):
                return True
        
        return False
    
    async def get_conversation(self, conversation_id: str) -> Optional[List[ClaudeMessage]]:
        """Get conversation history."""
        return self.active_conversations.get(conversation_id)
    
    async def clear_conversation(self, conversation_id -> None: str) -> None:
        """Clear conversation history."""
        if conversation_id in self.active_conversations:
            del self.active_conversations[conversation_id]
            self.logger.info(f"Cleared conversation: {conversation_id}")
    
    async def export_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Export conversation to dictionary."""
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            return None
        
        return {
            'conversation_id': conversation_id,
            'messages': [
                {
                    'role': msg.role.value,
                    'content': msg.content,
                    'metadata': msg.metadata
                }
                for msg in conversation
            ],
            'created_at': datetime.now().isoformat(),
            'message_count': len(conversation)
        }
    
    async def import_conversation(self, conversation_data: Dict[str, Any]) -> str:
        """Import conversation from dictionary."""
        conversation_id = conversation_data['conversation_id']
        messages = []
        
        for msg_data in conversation_data['messages']:
            message = ClaudeMessage(
                role=MessageRole(msg_data['role']),
                content=msg_data['content'],
                metadata=msg_data.get('metadata', {})
            )
            messages.append(message)
        
        self.active_conversations[conversation_id] = messages
        return conversation_id
    
    async def analyze_conversation_sentiment(self, conversation_id: str) -> Dict[str, Any]:
        """Analyze sentiment of conversation."""
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            return {}
        
        # Simple sentiment analysis based on keywords
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'perfect']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'poor']
        
        total_messages = len(conversation)
        positive_count = 0
        negative_count = 0
        
        for message in conversation:
            content_lower = message.content.lower()
            
            for word in positive_words:
                if word in content_lower:
                    positive_count += 1
                    break
            
            for word in negative_words:
                if word in content_lower:
                    negative_count += 1
                    break
        
        if total_messages > 0:
            positive_ratio = positive_count / total_messages
            negative_ratio = negative_count / total_messages
            
            if positive_ratio > negative_ratio:
                overall_sentiment = "positive"
            elif negative_ratio > positive_ratio:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
        else:
            overall_sentiment = "neutral"
            positive_ratio = 0
            negative_ratio = 0
        
        return {
            'overall_sentiment': overall_sentiment,
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio,
            'total_messages': total_messages,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    async def _update_metrics(self, response -> None: ClaudeResponse, success -> None: bool) -> None:
        """Update integration metrics."""
        self.metrics['total_requests'] += 1
        
        if success:
            self.metrics['successful_requests'] += 1
            
            # Update token usage
            if response.usage:
                self.token_usage['input_tokens'] += response.usage.get('input_tokens', 0)
                self.token_usage['output_tokens'] += response.usage.get('output_tokens', 0)
                self.token_usage['total_tokens'] += response.usage.get('total_tokens', 0)
            
            # Update model usage
            if response.model not in self.metrics['model_usage']:
                self.metrics['model_usage'][response.model] = 0
            self.metrics['model_usage'][response.model] += 1
            
        else:
            self.metrics['failed_requests'] += 1
        
        # Update average response time
        total_requests = self.metrics['total_requests']
        current_avg = self.metrics['average_response_time']
        self.metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + response.processing_time) / total_requests
        )
        
        # Add to history
        self.request_history.append(response)
        if len(self.request_history) > self.max_history:
            self.request_history.pop(0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get integration metrics."""
        return {
            'requests': {
                'total': self.metrics['total_requests'],
                'successful': self.metrics['successful_requests'],
                'failed': self.metrics['failed_requests'],
                'success_rate': (
                    self.metrics['successful_requests'] / max(self.metrics['total_requests'], 1)
                ) * 100
            },
            'performance': {
                'average_response_time': self.metrics['average_response_time']
            },
            'usage': {
                'token_usage': self.token_usage,
                'model_usage': self.metrics['model_usage']
            },
            'conversations': {
                'total_conversations': self.metrics['conversation_count'],
                'active_conversations': len(self.active_conversations)
            },
            'safety': {
                'safety_blocks': self.metrics['safety_blocks']
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            # Simple API test
            test_response = await self.send_message(
                "Hello, please respond with 'OK'",
                model=ClaudeModel.CLAUDE_3_HAIKU,
                max_tokens=10
            )
            
            return {
                'status': 'healthy',
                'api_accessible': test_response.error is None,
                'response_time': test_response.processing_time,
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'api_accessible': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        await self.client.aclose()


# Example usage
if __name__ == "__main__":
    async def main() -> None:
        # Initialize Anthropic integration
        anthropic = AnthropicIntegration(
            api_key="your-anthropic-api-key"
        )
        
        await anthropic.initialize()
        
        # Create conversation
        conversation_id = await anthropic.create_conversation()
        
        # Send message
        response = await anthropic.send_message(
            "What is the capital of France?",
            conversation_id=conversation_id,
            model=ClaudeModel.CLAUDE_3_SONNET
        )
        
        print(f"Response: {response.content}")
        
        # Get conversation
        conversation = await anthropic.get_conversation(conversation_id)
        print(f"Conversation has {len(conversation)} messages")
        
        # Get metrics
        metrics = anthropic.get_metrics()
        print(f"Metrics: {json.dumps(metrics, indent=2)}")
        
        await anthropic.cleanup()
    
    # asyncio.run(main())