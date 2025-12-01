import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.models import Ingredient, Recipe
from cookbook.repositories.ingredient_repository import IngredientRepository
from cookbook.repositories.recipe_repository import RecipeRepository


async def create_test_recipe(db: AsyncSession) -> Recipe:
    salt = Ingredient(name="Salt")
    tomato = Ingredient(name="Tomato")
    await IngredientRepository.create(db, salt)
    await IngredientRepository.create(db, tomato)
    await db.commit()

    recipe = Recipe(
        title="Tomato Salad",
        description="A simple salad with tomato and salt",
        ingredients=[salt, tomato],
    )
    await RecipeRepository.create(db, recipe)
    await db.commit()
    return recipe


async def test_create_recipe(db: AsyncSession):
    created = await create_test_recipe(db)
    assert created.title == "Tomato Salad"
    assert len(created.ingredients) == 2


async def test_get_recipe_by_id(db: AsyncSession):
    recipe = await create_test_recipe(db)
    fetched = await RecipeRepository.get_by_id(db, recipe.id)

    assert fetched.title == recipe.title
    names = [ing.name for ing in fetched.ingredients]
    assert "Salt" in names
    assert "Tomato" in names


async def test_delete_recipe(db: AsyncSession):
    recipe = await create_test_recipe(db)
    await RecipeRepository.delete(db, recipe)

    deleted = await RecipeRepository.get_by_id(db, recipe.id)
    assert deleted is None
