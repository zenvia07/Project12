"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


# Registration Schemas
class UserRegister(BaseModel):
    """User registration request schema"""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: datetime
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8, max_length=100)

    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Remove spaces, dashes, and parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        # Check if it contains only digits and optional + at start
        if not re.match(r'^\+?[1-9]\d{9,14}$', cleaned):
            raise ValueError('Invalid phone number format')
        return cleaned

    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserRegisterResponse(BaseModel):
    """User registration response schema"""
    message: str
    user_id: str
    email: str


# Login Schemas
class UserLogin(BaseModel):
    """User login request schema"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserLoginResponse(BaseModel):
    """User login response schema"""
    message: str
    tokens: TokenResponse
    user: dict


# Password Change Schemas
class ChangePassword(BaseModel):
    """Change password request schema"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class ForgotPassword(BaseModel):
    """Forgot password request schema"""
    email: EmailStr


class ResetPassword(BaseModel):
    """Reset password request schema"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


# User Profile Schemas
class UserProfile(BaseModel):
    """User profile response schema"""
    id: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    date_of_birth: datetime
    is_active: bool
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Activation Schemas
class ActivateAccount(BaseModel):
    """Account activation request schema"""
    token: str


class ActivateAccountResponse(BaseModel):
    """Account activation response schema"""
    message: str
    user_id: str


# Refresh Token Schema
class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


# Generic Response Schemas
class MessageResponse(BaseModel):
    """Generic message response schema"""
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
