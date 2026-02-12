"""
Database helper functions for user operations
"""
from typing import Optional
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from .models import User, PasswordHistory
from .database import get_database


async def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    db = await get_database()
    user = await db.users.find_one({"email": email.lower()})
    return user


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID"""
    db = await get_database()
    if not ObjectId.is_valid(user_id):
        return None
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    return user


async def get_user_by_phone(phone_number: str) -> Optional[dict]:
    """Get user by phone number"""
    db = await get_database()
    user = await db.users.find_one({"phone_number": phone_number})
    return user


async def create_user(user_data: dict) -> str:
    """Create a new user"""
    db = await get_database()
    user_data["email"] = user_data["email"].lower()
    user_data["created_at"] = datetime.utcnow()
    user_data["updated_at"] = datetime.utcnow()
    result = await db.users.insert_one(user_data)
    return str(result.inserted_id)


async def update_user(user_id: str, update_data: dict) -> bool:
    """Update user data"""
    db = await get_database()
    if not ObjectId.is_valid(user_id):
        return False
    update_data["updated_at"] = datetime.utcnow()
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0


async def activate_user(user_id: str) -> bool:
    """Activate user account"""
    return await update_user(user_id, {
        "is_active": True,
        "activation_token": None,
        "activation_token_expires": None
    })


async def lock_user_account(user_id: str) -> bool:
    """Lock user account"""
    return await update_user(user_id, {
        "is_locked": True
    })


async def unlock_user_account(user_id: str) -> bool:
    """Unlock user account"""
    return await update_user(user_id, {
        "is_locked": False,
        "failed_login_attempts": 0,
        "last_failed_login": None
    })


async def increment_failed_login_attempts(user_id: str) -> dict:
    """Increment failed login attempts and lock if threshold reached"""
    db = await get_database()
    if not ObjectId.is_valid(user_id):
        return {"success": False}
    
    user = await get_user_by_id(user_id)
    if not user:
        return {"success": False}
    
    new_attempts = user.get("failed_login_attempts", 0) + 1
    update_data = {
        "failed_login_attempts": new_attempts,
        "last_failed_login": datetime.utcnow()
    }
    
    # Lock account after 3 failed attempts
    if new_attempts >= 3:
        update_data["is_locked"] = True
    
    await update_user(user_id, update_data)
    return {
        "success": True,
        "attempts": new_attempts,
        "is_locked": new_attempts >= 3
    }


async def reset_failed_login_attempts(user_id: str) -> bool:
    """Reset failed login attempts on successful login"""
    return await update_user(user_id, {
        "failed_login_attempts": 0,
        "last_failed_login": None
    })


async def update_password(user_id: str, new_hashed_password: str) -> bool:
    """Update user password and maintain password history"""
    db = await get_database()
    if not ObjectId.is_valid(user_id):
        return False
    
    user = await get_user_by_id(user_id)
    if not user:
        return False
    
    # Get current password history
    password_history = user.get("password_history", [])
    
    # Add current password to history (keep last 3)
    current_password = user.get("hashed_password")
    if current_password:
        password_history.append(PasswordHistory(
            hashed_password=current_password,
            changed_at=datetime.utcnow()
        ).dict())
        # Keep only last 3 passwords
        password_history = password_history[-3:]
    
    # Update password and history
    update_data = {
        "hashed_password": new_hashed_password,
        "password_history": password_history,
        "updated_at": datetime.utcnow()
    }
    
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0


async def check_password_in_history(user_id: str, hashed_password: str) -> bool:
    """Check if password exists in last 3 passwords"""
    user = await get_user_by_id(user_id)
    if not user:
        return False
    
    password_history = user.get("password_history", [])
    for pwd_entry in password_history:
        if pwd_entry.get("hashed_password") == hashed_password:
            return True
    return False


async def set_activation_token(user_id: str, token: str, expires_in_hours: int = 24) -> bool:
    """Set activation token for user"""
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    return await update_user(user_id, {
        "activation_token": token,
        "activation_token_expires": expires_at
    })


async def get_user_by_activation_token(token: str) -> Optional[dict]:
    """Get user by activation token"""
    db = await get_database()
    
    # Clean the token (remove any whitespace, URL encoding issues)
    token = token.strip()
    
    # Try to find user with this token
    user = await db.users.find_one({
        "activation_token": token
    })
    
    if not user:
        return None
    
    # Check if token is expired
    expires = user.get("activation_token_expires")
    if expires:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        # Handle both timezone-aware and naive datetimes
        if expires.tzinfo is None:
            from datetime import timezone
            expires = expires.replace(tzinfo=timezone.utc)
        
        if expires < now:
            print(f"[TOKEN] Token expired. Expires: {expires}, Now: {now}")
            return None
    
    return user


async def set_reset_password_token(user_id: str, token: str, expires_in_hours: int = 1) -> bool:
    """Set password reset token for user"""
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    return await update_user(user_id, {
        "reset_password_token": token,
        "reset_password_token_expires": expires_at
    })


async def get_user_by_reset_token(token: str) -> Optional[dict]:
    """Get user by password reset token"""
    db = await get_database()
    user = await db.users.find_one({
        "reset_password_token": token,
        "reset_password_token_expires": {"$gt": datetime.utcnow()}
    })
    return user


async def clear_reset_password_token(user_id: str) -> bool:
    """Clear password reset token after use"""
    return await update_user(user_id, {
        "reset_password_token": None,
        "reset_password_token_expires": None
    })
