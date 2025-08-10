#!/usr/bin/env python3
"""
Test if the user exists in the database with the token's subject ID
"""
import sys
import asyncio
import jwt
from sqlalchemy import select
from afsp_app.app.database import async_session_maker, User

async def check_user_in_db():
    """Check if the user from the token actually exists in the database"""
    # Token from our test
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjYTg2ODQ2MC0zOGU3LTQ4NTUtYTgyNS01MWJjZjBmMTdjNjIiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc1NDEwNTMxMH0.Duwsa4pwwwOZ1eLOPAgm2q1AAqC1A8YKmMb1kxT3Tqo"
    
    # Decode token to get user ID
    try:
        payload = jwt.decode(token, options={'verify_signature': False})
        user_id = payload['sub']
        print(f"Token user ID: {user_id}")
        print(f"Token user ID type: {type(user_id)}")
    except Exception as e:
        print(f"Failed to decode token: {e}")
        return False
    
    # Check if user exists in database
    async with async_session_maker() as session:
        # Try to find user by ID
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"✅ User found in database:")
            print(f"  ID: {user.id} (type: {type(user.id)})")
            print(f"  Email: {user.email}")
            print(f"  Active: {user.is_active}")
            print(f"  Verified: {user.is_verified}")
            return True
        else:
            print(f"❌ User NOT found in database")
            
            # List all users to see what's in the database
            all_users_result = await session.execute(select(User))
            all_users = all_users_result.scalars().all()
            print(f"All users in database ({len(all_users)}):")
            for u in all_users:
                print(f"  - ID: {u.id} (type: {type(u.id)}), Email: {u.email}")
            return False

if __name__ == "__main__":
    result = asyncio.run(check_user_in_db())
    sys.exit(0 if result else 1)
