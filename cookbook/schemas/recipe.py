from pydantic import BaseModel, ConfigDict, Field, field_validator

from cookbook.schemas.ingredient import IngredientCreate, IngredientRead


class RecipeBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=10000)
    model_config = ConfigDict(from_attributes=True)

    @field_validator("title")
    def normalize_name(cls, v: str) -> str:
        return v.strip().lower()


class RecipeCreate(RecipeBase):
    ingredients: list[IngredientCreate]


class RecipeRead(RecipeBase):
    id: int
    ingredients: list[IngredientRead] = Field(default_factory=list)


class RecipeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    ingredients: list[IngredientCreate] | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("title")
    def normalize_name(cls, v: str) -> str:
        return v.strip().lower()
