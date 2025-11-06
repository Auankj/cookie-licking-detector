#!/usr/bin/env python3
"""
Create a test user for the Cookie-Licking Detector system
"""
import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.database import get_async_session
from app.db.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select


async def create_test_user():
    """Create a test user for development"""
    
    async for db in get_async_session():
        try:
            # Check if user already exists
            stmt = select(User).where(User.email == 'test@example.com')
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("✅ Test user already exists!")
                print(f"   Email: test@example.com")
                print(f"   Password: testpass123")
                print(f"   ID: {existing_user.id}")
                return
            
            # Create new test user
            hashed_password = get_password_hash('testpass123')
            
            new_user = User(
                email='test@example.com',
                password_hash=hashed_password,
                full_name='Test User',
                github_username='testuser',
                is_active=True,
                is_verified=True,
                roles=['user']
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            print("✅ Test user created successfully!")
            print()
            print("=" * 50)
            print("LOGIN CREDENTIALS")
            print("=" * 50)
            print(f"Email (username): test@example.com")
            print(f"Password: testpass123")
            print(f"User ID: {new_user.id}")
            print("=" * 50)
            print()
            print("You can now login to the web app at:")
            print("http://localhost:8000/")
            print()
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise
        finally:
            break


if __name__ == "__main__":
    print("Creating test user...")
    asyncio.run(create_test_user())
