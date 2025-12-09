import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.exceptions import AlreadyExistsError, NotFoundError
from cookbook.models import Ingredient
from cookbook.repositories.ingredient_repository import IngredientRepository
from cookbook.schemas.ingredient import IngredientCreate
from cookbook.services.ingredient_service import (
    create_ingredient_service,
    delete_ingredient_service,
    get_all_ingredients,
)


async def test_get_all_ingredients(db: AsyncSession):
    ing1 = IngredientCreate(name="salt")
    ing2 = IngredientCreate(name="Sugar")
    await create_ingredient_service(ing1, db)
    await create_ingredient_service(ing2, db)

    ingredients = await get_all_ingredients(db)
    ingredient_names = [ingredient.name for ingredient in ingredients]

    assert len(ingredients) == 2
    assert "salt" in ingredient_names
    assert "sugar" in ingredient_names


async def test_create_ingredient_success(db: AsyncSession):
    ing = IngredientCreate(name="Pepper")

    result = await create_ingredient_service(ing, db)

    assert result.id is not None
    assert result.name == "pepper"


async def test_create_ingredient_already_exists(db: AsyncSession):
    ing = IngredientCreate(name="milk")
    await create_ingredient_service(ing, db)
    new_ing = IngredientCreate(name="Milk")
    with pytest.raises(AlreadyExistsError):
        await create_ingredient_service(new_ing, db)


async def test_delete_ingredient_success(db: AsyncSession):
    ing = IngredientCreate(name="oil")
    existing_ing = await create_ingredient_service(ing, db)
    deleted = await delete_ingredient_service(existing_ing.id, db)

    assert deleted.id == existing_ing.id

    check = await IngredientRepository.get_by_id(db, existing_ing.id)
    assert check is None


async def test_delete_ingredient_not_found(db: AsyncSession):
    with pytest.raises(NotFoundError):
        await delete_ingredient_service(9, db)
