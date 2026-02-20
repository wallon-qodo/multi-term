"""VSCode connector for bidirectional communication with VSCode extension."""

import asyncio
import json
import logging
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import websockets
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FileLocation:
    """Represents a file location with optional line/column."""

    path: Path
    line: Optional[int] = None
    column: Optional[int] = None

    def __str__(self) -> str:
        result = str(self.path)
        if self.line:
            result += f":{self.line}"
            if self.column:
                result += f":{self.column}"
        return result


@dataclass
class CodeChange:
    """Represents a code change to apply."""

    start_line: int
    end_line: int
    new_text: str
    start_column: int = 0
    end_column: int = 0


class VSCodeConnector:
    """Connector for communicating with VSCode extension via WebSocket."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        """Initialize VSCode connector.

        Args:
            host: VSCode extension server host
            port: VSCode extension server port
        """
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._connected = False
        self._message_id = 0
        self._pending_responses: Dict[int, asyncio.Future] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}

        logger.info(f"VSCodeConnector initialized (server: {self.uri})")

    async def connect(self, timeout: float = 5.0) -> bool:
        """Connect to VSCode extension.

        Args:
            timeout: Connection timeout in seconds

        Returns:
            True if connected successfully
        """
        try:
            self._websocket = await asyncio.wait_for(
                websockets.connect(self.uri), timeout=timeout
            )
            self._connected = True

            # Start message receiver
            asyncio.create_task(self._receive_messages())

            logger.info("Connected to VSCode")
            return True

        except asyncio.TimeoutError:
            logger.error("Connection to VSCode timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to VSCode: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect from VSCode extension."""
        if self._websocket:
            await self._websocket.close()
            self._websocket = None
            self._connected = False
            logger.info("Disconnected from VSCode")

    def is_connected(self) -> bool:
        """Check if connected to VSCode."""
        return self._connected and self._websocket is not None

    async def _receive_messages(self) -> None:
        """Receive and process messages from VSCode."""
        if not self._websocket:
            return

        try:
            async for message in self._websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        except websockets.exceptions.ConnectionClosed:
            self._connected = False
            logger.info("VSCode connection closed")
        except Exception as e:
            logger.error(f"Error in receive loop: {e}")
            self._connected = False

    async def _handle_message(self, data: Dict[str, Any]) -> None:
        """Handle incoming message from VSCode.

        Args:
            data: Message data
        """
        message_type = data.get("type")
        message_id = data.get("messageId")

        # Handle response to pending request
        if message_id and message_id in self._pending_responses:
            future = self._pending_responses.pop(message_id)
            future.set_result(data)
            return

        # Handle events
        if message_type and message_type in self._event_handlers:
            for handler in self._event_handlers[message_type]:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")

        logger.debug(f"Received message: {message_type}")

    async def _send_message(
        self, message: Dict[str, Any], wait_response: bool = False, timeout: float = 10.0
    ) -> Optional[Dict[str, Any]]:
        """Send message to VSCode.

        Args:
            message: Message to send
            wait_response: Whether to wait for response
            timeout: Response timeout in seconds

        Returns:
            Response data if wait_response is True, None otherwise
        """
        if not self._websocket or not self._connected:
            logger.error("Not connected to VSCode")
            return None

        # Add message ID
        self._message_id += 1
        message["id"] = self._message_id

        # Create future for response if needed
        future = None
        if wait_response:
            future = asyncio.Future()
            self._pending_responses[self._message_id] = future

        try:
            # Send message
            await self._websocket.send(json.dumps(message))
            logger.debug(f"Sent message: {message.get('type')}")

            # Wait for response if requested
            if future:
                try:
                    response = await asyncio.wait_for(future, timeout=timeout)
                    return response
                except asyncio.TimeoutError:
                    logger.error("Response timeout")
                    self._pending_responses.pop(self._message_id, None)
                    return None

            return None

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            if self._message_id in self._pending_responses:
                self._pending_responses.pop(self._message_id)
            return None

    async def open_file(
        self, file_path: Path, line: Optional[int] = None, column: Optional[int] = None
    ) -> bool:
        """Open a file in VSCode.

        Args:
            file_path: Path to file
            line: Line number (1-indexed)
            column: Column number (1-indexed)

        Returns:
            True if successful
        """
        message = {
            "type": "openFile",
            "filePath": str(file_path.absolute()),
        }

        if line is not None:
            message["line"] = line
        if column is not None:
            message["column"] = column

        response = await self._send_message(message, wait_response=True)

        if response and response.get("success"):
            logger.info(f"Opened file in VSCode: {file_path}")
            return True

        logger.error(f"Failed to open file in VSCode: {file_path}")
        return False

    async def apply_changes(
        self, file_path: Path, changes: List[CodeChange], description: Optional[str] = None
    ) -> bool:
        """Apply code changes to a file in VSCode.

        Args:
            file_path: Path to file
            changes: List of changes to apply
            description: Optional description of changes

        Returns:
            True if successful
        """
        message = {
            "type": "applyChanges",
            "filePath": str(file_path.absolute()),
            "changes": [
                {
                    "startLine": change.start_line,
                    "endLine": change.end_line,
                    "startColumn": change.start_column,
                    "endColumn": change.end_column,
                    "newText": change.new_text,
                }
                for change in changes
            ],
        }

        if description:
            message["description"] = description

        response = await self._send_message(message, wait_response=True)

        if response and response.get("success"):
            logger.info(f"Applied {len(changes)} changes to {file_path}")
            return True

        logger.error(f"Failed to apply changes to {file_path}")
        return False

    async def jump_to_line(self, file_path: Path, line: int, column: int = 0) -> bool:
        """Jump to a specific line in a file.

        Args:
            file_path: Path to file
            line: Line number (1-indexed)
            column: Column number (1-indexed)

        Returns:
            True if successful
        """
        message = {
            "type": "jumpToLine",
            "filePath": str(file_path.absolute()),
            "line": line,
            "column": column,
        }

        response = await self._send_message(message, wait_response=True)

        if response and response.get("success"):
            logger.info(f"Jumped to {file_path}:{line}")
            return True

        logger.error(f"Failed to jump to {file_path}:{line}")
        return False

    async def get_context(self) -> Optional[Dict[str, Any]]:
        """Get current VSCode context (active file, selection, etc.).

        Returns:
            Context dictionary or None if failed
        """
        message = {"type": "getContext"}

        response = await self._send_message(message, wait_response=True)

        if response and "context" in response:
            logger.info("Retrieved VSCode context")
            return response["context"]

        logger.error("Failed to get VSCode context")
        return None

    async def ping(self) -> bool:
        """Ping VSCode to check connection.

        Returns:
            True if VSCode responds
        """
        message = {"type": "ping"}

        response = await self._send_message(message, wait_response=True, timeout=2.0)

        return response is not None and response.get("type") == "pong"

    def on_event(self, event_type: str, handler: Callable) -> None:
        """Register event handler.

        Args:
            event_type: Type of event to listen for
            handler: Async callback function
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []

        if handler not in self._event_handlers[event_type]:
            self._event_handlers[event_type].append(handler)
            logger.debug(f"Registered handler for {event_type}")

    def remove_event_handler(self, event_type: str, handler: Callable) -> None:
        """Remove event handler.

        Args:
            event_type: Event type
            handler: Handler to remove
        """
        if event_type in self._event_handlers:
            if handler in self._event_handlers[event_type]:
                self._event_handlers[event_type].remove(handler)
                logger.debug(f"Removed handler for {event_type}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Convenience functions for synchronous usage
class VSCodeSync:
    """Synchronous wrapper for VSCodeConnector."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.connector = VSCodeConnector(host, port)
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _run_async(self, coro):
        """Run async coroutine synchronously."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
        return self._loop.run_until_complete(coro)

    def connect(self) -> bool:
        """Connect to VSCode."""
        return self._run_async(self.connector.connect())

    def disconnect(self) -> None:
        """Disconnect from VSCode."""
        self._run_async(self.connector.disconnect())

    def open_file(self, file_path: Path, line: Optional[int] = None) -> bool:
        """Open file in VSCode."""
        return self._run_async(self.connector.open_file(file_path, line))

    def apply_changes(self, file_path: Path, changes: List[CodeChange]) -> bool:
        """Apply changes to file."""
        return self._run_async(self.connector.apply_changes(file_path, changes))

    def jump_to_line(self, file_path: Path, line: int) -> bool:
        """Jump to line in file."""
        return self._run_async(self.connector.jump_to_line(file_path, line))

    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connector.is_connected()
