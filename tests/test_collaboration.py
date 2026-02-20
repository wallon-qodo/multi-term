#!/usr/bin/env python3
"""
Tests for Collaboration System

Tests session sharing, real-time sync, and collaboration features.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Import collaboration components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_multi_terminal.collaboration.share_manager import (
    ShareManager,
    ShareConfig,
    ShareInfo,
    AccessType
)


class TestShareManager:
    """Test ShareManager functionality"""

    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return ShareConfig(
            server_url="http://localhost:8765",
            default_access_type=AccessType.READ_ONLY,
            default_expiry_hours=24,
            require_encryption=True,
            auto_sync=False  # Disable for tests
        )

    @pytest.fixture
    def manager(self, config):
        """Create ShareManager instance"""
        manager = ShareManager(config)
        return manager

    @pytest.mark.asyncio
    async def test_initialization(self, config):
        """Test manager initialization"""
        manager = ShareManager(config)
        await manager.initialize()

        assert manager.session is not None
        assert manager.config == config

        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_create_share_success(self, manager):
        """Test successful share creation"""
        # Mock HTTP response
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'share_token': 'test_token_123',
                'share_url': 'http://localhost:8765/viewer?token=test_token_123',
                'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
                'access_type': 'read',
                'encryption_key': 'test_key'
            })
            mock_post.return_value.__aenter__.return_value = mock_response

            await manager.initialize()

            share = await manager.create_share(
                session_id='session_1',
                owner_id='owner_1',
                access_type=AccessType.READ_ONLY,
                expires_in_hours=24
            )

            assert share is not None
            assert share.session_id == 'session_1'
            assert share.share_token == 'test_token_123'
            assert share.access_type == AccessType.READ_ONLY
            assert share.encryption_key == 'test_key'

            # Verify stored in active shares
            assert 'test_token_123' in manager.active_shares

    @pytest.mark.asyncio
    async def test_create_share_failure(self, manager):
        """Test share creation failure"""
        # Mock HTTP error response
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_response.json = AsyncMock(return_value={
                'error': 'Invalid session ID'
            })
            mock_post.return_value.__aenter__.return_value = mock_response

            await manager.initialize()

            with pytest.raises(Exception, match="Failed to create share"):
                await manager.create_share(
                    session_id='invalid',
                    owner_id='owner_1'
                )

    @pytest.mark.asyncio
    async def test_revoke_share(self, manager):
        """Test share revocation"""
        # Add a test share
        share_info = ShareInfo(
            session_id='session_1',
            share_token='test_token',
            share_url='http://test.com',
            access_type=AccessType.READ_ONLY,
            created_at=datetime.now().isoformat()
        )
        manager.active_shares['test_token'] = share_info

        # Mock HTTP response
        with patch('aiohttp.ClientSession.delete') as mock_delete:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={'status': 'revoked'})
            mock_delete.return_value.__aenter__.return_value = mock_response

            await manager.initialize()

            result = await manager.revoke_share('test_token')

            assert result is True
            assert 'test_token' not in manager.active_shares

    @pytest.mark.asyncio
    async def test_get_share_info_local(self, manager):
        """Test getting share info from local cache"""
        # Add a test share
        share_info = ShareInfo(
            session_id='session_1',
            share_token='test_token',
            share_url='http://test.com',
            access_type=AccessType.READ_ONLY,
            created_at=datetime.now().isoformat()
        )
        manager.active_shares['test_token'] = share_info

        result = await manager.get_share_info('test_token')

        assert result is not None
        assert result.share_token == 'test_token'
        assert result.session_id == 'session_1'

    @pytest.mark.asyncio
    async def test_get_share_info_remote(self, manager):
        """Test getting share info from server"""
        # Mock HTTP response
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'session_id': 'session_1',
                'share_token': 'remote_token',
                'access_type': 'read',
                'created_at': datetime.now().isoformat(),
                'views': 5,
                'participants': ['user1', 'user2']
            })
            mock_get.return_value.__aenter__.return_value = mock_response

            await manager.initialize()

            result = await manager.get_share_info('remote_token')

            assert result is not None
            assert result.share_token == 'remote_token'
            assert result.views == 5
            assert result.active_participants == 2

    @pytest.mark.asyncio
    async def test_get_analytics(self, manager):
        """Test getting share analytics"""
        # Mock HTTP response
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'views': 10,
                'participants': ['user1', 'user2', 'user3'],
                'created_at': datetime.now().isoformat(),
                'is_expired': False
            })
            mock_get.return_value.__aenter__.return_value = mock_response

            await manager.initialize()

            analytics = await manager.get_analytics('test_token')

            assert analytics is not None
            assert analytics['views'] == 10
            assert len(analytics['participants']) == 3
            assert analytics['is_expired'] is False

    def test_get_active_shares(self, config):
        """Test getting active shares"""
        # Create fresh manager for this test
        manager = ShareManager(config)
        manager.active_shares.clear()  # Clear any loaded shares

        # Add test shares
        share1 = ShareInfo(
            session_id='session_1',
            share_token='token1',
            share_url='http://test.com/1',
            access_type=AccessType.READ_ONLY,
            created_at=datetime.now().isoformat(),
            is_active=True
        )
        share2 = ShareInfo(
            session_id='session_2',
            share_token='token2',
            share_url='http://test.com/2',
            access_type=AccessType.INTERACTIVE,
            created_at=datetime.now().isoformat(),
            is_active=False
        )
        share3 = ShareInfo(
            session_id='session_3',
            share_token='token3',
            share_url='http://test.com/3',
            access_type=AccessType.READ_ONLY,
            created_at=datetime.now().isoformat(),
            is_active=True
        )

        manager.active_shares['token1'] = share1
        manager.active_shares['token2'] = share2
        manager.active_shares['token3'] = share3

        active = manager.get_active_shares()

        assert len(active) == 2
        assert all(share.is_active for share in active)

    def test_get_shares_for_session(self, config):
        """Test getting shares for specific session"""
        # Create fresh manager for this test
        manager = ShareManager(config)
        manager.active_shares.clear()  # Clear any loaded shares

        # Add test shares
        share1 = ShareInfo(
            session_id='session_1',
            share_token='token1',
            share_url='http://test.com/1',
            access_type=AccessType.READ_ONLY,
            created_at=datetime.now().isoformat(),
            is_active=True
        )
        share2 = ShareInfo(
            session_id='session_1',
            share_token='token2',
            share_url='http://test.com/2',
            access_type=AccessType.INTERACTIVE,
            created_at=datetime.now().isoformat(),
            is_active=True
        )
        share3 = ShareInfo(
            session_id='session_2',
            share_token='token3',
            share_url='http://test.com/3',
            access_type=AccessType.READ_ONLY,
            created_at=datetime.now().isoformat(),
            is_active=True
        )

        manager.active_shares['token1'] = share1
        manager.active_shares['token2'] = share2
        manager.active_shares['token3'] = share3

        session_shares = manager.get_shares_for_session('session_1')

        assert len(session_shares) == 2
        assert all(share.session_id == 'session_1' for share in session_shares)


class TestAccessTypes:
    """Test access type functionality"""

    def test_access_type_enum(self):
        """Test AccessType enum"""
        assert AccessType.READ_ONLY.value == "read"
        assert AccessType.INTERACTIVE.value == "interactive"

    def test_share_info_access_type(self):
        """Test ShareInfo with different access types"""
        read_only = ShareInfo(
            session_id='session_1',
            share_token='token1',
            share_url='http://test.com',
            access_type=AccessType.READ_ONLY,
            created_at=datetime.now().isoformat()
        )

        interactive = ShareInfo(
            session_id='session_2',
            share_token='token2',
            share_url='http://test.com',
            access_type=AccessType.INTERACTIVE,
            created_at=datetime.now().isoformat()
        )

        assert read_only.access_type == AccessType.READ_ONLY
        assert interactive.access_type == AccessType.INTERACTIVE


class TestShareInfoSerialization:
    """Test ShareInfo serialization"""

    def test_to_dict(self):
        """Test converting ShareInfo to dictionary"""
        share = ShareInfo(
            session_id='session_1',
            share_token='token1',
            share_url='http://test.com',
            access_type=AccessType.READ_ONLY,
            created_at='2024-01-01T00:00:00',
            expires_at='2024-01-02T00:00:00',
            views=5,
            active_participants=2
        )

        data = share.to_dict()

        assert data['session_id'] == 'session_1'
        assert data['share_token'] == 'token1'
        assert data['access_type'] == 'read'
        assert data['views'] == 5
        assert data['active_participants'] == 2

    def test_from_dict(self):
        """Test creating ShareInfo from dictionary"""
        data = {
            'session_id': 'session_1',
            'share_token': 'token1',
            'share_url': 'http://test.com',
            'access_type': 'interactive',
            'created_at': '2024-01-01T00:00:00',
            'expires_at': '2024-01-02T00:00:00',
            'views': 10,
            'active_participants': 3,
            'is_active': True,
            'encryption_key': 'key123'
        }

        share = ShareInfo.from_dict(data)

        assert share.session_id == 'session_1'
        assert share.access_type == AccessType.INTERACTIVE
        assert share.views == 10
        assert share.encryption_key == 'key123'


def run_tests():
    """Run all tests"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_tests()
