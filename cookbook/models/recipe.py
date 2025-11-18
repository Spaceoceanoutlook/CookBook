from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cookbook.models.base import Base
from cookbook.models.ingredient import Ingredient


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False)

    ingredients: Mapped[list["Ingredient"]] = relationship(
        secondary="recipe_ingredients",
        back_populates="recipes",
    )
