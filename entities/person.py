from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class PersonModel(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
