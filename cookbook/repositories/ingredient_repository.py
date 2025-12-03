from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.models import Ingredient


class IngredientRepository:
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str):
        stmt = select(Ingredient).where(Ingredient.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, ingredient_id: int):
        stmt = select(Ingredient).where(Ingredient.id == ingredient_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession):
        stmt = select(Ingredient).order_by(Ingredient.id)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, ingredient: Ingredient):
        db.add(ingredient)
        await db.flush()
        return ingredient

    @staticmethod
    async def delete(db: AsyncSession, ingredient: Ingredient):
        await db.delete(ingredient)
