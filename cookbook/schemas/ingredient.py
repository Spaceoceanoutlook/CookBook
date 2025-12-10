from pydantic import BaseModel, ConfigDict, Field, field_validator


class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    model_config = ConfigDict(from_attributes=True)

    @field_validator("name")
    def normalize_name(cls, v: str) -> str:
        return v.strip().lower()


class IngredientCreate(IngredientBase):
    pass


class IngredientRead(IngredientBase):
    id: int
