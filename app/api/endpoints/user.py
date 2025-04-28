import uuid
from datetime import datetime, timezone, timedelta
from typing import Annotated, List

from app.celery.clickhouse import process_event
from app.core.enums import EventNameEnum
from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.openapi.models import EmailStr
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.deps import get_db, get_current_user
from app.core.logging import AppLogger
from app.db.models import User
from app.db.services import user_crud, token_crud, password_reset
from app.schema.token import TokenResponse, RefreshTokenRequest
from app.schema.user import (
    UserCreate,
    UserOut,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserUpdateRequest,
)
from app.utils.auth import (
    get_password_hash,
    authenticate_user,
    create_refresh_token,
    decode_token,
    create_jwt_token,
    generate_token_response,
)
from app.utils.notification import handle_send_notification

logger = AppLogger().get_logger()

router = APIRouter()
USER_NOT_FOUND = "User not found"


@router.post("/signup", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = await get_password_hash(user.password)
    user.password = hashed_password
    db_user = await user_crud.create(db, user)
    process_event.delay(
        name=EventNameEnum.USER_CREATE,
        payload=db_user.to_dict(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        org_id=db_user.organization_id if db_user.organization_id else "none",
        user_id=db_user.id,
    )
    return db_user


@router.post("/login", response_model=TokenResponse)
async def login(
    username: Annotated[EmailStr, Form()], password: Annotated[str, Form()], db: AsyncSession = Depends(get_db)
):
    authenticated_user = await authenticate_user(db, username, password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires_delta = timedelta(minutes=30)
    output_dict = await generate_token_response(db, authenticated_user, access_token_expires_delta)
    return TokenResponse(**output_dict)


@router.get("/get-users", response_model=List[UserOut])
async def get_all_users(organization_id: str, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    try:
        users = await user_crud.get_all_users(db, organization_id, skip, limit)
        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)
        return users
    except Exception as e:
        logger.error(f"Error while fetching users: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching the users")


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = await decode_token(request.refresh_token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    stored_token = await token_crud.get_valid_token(db, token=request.refresh_token, user_id=user_id)
    if not stored_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user = stored_token.user

    access_token_expires_delta = timedelta(minutes=30)
    access_token, access_token_expires = await create_jwt_token(user=user, expires_delta=access_token_expires_delta)
    new_refresh_token, refresh_token_expires = await create_refresh_token(db, user_id)

    output_dict = {
        "access_token": access_token,
        "access_token_expiry": access_token_expires,
        "refresh_token": new_refresh_token,
        "refresh_token_expiry": refresh_token_expires,
        "token_type": "bearer",
    }
    return TokenResponse(**output_dict)


@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get_by_email(db, request.email)

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)

    new_hashed_password = await get_password_hash(request.new_password)

    db_user.password = new_hashed_password

    await db.commit()

    await db.refresh(db_user)

    return db_user


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, req: Request, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND)

    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    expires_at_naive = expires_at.replace(tzinfo=None)

    await password_reset.create_password_reset_token(db, user.id, token, expires_at_naive)

    domain_name = req.url.netloc
    domain_scheme = req.url.scheme
    reset_link = f"{domain_scheme}://{domain_name}/reset-password?token={token}"

    context = {"username": user.email, "name": user.name, "reset_token": token, "reset_link": reset_link}
    await handle_send_notification(
        recipient_addr=user.email,
        db=db,
        context=context,
        template_name=request.template_name,  # Use template_name from request
    )

    return {"msg": "Password reset email sent"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    reset_token = await password_reset.get_password_reset_token(db, request.token)
    if not reset_token:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    if request.new_password != request.confirm_new_password:
        raise HTTPException(status_code=400, detail="New password and confirmation do not match")

    user = await user_crud.get(db, reset_token.user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND)

    new_hashed_password = await get_password_hash(request.new_password)
    user.password = new_hashed_password

    await password_reset.mark_token_as_used(db, request.token)

    return {"msg": "Password reset successfully"}


@router.put("/update", response_model=UserOut)
async def update_user(request: UserUpdateRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info("Fetching the user")

        user = await user_crud.get_by_email(db, request.email)
        if not user:
            logger.info("User with email %s does not exist", request.email)
            raise HTTPException(status_code=404, detail="User with this email does not exist")
        logger.info("Updating user fields")
        if request.name:
            user.name = request.name
        if request.phone_number:
            user.phone_number = request.phone_number
        if request.is_active:
            user.is_active = request.is_active
        logger.info("Committing changes to database")
        await db.commit()
        await db.refresh(user)
        return user

    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the user")
