from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.models import Ingredient
from cookbook.repositories.ingredient_repository import IngredientRepository
from cookbook.schemas.ingredient import IngredientCreate


async def get_all_ingredients(db: AsyncSession):
    return await IngredientRepository.get_all(db)


async def create_ingredient_service(data: IngredientCreate, db: AsyncSession):
    existing = await IngredientRepository.get_by_name(db, data.name)
    if existing:
        raise ValueError(f"Ингредиент '{data.name}' уже существует")
    ingredient = Ingredient(**data.model_dump())

    try:
        await IngredientRepository.create(db, ingredient)
        await db.commit()
        await db.refresh(ingredient)
        return ingredient
    except Exception:
        await db.rollback()
        raise


async def delete_ingredient_service(ingredient_id: int, db: AsyncSession):
    ingredient = await IngredientRepository.get_by_id(db, ingredient_id)
    if ingredient is None:
        return None

    try:
        await IngredientRepository.delete(db, ingredient)
        await db.commit()
        return ingredient

    except Exception:
        await db.rollback()
        raise
