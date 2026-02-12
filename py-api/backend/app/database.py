"""
Database connection and configuration using Motor (async MongoDB driver)
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    mongodb_uri: str
    mongodb_db_name: str = "login_app"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    environment: str = "development"
    api_prefix: str = "/api"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = ""
    rate_limit_per_minute: int = 60
    cache_ttl_seconds: int = 300

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_ignore_empty = True


# Load settings with better error handling
import sys
import time
from pydantic import ValidationError

try:
    settings = Settings()
except ValidationError as e:
    # Print error message only once, then wait before exit to prevent rapid restarts
    print("\n" + "="*80)
    print("ERROR: Missing required environment variables!")
    print("="*80)
    print("\nThe following environment variables MUST be set in Railway:")
    print("  - MONGODB_URI (required)")
    print("  - JWT_SECRET_KEY (required)")
    print("\nPlease add these variables in Railway dashboard:")
    print("  1. Go to your Railway project")
    print("  2. Click on your service")
    print("  3. Go to 'Variables' tab")
    print("  4. Add MONGODB_URI and JWT_SECRET_KEY")
    print("\nSee py-api/RAILWAY_ENV_VARIABLES.txt for all required variables.")
    print("="*80)
    print("\nWaiting 30 seconds before exit to prevent rapid restarts...")
    print("Add the environment variables in Railway to fix this issue.\n")
    time.sleep(30)  # Wait 30 seconds before exiting to reduce restart spam
    sys.exit(1)
except Exception as e:
    print(f"\nERROR: Failed to load settings: {e}\n")
    time.sleep(30)
    sys.exit(1)

# Global database client
client: Optional[AsyncIOMotorClient] = None
database = None


async def connect_to_mongo():
    """Create database connection"""
    global client, database
    try:
        from urllib.parse import quote, urlparse, urlunparse, parse_qs, urlencode
        
        # Validate database name - ensure it's not empty
        db_name = settings.mongodb_db_name.strip() if settings.mongodb_db_name else "login_app"
        if not db_name:
            db_name = "login_app"
        
        # Clean and validate MongoDB URI
        uri = settings.mongodb_uri.strip()
        
        # Only modify URI if password needs encoding
        parsed = urlparse(uri)
        if parsed.password and ('<' in parsed.password or '>' in parsed.password or '@' in parsed.password):
            # Encode password and reconstruct URI properly
            encoded_password = quote(parsed.password, safe='')
            netloc = f"{parsed.username}:{encoded_password}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            
            # Preserve query string properly
            query = parsed.query
            if query:
                # Validate query parameters are in key=value format
                try:
                    parse_qs(query, strict_parsing=True)
                except ValueError:
                    # If query is malformed, remove it
                    print(f"[WARNING] Removing invalid query parameters from MongoDB URI")
                    query = ""
            
            uri = urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, query, parsed.fragment))
        
        # Use URI as-is if no password encoding needed
        client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000
        )
        # Test the connection
        await client.admin.command('ping')
        database = client[db_name]
        print(f"[SUCCESS] Connected to MongoDB: {db_name}")
        return database
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("[INFO] MongoDB connection closed")


async def get_database():
    """Get database instance"""
    if database is None:
        await connect_to_mongo()
    return database


async def create_indexes():
    """Create database indexes for better performance"""
    db = await get_database()
    
    # Create indexes on users collection
    users_collection = db.users
    
    # Unique index on email
    await users_collection.create_index("email", unique=True)
    
    # Unique index on phone_number
    await users_collection.create_index("phone_number", unique=True, sparse=True)
    
    # Index on is_active for faster queries
    await users_collection.create_index("is_active")
    
    # Index on created_at for sorting
    await users_collection.create_index("created_at")
    
    print("[SUCCESS] Database indexes created")
