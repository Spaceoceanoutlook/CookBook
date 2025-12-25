from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, r, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.core.database import get_db
from cookbook.core.exceptions import AlreadyExistsError, AuthenticationError
from cookbook.core.security import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiration,
)
from cookbook.models.refresh_token import RefreshToken
from cookbook.repositories.refresh_token import RefreshTokenRepository
from cookbook.schemas.user import UserLogin, UserRead, UserRegister
from cookbook.services.user_service import login_user_service, register_user_service

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", response_model=UserRead)
async def register(
    new_user: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await register_user_service(
            db=db,
            email=new_user.email,
            name=new_user.name,
            password=new_user.password,
        )
        return user
    except AlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных",
        )


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    try:
        access_token, refresh_token = await login_user_service(
            db=db,
            email=form_data.username,
            password=form_data.password,
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
):
    token = await RefreshTokenRepository.get_by_token(
        db,
        refresh_token,
    )

    if not token or token.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    await RefreshTokenRepository.revoke(db, token)

    new_refresh_value = create_refresh_token()
    new_refresh = RefreshToken(
        token=new_refresh_value,
        user_id=token.user_id,
        expires_at=get_refresh_token_expiration(),
    )

    await RefreshTokenRepository.create(db, new_refresh)
    access_token = create_access_token(token.user_id)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_value,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
):
    token = await RefreshTokenRepository.get_by_token(
        db,
        refresh_token,
    )

    if token and not token.revoked:
        await RefreshTokenRepository.revoke(db, token)
        await db.commit()

    return {"detail": "Logged out"}
