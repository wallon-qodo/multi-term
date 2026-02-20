#!/usr/bin/env python3
"""
Collaboration Server for Claude Multi-Terminal

Real-time session sharing and collaboration via WebSocket server.
Supports multiple users, access control, and encryption.
"""

import asyncio
import json
import secrets
import logging
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from cryptography.fernet import Fernet
import base64

from aiohttp import web
import aiohttp_cors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SessionShare:
    """Represents a shared session"""
    session_id: str
    share_token: str
    owner_id: str
    access_type: str = "read"  # "read", "interactive"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    encryption_key: Optional[str] = None
    views: int = 0
    participants: Set[str] = field(default_factory=set)
    is_public: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['participants'] = list(data['participants'])
        return data

    def is_expired(self) -> bool:
        """Check if share link has expired"""
        if not self.expires_at:
            return False
        return datetime.fromisoformat(self.expires_at) < datetime.now()


@dataclass
class Participant:
    """Represents a participant in a session"""
    user_id: str
    websocket: web.WebSocketResponse
    session_id: str
    access_type: str
    cursor_position: Optional[Dict[str, int]] = None
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())


class CollaborationServer:
    """WebSocket server for real-time collaboration"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.shares: Dict[str, SessionShare] = {}
        self.participants: Dict[str, Participant] = {}
        self.session_data: Dict[str, Dict[str, Any]] = {}
        self.encryption_keys: Dict[str, bytes] = {}

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup HTTP and WebSocket routes"""
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_post('/share/create', self.create_share)
        self.app.router.add_get('/share/{token}', self.get_share_info)
        self.app.router.add_delete('/share/{token}', self.revoke_share)
        self.app.router.add_get('/share/{token}/analytics', self.get_analytics)
        self.app.router.add_get('/health', self.health_check)

        # Setup CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })

        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "active_sessions": len(self.session_data),
            "active_participants": len(self.participants),
            "shares": len(self.shares)
        })

    async def create_share(self, request: web.Request) -> web.Response:
        """Create a new session share"""
        try:
            data = await request.json()
            session_id = data.get('session_id')
            owner_id = data.get('owner_id')
            access_type = data.get('access_type', 'read')
            is_public = data.get('is_public', False)
            expires_in_hours = data.get('expires_in_hours')
            require_encryption = data.get('require_encryption', True)

            if not session_id or not owner_id:
                return web.json_response(
                    {"error": "session_id and owner_id required"},
                    status=400
                )

            # Generate share token
            share_token = secrets.token_urlsafe(32)

            # Calculate expiration
            expires_at = None
            if expires_in_hours:
                expires_at = (datetime.now() + timedelta(hours=expires_in_hours)).isoformat()

            # Generate encryption key if required
            encryption_key = None
            if require_encryption:
                key = Fernet.generate_key()
                self.encryption_keys[share_token] = key
                encryption_key = base64.b64encode(key).decode()

            # Create share
            share = SessionShare(
                session_id=session_id,
                share_token=share_token,
                owner_id=owner_id,
                access_type=access_type,
                expires_at=expires_at,
                encryption_key=encryption_key,
                is_public=is_public
            )

            self.shares[share_token] = share

            logger.info(f"Created share: {share_token} for session {session_id}")

            return web.json_response({
                "share_token": share_token,
                "share_url": f"http://{self.host}:{self.port}/viewer?token={share_token}",
                "expires_at": expires_at,
                "access_type": access_type,
                "encryption_key": encryption_key
            })

        except Exception as e:
            logger.error(f"Error creating share: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def get_share_info(self, request: web.Request) -> web.Response:
        """Get information about a share"""
        token = request.match_info['token']

        share = self.shares.get(token)
        if not share:
            return web.json_response({"error": "Share not found"}, status=404)

        if share.is_expired():
            return web.json_response({"error": "Share has expired"}, status=410)

        return web.json_response(share.to_dict())

    async def revoke_share(self, request: web.Request) -> web.Response:
        """Revoke a share link"""
        token = request.match_info['token']

        if token not in self.shares:
            return web.json_response({"error": "Share not found"}, status=404)

        # Disconnect all participants
        share = self.shares[token]
        participants_to_disconnect = [
            p for p in self.participants.values()
            if p.session_id == share.session_id
        ]

        for participant in participants_to_disconnect:
            await participant.websocket.close(
                code=1000,
                message=b"Share has been revoked"
            )

        del self.shares[token]
        logger.info(f"Revoked share: {token}")

        return web.json_response({"status": "revoked"})

    async def get_analytics(self, request: web.Request) -> web.Response:
        """Get analytics for a share"""
        token = request.match_info['token']

        share = self.shares.get(token)
        if not share:
            return web.json_response({"error": "Share not found"}, status=404)

        return web.json_response({
            "views": share.views,
            "participants": list(share.participants),
            "created_at": share.created_at,
            "expires_at": share.expires_at,
            "is_expired": share.is_expired()
        })

    async def websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        user_id = None
        session_id = None

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    msg_type = data.get('type')

                    if msg_type == 'join':
                        # Join a session
                        result = await self._handle_join(ws, data)
                        if result.get('success'):
                            user_id = result['user_id']
                            session_id = result['session_id']
                        await ws.send_json(result)

                    elif msg_type == 'cursor_move':
                        # Update cursor position
                        await self._handle_cursor_move(user_id, data)

                    elif msg_type == 'message':
                        # Chat message
                        await self._handle_message(user_id, session_id, data)

                    elif msg_type == 'input':
                        # Terminal input (interactive mode only)
                        await self._handle_input(user_id, session_id, data)

                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")

        finally:
            # Cleanup on disconnect
            if user_id and user_id in self.participants:
                await self._handle_disconnect(user_id, session_id)

        return ws

    async def _handle_join(self, ws: web.WebSocketResponse, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a user joining a session"""
        share_token = data.get('share_token')

        # Validate share token
        share = self.shares.get(share_token)
        if not share:
            return {"success": False, "error": "Invalid share token"}

        if share.is_expired():
            return {"success": False, "error": "Share has expired"}

        # Generate user ID
        user_id = secrets.token_urlsafe(16)

        # Create participant
        participant = Participant(
            user_id=user_id,
            websocket=ws,
            session_id=share.session_id,
            access_type=share.access_type
        )

        self.participants[user_id] = participant
        share.participants.add(user_id)
        share.views += 1

        logger.info(f"User {user_id} joined session {share.session_id}")

        # Broadcast join event
        await self._broadcast(share.session_id, {
            "type": "user_joined",
            "user_id": user_id,
            "participant_count": len(share.participants)
        }, exclude_user=user_id)

        # Send session data to new participant
        session_data = self.session_data.get(share.session_id, {})

        return {
            "success": True,
            "user_id": user_id,
            "session_id": share.session_id,
            "access_type": share.access_type,
            "session_data": session_data,
            "participants": list(share.participants)
        }

    async def _handle_cursor_move(self, user_id: str, data: Dict[str, Any]):
        """Handle cursor position update"""
        if user_id not in self.participants:
            return

        participant = self.participants[user_id]
        participant.cursor_position = data.get('position')
        participant.last_seen = datetime.now().isoformat()

        # Broadcast cursor position
        await self._broadcast(participant.session_id, {
            "type": "cursor_move",
            "user_id": user_id,
            "position": participant.cursor_position
        }, exclude_user=user_id)

    async def _handle_message(self, user_id: str, session_id: str, data: Dict[str, Any]):
        """Handle chat message"""
        message = data.get('message')

        await self._broadcast(session_id, {
            "type": "message",
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    async def _handle_input(self, user_id: str, session_id: str, data: Dict[str, Any]):
        """Handle terminal input (interactive mode only)"""
        if user_id not in self.participants:
            return

        participant = self.participants[user_id]
        if participant.access_type != 'interactive':
            return

        # Broadcast input to all participants
        await self._broadcast(session_id, {
            "type": "input",
            "user_id": user_id,
            "data": data.get('data')
        })

    async def _handle_disconnect(self, user_id: str, session_id: str):
        """Handle user disconnect"""
        if user_id in self.participants:
            del self.participants[user_id]

        # Update share participants
        for share in self.shares.values():
            if session_id == share.session_id:
                share.participants.discard(user_id)

        logger.info(f"User {user_id} disconnected from session {session_id}")

        # Broadcast disconnect event
        await self._broadcast(session_id, {
            "type": "user_left",
            "user_id": user_id
        })

    async def _broadcast(self, session_id: str, message: Dict[str, Any], exclude_user: Optional[str] = None):
        """Broadcast message to all participants in a session"""
        participants = [
            p for p in self.participants.values()
            if p.session_id == session_id and p.user_id != exclude_user
        ]

        for participant in participants:
            try:
                await participant.websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {participant.user_id}: {e}")

    async def update_session_data(self, session_id: str, data: Dict[str, Any]):
        """Update session data and broadcast to participants"""
        self.session_data[session_id] = data

        await self._broadcast(session_id, {
            "type": "session_update",
            "data": data
        })

    async def start(self):
        """Start the server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        logger.info(f"Collaboration server started on {self.host}:{self.port}")
        logger.info(f"WebSocket endpoint: ws://{self.host}:{self.port}/ws")
        logger.info(f"HTTP API: http://{self.host}:{self.port}")

        # Keep server running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Shutting down server...")


async def main():
    """Main entry point"""
    server = CollaborationServer(host="0.0.0.0", port=8765)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
