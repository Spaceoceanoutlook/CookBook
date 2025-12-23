from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.core.database import get_db
from cookbook.core.exceptions import NotFoundError
from cookbook.core.security import get_current_user
from cookbook.schemas.recipe import RecipeCreate, RecipeRead, RecipeUpdate
from cookbook.services.recipe_service import (
    create_recipe_service,
    delete_recipe_service,
    get_all_recipes,
    get_recipe_by_id,
    update_recipe_service,
)

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get(
    "",
    summary="Список рецептов",
    response_model=list[RecipeRead],
)
async def list_recipes(db: AsyncSession = Depends(get_db)):
    return await get_all_recipes(db)


@router.get(
    "/{recipe_id}",
    summary="Получить рецепт по ID",
    response_model=RecipeRead,
)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await get_recipe_by_id(recipe_id, db)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных"
        )


@router.post(
    "",
    summary="Создание нового рецепта",
    response_model=RecipeRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(
    new_recipe: RecipeCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await create_recipe_service(new_recipe, db, current_user)
    except SQLAlchemyError:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных"
        )


@router.put(
    "/{recipe_id}",
    summary="Обновить рецепт",
    response_model=RecipeRead,
)
async def update_recipe(
    recipe_id: int,
    update_data: RecipeUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await update_recipe_service(recipe_id, update_data, db, current_user)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных"
        )


@router.delete(
    "/{recipe_id}",
    summary="Удаление рецепта",
    response_model=RecipeRead,
)
async def delete_recipe(
    recipe_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await delete_recipe_service(recipe_id, db, current_user)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных"
        )
