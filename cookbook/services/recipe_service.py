from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.exceptions import NotFoundError
from cookbook.models import Ingredient, Recipe
from cookbook.repositories.ingredient_repository import IngredientRepository
from cookbook.repositories.recipe_repository import RecipeRepository
from cookbook.schemas.recipe import RecipeCreate, RecipeUpdate


async def get_all_recipes(db: AsyncSession):
    return await RecipeRepository.get_all(db)


async def get_recipe_by_id(recipe_id: int, db: AsyncSession):
    return await RecipeRepository.get_by_id(db, recipe_id)


async def create_recipe_service(data: RecipeCreate, db: AsyncSession):
    recipe = Recipe(title=data.title, description=data.description)

    try:
        for ing_data in data.ingredients:
            ingredient = await IngredientRepository.get_by_name(db, ing_data.name)
            if ingredient is None:
                ingredient = Ingredient(name=ing_data.name)
                await IngredientRepository.create(db, ingredient)

            recipe.ingredients.append(ingredient)

        await RecipeRepository.create(db, recipe)
        await db.commit()
        await db.refresh(recipe, attribute_names=["ingredients"])
        return recipe

    except Exception:
        await db.rollback()
        raise


async def update_recipe_service(recipe_id: int, data: RecipeUpdate, db: AsyncSession):
    recipe = await RecipeRepository.get_by_id(db, recipe_id)
    if recipe is None:
        raise NotFoundError("Рецепт не найден")

    try:
        update_data = data.model_dump(exclude_unset=True)
        if "title" in update_data:
            recipe.title = update_data["title"]
        if "description" in update_data:
            recipe.description = update_data["description"]
        if "ingredients" in update_data:
            new_ingredients = []
            for ing_data in update_data["ingredients"]:
                ingredient = await IngredientRepository.get_by_name(db, ing_data['name'])
                if ingredient is None:
                    ingredient = Ingredient(name=ing_data['name'])
                    await IngredientRepository.create(db, ingredient)
                new_ingredients.append(ingredient)

            recipe.ingredients = new_ingredients

        await RecipeRepository.update(db, recipe)
        await db.commit()
        await db.refresh(recipe, attribute_names=["ingredients"])
        return recipe

    except Exception:
        await db.rollback()
        raise


async def delete_recipe_service(recipe_id: int, db: AsyncSession):
    recipe = await RecipeRepository.get_by_id(db, recipe_id)
    if recipe is None:
        raise NotFoundError("Рецепт не найден")

    try:
        await RecipeRepository.delete(db, recipe)
        await db.commit()
        return recipe

    except Exception:
        await db.rollback()
        raise
