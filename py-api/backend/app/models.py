"""
Database models/schemas for MongoDB documents
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic v2"""
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
            raise ValueError("Invalid ObjectId string")
        raise ValueError("Invalid ObjectId")


class PasswordHistory(BaseModel):
    """Stores last 3 passwords for password change validation"""
    hashed_password: str
    changed_at: datetime


class User(BaseModel):
    """User document model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    first_name: str
    last_name: str
    date_of_birth: datetime
    email: EmailStr
    phone_number: str
    hashed_password: str
    is_active: bool = False  # Account activation status
    is_locked: bool = False  # Account lock status
    failed_login_attempts: int = 0
    last_failed_login: Optional[datetime] = None
    password_history: List[PasswordHistory] = []  # Last 3 passwords
    activation_token: Optional[str] = None
    activation_token_expires: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class UserInDB(User):
    """User model for database operations"""
    pass


# MongoDB document structure (for reference)
"""
User Document Structure:
{
    "_id": ObjectId("..."),
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": ISODate("1990-01-01T00:00:00Z"),
    "email": "john.doe@example.com",
    "phone_number": "+1234567890",
    "hashed_password": "$2b$12$...",
    "is_active": false,
    "is_locked": false,
    "failed_login_attempts": 0,
    "last_failed_login": null,
    "password_history": [
        {
            "hashed_password": "$2b$12$...",
            "changed_at": ISODate("2024-01-01T00:00:00Z")
        }
    ],
    "activation_token": "random-token-string",
    "activation_token_expires": ISODate("2024-01-02T00:00:00Z"),
    "created_at": ISODate("2024-01-01T00:00:00Z"),
    "updated_at": ISODate("2024-01-01T00:00:00Z")
}
"""
