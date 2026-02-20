"""
WebSocket Handler for Real-time Session Sync

Handles WebSocket connections, message routing, and conflict resolution.
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """WebSocket message types"""
    JOIN = "join"
    LEAVE = "leave"
    CURSOR_MOVE = "cursor_move"
    INPUT = "input"
    OUTPUT = "output"
    MESSAGE = "message"
    SESSION_UPDATE = "session_update"
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"
    ERROR = "error"


@dataclass
class WebSocketMessage:
    """Represents a WebSocket message"""
    type: MessageType
    data: Dict[str, Any]
    user_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps({
            "type": self.type.value,
            "data": self.data,
            "user_id": self.user_id,
            "timestamp": self.timestamp
        })

    @classmethod
    def from_json(cls, data: str) -> 'WebSocketMessage':
        """Create from JSON string"""
        parsed = json.loads(data)
        return cls(
            type=MessageType(parsed['type']),
            data=parsed['data'],
            user_id=parsed.get('user_id'),
            timestamp=parsed.get('timestamp', datetime.now().isoformat())
        )


class ConflictResolver:
    """Handles conflicts in collaborative editing"""

    def __init__(self):
        self.operation_queue: List[Dict[str, Any]] = []

    def resolve_input_conflict(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve conflicting input operations using Last-Write-Wins strategy
        with timestamp ordering
        """
        if not operations:
            return {}

        # Sort by timestamp
        sorted_ops = sorted(operations, key=lambda x: x.get('timestamp', ''))

        # Return the last operation
        return sorted_ops[-1]

    def resolve_cursor_conflict(self, cursors: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
        """
        Resolve cursor position conflicts - keep all cursors
        but mark the most recent one as active
        """
        if not cursors:
            return {}

        # Find most recent cursor
        latest_user = max(
            cursors.items(),
            key=lambda x: x[1].get('timestamp', '')
        )[0]

        # Add active flag
        result = {}
        for user_id, cursor in cursors.items():
            result[user_id] = {
                **cursor,
                'active': user_id == latest_user
            }

        return result

    def merge_session_state(self, base: Dict[str, Any], updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple session state updates using three-way merge
        """
        result = base.copy()

        for update in updates:
            for key, value in update.items():
                if key not in result:
                    result[key] = value
                elif isinstance(value, dict) and isinstance(result[key], dict):
                    # Recursive merge for nested dicts
                    result[key] = self._merge_dicts(result[key], value)
                else:
                    # Prefer newer values
                    result[key] = value

        return result

    def _merge_dicts(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge dictionaries"""
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result


class MessageRouter:
    """Routes WebSocket messages to appropriate handlers"""

    def __init__(self):
        self.handlers: Dict[MessageType, Callable] = {}

    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a message handler"""
        self.handlers[message_type] = handler

    async def route(self, message: WebSocketMessage) -> Optional[Any]:
        """Route a message to its handler"""
        handler = self.handlers.get(message.type)
        if not handler:
            logger.warning(f"No handler registered for message type: {message.type}")
            return None

        try:
            return await handler(message)
        except Exception as e:
            logger.error(f"Error handling message {message.type}: {e}")
            return None


class SessionSync:
    """Manages session synchronization between participants"""

    def __init__(self):
        self.pending_operations: Dict[str, List[Dict[str, Any]]] = {}
        self.acknowledged_operations: Dict[str, set] = {}
        self.conflict_resolver = ConflictResolver()

    def add_operation(self, session_id: str, operation: Dict[str, Any]):
        """Add an operation to the pending queue"""
        if session_id not in self.pending_operations:
            self.pending_operations[session_id] = []

        self.pending_operations[session_id].append(operation)

    def acknowledge_operation(self, session_id: str, operation_id: str, user_id: str):
        """Mark an operation as acknowledged by a user"""
        key = f"{session_id}:{operation_id}"
        if key not in self.acknowledged_operations:
            self.acknowledged_operations[key] = set()

        self.acknowledged_operations[key].add(user_id)

    def is_operation_synced(self, session_id: str, operation_id: str, participant_count: int) -> bool:
        """Check if an operation has been synced to all participants"""
        key = f"{session_id}:{operation_id}"
        if key not in self.acknowledged_operations:
            return False

        return len(self.acknowledged_operations[key]) >= participant_count

    async def sync_session(self, session_id: str, participant_count: int) -> List[Dict[str, Any]]:
        """
        Synchronize pending operations and return resolved operations
        """
        if session_id not in self.pending_operations:
            return []

        operations = self.pending_operations[session_id]

        # Group operations by type
        grouped_ops: Dict[str, List[Dict[str, Any]]] = {}
        for op in operations:
            op_type = op.get('type', 'unknown')
            if op_type not in grouped_ops:
                grouped_ops[op_type] = []
            grouped_ops[op_type].append(op)

        # Resolve conflicts
        resolved_operations = []

        for op_type, ops in grouped_ops.items():
            if op_type == 'input':
                resolved = self.conflict_resolver.resolve_input_conflict(ops)
                if resolved:
                    resolved_operations.append(resolved)
            else:
                # No conflict for other types, include all
                resolved_operations.extend(ops)

        # Clear pending operations that have been synced
        synced_ops = [
            op for op in operations
            if self.is_operation_synced(session_id, op.get('id', ''), participant_count)
        ]

        # Remove synced operations
        self.pending_operations[session_id] = [
            op for op in operations
            if op not in synced_ops
        ]

        return resolved_operations


class WebSocketHandler:
    """Main WebSocket handler for managing connections and routing"""

    def __init__(self):
        self.router = MessageRouter()
        self.sync_manager = SessionSync()
        self.conflict_resolver = ConflictResolver()
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup default message handlers"""
        self.router.register_handler(MessageType.JOIN, self._handle_join)
        self.router.register_handler(MessageType.LEAVE, self._handle_leave)
        self.router.register_handler(MessageType.CURSOR_MOVE, self._handle_cursor_move)
        self.router.register_handler(MessageType.INPUT, self._handle_input)
        self.router.register_handler(MessageType.MESSAGE, self._handle_message)
        self.router.register_handler(MessageType.SYNC_REQUEST, self._handle_sync_request)

    async def _handle_join(self, message: WebSocketMessage) -> Dict[str, Any]:
        """Handle user joining a session"""
        logger.info(f"User {message.user_id} joining session")
        return {
            "type": "join_ack",
            "user_id": message.user_id,
            "timestamp": datetime.now().isoformat()
        }

    async def _handle_leave(self, message: WebSocketMessage) -> Dict[str, Any]:
        """Handle user leaving a session"""
        logger.info(f"User {message.user_id} leaving session")
        return {
            "type": "leave_ack",
            "user_id": message.user_id
        }

    async def _handle_cursor_move(self, message: WebSocketMessage) -> Dict[str, Any]:
        """Handle cursor position update"""
        return {
            "type": "cursor_update",
            "user_id": message.user_id,
            "position": message.data.get('position')
        }

    async def _handle_input(self, message: WebSocketMessage) -> Dict[str, Any]:
        """Handle terminal input"""
        session_id = message.data.get('session_id')
        operation = {
            'id': message.data.get('operation_id'),
            'type': 'input',
            'data': message.data.get('input'),
            'timestamp': message.timestamp,
            'user_id': message.user_id
        }

        self.sync_manager.add_operation(session_id, operation)

        return {
            "type": "input_ack",
            "operation_id": operation['id']
        }

    async def _handle_message(self, message: WebSocketMessage) -> Dict[str, Any]:
        """Handle chat message"""
        return {
            "type": "message_broadcast",
            "user_id": message.user_id,
            "message": message.data.get('message'),
            "timestamp": message.timestamp
        }

    async def _handle_sync_request(self, message: WebSocketMessage) -> Dict[str, Any]:
        """Handle synchronization request"""
        session_id = message.data.get('session_id')
        participant_count = message.data.get('participant_count', 1)

        resolved_ops = await self.sync_manager.sync_session(session_id, participant_count)

        return {
            "type": "sync_response",
            "operations": resolved_ops
        }

    async def handle_message(self, raw_message: str) -> Optional[Dict[str, Any]]:
        """Handle incoming WebSocket message"""
        try:
            message = WebSocketMessage.from_json(raw_message)
            return await self.router.route(message)
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return {
                "type": "error",
                "error": str(e)
            }

    def create_message(self, message_type: MessageType, data: Dict[str, Any], user_id: Optional[str] = None) -> str:
        """Create a WebSocket message"""
        message = WebSocketMessage(
            type=message_type,
            data=data,
            user_id=user_id
        )
        return message.to_json()


# Factory function
def create_websocket_handler() -> WebSocketHandler:
    """Create a new WebSocket handler instance"""
    return WebSocketHandler()
