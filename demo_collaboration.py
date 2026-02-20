#!/usr/bin/env python3
"""
Demo script for Collaboration System

Shows how to use the collaboration features.
"""

import asyncio
from claude_multi_terminal.collaboration import ShareManager, ShareConfig, AccessType


async def main():
    """Demo the collaboration system"""
    print("=" * 60)
    print("Claude Multi-Terminal - Collaboration System Demo")
    print("=" * 60)
    print()

    # Initialize share manager
    config = ShareConfig(
        server_url="http://localhost:8765",
        default_access_type=AccessType.READ_ONLY,
        default_expiry_hours=24,
        require_encryption=True
    )

    manager = ShareManager(config)
    await manager.initialize()

    print("✅ Share manager initialized")
    print()

    try:
        # Create a read-only share
        print("Creating read-only share...")
        read_share = await manager.create_share(
            session_id="demo_session_1",
            owner_id="demo_user",
            access_type=AccessType.READ_ONLY,
            expires_in_hours=24
        )

        print(f"✅ Read-only share created:")
        print(f"   Token: {read_share.share_token[:32]}...")
        print(f"   URL: {read_share.share_url}")
        print(f"   Expires: {read_share.expires_at}")
        print(f"   Encrypted: {'Yes' if read_share.encryption_key else 'No'}")
        print()

        # Create an interactive share
        print("Creating interactive share...")
        interactive_share = await manager.create_share(
            session_id="demo_session_2",
            owner_id="demo_user",
            access_type=AccessType.INTERACTIVE,
            expires_in_hours=12
        )

        print(f"✅ Interactive share created:")
        print(f"   Token: {interactive_share.share_token[:32]}...")
        print(f"   URL: {interactive_share.share_url}")
        print(f"   Expires: {interactive_share.expires_at}")
        print()

        # Get share info
        print("Retrieving share info...")
        info = await manager.get_share_info(read_share.share_token)

        if info:
            print(f"✅ Share info retrieved:")
            print(f"   Session ID: {info.session_id}")
            print(f"   Access Type: {info.access_type.value}")
            print(f"   Views: {info.views}")
            print(f"   Participants: {info.active_participants}")
        print()

        # List active shares
        print("Active shares:")
        active = manager.get_active_shares()
        for i, share in enumerate(active, 1):
            print(f"  {i}. {share.session_id} - {share.access_type.value}")
        print()

        # Get analytics
        print("Getting analytics...")
        analytics = await manager.get_analytics(read_share.share_token)

        if analytics:
            print(f"✅ Analytics retrieved:")
            print(f"   Views: {analytics.get('views', 0)}")
            print(f"   Participants: {len(analytics.get('participants', []))}")
            print(f"   Expired: {analytics.get('is_expired', False)}")
        print()

        # Revoke a share
        print(f"Revoking share {read_share.share_token[:16]}...")
        revoked = await manager.revoke_share(read_share.share_token)

        if revoked:
            print("✅ Share revoked successfully")
        else:
            print("❌ Failed to revoke share")
        print()

        # Show remaining shares
        print("Remaining active shares:")
        remaining = manager.get_active_shares()
        for i, share in enumerate(remaining, 1):
            print(f"  {i}. {share.session_id} - {share.access_type.value}")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Note: Make sure the collaboration server is running:")
        print("  python server/collaboration_server.py")
        print()

    finally:
        await manager.shutdown()
        print("✅ Share manager shutdown")


if __name__ == "__main__":
    print("\n🚀 Starting collaboration demo...\n")
    asyncio.run(main())
    print("\n✅ Demo complete!\n")
