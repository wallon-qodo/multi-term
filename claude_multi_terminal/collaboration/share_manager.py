"""
Share Manager for Claude Multi-Terminal

Manages session sharing, access control, and collaboration server integration.
"""

import json
import asyncio
import logging
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
import aiohttp
from enum import Enum

logger = logging.getLogger(__name__)


class AccessType(Enum):
    """Session access types"""
    READ_ONLY = "read"
    INTERACTIVE = "interactive"


@dataclass
class ShareConfig:
    """Configuration for session sharing"""
    server_url: str = "http://localhost:8765"
    default_access_type: AccessType = AccessType.READ_ONLY
    default_expiry_hours: int = 24
    require_encryption: bool = True
    auto_sync: bool = True
    sync_interval: float = 1.0  # seconds


@dataclass
class ShareInfo:
    """Information about a shared session"""
    session_id: str
    share_token: str
    share_url: str
    access_type: AccessType
    created_at: str
    expires_at: Optional[str] = None
    encryption_key: Optional[str] = None
    views: int = 0
    active_participants: int = 0
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['access_type'] = self.access_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShareInfo':
        """Create from dictionary"""
        data['access_type'] = AccessType(data['access_type'])
        return cls(**data)


class ShareManager:
    """
    Manages session sharing and collaboration

    Features:
    - Create shareable session links
    - Access control (read-only / interactive)
    - Expiring links
    - Analytics tracking
    - Real-time sync with collaboration server
    """

    def __init__(self, config: Optional[ShareConfig] = None):
        self.config = config or ShareConfig()
        self.active_shares: Dict[str, ShareInfo] = {}
        self.session = None
        self._sync_task = None
        self._storage_path = Path.home() / ".claude-multi-terminal" / "shares.json"
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing shares
        self._load_shares()

    async def initialize(self):
        """Initialize the share manager"""
        self.session = aiohttp.ClientSession()

        if self.config.auto_sync:
            self._sync_task = asyncio.create_task(self._sync_loop())

        logger.info("Share manager initialized")

    async def shutdown(self):
        """Shutdown the share manager"""
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass

        if self.session:
            await self.session.close()

        logger.info("Share manager shutdown")

    async def create_share(
        self,
        session_id: str,
        owner_id: str,
        access_type: Optional[AccessType] = None,
        expires_in_hours: Optional[int] = None,
        is_public: bool = False
    ) -> ShareInfo:
        """
        Create a new session share

        Args:
            session_id: ID of session to share
            owner_id: ID of session owner
            access_type: Access level (read-only or interactive)
            expires_in_hours: Hours until link expires (None = no expiry)
            is_public: Whether share is publicly discoverable

        Returns:
            ShareInfo object with share details
        """
        access_type = access_type or self.config.default_access_type
        expires_in_hours = expires_in_hours or self.config.default_expiry_hours

        try:
            # Call collaboration server
            async with self.session.post(
                f"{self.config.server_url}/share/create",
                json={
                    "session_id": session_id,
                    "owner_id": owner_id,
                    "access_type": access_type.value,
                    "expires_in_hours": expires_in_hours,
                    "is_public": is_public,
                    "require_encryption": self.config.require_encryption
                }
            ) as resp:
                if resp.status != 200:
                    error_data = await resp.json()
                    raise Exception(f"Failed to create share: {error_data.get('error')}")

                data = await resp.json()

                # Create ShareInfo
                share_info = ShareInfo(
                    session_id=session_id,
                    share_token=data['share_token'],
                    share_url=data['share_url'],
                    access_type=access_type,
                    created_at=datetime.now().isoformat(),
                    expires_at=data.get('expires_at'),
                    encryption_key=data.get('encryption_key')
                )

                # Store locally
                self.active_shares[share_info.share_token] = share_info
                self._save_shares()

                logger.info(f"Created share {share_info.share_token} for session {session_id}")

                return share_info

        except Exception as e:
            logger.error(f"Error creating share: {e}")
            raise

    async def revoke_share(self, share_token: str) -> bool:
        """
        Revoke a share link

        Args:
            share_token: Token of share to revoke

        Returns:
            True if revoked successfully
        """
        try:
            # Call collaboration server
            async with self.session.delete(
                f"{self.config.server_url}/share/{share_token}"
            ) as resp:
                if resp.status == 404:
                    logger.warning(f"Share {share_token} not found on server")
                elif resp.status != 200:
                    error_data = await resp.json()
                    raise Exception(f"Failed to revoke share: {error_data.get('error')}")

                # Remove locally
                if share_token in self.active_shares:
                    self.active_shares[share_token].is_active = False
                    del self.active_shares[share_token]
                    self._save_shares()

                logger.info(f"Revoked share {share_token}")
                return True

        except Exception as e:
            logger.error(f"Error revoking share: {e}")
            return False

    async def get_share_info(self, share_token: str) -> Optional[ShareInfo]:
        """
        Get information about a share

        Args:
            share_token: Token of share

        Returns:
            ShareInfo if found, None otherwise
        """
        # Check local cache first
        if share_token in self.active_shares:
            return self.active_shares[share_token]

        # Query server
        try:
            async with self.session.get(
                f"{self.config.server_url}/share/{share_token}"
            ) as resp:
                if resp.status != 200:
                    return None

                data = await resp.json()
                return ShareInfo(
                    session_id=data['session_id'],
                    share_token=data['share_token'],
                    share_url=f"{self.config.server_url}/viewer?token={share_token}",
                    access_type=AccessType(data['access_type']),
                    created_at=data['created_at'],
                    expires_at=data.get('expires_at'),
                    views=data.get('views', 0),
                    active_participants=len(data.get('participants', []))
                )

        except Exception as e:
            logger.error(f"Error getting share info: {e}")
            return None

    async def get_analytics(self, share_token: str) -> Optional[Dict[str, Any]]:
        """
        Get analytics for a share

        Args:
            share_token: Token of share

        Returns:
            Analytics data or None
        """
        try:
            async with self.session.get(
                f"{self.config.server_url}/share/{share_token}/analytics"
            ) as resp:
                if resp.status != 200:
                    return None

                return await resp.json()

        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return None

    def get_active_shares(self) -> List[ShareInfo]:
        """Get list of active shares"""
        return [
            share for share in self.active_shares.values()
            if share.is_active
        ]

    def get_shares_for_session(self, session_id: str) -> List[ShareInfo]:
        """Get all shares for a specific session"""
        return [
            share for share in self.active_shares.values()
            if share.session_id == session_id and share.is_active
        ]

    async def update_session_data(self, session_id: str, data: Dict[str, Any]):
        """
        Push session data update to collaboration server

        Args:
            session_id: Session ID
            data: Session data to sync
        """
        # This would integrate with the collaboration server
        # to push updates in real-time
        pass

    async def _sync_loop(self):
        """Background task to sync share analytics"""
        while True:
            try:
                await asyncio.sleep(self.config.sync_interval)

                # Update analytics for active shares
                for share_token, share_info in list(self.active_shares.items()):
                    if not share_info.is_active:
                        continue

                    # Get updated analytics
                    analytics = await self.get_analytics(share_token)
                    if analytics:
                        share_info.views = analytics.get('views', 0)
                        share_info.active_participants = len(analytics.get('participants', []))

                        # Check if expired
                        if analytics.get('is_expired'):
                            share_info.is_active = False

                self._save_shares()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")

    def _save_shares(self):
        """Save shares to disk"""
        try:
            data = {
                token: share.to_dict()
                for token, share in self.active_shares.items()
            }

            with open(self._storage_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving shares: {e}")

    def _load_shares(self):
        """Load shares from disk"""
        try:
            if not self._storage_path.exists():
                return

            with open(self._storage_path, 'r') as f:
                data = json.load(f)

            self.active_shares = {
                token: ShareInfo.from_dict(share_data)
                for token, share_data in data.items()
            }

            logger.info(f"Loaded {len(self.active_shares)} shares from disk")

        except Exception as e:
            logger.error(f"Error loading shares: {e}")


# Factory function
def create_share_manager(config: Optional[ShareConfig] = None) -> ShareManager:
    """Create a new share manager instance"""
    return ShareManager(config)
