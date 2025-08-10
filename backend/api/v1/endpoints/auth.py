# backend/api/v1/endpoints/auth.py

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from backend.routes.auth_routes import fastapi_users, auth_backend
from backend.schemas.user_schema import UserRead, UserCreate, UserUpdate
from backend.database.models import User
from backend.database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
try:
    from backend.middleware.rate_limiting import limiter, RateLimits, create_rate_limit_decorator
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    # Mock limiter and decorator for when rate limiting is not available
    def create_rate_limit_decorator(limit: str):
        def decorator(func):
            return func
        return decorator
    
    class MockLimiter:
        def limit(self, limit_string):
            return create_rate_limit_decorator(limit_string)
    limiter = MockLimiter()
    
    # Mock RateLimits class
    RateLimits = type('RateLimits', (), {
        'API_READ': '30/minute',
        'AUTH_LOGIN': '5/minute',
        'AUTH_REGISTER': '3/minute', 
        'AUTH_RESET_PASSWORD': '2/minute'
    })()

router = APIRouter()

# Simple password hashing with fallback (matches seed_db.py)
def hash_password_simple(password: str) -> str:
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    except Exception:
        # Fallback to MD5 - NOT secure, only for development
        import hashlib
        return f"fallback_{hashlib.md5(password.encode()).hexdigest()}"

@router.post("/register-simple", response_model=UserRead, summary="User Registration")
@create_rate_limit_decorator(RateLimits.AUTH_REGISTER)
async def register_user(
    request: Request,
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    User registration endpoint with bcrypt fallback
    Replaces the broken FastAPI Users registration
    """
    try:
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="REGISTER_USER_ALREADY_EXISTS")

        # Create new user
        hashed_password = hash_password_simple(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name or user_data.email,
            is_active=True,
            is_verified=True,  # Auto-verify for now
            is_superuser=False
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return UserRead.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/register", response_model=UserRead, summary="User Registration (Proxy)")
@create_rate_limit_decorator(RateLimits.AUTH_REGISTER)  
async def register_proxy(
    request: Request,
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Proxy endpoint that forwards to the working registration logic
    """
    return await register_user(request, user_data, session)

# Get the current user (with rate limiting)
@router.get("/me", response_model=UserRead, summary="Get Current User")
@create_rate_limit_decorator(RateLimits.API_READ)
async def get_current_user(
    request: Request,
    user: User = Depends(fastapi_users.current_user(active=True))
):
    """
    Get the currently authenticated user's information
    
    Returns:
        UserRead: Current user's profile information
    """
    return user

# Include FastAPIUsers authentication routes with rate limiting applied at router level
auth_jwt_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router(UserRead, UserCreate)
reset_password_router = fastapi_users.get_reset_password_router()
verify_router = fastapi_users.get_verify_router(UserRead)
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)

# Add rate limiting to auth routers (applied to all endpoints in each router)
# Only apply if slowapi is available
try:
    if hasattr(limiter, '__class__') and 'MockLimiter' not in str(limiter.__class__):
        for route in auth_jwt_router.routes:
            if hasattr(route, 'endpoint'):
                # Apply stricter rate limits to login endpoints
                route.endpoint = limiter.limit(RateLimits.AUTH_LOGIN)(route.endpoint)

        for route in register_router.routes:
            if hasattr(route, 'endpoint'):
                route.endpoint = limiter.limit(RateLimits.AUTH_REGISTER)(route.endpoint)

        for route in reset_password_router.routes:
            if hasattr(route, 'endpoint'):
                route.endpoint = limiter.limit(RateLimits.AUTH_RESET_PASSWORD)(route.endpoint)
except Exception:
    # Skip rate limiting if not available
    pass

# Include the routers
router.include_router(auth_jwt_router, prefix="/jwt", tags=["auth"])
# router.include_router(register_router, tags=["auth"])  # DISABLED: FastAPI Users registration broken due to bcrypt
router.include_router(reset_password_router, tags=["auth"])
router.include_router(verify_router, tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])