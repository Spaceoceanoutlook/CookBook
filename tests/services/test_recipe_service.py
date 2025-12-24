import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.core.exceptions import NotFoundError
from cookbook.models import Ingredient, Recipe
from cookbook.repositories.ingredient_repository import IngredientRepository
from cookbook.repositories.recipe_repository import RecipeRepository
from cookbook.schemas.ingredient import IngredientCreate
from cookbook.schemas.recipe import RecipeCreate, RecipeUpdate
from cookbook.services.ingredient_service import create_ingredient_service
from cookbook.services.recipe_service import (
    create_recipe_service,
    delete_recipe_service,
    get_all_recipes,
    get_recipe_by_id,
    update_recipe_service,
)


async def test_get_all_recipes(db: AsyncSession, test_user):
    recipe_data1 = RecipeCreate(
        title="Pancakes",
        description="Delicious pancakes",
        ingredients=[IngredientCreate(name="flour"), IngredientCreate(name="eggs")],
    )
    recipe_data2 = RecipeCreate(
        title="Omelette",
        description="Simple omelette",
        ingredients=[IngredientCreate(name="eggs"), IngredientCreate(name="cheese")],
    )
    await create_recipe_service(recipe_data1, db, test_user)
    await create_recipe_service(recipe_data2, db, test_user)

    recipes = await get_all_recipes(db)

    assert len(recipes) == 2
    titles = {recipe.title for recipe in recipes}
    assert titles == {"pancakes", "omelette"}
    descriptions = {recipe.description for recipe in recipes}
    assert descriptions == {"Delicious pancakes", "Simple omelette"}


async def test_get_recipe_by_id_success(db: AsyncSession, test_user):
    recipe_data = RecipeCreate(
        title="Soup",
        description="Vegetable soup",
        ingredients=[IngredientCreate(name="carrot"), IngredientCreate(name="potato")],
    )
    created_recipe = await create_recipe_service(recipe_data, db, test_user)

    recipe = await get_recipe_by_id(created_recipe.id, db)

    assert recipe.id == created_recipe.id
    assert recipe.title == "soup"
    assert recipe.description == "Vegetable soup"
    assert len(recipe.ingredients) == 2
    ingredient_names = {ing.name for ing in recipe.ingredients}
    assert ingredient_names == {"carrot", "potato"}


async def test_get_recipe_by_id_not_found(db: AsyncSession):
    with pytest.raises(NotFoundError):
        await get_recipe_by_id(9, db)


async def test_create_recipe_service_success(db: AsyncSession, test_user):
    recipe_data = RecipeCreate(
        title="Pizza",
        description="Homemade pizza",
        ingredients=[IngredientCreate(name="flour"), IngredientCreate(name="cheese")],
    )

    result = await create_recipe_service(recipe_data, db, test_user)

    assert result.id is not None
    assert result.title == "pizza"
    assert result.description == "Homemade pizza"
    assert len(result.ingredients) == 2
    ingredient_names = {ing.name for ing in result.ingredients}
    assert ingredient_names == {"flour", "cheese"}


async def test_create_recipe_service_creates_new_ingredients(
    db: AsyncSession, test_user
):
    ing = IngredientCreate(name="Pepper")
    await create_ingredient_service(ing, db)

    recipe_data = RecipeCreate(
        title="Salad",
        description="Simple salad",
        ingredients=[
            IngredientCreate(name="Pepper"),
            IngredientCreate(name="cucumber"),
        ],
    )

    result = await create_recipe_service(recipe_data, db, test_user)

    assert result.title == "salad"
    assert len(result.ingredients) == 2
    ingredient_names = {ing.name for ing in result.ingredients}
    assert ingredient_names == {
        "pepper",
        "cucumber",
    }

    cucumber_db = await IngredientRepository.get_by_name(db, "cucumber")
    assert cucumber_db is not None
    assert cucumber_db.name == "cucumber"


async def test_update_recipe_service_success(db: AsyncSession, test_user):
    initial_data = RecipeCreate(
        title="Cake",
        description="Chocolate cake",
        ingredients=[IngredientCreate(name="flour"), IngredientCreate(name="sugar")],
    )
    created_recipe = await create_recipe_service(initial_data, db, test_user)

    update_data = RecipeUpdate(
        title="Updated Cake",
        description="New description for cake",
        ingredients=[IngredientCreate(name="flour"), IngredientCreate(name="milk")],
    )

    updated_recipe = await update_recipe_service(
        created_recipe.id, update_data, db, test_user
    )

    assert updated_recipe.id == created_recipe.id
    assert updated_recipe.title == "updated cake"
    assert updated_recipe.description == "New description for cake"
    ingredient_names = {ing.name for ing in updated_recipe.ingredients}
    assert ingredient_names == {"flour", "milk"}


async def test_update_recipe_service_partial_update(db: AsyncSession, test_user):
    initial_data = RecipeCreate(
        title="Salad",
        description="Green salad",
        ingredients=[IngredientCreate(name="onion"), IngredientCreate(name="tomato")],
    )
    created_recipe = await create_recipe_service(initial_data, db, test_user)

    update_data = RecipeUpdate(description="Fresh green salad")

    updated_recipe = await update_recipe_service(
        created_recipe.id, update_data, db, test_user
    )

    assert updated_recipe.id == created_recipe.id
    assert updated_recipe.title == "salad"
    assert updated_recipe.description == "Fresh green salad"
    ingredient_names = {ing.name for ing in updated_recipe.ingredients}
    assert ingredient_names == {"onion", "tomato"}


async def test_update_recipe_service_not_found(db: AsyncSession, test_user):
    update_data = RecipeCreate(
        title="Pizza",
        description="Homemade pizza",
        ingredients=[IngredientCreate(name="flour"), IngredientCreate(name="cheese")],
    )

    with pytest.raises(NotFoundError):
        await update_recipe_service(9, update_data, db, test_user)


async def test_delete_recipe_service_success(db: AsyncSession, test_user):
    recipe_data = RecipeCreate(
        title="Cookies",
        description="Chocolate chip cookies",
        ingredients=[
            IngredientCreate(name="flour"),
            IngredientCreate(name="chocolate"),
        ],
    )
    created_recipe = await create_recipe_service(recipe_data, db, test_user)

    deleted = await delete_recipe_service(created_recipe.id, db, test_user)

    assert deleted.id == created_recipe.id
    check = await RecipeRepository.get_by_id(db, created_recipe.id)
    assert check is None


async def test_delete_recipe_service_not_found(db: AsyncSession, test_user):
    with pytest.raises(NotFoundError):
        await delete_recipe_service(9, db, test_user)
