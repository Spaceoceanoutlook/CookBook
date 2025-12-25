from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    @staticmethod
    async def create(
        db: AsyncSession,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        db.add(refresh_token)
        await db.flush()
        return refresh_token

    @staticmethod
    async def get_by_token(
        db: AsyncSession,
        token: str,
    ) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def revoke(
        db: AsyncSession,
        refresh_token: RefreshToken,
    ) -> None:
        refresh_token.revoked = True
        await db.flush()

    @staticmethod
    async def is_expired(refresh_token: RefreshToken) -> bool:
        return refresh_token.expires_at < datetime.utcnow()
