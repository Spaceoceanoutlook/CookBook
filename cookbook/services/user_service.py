from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.core.exceptions import AlreadyExistsError, AuthenticationError
from cookbook.core.security import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiration,
    hash_password,
    verify_password,
)
from cookbook.models import User
from cookbook.models.refresh_token import RefreshToken
from cookbook.repositories.refresh_token import RefreshTokenRepository
from cookbook.repositories.user_repository import UserRepository


async def register_user_service(
    db: AsyncSession, email: str, name: str, password: str
) -> User:
    existing_user = await UserRepository.get_by_email(db, email)
    if existing_user:
        raise AlreadyExistsError(f"Пользователь '{email}' уже существует")
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
    )

    try:
        created_user = await UserRepository.create(db, user)
        await db.commit()
        await db.refresh(created_user)
        return created_user
    except Exception:
        await db.rollback()
        raise


async def login_user_service(
    db: AsyncSession, email: str, password: str
) -> tuple[str, str]:
    user = await UserRepository.get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError("Неправильный email или пароль")

    access_token = create_access_token(user.id)

    refresh_token_value = create_refresh_token()
    refresh_token = RefreshToken(
        token=refresh_token_value,
        user_id=user.id,
        expires_at=get_refresh_token_expiration(),
    )
    await RefreshTokenRepository.create(db, refresh_token)
    await db.commit()

    return access_token, refresh_token_value
