from pydantic import BaseModel, ConfigDict, Field


class IngredientBase(BaseModel):
    name: str = Field(..., max_length=100)
    model_config = ConfigDict(from_attributes=True)


class IngredientCreate(IngredientBase):
    pass


class IngredientRead(IngredientBase):
    id: int
