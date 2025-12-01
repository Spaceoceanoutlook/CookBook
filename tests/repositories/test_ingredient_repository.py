import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.models import Ingredient
from cookbook.repositories.ingredient_repository import IngredientRepository


async def create_test_ingredient(db: AsyncSession, name: str) -> Ingredient:
    ingredient = Ingredient(name=name)
    created = await IngredientRepository.create(db, ingredient)
    await db.commit()
    return created


async def test_create_ingredient(db: AsyncSession):
    created = await create_test_ingredient(db, "Salt")
    assert created.name == "Salt"


async def test_get_by_name(db: AsyncSession):
    created = await create_test_ingredient(db, "Sugar")
    
    fetched = await IngredientRepository.get_by_name(db, "Sugar")
    assert fetched.name == "Sugar"
    assert fetched.id == created.id


async def test_get_by_id(db: AsyncSession):
    created = await create_test_ingredient(db, "Pepper")
    
    fetched = await IngredientRepository.get_by_id(db, created.id)
    assert fetched.id == created.id


async def test_get_all(db: AsyncSession):
    await create_test_ingredient(db, "Salt")
    await create_test_ingredient(db, "Sugar")
    
    all_ingredients = await IngredientRepository.get_all(db)
    names = [ing.name for ing in all_ingredients]

    assert "Salt" in names
    assert "Sugar" in names


async def test_delete_ingredient(db: AsyncSession):
    created = await create_test_ingredient(db, "Pepper")
    
    await IngredientRepository.delete(db, created)
    await db.commit()

    fetched = await IngredientRepository.get_by_id(db, created.id)
    assert fetched is None