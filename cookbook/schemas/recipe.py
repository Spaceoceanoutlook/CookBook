from pydantic import BaseModel, ConfigDict, Field

from cookbook.schemas.ingredient import IngredientCreate, IngredientRead


class RecipeBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=10000)
    model_config = ConfigDict(from_attributes=True)


class RecipeCreate(RecipeBase):
    ingredients: list[IngredientCreate]


class RecipeRead(RecipeBase):
    id: int
    ingredients: list[IngredientRead] = Field(default_factory=list)
