#!/usr/bin/env python3
"""
Tests for Collaboration Server

Tests WebSocket server, session sharing, and real-time features.
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# Import server components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "server"))

try:
    from collaboration_server import (
        CollaborationServer,
        SessionShare,
        Participant
    )
    from websocket_handler import (
        WebSocketHandler,
        WebSocketMessage,
        MessageType,
        ConflictResolver,
        SessionSync
    )
    SERVER_AVAILABLE = True
except ImportError:
    SERVER_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="Server dependencies not available")


@pytest.mark.skipif(not SERVER_AVAILABLE, reason="Server not available")
class TestSessionShare:
    """Test SessionShare functionality"""

    def test_session_share_creation(self):
        """Test creating a session share"""
        share = SessionShare(
            session_id="session_1",
            share_token="token_123",
            owner_id="owner_1",
            access_type="read"
        )

        assert share.session_id == "session_1"
        assert share.share_token == "token_123"
        assert share.owner_id == "owner_1"
        assert share.access_type == "read"
        assert share.is_public is False
        assert share.views == 0

    def test_session_share_expiry(self):
        """Test share expiry checking"""
        from datetime import timedelta

        # Not expired
        share1 = SessionShare(
            session_id="session_1",
            share_token="token_1",
            owner_id="owner_1",
            expires_at=(datetime.now() + timedelta(hours=1)).isoformat()
        )
        assert share1.is_expired() is False

        # Expired
        share2 = SessionShare(
            session_id="session_2",
            share_token="token_2",
            owner_id="owner_1",
            expires_at=(datetime.now() - timedelta(hours=1)).isoformat()
        )
        assert share2.is_expired() is True

        # No expiry
        share3 = SessionShare(
            session_id="session_3",
            share_token="token_3",
            owner_id="owner_1"
        )
        assert share3.is_expired() is False


@pytest.mark.skipif(not SERVER_AVAILABLE, reason="Server not available")
class TestWebSocketHandler:
    """Test WebSocketHandler functionality"""

    @pytest.fixture
    def handler(self):
        """Create WebSocketHandler instance"""
        return WebSocketHandler()

    @pytest.mark.asyncio
    async def test_handle_join_message(self, handler):
        """Test handling join message"""
        message = WebSocketMessage(
            type=MessageType.JOIN,
            data={'session_id': 'session_1'},
            user_id='user_1'
        )

        result = await handler._handle_join(message)

        assert result is not None
        assert result['type'] == 'join_ack'
        assert result['user_id'] == 'user_1'

    @pytest.mark.asyncio
    async def test_handle_cursor_move(self, handler):
        """Test handling cursor movement"""
        message = WebSocketMessage(
            type=MessageType.CURSOR_MOVE,
            data={'position': {'line': 10, 'column': 5}},
            user_id='user_1'
        )

        result = await handler._handle_cursor_move(message)

        assert result is not None
        assert result['type'] == 'cursor_update'
        assert result['user_id'] == 'user_1'
        assert result['position'] == {'line': 10, 'column': 5}

    @pytest.mark.asyncio
    async def test_handle_input(self, handler):
        """Test handling terminal input"""
        message = WebSocketMessage(
            type=MessageType.INPUT,
            data={
                'session_id': 'session_1',
                'operation_id': 'op_1',
                'input': 'ls -la'
            },
            user_id='user_1'
        )

        result = await handler._handle_input(message)

        assert result is not None
        assert result['type'] == 'input_ack'
        assert result['operation_id'] == 'op_1'

    @pytest.mark.asyncio
    async def test_handle_message(self, handler):
        """Test handling chat message"""
        message = WebSocketMessage(
            type=MessageType.MESSAGE,
            data={'message': 'Hello, world!'},
            user_id='user_1'
        )

        result = await handler._handle_message(message)

        assert result is not None
        assert result['type'] == 'message_broadcast'
        assert result['message'] == 'Hello, world!'

    def test_create_message(self, handler):
        """Test creating WebSocket message"""
        message_json = handler.create_message(
            MessageType.JOIN,
            {'session_id': 'session_1'},
            user_id='user_1'
        )

        message_data = json.loads(message_json)

        assert message_data['type'] == 'join'
        assert message_data['data']['session_id'] == 'session_1'
        assert message_data['user_id'] == 'user_1'


@pytest.mark.skipif(not SERVER_AVAILABLE, reason="Server not available")
class TestConflictResolver:
    """Test ConflictResolver functionality"""

    @pytest.fixture
    def resolver(self):
        """Create ConflictResolver instance"""
        return ConflictResolver()

    def test_resolve_input_conflict(self, resolver):
        """Test resolving input conflicts"""
        operations = [
            {
                'id': 'op_1',
                'data': 'command1',
                'timestamp': '2024-01-01T00:00:00'
            },
            {
                'id': 'op_2',
                'data': 'command2',
                'timestamp': '2024-01-01T00:00:02'
            },
            {
                'id': 'op_3',
                'data': 'command3',
                'timestamp': '2024-01-01T00:00:01'
            }
        ]

        result = resolver.resolve_input_conflict(operations)

        # Should return the latest operation (op_2)
        assert result['id'] == 'op_2'
        assert result['data'] == 'command2'

    def test_resolve_cursor_conflict(self, resolver):
        """Test resolving cursor conflicts"""
        cursors = {
            'user_1': {
                'position': {'line': 1, 'column': 0},
                'timestamp': '2024-01-01T00:00:00'
            },
            'user_2': {
                'position': {'line': 5, 'column': 10},
                'timestamp': '2024-01-01T00:00:02'
            },
            'user_3': {
                'position': {'line': 3, 'column': 5},
                'timestamp': '2024-01-01T00:00:01'
            }
        }

        result = resolver.resolve_cursor_conflict(cursors)

        # Should mark user_2 as active (most recent)
        assert result['user_2']['active'] is True
        assert result['user_1']['active'] is False
        assert result['user_3']['active'] is False

    def test_merge_session_state(self, resolver):
        """Test merging session states"""
        base = {
            'terminal_output': 'line1\nline2',
            'cursor_position': {'line': 2, 'column': 0}
        }

        updates = [
            {
                'terminal_output': 'line1\nline2\nline3',
                'mode': 'insert'
            },
            {
                'cursor_position': {'line': 3, 'column': 5},
                'history': ['cmd1', 'cmd2']
            }
        ]

        result = resolver.merge_session_state(base, updates)

        assert result['terminal_output'] == 'line1\nline2\nline3'
        assert result['cursor_position'] == {'line': 3, 'column': 5}
        assert result['mode'] == 'insert'
        assert result['history'] == ['cmd1', 'cmd2']


@pytest.mark.skipif(not SERVER_AVAILABLE, reason="Server not available")
class TestSessionSync:
    """Test SessionSync functionality"""

    @pytest.fixture
    def sync_manager(self):
        """Create SessionSync instance"""
        return SessionSync()

    def test_add_operation(self, sync_manager):
        """Test adding operations"""
        operation = {
            'id': 'op_1',
            'type': 'input',
            'data': 'command'
        }

        sync_manager.add_operation('session_1', operation)

        assert 'session_1' in sync_manager.pending_operations
        assert len(sync_manager.pending_operations['session_1']) == 1

    def test_acknowledge_operation(self, sync_manager):
        """Test acknowledging operations"""
        sync_manager.acknowledge_operation('session_1', 'op_1', 'user_1')
        sync_manager.acknowledge_operation('session_1', 'op_1', 'user_2')

        key = 'session_1:op_1'
        assert key in sync_manager.acknowledged_operations
        assert len(sync_manager.acknowledged_operations[key]) == 2

    def test_is_operation_synced(self, sync_manager):
        """Test checking if operation is synced"""
        sync_manager.acknowledge_operation('session_1', 'op_1', 'user_1')
        sync_manager.acknowledge_operation('session_1', 'op_1', 'user_2')

        # Synced with 2 participants
        assert sync_manager.is_operation_synced('session_1', 'op_1', 2) is True

        # Not synced with 3 participants
        assert sync_manager.is_operation_synced('session_1', 'op_1', 3) is False

    @pytest.mark.asyncio
    async def test_sync_session(self, sync_manager):
        """Test synchronizing session"""
        # Add operations
        operations = [
            {'id': 'op_1', 'type': 'input', 'data': 'cmd1'},
            {'id': 'op_2', 'type': 'input', 'data': 'cmd2'},
            {'id': 'op_3', 'type': 'cursor', 'data': {'line': 1}}
        ]

        for op in operations:
            sync_manager.add_operation('session_1', op)

        # Mark some as synced
        sync_manager.acknowledge_operation('session_1', 'op_1', 'user_1')
        sync_manager.acknowledge_operation('session_1', 'op_1', 'user_2')

        resolved = await sync_manager.sync_session('session_1', 2)

        assert len(resolved) > 0


@pytest.mark.skipif(not SERVER_AVAILABLE, reason="Server not available")
class TestCollaborationServerIntegration:
    """Integration tests for collaboration server"""

    def test_server_initialization(self):
        """Test server initialization"""
        server = CollaborationServer(host="localhost", port=8766)
        assert server.host == "localhost"
        assert server.port == 8766
        assert server.app is not None
        assert len(server.shares) == 0
        assert len(server.participants) == 0


def run_tests():
    """Run all tests"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_tests()
