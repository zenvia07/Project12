"""
User management routes with pagination
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional
from ..dependencies import get_current_user
from ..schemas import UserProfile
from ..database import get_database

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        id=str(current_user["_id"]),
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        email=current_user["email"],
        phone_number=current_user["phone_number"],
        date_of_birth=current_user["date_of_birth"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"]
    )


@router.get("/list")
async def list_users(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user)
):
    """List users with pagination (admin only - can be enhanced later)"""
    db = await get_database()
    
    # Calculate skip
    skip = (page - 1) * page_size
    
    # Get total count
    total = await db.users.count_documents({})
    
    # Get users with pagination
    cursor = db.users.find({}).skip(skip).limit(page_size).sort("created_at", -1)
    users = await cursor.to_list(length=page_size)
    
    # Format users (exclude sensitive data)
    user_list = []
    for user in users:
        user_list.append({
            "id": str(user["_id"]),
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "phone_number": user["phone_number"],
            "is_active": user.get("is_active", False),
            "created_at": user["created_at"]
        })
    
    # Calculate pagination metadata
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "data": user_list,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
