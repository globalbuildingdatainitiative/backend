"""
Migration script to fix user IDs in the custom usermetadata table.

This script:
1. Finds users in the custom usermetadata table with app_user_id (wrong ID)
2. Looks up the correct recipe_user_id from SuperTokens
3. Migrates the data to use the correct recipe_user_id
4. Removes email and time_joined from metadata (these come from SuperTokens)

Run this script ONCE to fix all old users.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from supertokens_python.asyncio import get_user as get_st_user
from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata

from core.connection import get_postgres_engine
from models.user import UserMetadata


async def migrate_user_ids():
    """Migrate user IDs from app_user_id to recipe_user_id"""
    
    print("Starting user ID migration...")
    
    engine = get_postgres_engine()
    async with AsyncSession(engine) as session:
        # Get all users from custom usermetadata table
        result = await session.exec(select(UserMetadata))
        users = result.all()
        
        print(f"Found {len(users)} users in custom usermetadata table")
        
        migrated = 0
        skipped = 0
        errors = []
        
        for user in users:
            user_id = user.id
            
            # Try to get SuperTokens user
            st_user = await get_st_user(user_id)
            
            if not st_user:
                # User not found by this ID - might be app_user_id
                # Try to get from SuperTokens user_metadata to find the real email
                try:
                    st_metadata = await get_user_metadata(user_id)
                    email = st_metadata.metadata.get("email") or user.meta_data.get("email")
                    
                    if not email:
                        print(f"  ❌ User {user_id}: No email found in metadata")
                        errors.append(user_id)
                        continue
                    
                    print(f"  ⚠️  User {user_id} (app_user_id) - email: {email}")
                    print(f"      This user has the wrong ID. You need to manually find the recipe_user_id.")
                    print(f"      Keeping email and time_joined in metadata for now...")
                    
                    # Keep email and time_joined in metadata for these old users
                    # They'll still work with the fallback logic
                    skipped += 1
                    
                except Exception as e:
                    print(f"  ❌ User {user_id}: Error - {e}")
                    errors.append(user_id)
                    
            else:
                # User found! Check if it's using the correct recipe_user_id
                recipe_user_id = st_user.login_methods[0].recipe_user_id.get_as_string()
                
                if user_id != recipe_user_id:
                    print(f"  🔄 User {user_id} needs migration to {recipe_user_id}")
                    
                    # Check if a record with recipe_user_id already exists
                    existing = await session.get(UserMetadata, recipe_user_id)
                    if existing:
                        print(f"      ⚠️  Record with recipe_user_id {recipe_user_id} already exists. Skipping.")
                        skipped += 1
                        continue
                    
                    # Create new record with correct ID
                    new_metadata = user.meta_data.copy()
                    # Remove email and time_joined - these come from SuperTokens
                    new_metadata.pop("email", None)
                    new_metadata.pop("time_joined", None)
                    
                    new_user = UserMetadata(id=recipe_user_id, meta_data=new_metadata)
                    session.add(new_user)
                    
                    # Delete old record
                    await session.delete(user)
                    
                    print(f"      ✅ Migrated to {recipe_user_id}")
                    migrated += 1
                    
                else:
                    # User already has correct ID - just clean up metadata
                    updated = False
                    if "email" in user.meta_data:
                        user.meta_data.pop("email")
                        updated = True
                    if "time_joined" in user.meta_data:
                        user.meta_data.pop("time_joined")
                        updated = True
                    
                    if updated:
                        session.add(user)
                        print(f"  🧹 User {user_id}: Cleaned up email/time_joined from metadata")
                        migrated += 1
                    else:
                        skipped += 1
        
        # Commit all changes
        await session.commit()
        
    print("\n" + "="*60)
    print(f"Migration complete!")
    print(f"  ✅ Migrated: {migrated}")
    print(f"  ⏭️  Skipped: {skipped}")
    if errors:
        print(f"  ❌ Errors: {len(errors)}")
        print(f"     {errors}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(migrate_user_ids())
