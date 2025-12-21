from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.core.database import get_db
from cookbook.core.exceptions import AlreadyExistsError, AuthenticationError
from cookbook.schemas.user import UserLogin, UserRead, UserRegister
from cookbook.services.user_service import login_user_service, register_user_service

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", response_model=UserRead)
async def register(
    new_user: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await register_user_service(
            db=db,
            email=new_user.email,
            name=new_user.name,
            password=new_user.password,
        )
        return user
    except AlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных",
        )


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    try:
        token = await login_user_service(
            db=db,
            email=form_data.username,
            password=form_data.password,
        )
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
