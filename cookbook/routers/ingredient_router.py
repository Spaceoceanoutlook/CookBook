from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.database import get_db
from cookbook.exceptions import AlreadyExistsError, NotFoundError
from cookbook.schemas.ingredient import (
    IngredientCreate,
    IngredientRead,
)
from cookbook.services.ingredient_service import (
    create_ingredient_service,
    delete_ingredient_service,
    get_all_ingredients,
)

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


@router.get(
    "",
    summary="Список ингредиентов",
    response_model=list[IngredientRead],
)
async def list_ingredients(db: AsyncSession = Depends(get_db)):
    return await get_all_ingredients(db)


@router.post(
    "",
    summary="Создание нового ингредиента",
    response_model=IngredientRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_ingredient(
    new_ingredient: IngredientCreate, db: AsyncSession = Depends(get_db)
):
    try:
        return await create_ingredient_service(new_ingredient, db)
    except AlreadyExistsError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных"
        )


@router.delete(
    "/{ingredient_id}",
    summary="Удаление ингредиента",
    response_model=IngredientRead,
)
async def delete_ingredient(ingredient_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await delete_ingredient_service(ingredient_id, db)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных"
        )
