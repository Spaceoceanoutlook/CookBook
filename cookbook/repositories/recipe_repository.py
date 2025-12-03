from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from cookbook.models import Recipe


class RecipeRepository:
    @staticmethod
    async def get_all(db: AsyncSession):
        stmt = (
            select(Recipe).options(selectinload(Recipe.ingredients)).order_by(Recipe.id)
        )
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, recipe_id: int):
        stmt = (
            select(Recipe)
            .where(Recipe.id == recipe_id)
            .options(selectinload(Recipe.ingredients))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, recipe: Recipe):
        db.add(recipe)
        await db.flush()
        return recipe

    @staticmethod
    async def delete(db: AsyncSession, recipe: Recipe):
        await db.delete(recipe)

    @staticmethod
    async def update(db: AsyncSession, recipe: Recipe):
        await db.flush()
        return recipe
