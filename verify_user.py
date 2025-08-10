#!/usr/bin/env python3
"""
Verify the user and test authentication again
"""
import sys
import asyncio
from sqlalchemy import select, update
from afsp_app.app.database import async_session_maker, User

async def verify_user():
    """Set the user as verified"""
    user_id = "ca868460-38e7-4855-a825-51bcf0f17c62"
    
    async with async_session_maker() as session:
        # Update user to be verified
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_verified=True)
        )
        await session.commit()
        
        # Verify the update
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"✅ User updated:")
            print(f"  ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Active: {user.is_active}")
            print(f"  Verified: {user.is_verified}")
            return user.is_verified
        else:
            print("❌ User not found")
            return False

if __name__ == "__main__":
    result = asyncio.run(verify_user())
    sys.exit(0 if result else 1)
