"""Session lifecycle management with direct Anthropic API integration."""

import os
import time
import uuid
from typing import Dict, Optional
from dataclasses import dataclass

from ..api import AnthropicClient, TokenTracker, CacheManager, VisionHandler
from ..api.anthropic_client import ConversationManager


@dataclass
class APISessionInfo:
    """Metadata for an API-based Claude session."""
    session_id: str
    name: str
    api_client: AnthropicClient
    conversation_manager: ConversationManager
    token_tracker: TokenTracker
    cache_manager: CacheManager
    vision_handler: VisionHandler
    created_at: float
    working_directory: str
    model: str


class APISessionManager:
    """
    Manages lifecycle of multiple Claude API sessions.

    This replaces PTY-based sessions with direct API integration:
    - Real token tracking from API responses
    - Prompt caching for 90% cost reduction
    - Vision API support for images
    - Streaming responses
    - Better error handling
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "claude-sonnet-4-5-20250929",
        enable_prompt_caching: bool = True,
    ):
        """
        Initialize API session manager.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            default_model: Default model to use
            enable_prompt_caching: Enable prompt caching for cost reduction
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.default_model = default_model
        self.enable_prompt_caching = enable_prompt_caching

        self.sessions: Dict[str, APISessionInfo] = {}
        self._session_counter = 0

        # Global token tracker
        self.global_token_tracker = TokenTracker()

    def create_session(
        self,
        name: Optional[str] = None,
        working_dir: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Create a new Claude API session.

        Args:
            name: Human-readable session name
            working_dir: Working directory for the session
            model: Model to use (defaults to default_model)
            system_prompt: Optional system prompt

        Returns:
            session_id: UUID string for the new session
        """
        session_id = str(uuid.uuid4())
        self._session_counter += 1

        if name is None:
            name = f"Session {self._session_counter}"

        if model is None:
            model = self.default_model

        if working_dir is None:
            # Create a unique working directory for this session
            sessions_root = os.path.join(
                os.path.expanduser("~"),
                "Desktop",
                "multi-claude-sessions",
                "sessions"
            )
            os.makedirs(sessions_root, exist_ok=True)

            # Generate filesystem-safe directory name
            from ..utils.naming import generate_unique_directory_name
            dir_name = generate_unique_directory_name(
                base_name=name if name else f"Session {self._session_counter}",
                parent_dir=sessions_root,
                session_id=session_id
            )
            working_dir = os.path.join(sessions_root, dir_name)
            os.makedirs(working_dir, exist_ok=True)

        # Create API client
        api_client = AnthropicClient(
            api_key=self.api_key,
            model=model,
            enable_prompt_caching=self.enable_prompt_caching,
        )

        # Create conversation manager with system prompt
        conversation_manager = ConversationManager()

        # Store system prompt if provided (for prompt caching)
        if system_prompt:
            conversation_manager.system_prompt = system_prompt

        # Create cache manager
        cache_manager = CacheManager(
            enable_caching=self.enable_prompt_caching,
        )

        # Create vision handler
        vision_handler = VisionHandler()

        # Create session info
        session_info = APISessionInfo(
            session_id=session_id,
            name=name,
            api_client=api_client,
            conversation_manager=conversation_manager,
            token_tracker=self.global_token_tracker,
            cache_manager=cache_manager,
            vision_handler=vision_handler,
            created_at=time.time(),
            working_directory=working_dir,
            model=model,
        )

        self.sessions[session_id] = session_info

        return session_id

    async def send_message(
        self,
        session_id: str,
        prompt: str,
        images: Optional[list] = None,
    ) -> tuple[str, int, int, int]:
        """
        Send a message in a session with API.

        Args:
            session_id: Session identifier
            prompt: User prompt
            images: Optional list of image paths

        Returns:
            Tuple of (response_text, input_tokens, output_tokens, cached_tokens)
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Add user message to history
        session.conversation_manager.add_user_message(prompt)

        # Get conversation history
        messages = session.conversation_manager.get_messages()

        # Build system prompt with caching
        system = None
        if hasattr(session.conversation_manager, 'system_prompt'):
            system = session.cache_manager.build_cached_system_prompt(
                session.conversation_manager.system_prompt
            )

        # Send message
        response_text, input_tokens, output_tokens, cached_tokens = (
            await session.api_client.send_message_simple(
                prompt=prompt,
                conversation_history=messages[:-1],  # Exclude current message
                system=system,
            )
        )

        # Add assistant response to history
        session.conversation_manager.add_assistant_message(response_text)

        # Update token counts
        session.conversation_manager.update_token_count(input_tokens, output_tokens)

        # Track tokens
        session.token_tracker.track_request(
            session_id=session_id,
            model_name=session.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
        )

        return response_text, input_tokens, output_tokens, cached_tokens

    async def stream_message(
        self,
        session_id: str,
        prompt: str,
        callback,
        images: Optional[list] = None,
    ) -> tuple[int, int, int]:
        """
        Stream a message in a session with API.

        Args:
            session_id: Session identifier
            prompt: User prompt
            callback: Callback function for streaming chunks
            images: Optional list of image paths

        Returns:
            Tuple of (input_tokens, output_tokens, cached_tokens)
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Add user message to history
        session.conversation_manager.add_user_message(prompt)

        # Get conversation history
        messages = session.conversation_manager.get_messages()

        # Build system prompt with caching
        system = None
        if hasattr(session.conversation_manager, 'system_prompt'):
            system = session.cache_manager.build_cached_system_prompt(
                session.conversation_manager.system_prompt
            )

        # Stream message
        response_text = ""
        input_tokens = 0
        output_tokens = 0
        cached_tokens = 0

        async for chunk in session.api_client.send_message(
            messages=messages,
            system=system,
            stream=True,
        ):
            if chunk.type == "content":
                response_text += chunk.content
                callback(chunk.content)
            elif chunk.type == "token_usage":
                input_tokens = chunk.input_tokens
                output_tokens = chunk.output_tokens
                cached_tokens = chunk.cached_tokens
            elif chunk.type == "error":
                callback(f"\n❌ Error: {chunk.error}\n")
                raise RuntimeError(chunk.error)

        # Add assistant response to history
        session.conversation_manager.add_assistant_message(response_text)

        # Update token counts
        session.conversation_manager.update_token_count(input_tokens, output_tokens)

        # Track tokens
        session.token_tracker.track_request(
            session_id=session_id,
            model_name=session.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
        )

        return input_tokens, output_tokens, cached_tokens

    async def terminate_session(self, session_id: str) -> None:
        """
        Gracefully terminate a session.

        Args:
            session_id: UUID of session to terminate
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            await session.api_client.close()
            del self.sessions[session_id]

    def get_session(self, session_id: str) -> Optional[APISessionInfo]:
        """
        Get session information by ID.

        Args:
            session_id: UUID of session to retrieve

        Returns:
            APISessionInfo if session exists, None otherwise
        """
        return self.sessions.get(session_id)

    def list_sessions(self) -> list:
        """
        List all active sessions.

        Returns:
            List of APISessionInfo objects for all active sessions
        """
        return list(self.sessions.values())

    def get_session_usage(self, session_id: str) -> Optional[dict]:
        """
        Get token usage for a session.

        Args:
            session_id: Session identifier

        Returns:
            Usage dictionary if session exists, None otherwise
        """
        session_usage = self.global_token_tracker.get_session_usage(session_id)
        if session_usage:
            return session_usage.to_dict()
        return None

    def get_global_usage(self) -> dict:
        """
        Get total usage across all sessions.

        Returns:
            Usage dictionary
        """
        return self.global_token_tracker.export_usage_report()

    def clear_session_history(self, session_id: str) -> bool:
        """
        Clear conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session exists, False otherwise
        """
        session = self.sessions.get(session_id)
        if session:
            session.conversation_manager.clear_history()
            return True
        return False

    def update_session_model(self, session_id: str, model: str) -> bool:
        """
        Update the model for a session.

        Args:
            session_id: Session identifier
            model: New model name

        Returns:
            True if session exists, False otherwise
        """
        session = self.sessions.get(session_id)
        if session:
            session.api_client.update_model(model)
            session.model = model
            return True
        return False
