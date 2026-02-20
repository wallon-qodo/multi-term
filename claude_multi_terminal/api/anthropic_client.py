"""Direct Anthropic API client with streaming support."""

import asyncio
import os
from typing import AsyncIterator, Dict, List, Optional, Callable, Any
from dataclasses import dataclass

try:
    from anthropic import Anthropic, AsyncAnthropic
    from anthropic.types import Message, MessageStreamEvent
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class StreamChunk:
    """Represents a chunk of streaming response."""

    type: str  # 'content', 'token_usage', 'error', 'complete'
    content: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    error: Optional[str] = None


class AnthropicClient:
    """
    Direct Anthropic API client replacing PTY-based Claude CLI.

    Features:
    - Streaming responses with low latency
    - Automatic prompt caching
    - Real token tracking from API
    - Connection pooling
    - Error handling and retries
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        enable_prompt_caching: bool = True,
    ):
        """
        Initialize Anthropic API client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            enable_prompt_caching: Enable prompt caching for cost reduction
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.enable_prompt_caching = enable_prompt_caching

        # Initialize async client
        self.client = AsyncAnthropic(api_key=self.api_key)

        # Connection pooling handled by httpx internally
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1.0

    async def send_message(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        stream: bool = True,
    ) -> AsyncIterator[StreamChunk]:
        """
        Send a message to Claude API with streaming.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt
            stream: Whether to stream the response

        Yields:
            StreamChunk objects containing content or metadata
        """
        # Build request parameters
        params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages,
        }

        # Add system prompt with caching if enabled
        if system:
            if self.enable_prompt_caching:
                # Use prompt caching to reduce costs
                # System prompts are typically static and repeated
                params["system"] = [
                    {
                        "type": "text",
                        "text": system,
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
            else:
                params["system"] = system

        # Execute with retries
        for attempt in range(self.max_retries):
            try:
                if stream:
                    async for chunk in self._stream_message(params):
                        yield chunk
                    return
                else:
                    # Non-streaming response
                    response = await self.client.messages.create(**params)

                    # Extract token usage
                    usage = response.usage
                    input_tokens = usage.input_tokens
                    output_tokens = usage.output_tokens
                    cached_tokens = getattr(usage, 'cache_read_input_tokens', 0)

                    # Yield content
                    content = ""
                    for block in response.content:
                        if block.type == "text":
                            content += block.text

                    yield StreamChunk(
                        type="content",
                        content=content,
                    )

                    # Yield token usage
                    yield StreamChunk(
                        type="token_usage",
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cached_tokens=cached_tokens,
                    )

                    # Yield completion
                    yield StreamChunk(type="complete")
                    return

            except Exception as e:
                if attempt < self.max_retries - 1:
                    # Retry with exponential backoff
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    # Final attempt failed
                    yield StreamChunk(
                        type="error",
                        error=f"API error: {str(e)}",
                    )
                    return

    async def _stream_message(
        self,
        params: Dict[str, Any],
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream a message from the API.

        Args:
            params: Request parameters

        Yields:
            StreamChunk objects
        """
        try:
            async with self.client.messages.stream(**params) as stream:
                # Track token usage
                input_tokens = 0
                output_tokens = 0
                cached_tokens = 0

                async for event in stream:
                    # Handle different event types
                    if event.type == "message_start":
                        # Extract initial usage information
                        if hasattr(event, 'message') and hasattr(event.message, 'usage'):
                            usage = event.message.usage
                            input_tokens = usage.input_tokens
                            cached_tokens = getattr(usage, 'cache_read_input_tokens', 0)

                    elif event.type == "content_block_delta":
                        # Stream content chunks
                        if hasattr(event, 'delta') and hasattr(event.delta, 'text'):
                            yield StreamChunk(
                                type="content",
                                content=event.delta.text,
                            )

                    elif event.type == "message_delta":
                        # Update output token count
                        if hasattr(event, 'usage'):
                            output_tokens = event.usage.output_tokens

                    elif event.type == "message_stop":
                        # Final token usage
                        yield StreamChunk(
                            type="token_usage",
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            cached_tokens=cached_tokens,
                        )

                        # Signal completion
                        yield StreamChunk(type="complete")

        except Exception as e:
            yield StreamChunk(
                type="error",
                error=f"Streaming error: {str(e)}",
            )

    async def send_message_simple(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        system: Optional[str] = None,
    ) -> tuple[str, int, int, int]:
        """
        Send a simple message and return the complete response.

        Args:
            prompt: User prompt
            conversation_history: Optional conversation history
            system: Optional system prompt

        Returns:
            Tuple of (response_text, input_tokens, output_tokens, cached_tokens)
        """
        # Build messages
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})

        # Collect response
        response_text = ""
        input_tokens = 0
        output_tokens = 0
        cached_tokens = 0

        async for chunk in self.send_message(messages, system=system, stream=True):
            if chunk.type == "content":
                response_text += chunk.content
            elif chunk.type == "token_usage":
                input_tokens = chunk.input_tokens
                output_tokens = chunk.output_tokens
                cached_tokens = chunk.cached_tokens
            elif chunk.type == "error":
                raise RuntimeError(chunk.error)

        return response_text, input_tokens, output_tokens, cached_tokens

    async def cancel_current_request(self) -> None:
        """
        Cancel the current API request.

        Note: HTTP requests are cancelled by breaking the async iteration.
        """
        # The stream will be cancelled when the async context exits
        # This is handled automatically by the async with block
        pass

    def update_model(self, model: str) -> None:
        """Update the model to use for future requests."""
        self.model = model

    def update_temperature(self, temperature: float) -> None:
        """Update the temperature for future requests."""
        self.temperature = max(0.0, min(1.0, temperature))

    def update_max_tokens(self, max_tokens: int) -> None:
        """Update the max tokens for future requests."""
        self.max_tokens = max(1, min(8192, max_tokens))

    async def close(self) -> None:
        """Close the API client and cleanup resources."""
        await self.client.close()


class ConversationManager:
    """
    Manages conversation history for continuous interactions.

    Maintains message history and handles context management.
    """

    def __init__(self, max_history_tokens: int = 100000):
        """
        Initialize conversation manager.

        Args:
            max_history_tokens: Maximum tokens to keep in history
        """
        self.messages: List[Dict[str, Any]] = []
        self.max_history_tokens = max_history_tokens
        self.total_tokens = 0

    def add_user_message(self, content: str) -> None:
        """Add a user message to history."""
        self.messages.append({
            "role": "user",
            "content": content,
        })

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to history."""
        self.messages.append({
            "role": "assistant",
            "content": content,
        })

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get the current message history."""
        return self.messages.copy()

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.messages.clear()
        self.total_tokens = 0

    def prune_history(self, target_tokens: Optional[int] = None) -> None:
        """
        Prune old messages to stay under token limit.

        Args:
            target_tokens: Target token count (defaults to max_history_tokens)
        """
        if target_tokens is None:
            target_tokens = self.max_history_tokens

        # Simple pruning: remove oldest messages
        # Keep at least 1 message pair (user + assistant)
        while len(self.messages) > 2 and self.total_tokens > target_tokens:
            # Remove oldest pair
            self.messages.pop(0)
            if self.messages:
                self.messages.pop(0)

            # Rough estimate: recalculate tokens
            # In practice, you'd use tiktoken for accurate counts
            self.total_tokens = sum(len(m["content"]) // 4 for m in self.messages)

    def update_token_count(self, input_tokens: int, output_tokens: int) -> None:
        """Update the total token count."""
        self.total_tokens = input_tokens + output_tokens
