"""
Authentication routes: registration, login, activation, password management
"""
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Request
from datetime import timedelta
from ..schemas import (
    UserRegister, UserRegisterResponse,
    UserLogin, UserLoginResponse, TokenResponse,
    ChangePassword, ForgotPassword, ResetPassword,
    ActivateAccount, ActivateAccountResponse,
    RefreshTokenRequest, MessageResponse
)
from ..db_helpers import (
    get_user_by_email, get_user_by_phone, create_user,
    activate_user, update_password, check_password_in_history,
    set_activation_token, get_user_by_activation_token,
    set_reset_password_token, get_user_by_reset_token,
    clear_reset_password_token, increment_failed_login_attempts,
    reset_failed_login_attempts, lock_user_account
)
from ..auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    verify_token, create_activation_token,
    create_reset_password_token
)
from ..email_service import send_activation_email, send_password_reset_email
from ..dependencies import get_current_user
from ..database import settings

router = APIRouter()


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserRegister,
    background_tasks: BackgroundTasks
):
    # Rate limiting handled by middleware
    """Register a new user"""
    # Check if email already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if phone number already exists
    existing_phone = await get_user_by_phone(user_data.phone_number)
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create activation token
    activation_token = create_activation_token()
    
    # Create user document
    user_doc = {
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "date_of_birth": user_data.date_of_birth,
        "email": user_data.email.lower(),
        "phone_number": user_data.phone_number,
        "hashed_password": hashed_password,
        "is_active": False,
        "is_locked": False,
        "failed_login_attempts": 0,
        "password_history": []
    }
    
    # Create user
    user_id = await create_user(user_doc)
    
    # Set activation token
    await set_activation_token(user_id, activation_token)
    
    # Send activation email in background
    user_name = f"{user_data.first_name} {user_data.last_name}"
    recipient_email = user_data.email.lower().strip()  # Ensure clean email
    print(f"[REGISTRATION] User registered with email: {recipient_email}")
    print(f"[REGISTRATION] Sending activation email TO: {recipient_email}")
    print(f"[REGISTRATION] Email will be sent FROM: {settings.email_from}")
    background_tasks.add_task(
        send_activation_email,
        recipient_email,  # Send to the user's email, not the sender's
        activation_token,
        user_name
    )
    
    return UserRegisterResponse(
        message=f"Registration successful. Please check your email ({user_data.email}) to activate your account. Check spam folder if not received.",
        user_id=user_id,
        email=user_data.email
    )


@router.post("/activate", response_model=ActivateAccountResponse)
async def activate_account(activation_data: ActivateAccount):
    """Activate user account"""
    user = await get_user_by_activation_token(activation_data.token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired activation token"
        )
    
    user_id = str(user["_id"])
    await activate_user(user_id)
    
    return ActivateAccountResponse(
        message="Account activated successfully. You can now log in.",
        user_id=user_id
    )


@router.post("/login", response_model=UserLoginResponse)
async def login(
    request: Request,
    credentials: UserLogin
):
    # Rate limiting handled by middleware
    """User login"""
    # Get user by email
    user = await get_user_by_email(credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if account is locked
    if user.get("is_locked"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked due to multiple failed login attempts. Please contact support."
        )
    
    # Check if account is activated
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not activated. Please check your email and activate your account."
        )
    
    # Verify password
    if not verify_password(credentials.password, user["hashed_password"]):
        user_id = str(user["_id"])
        result = await increment_failed_login_attempts(user_id)
        
        if result["is_locked"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account locked due to 3 consecutive failed login attempts. Please contact support."
            )
        
        attempts_remaining = 3 - result["attempts"]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid email or password. {attempts_remaining} attempt(s) remaining."
        )
    
    # Reset failed login attempts on successful login
    user_id = str(user["_id"])
    await reset_failed_login_attempts(user_id)
    
    # Create tokens
    token_data = {"sub": user_id, "email": user["email"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Prepare user info (exclude sensitive data)
    user_info = {
        "id": user_id,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "phone_number": user["phone_number"]
    }
    
    return UserLoginResponse(
        message="Login successful",
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60
        ),
        user=user_info
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("sub")
    user = await get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Check if account is active and not locked
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not activated"
        )
    
    if user.get("is_locked"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked"
        )
    
    # Create new access token
    new_token_data = {"sub": user_id, "email": user["email"]}
    access_token = create_access_token(new_token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=token_data.refresh_token,  # Refresh token remains the same
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    user_id = str(current_user["_id"])
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_hashed_password = hash_password(password_data.new_password)
    
    # Check if new password matches any of the last 3 passwords
    if await check_password_in_history(user_id, new_hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as any of your last 3 passwords"
        )
    
    # Update password
    success = await update_password(user_id, new_hashed_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return MessageResponse(message="Password changed successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: Request,
    forgot_data: ForgotPassword,
    background_tasks: BackgroundTasks
):
    # Rate limiting handled by middleware
    """Request password reset"""
    user = await get_user_by_email(forgot_data.email)
    
    if not user:
        # Don't reveal if email exists or not (security best practice)
        return MessageResponse(
            message="If the email exists, a password reset link has been sent."
        )
    
    # Create reset token
    reset_token = create_reset_password_token()
    user_id = str(user["_id"])
    await set_reset_password_token(user_id, reset_token)
    
    # Send reset email in background
    user_name = f"{user.get('first_name', 'User')} {user.get('last_name', '')}"
    background_tasks.add_task(
        send_password_reset_email,
        user["email"],
        reset_token,
        user_name
    )
    
    return MessageResponse(
        message="If the email exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(reset_data: ResetPassword):
    """Reset password using token"""
    user = await get_user_by_reset_token(reset_data.token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user_id = str(user["_id"])
    
    # Hash new password
    new_hashed_password = hash_password(reset_data.new_password)
    
    # Check if new password matches any of the last 3 passwords
    if await check_password_in_history(user_id, new_hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as any of your last 3 passwords"
        )
    
    # Update password
    success = await update_password(user_id, new_hashed_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )
    
    # Clear reset token
    await clear_reset_password_token(user_id)
    
    return MessageResponse(message="Password reset successfully")


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": str(current_user["_id"]),
        "first_name": current_user["first_name"],
        "last_name": current_user["last_name"],
        "email": current_user["email"],
        "phone_number": current_user["phone_number"],
        "date_of_birth": current_user["date_of_birth"],
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"]
    }
